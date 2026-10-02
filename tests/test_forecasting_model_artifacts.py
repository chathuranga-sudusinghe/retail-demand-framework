"""Controlled native serialization smoke tests, never project data or research evidence."""
import json
import re
from pathlib import Path
from unittest.mock import Mock
import numpy as np
import pandas as pd
import pytest
from src.forecasting import model_artifacts, reporting
from src.forecasting.artifacts import ArtifactWriter, file_hash
from src.forecasting.paths import RepositoryLayout
from src.forecasting.configuration import PRIMARY_GRID, PRIMARY_MODELS, SUPPORTIVE_MODELS
from src.forecasting.features import FEATURE_COLUMNS
from src.forecasting.metadata import initial_metadata, REPOSITORY
from src.forecasting.models import construct_estimator, fit_estimator
from src.forecasting.preprocessing import fit_preprocessor, preprocessor_state, restore_preprocessor
from test_forecasting_orchestration import authorization


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
    writer = ArtifactWriter(tmp_path, metadata["run_id"])
    directory = writer.directory
    record = model_artifacts.persist_model(directory, estimator, candidate, state, origin, metadata)
    model_path.assert_called_once_with(directory, model, 1, candidate["configuration_id"], 1)
    state_path.assert_called_once_with(directory, model, 1, 1)
    for key in ("model", "descriptor", "preprocessor", "origin_features"):
        path = model_artifacts.safe_path(directory, record[f"{key}_path"])
        assert path == tmp_path / record[f"{key}_path"]
        assert path.is_relative_to(writer.model_directory)
        assert file_hash(path) == record[f"{key}_hash"]
    assert not list(directory.iterdir())
    assert not list(writer.report_directory.iterdir())
    descriptor = json.loads((tmp_path / record["descriptor_path"]).read_text())
    assert descriptor["descriptor_version"] == 2
    assert descriptor["source_hashes"] == directory.relative_to(tmp_path).as_posix() + "/run_metadata.json#source_hashes"
    restored_features, predictions = model_artifacts.replay_model(directory, record, metadata)
    assert len(restored_features) == 5
    np.testing.assert_array_equal(predictions, expected)
    if model in PRIMARY_MODELS:
        other = model_artifacts.persist_model(directory, estimator, {**candidate, "configuration_id": "GBM002"},
                                              state, origin, metadata)
        assert other["model_path"] != record["model_path"]
        assert other["descriptor_path"] != record["descriptor_path"]
        assert other["preprocessor_path"] == record["preprocessor_path"]
        assert other["origin_features_path"] == record["origin_features_path"]
        np.testing.assert_array_equal(model_artifacts.replay_model(directory, other, metadata)[1], expected)
        np.testing.assert_array_equal(model_artifacts.replay_model(directory, record, metadata)[1], expected)
    if model == "xgboost":
        changed_origin = origin.copy()
        changed_origin.loc[changed_origin.index[0], FEATURE_COLUMNS[0]] += 1
        with pytest.raises(ValueError, match="Shared preprocessing evidence changed"):
            model_artifacts.persist_model(directory, estimator, {**candidate, "configuration_id": "GBM003"},
                                          state, changed_origin, metadata)
        np.testing.assert_array_equal(model_artifacts.replay_model(directory, record, metadata)[1], expected)
        np.testing.assert_array_equal(model_artifacts.replay_model(directory, other, metadata)[1], expected)
    # Completion authority stays at the artifact anchor, including model writes.
    writer.write_json("run_manifest.json", {"synthetic_completion_marker": True})
    np.testing.assert_array_equal(model_artifacts.replay_model(directory, record, metadata)[1], expected)
    with pytest.raises(FileExistsError, match="published run cannot be modified"):
        model_artifacts.persist_model(directory, estimator, candidate, state, origin, metadata)
    loader = Mock(side_effect=AssertionError("Corrupt evidence must not be deserialized."))
    monkeypatch.setattr(model_artifacts, "_load_estimator", loader)
    for key in ("descriptor", "model", "preprocessor", "origin_features"):
        path = tmp_path / record[f"{key}_path"]
        original = path.read_bytes()
        path.write_bytes(original + b"corruption")
        with pytest.raises(ValueError, match="hash mismatch"):
            model_artifacts.replay_model(directory, record, metadata)
        path.write_bytes(original)
    for key in ("descriptor", "model", "preprocessor", "origin_features"):
        rejected = {**record, f"{key}_path": record[f"{key}_path"].replace(f"/{directory.name}/", "/other-run/")}
        with pytest.raises(ValueError, match="escapes"):
            model_artifacts.replay_model(directory, rejected, metadata)
    descriptor_path = tmp_path / record["descriptor_path"]
    original = descriptor_path.read_bytes()
    descriptor_path.write_text(json.dumps({**descriptor, "descriptor_version": 1}))
    legacy_record = {**record, "descriptor_hash": file_hash(descriptor_path)}
    with pytest.raises(ValueError, match="Only version-2 validation candidate"):
        model_artifacts.replay_model(directory, legacy_record, metadata)
    descriptor_path.write_bytes(original)
    if model == "ridge":
        descriptor_path = tmp_path / record["descriptor_path"]
        original = descriptor_path.read_bytes()
        descriptor["source_hashes"] = "artifacts/forecasting/other-run/run_metadata.json#source_hashes"
        descriptor_path.write_text(json.dumps(descriptor))
        changed_record = {**record, "descriptor_hash": file_hash(descriptor_path)}
        with pytest.raises(ValueError, match="source provenance reference differs"):
            model_artifacts.replay_model(directory, changed_record, metadata)
        descriptor_path.write_bytes(original)
    loader.assert_not_called()


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


@pytest.mark.parametrize("reference", [
    "../outside.joblib", "/tmp/outside.joblib",
    "models/forecasting/other-run/validation/model.joblib",
    "artifacts/forecasting/synthetic/model.joblib",
    "reports/forecasting/drafts/synthetic/model.joblib",
    "models/forecasting/synthetic/../other-run/model.joblib",
    "models/forecasting/synthetic/./model.joblib",
    r"models\forecasting\synthetic\model.joblib",
    "models/forecasting/synthetic//model.joblib",
])
def test_model_reference_cannot_escape_model_run_directory(tmp_path, reference):
    writer = ArtifactWriter(tmp_path, "synthetic")
    with pytest.raises(ValueError, match="escapes"):
        model_artifacts.safe_path(writer.directory, reference)


def snapshot_files(repository):
    return {p.relative_to(repository): p.read_bytes() for p in repository.rglob("*") if p.is_file()}


def test_model_persistence_rejects_completed_run_before_any_write(tmp_path, monkeypatch):
    writer = ArtifactWriter(tmp_path, "synthetic")
    writer.write_json("run_manifest.json", {"synthetic_completion_marker": True})
    before = snapshot_files(tmp_path)
    saver = Mock(side_effect=AssertionError("Completed evidence must not be touched."))
    monkeypatch.setattr(model_artifacts, "_save_estimator", saver)
    with pytest.raises(FileExistsError, match="published run cannot be modified"):
        model_artifacts.persist_model(writer.directory, None, {}, None, None, {})
    assert snapshot_files(tmp_path) == before
    assert not list(writer.model_directory.iterdir())
    saver.assert_not_called()


@pytest.mark.parametrize("name", ["state.json", "origin_features.json", "descriptor.json"])
def test_public_json_persistence_rejects_completed_run_without_temporary_files(tmp_path, name):
    writer = ArtifactWriter(tmp_path, "synthetic")
    folder = (RepositoryLayout.candidate_model_directory(writer.directory, "ridge", 1, "fixed", 1)
              if name == "descriptor.json"
              else RepositoryLayout.preprocessing_state_directory(writer.directory, "ridge", 1, 1))
    folder.mkdir(parents=True)
    path = folder / name
    path.write_text("original evidence")
    writer.write_json("run_manifest.json", {"synthetic_completion_marker": True})
    before = snapshot_files(tmp_path)
    with pytest.raises(FileExistsError, match="published run cannot be modified"):
        model_artifacts.atomic_json(path, {"changed": True}, directory=writer.directory)
    assert snapshot_files(tmp_path) == before


@pytest.mark.parametrize("owner", ["artifact", "model", "report"])
def test_writer_rejects_existing_run_storage_without_creating_other_directories(tmp_path, owner):
    layout = RepositoryLayout(tmp_path)
    directories = {"artifact": layout.run_directory("synthetic"),
                   "model": layout.model_run_directory("synthetic"),
                   "report": layout.draft_report_directory("synthetic")}
    directories[owner].mkdir(parents=True)
    sentinel = directories[owner] / "retained.txt"
    sentinel.write_text("previous evidence")
    with pytest.raises(FileExistsError, match="already exists"):
        ArtifactWriter(layout, "synthetic")
    assert sentinel.read_text() == "previous evidence"
    assert all(not path.exists() for key, path in directories.items() if key != owner)


def test_draft_report_location_links_receipts_and_pending_review(tmp_path):
    from test_forecasting_observability import saved_evidence
    writer = saved_evidence.__wrapped__(tmp_path)
    for name in ("predictions.csv", "eligibility_counts.csv"):
        writer.write_csv(name, [])
    before = snapshot_files(writer.repository)
    text = reporting.comparison_text(writer.directory, require_verified=False)
    assert snapshot_files(writer.repository) == before
    writer.write_comparison(text)
    path = writer.report_directory / "comparison.md"
    assert path.read_text() == text
    assert not (writer.directory / "comparison.md").exists()
    assert "pending human review" in text and "pending_human_review" in text
    assert "Human selection/freeze remains pending" in text
    assert not (writer.directory / "run_manifest.json").exists()
    names = {"run_manifest.json", "run_metadata.json", "configuration_summary.csv",
             "selected_configurations.json", "fold_metrics.csv", "predictions.csv", "eligibility_counts.csv"}
    links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
    assert {Path(link).name for link in links} == names
    for link in links:
        assert not Path(link).is_absolute()
        target = (path.parent / link).resolve()
        assert target == writer.directory / Path(link).name
        if target.name != "run_manifest.json":
            assert target.is_file()
    receipt = next(r for r in writer.manifest() if r["artifact_path"].endswith("/comparison.md"))
    assert receipt == {"artifact_path": path.relative_to(writer.repository).as_posix(),
                       "artifact_hash": file_hash(path), "artifact_status": "written", "diagnostic_paths": []}
    writer.write_json("run_manifest.json", {"synthetic_completion_marker": True})
    before = snapshot_files(writer.repository)
    with pytest.raises(FileExistsError, match="published run cannot be modified"):
        writer.write_comparison("changed")
    assert snapshot_files(writer.repository) == before


@pytest.mark.parametrize("operation", ["model_reference", "model_json", "draft_report"])
def test_split_storage_rejects_symlink_redirection_before_writing(tmp_path, operation):
    writer = ArtifactWriter(tmp_path, "synthetic")
    external = tmp_path / "unowned.txt"
    external.write_text("must remain unchanged")
    if operation == "draft_report":
        destination = writer.report_directory / "comparison.md.tmp"
        def write():
            writer.write_comparison("changed")
    else:
        destination = writer.model_directory / "state.json"
        reference = destination.relative_to(tmp_path).as_posix()
        def write():
            if operation == "model_reference":
                model_artifacts.safe_path(writer.directory, reference)
            else:
                model_artifacts.atomic_json(destination, {"changed": True}, directory=writer.directory)
    destination.symlink_to(external)
    with pytest.raises(ValueError, match="symlink"):
        write()
    assert external.read_text() == "must remain unchanged"


@pytest.mark.parametrize("candidate_id,metadata_id", [("other-run", "synthetic"), ("synthetic", "other-run")])
def test_model_write_and_replay_reject_identity_mismatch_before_serialization(tmp_path, monkeypatch, candidate_id, metadata_id):
    writer = ArtifactWriter(tmp_path, "synthetic")
    saver, loader = Mock(), Mock()
    monkeypatch.setattr(model_artifacts, "_save_estimator", saver)
    monkeypatch.setattr(model_artifacts, "_load_estimator", loader)
    candidate, metadata = {"run_id": candidate_id}, {"run_id": metadata_id}
    with pytest.raises(ValueError, match="identity differs"):
        model_artifacts.persist_model(writer.directory, None, candidate, None, None, metadata)
    with pytest.raises(ValueError, match="identity differs"):
        model_artifacts.replay_model(writer.directory, candidate, metadata)
    saver.assert_not_called()
    loader.assert_not_called()
    assert snapshot_files(tmp_path) == {}


@pytest.mark.parametrize("exception", [OSError("synthetic save failure"), KeyboardInterrupt()])
def test_failed_or_interrupted_model_write_keeps_partial_evidence_unpublished(tmp_path, monkeypatch, exception):
    writer = ArtifactWriter(tmp_path, "synthetic")
    partial = b"partial native bytes"

    def fail_save(estimator, model, path):
        path.write_bytes(partial)
        raise exception

    monkeypatch.setattr(model_artifacts, "_save_estimator", fail_save)
    candidate = {"run_id": "synthetic", "model": "ridge", "horizon": 1, "configuration_id": "fixed", "fold_id": 1}
    with pytest.raises(type(exception)) as caught:
        model_artifacts.persist_model(writer.directory, None, candidate, None, None, {"run_id": "synthetic"})
    assert caught.value is exception
    folder = RepositoryLayout.candidate_model_directory(writer.directory, "ridge", 1, "fixed", 1)
    assert (folder / "model.tmp.joblib").read_bytes() == partial
    assert not (folder / "descriptor.json").exists()
    assert not (writer.directory / "run_manifest.json").exists()
    assert not list(writer.report_directory.iterdir())
    with pytest.raises(FileExistsError, match="already exists"):
        ArtifactWriter(tmp_path, "synthetic")


def test_report_default_verification_remains_required(tmp_path, monkeypatch):
    from src.forecasting import integrity
    writer = ArtifactWriter(tmp_path, "synthetic")
    verifier = Mock(side_effect=integrity.IntegrityError("Synthetic unverified run"))
    monkeypatch.setattr(integrity, "verify_completed", verifier)
    with pytest.raises(integrity.IntegrityError, match="unverified"):
        reporting.comparison_text(writer.directory)
    verifier.assert_called_once_with(writer.directory)
    assert snapshot_files(tmp_path) == {}
