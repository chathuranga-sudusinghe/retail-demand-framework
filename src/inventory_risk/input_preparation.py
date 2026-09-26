"""Prepare source inventory observations for downstream risk analysis.

This module validates and selects the source dataset fields needed by the
inventory-risk component. It does not calculate inventory risk or replenishment
quantities. The source ``Demand_Forecast`` column remains a reference field;
it is not Chathuranga's model-generated forecast output.

Missing or invalid values are rejected rather than imputed, clipped, or
otherwise repaired. Missing calendar dates between observations are not
inserted or inferred because the repository has not approved a gap policy.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.data.profile_inventory_alignment import load_data as load_inventory_source

KEY_COLUMNS = ("Date", "SKU_ID", "Warehouse_ID")
REQUIRED_COLUMNS = (
    *KEY_COLUMNS,
    "Units_Sold",
    "Inventory_Level",
    "Reorder_Point",
    "Supplier_Lead_Time_Days",
    "Order_Quantity",
    "Demand_Forecast",
)
COUNT_COLUMNS = (
    "Units_Sold",
    "Inventory_Level",
    "Reorder_Point",
    "Supplier_Lead_Time_Days",
    "Order_Quantity",
)


def prepare_inventory_inputs(data: pd.DataFrame) -> pd.DataFrame:
    """Validate and return inventory inputs at Date + SKU + warehouse grain.

    The input is not mutated. The output contains only ``REQUIRED_COLUMNS``,
    has a parsed calendar ``Date``, and is sorted by SKU, warehouse, then date.
    Required values must be present; no imputation or data repair is applied.
    Extra columns (including ``Stockout_Flag``) are ignored.
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame.")
    if not data.columns.is_unique:
        raise ValueError("Column names must be unique.")
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(data.columns))
    if missing_columns:
        raise ValueError("Missing required columns: " + ", ".join(missing_columns))
    if data.empty:
        raise ValueError("Inventory input data is empty.")

    frame = data.loc[:, REQUIRED_COLUMNS].copy()

    for column in ("SKU_ID", "Warehouse_ID"):
        valid = frame[column].map(
            lambda value: isinstance(value, str)
            and bool(value.strip())
            and value == value.strip()
        )
        if not valid.all():
            raise ValueError(f"{column} must contain nonblank, unpadded text identifiers.")

    if pd.api.types.is_numeric_dtype(frame["Date"].dtype):
        raise ValueError("Date must contain calendar dates, not numeric timestamps.")
    frame["Date"] = pd.to_datetime(
        frame["Date"], format="%Y-%m-%d", errors="coerce"
    )
    if frame["Date"].isna().any():
        raise ValueError("Date contains missing or invalid calendar dates.")
    has_time = frame["Date"].ne(frame["Date"].dt.normalize()).any()
    if frame["Date"].dt.tz is not None or has_time:
        raise ValueError("Date must be timezone-naive and at midnight.")

    if frame[list(REQUIRED_COLUMNS[3:])].isna().any().any():
        missing_values = frame[list(REQUIRED_COLUMNS[3:])].columns[
            frame[list(REQUIRED_COLUMNS[3:])].isna().any()
        ].tolist()
        raise ValueError("Missing values in required fields: " + ", ".join(missing_values))

    numeric_columns = (*COUNT_COLUMNS, "Demand_Forecast")
    for column in numeric_columns:
        parsed = pd.to_numeric(frame[column], errors="coerce")
        if parsed.isna().any():
            raise ValueError(f"{column} contains missing or non-numeric values.")
        values = parsed.to_numpy(dtype=float)
        if not np.isfinite(values).all():
            raise ValueError(f"{column} contains non-finite values.")
        if column in COUNT_COLUMNS:
            if (parsed < 0).any():
                raise ValueError(f"{column} contains negative values.")
            if parsed.mod(1).ne(0).any():
                raise ValueError(f"{column} contains fractional values.")
        frame[column] = parsed

    if frame.duplicated(list(KEY_COLUMNS), keep=False).any():
        raise ValueError("Duplicate Date + SKU_ID + Warehouse_ID keys.")

    return frame.sort_values(["SKU_ID", "Warehouse_ID", "Date"]).reset_index(drop=True)


def load_inventory_inputs(path: str | Path) -> pd.DataFrame:
    """Load the local inventory source and prepare its required input fields.

    Reuses the existing inventory-alignment CSV loader for source loading and
    then applies this module's complete inventory-risk input contract.
    """
    source = load_inventory_source(Path(path))
    return prepare_inventory_inputs(source)
