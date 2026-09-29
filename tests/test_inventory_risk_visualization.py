"""Tests for descriptive inventory-risk visualization data and figures."""
import matplotlib.pyplot as plt
import pandas as pd
import pytest

from src.inventory_risk.evidence import DESCRIPTIVE_DIFFERENCE
from src.visualization.inventory_risk import (
    SOURCE_FORECAST_REFERENCE_LABEL,
    make_inventory_figures,
    prepare_inventory_visual_data,
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
                "Stockout_Flag": 0,
            },
        ]
    )


def test_visual_data_requires_existing_inventory_evidence_columns(inventory_panel):
    with pytest.raises(ValueError, match="Missing required columns: Demand_Forecast"):
        prepare_inventory_visual_data(inventory_panel.drop(columns="Demand_Forecast"))


def test_visual_data_preserves_identity_and_descriptive_comparison(inventory_panel):
    original = inventory_panel.copy(deep=True)

    visual_data = prepare_inventory_visual_data(inventory_panel)
    comparison = visual_data["inventory_reorder_comparison"]

    assert comparison[["SKU_ID", "Warehouse_ID", "Date"]].to_records(
        index=False
    ).tolist() == [
        ("A", "W1", pd.Timestamp("2024-01-01")),
        ("B", "W2", pd.Timestamp("2024-01-02")),
    ]
    assert comparison[DESCRIPTIVE_DIFFERENCE].tolist() == [45, 50]
    pd.testing.assert_frame_equal(inventory_panel, original)


def test_order_quantity_plot_data_reports_zero_and_nonzero_rows(inventory_panel):
    counts = prepare_inventory_visual_data(inventory_panel)[
        "order_quantity_counts"
    ].set_index("quantity_status")

    assert counts.loc["zero_recorded_quantity", "row_count"] == 1
    assert counts.loc["nonzero_recorded_quantity", "row_count"] == 1
    assert counts.loc["zero_recorded_quantity", "row_share"] == 0.5
    assert counts.loc["nonzero_recorded_quantity", "row_share"] == 0.5


def test_source_forecast_is_identified_as_reference_not_project_output(inventory_panel):
    visual_data = prepare_inventory_visual_data(inventory_panel)
    forecast_rows = visual_data["distributions"].loc[
        lambda frame: frame["field"].eq("Demand_Forecast")
    ]

    assert forecast_rows["display_label"].unique().tolist() == [
        SOURCE_FORECAST_REFERENCE_LABEL
    ]
    assert "project-generated" in forecast_rows["display_label"].iloc[0]
    assert "Demand_Forecast" in visual_data["descriptive_summary"]["field"].tolist()


@pytest.mark.parametrize(
    "data, error, message",
    [
        (
            pd.DataFrame(columns=[
                "Date",
                "SKU_ID",
                "Warehouse_ID",
                "Units_Sold",
                "Inventory_Level",
                "Reorder_Point",
                "Supplier_Lead_Time_Days",
                "Order_Quantity",
                "Demand_Forecast",
            ]),
            ValueError,
            "Inventory input data is empty",
        ),
        (
            pd.DataFrame(
                {
                    "Date": ["2024-01-01"],
                    "SKU_ID": ["A"],
                    "Warehouse_ID": ["W1"],
                    "Units_Sold": [1],
                    "Inventory_Level": [-1],
                    "Reorder_Point": [2],
                    "Supplier_Lead_Time_Days": [3],
                    "Order_Quantity": [0],
                    "Demand_Forecast": [1.0],
                }
            ),
            ValueError,
            "negative values",
        ),
    ],
)
def test_empty_or_invalid_data_uses_existing_validation(data, error, message):
    with pytest.raises(error, match=message):
        prepare_inventory_visual_data(data)


def test_make_inventory_figures_returns_unshown_descriptive_figures(inventory_panel):
    figures = make_inventory_figures(inventory_panel)

    assert set(figures) == {
        "descriptive_distributions",
        "order_quantity_availability",
        "inventory_reorder_comparison",
    }
    assert all(len(figure.axes) > 0 for figure in figures.values())
    distribution_titles = [
        axis.get_title() for axis in figures["descriptive_distributions"].axes
    ]
    assert SOURCE_FORECAST_REFERENCE_LABEL in distribution_titles

    for figure in figures.values():
        plt.close(figure)
