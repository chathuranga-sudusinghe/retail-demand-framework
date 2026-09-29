"""DR-013 declaration checks only: no estimator construction, fitting or scoring."""
from dataclasses import FrozenInstanceError, replace

import pytest

from src.forecasting.configuration import (
    PRIMARY_GRID, PRIMARY_MODELS, SUPPORTIVE_MODELS,
    primary_configuration_grid, primary_model_parameters, supportive_model_parameters,
)

EXPECTED_GRID = (
    (0.03, 100, 4, 0.8), (0.03, 100, 4, 1.0),
    (0.03, 100, 8, 0.8), (0.03, 100, 8, 1.0),
    (0.03, 300, 4, 0.8), (0.03, 300, 4, 1.0),
    (0.03, 300, 8, 0.8), (0.03, 300, 8, 1.0),
    (0.05, 100, 4, 0.8), (0.05, 100, 4, 1.0),
    (0.05, 100, 8, 0.8), (0.05, 100, 8, 1.0),
    (0.05, 300, 4, 0.8), (0.05, 300, 4, 1.0),
    (0.05, 300, 8, 0.8), (0.05, 300, 8, 1.0),
    (0.10, 100, 4, 0.8), (0.10, 100, 4, 1.0),
    (0.10, 100, 8, 0.8), (0.10, 100, 8, 1.0),
    (0.10, 300, 4, 0.8), (0.10, 300, 4, 1.0),
    (0.10, 300, 8, 0.8), (0.10, 300, 8, 1.0),
)
EXPECTED_FIXED = {
    "xgboost": {
        "objective": "reg:squarederror", "booster": "gbtree", "tree_method": "hist",
        "sampling_method": "uniform", "colsample_bytree": 1.0,
        "random_state": 42, "device": "cpu",
    },
    "lightgbm": {
        "objective": "regression", "boosting_type": "gbdt",
        "data_sample_strategy": "bagging", "subsample_freq": 1,
        "deterministic": True, "force_col_wise": True, "force_row_wise": False,
        "feature_fraction": 1.0, "random_state": 42, "device_type": "cpu",
    },
    "catboost": {
        "loss_function": "RMSE", "bootstrap_type": "Bernoulli",
        "sampling_unit": "Object", "sampling_frequency": "PerTree",
        "task_type": "CPU", "grow_policy": "SymmetricTree", "rsm": 1.0,
        "use_best_model": False, "random_seed": 42,
    },
}


def test_primary_grid_has_literal_order_and_stable_shared_identities():
    assert PRIMARY_MODELS == ("xgboost", "lightgbm", "catboost")
    assert SUPPORTIVE_MODELS == ("ridge", "random_forest")
    assert len(PRIMARY_GRID) == 24
    assert tuple(
        (c.learning_rate, c.boosting_iterations, c.max_depth, c.subsample)
        for c in PRIMARY_GRID
    ) == EXPECTED_GRID
    assert tuple(c.canonical_config_id for c in PRIMARY_GRID) == tuple(
        f"GBM{number:03d}" for number in range(1, 25)
    )
    assert len(set(PRIMARY_GRID)) == 24
    assert PRIMARY_GRID[14].canonical_config_id == "GBM015"
    assert PRIMARY_GRID[14].canonical_parameters == {
        "learning_rate": 0.05, "boosting_iterations": 300, "max_depth": 8, "subsample": 0.8,
    }
    for first, second in zip(PRIMARY_GRID[::2], PRIMARY_GRID[1::2], strict=True):
        assert first.subsample == 0.8
        assert second.subsample == 1.0
        assert (first.learning_rate, first.boosting_iterations, first.max_depth) == (
            second.learning_rate, second.boosting_iterations, second.max_depth,
        )


@pytest.mark.parametrize("model", ["xgboost", "lightgbm", "catboost"])
@pytest.mark.parametrize("horizon", [1, 7, 14, 28])
def test_each_primary_model_and_horizon_uses_the_identical_canonical_grid(model, horizon):
    grid = primary_configuration_grid(model, horizon=horizon)
    assert grid is PRIMARY_GRID
    assert tuple(primary_model_parameters(model, c) for c in grid) == tuple(
        primary_model_parameters(model, c)
        for c in primary_configuration_grid(model, horizon=1)
    )


@pytest.mark.parametrize("model", ["xgboost", "lightgbm", "catboost"])
@pytest.mark.parametrize("index", range(24))
def test_all_canonical_values_map_to_only_the_approved_api_dimensions(model, index):
    rate, iterations, depth, subsample = EXPECTED_GRID[index]
    params = primary_model_parameters(model, PRIMARY_GRID[index])
    mapped = {
        "learning_rate": rate, "subsample": subsample,
        "iterations" if model == "catboost" else "n_estimators": iterations,
        "depth" if model == "catboost" else "max_depth": depth,
    }
    assert params == {**EXPECTED_FIXED[model], **mapped}
    if model == "lightgbm":
        assert params["subsample_freq"] == 1
        assert params["force_col_wise"] is True
        assert params["force_row_wise"] is False
    if model == "catboost":
        assert params["use_best_model"] is False
    assert not set(params).intersection({
        "early_stopping_rounds", "early_stopping_round", "callbacks", "od_type",
        "od_wait", "od_pval", "n_jobs", "nthread", "num_threads", "thread_count",
    })


def test_canonical_declarations_and_returned_parameter_dicts_cannot_corrupt_later_calls():
    configuration = PRIMARY_GRID[0]
    with pytest.raises(FrozenInstanceError):
        setattr(configuration, "subsample", 0.1)
    values = configuration.canonical_parameters
    values["subsample"] = 0.1
    assert configuration.subsample == 0.8
    params = primary_model_parameters("lightgbm", configuration)
    params["force_col_wise"] = False
    assert primary_model_parameters("lightgbm", configuration)["force_col_wise"] is True


@pytest.mark.parametrize("model", ["ridge", "random_forest", "naive", "unknown", None])
def test_supportive_and_unknown_models_cannot_enter_primary_search(model):
    with pytest.raises(ValueError, match="Primary model"):
        primary_configuration_grid(model, horizon=1)
    with pytest.raises(ValueError, match="Primary model"):
        primary_model_parameters(model, PRIMARY_GRID[0])


@pytest.mark.parametrize("horizon", [0, 2, 29, True, 1.0, "7", None])
def test_unapproved_horizons_cannot_enter_primary_search(horizon):
    with pytest.raises(ValueError, match="horizon"):
        primary_configuration_grid("xgboost", horizon=horizon)


@pytest.mark.parametrize("change", [
    {"learning_rate": 0.2}, {"boosting_iterations": 200},
    {"max_depth": 6}, {"subsample": 0.5}, {"canonical_config_id": "GBM024"},
])
def test_unapproved_values_and_mislabelled_canonical_identities_are_rejected(change):
    with pytest.raises(ValueError, match="canonical grid identity"):
        primary_model_parameters("xgboost", replace(PRIMARY_GRID[0], **change))


@pytest.mark.parametrize("model, expected", [
    ("ridge", {"alpha": 1.0, "fit_intercept": True, "solver": "auto"}),
    ("random_forest", {
        "n_estimators": 300, "max_depth": None, "min_samples_split": 2,
        "min_samples_leaf": 1, "max_features": 1.0, "bootstrap": True, "random_state": 42,
    }),
])
def test_supportive_models_have_exactly_one_predeclared_configuration(model, expected):
    assert supportive_model_parameters(model) == expected
    modified = supportive_model_parameters(model)
    modified["alpha"] = 99
    assert supportive_model_parameters(model) == expected
    assert "n_jobs" not in expected


@pytest.mark.parametrize("model", ["xgboost", "lightgbm", "catboost", "naive", None])
def test_primary_models_cannot_enter_supportive_configuration_path(model):
    with pytest.raises(ValueError, match="Supportive model"):
        supportive_model_parameters(model)
