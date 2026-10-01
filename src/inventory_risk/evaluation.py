"""Proposed DR-012 exposure evidence and retrospective comparison utilities.

Outputs are structured evidence for later analysis, not approved risk
classifications, actual-stockout predictions, replenishment recommendations,
or a final cross-component schema. DR-012 remains proposed for group approval.
The function keeps each forecast origin and horizon separate and never pools
across origins or horizons.
"""
from __future__ import annotations

import pandas as pd

from src.inventory_risk.input_preparation import (
    EVALUABLE_HORIZONS,
    METHOD_STATUS,
    prepare_inventory_risk_inputs,
)

_GROUP_FIELDS = (
    "run_id",
    "evaluation_stage",
    "evidence_role",
    "model",
    "configuration_id",
    "horizon",
    "forecast_origin",
    "canonical_config_id",
    "fold_id",
    "target_start_date",
    "target_end_date",
    "selection_status",
    "representation_id",
)


def _case_evidence(prepared: pd.DataFrame) -> pd.DataFrame:
    cases = prepared.copy(deep=True)
    cases["inventory_buffer"] = pd.NA
    cases["origin_exposure_state"] = "unavailable"
    cases["forecast_exposure_state"] = "unavailable"
    cases["retrospective_exposure_state"] = "unavailable"
    cases["predicted_margin"] = pd.NA
    cases["retrospective_margin"] = pd.NA
    cases["comparison_case"] = "unavailable"
    cases["confusion_cell"] = pd.NA
    cases["evaluation_unavailable_reasons"] = [[] for _ in range(len(cases))]
    cases["methodology_status"] = METHOD_STATUS

    for index, row in cases.iterrows():
        reasons: list[str] = []
        if not bool(row["inventory_state_available"]):
            reasons.append(str(row["origin_snapshot_reason"]))
            cases.at[index, "comparison_case"] = "unavailable"
            cases.at[index, "evaluation_unavailable_reasons"] = list(dict.fromkeys(reasons))
            continue

        inventory = float(row["_inventory_level_value"])
        reorder = float(row["_reorder_point_value"])
        buffer = inventory - reorder
        cases.at[index, "inventory_buffer"] = buffer
        if buffer <= 0:
            cases.at[index, "origin_exposure_state"] = "already_at_or_below_threshold"
            # This is origin-known evidence, not a forecast skill comparison.
            cases.at[index, "forecast_exposure_state"] = "not_needed_origin_state_known"
            cases.at[index, "retrospective_exposure_state"] = "not_in_primary_comparison"
            cases.at[index, "comparison_case"] = "origin_known_at_or_below_threshold"
            cases.at[index, "evaluation_unavailable_reasons"] = []
            continue

        cases.at[index, "origin_exposure_state"] = "initially_above_threshold"
        horizon = row["_horizon_days"]
        forecast_ready = (
            horizon in EVALUABLE_HORIZONS
            and row["forecast_input_status"] == "available"
            and row["_forecast_demand_value"] is not None
        )
        actual_ready = (
            horizon in EVALUABLE_HORIZONS
            and row["retrospective_input_status"] == "available"
            and row["_observed_demand_value"] is not None
        )

        forecast_crossing: bool | None = None
        actual_crossing: bool | None = None
        if forecast_ready:
            forecast_crossing = float(row["_forecast_demand_value"]) >= buffer
            cases.at[index, "forecast_exposure_state"] = (
                "forecast_crossing" if forecast_crossing else "no_forecast_crossing"
            )
            cases.at[index, "predicted_margin"] = buffer - float(row["_forecast_demand_value"])
        else:
            forecast_reason = (
                row["downstream_use_reason"]
                if horizon == 28
                else row["forecast_input_reason"] or "forecast_exposure_not_assessed"
            )
            reasons.extend(str(forecast_reason).split(";"))

        if actual_ready:
            actual_crossing = float(row["_observed_demand_value"]) >= buffer
            cases.at[index, "retrospective_exposure_state"] = (
                "realised_crossing" if actual_crossing else "no_realised_crossing"
            )
            cases.at[index, "retrospective_margin"] = buffer - float(row["_observed_demand_value"])
        else:
            actual_reason = (
                row["downstream_use_reason"]
                if horizon == 28
                else row["retrospective_input_reason"] or "retrospective_exposure_not_assessed"
            )
            reasons.extend(str(actual_reason).split(";"))

        if forecast_crossing is not None and actual_crossing is not None:
            if forecast_crossing and actual_crossing:
                cell = "TP"
            elif not forecast_crossing and not actual_crossing:
                cell = "TN"
            elif not forecast_crossing and actual_crossing:
                cell = "FN"
            else:
                cell = "FP"
            cases.at[index, "confusion_cell"] = cell
            cases.at[index, "comparison_case"] = "evaluable_paired_case"
        else:
            cases.at[index, "comparison_case"] = "unavailable"
        cases.at[index, "evaluation_unavailable_reasons"] = list(dict.fromkeys(reasons))

    return cases


def _metric(numerator: int, denominator: int) -> tuple[float | None, str]:
    if denominator == 0:
        return None, "unavailable_zero_denominator"
    return numerator / denominator, "available"


def _summary_for_group(group: pd.DataFrame) -> dict[str, object]:
    cells = group["confusion_cell"]
    tp = int(cells.eq("TP").sum())
    tn = int(cells.eq("TN").sum())
    fp = int(cells.eq("FP").sum())
    fn = int(cells.eq("FN").sum())
    n = tp + tn + fp + fn

    metrics = {
        "event_prevalence": _metric(tp + fn, n),
        "missed_crossing_rate": _metric(fn, tp + fn),
        "false_alert_rate": _metric(fp, fp + tn),
        "agreement": _metric(tp + tn, n),
        "precision": _metric(tp, tp + fp),
        "recall": _metric(tp, tp + fn),
    }
    recall = metrics["recall"][0]
    specificity, specificity_status = _metric(tn, tn + fp)
    if recall is None or specificity is None:
        balanced_accuracy, balanced_status = None, "unavailable_undefined_class_rate"
    else:
        balanced_accuracy = 0.5 * (recall + specificity)
        balanced_status = "available"
    metrics["balanced_accuracy"] = (balanced_accuracy, balanced_status)

    result: dict[str, object] = {
        "N": n,
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "origin_known_at_or_below_count": int(group["comparison_case"].eq("origin_known_at_or_below_threshold").sum()),
        "initially_above_threshold_count": int(group["origin_exposure_state"].eq("initially_above_threshold").sum()),
        "evaluable_paired_case_count": n,
        "unavailable_case_count": int(group["comparison_case"].eq("unavailable").sum()),
        "forecast_unavailable_or_gated_count": int((
            group["origin_exposure_state"].eq("initially_above_threshold")
            & (group["forecast_input_status"].ne("available") | ~group["_horizon_days"].isin(EVALUABLE_HORIZONS))
        ).sum()),
        "retrospective_unavailable_or_gated_count": int((
            group["origin_exposure_state"].eq("initially_above_threshold")
            & (group["retrospective_input_status"].ne("available") | ~group["_horizon_days"].isin(EVALUABLE_HORIZONS))
        ).sum()),
        "methodology_status": METHOD_STATUS,
    }
    for name, (value, status) in metrics.items():
        result[name] = value
        result[f"{name}_status"] = status
    return result


def evaluate_inventory_risk(records: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Return proposed exposure cases and per-origin/horizon comparison metrics.

    The primary retrospective comparison includes only initially-above-threshold
    rows with both a valid forecast and a complete realised cumulative target.
    Already-at/below-threshold rows and unavailable rows are reported separately.
    Metrics are not pooled across forecast origins, horizons, folds, or candidate
    models because the cross-origin aggregation protocol remains open.

    Horizon 28 records retain forecast and origin metadata, but no downstream
    forecast/realised exposure or confusion result is calculated until separate
    component-owner/human approval is granted. ``observed_target`` is consumed
    only for retrospective evidence. Source ``Demand_Forecast`` and
    ``Stockout_Flag`` are never used by these calculations.
    """
    prepared = prepare_inventory_risk_inputs(records)
    cases = _case_evidence(prepared)
    group_fields = [column for column in _GROUP_FIELDS if column in cases.columns]
    summary_rows: list[dict[str, object]] = []
    for values, group in cases.groupby(group_fields, dropna=False, sort=True, observed=True):
        if not isinstance(values, tuple):
            values = (values,)
        summary = dict(zip(group_fields, values, strict=True))
        summary.update(_summary_for_group(group))
        summary_rows.append(summary)
    return {"cases": cases, "summary": pd.DataFrame(summary_rows)}
