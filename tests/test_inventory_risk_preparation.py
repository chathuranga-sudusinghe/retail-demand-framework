"""Tests for inventory-risk input preparation; no project data is embedded."""
import numpy as np
import pandas as pd
import pytest

from src.inventory_risk.input_preparation import (
    REQUIRED_COLUMNS,
    load_inventory_inputs,
    prepare_inventory_inputs,
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


def test_prepares_required_fields_sorted_and_does_not_mutate(inventory_panel):
    original = inventory_panel.copy(deep=True)

    prepared = prepare_inventory_inputs(inventory_panel)

    assert prepared.columns.tolist() == list(REQUIRED_COLUMNS)
    assert prepared[["SKU_ID", "Warehouse_ID", "Date"]].to_records(index=False).tolist() == [
        ("A", "W1", pd.Timestamp("2024-01-01")),
        ("B", "W2", pd.Timestamp("2024-01-02")),
    ]
    assert prepared["Demand_Forecast"].tolist() == [100.5, 4.25]
    assert "Stockout_Flag" not in prepared.columns
    pd.testing.assert_frame_equal(inventory_panel, original)


def test_missing_required_column_is_rejected(inventory_panel):
    with pytest.raises(ValueError, match="Missing required columns: Demand_Forecast"):
        prepare_inventory_inputs(inventory_panel.drop(columns="Demand_Forecast"))


@pytest.mark.parametrize("column", REQUIRED_COLUMNS)
def test_missing_required_values_are_rejected_without_imputation(inventory_panel, column):
    inventory_panel.loc[0, column] = None

    with pytest.raises(ValueError):
        prepare_inventory_inputs(inventory_panel)


@pytest.mark.parametrize(
    "column,value,message",
    [
        ("Date", "not-a-date", "Date contains missing or invalid"),
        ("SKU_ID", " ", "SKU_ID must contain nonblank"),
        ("Warehouse_ID", " W1", "Warehouse_ID must contain nonblank"),
        ("Units_Sold", -1, "Units_Sold contains negative"),
        ("Inventory_Level", 1.5, "Inventory_Level contains fractional"),
        ("Supplier_Lead_Time_Days", np.inf, "Supplier_Lead_Time_Days contains non-finite"),
        ("Order_Quantity", "unknown", "Order_Quantity contains missing or non-numeric"),
        ("Demand_Forecast", np.nan, "Missing values in required fields"),
    ],
)
def test_invalid_values_are_rejected(inventory_panel, column, value, message):
    inventory_panel[column] = inventory_panel[column].astype(object)
    inventory_panel.loc[0, column] = value

    with pytest.raises(ValueError, match=message):
        prepare_inventory_inputs(inventory_panel)


def test_duplicate_native_keys_are_rejected(inventory_panel):
    duplicated = pd.concat([inventory_panel, inventory_panel.iloc[[0]]], ignore_index=True)

    with pytest.raises(ValueError, match=r"Duplicate Date \+ SKU_ID \+ Warehouse_ID"):
        prepare_inventory_inputs(duplicated)


def test_load_function_reuses_inventory_source_loader(tmp_path, inventory_panel):
    source_path = tmp_path / "inventory.csv"
    inventory_panel.drop(columns="Stockout_Flag").to_csv(source_path, index=False)

    prepared = load_inventory_inputs(source_path)

    assert prepared.columns.tolist() == list(REQUIRED_COLUMNS)
    assert prepared["Demand_Forecast"].tolist() == [100.5, 4.25]
