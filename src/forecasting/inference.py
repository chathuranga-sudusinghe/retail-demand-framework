"""Request-time forecasts from hash-bound saved producer models and supplied history."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from threading import Lock
from typing import Any

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from src.forecasting.export import (
    _VERIFIED_SOURCE,
    ORIGIN,
    PRODUCERS,
    RUN_ID,
    SOURCE_SCHEMA,
    _json,
    _producer_reference,
    _read_bound,
    _receipts,
)
from src.forecasting.features import (
    build_origin_features,
    calendar_date,
    feature_eligibility,
    prepare_demand,
)
from src.forecasting.paths import REPOSITORY, RepositoryLayout
from src.forecasting.preprocessing import ForecastPreprocessor, restore_preprocessor

MANIFEST_SHA256 = _VERIFIED_SOURCE.manifest_sha256
RECEIPT_SHA256 = _VERIFIED_SOURCE.receipt_sha256
INFERENCE_SCHEMA = "forecast-inference-v1"


class InferenceError(ValueError):
    """An explicit request or source failure; no substitute forecast."""

    def __init__(self, reason_code: str, message: str):
        super().__init__(message)
        self.reason_code = reason_code


@dataclass(frozen=True)
class Producer:
    horizon: int
    model: str
    configuration_id: str
    preprocessor: ForecastPreprocessor
    estimator: Any
    references: dict[str, str]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise InferenceError("source_unverified", message)


def _load_native(model: str, data: bytes) -> Any:
    """Load the exact checked bytes; no user-selected path or executable pickle."""
    if model == "lightgbm":
        from lightgbm import Booster

        return Booster(model_str=data.decode("utf-8"))
    from xgboost import XGBRegressor

    estimator = XGBRegressor(n_jobs=1, device="cpu")
    estimator.load_model(bytearray(data))
    return estimator


def load_inference(repository: Path = REPOSITORY) -> ForecastInference:
    """Bind four saved models once. No saved forecasts or outcome files are read."""
    try:
        return _load_inference(RepositoryLayout(repository))
    except InferenceError:
        raise
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        AttributeError,
        RuntimeError,
    ) as exc:
        raise InferenceError(
            "source_unverified", "Saved producer artifacts are missing or inconsistent."
        ) from exc


def _load_inference(layout: RepositoryLayout) -> ForecastInference:
    prefix = f"artifacts/forecasting/{RUN_ID}"
    manifest_bytes = layout._owned_path(
        layout.run_directory(RUN_ID) / "run_manifest.json"
    ).read_bytes()
    _require(
        hashlib.sha256(manifest_bytes).hexdigest() == MANIFEST_SHA256,
        "Pinned source manifest differs.",
    )
    manifest = _json(manifest_bytes)
    _require(
        isinstance(manifest, dict)
        and manifest["manifest_version"] == 2
        and manifest["run_id"] == RUN_ID
        and manifest["schema_version"] == SOURCE_SCHEMA
        and manifest["evaluation_stage"] == "final_evaluation"
        and manifest["final_status"] == "verified_completed"
        and manifest["integrity_result"]["status"] == "passed",
        "Source completion identity differs.",
    )
    bindings = _receipts(layout, manifest["files"])
    metadata = _json(_read_bound(layout, f"{prefix}/run_metadata.json", bindings))
    receipt_bytes = _read_bound(layout, f"{prefix}/prediction_receipt.json", bindings)
    _require(
        hashlib.sha256(receipt_bytes).hexdigest() == RECEIPT_SHA256,
        "Pinned source receipt differs.",
    )
    receipt = _json(receipt_bytes)
    _require(
        receipt["run_id"] == RUN_ID
        and receipt["evaluation_stage"] == "final_evaluation"
        and receipt["candidate_count"] == 28,
        "Source receipt identity differs.",
    )
    sealed = _receipts(layout, receipt["files"])
    _require(
        all(bindings.get(path) == row for path, row in sealed.items()),
        "Receipt and manifest bindings differ.",
    )
    expected_mapping = [
        {"horizon": h, "model": model, "configuration_id": config}
        for h, model, config in PRODUCERS
    ]
    _require(
        metadata["run_id"] == RUN_ID
        and metadata["schema_version"] == SOURCE_SCHEMA
        and metadata["evaluation_stage"] == "final_evaluation"
        and metadata["prediction_receipt_hash"] == RECEIPT_SHA256
        and metadata["run_status"] == "verified_completed"
        and metadata["completed_at_utc"] == manifest["completed_at_utc"]
        and metadata["integrity_result"] == manifest["integrity_result"]
        and metadata["producer_mapping"] == expected_mapping,
        "Source metadata or producer mapping differs.",
    )
    candidates = _json(_read_bound(layout, f"{prefix}/candidates.json", bindings))
    _require(
        isinstance(candidates, list) and len(candidates) == 28,
        "Candidate roster differs.",
    )
    producers = {}
    for horizon, model, configuration in PRODUCERS:
        matching = [
            row
            for row in candidates
            if (row["horizon"], row["model"], row["configuration_id"])
            == (horizon, model, configuration)
        ]
        _require(len(matching) == 1, "Designated producer is missing or duplicated.")
        candidate = matching[0]
        _require(
            candidate["run_id"] == RUN_ID
            and candidate["evaluation_stage"] == "final_evaluation"
            and candidate["candidate_status"] == "completed"
            and candidate["evidence_role"] == "primary",
            "Designated producer is unavailable.",
        )
        references = _producer_reference(layout, candidate, bindings, sealed)
        descriptor = _json(_read_bound(layout, references["descriptor_path"], bindings))
        _require(
            descriptor["artifact_kind"] == "final_refit"
            and descriptor["descriptor_version"] == 1
            and descriptor["run_id"] == RUN_ID
            and (
                descriptor["horizon"],
                descriptor["model"],
                descriptor["configuration_id"],
            )
            == (horizon, model, configuration)
            and all(
                descriptor.get(key) == value
                for key, value in references.items()
                if key != "descriptor_hash"
            ),
            "Producer descriptor differs.",
        )
        state = restore_preprocessor(
            _json(_read_bound(layout, references["preprocessor_path"], bindings))
        )
        _require(
            state.model == model
            and state.horizon == horizon
            and state.training_end == calendar_date(ORIGIN)
            and list(state.physical_feature_names)
            == descriptor["physical_feature_names"],
            "Saved input representation differs.",
        )
        # Decode/load precisely the bytes that passed the pinned binding check.
        model_bytes = _read_bound(layout, references["model_path"], bindings)
        try:
            estimator = _load_native(model, model_bytes)
        except Exception as exc:
            raise InferenceError(
                "source_unverified", "The saved native model could not load."
            ) from exc
        producers[horizon] = Producer(
            horizon, model, configuration, state, estimator, references
        )
    return ForecastInference(producers)


class ForecastInference:
    """Cache models and their input representation, never forecast responses."""

    def __init__(self, producers: dict[int, Producer]):
        _require(
            set(producers) == {h for h, _, _ in PRODUCERS}
            and all(
                (producers[h].model, producers[h].configuration_id) == (model, config)
                for h, model, config in PRODUCERS
            ),
            "Only the four designated producers may serve requests.",
        )
        self.producers = producers
        self._lock = Lock()

    def predict(
        self,
        *,
        sku_id: str,
        warehouse_id: str,
        forecast_origin: str,
        horizon: int,
        history: list[dict[str, Any]],
        input_kind: str = "supplied_history",
    ) -> dict[str, Any]:
        if type(horizon) is not int or horizon not in self.producers:
            raise InferenceError("unsupported_horizon", "Choose 1, 7, 14 or 28 days.")
        producer = self.producers[horizon]
        vocab = producer.preprocessor.category_vocabularies
        if sku_id not in vocab["SKU_ID"]:
            raise InferenceError(
                "unknown_sku", "SKU_ID is outside the saved model vocabulary."
            )
        if warehouse_id not in vocab["Warehouse_ID"]:
            raise InferenceError(
                "unknown_warehouse",
                "Warehouse_ID is outside the saved model vocabulary.",
            )
        try:
            origin = calendar_date(forecast_origin)
            if origin < producer.preprocessor.training_end:
                raise InferenceError(
                    "invalid_origin",
                    "Forecast origin predates the saved model boundary.",
                )
            if not 28 <= len(history) <= 366:
                raise InferenceError(
                    "insufficient_history",
                    "Supply between 28 and 366 consecutive daily records.",
                )
            if any(set(row) != {"Date", "Units_Sold"} for row in history):
                raise InferenceError(
                    "invalid_history", "History accepts Date and Units_Sold only."
                )
            frame = pd.DataFrame(history).assign(
                SKU_ID=sku_id, Warehouse_ID=warehouse_id
            )
            frame = prepare_demand(frame)
            if frame.Date.gt(origin).any():
                raise InferenceError(
                    "future_history", "History must not extend past forecast_origin."
                )
            if frame.Date.max() != origin:
                raise InferenceError(
                    "incomplete_history", "Daily history must end at forecast_origin."
                )
            features = build_origin_features(frame, origin=origin)
            if len(features) != 1 or not feature_eligibility(features).all():
                raise InferenceError(
                    "incomplete_history",
                    "The complete 28-day input window is required.",
                )
            matrix = producer.preprocessor.transform(features)
        except InferenceError:
            raise
        except (TypeError, ValueError, KeyError, OverflowError) as exc:
            raise InferenceError(
                "invalid_history",
                "History must contain valid daily dates and whole demand units.",
            ) from exc
        try:
            # Each request invokes the selected model on this request's own matrix.
            with self._lock, threadpool_limits(limits=1):
                kwargs = {"num_threads": 1} if producer.model == "lightgbm" else {}
                values = np.asarray(
                    producer.estimator.predict(matrix.to_numpy(dtype=float), **kwargs),
                    dtype=float,
                )
            if values.shape != (1,) or not np.isfinite(values).all():
                raise InferenceError(
                    "unavailable_forecast", "The model returned no finite forecast."
                )
        except InferenceError:
            raise
        except Exception as exc:
            raise InferenceError(
                "unavailable_forecast", "The saved model could not produce a forecast."
            ) from exc
        canonical = {
            "SKU_ID": sku_id,
            "Warehouse_ID": warehouse_id,
            "forecast_origin": forecast_origin,
            "horizon": horizon,
            "input_kind": input_kind,
            "history": [
                {"Date": day, "Units_Sold": units}
                for day, units in zip(
                    frame.Date.dt.strftime("%Y-%m-%d").tolist(),
                    [int(units) for units in frame.Units_Sold],
                    strict=True,
                )
            ],
        }
        input_hash = hashlib.sha256(
            json.dumps(
                canonical, sort_keys=True, separators=(",", ":"), allow_nan=False
            ).encode()
        ).hexdigest()
        references = producer.references
        return {
            "inference_schema": INFERENCE_SCHEMA,
            "inference_mode": "request_time",
            "input_kind": input_kind,
            "model_source_run_id": RUN_ID,
            "manifest_reference": f"artifacts/forecasting/{RUN_ID}/run_manifest.json",
            "manifest_sha256": MANIFEST_SHA256,
            "SKU_ID": sku_id,
            "Warehouse_ID": warehouse_id,
            "forecast_origin": origin.strftime("%Y-%m-%d"),
            "horizon": horizon,
            "target_start_date": (origin + timedelta(days=1)).strftime("%Y-%m-%d"),
            "target_end_date": (origin + timedelta(days=horizon)).strftime("%Y-%m-%d"),
            "forecast_type": "next_day" if horizon == 1 else "cumulative_window",
            "forecast_quantity": float(values[0]),
            "model": producer.model,
            "configuration_id": producer.configuration_id,
            "producer_designation": "frozen_designated_producer",
            "provenance": {
                **{
                    key: references[key]
                    for key in (
                        "model_path",
                        "model_hash",
                        "preprocessor_path",
                        "preprocessor_hash",
                    )
                },
                "input_sha256": input_hash,
            },
            "status": "available",
            "unavailable_reasons": [],
            "assumptions": [
                "Forecast uses only the supplied history through forecast_origin."
            ],
            "limitations": [
                "Synthetic demo input is illustrative supplied history."
                if input_kind == "synthetic_demo"
                else "The caller is responsible for the supplied history's provenance.",
                "Multi-day quantities are cumulative totals, not daily paths.",
                "28-day forecast availability does not approve downstream inventory use.",
            ],
        }
