"""DR-005 calendar boundaries and explicit raw-demand fold slicing.

No features, horizon labels, fitting or scoring are generated here.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from src.forecasting.features import SERIES_COLUMNS, prepare_demand


@dataclass(frozen=True)
class DateWindow:
    start: date
    end: date


@dataclass(frozen=True)
class ValidationFold:
    number: int
    training: DateWindow
    validation: DateWindow


VALIDATION_FOLDS = (
    ValidationFold(1, DateWindow(date(2024, 1, 1), date(2024, 3, 31)),
                   DateWindow(date(2024, 4, 1), date(2024, 4, 14))),
    ValidationFold(2, DateWindow(date(2024, 1, 1), date(2024, 6, 30)),
                   DateWindow(date(2024, 7, 1), date(2024, 7, 14))),
    ValidationFold(3, DateWindow(date(2024, 1, 1), date(2024, 9, 30)),
                   DateWindow(date(2024, 10, 1), date(2024, 10, 14))),
    ValidationFold(4, DateWindow(date(2024, 1, 1), date(2024, 12, 2)),
                   DateWindow(date(2024, 12, 3), date(2024, 12, 16))),
)
FINAL_HOLDOUT = DateWindow(date(2024, 12, 17), date(2024, 12, 30))


def split_fold(data: pd.DataFrame, fold_number: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return copied training/validation demand rows at exact inclusive bounds.

    Intentionally selects only the named fold's periods and returns only keys
    and Units_Sold. The final holdout is never returned. Supplied series must
    cover every scheduled day of both windows; incomplete slices raise rather
    than silently shortening training or validation. Missing Units_Sold remains
    missing; coverage validation is not imputation or a model-eligibility rule.
    Use the returned training end as build_features(history_end=...) when
    preparing fixed-origin validation inputs. Do not build unbounded features
    on the full source and then slice them as fixed-origin validation inputs.
    """
    if type(fold_number) is not int or fold_number not in (1, 2, 3, 4):
        raise ValueError("fold_number must be an integer from 1 to 4.")
    frame = prepare_demand(data)
    if frame.empty:
        raise ValueError("Cannot construct a fold from empty data.")
    fold = VALIDATION_FOLDS[fold_number - 1]
    pairs = frame.groupby(list(SERIES_COLUMNS), observed=True).size().index
    parts = []
    for name, window in (("training", fold.training), ("validation", fold.validation)):
        part = frame.loc[frame.Date.between(pd.Timestamp(window.start), pd.Timestamp(window.end))].copy()
        expected = (window.end - window.start).days + 1
        counts = part.groupby(list(SERIES_COLUMNS), observed=True).Date.nunique().reindex(pairs, fill_value=0)
        if not counts.eq(expected).all():
            raise ValueError(f"Incomplete {name} date coverage for DR-005 fold {fold_number}.")
        parts.append(part.reset_index(drop=True))
    return parts[0], parts[1]
