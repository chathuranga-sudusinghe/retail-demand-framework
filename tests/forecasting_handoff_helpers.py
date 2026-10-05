"""Temporary synthetic shared-data handoffs for forecasting tests only."""
from pathlib import Path

import pandas as pd

from src.data import data_cleaning as cleaning
from src.data.validated_handoff import PROJECT_DATA_VERSION
from test_validated_handoff import publish


def panel():
    """Complete crossed SKU/warehouse roster required by the shared contract."""
    return pd.DataFrame([{"SKU_ID": sku, "Warehouse_ID": warehouse, "Date": day,
                          "Units_Sold": base + offset % 5}
                         for sku, base in (("A", 2), ("B", 8))
                         for warehouse in ("W1", "W2")
                         for offset, day in enumerate(pd.date_range("2024-01-01", "2024-12-30"))])


def publish_forecasting_handoff(repository: Path, demand: pd.DataFrame):
    source = demand.copy()
    defaults = {**dict.fromkeys(cleaning.COLUMNS, 0), "Supplier_ID": "synthetic", "Region": "synthetic",
                "Inventory_Level": 100, "Reorder_Point": 20, "Supplier_Lead_Time_Days": 2,
                "Unit_Cost": 1.5, "Unit_Price": 2.5}
    for column in cleaning.COLUMNS:
        if column not in source:
            source[column] = defaults[column]
    source["Date"] = pd.to_datetime(source.Date).dt.strftime("%Y-%m-%d")
    path = repository / "data/raw/source.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    source.loc[:, cleaning.COLUMNS].to_csv(path, index=False)
    return publish(path, version=PROJECT_DATA_VERSION, start=source.Date.min(), end=source.Date.max())
