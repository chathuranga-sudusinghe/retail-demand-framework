"""Construct frozen CPU estimators; importing this module never fits a model."""
from __future__ import annotations

import json
from typing import Any, cast

import numpy as np
from threadpoolctl import threadpool_limits

from src.forecasting.configuration import (
    PRIMARY_MODELS, SUPPORTIVE_MODELS, CanonicalConfiguration, ModelName,
    primary_model_parameters, supportive_model_parameters,
)


def estimator_parameters(
    model: ModelName, configuration: CanonicalConfiguration | None = None,
) -> dict[str, Any]:
    """Reuse accepted declarations and add only frozen runtime/I/O controls."""
    if model in PRIMARY_MODELS:
        if configuration is None:
            raise ValueError("Primary construction requires an approved canonical configuration.")
        parameters = dict(primary_model_parameters(model, configuration))  # type: ignore[arg-type]
    elif model in SUPPORTIVE_MODELS:
        if configuration is not None:
            raise ValueError("Supportive models have one fixed configuration, not a GBM grid.")
        parameters = dict(supportive_model_parameters(model))  # type: ignore[arg-type]
    else:
        raise ValueError("Unknown learned model.")
    if model in ("xgboost", "lightgbm", "random_forest"):
        parameters["n_jobs"] = 1
    elif model == "catboost":
        parameters["thread_count"] = 1
        # Training logs/snapshots are unnecessary artifacts, not tuning dimensions.
        parameters["allow_writing_files"] = False
    return parameters


def construct_estimator(
    model: ModelName, configuration: CanonicalConfiguration | None = None,
) -> Any:
    """Lazy imports, exact requested recipe, no hidden fitting or file access."""
    parameters = estimator_parameters(model, configuration)
    if model == "xgboost":
        from xgboost import XGBRegressor
        return XGBRegressor(**parameters)
    if model == "lightgbm":
        from lightgbm import LGBMRegressor
        return LGBMRegressor(**parameters)
    if model == "catboost":
        from catboost import CatBoostRegressor
        return CatBoostRegressor(**parameters)
    if model == "ridge":
        from sklearn.linear_model import Ridge
        return Ridge(**parameters)
    from sklearn.ensemble import RandomForestRegressor
    return RandomForestRegressor(**parameters)


def effective_iterations(estimator: Any, model: ModelName) -> int | None:
    """Read fitted iteration/tree counts, not the requested constructor budget."""
    if model == "xgboost":
        return int(estimator.get_booster().num_boosted_rounds())
    if model == "lightgbm":
        return int(estimator.booster_.num_trees())
    if model == "catboost":
        return int(estimator.tree_count_)
    if model == "random_forest":
        return len(estimator.estimators_)
    return None


def effective_parameters(estimator: Any, model: ModelName) -> dict[str, Any]:
    """Capture sklearn defaults plus native fitted defaults without model binaries."""
    result = dict(estimator.get_params(deep=True))
    if model == "xgboost":
        result["native_configuration"] = json.loads(estimator.get_booster().save_config())
    elif model == "lightgbm":
        # model_to_string carries all native defaults in a dedicated parameter block;
        # tree values are deliberately discarded, not persisted in run metadata.
        text = estimator.booster_.model_to_string()
        if "parameters:\n" not in text or "end of parameters" not in text:
            raise ValueError("Cannot capture complete effective LightGBM defaults.")
        block = text.split("parameters:\n", 1)[1].split("end of parameters", 1)[0]
        result["native_parameters"] = dict(
            line.strip()[1:-1].split(": ", 1) for line in block.splitlines()
            if line.strip().startswith("[") and ": " in line
        )
    elif model == "catboost":
        result.update(estimator.get_all_params())
    return parameter_metadata(result)


def parameter_metadata(parameters: dict[str, Any]) -> dict[str, Any]:
    """Encode nonfinite library sentinels as null with their explicit meaning.

    XGBoost's inherited missing=np.nan is an API sentinel, not a metric or an
    imputed input. Retain that fact while prohibiting JSON NaN/infinity.
    """
    unavailable: dict[str, str] = {}

    def encode(value: Any, path: str) -> Any:
        if isinstance(value, dict):
            return {k: encode(v, f"{path}.{k}" if path else str(k)) for k, v in value.items()}
        if isinstance(value, (tuple, list)):
            return [encode(v, f"{path}[{i}]") for i, v in enumerate(value)]
        if isinstance(value, (float, np.floating)) and not np.isfinite(value):
            unavailable[path] = "library_nan_sentinel" if np.isnan(value) else "library_infinity_sentinel"
            return None
        return value

    result = encode(parameters, "")
    if unavailable:
        result["unavailable_parameter_values"] = unavailable
    return cast(dict[str, Any], result)


def fit_estimator(
    estimator: Any, model: ModelName, configuration: CanonicalConfiguration | None,
    matrix: Any, labels: Any,
) -> dict[str, Any]:
    """Fit historical inputs only; no eval_set, callbacks, continuation or kwargs.

    Called by the authorised runner or explicit synthetic tests. Check constructor
    tampering before fitting and exact iterations after fitting. Ridge BLAS is
    also limited to one thread without changing its approved solver.
    """
    expected = estimator_parameters(model, configuration)
    requested = estimator.get_params(deep=True)
    if any(requested.get(key) != value for key, value in expected.items()):
        raise ValueError("Estimator no longer matches the frozen runtime recipe.")
    forbidden = ("early_stopping_rounds", "early_stopping_round", "callbacks", "od_type",
                 "od_wait", "od_pval")
    if any(requested.get(key) is not None for key in forbidden):
        raise ValueError("Primary early stopping/callbacks are forbidden.")
    x, y = np.asarray(matrix, dtype=float), np.asarray(labels, dtype=float)
    if (x.ndim != 2 or y.ndim != 1 or len(x) != len(y) or not len(y)
            or not np.isfinite(x).all() or not np.isfinite(y).all()):
        raise ValueError("Fit requires aligned nonempty finite training inputs and labels.")
    with threadpool_limits(limits=1):
        # Numeric array avoids library restrictions on identity labels containing '='.
        estimator.fit(x, y)
    requested_iterations = configuration.boosting_iterations if configuration else (
        300 if model == "random_forest" else None
    )
    count = effective_iterations(estimator, model)
    if count != requested_iterations:
        raise ValueError(f"Iteration mismatch: requested {requested_iterations}, effective {count}.")
    effective = effective_parameters(estimator, model)
    if model == "xgboost":
        native = effective["native_configuration"]["learner"]["generic_param"]
        if native["device"] != "cpu" or native["nthread"] != "1" or native["seed"] != "42":
            raise ValueError("Effective XGBoost CPU/thread/seed controls differ from the frozen recipe.")
    elif model == "lightgbm":
        native = effective["native_parameters"]
        controls = {
            "device_type": "cpu", 
            "num_threads": "1", 
            "seed": "42",
            "deterministic": "1", 
            "force_col_wise": "1", 
            "force_row_wise": "0",
            "bagging_freq": "1"
            }
        if any(native.get(key) != value for key, value in controls.items()):
            raise ValueError("Effective LightGBM runtime controls differ from the frozen recipe.")
    elif model == "catboost":
        cat_controls: dict[str, Any] = {
            "task_type": "CPU", 
            "thread_count": 1, 
            "random_seed": 42, 
            "use_best_model": False
            }
        if any(effective.get(key) != value for key, value in cat_controls.items()):
            raise ValueError("Effective CatBoost runtime controls differ from the frozen recipe.")
    return {"requested_api_parameters": expected,
            "effective_api_parameters": effective,
            "requested_iterations": requested_iterations, "effective_iterations": count}
