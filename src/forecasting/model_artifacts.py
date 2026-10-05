"""Native validation model persistence and replay; never refit or promote models."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from src.forecasting.artifacts import file_hash, json_text, require_mutable_run
from src.forecasting.paths import RepositoryLayout
from src.forecasting.preprocessing import ForecastPreprocessor, preprocessor_state, restore_preprocessor

# Version 2 uses repository-relative references owned by the artifact run.
DESCRIPTOR_VERSION = 2

FORMATS = {"xgboost": "ubj", "lightgbm": "txt", "catboost": "cbm",
           "ridge": "joblib", "random_forest": "joblib"}


def atomic_json(path: Path, value: Any, *, directory: Path) -> None:
    require_mutable_run(directory)
    layout = RepositoryLayout.from_artifact_directory(directory)
    path = safe_path(directory, path.relative_to(layout.root).as_posix())
    temporary = safe_path(directory, path.with_name(path.name + ".tmp").relative_to(layout.root).as_posix())
    temporary.write_text(json_text(value), encoding="utf-8")
    temporary.replace(path)


def safe_path(directory: Path, relative: str) -> Path:
    """Resolve a repository-relative model reference owned by the artifact run."""
    layout = RepositoryLayout.from_artifact_directory(directory)
    reference = Path(relative)
    if (reference.is_absolute() or ".." in reference.parts or "\\" in relative
            or reference.as_posix() != relative):
        raise ValueError("Model reference escapes its run directory.")
    path = layout.repository_path(relative)
    if not path.is_relative_to(layout.model_run_directory(directory.name)):
        raise ValueError("Model reference escapes its run directory.")
    return layout._owned_path(path)


def _save_estimator(estimator: Any, model: str, path: Path) -> None:
    if model == "lightgbm":
        estimator.booster_.save_model(str(path), num_iteration=-1)
    elif model in ("xgboost", "catboost"):
        estimator.save_model(str(path))
    else:
        joblib.dump(estimator, path)


def _load_estimator(model: str, path: Path) -> Any:
    if model == "xgboost":
        from xgboost import XGBRegressor
        estimator = XGBRegressor(n_jobs=1, device="cpu")
        estimator.load_model(path)
        return estimator
    if model == "lightgbm":
        from lightgbm import Booster
        return Booster(model_file=str(path))
    if model == "catboost":
        from catboost import CatBoostRegressor
        estimator = CatBoostRegressor(thread_count=1, task_type="CPU")
        estimator.load_model(str(path))
        return estimator
    # Callers verify provenance and hashes before loading trusted local joblib.
    return joblib.load(path)


def persist_model(directory: Path, estimator: Any, candidate: dict[str, Any],
                  state: ForecastPreprocessor, origin_features: pd.DataFrame,
                  metadata: dict[str, Any]) -> dict[str, Any]:
    require_mutable_run(directory)
    layout = RepositoryLayout.from_artifact_directory(directory)
    if candidate["run_id"] != directory.name or metadata["run_id"] != directory.name:
        raise ValueError("Model identity differs from the artifact run.")
    model = candidate["model"]
    folder = RepositoryLayout.candidate_model_directory(
        directory, model, candidate["horizon"], candidate["configuration_id"], candidate["fold_id"],
    )
    state_folder = RepositoryLayout.preprocessing_state_directory(
        directory, model, candidate["horizon"], candidate["fold_id"],
    )
    folder.mkdir(parents=True, exist_ok=False)
    filename = f"model.{FORMATS[model]}"
    path = safe_path(directory, (folder / filename).relative_to(layout.root).as_posix())
    temporary = safe_path(directory, (folder / f"model.tmp.{FORMATS[model]}").relative_to(layout.root).as_posix())
    _save_estimator(estimator, model, temporary)
    temporary.replace(path)
    state_folder.mkdir(parents=True, exist_ok=True)
    state_path = safe_path(directory, (state_folder / "state.json").relative_to(layout.root).as_posix())
    features_path = safe_path(directory, (state_folder / "origin_features.json").relative_to(layout.root).as_posix())
    values = {state_path: preprocessor_state(state),
              features_path: origin_features.loc[:, list(state.conceptual_feature_names)].to_dict(orient="records")}
    for destination, value in values.items():
        if destination.exists():
            if destination.read_text(encoding="utf-8") != json_text(value):
                raise ValueError("Shared preprocessing evidence changed within a run.")
        else:
            atomic_json(destination, value, directory=directory)
    references = {"model": path, "preprocessor": state_path, "origin_features": features_path}
    record = {**{key: candidate[key] for key in (
        "run_id", "evaluation_stage", "model", "horizon", "configuration_id", "fold_id", "representation_id")},
        **{f"{key}_path": value.relative_to(layout.root).as_posix() for key, value in references.items()},
        **{f"{key}_hash": file_hash(value) for key, value in references.items()}}
    descriptor = {**record, "artifact_kind": "validation_candidate", "descriptor_version": DESCRIPTOR_VERSION,
                  "training_start": candidate["training_start"], "training_end": candidate["training_end"],
                  "validation_start": candidate["outcome_window_start"], "validation_end": candidate["outcome_window_end"],
                  "target_start_date": candidate["target_start_date"], "target_end_date": candidate["target_end_date"],
                  "training_population_hash": candidate["training_population_hash"],
                  "requested_api_parameters": candidate["requested_api_parameters"],
                  "effective_api_parameters": candidate["effective_api_parameters"],
                  "git_commit_sha": metadata["git_commit_sha"],
                  "source_hashes": (directory / "run_metadata.json").relative_to(layout.root).as_posix() + "#source_hashes",
                  "protocol_hash": metadata["protocol_hash"], "feature_contract_hash": metadata["feature_contract_hash"],
                  "input_view_hash": metadata["input_view_hash"], "python_version": metadata["python_version"],
                  "library_versions": metadata["library_versions"]}
    descriptor_path = folder / "descriptor.json"
    atomic_json(descriptor_path, descriptor, directory=directory)
    return {**record, "descriptor_path": descriptor_path.relative_to(layout.root).as_posix(),
            "descriptor_hash": file_hash(descriptor_path)}


def replay_model(directory: Path, record: dict[str, Any], metadata: dict[str, Any]) -> tuple[pd.DataFrame, np.ndarray]:
    layout = RepositoryLayout.from_artifact_directory(directory)
    if record["run_id"] != directory.name or metadata["run_id"] != directory.name:
        raise ValueError("Model identity differs from the artifact run.")
    for key in ("descriptor", "model", "preprocessor", "origin_features"):
        if file_hash(safe_path(directory, record[f"{key}_path"])) != record[f"{key}_hash"]:
            raise ValueError("Persisted model evidence hash mismatch.")
    descriptor = json.loads(safe_path(directory, record["descriptor_path"]).read_text(encoding="utf-8"))
    if descriptor.get("artifact_kind") != "validation_candidate" or descriptor.get("descriptor_version") != DESCRIPTOR_VERSION:
        raise ValueError("Only version-2 validation candidate models may be replayed.")
    source_reference = (directory / "run_metadata.json").relative_to(layout.root).as_posix() + "#source_hashes"
    if descriptor.get("source_hashes") != source_reference:
        raise ValueError("Model source provenance reference differs from the artifact run.")
    for key, value in record.items():
        if key not in ("descriptor_path", "descriptor_hash") and descriptor.get(key) != value:
            raise ValueError("Model descriptor/index relationship differs.")
    for key in ("run_id", "protocol_hash", "feature_contract_hash", "input_view_hash", "git_commit_sha", "python_version", "library_versions"):
        if descriptor[key] != metadata[key]:
            raise ValueError("Model provenance differs from the run.")
    state = restore_preprocessor(json.loads(safe_path(directory, record["preprocessor_path"]).read_text(encoding="utf-8")))
    if state.model != record["model"] or state.horizon != record["horizon"] or state.training_end.date().isoformat() != descriptor["training_end"]:
        raise ValueError("Model/preprocessor timing or family differs.")
    features = pd.DataFrame(json.loads(safe_path(directory, record["origin_features_path"]).read_text(encoding="utf-8")))
    matrix = state.transform(features).to_numpy(dtype=float)
    estimator = _load_estimator(record["model"], safe_path(directory, record["model_path"]))
    with threadpool_limits(limits=1):
        if record["model"] == "lightgbm":
            predictions = estimator.predict(matrix.copy(), num_threads=1)
        elif record["model"] == "catboost":
            predictions = estimator.predict(matrix.copy(), thread_count=1)
        else:
            predictions = estimator.predict(matrix.copy())
    predictions = np.asarray(predictions, dtype=float)
    if predictions.shape != (len(features),) or not np.isfinite(predictions).all():
        raise ValueError("Reloaded model predictions are invalid.")
    return features, predictions
