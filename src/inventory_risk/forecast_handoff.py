"""Read the pinned prospective export and map it to inventory preparation.

No model, future demand or inventory exposure is evaluated here. Forecast
eligibility describes a usable source quantity, independently of snapshot
availability and downstream method/horizon gates.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, timedelta
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any

import pandas as pd

from src.forecasting.export import (
    DESTINATION,
    EXPORT_SCHEMA,
    ORIGIN,
    PRODUCERS,
    RUN_ID,
    SOURCE_SCHEMA,
    TRAINING_START,
)
from src.inventory_risk.input_preparation import prepare_inventory_risk_inputs
from src.forecasting.paths import REPOSITORY

MAPPING_VERSION = "issue-164-168-v1"
EXPORT_SHA256 = "c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863"
MANIFEST_SHA256 = "adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43"
RECEIPT_SHA256 = "853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692"
_ROW_FIELDS = {
    "SKU_ID",
    "Warehouse_ID",
    "forecast_origin",
    "horizon",
    "target_start_date",
    "target_end_date",
    "prediction",
    "model",
    "configuration_id",
    "forecast_type",
    "unit",
    "producer_status",
    "forecast_status",
    "uncertainty",
}
_INVENTORY_FIELDS = {
    "SKU_ID",
    "Warehouse_ID",
    "Date",
    "Inventory_Level",
    "Reorder_Point",
    "Supplier_Lead_Time_Days",
    "Order_Quantity",
    "Stockout_Flag",
    "Demand_Forecast",
    "origin_snapshot_available",
    "origin_snapshot_unavailable_reason",
    "supplier_lead_time_available_at_origin",
    "order_quantity_available_at_origin",
    "assumptions",
    "limitations",
    "unavailable_information_reasons",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        _require(key not in result, f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise ValueError(f"Non-finite JSON constant: {value}")


def _parse(payload: bytes) -> dict[str, Any]:
    value = json.loads(
        payload, object_pairs_hook=_object, parse_constant=_invalid_constant
    )
    _require(isinstance(value, dict), "Export must be a JSON object.")
    return value


def _digest(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _validate(document: dict[str, Any]) -> None:
    envelope = {
        "export_schema",
        "source",
        "forecast_origin",
        "training_start",
        "training_end",
        "producers",
        "series_count",
        "record_count",
        "forecasts",
    }
    _require(set(document) == envelope, "Unexpected or missing export envelope fields.")
    _require(document["export_schema"] == EXPORT_SCHEMA, "Unsupported export schema.")
    _require(
        document["forecast_origin"] == document["training_end"] == ORIGIN
        and document["training_start"] == TRAINING_START,
        "Export temporal policy differs.",
    )
    source = document["source"]
    _require(isinstance(source, dict), "Missing export-level source provenance.")
    _require(
        set(source)
        == {
            "run_id",
            "evaluation_stage",
            "source_schema",
            "run_manifest_path",
            "run_manifest_sha256",
            "prediction_receipt_sha256",
            "integrity_result",
        },
        "Unexpected or missing source provenance fields.",
    )
    _require(
        source.get("run_id") == RUN_ID
        and source.get("evaluation_stage") == "final_evaluation"
        and source.get("source_schema") == SOURCE_SCHEMA
        and source.get("run_manifest_path")
        == f"artifacts/forecasting/{RUN_ID}/run_manifest.json"
        and source.get("run_manifest_sha256") == MANIFEST_SHA256
        and source.get("prediction_receipt_sha256") == RECEIPT_SHA256,
        "Export source identity or parent anchors differ.",
    )
    integrity = source.get("integrity_result")
    _require(
        integrity
        == {
            "status": "passed",
            "evaluations": 28,
            "learned_refits": 20,
            "baseline_evaluations": 8,
            "predictions": 7000,
            "models_replayed": 20,
        }
        and all(type(integrity[key]) is int for key in integrity if key != "status"),
        "Source integrity reference differs.",
    )
    _require(
        type(document["series_count"]) is int
        and document["series_count"] == 250
        and type(document["record_count"]) is int
        and document["record_count"] == 1000,
        "Export population must be 250 series and 1000 forecasts.",
    )
    producers = document["producers"]
    _require(
        isinstance(producers, list) and len(producers) == 4, "Missing producer roster."
    )
    mapping = {h: (model, config) for h, model, config in PRODUCERS}
    producer_horizons: set[int] = set()
    for producer in producers:
        _require(isinstance(producer, dict), "Malformed producer reference.")
        horizon = producer.get("horizon")
        _require(
            type(horizon) is int and horizon in mapping, "Invalid producer horizon."
        )
        _require(horizon not in producer_horizons, "Duplicate producer horizon.")
        producer_horizons.add(horizon)
        _require(
            (producer.get("model"), producer.get("configuration_id"))
            == mapping[horizon]
            and producer.get("forecast_type")
            == ("next_day" if horizon == 1 else "cumulative_window"),
            "Designated producer differs.",
        )
        reference = producer.get("model_reference")
        _require(isinstance(reference, dict), "Missing model reference metadata.")
        for name in ("model", "descriptor", "preprocessor", "origin_features"):
            _require(
                isinstance(reference.get(name + "_path"), str)
                and _digest(reference.get(name + "_hash")),
                "Incomplete model reference metadata.",
            )
    rows = document["forecasts"]
    _require(
        isinstance(rows, list) and len(rows) == 1000,
        "Missing or partial forecast population.",
    )
    seen: set[tuple[str, str, int]] = set()
    roster: dict[int, set[tuple[str, str]]] = {h: set() for h in mapping}
    for row in rows:
        _require(
            isinstance(row, dict) and set(row) == _ROW_FIELDS,
            "Unexpected or missing forecast fields.",
        )
        horizon = row["horizon"]
        _require(
            type(horizon) is int and horizon in mapping, "Invalid forecast horizon."
        )
        _require(
            all(
                isinstance(row[key], str)
                and bool(row[key])
                and row[key] == row[key].strip()
                for key in ("SKU_ID", "Warehouse_ID")
            ),
            "Invalid SKU/warehouse identity.",
        )
        key = row["SKU_ID"], row["Warehouse_ID"], horizon
        _require(key not in seen, "Duplicate forecast identity.")
        seen.add(key)
        roster[horizon].add(key[:2])
        _require(
            row["forecast_origin"] == ORIGIN
            and row["target_start_date"]
            == (date.fromisoformat(ORIGIN) + timedelta(days=1)).isoformat()
            and row["target_end_date"]
            == (date.fromisoformat(ORIGIN) + timedelta(days=horizon)).isoformat(),
            "Forecast target interval differs from origin/horizon.",
        )
        _require(
            (row["model"], row["configuration_id"]) == mapping[horizon]
            and row["producer_status"] == "designated_producer"
            and row["forecast_status"] == "available"
            and row["unit"] == "units"
            and row["forecast_type"]
            == ("next_day" if horizon == 1 else "cumulative_window")
            and row["uncertainty"]
            == {"status": "unavailable", "reason": "no_agreed_method"},
            "Forecast producer, status, unit or interpretation differs.",
        )
        quantity = row["prediction"]
        try:
            finite_number = type(quantity) in (int, float) and math.isfinite(quantity)
        except OverflowError:
            finite_number = False
        _require(
            finite_number,
            "Prediction must be a finite JSON number.",
        )
    pairs = roster[1]
    _require(
        all(len(value) == 250 and value == pairs for value in roster.values()),
        "Horizons have different or incomplete series rosters.",
    )
    skus, warehouses = {p[0] for p in pairs}, {p[1] for p in pairs}
    _require(
        len(skus) == 50
        and len(warehouses) == 5
        and pairs == {(s, w) for s in skus for w in warehouses},
        "Series roster is not the complete SKU/warehouse grid.",
    )


@dataclass(frozen=True)
class ForecastHandoff:
    """Immutable, hash-bound bytes; every document access returns a fresh copy."""

    payload: bytes
    sha256: str

    def __post_init__(self) -> None:
        _require(
            _digest(self.sha256)
            and hashlib.sha256(self.payload).hexdigest() == self.sha256,
            "Forecast export SHA-256 mismatch.",
        )
        _validate(self.document)

    @property
    def document(self) -> dict[str, Any]:
        return _parse(self.payload)


def load_forecast_handoff(
    path: Path = Path(DESTINATION), *, expected_sha256: str = EXPORT_SHA256
) -> ForecastHandoff:
    """Read bytes only; expected_sha256 must come from a trusted reference."""
    return ForecastHandoff(path.read_bytes(), expected_sha256)


def _snapshot_day(value: Any) -> str:
    _require(
        isinstance(value, (str, date, pd.Timestamp)), "Invalid inventory snapshot date."
    )
    stamp = pd.Timestamp(value)
    _require(
        pd.notna(stamp) and stamp.tzinfo is None and stamp == stamp.normalize(),
        "Inventory snapshot must be a timezone-naive calendar date.",
    )
    return stamp.isoformat()


def forecast_inventory_inputs(
    handoff: ForecastHandoff, inventory: pd.DataFrame | None = None
) -> pd.DataFrame:
    """Map all source rows; join only exact-origin snapshots with explicit markers.

    Missing availability stays unknown. ``eligible`` denotes a valid nonnegative
    source forecast only; it never implies known inventory or method approval.
    A finite negative prediction is preserved but ineligible for exposure.
    """
    document = handoff.document
    rows = pd.DataFrame(document["forecasts"])
    # Mixed JSON integers/floats must not force raw integer quantities through
    # pandas' float64 inference (which can lose precision above 2**53).
    rows["prediction"] = pd.Series(
        [row["prediction"] for row in document["forecasts"]], dtype=object
    )
    rows["run_id"] = document["source"]["run_id"]
    rows["evaluation_stage"] = document["source"]["evaluation_stage"]
    # This binding is specific to the pinned export: its producer code checks
    # primary on both parent candidate and prediction, not just producer_status.
    rows["evidence_role"] = "primary"
    rows["prediction_status"] = rows["forecast_status"]
    rows["eligibility_status"] = rows["prediction"].map(
        lambda value: "eligible" if value >= 0 else "ineligible"
    )
    rows["canonical_config_id"] = rows["configuration_id"]
    rows["source_export_sha256"] = handoff.sha256
    rows["source_export_schema"] = document["export_schema"]
    rows["source_provenance"] = json.dumps(document["source"], sort_keys=True)
    if inventory is None:
        for column in ("Date", "Inventory_Level", "Reorder_Point"):
            rows[column] = pd.NA
    else:
        _require(
            isinstance(inventory, pd.DataFrame),
            "Inventory snapshots must be a DataFrame.",
        )
        _require(inventory.columns.is_unique, "Duplicate inventory column names.")
        required = {
            "SKU_ID",
            "Warehouse_ID",
            "Date",
            "Inventory_Level",
            "Reorder_Point",
        }
        _require(
            required <= set(inventory.columns),
            "Missing required inventory snapshot columns.",
        )
        snapshots = inventory.loc[
            :, [c for c in inventory.columns if c in _INVENTORY_FIELDS]
        ].copy(deep=True)
        for column in ("SKU_ID", "Warehouse_ID"):
            _require(
                bool(
                    snapshots[column]
                    .map(lambda v: isinstance(v, str) and bool(v) and v == v.strip())
                    .all()
                ),
                "Invalid inventory identity.",
            )
        snapshots["_origin_join"] = snapshots["Date"].map(_snapshot_day)
        _require(
            bool(snapshots["_origin_join"].notna().all()),
            "Invalid inventory snapshot date.",
        )
        _require(
            not snapshots.duplicated(["SKU_ID", "Warehouse_ID", "_origin_join"]).any(),
            "Duplicate inventory snapshot identity/date.",
        )
        rows["_origin_join"] = pd.Timestamp(ORIGIN).isoformat()
        rows = rows.merge(
            snapshots,
            on=["SKU_ID", "Warehouse_ID", "_origin_join"],
            how="left",
            validate="many_to_one",
            sort=False,
            indicator="_inventory_join",
        )
        missing_snapshot = rows["_inventory_join"].eq("left_only")
        for column in (
            "origin_snapshot_available",
            "origin_snapshot_unavailable_reason",
        ):
            if column not in rows.columns:
                rows[column] = pd.Series(pd.NA, index=rows.index, dtype=object)
            else:
                rows[column] = rows[column].astype(object)
        rows.loc[missing_snapshot, "origin_snapshot_available"] = False
        rows.loc[missing_snapshot, "origin_snapshot_unavailable_reason"] = (
            "origin_inventory_record_missing"
        )
        rows = rows.drop(columns=["_origin_join", "_inventory_join"])
    return prepare_inventory_risk_inputs(rows)


def _json_value(value: Any) -> Any:
    """Normalize missing/scalar metadata without rounding raw forecast numbers."""
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if value is None or value is pd.NA or value is pd.NaT:
        return None
    if isinstance(value, (date, pd.Timestamp)):
        return value.isoformat()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "item"):
        return _json_value(value.item())
    raise TypeError(f"Unsupported prepared-input value: {type(value).__name__}")


def main(argv: list[str] | None = None) -> int:
    """Human-run preparation only; no exposure, outcomes or research metrics."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--operator", required=True)
    parser.add_argument(
        "--snapshot-availability", choices=("unknown", "confirmed"), default="unknown"
    )
    parser.add_argument(
        "--snapshot-basis", default="Source within-day timing has not been established."
    )
    args = parser.parse_args(argv)
    try:
        _require(
            bool(args.operator.strip()) and bool(args.snapshot_basis.strip()),
            "Operator and snapshot basis must be nonblank.",
        )
        if args.snapshot_availability == "confirmed":
            _require(
                args.snapshot_basis != parser.get_default("snapshot_basis"),
                "Confirmed snapshot availability needs the actual source timing basis.",
            )
        destination = args.output.resolve()
        root = (REPOSITORY / "research-materials").resolve()
        _require(
            destination != root and destination.is_relative_to(root),
            "Prepared inputs must stay inside ignored research-materials/.",
        )
        # Restrict decoded inventory data to the origin; no future sales/outcomes.
        from src.data.validated_handoff import read_validated_projection

        source = load_forecast_handoff(REPOSITORY / DESTINATION)
        projection = read_validated_projection(
            repository=REPOSITORY,
            data_version="supply-chain-dataset1-validated-v1",
            columns=(
                "SKU_ID",
                "Warehouse_ID",
                "Date",
                "Inventory_Level",
                "Reorder_Point",
                "Supplier_Lead_Time_Days",
                "Order_Quantity",
            ),
            start=ORIGIN,
            end=ORIGIN,
            expected_provenance_sha256="35e9fb4218bfaf301703d6885decebaee6a3af2aa85aef55247c3a77d0ea964f",
        )
        snapshots = projection.frame.copy(deep=True)
        if args.snapshot_availability == "confirmed":
            snapshots["origin_snapshot_available"] = True
        inputs = forecast_inventory_inputs(source, snapshots)
        result = {
            "mapping_version": MAPPING_VERSION,
            "operator": args.operator,
            "code_sha256": {
                name: hashlib.sha256(
                    (Path(__file__).resolve().parents[2] / name).read_bytes()
                ).hexdigest()
                for name in (
                    "src/inventory_risk/forecast_handoff.py",
                    "src/inventory_risk/input_preparation.py",
                )
            },
            "source_export_sha256": source.sha256,
            "dataset_provenance_sha256": projection.provenance_sha256,
            "snapshot_availability": args.snapshot_availability,
            "snapshot_basis": args.snapshot_basis,
            "scope": "Prepared inputs only; no exposure evaluation or research metrics.",
            "records": _json_value(inputs.to_dict(orient="records")),
        }
        payload = (
            json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
        ).encode()
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as stream:
            stream.write(payload)
        print(
            f"Wrote {len(inputs)} prepared inputs to {destination}; no inventory evaluation executed."
        )
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"Inventory handoff preparation failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
