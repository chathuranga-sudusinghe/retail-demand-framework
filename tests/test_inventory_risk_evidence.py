"""Synthetic tests for descriptive inventory evidence outputs."""
import pandas as pd
import pytest

from src.inventory_risk.evidence import (
    DESCRIPTIVE_DIFFERENCE,
    analyze_inventory_evidence,
)


@pytest.fixture
def inventory_panel():
    return pd.DataFrame(
        [
            {
                "Date": "2024-01-02",
                "SKU_ID": "B",
                "Warehouse_ID": "W2",
                "Units_Sold": 4,
                "Inventory_Level": 80,
                "Reorder_Point": 30,
                "Supplier_Lead_Time_Days": 5,
                "Order_Quantity": 0,
                "Demand_Forecast": 4.25,
                "Stockout_Flag": 0,
            },
            {
                "Date": "2024-01-01",
                "SKU_ID": "A",
                "Warehouse_ID": "W1",
                "Units_Sold": 3,
                "Inventory_Level": 70,
                "Reorder_Point": 25,
                "Supplier_Lead_Time_Days": 4,
                "Order_Quantity": 12,
                "Demand_Forecast": 100.5,
                "Stockout_Flag": 1,
            },
        ]
    )


def test_evidence_preserves_keys_and_labels_reorder_difference_as_descriptive(inventory_panel):
    original = inventory_panel.copy(deep=True)

    result = analyze_inventory_evidence(inventory_panel)
    observations = result["observations"]

    assert observations[["SKU_ID", "Warehouse_ID", "Date"]].to_records(index=False).tolist() == [
        ("A", "W1", pd.Timestamp("2024-01-01")),
        ("B", "W2", pd.Timestamp("2024-01-02")),
    ]
    assert observations[DESCRIPTIVE_DIFFERENCE].tolist() == [45, 50]
    assert "Stockout_Flag" not in observations.columns
    pd.testing.assert_frame_equal(inventory_panel, original)


def test_descriptive_summary_includes_source_reference_forecast(inventory_panel):
    summary = analyze_inventory_evidence(inventory_panel)["descriptive_summary"].set_index("field")

    assert set(summary.index) == {
        "Units_Sold",
        "Inventory_Level",
        "Reorder_Point",
        "Supplier_Lead_Time_Days",
        "Order_Quantity",
        "Demand_Forecast",
        DESCRIPTIVE_DIFFERENCE,
    }
    assert summary.loc["Inventory_Level", "mean"] == 75
    assert summary.loc["Reorder_Point", "median"] == 27.5
    assert summary.loc["Demand_Forecast", "mean"] == 52.375
    assert summary.loc["Demand_Forecast", "count"] == 2


def test_order_quantity_availability_reports_zero_and_nonzero_rows(inventory_panel):
    availability = analyze_inventory_evidence(inventory_panel)["order_quantity_availability"].iloc[0]

    assert availability.observations == 2
    assert availability.zero_quantity_rows == 1
    assert availability.nonzero_quantity_rows == 1
    assert availability.zero_quantity_share == 0.5
    assert availability.nonzero_quantity_share == 0.5


def test_reorder_point_evidence_is_summarized_by_sku_and_warehouse(inventory_panel):
    additional_observation = inventory_panel.iloc[[1]].copy()
    additional_observation["Date"] = "2024-01-03"
    additional_observation["Inventory_Level"] = 20
    additional_observation["Reorder_Point"] = 25
    inventory_panel = pd.concat(
        [inventory_panel, additional_observation], ignore_index=True
    )

    summary = analyze_inventory_evidence(inventory_panel)[
        "sku_warehouse_reorder_point_summary"
    ].set_index(["SKU_ID", "Warehouse_ID"])

    sku_summary = summary.loc[("A", "W1")]
    assert sku_summary.observation_count == 2
    assert sku_summary.first_observation_date == pd.Timestamp("2024-01-01")
    assert sku_summary.last_observation_date == pd.Timestamp("2024-01-03")
    assert sku_summary.mean_inventory_minus_reorder_point == 20
    assert sku_summary.median_inventory_minus_reorder_point == 20
    assert sku_summary.min_inventory_minus_reorder_point == -5
    assert sku_summary.max_inventory_minus_reorder_point == 45

    other_summary = summary.loc[("B", "W2")]
    assert other_summary.observation_count == 1
    assert other_summary.mean_inventory_minus_reorder_point == 50


def test_input_validation_rejects_duplicate_keys_and_invalid_values(inventory_panel):
    duplicated = pd.concat([inventory_panel, inventory_panel.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="Duplicate Date"):
        analyze_inventory_evidence(duplicated)

    invalid = inventory_panel.copy()
    invalid.loc[0, "Inventory_Level"] = -1
    with pytest.raises(ValueError, match="negative values"):
        analyze_inventory_evidence(invalid)


def test_missing_calendar_days_are_not_filled_or_inferred(inventory_panel):
    inventory_panel.loc[0, "Date"] = "2024-01-03"

    observations = analyze_inventory_evidence(inventory_panel)["observations"]

    assert len(observations) == len(inventory_panel)
    assert observations.Date.tolist() == [
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-01-03"),
    ]
