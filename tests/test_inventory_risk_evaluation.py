from __future__ import annotations

import pandas as pd
import pytest

from src.inventory_risk.evaluation import evaluate_inventory_risk


def forecast_inventory_row(**updates):
    row = {
        "SKU_ID": "SKU001",
        "Warehouse_ID": "WH001",
        "forecast_origin": "2024-01-01",
        "horizon": 7,
        "target_start_date": "2024-01-02",
        "target_end_date": "2024-01-08",
        "prediction": 8.5,
        "observed_target": 9,
        "prediction_status": "available",
        "target_status": "complete",
        "eligibility_status": "eligible",
        "run_id": "run-a",
        "evaluation_stage": "validation",
        "evidence_role": "primary",
        "model": "xgboost",
        "configuration_id": "GBM001",
        "canonical_config_id": "GBM001",
        "fold_id": 1,
        "selection_status": "candidate",
        "representation_id": "matched-full-one-hot-v1",
        "Date": "2024-01-01",
        "Inventory_Level": 20,
        "Reorder_Point": 10,
        "Supplier_Lead_Time_Days": 7,
        "Order_Quantity": 0,
        "Demand_Forecast": 999,
        "Stockout_Flag": 0,
        "origin_snapshot_available": True,
        "origin_snapshot_unavailable_reason": None,
        "unavailable_information_reasons": [],
    }
    row.update(updates)
    return row


def make_row(sku, *, inventory=20, reorder=10, prediction=10, observed=10, **updates):
    values = forecast_inventory_row(
        SKU_ID=sku,
        Inventory_Level=inventory,
        Reorder_Point=reorder,
        prediction=prediction,
        observed_target=observed,
        **updates,
    )
    return values


def test_evaluation_reports_documented_counts_rates_and_margin_evidence():
    rows = [
        make_row("TP", prediction=10, observed=10),
        make_row("TN", prediction=9, observed=9),
        make_row("FP", prediction=10, observed=9),
        make_row("FN", prediction=9, observed=10),
        make_row("KNOWN", inventory=10, prediction=None, observed=None),
    ]
    result = evaluate_inventory_risk(pd.DataFrame(rows))
    summary = result["summary"].iloc[0]
    cases = result["cases"].set_index("SKU_ID")

    assert (
        summary["N"],
        summary["TP"],
        summary["TN"],
        summary["FP"],
        summary["FN"],
    ) == (4, 1, 1, 1, 1)
    assert summary["origin_known_at_or_below_count"] == 1
    assert summary["initially_above_threshold_count"] == 4
    assert summary["event_prevalence"] == 0.5
    assert summary["missed_crossing_rate"] == 0.5
    assert summary["false_alert_rate"] == 0.5
    assert summary["agreement"] == 0.5
    assert summary["precision"] == 0.5
    assert summary["recall"] == 0.5
    assert summary["balanced_accuracy"] == 0.5
    assert cases.loc["TP", "confusion_cell"] == "TP"
    assert cases.loc["TN", "confusion_cell"] == "TN"
    assert cases.loc["FP", "confusion_cell"] == "FP"
    assert cases.loc["FN", "confusion_cell"] == "FN"
    assert (
        cases.loc["KNOWN", "origin_exposure_state"] == "already_at_or_below_threshold"
    )
    assert cases.loc["KNOWN", "comparison_case"] == "origin_known_at_or_below_threshold"
    assert cases.loc["TP", "predicted_margin"] == 0
    assert cases.loc["TP", "retrospective_margin"] == 0
    assert cases.loc["TP", "methodology_status"] == "proposed_for_group_approval"


def test_28_day_keeps_origin_evidence_but_does_not_calculate_downstream_crossing():
    result = evaluate_inventory_risk(
        pd.DataFrame(
            [
                make_row(
                    "S28",
                    horizon=28,
                    target_end_date="2024-01-29",
                    prediction=50,
                    observed=50,
                )
            ]
        )
    )
    case = result["cases"].iloc[0]
    summary = result["summary"].iloc[0]

    assert case["origin_exposure_state"] == "initially_above_threshold"
    assert case["forecast_exposure_state"] == "unavailable"
    assert case["retrospective_exposure_state"] == "unavailable"
    assert case["confusion_cell"] is pd.NA or pd.isna(case["confusion_cell"])
    assert (
        "28_day_downstream_use_requires_separate_approval"
        in case["evaluation_unavailable_reasons"]
    )
    assert summary["N"] == 0
    assert summary["unavailable_case_count"] == 1
    assert summary["forecast_unavailable_or_gated_count"] == 1
    assert summary["retrospective_unavailable_or_gated_count"] == 1


def test_unavailable_snapshot_is_retained_and_not_scored():
    result = evaluate_inventory_risk(
        pd.DataFrame([make_row("NO_SNAPSHOT", origin_snapshot_available=False)])
    )
    case = result["cases"].iloc[0]
    summary = result["summary"].iloc[0]

    assert case["SKU_ID"] == "NO_SNAPSHOT"
    assert case["origin_exposure_state"] == "unavailable"
    assert case["comparison_case"] == "unavailable"
    assert (
        "origin_snapshot_not_available_at_forecast_origin"
        in case["evaluation_unavailable_reasons"]
    )
    assert summary["N"] == 0
    assert summary["unavailable_case_count"] == 1


def test_undefined_denominators_are_reported_as_unavailable():
    result = evaluate_inventory_risk(
        pd.DataFrame([make_row("ONLY_TP", prediction=10, observed=10)])
    )
    summary = result["summary"].iloc[0]

    assert summary["precision"] == 1
    assert summary["recall"] == 1
    assert summary["missed_crossing_rate"] == 0
    assert pd.isna(summary["false_alert_rate"])
    assert summary["false_alert_rate_status"] == "unavailable_zero_denominator"
    assert pd.isna(summary["balanced_accuracy"])
    assert summary["balanced_accuracy_status"] == "unavailable_undefined_class_rate"


def test_metrics_with_no_retrospective_crossing_have_explicit_undefined_rates():
    result = evaluate_inventory_risk(
        pd.DataFrame([make_row("ONLY_TN", prediction=9, observed=9)])
    )
    summary = result["summary"].iloc[0]

    assert summary["N"] == 1
    assert summary["TN"] == 1
    assert summary["event_prevalence"] == 0
    assert pd.isna(summary["missed_crossing_rate"])
    assert summary["missed_crossing_rate_status"] == "unavailable_zero_denominator"
    assert pd.isna(summary["recall"])
    assert pd.isna(summary["precision"])
    assert pd.isna(summary["balanced_accuracy"])


def test_metrics_are_separate_for_horizons_and_forecast_origins():
    rows = [
        make_row(
            "H1", horizon=1, target_end_date="2024-01-02", prediction=10, observed=10
        ),
        make_row("H7", horizon=7, prediction=9, observed=9),
        make_row(
            "NEXT_ORIGIN",
            forecast_origin="2024-01-02",
            Date="2024-01-02",
            target_start_date="2024-01-03",
            target_end_date="2024-01-09",
            prediction=10,
            observed=10,
        ),
    ]
    result = evaluate_inventory_risk(pd.DataFrame(rows))

    assert len(result["summary"]) == 3
    assert set(result["summary"]["horizon"]) == {1, 7}
    assert set(result["summary"]["forecast_origin"]) == {"2024-01-01", "2024-01-02"}


def test_source_forecast_and_stockout_flag_do_not_change_evaluation():
    first = make_row(
        "S1", Demand_Forecast=0, Stockout_Flag=0, prediction=10, observed=10
    )
    second = make_row(
        "S2", Demand_Forecast=10000, Stockout_Flag=0, prediction=10, observed=10
    )
    result = evaluate_inventory_risk(pd.DataFrame([first, second]))

    assert result["summary"].loc[0, "TP"] == 2
    assert result["cases"]["Demand_Forecast"].tolist() == [0, 10000]
    assert result["cases"]["Stockout_Flag"].tolist() == [0, 0]


@pytest.mark.parametrize("horizon", [1, 7, 14])
def test_documented_proposed_horizons_are_kept_separate(horizon):
    end_date = pd.Timestamp("2024-01-01") + pd.Timedelta(days=horizon)
    start_date = pd.Timestamp("2024-01-02")
    result = evaluate_inventory_risk(
        pd.DataFrame(
            [
                make_row(
                    f"S{horizon}",
                    horizon=horizon,
                    target_start_date=start_date.strftime("%Y-%m-%d"),
                    target_end_date=end_date.strftime("%Y-%m-%d"),
                    prediction=10,
                    observed=10,
                )
            ]
        )
    )
    case = result["cases"].iloc[0]

    assert case["confusion_cell"] == "TP"
    assert case["methodology_status"] == "proposed_for_group_approval"


def assert_invalid_case_is_not_scored(result, reason):
    cases = result["cases"].set_index("SKU_ID")
    assert len(cases) == 2
    assert cases.loc["VALID", "confusion_cell"] == "TP"
    invalid = cases.loc["INVALID"]
    assert invalid["comparison_case"] == "unavailable"
    assert pd.isna(invalid["confusion_cell"])
    assert reason in invalid["evaluation_unavailable_reasons"]
    assert all(reason.strip() for reason in invalid["evaluation_unavailable_reasons"])
    totals = result["summary"][["N", "TP", "TN", "FP", "FN"]].sum()
    assert tuple(totals) == (1, 1, 0, 0, 0)
    assert result["summary"]["unavailable_case_count"].sum() == 1
    return invalid


@pytest.mark.parametrize(
    ("column", "reason"),
    [
        ("prediction", "forecast_missing_or_nonfinite"),
        ("observed_target", "realised_horizon_demand_unavailable"),
        ("Inventory_Level", "inventory_level_missing_or_invalid"),
        ("Reorder_Point", "reorder_point_missing_or_invalid"),
    ],
)
@pytest.mark.parametrize(
    "value", [None, float("nan"), pd.NA, float("inf"), float("-inf"), "invalid"]
)
def test_mixed_invalid_numeric_values_never_enter_confusion_counts(
    column, reason, value
):
    invalid_row = make_row("INVALID")
    invalid_row[column] = value
    result = evaluate_inventory_risk(pd.DataFrame([make_row("VALID"), invalid_row]))
    invalid = assert_invalid_case_is_not_scored(result, reason)

    if column != "observed_target":
        assert invalid["forecast_exposure_state"] == "unavailable"
        assert pd.isna(invalid["predicted_margin"])
    if column != "prediction":
        assert invalid["retrospective_exposure_state"] == "unavailable"
        assert pd.isna(invalid["retrospective_margin"])
    if column in ("Inventory_Level", "Reorder_Point"):
        assert invalid["origin_exposure_state"] == "unavailable"
        assert pd.isna(invalid["inventory_buffer"])


@pytest.mark.parametrize("column", ["Inventory_Level", "Reorder_Point"])
@pytest.mark.parametrize("value", [-1, 1.5])
def test_invalid_inventory_counts_preserve_preparation_failure_reasons(column, value):
    invalid_row = make_row(
        "INVALID", unavailable_information_reasons=["upstream warning", ""]
    )
    invalid_row[column] = value
    result = evaluate_inventory_risk(pd.DataFrame([make_row("VALID"), invalid_row]))
    reason = (
        "inventory_level_missing_or_invalid"
        if column == "Inventory_Level"
        else "reorder_point_missing_or_invalid"
    )
    invalid = assert_invalid_case_is_not_scored(result, reason)

    assert "upstream warning" in invalid["preparation_unavailable_reasons"]
    assert "upstream warning" in invalid["evaluation_unavailable_reasons"]
    assert invalid["origin_exposure_state"] == "unavailable"
    assert pd.isna(invalid["inventory_buffer"])
    assert pd.isna(invalid["predicted_margin"])
    assert pd.isna(invalid["retrospective_margin"])


@pytest.mark.parametrize(
    "horizon",
    [None, float("nan"), pd.NA, float("inf"), float("-inf"), "invalid", 0, 2, 1.5],
)
def test_mixed_invalid_horizons_never_enter_confusion_counts(horizon):
    result = evaluate_inventory_risk(
        pd.DataFrame(
            [
                make_row("VALID"),
                make_row("INVALID", horizon=horizon),
            ]
        )
    )
    invalid = assert_invalid_case_is_not_scored(
        result, "unsupported_or_invalid_forecast_horizon"
    )

    assert invalid["forecast_exposure_state"] == "unavailable"
    assert invalid["retrospective_exposure_state"] == "unavailable"
    assert pd.isna(invalid["predicted_margin"])
    assert pd.isna(invalid["retrospective_margin"])


@pytest.mark.parametrize(
    ("column", "value", "reason", "exposure_column", "margin_column"),
    [
        (
            "prediction_status",
            pd.NA,
            "forecast_prediction_status_not_available",
            "forecast_exposure_state",
            "predicted_margin",
        ),
        (
            "eligibility_status",
            pd.NA,
            "forecast_eligibility_status_not_eligible",
            "forecast_exposure_state",
            "predicted_margin",
        ),
        (
            "target_status",
            pd.NA,
            "retrospective_target_status_not_complete",
            "retrospective_exposure_state",
            "retrospective_margin",
        ),
        (
            "target_status",
            "incomplete",
            "retrospective_target_status_not_complete",
            "retrospective_exposure_state",
            "retrospective_margin",
        ),
    ],
)
def test_missing_or_incomplete_status_never_enters_confusion_counts(
    column, value, reason, exposure_column, margin_column
):
    records = pd.DataFrame(
        [
            make_row("VALID"),
            make_row("INVALID", **{column: value}),
        ]
    )
    records[column] = records[column].astype("string")
    if value is pd.NA:
        assert records.loc[1, column] is pd.NA
    result = evaluate_inventory_risk(records)
    invalid = assert_invalid_case_is_not_scored(result, reason)

    assert invalid["prediction"] == 10
    assert invalid["observed_target"] == 10
    assert invalid[exposure_column] == "unavailable"
    assert pd.isna(invalid[margin_column])
    assert (
        "realised_horizon_demand_unavailable"
        not in invalid["evaluation_unavailable_reasons"]
    )


@pytest.mark.parametrize(
    "updates",
    [
        {"target_start_date": "2024-01-01"},
        {"target_start_date": "2024-01-03"},
        {"target_end_date": "2024-01-09"},
        {"target_start_date": None},
        {"target_end_date": pd.NA},
    ],
)
def test_invalid_retrospective_interval_produces_no_crossing_or_margin(updates):
    result = evaluate_inventory_risk(
        pd.DataFrame(
            [
                make_row("VALID"),
                make_row("INVALID", **updates),
            ]
        )
    )
    invalid = assert_invalid_case_is_not_scored(
        result, "forecast_target_interval_does_not_match_origin_and_horizon"
    )

    assert invalid["observed_target"] == 10
    assert invalid["target_status"] == "complete"
    assert invalid["retrospective_input_status"] == "unavailable"
    assert invalid["retrospective_exposure_state"] == "unavailable"
    assert pd.isna(invalid["retrospective_margin"])
