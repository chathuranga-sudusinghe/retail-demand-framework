"""DR-013 parameter declarations only; no estimators, data, fitting or scoring.

The primary grid is shared across models/horizons. Fixed supportive benchmarks
have no search space. Returned dictionaries contain requested explicit settings,
not every effective pinned-library default. A later authorised runner must record
those defaults, fix thread counts and reject early-stopping callbacks. This module
neither chooses thread counts nor grants experiment-execution approval.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Literal

from src.forecasting.targets import FORECAST_HORIZONS

PrimaryModel = Literal["xgboost", "lightgbm", "catboost"]
SupportiveModel = Literal["ridge", "random_forest"]
ModelName = PrimaryModel | SupportiveModel
ParameterValue = str | int | float | bool | None
ModelParameters = dict[str, ParameterValue]

PRIMARY_MODELS: tuple[PrimaryModel, ...] = ("xgboost", "lightgbm", "catboost")
SUPPORTIVE_MODELS: tuple[SupportiveModel, ...] = ("ridge", "random_forest")


@dataclass(frozen=True)
class CanonicalConfiguration:
    """Immutable external settings with the same identity for every primary model."""

    canonical_config_id: str
    learning_rate: float
    boosting_iterations: int
    max_depth: int
    subsample: float

    @property
    def canonical_parameters(self) -> dict[str, float | int]:
        """Fresh canonical values, separate from library-specific API parameters."""
        return {
            "learning_rate": self.learning_rate,
            "boosting_iterations": self.boosting_iterations,
            "max_depth": self.max_depth,
            "subsample": self.subsample,
        }


PRIMARY_GRID = tuple(
    CanonicalConfiguration(f"GBM{index:03d}", rate, iterations, depth, subsample)
    for index, (rate, iterations, depth, subsample) in enumerate(
        product((0.03, 0.05, 0.10), (100, 300), (4, 8), (0.8, 1.0)), start=1,
    )
)


def primary_configuration_grid(
    model: PrimaryModel, *, horizon: int,
) -> tuple[CanonicalConfiguration, ...]:
    """Return the same ordered 24 declarations, without evaluating candidates."""
    if model not in PRIMARY_MODELS:
        raise ValueError("Primary model must be xgboost, lightgbm or catboost.")
    if type(horizon) is not int or horizon not in FORECAST_HORIZONS:
        raise ValueError("horizon must be 1, 7, 14 or 28 days.")
    return PRIMARY_GRID


def primary_model_parameters(
    model: PrimaryModel, configuration: CanonicalConfiguration,
) -> ModelParameters:
    """Map an approved canonical identity to fresh CPU estimator parameters.

    No early-stopping parameter or callback is supplied. CatBoost explicitly
    disables use_best_model. Unlisted growth/regularisation settings inherit
    pinned-library defaults; these must later be captured in run metadata.
    Numeric thread counts remain a separate implementation/protocol decision.
    """
    if model not in PRIMARY_MODELS:
        raise ValueError("Primary model must be xgboost, lightgbm or catboost.")
    if configuration not in PRIMARY_GRID:
        raise ValueError("Configuration must match an approved canonical grid identity.")
    common: ModelParameters = {
        "learning_rate": configuration.learning_rate,
        "subsample": configuration.subsample,
    }
    if model == "xgboost":
        return {
            **common,
            "n_estimators": configuration.boosting_iterations,
            "max_depth": configuration.max_depth,
            "objective": "reg:squarederror",
            "booster": "gbtree",
            "tree_method": "hist",
            "sampling_method": "uniform",
            "colsample_bytree": 1.0,
            "random_state": 42,
            "device": "cpu",
        }
    if model == "lightgbm":
        return {
            **common,
            "n_estimators": configuration.boosting_iterations,
            "max_depth": configuration.max_depth,
            "objective": "regression",
            "boosting_type": "gbdt",
            "data_sample_strategy": "bagging",
            "subsample_freq": 1,
            "deterministic": True,
            "force_col_wise": True,
            "force_row_wise": False,
            "feature_fraction": 1.0,
            "random_state": 42,
            "device_type": "cpu",
        }
    return {
        **common,
        "iterations": configuration.boosting_iterations,
        "depth": configuration.max_depth,
        "loss_function": "RMSE",
        "bootstrap_type": "Bernoulli",
        "sampling_unit": "Object",
        "sampling_frequency": "PerTree",
        "task_type": "CPU",
        "grow_policy": "SymmetricTree",
        "rsm": 1.0,
        "use_best_model": False,
        "random_seed": 42,
    }


def supportive_model_parameters(model: SupportiveModel) -> ModelParameters:
    """Return one predeclared contextual benchmark; no optimisation is implied."""
    if model == "ridge":
        return {"alpha": 1.0, "fit_intercept": True, "solver": "auto"}
    if model == "random_forest":
        return {
            "n_estimators": 300,
            "max_depth": None,
            "min_samples_split": 2,
            "min_samples_leaf": 1,
            "max_features": 1.0,
            "bootstrap": True,
            "random_state": 42,
        }
    raise ValueError("Supportive model must be ridge or random_forest.")
