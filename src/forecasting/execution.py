"""Current four-column CSV loader and explicit legacy authorization exports."""
from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

# Preserve previous public imports; authorization.py is the sole implementation.
from src.forecasting.authorization import (
    ExecutionBlocked as ExecutionBlocked,
    ExecutionContext as ExecutionContext,
    RunScope as RunScope,
    ValidationAuthorization as ValidationAuthorization,
    resolve_execution as resolve_execution,
)

def load_dataset(path: Path) -> pd.DataFrame:
    columns = ["Date", "SKU_ID", "Warehouse_ID", "Units_Sold"]
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            header = next(csv.reader(stream), [])
        if any(header.count(column) != 1 for column in columns):
            raise ExecutionBlocked("Required CSV columns must each occur exactly once.")
        return pd.read_csv(path, usecols=columns,
                           dtype={"SKU_ID": str, "Warehouse_ID": str, "Units_Sold": object})
    except ExecutionBlocked:
        raise
    except (OSError, ValueError, pd.errors.ParserError, csv.Error) as exc:
        raise ExecutionBlocked("Approved forecasting CSV could not be loaded.") from exc
