"""Proposed DR-012 exposure evidence and retrospective comparison utilities.

Outputs are structured evidence for later analysis, not approved risk
classifications, actual-stockout predictions, replenishment recommendations,
or a final cross-component schema. DR-012 remains proposed for group approval.
The function keeps each forecast origin and horizon separate and never pools
across origins or horizons.
"""

from __future__ import annotations

from typing import Any, cast

import pandas as pd

from src.inventory_risk.input_preparation import (
    EVALUABLE_HORIZONS,
    METHOD_STATUS,
    prepare_inventory_risk_inputs,
)

SCENARIO_LIMITATION = (
    "Constructed starting balances are hypothetical; source origin availability "
    "is not established by this scenario."
)

_GROUP_FIELDS = (
    "inventory_basis",
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


def _case_evidence(
    prepared: pd.DataFrame, *, scenario_basis: str | None = None
) -> pd.DataFrame:
    cases = prepared.copy(deep=True)
    cases["inventory_basis"] = (
        "constructed_origin_scenario" if scenario_basis else "source_availability"
    )
    cases["snapshot_assumption"] = scenario_basis
    cases["scenario_inventory_state_available"] = False
    cases["analysis_inventory_state_available"] = cases["inventory_state_available"]
    if scenario_basis:
        cases["method_assumptions"] = cases["method_assumptions"].map(
            lambda values: (*values[1:], scenario_basis)
        )
        cases["method_limitations"] = cases["method_limitations"].map(
            lambda values: (
                *values,
                SCENARIO_LIMITATION,
            )
        )
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

    # Object cells support lists; pandas-stubs restrict the scalar setter's types.
    reason_cells = cast(Any, cases.at)
    for index, row in cases.iterrows():
        reasons: list[str] = []
        inventory_available = bool(row["inventory_state_available"])
        if scenario_basis:
            inventory_available = bool(
                pd.notna(row["_forecast_origin_date"])
                and pd.notna(row["_inventory_record_date"])
                and row["_forecast_origin_date"] == row["_inventory_record_date"]
                and pd.notna(row["_inventory_level_value"])
                and pd.notna(row["_reorder_point_value"])
            )
            cases.at[index, "scenario_inventory_state_available"] = inventory_available
            cases.at[index, "analysis_inventory_state_available"] = inventory_available
        if not inventory_available:
            if scenario_basis:
                reasons.append("scenario_origin_snapshot_missing_or_invalid")
            reasons.extend(row["preparation_unavailable_reasons"])
            reasons.append(str(row["origin_snapshot_reason"]))
            cases.at[index, "comparison_case"] = "unavailable"
            reason_cells[index, "evaluation_unavailable_reasons"] = list(
                dict.fromkeys(reason for reason in reasons if reason.strip())
            )
            continue

        inventory = float(row["_inventory_level_value"])
        reorder = float(row["_reorder_point_value"])
        buffer = inventory - reorder
        cases.at[index, "inventory_buffer"] = buffer
        if buffer <= 0:
            cases.at[index, "origin_exposure_state"] = (
                "scenario_already_at_or_below_threshold"
                if scenario_basis
                else "already_at_or_below_threshold"
            )
            # This is origin-known evidence, not a forecast skill comparison.
            cases.at[index, "forecast_exposure_state"] = (
                "not_needed_scenario_origin_state"
                if scenario_basis
                else "not_needed_origin_state_known"
            )
            cases.at[index, "retrospective_exposure_state"] = (
                "not_in_primary_comparison"
            )
            cases.at[index, "comparison_case"] = (
                "scenario_at_or_below_threshold"
                if scenario_basis
                else "origin_known_at_or_below_threshold"
            )
            reason_cells[index, "evaluation_unavailable_reasons"] = []
            continue

        cases.at[index, "origin_exposure_state"] = (
            "scenario_initially_above_threshold"
            if scenario_basis
            else "initially_above_threshold"
        )
        horizon = row["_horizon_days"]
        forecast_ready = (
            horizon in EVALUABLE_HORIZONS
            and row["forecast_input_status"] == "available"
            and pd.notna(row["_forecast_demand_value"])
        )
        actual_ready = (
            horizon in EVALUABLE_HORIZONS
            and row["retrospective_input_status"] == "available"
            and pd.notna(row["_observed_demand_value"])
        )

        forecast_crossing: bool | None = None
        actual_crossing: bool | None = None
        if forecast_ready:
            forecast_crossing = float(row["_forecast_demand_value"]) >= buffer
            cases.at[index, "forecast_exposure_state"] = (
                "forecast_crossing" if forecast_crossing else "no_forecast_crossing"
            )
            cases.at[index, "predicted_margin"] = buffer - float(
                row["_forecast_demand_value"]
            )
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
            cases.at[index, "retrospective_margin"] = buffer - float(
                row["_observed_demand_value"]
            )
        else:
            actual_reason = (
                row["downstream_use_reason"]
                if horizon == 28
                else row["retrospective_input_reason"]
                or "retrospective_exposure_not_assessed"
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
        reason_cells[index, "evaluation_unavailable_reasons"] = list(
            dict.fromkeys(reason for reason in reasons if reason.strip())
        )

    return cases


def _metric(numerator: int, denominator: int) -> tuple[float | None, str]:
    if denominator == 0:
        return None, "unavailable_zero_denominator"
    return numerator / denominator, "available"


def _summary_for_group(group: pd.DataFrame) -> dict[str, object]:
    initially_above = group["origin_exposure_state"].isin(
        ("initially_above_threshold", "scenario_initially_above_threshold")
    )
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
        "origin_known_at_or_below_count": int(
            group["comparison_case"].eq("origin_known_at_or_below_threshold").sum()
        ),
        "scenario_at_or_below_count": int(
            group["comparison_case"].eq("scenario_at_or_below_threshold").sum()
        ),
        "initially_above_threshold_count": int(initially_above.sum()),
        "evaluable_paired_case_count": n,
        "unavailable_case_count": int(group["comparison_case"].eq("unavailable").sum()),
        "forecast_unavailable_or_gated_count": int(
            (
                initially_above
                & (
                    group["forecast_input_status"].ne("available")
                    | ~group["_horizon_days"].isin(EVALUABLE_HORIZONS)
                )
            ).sum()
        ),
        "retrospective_unavailable_or_gated_count": int(
            (
                initially_above
                & (
                    group["retrospective_input_status"].ne("available")
                    | ~group["_horizon_days"].isin(EVALUABLE_HORIZONS)
                )
            ).sum()
        ),
        "methodology_status": METHOD_STATUS,
    }
    for name, (value, status) in metrics.items():
        result[name] = value
        result[f"{name}_status"] = status
    return result


def evaluate_inventory_risk(
    records: pd.DataFrame, *, scenario_basis: str | None = None
) -> dict[str, pd.DataFrame]:
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

    An explicit nonblank ``scenario_basis`` evaluates a hypothetical scenario
    from same-origin recorded balances. It never changes source availability
    markers/statuses. Scenario origin states and counts are labelled separately
    from origin-known source evidence. Omitting it retains the existing gate.
    An explicit False marker also remains unavailable as source evidence; an
    explicitly requested counterfactual can still use valid same-origin quantities
    as hypothetical starting balances. It does not assert that those balances
    were actually available at forecast issuance.
    """
    if scenario_basis is not None and (
        not isinstance(scenario_basis, str) or not scenario_basis.strip()
    ):
        raise ValueError("A constructed scenario requires a nonblank snapshot basis.")
    prepared = prepare_inventory_risk_inputs(records)
    cases = _case_evidence(prepared, scenario_basis=scenario_basis)
    group_fields = [column for column in _GROUP_FIELDS if column in cases.columns]
    summary_rows: list[dict[str, object]] = []
    for values, group in cases.groupby(
        group_fields, dropna=False, sort=True, observed=True
    ):
        if not isinstance(values, tuple):
            values = (values,)
        summary = dict(zip(group_fields, values, strict=True))
        summary.update(_summary_for_group(group))
        summary_rows.append(summary)
    return {"cases": cases, "summary": pd.DataFrame(summary_rows)}
