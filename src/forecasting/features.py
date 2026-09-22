"""Past-only candidate features for Issue #35 (DR-002 and DR-003).

Date is the date whose Units_Sold is to be predicted. Features for Date=t
use demand strictly before t. For forecasts issued at a fixed earlier cutoff,
pass history_end: per-row shifting alone is not safe for that use case.
No files are read/written and no model or fitted transformation is created.
"""
from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

KEY_COLUMNS = ("SKU_ID", "Warehouse_ID", "Date")
SERIES_COLUMNS = KEY_COLUMNS[:2]
TARGET_COLUMN = "Units_Sold"
CALENDAR_FEATURES = ("day_of_week", "month", "quarter")
CANDIDATE_LAGS = (1, 7, 14, 28)
ROLLING_WINDOWS = (7, 14)
FEATURE_COLUMNS = (
    *CALENDAR_FEATURES,
    *(f"lag_{lag}" for lag in CANDIDATE_LAGS),
    *(f"rolling_{stat}_{window}" for window in ROLLING_WINDOWS
      for stat in ("mean", "median", "std")),
)


def calendar_date(value: str | date | pd.Timestamp) -> pd.Timestamp:
    """Validate a timezone-naive calendar boundary without truncating times."""
    if not isinstance(value, (str, date)):
        raise ValueError("A boundary must be a calendar date, not a numeric timestamp.")
    try:
        result = pd.Timestamp(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid calendar boundary.") from exc
    if pd.isna(result) or result.tzinfo is not None or result != result.normalize():
        raise ValueError("A boundary must be a nonmissing timezone-naive calendar date.")
    return result


def prepare_demand(data: pd.DataFrame) -> pd.DataFrame:
    """Copy, validate and sort the four-column daily demand view.

    Only keys and Units_Sold are selected; all source/existing feature columns
    are excluded. Unknown demand (NaN) is retained, never filled or dropped.
    Reject invalid quantities, duplicate keys and non-daily gaps rather than
    introducing a new cleaning or missing-period policy. Each provided series
    must be daily within its own span; subsets of series/history are permitted.
    Output has a fresh RangeIndex in SKU, warehouse, date order.
    """
    if not data.columns.is_unique:
        raise ValueError("Column names must be unique.")
    required = [*KEY_COLUMNS, TARGET_COLUMN]
    missing = set(required) - set(data.columns)
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))
    frame = data.loc[:, required].copy()
    for column in SERIES_COLUMNS:
        values = frame[column]
        valid = values.map(
            lambda x: isinstance(x, str) and bool(x.strip()) and x == x.strip()
        )
        if not valid.all():
            raise ValueError(f"{column} must contain nonblank, unpadded text identifiers.")
    if pd.api.types.is_numeric_dtype(frame.Date.dtype):
        raise ValueError("Date must contain calendar dates, not numeric timestamps.")
    try:
        frame["Date"] = pd.to_datetime(frame.Date, format="%Y-%m-%d", errors="raise")
    except (TypeError, ValueError) as exc:
        raise ValueError("Date must contain valid YYYY-MM-DD calendar dates.") from exc
    if (frame.Date.isna().any() or frame.Date.dt.tz is not None
            or frame.Date.ne(frame.Date.dt.normalize()).any()):
        raise ValueError("Date must be nonmissing, timezone-naive and at midnight.")
    if frame.duplicated(list(KEY_COLUMNS)).any():
        raise ValueError("Duplicate native keys; no aggregation or deduplication applied.")
    try:
        demand = pd.to_numeric(frame[TARGET_COLUMN], errors="raise")
    except (TypeError, ValueError) as exc:
        raise ValueError("Units_Sold must be numeric or missing.") from exc
    observed = demand.dropna().to_numpy(dtype=float)
    if (not np.isfinite(observed).all() or (observed < 0).any()
            or np.not_equal(observed, np.floor(observed)).any()):
        raise ValueError("Observed Units_Sold must be finite nonnegative whole units.")
    frame[TARGET_COLUMN] = demand
    frame = frame.sort_values(list(KEY_COLUMNS)).reset_index(drop=True)
    gaps = frame.groupby(list(SERIES_COLUMNS), observed=True).Date.diff().dropna()
    if gaps.ne(pd.Timedelta(days=1)).any():
        raise ValueError("Each series must be daily without gaps; no missing dates filled.")
    return frame


def build_features(
    data: pd.DataFrame, *, history_end: str | date | pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Return keys plus the 13 scoped features; no target or source extras.

    day_of_week is Monday=0 ... Sunday=6; month=1..12; quarter=1..4.
    lag_k(t)=Units_Sold(t-k). Rolling statistics use exactly t-w ... t-1,
    require w nonmissing days and use sample standard deviation (ddof=1).
    Early/unknown history stays NaN. No rows are dropped or added.

    With history_end=None, available history advances with each row. Use that
    mode for historical training construction, NOT as a ready-made fixed-origin
    validation/test matrix. For a fixed origin, history_end masks all later
    demand before lag/rolling construction, even if actuals exist in data.
    Unavailable multi-step inputs remain NaN; no recursive/direct strategy or
    within-window update policy is supplied.
    """
    frame = prepare_demand(data)
    history = frame[TARGET_COLUMN].astype(float)
    if history_end is not None:
        cutoff = calendar_date(history_end)
        history = history.where(frame.Date.le(cutoff))
    result = frame.loc[:, list(KEY_COLUMNS)].copy()
    result["day_of_week"] = frame.Date.dt.dayofweek
    result["month"] = frame.Date.dt.month
    result["quarter"] = frame.Date.dt.quarter
    groups = history.groupby([frame[c] for c in SERIES_COLUMNS], observed=True)
    for lag in CANDIDATE_LAGS:
        result[f"lag_{lag}"] = groups.shift(lag)
    for window in ROLLING_WINDOWS:
        for stat in ("mean", "median", "std"):
            # Shift INSIDE each series, then roll within that same series.
            result[f"rolling_{stat}_{window}"] = groups.transform(
                lambda s, w=window, method=stat: getattr(
                    s.shift(1).rolling(w, min_periods=w), method
                )(**({"ddof": 1} if method == "std" else {}))
            )
    return result.loc[:, [*KEY_COLUMNS, *FEATURE_COLUMNS]]
