"""Training-only representations of the frozen Issue #57 predictor contract.

Issue #62 prepares inputs only: no estimator, training loop, score or experiment.
Call fit_preprocessor on historical feature rows for one training fold/horizon.
The caller must restrict those rows to complete observed horizon labels using
build_horizon_targets. We additionally enforce predictor completeness, the
training cutoff and the horizon's outcome-end boundary, without reading labels.

Vocabularies are lexically sorted from eligible training rows only. One-hot
models retain ALL fitted levels; smaller coverage gives len(SKUs)+len(warehouses)
+12 physical columns rather than forcing 67 with future categories. LightGBM
keeps unordered pandas categorical dtypes with the same frozen vocabularies.
Unknown prediction identities raise: no all-zero identity block, new category,
numeric ID interpretation or silent missing-category conversion is introduced.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

import numpy as np
import pandas as pd

from src.forecasting.features import (
    CATEGORICAL_FEATURE_COLUMNS, CONCEPTUAL_FEATURE_COLUMNS, FEATURE_COLUMNS,
    calendar_date, feature_eligibility,
)
from src.forecasting.targets import FORECAST_HORIZONS

ModelRepresentation = Literal["ridge", "random_forest", "lightgbm"]


def _predictors(features: pd.DataFrame) -> pd.DataFrame:
    """Select only frozen inputs; never pass alignment, labels or source extras."""
    feature_eligibility(features)  # Validate the numerical schema, including duplicates.
    result = features.loc[:, list(CONCEPTUAL_FEATURE_COLUMNS)].copy()
    for column in CATEGORICAL_FEATURE_COLUMNS:
        valid = result[column].map(
            lambda value: isinstance(value, str) and bool(value.strip())
            and value == value.strip()
        )
        if not valid.all():
            raise ValueError(f"{column} must contain nonblank, unpadded text categories.")
    result[list(FEATURE_COLUMNS)] = result.loc[:, list(FEATURE_COLUMNS)].astype(float)
    return result


@dataclass(frozen=True)
class ForecastPreprocessor:
    """Immutable fitted category/scaling state; transform never learns or fills."""

    model: ModelRepresentation
    training_end: pd.Timestamp
    horizon: int
    training_row_count: int
    vocabularies: tuple[tuple[str, ...], ...]
    numerical_means: tuple[float, ...]
    numerical_scales: tuple[float, ...]

    @property
    def conceptual_feature_names(self) -> tuple[str, ...]:
        return CONCEPTUAL_FEATURE_COLUMNS

    @property
    def numerical_feature_names(self) -> tuple[str, ...]:
        return FEATURE_COLUMNS

    @property
    def categorical_feature_names(self) -> tuple[str, ...]:
        return CATEGORICAL_FEATURE_COLUMNS

    @property
    def category_vocabularies(self) -> dict[str, tuple[str, ...]]:
        return dict(zip(CATEGORICAL_FEATURE_COLUMNS, self.vocabularies, strict=True))

    @property
    def category_mappings(self) -> dict[str, dict[str, int]]:
        return {
            column: {category: index for index, category in enumerate(categories)}
            for column, categories in self.category_vocabularies.items()
        }

    @property
    def physical_feature_names(self) -> tuple[str, ...]:
        if self.model == "lightgbm":
            return CONCEPTUAL_FEATURE_COLUMNS
        return (
            *(f"{column}={category}"
              for column, categories in self.category_vocabularies.items()
              for category in categories),
            *FEATURE_COLUMNS,
        )

    @property
    def physical_feature_count(self) -> int:
        return len(self.physical_feature_names)

    def transform(self, features: pd.DataFrame) -> pd.DataFrame:
        """Return a labelled model matrix for complete rows, preserving row index.

        Ridge standardises only numerical inputs: (x-training_mean)/training_std,
        using population std (ddof=0), as for ordinary standard scaling. Constant
        training columns use scale 1. This scaler convention does not change the
        demand-window SAMPLE standard deviations (ddof=1).
        """
        predictors = _predictors(features)
        if not feature_eligibility(predictors).all():
            raise ValueError("Cannot transform feature-ineligible rows; no imputation authorised.")
        for column, categories in self.category_vocabularies.items():
            if not predictors[column].isin(categories).all():
                raise ValueError(f"Unknown {column} category outside eligible training vocabulary.")
        if self.model == "lightgbm":
            for column, categories in self.category_vocabularies.items():
                predictors[column] = pd.Categorical(
                    predictors[column], categories=list(categories), ordered=False,
                )
            return predictors

        indicators = [
            predictors[column].eq(category).to_numpy(dtype=float)
            for column, categories in self.category_vocabularies.items()
            for category in categories
        ]
        numerical = predictors.loc[:, list(FEATURE_COLUMNS)].to_numpy(dtype=float)
        if self.model == "ridge":
            numerical = (numerical - np.asarray(self.numerical_means)) / np.asarray(
                self.numerical_scales
            )
        matrix = np.column_stack([*indicators, numerical])
        return pd.DataFrame(matrix, columns=self.physical_feature_names, index=features.index)


def fit_preprocessor(
    features: pd.DataFrame, model: ModelRepresentation, *,
    training_end: str | date | pd.Timestamp, horizon: int,
) -> ForecastPreprocessor:
    """Learn representation state from eligible, outcome-bounded training rows.

    Date is required for fitting and must be no later than training_end. Rows
    lacking a complete predictor vector or whose horizon ends after that cutoff
    are excluded BEFORE learning categories/scaler statistics. Caller-provided
    training rows must also have complete observed outcomes; this feature-only
    interface does not assess labels. An empty eligible population raises.
    No model is created/fitted; only category vocabularies and numerical scaling
    statistics are calculated. No additional dependency or data access is needed.
    """
    if model not in ("ridge", "random_forest", "lightgbm"):
        raise ValueError("model must be ridge, random_forest or lightgbm.")
    if type(horizon) is not int or horizon not in FORECAST_HORIZONS:
        raise ValueError("horizon must be 1, 7, 14 or 28 days.")
    cutoff = calendar_date(training_end)
    predictors = _predictors(features)
    if "Date" not in features.columns:
        raise ValueError("Date is required to verify the training cutoff.")
    if pd.api.types.is_numeric_dtype(features.Date.dtype):
        raise ValueError("Date must contain calendar dates, not numeric timestamps.")
    try:
        dates = pd.to_datetime(features.Date, format="%Y-%m-%d", errors="raise")
    except (TypeError, ValueError) as exc:
        raise ValueError("Date must contain valid calendar dates.") from exc
    if (dates.isna().any() or dates.dt.tz is not None
            or dates.ne(dates.dt.normalize()).any()):
        raise ValueError("Date must be nonmissing, timezone-naive and at midnight.")
    if dates.gt(cutoff).any():
        raise ValueError("Preprocessing fitting rows must not be after training_end.")
    if features.duplicated([*CATEGORICAL_FEATURE_COLUMNS, "Date"]).any():
        raise ValueError("Duplicate native training keys.")
    eligible = feature_eligibility(predictors) & (
        dates + pd.Timedelta(days=horizon - 1)
    ).le(cutoff)
    training = predictors.loc[eligible]
    if training.empty:
        raise ValueError("No eligible training rows for preprocessing.")
    vocabularies = tuple(
        tuple(sorted(training[column].unique())) for column in CATEGORICAL_FEATURE_COLUMNS
    )
    means: tuple[float, ...] = ()
    scales: tuple[float, ...] = ()
    if model == "ridge":
        numerical = training.loc[:, list(FEATURE_COLUMNS)].to_numpy(dtype=float)
        means = tuple(numerical.mean(axis=0))
        std = numerical.std(axis=0, ddof=0)
        scales = tuple(np.where(std == 0, 1.0, std))
    return ForecastPreprocessor(
        model=model, training_end=cutoff, horizon=horizon, training_row_count=len(training),
        vocabularies=vocabularies, numerical_means=means, numerical_scales=scales,
    )
