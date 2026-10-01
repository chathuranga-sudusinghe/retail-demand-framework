"""Shared typed, validated synthetic panel for descriptive analysis tests."""
import pandas as pd
import pytest

from src.data.data_cleaning import build_validated_dataset


@pytest.fixture
def panel():
    rows = []
    for day, date in enumerate(pd.date_range("2024-01-01", periods=60)):
        for sku in ["A", "B"]:
            for wh in ["W1", "W2"]:
                rows.append({"Date": date.strftime("%Y-%m-%d"), "SKU_ID": sku, "Warehouse_ID": wh,
                             "Supplier_ID": "S1", "Region": "R1", "Units_Sold": day,
                             "Inventory_Level": 100, "Supplier_Lead_Time_Days": 2,
                             "Reorder_Point": 20, "Order_Quantity": 0, "Unit_Cost": 1.5,
                             "Unit_Price": 2.5, "Promotion_Flag": day % 2,
                             "Stockout_Flag": 0, "Demand_Forecast": 9.2})
    return build_validated_dataset(pd.DataFrame(rows))[0]
