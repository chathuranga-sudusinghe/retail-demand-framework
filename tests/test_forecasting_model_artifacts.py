"""Controlled native serialization smoke tests, never project data or research evidence."""
import json
from unittest.mock import Mock
import numpy as np
import pandas as pd
import pytest
from src.forecasting import model_artifacts
from src.forecasting.configuration import PRIMARY_GRID, PRIMARY_MODELS, SUPPORTIVE_MODELS
from src.forecasting.features import FEATURE_COLUMNS
from src.forecasting.metadata import initial_metadata, REPOSITORY
from src.forecasting.models import construct_estimator, fit_estimator
from src.forecasting.preprocessing import fit_preprocessor, preprocessor_state, restore_preprocessor
from test_forecasting_experiment import authorization


def synthetic_features():
    rng = np.random.default_rng(42)
    data = pd.DataFrame(rng.normal(size=(200, len(FEATURE_COLUMNS))), columns=FEATURE_COLUMNS)
    data["SKU_ID"], data["Warehouse_ID"] = "synthetic", "synthetic"
    data["Date"] = pd.date_range("2024-01-01", periods=200)
    return data, rng.normal(size=200)


@pytest.mark.parametrize("model", [*PRIMARY_MODELS, *SUPPORTIVE_MODELS])
def test_native_saved_model_and_preprocessor_replay_exact_predictions(tmp_path, model, monkeypatch):
    features, labels = synthetic_features()
    state = fit_preprocessor(features, model, training_end="2024-07-18", horizon=1)
    restored = restore_preprocessor(json.loads(json.dumps(preprocessor_state(state))))
    pd.testing.assert_frame_equal(state.transform(features), restored.transform(features))
    configuration = PRIMARY_GRID[0] if model in PRIMARY_MODELS else None
    estimator = construct_estimator(model, configuration)
    fitted = fit_estimator(estimator, model, configuration, state.transform(features).to_numpy(), labels)
    metadata = initial_metadata(authorization(), REPOSITORY)
    metadata.update(git_commit_sha="synthetic", python_version="3.12.3", library_versions={})
    candidate = {"run_id": metadata["run_id"], "evaluation_stage": "validation", "model": model,
                 "horizon": 1, "fold_id": 1, "configuration_id": "GBM001" if configuration else "fixed",
                 "representation_id": "synthetic", "training_start": "2024-01-01", "training_end": "2024-07-18",
                 "outcome_window_start": "2024-07-19", "outcome_window_end": "2024-08-15",
                 "target_start_date": "2024-07-19", "target_end_date": "2024-07-19",
                 "training_population_hash": "synthetic", **fitted}
    origin = features.iloc[-5:]
    from threadpoolctl import threadpool_limits
    with threadpool_limits(limits=1):
        expected = np.asarray(estimator.predict(state.transform(origin).to_numpy().copy()), dtype=float)
    model_path = Mock(wraps=model_artifacts.RepositoryLayout.candidate_model_directory)
    state_path = Mock(wraps=model_artifacts.RepositoryLayout.preprocessing_state_directory)
    monkeypatch.setattr(model_artifacts.RepositoryLayout, "candidate_model_directory", model_path)
    monkeypatch.setattr(model_artifacts.RepositoryLayout, "preprocessing_state_directory", state_path)
    record = model_artifacts.persist_model(tmp_path, estimator, candidate, state, origin, metadata)
    model_path.assert_called_once_with(tmp_path, model, 1, candidate["configuration_id"], 1)
    state_path.assert_called_once_with(tmp_path, model, 1, 1)
    restored_features, predictions = model_artifacts.replay_model(tmp_path, record, metadata)
    assert len(restored_features) == 5
    np.testing.assert_array_equal(predictions, expected)
    path = tmp_path / record["model_path"]
    path.write_bytes(path.read_bytes() + b"corruption")
    with pytest.raises(ValueError, match="hash mismatch"):
        model_artifacts.replay_model(tmp_path, record, metadata)


def test_rejects_invalid_preprocessing_order_and_scaling():
    features, _ = synthetic_features()
    state = fit_preprocessor(features, "ridge", training_end="2024-07-18", horizon=1)
    value = preprocessor_state(state)
    value["physical_feature_names"] = list(reversed(value["physical_feature_names"]))
    with pytest.raises(ValueError, match="order"):
        restore_preprocessor(value)
    value = preprocessor_state(state)
    value["numerical_scales"] = (-1,) * len(FEATURE_COLUMNS)
    with pytest.raises(ValueError, match="scaling"):
        restore_preprocessor(value)


def test_model_reference_cannot_escape_run_directory(tmp_path):
    with pytest.raises(ValueError, match="escapes"):
        model_artifacts.safe_path(tmp_path, "../outside.joblib")


def test_model_persistence_rejects_completed_run_before_any_write(tmp_path, monkeypatch):
    (tmp_path / "run_manifest.json").write_text("completed")
    before = {p.relative_to(tmp_path): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    saver = Mock(side_effect=AssertionError("Completed evidence must not be touched."))
    monkeypatch.setattr(model_artifacts, "_save_estimator", saver)
    with pytest.raises(FileExistsError, match="published run cannot be modified"):
        model_artifacts.persist_model(tmp_path, None, {}, None, None, {})
    assert {p.relative_to(tmp_path): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == before
    assert not (tmp_path / "models").exists()
    saver.assert_not_called()


@pytest.mark.parametrize("name", ["state.json", "origin_features.json", "descriptor.json"])
def test_public_json_persistence_rejects_completed_run_without_temporary_files(tmp_path, name):
    path = tmp_path / "models" / name
    path.parent.mkdir()
    path.write_text("original evidence")
    (tmp_path / "run_manifest.json").write_text("completed")
    before = {p.relative_to(tmp_path): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    with pytest.raises(FileExistsError, match="published run cannot be modified"):
        model_artifacts.atomic_json(path, {"changed": True}, directory=tmp_path)
    assert {p.relative_to(tmp_path): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == before
