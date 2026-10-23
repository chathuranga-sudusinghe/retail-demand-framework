"""Human-run DR-012 evaluation of the retained forecasts, without model execution.

Origin inventory and future Units_Sold are read through separate projections.
Prospective evidence excludes retrospective observations, labels and metrics.
Constructed snapshots require an explicit CLI choice and remain distinct from
verified source availability. Project-data execution belongs to the human.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from numbers import Real
from pathlib import Path
from typing import Any

import pandas as pd

from src.data.validated_handoff import read_validated_projection
from src.forecasting.export import DESTINATION, ORIGIN
from src.forecasting.paths import REPOSITORY
from src.inventory_risk.evaluation import SCENARIO_LIMITATION, evaluate_inventory_risk
from src.inventory_risk.forecast_handoff import (
    MAPPING_VERSION,
    ForecastHandoff,
    _json_value,
    _snapshot_day,
    forecast_inventory_inputs,
    load_forecast_handoff,
)
from src.inventory_risk.input_preparation import EVALUABLE_HORIZONS, METHOD_STATUS

RUN_SCHEMA = "inventory-risk-evaluation-v1"
PROSPECTIVE_SCHEMA = "inventory-risk-prospective-v1"
DATA_VERSION = "supply-chain-dataset1-validated-v1"
PROVENANCE_SHA256 = "35e9fb4218bfaf301703d6885decebaee6a3af2aa85aef55247c3a77d0ea964f"
CONSTRUCTED_BASIS = (
    "Constructed no-receipt scenario: take the recorded Inventory_Level and "
    "Reorder_Point on 2024-12-02 as hypothetical starting balances immediately "
    "before the 2024-12-03 target window. Hold Reorder_Point fixed; model no "
    "receipts, transfers, returns, losses or other adjustments. This is not "
    "verified source timing or a reconstruction of realised inventory."
)
KEY = ["SKU_ID", "Warehouse_ID", "forecast_origin", "horizon"]
PROSPECTIVE_FIELDS = (
    *KEY,
    "target_start_date",
    "target_end_date",
    "prediction",
    "unit",
    "model",
    "configuration_id",
    "run_id",
    "evaluation_stage",
    "evidence_role",
    "source_export_sha256",
    "source_provenance",
    "Date",
    "Inventory_Level",
    "Reorder_Point",
    "origin_snapshot_available",
    "origin_snapshot_status",
    "origin_snapshot_reason",
    "inventory_state_available",
    "inventory_basis",
    "snapshot_assumption",
    "scenario_inventory_state_available",
    "analysis_inventory_state_available",
    "origin_exposure_state",
    "forecast_exposure_state",
    "inventory_buffer",
    "predicted_margin",
    "forecast_input_status",
    "forecast_input_reason",
    "downstream_use_status",
    "downstream_use_reason",
    "methodology_status",
    "method_assumptions",
    "method_limitations",
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _bytes(value: Any) -> bytes:
    return (
        json.dumps(_json_value(value), indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode()


def _destination(path: Path) -> Path:
    path = path.resolve()
    root = (REPOSITORY / "research-materials").resolve()
    _require(
        path != root and path.is_relative_to(root),
        "Outputs must stay inside ignored research-materials/.",
    )
    return path


def _daily_count(value: Any) -> int | None:
    original = value
    if not isinstance(value, Real) or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (ValueError, OverflowError):
        return None
    if not math.isfinite(number) or number < 0 or not number.is_integer():
        return None
    return int(original)


def validate_prospective_state(row: dict[str, Any], source: dict[str, Any]) -> None:
    """Reject contradictory evidence; never generate or repair exposure outputs.

    These are producer-contract checks of the existing DR-012 arithmetic and
    status meanings. They require no observations or retrospective calculations.
    """
    _require(
        row["methodology_status"] == METHOD_STATUS,
        "Methodology status differs from the producer contract.",
    )
    _require(
        row["evidence_role"] == "primary",
        "Forecast evidence role differs from the pinned export contract.",
    )
    for name in (
        "inventory_state_available",
        "scenario_inventory_state_available",
        "analysis_inventory_state_available",
    ):
        _require(type(row[name]) is bool, f"Invalid inventory availability: {name}")
    marker = row["origin_snapshot_available"]
    _require(
        marker is None or type(marker) is bool, "Invalid source availability marker."
    )
    same_date = row["Date"] is not None and (
        _snapshot_day(row["Date"]) == _snapshot_day(row["forecast_origin"])
    )
    _require(
        row["Date"] is None or same_date,
        "Inventory snapshot is not from the forecast origin.",
    )
    expected_status = (
        "unknown"
        if marker is None
        else "available"
        if marker and same_date
        else "unavailable"
    )
    _require(
        row["origin_snapshot_status"] == expected_status,
        "Source availability/status differs.",
    )
    reason = row["origin_snapshot_reason"]
    _require(
        isinstance(reason, str)
        and (reason == "" if expected_status == "available" else bool(reason.strip())),
        "Missing or inconsistent snapshot reason.",
    )
    valid_balances = bool(
        same_date
        and _daily_count(row["Inventory_Level"]) is not None
        and _daily_count(row["Reorder_Point"]) is not None
    )
    source_available = marker is True and valid_balances
    _require(
        row["inventory_state_available"] == source_available,
        "Source inventory availability contradicts its balances.",
    )
    policy = source["snapshot_policy"]
    constructed = policy == "constructed-origin"
    gated = row["horizon"] == 28
    expected_downstream = (
        (
            "not_approved_for_downstream_use",
            "28_day_downstream_use_requires_separate_approval",
        )
        if gated
        else (
            "proposed_method_not_group_approved",
            "DR-012_remains_proposed_for_group_approval",
        )
    )
    _require(
        (row["downstream_use_status"], row["downstream_use_reason"])
        == expected_downstream,
        "Downstream use status/reason differs from the producer contract.",
    )
    for name in ("method_assumptions", "method_limitations"):
        _require(
            isinstance(row[name], list)
            and all(isinstance(v, str) and bool(v.strip()) for v in row[name]),
            f"Invalid inventory disclosure: {name}",
        )
    if constructed:
        _require(
            marker is not True
            and row["inventory_basis"] == "constructed_origin_scenario"
            and row["snapshot_assumption"] == source["snapshot_basis"],
            "Constructed inventory must preserve unknown/unavailable source timing.",
        )
        _require(
            source["snapshot_basis"] in row["method_assumptions"]
            and SCENARIO_LIMITATION in row["method_limitations"],
            "Constructed scenario disclosure is missing.",
        )
    else:
        _require(
            row["inventory_basis"] == "source_availability"
            and row["snapshot_assumption"] is None,
            "Source inventory basis/assumption differs.",
        )
        if policy == "unknown":
            _require(
                marker is not True, "Unknown policy cannot confirm source availability."
            )
        else:
            _require(policy == "source-confirmed", "Unsupported snapshot policy.")
            _require(
                marker is (True if same_date else False),
                "Source-confirmed marker contradicts the supplied origin row.",
            )
    scenario_available = constructed and valid_balances and not gated
    analysis_available = (
        scenario_available
        if constructed
        else source_available and policy == "source-confirmed" and not gated
    )
    _require(
        row["scenario_inventory_state_available"] == scenario_available,
        "Scenario inventory availability differs.",
    )
    _require(
        row["analysis_inventory_state_available"] == analysis_available,
        "Analysis inventory availability contradicts its policy/balances.",
    )
    forecast_available = row["prediction"] >= 0
    _require(
        row["forecast_input_status"]
        == ("available" if forecast_available else "unavailable"),
        "Forecast usability contradicts its raw prediction.",
    )
    forecast_reason = row["forecast_input_reason"]
    _require(
        isinstance(forecast_reason, str)
        and (
            forecast_reason == ""
            if forecast_available
            else bool(forecast_reason.strip())
        ),
        "Forecast unavailable reason is inconsistent.",
    )
    if not analysis_available:
        _require(
            row["origin_exposure_state"]
            == row["forecast_exposure_state"]
            == "unavailable"
            and row["inventory_buffer"] is None
            and row["predicted_margin"] is None,
            "Unavailable/gated inventory must not contain exposure values.",
        )
        return

    def require_number(value: Any, expected: float, name: str) -> None:
        _require(
            type(value) in (int, float)
            and math.isfinite(float(value))
            and value == expected,
            f"Inventory {name} is inconsistent with its input quantities.",
        )

    buffer = float(row["Inventory_Level"]) - float(row["Reorder_Point"])
    require_number(row["inventory_buffer"], buffer, "buffer")
    prefix = "scenario_" if constructed else ""
    if buffer <= 0:
        _require(
            row["origin_exposure_state"] == prefix + "already_at_or_below_threshold",
            "Origin threshold state is inconsistent.",
        )
        _require(
            row["forecast_exposure_state"]
            == (
                "not_needed_scenario_origin_state"
                if constructed
                else "not_needed_origin_state_known"
            )
            and row["predicted_margin"] is None,
            "Origin-known/scenario state must not contain forecast margin evidence.",
        )
    else:
        _require(
            row["origin_exposure_state"] == prefix + "initially_above_threshold",
            "Origin threshold state is inconsistent.",
        )
        if forecast_available:
            prediction = float(row["prediction"])
            expected_state = (
                "forecast_crossing" if prediction >= buffer else "no_forecast_crossing"
            )
            _require(
                row["forecast_exposure_state"] == expected_state,
                "Forecast threshold state is inconsistent.",
            )
            require_number(row["predicted_margin"], buffer - prediction, "margin")
        else:
            _require(
                row["forecast_exposure_state"] == "unavailable"
                and row["predicted_margin"] is None,
                "Invalid forecasts must not contain forecast exposure evidence.",
            )


def retrospective_targets(
    handoff: ForecastHandoff, sales: pd.DataFrame
) -> pd.DataFrame:
    """Sum only complete, unique, valid daily windows; keep missing targets null."""
    required = {"SKU_ID", "Warehouse_ID", "Date", "Units_Sold"}
    _require(
        sales.columns.is_unique and required <= set(sales.columns),
        "Invalid sales projection columns.",
    )
    frame = sales.loc[:, sorted(required)].copy(deep=True)
    for name in ("SKU_ID", "Warehouse_ID"):
        _require(
            bool(
                frame[name]
                .map(
                    lambda v: isinstance(v, str) and bool(v.strip()) and v == v.strip()
                )
                .all()
            ),
            "Invalid sales identity.",
        )
    frame["Date"] = frame["Date"].map(_snapshot_day).map(pd.Timestamp)
    first, last = (
        pd.Timestamp(ORIGIN) + pd.Timedelta(days=1),
        pd.Timestamp(ORIGIN) + pd.Timedelta(days=14),
    )
    _require(
        bool(frame["Date"].between(first, last).all()),
        "Sales projection exceeds the 1/7/14-day evaluation window.",
    )
    _require(
        not frame.duplicated(["SKU_ID", "Warehouse_ID", "Date"]).any(),
        "Duplicate daily sales key.",
    )
    source = handoff.document["forecasts"]
    roster = {(r["SKU_ID"], r["Warehouse_ID"]) for r in source}
    _require(
        set(zip(frame["SKU_ID"], frame["Warehouse_ID"], strict=True)) <= roster,
        "Unexpected sales series.",
    )
    groups = {
        key: group.set_index("Date")["Units_Sold"].to_dict()
        for key, group in frame.groupby(["SKU_ID", "Warehouse_ID"], observed=True)
    }
    rows: list[dict[str, Any]] = []
    for forecast in source:
        horizon = forecast["horizon"]
        if horizon not in EVALUABLE_HORIZONS:
            continue
        daily = groups.get((forecast["SKU_ID"], forecast["Warehouse_ID"]), {})
        dates = pd.date_range(
            forecast["target_start_date"], forecast["target_end_date"]
        )
        values = [_daily_count(daily.get(day)) for day in dates]
        missing = any(day not in daily for day in dates)
        valid = all(v is not None for v in values)
        complete = not missing and valid and len(dates) == horizon
        rows.append(
            {
                **{name: forecast[name] for name in KEY},
                "observed_target": sum(v for v in values if v is not None)
                if complete
                else None,
                "target_status": "complete" if complete else "unavailable",
                "target_expected_days": horizon,
                "target_present_days": sum(day in daily for day in dates),
                "target_unavailable_reason": ""
                if complete
                else (
                    "missing_daily_target_records"
                    if missing
                    else "invalid_daily_units_sold"
                ),
            }
        )
    result = pd.DataFrame(rows)
    result["observed_target"] = pd.Series(
        [r["observed_target"] for r in rows], dtype=object
    )
    return result


def evaluate_handoff(
    handoff: ForecastHandoff,
    inventory: pd.DataFrame,
    sales: pd.DataFrame,
    *,
    snapshot_policy: str,
    snapshot_basis: str = "",
) -> dict[str, Any]:
    """Evaluate supplied evidence; this function is tested only with synthetic data."""
    _require(
        snapshot_policy in ("unknown", "source-confirmed", "constructed-origin"),
        "Unsupported snapshot policy.",
    )
    snapshots = inventory.copy(deep=True)
    basis = "Source origin availability is unknown."
    scenario_basis = None
    if snapshot_policy == "source-confirmed":
        _require(
            bool(snapshot_basis.strip()),
            "Source-confirmed inventory needs its actual timing basis.",
        )
        basis = snapshot_basis
        snapshots["origin_snapshot_available"] = True
    else:
        # Neither an unknown source nor a hypothetical scenario verifies timing.
        snapshots["origin_snapshot_available"] = pd.NA
        if snapshot_policy == "constructed-origin":
            basis = CONSTRUCTED_BASIS
            scenario_basis = basis
    inputs = forecast_inventory_inputs(handoff, snapshots)
    eligible = inputs.loc[inputs["horizon"].isin(EVALUABLE_HORIZONS)].copy()
    # Build the prospective view before joining any realised demand.
    forecast_cases = evaluate_inventory_risk(eligible, scenario_basis=scenario_basis)[
        "cases"
    ]
    prospective: list[dict[str, Any]] = [
        {name: row[name] for name in PROSPECTIVE_FIELDS}
        for row in forecast_cases.to_dict(orient="records")
    ]
    for row in inputs.loc[inputs["horizon"].eq(28)].to_dict(orient="records"):
        case = {name: row.get(name) for name in PROSPECTIVE_FIELDS}
        case.update(
            inventory_basis="constructed_origin_scenario"
            if scenario_basis
            else "source_availability",
            snapshot_assumption=scenario_basis,
            scenario_inventory_state_available=False,
            analysis_inventory_state_available=False,
            origin_exposure_state="unavailable",
            forecast_exposure_state="unavailable",
        )
        if scenario_basis:
            case["method_assumptions"] = (
                *row["method_assumptions"][1:],
                scenario_basis,
            )
            case["method_limitations"] = (
                *row["method_limitations"],
                SCENARIO_LIMITATION,
            )
        prospective.append(case)
    targets = retrospective_targets(handoff, sales)
    paired = eligible.merge(
        targets, on=KEY, how="left", validate="one_to_one", sort=False
    )
    evaluation = evaluate_inventory_risk(paired, scenario_basis=scenario_basis)
    source = {
        "mapping_version": MAPPING_VERSION,
        "forecast_export_sha256": handoff.sha256,
        "forecast_source": handoff.document["source"],
        "snapshot_policy": snapshot_policy,
        "snapshot_basis": basis,
    }
    return {
        "prospective": {
            "schema": PROSPECTIVE_SCHEMA,
            "source": source,
            "scope": "Origin/forecast-only evidence; no realised demand, retrospective labels or metrics. H=28 inventory interpretation is gated.",
            "records": _json_value(prospective),
        },
        "evaluation": {
            "schema": RUN_SCHEMA,
            "source": source,
            "scope": "Separate 1/7/14-day DR-012 proxy comparisons; no pooled score, actual-stockout labels or replenishment quantities.",
            "cases": _json_value(evaluation["cases"].to_dict(orient="records")),
            "summary": _json_value(evaluation["summary"].to_dict(orient="records")),
        },
    }


def report_markdown(result: dict[str, Any]) -> str:
    evaluation = result["evaluation"]
    source = evaluation["source"]
    lines = [
        "# Inventory reorder-threshold exposure evaluation",
        "",
        f"Snapshot policy: **{source['snapshot_policy']}**.",
        "",
        source["snapshot_basis"],
        "",
        "## Population and counts",
        "",
        "| Horizon | Paired N | TP | TN | FP | FN | Source-known at/below | Scenario at/below | Unavailable |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in evaluation["summary"]:
        lines.append(
            "| "
            + " | ".join(
                str(row[k])
                for k in (
                    "horizon",
                    "N",
                    "TP",
                    "TN",
                    "FP",
                    "FN",
                    "origin_known_at_or_below_count",
                    "scenario_at_or_below_count",
                    "unavailable_case_count",
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Horizon-specific proxy metrics",
            "",
            "| Horizon | Metric | Value | Denominator | Status |",
            "|---|---|---:|---:|---|",
        ]
    )
    for row in evaluation["summary"]:
        denominators = {
            "event_prevalence": row["N"],
            "missed_crossing_rate": row["TP"] + row["FN"],
            "false_alert_rate": row["FP"] + row["TN"],
            "agreement": row["N"],
            "precision": row["TP"] + row["FP"],
            "recall": row["TP"] + row["FN"],
            "balanced_accuracy": f"positive={row['TP'] + row['FN']}; negative={row['TN'] + row['FP']}",
        }
        for name, denominator in denominators.items():
            value = row[name]
            lines.append(
                f"| {row['horizon']} | {name} | {'N/A' if value is None else f'{value:.4f}'} | {denominator} | {row[name + '_status']} |"
            )
    lines.extend(
        [
            "",
            "## Interpretation and limitations",
            "",
            "These results compare a fixed-origin, fixed-reorder-point, no-receipt scenario with a constructed retrospective demand proxy. They do not establish actual stockout accuracy, optimal orders, real-retailer effectiveness or managerial benefit.",
            "",
            "Already-at/below-threshold cases are excluded from paired forecast-skill comparisons. Missing targets and invalid forecasts remain unavailable. Undefined denominators remain null, not zero. Horizons are separate; 28-day inventory evaluation is excluded.",
            "",
            "The Kaggle dataset is publisher-simulated and Stockout_Flag has zero variance. Order_Quantity is not treated as receipts. Numerical replenishment, overstock, uncertainty and managerial review rules remain unavailable.",
            "",
            "The final interval has December 3–16 prior validation exposure and full-year exploratory exposure. This conditional secondary analysis does not change frozen forecasting producers or replay their final evaluation.",
            "",
            "Use prospective.json for downstream records. Evaluation-only observations, confusion cells and metrics remain in evaluation.json.",
            "",
            f"Forecast export SHA-256: `{source['forecast_export_sha256']}`.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_result(
    result: dict[str, Any], output: Path, operator: str, provenance_sha256: str
) -> None:
    """Publish an exclusive local bundle; manifest is written last."""
    _require(bool(operator.strip()), "A human operator is required.")
    output = _destination(output)
    _require(
        provenance_sha256 == PROVENANCE_SHA256,
        "Unexpected validated-dataset provenance.",
    )
    payloads = {
        "prospective.json": _bytes(result["prospective"]),
        "evaluation.json": _bytes(result["evaluation"]),
        "report.md": report_markdown(result).encode(),
    }
    manifest = {
        "schema": RUN_SCHEMA,
        "operator": operator,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": result["evaluation"]["source"],
        "dataset_provenance_sha256": provenance_sha256,
        "files": {
            name: hashlib.sha256(payload).hexdigest()
            for name, payload in payloads.items()
        },
        "code_sha256": {
            name: hashlib.sha256(
                (Path(__file__).resolve().parents[2] / name).read_bytes()
            ).hexdigest()
            for name in (
                "src/inventory_risk/runner.py",
                "src/inventory_risk/evaluation.py",
                "src/inventory_risk/input_preparation.py",
                "src/inventory_risk/forecast_handoff.py",
            )
        },
    }
    output.mkdir(parents=True, exist_ok=False)
    for name, payload in (*payloads.items(), ("manifest.json", _bytes(manifest))):
        with (output / name).open("xb") as stream:
            stream.write(payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operator", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--snapshot-policy",
        choices=("unknown", "source-confirmed", "constructed-origin"),
        required=True,
    )
    parser.add_argument(
        "--snapshot-basis",
        default="",
        help="Required source timing evidence for source-confirmed policy.",
    )
    args = parser.parse_args(argv)
    try:
        output = _destination(args.output)
        _require(bool(args.operator.strip()), "A human operator is required.")
        if output.exists():
            raise FileExistsError(f"Output directory already exists: {output}")
        if args.snapshot_policy == "source-confirmed":
            _require(
                bool(args.snapshot_basis.strip()),
                "Source-confirmed inventory needs its actual timing basis.",
            )
        handoff = load_forecast_handoff(REPOSITORY / DESTINATION)
        origin = read_validated_projection(
            repository=REPOSITORY,
            data_version=DATA_VERSION,
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
            expected_provenance_sha256=PROVENANCE_SHA256,
        )
        outcomes = read_validated_projection(
            repository=REPOSITORY,
            data_version=DATA_VERSION,
            columns=("SKU_ID", "Warehouse_ID", "Date", "Units_Sold"),
            start="2024-12-03",
            end="2024-12-16",
            expected_provenance_sha256=PROVENANCE_SHA256,
        )
        _require(
            origin.provenance_sha256 == outcomes.provenance_sha256 == PROVENANCE_SHA256,
            "Projection provenance differs.",
        )
        result = evaluate_handoff(
            handoff,
            origin.frame,
            outcomes.frame,
            snapshot_policy=args.snapshot_policy,
            snapshot_basis=args.snapshot_basis,
        )
        write_result(result, output, args.operator, origin.provenance_sha256)
        print(
            f"Wrote prospective.json, evaluation.json, report.md and manifest.json to {output}; snapshot policy={args.snapshot_policy}; no model training or inference executed."
        )
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"Inventory evaluation failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
