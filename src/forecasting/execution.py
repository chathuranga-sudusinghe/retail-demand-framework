"""Approved scoped validated forecasting input; direct legacy authorization exports."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data.validated_handoff import PROJECT_DATA_VERSION, ValidatedProjection, read_validated_projection
# Preserve previous public imports; authorization.py is the sole implementation.
from src.forecasting.authorization import (
    ExecutionBlocked as ExecutionBlocked,
    ExecutionContext as ExecutionContext,
    RunScope as RunScope,
    ValidationAuthorization as ValidationAuthorization,
    resolve_execution as resolve_execution,
)
from src.forecasting.features import KEY_COLUMNS, TARGET_COLUMN, prepare_demand
from src.forecasting.paths import VALIDATED_DATASET_RELATIVE_PATH, RepositoryLayout
from src.forecasting.validation import FINAL_HOLDOUT, VALIDATION_FOLDS

FORECAST_INPUT_COLUMNS = (*KEY_COLUMNS, TARGET_COLUMN)


def forecasting_projection(data: pd.DataFrame) -> pd.DataFrame:
    """Select the approved fields and reject defects/disorder without repairing data."""
    if not data.columns.is_unique or set(FORECAST_INPUT_COLUMNS) - set(data.columns):
        raise ValueError("Unique required forecasting projection columns are required.")
    frame = data.loc[:, list(FORECAST_INPUT_COLUMNS)].copy()
    # The input is a declared typed handoff; no string parsing/coercion is inferred.
    if not pd.api.types.is_datetime64_any_dtype(frame.Date.dtype):
        raise ValueError("Validated Date must retain its declared datetime dtype.")
    if frame.Date.ge(pd.Timestamp(FINAL_HOLDOUT.start)).any():
        raise ExecutionBlocked("Reserved final-evaluation rows cannot enter forecasting preparation.")
    checked = prepare_demand(frame, require_daily=False)
    pd.testing.assert_frame_equal(frame, checked, check_exact=True)
    if frame.isna().any().any():
        raise ValueError("Validated forecasting input cannot contain missing values.")
    return frame


def load_projection(layout: RepositoryLayout, *, fold_number: int | None = None,
                    expected_provenance_sha256: str | None = None) -> ValidatedProjection:
    """Verify whole-file bytes, then scope decoding before quantity checks or feature preparation."""
    if fold_number is not None and (type(fold_number) is not int or fold_number not in (1, 2, 3, 4)):
        raise ExecutionBlocked("Only the four validation folds may be loaded; final evaluation is blocked.")
    fold = VALIDATION_FOLDS[(fold_number or 4) - 1]
    try:
        loaded = read_validated_projection(
            repository=layout.root, data_version=PROJECT_DATA_VERSION, columns=FORECAST_INPUT_COLUMNS,
            start=fold.training.start.isoformat(), end=fold.validation.end.isoformat(),
            expected_provenance_sha256=expected_provenance_sha256,
        )
        return ValidatedProjection(forecasting_projection(loaded.frame), loaded.provenance,
                                   loaded.provenance_sha256, loaded.scope)
    except ExecutionBlocked:
        raise
    except (OSError, ValueError, TypeError, AssertionError) as exc:
        raise ExecutionBlocked("Approved validated forecasting Parquet could not be loaded.") from exc


def load_dataset(path: Path) -> pd.DataFrame:
    """Runtime compatibility signature; only the fixed validated handoff is authoritative."""
    path = path.absolute()
    root = path
    for component in reversed(VALIDATED_DATASET_RELATIVE_PATH.parts):
        if root.name != component:
            raise ExecutionBlocked("Forecasting requires the approved validated Parquet handoff.")
        root = root.parent
    layout = RepositoryLayout(root)
    if path != layout.dataset:
        raise ExecutionBlocked("Forecasting requires the approved validated Parquet handoff.")
    return load_projection(layout).frame
