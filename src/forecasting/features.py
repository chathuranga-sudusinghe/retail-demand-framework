"""Frozen Issue #57 predictors, implemented under Issue #62.

Date is the FIRST target day t=o+1. Demand inputs end at origin o, within
SKU_ID + Warehouse_ID. No data is filled, no files are read/written and no
model is fitted. Use build_origin_features for one reusable fixed-origin row.
"""
from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

KEY_COLUMNS = ("SKU_ID", "Warehouse_ID", "Date")
SERIES_COLUMNS = KEY_COLUMNS[:2]
TARGET_COLUMN = "Units_Sold"
CATEGORICAL_FEATURE_COLUMNS = SERIES_COLUMNS
CALENDAR_FEATURES = ("dow_sin", "dow_cos")
LAGS = (1, 7, 14)
ROLLING_WINDOWS = (7, 14, 28)
MINIMUM_HISTORY_DAYS = 28
FEATURE_COLUMNS = (
    *CALENDAR_FEATURES,
    *(f"lag_{lag}" for lag in LAGS),
    *(f"rolling_{stat}_{window}" for window in ROLLING_WINDOWS
      for stat in ("mean", "std")),
    "rolling_slope_14",
)
CONCEPTUAL_FEATURE_COLUMNS = (*CATEGORICAL_FEATURE_COLUMNS, *FEATURE_COLUMNS)


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


def prepare_demand(
    data: pd.DataFrame, *, require_daily: bool = True,
    history_end: str | date | pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Copy, validate and sort the four-column daily demand view.

    Only keys and Units_Sold are selected; all source/existing feature columns
    are excluded. Unknown demand (NaN) is retained, never filled or dropped.
    Reject invalid quantities, duplicate keys and non-daily gaps rather than
    introducing a new cleaning or missing-period policy. Each provided series
    must be daily within its own span; subsets of series/history are permitted.
    Output has a fresh RangeIndex in SKU, warehouse, date order.
    Feature construction can set require_daily=False to retain gaps as
    unavailable history, without filling dates. Default target/fold validation
    remains strict. An explicit history_end masks later demand BEFORE quantity
    validation; those outcomes are unavailable, even if supplied by the caller.
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
    if history_end is not None:
        cutoff = calendar_date(history_end)
        frame[TARGET_COLUMN] = frame[TARGET_COLUMN].where(frame.Date.le(cutoff))
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
    if require_daily and gaps.ne(pd.Timedelta(days=1)).any():
        raise ValueError("Each series must be daily without gaps; no missing dates filled.")
    return frame


def build_features(
    data: pd.DataFrame, *, history_end: str | date | pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Return keys plus exactly twelve ordered numerical engineered features.

    Date=t is the first target day; weekday phase is Monday=0 ... Sunday=6.
    lag_k(t)=y_(t-k), using exact calendar dates rather than arbitrary row offsets.
    Rolling mean/sample std (ddof=1) and the 14-day slope use complete consecutive
    histories ending at t-1. Missing dates/values leave affected inputs NaN.
    Rows are retained; feature_eligibility enforces the full 28-day vector.

    With history_end=None, each historical training row uses its own origin.
    For fixed-origin inputs, mask all later demand and select ONLY Date=o+1,
    or use build_origin_features. Later target dates do not become new origins.
    """
    frame = prepare_demand(data, require_daily=False, history_end=history_end)
    history = frame[TARGET_COLUMN].astype(float)
    result = frame.loc[:, list(KEY_COLUMNS)].copy()
    phase = 2 * np.pi * frame.Date.dt.dayofweek / 7
    result["dow_sin"] = np.sin(phase)
    result["dow_cos"] = np.cos(phase)

    lookup = pd.Series(
        history.to_numpy(), index=pd.MultiIndex.from_frame(frame.loc[:, list(KEY_COLUMNS)])
    )
    for lag in LAGS:
        lag_keys = result.loc[:, list(KEY_COLUMNS)].copy()
        lag_keys["Date"] = frame.Date - pd.Timedelta(days=lag)
        result[f"lag_{lag}"] = lookup.reindex(
            pd.MultiIndex.from_frame(lag_keys)
        ).to_numpy()

    groups = history.groupby([frame[c] for c in SERIES_COLUMNS], observed=True)
    date_groups = frame.groupby(list(SERIES_COLUMNS), observed=True).Date
    consecutive = {}
    for window in ROLLING_WINDOWS:
        # w preceding unique dates span exactly w days up to t: no internal gap
        # or gap between the latest observation and origin t-1 can be hidden.
        consecutive[window] = date_groups.shift(window).eq(
            frame.Date - pd.Timedelta(days=window)
        )
        for stat in ("mean", "std"):
            values = groups.transform(
                lambda s, w=window, method=stat: getattr(
                    s.shift(1).rolling(w, min_periods=w), method
                )(**({"ddof": 1} if method == "std" else {}))
            )
            result[f"rolling_{stat}_{window}"] = values.where(consecutive[window])

    day_indices = np.arange(14, dtype=float) - 6.5
    denominator = np.dot(day_indices, day_indices)
    result["rolling_slope_14"] = groups.transform(
        lambda s: s.shift(1).rolling(14, min_periods=14).apply(
            lambda values: np.dot(day_indices, values - values.mean()) / denominator,
            raw=True,
        )
    ).where(consecutive[14])
    return result.loc[:, [*KEY_COLUMNS, *FEATURE_COLUMNS]]


def feature_eligibility(features: pd.DataFrame) -> pd.Series:
    """Flag complete frozen vectors produced by build_features.

    The 28-day mean/std enforce consecutive daily history, including all values.
    Finite values are required for every numerical input; never impute a vector.
    This checks predictor availability only. Complete horizon outcomes ending
    by the fitting cutoff must be checked separately by the target pipeline.
    """
    if not features.columns.is_unique:
        raise ValueError("Column names must be unique.")
    missing = set(CONCEPTUAL_FEATURE_COLUMNS) - set(features.columns)
    if missing:
        raise ValueError("Missing predictor columns: " + ", ".join(sorted(missing)))
    try:
        numerical = features.loc[:, list(FEATURE_COLUMNS)].to_numpy(dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("Engineered predictors must be numerical or missing.") from exc
    return pd.Series(
        np.isfinite(numerical).all(axis=1), index=features.index, name="feature_eligible",
    )


def build_origin_features(
    data: pd.DataFrame, *, origin: str | date | pd.Timestamp,
) -> pd.DataFrame:
    """Return one row at Date=origin+1 per pair present at/before origin.

    Only historical identity/demand evidence is retained. Add a calendar-only
    target-start row with unknown demand; this requires no future actuals.
    Missing/incomplete pairs remain present but feature-ineligible. Reuse these
    SAME conceptual rows for all 1/7/14/28-day direct horizon models.
    """
    cutoff = calendar_date(origin)
    frame = prepare_demand(data, require_daily=False, history_end=cutoff)
    history = frame.loc[frame.Date.le(cutoff)].copy()
    target_rows = history.loc[:, list(SERIES_COLUMNS)].drop_duplicates().copy()
    target_rows["Date"] = cutoff + pd.Timedelta(days=1)
    target_rows[TARGET_COLUMN] = np.nan
    features = build_features(
        pd.concat([history, target_rows], ignore_index=True), history_end=cutoff,
    )
    return features.loc[features.Date.eq(cutoff + pd.Timedelta(days=1))].reset_index(drop=True)
