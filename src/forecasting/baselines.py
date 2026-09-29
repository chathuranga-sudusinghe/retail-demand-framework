"""Untuned origin-available formulas from protocol Section 10."""
from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from src.forecasting.features import SERIES_COLUMNS, calendar_date, prepare_demand
from src.forecasting.targets import FORECAST_HORIZONS

BASELINE_MODELS = ("naive", "seasonal_naive")
BASELINE_FORMULAS = {
    "naive": "protocol.md Section 10: h * y_o",
    "seasonal_naive": "protocol.md Section 10: y_(o-6) for h=1; (h/7) * S_o otherwise",
}


def baseline_history(data: pd.DataFrame, *, origin: str | date | pd.Timestamp) -> pd.DataFrame:
    """Latest complete week per historical pair; future demand is never inspected."""
    cutoff = calendar_date(origin)
    # The utility masks quantities before validating them. Remove future keys as well.
    history = prepare_demand(data, require_daily=False, history_end=cutoff)
    history = history.loc[history.Date.le(cutoff)]
    roster = history.loc[:, list(SERIES_COLUMNS)].drop_duplicates()
    rows = []
    for pair in roster.itertuples(index=False, name=None):
        values = history.loc[
            history.SKU_ID.eq(pair[0]) & history.Warehouse_ID.eq(pair[1])
            & history.Date.between(cutoff - pd.Timedelta(days=6), cutoff)
        ].sort_values("Date")
        if len(values) != 7 or values.Units_Sold.isna().any():
            raise ValueError(f"Incomplete baseline history for pair {pair} at {cutoff.date()}.")
        rows.append({"SKU_ID": pair[0], "Warehouse_ID": pair[1],
                     "latest": float(values.Units_Sold.iloc[-1]),
                     "previous_week": float(values.Units_Sold.iloc[0]),
                     "week_sum": float(values.Units_Sold.sum())})
    if not rows:
        raise ValueError("No baseline origin population.")
    return pd.DataFrame(rows)


def baseline_predictions(history: pd.DataFrame, model: str, horizon: int) -> np.ndarray:
    """Return raw predictions in the already checked pair order."""
    if type(horizon) is not int or horizon not in FORECAST_HORIZONS:
        raise ValueError("horizon must be 1, 7, 14 or 28.")
    if model not in BASELINE_MODELS:
        raise ValueError("Unknown baseline model.")
    required = [*SERIES_COLUMNS, "latest", "previous_week", "week_sum"]
    if history.empty or history.duplicated(list(SERIES_COLUMNS)).any():
        raise ValueError("Baseline population must be nonempty and unique.")
    if not np.isfinite(history.loc[:, required[2:]].to_numpy(dtype=float)).all():
        raise ValueError("Incomplete baseline evidence; no imputation.")
    if model == "naive":
        return history.latest.to_numpy(dtype=float) * horizon
    if horizon == 1:
        return history.previous_week.to_numpy(dtype=float)
    return history.week_sum.to_numpy(dtype=float) * (horizon // 7)
