from __future__ import annotations

import pandas as pd
import pytest

from src.inventory_risk.input_preparation import (
    METHOD_STATUS,
    prepare_inventory_risk_inputs,
)


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
        "supplier_lead_time_available_at_origin": True,
        "Order_Quantity": 0,
        "Demand_Forecast": 999,
        "Stockout_Flag": 0,
        "origin_snapshot_available": True,
        "origin_snapshot_unavailable_reason": None,
        "unavailable_information_reasons": [],
        "assumptions": ["provided test assumption"],
        "limitations": ["provided test limitation"],
    }
    row.update(updates)
    return row


def test_preparation_preserves_identity_timing_provenance_and_source_fields():
    source = pd.DataFrame([forecast_inventory_row()])
    result = prepare_inventory_risk_inputs(source)

    assert result.loc[0, "SKU_ID"] == "SKU001"
    assert result.loc[0, "Warehouse_ID"] == "WH001"
    assert result.loc[0, "forecast_origin"] == "2024-01-01"
    assert result.loc[0, "horizon"] == 7
    assert result.loc[0, "Date"] == "2024-01-01"
    assert result.loc[0, "run_id"] == "run-a"
    assert result.loc[0, "model"] == "xgboost"
    assert result.loc[0, "configuration_id"] == "GBM001"
    assert result.loc[0, "Demand_Forecast"] == 999
    assert result.loc[0, "prediction"] == 8.5
    assert result.loc[0, "Stockout_Flag"] == 0
    assert result.loc[0, "methodology_status"] == METHOD_STATUS
    assert result.loc[0, "origin_snapshot_status"] == "available"
    assert result.loc[0, "forecast_input_status"] == "available"
    assert result.loc[0, "retrospective_input_status"] == "available"
    assert result.loc[0, "assumptions"] == ["provided test assumption"]
    assert result.loc[0, "limitations"] == ["provided test limitation"]
    pd.testing.assert_frame_equal(source, pd.DataFrame([forecast_inventory_row()]))


def test_source_demand_forecast_is_optional_and_never_substitutes_prediction():
    row = forecast_inventory_row()
    del row["Demand_Forecast"]
    result = prepare_inventory_risk_inputs(pd.DataFrame([row]))

    assert result.loc[0, "prediction"] == 8.5
    assert "Demand_Forecast" not in result
    assert result.loc[0, "forecast_input_status"] == "available"


def test_missing_snapshot_availability_is_unknown_and_kept_with_reason():
    result = prepare_inventory_risk_inputs(
        pd.DataFrame([forecast_inventory_row(origin_snapshot_available=pd.NA)])
    )

    assert result.loc[0, "origin_snapshot_status"] == "unknown"
    assert (
        "origin_snapshot_availability_not_established"
        in result.loc[0, "preparation_unavailable_reasons"]
    )
    assert not result.loc[0, "inventory_state_available"]


def test_future_or_nonmatching_inventory_record_is_not_used_as_origin_snapshot():
    result = prepare_inventory_risk_inputs(
        pd.DataFrame([forecast_inventory_row(Date="2024-01-02")])
    )

    assert result.loc[0, "origin_snapshot_status"] == "unavailable"
    assert (
        result.loc[0, "origin_snapshot_reason"]
        == "inventory_record_date_does_not_match_forecast_origin"
    )
    assert not result.loc[0, "inventory_state_available"]


@pytest.mark.parametrize(
    ("updates", "reason"),
    [
        (
            {"horizon": 28, "target_end_date": "2024-01-29"},
            "28_day_downstream_use_requires_separate_approval",
        ),
        ({"prediction": -2}, "negative_forecast_handling_not_approved"),
        ({"prediction": float("inf")}, "forecast_missing_or_nonfinite"),
        (
            {"target_end_date": "2024-01-09"},
            "forecast_target_interval_does_not_match_origin_and_horizon",
        ),
        (
            {"prediction_status": "unavailable"},
            "forecast_prediction_status_not_available",
        ),
        (
            {"target_status": "incomplete", "observed_target": None},
            "realised_horizon_demand_unavailable",
        ),
    ],
)
def test_problematic_or_gated_inputs_are_retained_as_unavailable(updates, reason):
    row = forecast_inventory_row(**updates)
    result = prepare_inventory_risk_inputs(pd.DataFrame([row]))

    assert len(result) == 1
    if reason == "28_day_downstream_use_requires_separate_approval":
        assert result.loc[0, "downstream_use_reason"] == reason
        assert result.loc[0, "forecast_input_status"] == "available"
    else:
        assert reason in result.loc[0, "preparation_unavailable_reasons"]


def test_missing_columns_and_duplicate_forecast_keys_are_rejected():
    frame = pd.DataFrame([forecast_inventory_row()])
    with pytest.raises(ValueError, match="Missing required columns"):
        prepare_inventory_risk_inputs(frame.drop(columns="prediction"))

    with pytest.raises(ValueError, match="Duplicate forecast records"):
        prepare_inventory_risk_inputs(pd.concat([frame, frame], ignore_index=True))


def test_same_sku_warehouse_origin_model_and_configuration_allow_distinct_horizons():
    origin = pd.Timestamp("2024-01-01")
    horizons = (1, 7, 14, 28)
    records = pd.DataFrame(
        [
            forecast_inventory_row(
                horizon=horizon,
                target_end_date=(origin + pd.Timedelta(days=horizon)).strftime(
                    "%Y-%m-%d"
                ),
            )
            for horizon in horizons
        ]
    )

    prepared = prepare_inventory_risk_inputs(records)

    assert prepared["horizon"].tolist() == list(horizons)
    assert prepared["forecast_input_status"].tolist() == ["available"] * len(horizons)
    assert prepared["downstream_use_status"].tolist() == [
        "approved_method",
        "approved_method",
        "approved_method",
        "not_approved_for_downstream_use",
    ]
    assert prepared["methodology_status"].tolist() == ["group_approved"] * 4
    assert prepared["downstream_use_reason"].tolist() == [
        "",
        "",
        "",
        "28_day_downstream_use_requires_separate_approval",
    ]


def test_context_fields_are_preserved_but_not_reinterpreted_as_receipts():
    result = prepare_inventory_risk_inputs(pd.DataFrame([forecast_inventory_row()]))

    assert result.loc[0, "Supplier_Lead_Time_Days"] == 7
    assert result.loc[0, "Order_Quantity"] == 0
    assert result.loc[0, "lead_time_context_status"] == "available_as_context_only"
    assert result.loc[0, "lead_time_horizon_relation"] == "horizon_equal_to_lead_time"
    assert result.loc[0, "order_quantity_context_status"] == "unknown"
    assert (
        "Order_Quantity_availability_at_origin_not_established"
        in result.loc[0, "preparation_unavailable_reasons"]
    )


def test_order_quantity_is_context_only_when_origin_availability_is_explicit():
    result = prepare_inventory_risk_inputs(
        pd.DataFrame(
            [
                forecast_inventory_row(
                    order_quantity_available_at_origin=True,
                )
            ]
        )
    )

    assert result.loc[0, "order_quantity_context_status"] == "available_as_context_only"
    assert result.loc[0, "Order_Quantity"] == 0


@pytest.mark.parametrize(
    ("column", "status_column", "reason"),
    [
        ("prediction", "forecast_input_status", "forecast_missing_or_nonfinite"),
        (
            "observed_target",
            "retrospective_input_status",
            "realised_horizon_demand_unavailable",
        ),
        (
            "Inventory_Level",
            "inventory_state_available",
            "inventory_level_missing_or_invalid",
        ),
        (
            "Reorder_Point",
            "inventory_state_available",
            "reorder_point_missing_or_invalid",
        ),
    ],
)
@pytest.mark.parametrize(
    "value", [None, float("nan"), pd.NA, float("inf"), float("-inf"), "invalid"]
)
def test_mixed_invalid_numeric_values_remain_unavailable(
    column, status_column, reason, value
):
    records = pd.DataFrame(
        [
            forecast_inventory_row(SKU_ID="VALID"),
            forecast_inventory_row(SKU_ID="INVALID", **{column: value}),
        ]
    )
    result = prepare_inventory_risk_inputs(records).set_index("SKU_ID")

    assert len(result) == 2
    assert result.loc["VALID", "forecast_input_status"] == "available"
    assert result.loc["VALID", "retrospective_input_status"] == "available"
    invalid = result.loc["INVALID"]
    if status_column == "inventory_state_available":
        assert not invalid[status_column]
    else:
        assert invalid[status_column] == "unavailable"
    assert reason in invalid["preparation_unavailable_reasons"]


@pytest.mark.parametrize("column", ["Inventory_Level", "Reorder_Point"])
@pytest.mark.parametrize("value", [-1, 1.5])
def test_negative_or_fractional_inventory_counts_remain_unavailable(column, value):
    result = prepare_inventory_risk_inputs(
        pd.DataFrame(
            [
                forecast_inventory_row(SKU_ID="VALID"),
                forecast_inventory_row(SKU_ID="INVALID", **{column: value}),
            ]
        )
    ).set_index("SKU_ID")

    assert not result.loc["INVALID", "inventory_state_available"]
    reason = (
        "inventory_level_missing_or_invalid"
        if column == "Inventory_Level"
        else "reorder_point_missing_or_invalid"
    )
    assert reason in result.loc["INVALID", "preparation_unavailable_reasons"]


@pytest.mark.parametrize(
    "horizon",
    [None, float("nan"), pd.NA, float("inf"), float("-inf"), "invalid", 0, 2, 1.5],
)
def test_mixed_invalid_horizons_are_retained_without_date_arithmetic_errors(horizon):
    result = prepare_inventory_risk_inputs(
        pd.DataFrame(
            [
                forecast_inventory_row(SKU_ID="VALID"),
                forecast_inventory_row(SKU_ID="INVALID", horizon=horizon),
            ]
        )
    ).set_index("SKU_ID")

    assert len(result) == 2
    assert result.loc["VALID", "forecast_input_status"] == "available"
    invalid = result.loc["INVALID"]
    assert invalid["forecast_input_status"] == "unavailable"
    assert invalid["retrospective_input_status"] == "unavailable"
    assert invalid["downstream_use_status"] == "unavailable"
    assert "unsupported_or_invalid_forecast_horizon" in invalid["forecast_input_reason"]
    assert (
        "unsupported_or_invalid_forecast_horizon"
        in invalid["retrospective_input_reason"]
    )


@pytest.mark.parametrize(
    ("column", "value", "status_column", "reason"),
    [
        (
            "prediction_status",
            pd.NA,
            "forecast_input_status",
            "forecast_prediction_status_not_available",
        ),
        (
            "eligibility_status",
            pd.NA,
            "forecast_input_status",
            "forecast_eligibility_status_not_eligible",
        ),
        (
            "target_status",
            pd.NA,
            "retrospective_input_status",
            "retrospective_target_status_not_complete",
        ),
        (
            "target_status",
            "incomplete",
            "retrospective_input_status",
            "retrospective_target_status_not_complete",
        ),
    ],
)
def test_missing_or_incomplete_status_is_unavailable_with_valid_numeric_inputs(
    column, value, status_column, reason
):
    records = pd.DataFrame(
        [
            forecast_inventory_row(SKU_ID="VALID"),
            forecast_inventory_row(SKU_ID="INVALID", **{column: value}),
        ]
    )
    # Keep actual pd.NA cells instead of letting pandas infer NaN object cells.
    records[column] = records[column].astype("string")
    if value is pd.NA:
        assert records.loc[1, column] is pd.NA
    result = prepare_inventory_risk_inputs(records).set_index("SKU_ID")

    assert result.loc["VALID", status_column] == "available"
    invalid = result.loc["INVALID"]
    assert invalid["prediction"] == 8.5
    assert invalid["observed_target"] == 9
    assert invalid[status_column] == "unavailable"
    assert reason in invalid["preparation_unavailable_reasons"]
    assert (
        "realised_horizon_demand_unavailable"
        not in invalid["preparation_unavailable_reasons"]
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
def test_retrospective_input_requires_exact_origin_horizon_interval(updates):
    result = prepare_inventory_risk_inputs(
        pd.DataFrame(
            [
                forecast_inventory_row(SKU_ID="VALID"),
                forecast_inventory_row(SKU_ID="INVALID", **updates),
            ]
        )
    ).set_index("SKU_ID")

    assert result.loc["VALID", "retrospective_input_status"] == "available"
    invalid = result.loc["INVALID"]
    assert invalid["observed_target"] == 9
    assert invalid["target_status"] == "complete"
    assert invalid["forecast_input_status"] == "unavailable"
    assert invalid["retrospective_input_status"] == "unavailable"
    assert (
        "forecast_target_interval_does_not_match_origin_and_horizon"
        in invalid["retrospective_input_reason"]
    )
