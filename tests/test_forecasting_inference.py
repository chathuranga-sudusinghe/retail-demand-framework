"""Request-time inference checks with synthetic histories and spy models only."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pytest

import src.forecasting.inference as inference
from src.forecasting.export import ORIGIN, PRODUCERS, RUN_ID, SOURCE_SCHEMA
from src.forecasting.inference import ForecastInference, InferenceError, Producer
from src.forecasting.paths import REPOSITORY
from src.forecasting.preprocessing import ForecastPreprocessor, preprocessor_state


class SpyModel:
    def __init__(self, value: float = 12.375):
        self.value = value
        self.calls: list[np.ndarray[Any, Any]] = []
        self.kwargs: list[dict[str, Any]] = []

    def predict(
        self, matrix: np.ndarray[Any, Any], **kwargs: Any
    ) -> np.ndarray[Any, Any]:
        self.calls.append(matrix.copy())
        self.kwargs.append(kwargs)
        # Input-sensitive output lets checks detect unrelated/cached responses.
        return np.array([self.value + matrix[0, 4]])


def saved_state(horizon: int, model: Any) -> ForecastPreprocessor:
    return ForecastPreprocessor(
        model, pd.Timestamp(ORIGIN), horizon, 100, (("SKU_1",), ("WH_1",)), (), ()
    )


def service() -> ForecastInference:
    return ForecastInference(
        {
            h: Producer(
                h,
                model,
                config,
                saved_state(h, model),
                SpyModel(),
                {
                    "model_path": f"models/{model}/{config}",
                    "model_hash": "a" * 64,
                    "preprocessor_path": f"models/{model}/{config}/state.json",
                    "preprocessor_hash": "b" * 64,
                },
            )
            for h, model, config in PRODUCERS
        }
    )


def example(horizon: int = 1) -> dict[str, Any]:
    return json.loads(
        (REPOSITORY / f"examples/forecast-api/forecast-{horizon}-day.json").read_text()
    )


def invoke(engine: ForecastInference, payload: dict[str, Any]) -> dict[str, Any]:
    return engine.predict(
        sku_id=payload["SKU_ID"],
        warehouse_id=payload["Warehouse_ID"],
        forecast_origin=payload["forecast_origin"],
        horizon=payload["horizon"],
        history=payload["history"],
        input_kind=payload["input_kind"],
    )


@pytest.mark.parametrize("horizon,model,config", PRODUCERS)
def test_each_horizon_invokes_its_designated_model(
    horizon: int, model: str, config: str
) -> None:
    engine = service()
    result = invoke(engine, example(horizon))
    assert (result["model"], result["configuration_id"]) == (model, config)
    assert result["forecast_quantity"] == 12.375 + 15  # last observed day's lag
    assert result["forecast_origin"] == "2025-01-28"
    assert result["target_start_date"] == "2025-01-29"
    assert result["target_end_date"] == (
        pd.Timestamp("2025-01-28") + pd.Timedelta(days=horizon)
    ).strftime("%Y-%m-%d")
    assert result["forecast_type"] == (
        "next_day" if horizon == 1 else "cumulative_window"
    )
    assert result["inference_mode"] == "request_time"
    assert result["input_kind"] == "synthetic_demo"
    assert len(engine.producers[horizon].estimator.calls) == 1
    assert all(
        not p.estimator.calls for h, p in engine.producers.items() if h != horizon
    )
    assert engine.producers[horizon].estimator.kwargs == (
        [{"num_threads": 1}] if model == "lightgbm" else [{}]
    )
    assert (
        not {"observed_target", "MAE", "RMSE", "WAPE", "Bias", "prediction"}
        & result.keys()
    )
    assert result["provenance"]["model_hash"] == "a" * 64


def test_new_history_changes_model_matrix_and_output_without_response_cache() -> None:
    engine = service()
    payload = example()
    first = invoke(engine, payload)
    invoke(engine, payload)
    payload["history"][-1]["Units_Sold"] += 20
    second = invoke(engine, payload)
    spy = engine.producers[1].estimator
    assert len(spy.calls) == 3
    np.testing.assert_array_equal(spy.calls[0], spy.calls[1])
    assert not np.array_equal(spy.calls[0], spy.calls[2])
    assert second["forecast_quantity"] == first["forecast_quantity"] + 20
    assert second["provenance"]["input_sha256"] != first["provenance"]["input_sha256"]


@pytest.mark.parametrize("raw", [-10.125, 0.0, 0.125])
def test_raw_quantity_is_not_clipped_or_rounded(raw: float) -> None:
    engine = service()
    engine.producers[1].estimator.value = raw - 15
    assert invoke(engine, example())["forecast_quantity"] == raw


@pytest.mark.parametrize(
    "field,value,reason",
    [
        ("SKU_ID", "unknown", "unknown_sku"),
        ("Warehouse_ID", "unknown", "unknown_warehouse"),
        ("horizon", 2, "unsupported_horizon"),
        ("horizon", True, "unsupported_horizon"),
        ("forecast_origin", "2024-12-01", "invalid_origin"),
        ("forecast_origin", "2025-01-27", "future_history"),
        ("forecast_origin", "2025-01-29", "incomplete_history"),
        ("forecast_origin", "abc", "invalid_history"),
    ],
)
def test_invalid_identity_or_origin_never_invokes_model(
    field: str, value: Any, reason: str
) -> None:
    engine = service()
    payload = example()
    payload[field] = value
    with pytest.raises(InferenceError) as error:
        invoke(engine, payload)
    assert error.value.reason_code == reason
    assert all(not p.estimator.calls for p in engine.producers.values())


@pytest.mark.parametrize(
    "case", ["short", "duplicate", "gap", "negative", "missing", "fraction", "extra"]
)
def test_invalid_history_never_invokes_model(case: str) -> None:
    engine = service()
    payload = example()
    rows = payload["history"]
    if case == "short":
        rows.pop()
    elif case == "duplicate":
        rows[1]["Date"] = rows[0]["Date"]
    elif case == "gap":
        rows[0]["Date"] = "2024-12-30"
    elif case == "extra":
        rows[0]["Demand_Forecast"] = 1000
    else:
        rows[0]["Units_Sold"] = {"negative": -1, "missing": None, "fraction": 1.25}[
            case
        ]
    with pytest.raises(InferenceError):
        invoke(engine, payload)
    assert all(not p.estimator.calls for p in engine.producers.values())


@pytest.mark.parametrize("raw", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_model_output_has_explicit_unavailable_reason(raw: float) -> None:
    engine = service()
    engine.producers[1].estimator.value = raw
    with pytest.raises(InferenceError) as error:
        invoke(engine, example())
    assert error.value.reason_code == "unavailable_forecast"


def test_native_model_exception_has_explicit_unavailable_reason() -> None:
    engine = service()

    def broken(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("model failed")

    engine.producers[1].estimator.predict = broken
    with pytest.raises(InferenceError) as error:
        invoke(engine, example())
    assert error.value.reason_code == "unavailable_forecast"


def test_non_designated_producer_is_rejected() -> None:
    producers = service().producers.copy()
    p = producers[1]
    producers[1] = Producer(
        1, p.model, "GBM001", p.preprocessor, p.estimator, p.references
    )
    with pytest.raises(InferenceError):
        ForecastInference(producers)


def synthetic_source(root: Path) -> tuple[str, str]:
    """Bind a small fake model bundle. No retained evidence or model code runs."""
    files: list[dict[str, str]] = []

    def put(path: str, value: Any, owner: str) -> str:
        data = (
            value
            if isinstance(value, bytes)
            else json.dumps(value, sort_keys=True).encode()
        )
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()
        files.append({"path": path, "owner": owner, "sha256": digest})
        return digest

    candidates = []
    for h, model, config in PRODUCERS:
        prefix = f"models/forecasting/{RUN_ID}/final/{model}/h{h}/{config}"
        state = saved_state(h, model)
        refs: dict[str, str] = {}
        for name, filename, value in [
            (
                "model",
                "model.txt" if model == "lightgbm" else "model.ubj",
                f"synthetic native bytes {h}".encode(),
            ),
            ("preprocessor", "state.json", preprocessor_state(state)),
            ("origin_features", "origin_features.json", []),
        ]:
            path = f"{prefix}/{filename}"
            refs[name + "_path"] = path
            refs[name + "_hash"] = put(path, value, "models")
        refs["descriptor_path"] = f"{prefix}/descriptor.json"
        identity = {
            "run_id": RUN_ID,
            "evaluation_stage": "final_evaluation",
            "horizon": h,
            "model": model,
            "configuration_id": config,
        }
        descriptor = {
            **identity,
            **refs,
            "artifact_kind": "final_refit",
            "descriptor_version": 1,
            "physical_feature_names": state.physical_feature_names,
        }
        refs["descriptor_hash"] = put(refs["descriptor_path"], descriptor, "models")
        candidates.append(
            {
                **identity,
                "candidate_status": "completed",
                "evidence_role": "primary",
                "model_artifact": {**identity, **refs},
            }
        )
    candidates += [
        {"horizon": 1, "model": "unused", "configuration_id": f"unused-{i}"}
        for i in range(24)
    ]
    prefix = f"artifacts/forecasting/{RUN_ID}"
    sealed = copy.deepcopy(files)
    receipt_hash = put(
        f"{prefix}/prediction_receipt.json",
        {
            "run_id": RUN_ID,
            "evaluation_stage": "final_evaluation",
            "candidate_count": 28,
            "files": sealed,
        },
        "artifacts",
    )
    integrity = {"status": "passed"}
    completion = "2026-10-03T15:34:19.963693+00:00"
    put(f"{prefix}/candidates.json", candidates, "artifacts")
    put(
        f"{prefix}/run_metadata.json",
        {
            "run_id": RUN_ID,
            "schema_version": SOURCE_SCHEMA,
            "run_status": "verified_completed",
            "evaluation_stage": "final_evaluation",
            "prediction_receipt_hash": receipt_hash,
            "completed_at_utc": completion,
            "integrity_result": integrity,
            "producer_mapping": [
                {"horizon": h, "model": m, "configuration_id": c}
                for h, m, c in PRODUCERS
            ],
        },
        "artifacts",
    )
    manifest = {
        "manifest_version": 2,
        "run_id": RUN_ID,
        "schema_version": SOURCE_SCHEMA,
        "evaluation_stage": "final_evaluation",
        "final_status": "verified_completed",
        "completed_at_utc": completion,
        "integrity_result": integrity,
        "files": copy.deepcopy(files),
    }
    manifest_hash = put(f"{prefix}/run_manifest.json", manifest, "artifacts")
    return manifest_hash, receipt_hash


@pytest.fixture
def source(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    manifest, receipt = synthetic_source(tmp_path)
    monkeypatch.setattr(inference, "MANIFEST_SHA256", manifest)
    monkeypatch.setattr(inference, "RECEIPT_SHA256", receipt)
    return tmp_path


def test_loader_loads_only_four_bound_models_without_forecast_output_files(
    source: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = []

    def native(model: str, data: bytes) -> SpyModel:
        calls.append((model, data))
        return SpyModel()

    monkeypatch.setattr(inference, "_load_native", native)
    engine = inference.load_inference(source)
    assert len(calls) == 4
    assert [m for m, _ in calls] == ["lightgbm", "lightgbm", "xgboost", "xgboost"]
    assert [data for _, data in calls] == [
        f"synthetic native bytes {h}".encode() for h, _, _ in PRODUCERS
    ]
    assert not (source / f"artifacts/forecasting/{RUN_ID}/predictions.json").exists()
    assert invoke(engine, example())["inference_mode"] == "request_time"


@pytest.mark.parametrize("case", ["manifest", "receipt", "model", "state", "missing"])
def test_changed_or_missing_source_never_loads_models(
    source: Path, monkeypatch: pytest.MonkeyPatch, case: str
) -> None:
    def forbidden(*args: Any, **kwargs: Any) -> None:
        pytest.fail("No model should load from invalid source")

    monkeypatch.setattr(inference, "_load_native", forbidden)
    paths = {
        "manifest": f"artifacts/forecasting/{RUN_ID}/run_manifest.json",
        "receipt": f"artifacts/forecasting/{RUN_ID}/prediction_receipt.json",
        "model": f"models/forecasting/{RUN_ID}/final/lightgbm/h1/GBM018/model.txt",
        "state": f"models/forecasting/{RUN_ID}/final/lightgbm/h1/GBM018/state.json",
        "missing": f"artifacts/forecasting/{RUN_ID}/candidates.json",
    }
    path = source / paths[case]
    if case == "missing":
        path.unlink()
    else:
        path.write_bytes(path.read_bytes() + b"changed")
    with pytest.raises(InferenceError) as error:
        inference.load_inference(source)
    assert error.value.reason_code == "source_unverified"


def test_input_order_is_normalized_without_changing_input_hash() -> None:
    engine = service()
    payload = example()
    first = invoke(engine, payload)
    payload["history"].reverse()
    second = invoke(engine, payload)
    assert second["forecast_quantity"] == first["forecast_quantity"]
    assert second["provenance"]["input_sha256"] == first["provenance"]["input_sha256"]
    np.testing.assert_array_equal(
        engine.producers[1].estimator.calls[0], engine.producers[1].estimator.calls[1]
    )


@pytest.mark.parametrize("output", [[], [1, 2], [[1]]])
def test_wrong_model_output_shape_is_unavailable(output: list[Any]) -> None:
    engine = service()
    engine.producers[1].estimator.predict = lambda *args, **kwargs: np.array(output)
    with pytest.raises(InferenceError) as error:
        invoke(engine, example())
    assert error.value.reason_code == "unavailable_forecast"


@pytest.mark.parametrize("model", ["lightgbm", "xgboost"])
def test_native_loader_receives_exact_checked_bytes(
    model: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    import sys
    from types import ModuleType

    calls: list[Any] = []
    module = ModuleType(model)
    if model == "lightgbm":

        def booster(*, model_str: str) -> object:
            calls.append(model_str)
            return object()

        setattr(module, "Booster", booster)
    else:

        class Regressor:
            def __init__(self, **kwargs: Any):
                calls.append(kwargs)

            def load_model(self, value: bytearray) -> None:
                calls.append(value)

        setattr(module, "XGBRegressor", Regressor)
    monkeypatch.setitem(sys.modules, model, module)
    inference._load_native(model, b"exact checked bytes")
    expected: list[Any] = (
        ["exact checked bytes"]
        if model == "lightgbm"
        else [{"n_jobs": 1, "device": "cpu"}, bytearray(b"exact checked bytes")]
    )
    assert calls == expected


def test_native_load_failure_is_explicit_source_unavailable(
    source: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def broken(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("unsupported native model")

    monkeypatch.setattr(inference, "_load_native", broken)
    with pytest.raises(InferenceError) as error:
        inference.load_inference(source)
    assert error.value.reason_code == "source_unverified"


@pytest.mark.parametrize(
    "field,value",
    [
        ("producer_mapping", []),
        ("run_status", "failed"),
        ("prediction_receipt_hash", "0" * 64),
        ("evaluation_stage", "other"),
    ],
)
def test_bound_but_inconsistent_metadata_is_rejected(
    source: Path, monkeypatch: pytest.MonkeyPatch, field: str, value: Any
) -> None:
    prefix = source / f"artifacts/forecasting/{RUN_ID}"
    path = prefix / "run_metadata.json"
    metadata = json.loads(path.read_bytes())
    metadata[field] = value
    data = json.dumps(metadata, sort_keys=True).encode()
    path.write_bytes(data)
    manifest_path = prefix / "run_manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    for binding in manifest["files"]:
        if binding["path"].endswith("/run_metadata.json"):
            binding["sha256"] = hashlib.sha256(data).hexdigest()
    manifest_bytes = json.dumps(manifest, sort_keys=True).encode()
    manifest_path.write_bytes(manifest_bytes)
    # Treat this altered synthetic bundle as a separately pinned fixture,
    # so identity checks are reached instead of only a hash mismatch.
    monkeypatch.setattr(
        inference, "MANIFEST_SHA256", hashlib.sha256(manifest_bytes).hexdigest()
    )

    def forbidden(*args: Any, **kwargs: Any) -> None:
        pytest.fail("Invalid metadata must not reach native model loading")

    monkeypatch.setattr(inference, "_load_native", forbidden)
    with pytest.raises(InferenceError) as error:
        inference.load_inference(source)
    assert error.value.reason_code == "source_unverified"
