"""Separate observed-outcome labels for DR-004; never forecasting features."""
from __future__ import annotations

from datetime import date

import pandas as pd

from src.forecasting.features import (
    KEY_COLUMNS, SERIES_COLUMNS, TARGET_COLUMN, calendar_date, prepare_demand,
)

FORECAST_HORIZONS = (1, 7, 14)
TARGET_COLUMNS = tuple(f"target_{h}_day" for h in FORECAST_HORIZONS)


def build_horizon_targets(
    data: pd.DataFrame, *, window_start: str | date | pd.Timestamp,
    window_end: str | date | pd.Timestamp,
) -> pd.DataFrame:
    """Return keys and cumulative outcomes starting at each row's Date.

    Date is the FIRST forecast date, not the last known/history date. For an
    origin cutoff o, select the row Date=o+1: target_1_day is Units_Sold(o+1),
    target_7_day sums o+1..o+7, and target_14_day sums o+1..o+14.
    Thus target_1_day at Date=t is the approved daily target Units_Sold(t).

    Both outcome bounds are mandatory and inclusive. Labels require the entire
    horizon inside that interval and nonmissing outcomes on every day. Missing
    or boundary-crossing labels remain NaN, including all rows outside it.
    Row count/grain are preserved. These are actual labels only: generating
    them does not approve direct training, recursive prediction or a scoring
    policy. Never join these future outcomes into the feature set.
    """
    start, end = calendar_date(window_start), calendar_date(window_end)
    if start > end:
        raise ValueError("window_start must not be after window_end.")
    frame = prepare_demand(data)
    outcomes = frame[TARGET_COLUMN].astype(float).where(frame.Date.between(start, end))
    groups = outcomes.groupby([frame[c] for c in SERIES_COLUMNS], observed=True)
    result = frame.loc[:, list(KEY_COLUMNS)].copy()
    for horizon, column in zip(FORECAST_HORIZONS, TARGET_COLUMNS, strict=True):
        result[column] = groups.transform(
            lambda s, h=horizon: s.iloc[::-1].rolling(h, min_periods=h).sum().iloc[::-1]
        )
    return result
