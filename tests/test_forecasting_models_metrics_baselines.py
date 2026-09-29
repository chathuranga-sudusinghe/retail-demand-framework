"""Controlled synthetic diagnostics only; no project data or research experiment."""
from dataclasses import replace
from math import sqrt
from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest

from src.forecasting.artifacts import json_text
from src.forecasting.baselines import baseline_history, baseline_predictions
from src.forecasting.configuration import PRIMARY_GRID, primary_model_parameters, supportive_model_parameters
from src.forecasting.metrics import forecasting_metrics, four_fold_means
from src.forecasting.models import (
    construct_estimator, effective_iterations, estimator_parameters, fit_estimator,
)


@pytest.mark.parametrize("model", ["xgboost", "lightgbm", "catboost"])
@pytest.mark.parametrize("configuration", PRIMARY_GRID)
def test_estimator_construction_keeps_all_24_mappings_and_exact_requested_iterations(model, configuration):
    estimator = construct_estimator(model, configuration)
    declared = primary_model_parameters(model, configuration)
    requested = estimator.get_params()
    assert all(requested[k] == v for k, v in declared.items())
    key = "iterations" if model == "catboost" else "n_estimators"
    assert requested[key] == configuration.boosting_iterations
    assert requested["thread_count" if model == "catboost" else "n_jobs"] == 1
    assert requested["random_seed" if model == "catboost" else "random_state"] == 42
    assert requested["task_type" if model == "catboost" else "device_type" if model == "lightgbm" else "device"].lower() == "cpu"
    assert requested.get("early_stopping_rounds") is None
    assert requested.get("callbacks") is None
    if model == "catboost":
        assert requested["use_best_model"] is False
        assert requested["allow_writing_files"] is False


@pytest.mark.parametrize("model", ["ridge", "random_forest"])
def test_supportive_construction_reuses_only_fixed_configuration(model):
    params = construct_estimator(model).get_params()
    assert all(params[k] == v for k, v in supportive_model_parameters(model).items())
    if model == "random_forest":
        assert params["n_jobs"] == 1
        assert params["random_state"] == 42
    else:
        assert params["solver"] == "auto"


@pytest.mark.parametrize("model,configuration", [
    ("xgboost", None), ("ridge", PRIMARY_GRID[0]), ("random_forest", PRIMARY_GRID[0]),
    ("unknown", None), ("naive", None), ("catboost", replace(PRIMARY_GRID[0], boosting_iterations=5)),
])
def test_construction_rejects_unknown_models_or_unapproved_recipes(model, configuration):
    with pytest.raises(ValueError):
        construct_estimator(model, configuration)


@pytest.mark.parametrize("model", ["xgboost", "lightgbm", "catboost", "ridge", "random_forest"])
def test_fit_rejects_tampered_runtime_before_fit(model):
    configuration = PRIMARY_GRID[0] if model in ("xgboost", "lightgbm", "catboost") else None
    estimator = Mock()
    params = estimator_parameters(model, configuration)
    params[next(iter(params))] = "tampered"
    estimator.get_params.return_value = params
    with pytest.raises(ValueError, match="frozen runtime"):
        fit_estimator(estimator, model, configuration, np.ones((4, 2)), np.ones(4))
    estimator.fit.assert_not_called()


@pytest.mark.parametrize("model", ["xgboost", "lightgbm", "catboost"])
def test_early_stopping_cannot_be_added_and_fit_has_no_eval_kwargs(model):
    configuration = PRIMARY_GRID[0]
    estimator = Mock()
    params = estimator_parameters(model, configuration)
    estimator.get_params.return_value = {**params, "callbacks": [object()]}
    with pytest.raises(ValueError, match="early stopping"):
        fit_estimator(estimator, model, configuration, np.ones((4, 2)), np.ones(4))
    estimator.fit.assert_not_called()
    estimator.get_params.return_value = params
    estimator.get_booster.return_value.num_boosted_rounds.return_value = 99
    estimator.booster_.num_trees.return_value = 99
    estimator.tree_count_ = 99
    with pytest.raises(ValueError, match="requested 100, effective 99"):
        fit_estimator(estimator, model, configuration, np.ones((4, 2)), np.ones(4))
    assert estimator.fit.call_args.kwargs == {}
    assert effective_iterations(estimator, model) == 99


@pytest.mark.parametrize("model,configuration", [
    ("xgboost", PRIMARY_GRID[0]), ("lightgbm", PRIMARY_GRID[0]), ("catboost", PRIMARY_GRID[0]),
    ("ridge", None), ("random_forest", None),
    ("xgboost", PRIMARY_GRID[4]), ("lightgbm", PRIMARY_GRID[4]), ("catboost", PRIMARY_GRID[4]),
])
def test_small_controlled_library_fits_verify_effective_iterations_and_defaults(model, configuration, tmp_path, monkeypatch):
    # Independent random arrays (not project demand or fold scores), enough varied
    # targets for LightGBM to retain its budget under the frozen default leaf size.
    monkeypatch.chdir(tmp_path)
    rng = np.random.default_rng(42)
    matrix = rng.normal(size=(200, 6))
    labels = matrix[:, 0] * 20 + matrix[:, 1] ** 2 + rng.normal(size=200)
    estimator = construct_estimator(model, configuration)
    record = fit_estimator(estimator, model, configuration, matrix, labels)
    assert record["effective_iterations"] == (configuration.boosting_iterations if configuration else
                                              300 if model == "random_forest" else None)
    assert np.isfinite(estimator.predict(matrix[:2])).all()
    assert record["requested_api_parameters"] == estimator_parameters(model, configuration)
    assert record["effective_api_parameters"]
    json_text(record)  # No NaN/Infinity in inherited-default metadata.
    if model == "lightgbm":
        assert record["effective_api_parameters"]["num_leaves"] == 31
        native = record["effective_api_parameters"]["native_parameters"]
        assert native["num_threads"] == "1"
        assert native["device_type"] == "cpu"
    assert list(tmp_path.iterdir()) == []  # CatBoost log/snapshot files suppressed.


def test_real_lightgbm_shortened_budget_is_a_failure_even_without_early_stopping():
    estimator = construct_estimator("lightgbm", PRIMARY_GRID[0])
    with pytest.raises(ValueError, match="Iteration mismatch: requested 100"):
        fit_estimator(estimator, "lightgbm", PRIMARY_GRID[0], np.ones((32, 4)), np.ones(32))
    assert effective_iterations(estimator, "lightgbm") < 100
    assert estimator.get_params().get("early_stopping_rounds") is None


def test_metrics_exact_formulas_bias_sign_and_no_prediction_clipping():
    record = forecasting_metrics([2, 4, 6], [1, 7, 4])
    assert record == {"n_predictions": 3, "wape": 0.5, "mae": 2.0,
                      "rmse": sqrt(14 / 3), "bias": 0.0, "wape_denominator": 12.0,
                      "metric_status": "valid", "failure_reason": None}
    assert forecasting_metrics([2, 4], [3, 5])["bias"] == 1
    assert forecasting_metrics([2, 4], [1, 3])["bias"] == -1
    assert forecasting_metrics([0, 2], [-2, -1])["bias"] == -2.5
    assert forecasting_metrics([0, 2], [-2, -1])["mae"] == 2.5


def test_zero_wape_denominator_keeps_supporting_metrics_and_json_null():
    record = forecasting_metrics([0, 0], [1, -1])
    assert record["wape"] is None
    assert record["metric_status"] == "undefined_zero_actual_total"
    assert record["mae"] == record["rmse"] == 1
    assert record["bias"] == 0
    assert '"wape": null' in json_text(record)
    with pytest.raises(ValueError, match="Nonfinite"):
        json_text({"score": np.inf})


@pytest.mark.parametrize("actual,prediction,reason", [
    ([], [], "empty_population"), ([1], [np.nan], "nonfinite_prediction"),
    ([np.inf], [1], "nonfinite_actual"), ([1e308], [-1e308], "numeric_overflow"),
])
def test_failed_metric_populations_are_not_scores(actual, prediction, reason):
    record = forecasting_metrics(actual, prediction)
    assert record["metric_status"] == "failed"
    assert record["failure_reason"] == reason
    assert all(record[m] is None for m in ("wape", "mae", "rmse", "bias"))
    json_text(record)


def test_metrics_require_aligned_vector_shapes():
    with pytest.raises(ValueError, match="aligned vectors"):
        forecasting_metrics([1, 2], [1])
    with pytest.raises(ValueError, match="aligned vectors"):
        forecasting_metrics([[1]], [[1]])


def test_four_fold_means_are_arithmetic_unweighted_and_require_every_metric():
    records = [{"fold_id": i, **forecasting_metrics([1] * i, [i + 1] * i)} for i in range(1, 5)]
    summary = four_fold_means(records[::-1])
    assert summary["mean_wape"] == summary["mean_mae"] == summary["mean_rmse"] == summary["mean_bias"] == 2.5
    assert summary["n_predictions"] == 10
    assert four_fold_means(records[:-1])["mean_wape"] is None
    records[-1]["wape"] = None
    assert four_fold_means(records)["valid_fold_count"] == 3
    assert four_fold_means(records)["mean_mae"] is None
    with pytest.raises(ValueError, match="Duplicate"):
        four_fold_means(records + records[:1])
    with pytest.raises(ValueError, match="Final evidence"):
        four_fold_means([{**records[0], "evaluation_stage": "final_evaluation"}])


def week_panel():
    return pd.DataFrame([{"SKU_ID": sku, "Warehouse_ID": warehouse, "Date": day,
                          "Units_Sold": offset + base}
                         for sku, warehouse, base in (("A", "W1", 1), ("A", "W2", 10), ("B", "W1", 100))
                         for offset, day in enumerate(pd.date_range("2024-03-25", periods=10))])


@pytest.mark.parametrize("horizon", [1, 7, 14, 28])
def test_baseline_exact_formulas_latest_complete_week_and_series_boundaries(horizon):
    panel = week_panel()
    history = baseline_history(panel.sample(frac=1, random_state=2), origin="2024-03-31")
    np.testing.assert_array_equal(baseline_predictions(history, "naive", horizon), np.array([7, 16, 106]) * horizon)
    expected = np.array([1, 10, 100]) if horizon == 1 else np.array([28, 91, 721]) * (horizon // 7)
    np.testing.assert_array_equal(baseline_predictions(history, "seasonal_naive", horizon), expected)
    panel["Units_Sold"] = panel.Units_Sold.astype(object)
    panel.loc[panel.Date.gt(pd.Timestamp("2024-03-31")), "Units_Sold"] = "unknown future"
    pd.testing.assert_frame_equal(history, baseline_history(panel, origin="2024-03-31"))


@pytest.mark.parametrize("missing", ["date", "value"])
def test_baselines_fail_missing_observation_in_latest_week(missing):
    panel = week_panel()
    mask = panel.SKU_ID.eq("A") & panel.Warehouse_ID.eq("W1") & panel.Date.eq(pd.Timestamp("2024-03-27"))
    if missing == "date":
        panel = panel.loc[~mask]
    else:
        panel.loc[mask, "Units_Sold"] = np.nan
    with pytest.raises(ValueError, match="Incomplete baseline history"):
        baseline_history(panel, origin="2024-03-31")


@pytest.mark.parametrize("model,horizon", [("other", 1), ("naive", 2), ("naive", True), ("naive", 7.0)])
def test_baselines_reject_unapproved_models_horizons(model, horizon):
    history = baseline_history(week_panel(), origin="2024-03-31")
    with pytest.raises(ValueError):
        baseline_predictions(history, model, horizon)
