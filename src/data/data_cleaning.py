"""Non-destructive shared source validation; no training or import-time I/O.

Callers must isolate an explicitly authorized date scope. No final-period access
or preparation authorization is granted by these reusable functions.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

KEY = ["Date", "SKU_ID", "Warehouse_ID"]
IDS = ["SKU_ID", "Warehouse_ID", "Supplier_ID", "Region"]
COUNTS = ["Units_Sold", "Inventory_Level", "Supplier_Lead_Time_Days", "Reorder_Point", "Order_Quantity"]
FLAGS = ["Promotion_Flag", "Stockout_Flag"]
NUMERIC = COUNTS + ["Unit_Cost", "Unit_Price"] + FLAGS + ["Demand_Forecast"]
COLUMNS = ["Date"] + IDS + NUMERIC


def validate_schema(raw: pd.DataFrame) -> None:
    if not raw.columns.is_unique:
        raise ValueError("Source column names must be unique.")
    if set(raw.columns) != set(COLUMNS):
        raise ValueError("Source schema must contain exactly the fifteen required columns.")
    if raw.empty:
        raise ValueError("Source scope is empty.")


def load_raw_source(path: Path, *, start: str, end: str) -> pd.DataFrame:
    """Load text without ID inference; isolate authorized dates before other checks.

    Boundaries are caller-reviewed, not inferred permission. No whole-file hash
    or quantitative profiling is performed here.
    """
    boundaries = pd.to_datetime([start, end], format="%Y-%m-%d", errors="raise")
    if boundaries.tz is not None or any(boundaries != boundaries.normalize()) or boundaries[0] > boundaries[1]:
        raise ValueError("Scope requires ordered timezone-naive calendar boundaries.")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        header = next(csv.reader(stream), [])
    if len(header) != len(set(header)) or set(header) != set(COLUMNS):
        raise ValueError("Source headers must match the unique full schema.")
    raw = pd.read_csv(path, dtype=str, keep_default_na=False)
    dates = pd.to_datetime(raw.Date, format="%Y-%m-%d", errors="raise")
    if dates.isna().any() or dates.dt.tz is not None or dates.ne(dates.dt.normalize()).any():
        raise ValueError("Invalid dates prevent safe scope isolation.")
    return raw.loc[dates.between(boundaries[0], boundaries[1])].reset_index(drop=True)


def _numeric_date(value: Any) -> bool:
    return isinstance(value, (int, float, np.number))


def parse_datatypes(raw: pd.DataFrame) -> pd.DataFrame:
    """Audit representation only; failed parses stay missing, never valid defaults."""
    validate_schema(raw)
    if pd.api.types.is_numeric_dtype(raw.Date.dtype) or raw.Date.map(_numeric_date).any():
        raise ValueError("Date cannot be a numeric timestamp.")
    parsed = raw.loc[:, COLUMNS].copy(deep=True)
    parsed["Date"] = pd.to_datetime(raw.Date, format="%Y-%m-%d", errors="coerce")
    for column in NUMERIC:
        parsed[column] = pd.to_numeric(raw[column], errors="coerce")
    return parsed


def validate_missing_values(raw: pd.DataFrame) -> dict[str, int]:
    return {"missing_cells": int(raw.isna().sum().sum()),
            "blank_cells": int(sum(raw[c].astype("string").str.strip().eq("").fillna(False).sum() for c in COLUMNS))}


def validate_identifiers(raw: pd.DataFrame) -> dict[str, int]:
    return {f"{c}_invalid_identifier": int((~raw[c].map(
        lambda value: isinstance(value, str) and bool(value.strip()) and value == value.strip()
    )).sum()) for c in IDS}


def validate_numeric_domains(raw: pd.DataFrame, parsed: pd.DataFrame) -> dict[str, int]:
    checks: dict[str, int] = {}
    for c in NUMERIC:
        values = parsed[c].to_numpy(dtype=float, na_value=np.nan)
        checks[f"{c}_invalid_numeric"] = int((parsed[c].isna() & raw[c].notna()).sum())
        checks[f"{c}_infinite"] = int(np.isinf(values).sum())
        if c in COUNTS + ["Unit_Cost", "Unit_Price"]:
            checks[f"{c}_negative"] = int((parsed[c] < 0).sum())
        if c in COUNTS:
            checks[f"{c}_fractional"] = int((values[np.isfinite(values)] % 1 != 0).sum())
        if c in FLAGS:
            checks[f"{c}_not_binary"] = int((parsed[c].notna() & ~parsed[c].isin([0, 1])).sum())
    return checks


def detect_exact_duplicates(raw: pd.DataFrame) -> pd.Series:
    """Mark every member of identical full-source rows, without deletion."""
    return raw.loc[:, COLUMNS].duplicated(keep=False)


def detect_key_duplicates(raw: pd.DataFrame, parsed: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    repeated = parsed.duplicated(KEY, keep=False)
    conflicting = pd.Series(False, index=raw.index)
    for _, indices in parsed.loc[repeated].groupby(KEY, dropna=False).groups.items():
        if len(raw.loc[indices, COLUMNS].drop_duplicates()) > 1:
            conflicting.loc[indices] = True
    return repeated, conflicting


def validate_date_continuity(parsed: pd.DataFrame) -> tuple[int, bool]:
    """Use the observed scoped span and crossed roster, as existing source audits."""
    valid = parsed.dropna(subset=KEY)  # diagnostic subset only, never the handoff
    if valid.empty:
        return 0, False
    expected = len(pd.date_range(valid.Date.min(), valid.Date.max(), freq="D"))
    roster = pd.MultiIndex.from_product([sorted(valid.SKU_ID.unique()), sorted(valid.Warehouse_ID.unique())])
    observed = valid.groupby(KEY[1:]).Date.nunique().reindex(roster, fill_value=0)
    ordered = parsed.sort_values(KEY[1:] + ["Date"], kind="stable").index.equals(parsed.index)
    return int((expected - observed).sum()), ordered


def _finite_range(values: pd.Series) -> dict[str, float | None]:
    finite = values[np.isfinite(values.to_numpy(dtype=float, na_value=np.nan))]
    return {"min": float(finite.min()) if len(finite) else None,
            "max": float(finite.max()) if len(finite) else None}


def build_validation_audit(raw: pd.DataFrame, parsed: pd.DataFrame) -> dict[str, Any]:
    checks = {**validate_missing_values(raw), **validate_identifiers(raw),
              **validate_numeric_domains(raw, parsed)}
    dates = parsed.Date
    checks["invalid_dates"] = int(dates.isna().sum())
    if dates.dt.tz is not None:
        checks["timezone_dates"] = len(dates)
    checks["non_midnight_dates"] = int((dates.notna() & dates.ne(dates.dt.normalize())).sum())
    exact = detect_exact_duplicates(raw)
    repeated, conflicting = detect_key_duplicates(raw, parsed)
    checks.update(exact_duplicate_rows=int(exact.sum()), duplicate_native_key_rows=int(repeated.sum()),
                  conflicting_native_key_rows=int(conflicting.sum()))
    if any(checks[f"{c}_invalid_identifier"] for c in IDS):
        gaps, ordered = 0, False
    else:
        gaps, ordered = validate_date_continuity(parsed)
    checks["missing_series_days_in_observed_span"] = gaps
    return {"status": "failed" if any(checks.values()) else "passed", "checks": checks,
            "input_rows": len(raw), "output_rows": len(parsed),
            "unique_native_keys": len(parsed.loc[:, KEY].drop_duplicates()),
            "source_ordered": ordered,
            "defective_row_positions": {
                "exact_duplicates": np.flatnonzero(exact.to_numpy()).tolist(),
                "duplicate_keys": np.flatnonzero(repeated.to_numpy()).tolist(),
                "conflicting_keys": np.flatnonzero(conflicting.to_numpy()).tolist()},
            "distinct_values": {c: int(parsed[c].nunique(dropna=False)) for c in COLUMNS},
            "numeric_ranges": {c: _finite_range(parsed[c]) for c in NUMERIC}}


def build_validated_dataset(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Block defects, preserve all scoped observations, and sort per series/date."""
    # Row positions are diagnostic; arbitrary caller indexes never define identity.
    source = raw.reset_index(drop=True)
    parsed = parse_datatypes(source)
    audit = build_validation_audit(source, parsed)
    if audit["status"] != "passed":
        error = ValueError("Blocking source defects; no validated dataset accepted.")
        error.add_note(json.dumps(audit["checks"], sort_keys=True))
        raise error
    return parsed.sort_values(KEY[1:] + ["Date"], kind="stable").reset_index(drop=True), audit


def frame_fingerprint(frame: pd.DataFrame) -> str:
    canonical = frame.loc[:, COLUMNS].reset_index(drop=True)
    digest = hashlib.sha256(json.dumps(COLUMNS).encode())
    digest.update(pd.util.hash_pandas_object(canonical, index=False).to_numpy(dtype=np.uint64).tobytes())
    return digest.hexdigest()


def quality_tables(validated: pd.DataFrame, audit: dict[str, Any]) -> dict[str, pd.DataFrame]:
    """Present shared validation evidence for descriptive consumers, without repair."""
    require_valid_audit(audit)
    dates = pd.date_range(validated.Date.min(), validated.Date.max(), freq="D")
    pairs = pd.MultiIndex.from_product([sorted(validated.SKU_ID.unique()), sorted(validated.Warehouse_ID.unique())], names=KEY[1:])
    coverage = validated.groupby(KEY[1:]).Date.nunique().reindex(pairs, fill_value=0).rename("observed_days").reset_index()
    coverage["expected_days_in_observed_span"] = len(dates)
    coverage["missing_days"] = len(dates) - coverage.observed_days
    coverage["completeness"] = coverage.observed_days / len(dates)
    return {"validation": pd.DataFrame({"check": audit["checks"].keys(), "affected": audit["checks"].values()}),
            "missingness": pd.DataFrame({"column": validated.columns, "missing": validated.isna().sum().to_numpy(),
                                          "blank": [0] * len(validated.columns)}),
            "coverage": coverage,
            "numeric_ranges": validated[NUMERIC].agg(["min", "max", "mean", "median"]).T.rename_axis("column").reset_index()}


def require_valid_audit(audit: dict[str, Any]) -> None:
    if audit.get("status") != "passed" or any(audit["checks"].values()):
        raise ValueError("Shared validation failed; analysis cannot consume defective records.")


def scoped_source_receipt(raw: pd.DataFrame, path: Path) -> pd.DataFrame:
    """Fingerprint only the supplied scoped representation, never the whole file."""
    return pd.DataFrame({"item": ["source_file", "scoped_fingerprint", "scoped_rows", "pandas", "numpy"],
                         "value": [path.name, frame_fingerprint(raw), str(len(raw)), pd.__version__, np.__version__]})
