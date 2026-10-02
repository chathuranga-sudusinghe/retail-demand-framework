"""Fault injection against complete synthetic mocked bundles; no research runs."""
import csv
import json
from pathlib import Path
from unittest.mock import Mock
import pytest
from src.forecasting import orchestration, integrity, model_artifacts, reporting
from src.forecasting.artifacts import ArtifactWriter, file_hash
from src.forecasting.paths import RepositoryLayout
from test_forecasting_orchestration import (authorization, install_synthetic_runner_mocks,
                                         panel, scope)
from test_forecasting_orchestration import prepared_folds as _prepared_folds


@pytest.fixture
def prepared_folds():
    return _prepared_folds.__wrapped__()


@pytest.fixture
def complete_bundle(tmp_path, monkeypatch, prepared_folds):
    install_synthetic_runner_mocks(monkeypatch, tmp_path, prepared_folds)
    approved = authorization(supplied_scope=scope(primary=(), supportive=("ridge",), horizons=(1,)))
    return orchestration.run_validation(panel(), run_id=approved.run_id, authorization=approved)


def test_completed_bundle_manifest_counts_hashes_and_readonly_reporting(complete_bundle):
    result = integrity.verify_completed(complete_bundle)
    assert result == {"status": "passed", "evaluations": 12, "predictions": 24,
                      "configuration_summaries": 3, "models_replayed": 4}
    manifest = json.loads((complete_bundle / "run_manifest.json").read_text())
    assert manifest["metadata_hash"] == file_hash(complete_bundle / "run_metadata.json")
    layout = RepositoryLayout.from_artifact_directory(complete_bundle)
    assert manifest["manifest_version"] == 2
    assert manifest["run_id"] == complete_bundle.name
    assert {entry["owner"] for entry in manifest["artifacts"]} == {"artifacts", "models", "reports"}
    paths = {layout.root / entry["path"] for entry in manifest["artifacts"]}
    assert complete_bundle / "run_manifest.json" not in paths
    assert layout.draft_report_directory(complete_bundle.name) / "comparison.md" in paths
    metadata = json.loads((complete_bundle / "run_metadata.json").read_text())
    assert len(metadata["model_artifacts"]) == result["models_replayed"] == 4
    for record in metadata["model_artifacts"]:
        for key in ("model", "descriptor", "preprocessor", "origin_features"):
            assert layout.root / record[f"{key}_path"] in paths
    assert paths == {p for root in storage_directories(complete_bundle).values()
                     for p in root.rglob("*") if p.is_file() and p != complete_bundle / "run_manifest.json"}
    before = {p: p.read_bytes() for p in paths | {complete_bundle / "run_manifest.json"}}
    assert "pending human review" in reporting.comparison_text(complete_bundle)
    assert before == {p: p.read_bytes() for p in before}


@pytest.mark.parametrize("name", ["run_manifest.json", "predictions.csv", "fold_metrics.csv", "comparison.md", "run.log", "authorization.json"])
def test_missing_artifact_rejected(complete_bundle, name):
    layout = RepositoryLayout.from_artifact_directory(complete_bundle)
    parent = layout.draft_report_directory(complete_bundle.name) if name == "comparison.md" else complete_bundle
    (parent / name).unlink()
    with pytest.raises(integrity.IntegrityError):
        integrity.verify_completed(complete_bundle)
    with pytest.raises(integrity.IntegrityError):
        reporting.comparison_text(complete_bundle)


@pytest.mark.parametrize("name", ["run_metadata.json", "fold_metrics.csv", "predictions.csv", "run.log", "comparison.md"])
def test_corrupt_artifact_rejected(complete_bundle, name):
    root = storage_directories(complete_bundle)["reports"] if name == "comparison.md" else complete_bundle
    path = root / name
    path.write_bytes(path.read_bytes() + b"corrupt")
    with pytest.raises(integrity.IntegrityError):
        integrity.verify_completed(complete_bundle)


@pytest.mark.parametrize("field", ["completed_counts", "model_artifacts", "candidate_records", "selection_records"])
def test_semantic_corruption_rejected_even_before_hash_manifest(complete_bundle, field):
    path = complete_bundle / "run_metadata.json"
    metadata = json.loads(path.read_text())
    metadata[field] = {} if field == "completed_counts" else []
    if field == "selection_records":
        metadata[field] = [{"model": "xgboost", "horizon": 28, "configuration_id": "GBM024"}]
    path.write_text(json.dumps(metadata))
    with pytest.raises(integrity.IntegrityError):
        integrity.verify_scientific(complete_bundle)


@pytest.mark.parametrize("kind", ["model", "descriptor", "preprocessor", "origin_features"])
def test_missing_model_evidence_rejected(complete_bundle, kind):
    metadata = json.loads((complete_bundle / "run_metadata.json").read_text())
    model_artifacts.safe_path(complete_bundle, metadata["model_artifacts"][0][f"{kind}_path"]).unlink()
    with pytest.raises(integrity.IntegrityError):
        integrity.verify_scientific(complete_bundle)


def test_replay_mismatch_rejected(complete_bundle, monkeypatch):
    class WrongModel:
        def predict(self, matrix):
            import numpy as np
            return np.full(len(matrix), 999)
    monkeypatch.setattr(model_artifacts, "_load_estimator", lambda *args: WrongModel())
    with pytest.raises(integrity.IntegrityError, match="Reloaded predictions"):
        integrity.verify_scientific(complete_bundle)


@pytest.mark.parametrize("point", ["startup", "report", "manifest", "model", "model_after_write", "interrupt", "verification"])
def test_failure_never_publishes_completion_and_preserves_original(tmp_path, monkeypatch, prepared_folds, point):
    install_synthetic_runner_mocks(monkeypatch, tmp_path, prepared_folds)
    approved = authorization(supplied_scope=scope(primary=(), supportive=("ridge",), horizons=(1,), baselines=()))
    original = KeyboardInterrupt("controlled interrupt") if point == "interrupt" else OSError("controlled original")
    def fail(*args, **kwargs):
        if point == "model_after_write":
            args[-1].write_text("partial synthetic model")
        raise original
    if point == "report":
        monkeypatch.setattr(ArtifactWriter, "write_comparison", fail)
    elif point in ("model", "model_after_write"):
        monkeypatch.setattr(model_artifacts, "_save_estimator", fail)
    elif point == "interrupt":
        monkeypatch.setattr(orchestration, "fit_estimator", fail)
    elif point == "verification":
        monkeypatch.setattr(orchestration, "verify_scientific", fail)
    else:
        real = ArtifactWriter.write_json
        def write(self, name, value):
            if (point == "startup" and name == "run_metadata.json") or (point == "manifest" and name == "run_manifest.json"):
                raise original
            return real(self, name, value)
        monkeypatch.setattr(ArtifactWriter, "write_json", write)
    with pytest.raises(type(original)) as caught:
        orchestration.run_validation(panel(), run_id=approved.run_id, authorization=approved)
    assert caught.value is original
    directory = RepositoryLayout(tmp_path).run_directory(approved.run_id)
    assert not (directory / "run_manifest.json").exists()
    with pytest.raises(integrity.IntegrityError):
        integrity.verify_completed(directory)
    if point != "startup":
        metadata = json.loads((directory / "run_metadata.json").read_text())
        assert metadata["run_status"] == ("interrupted" if point == "interrupt" else "failed")
        assert metadata["selection_records"] == [] and metadata["completed_at_utc"] is None
        if point in ("model", "model_after_write"):
            assert metadata["completed_counts"]["supportive_fits"] == 1
        if point in ("report", "manifest", "verification"):
            assert len(metadata["model_artifacts"]) == 4
            for record in metadata["model_artifacts"]:
                for key in ("model", "descriptor", "preprocessor", "origin_features"):
                    assert file_hash(model_artifacts.safe_path(directory, record[f"{key}_path"])) == record[f"{key}_hash"]
    roots = storage_directories(directory)
    assert all(root.is_dir() and not (root / "run_manifest.json").exists() for root in roots.values())
    if point == "model_after_write":
        leftovers = list(roots["models"].rglob("model.tmp.joblib"))
        assert len(leftovers) == 1 and leftovers[0].read_text() == "partial synthetic model"
    before = {p: p.read_bytes() for root in roots.values() for p in root.rglob("*") if p.is_file()}
    with pytest.raises(FileExistsError):
        ArtifactWriter(tmp_path, approved.run_id)
    assert before == {p: p.read_bytes() for p in before}


def test_manifest_is_last_write_and_requires_verification(tmp_path, monkeypatch, prepared_folds):
    install_synthetic_runner_mocks(monkeypatch, tmp_path, prepared_folds)
    writes = []
    real = ArtifactWriter.write_json
    def write(self, name, value):
        writes.append(name)
        if name == "run_manifest.json":
            assert not (self.directory / "run.log.tmp").exists()
            assert integrity.verify_scientific(self.directory)["status"] == "passed"
            assert value["metadata_hash"] == file_hash(self.directory / "run_metadata.json")
        return real(self, name, value)
    monkeypatch.setattr(ArtifactWriter, "write_json", write)
    approved = authorization(supplied_scope=scope(primary=(), supportive=("ridge",), horizons=(1,), baselines=()))
    directory = orchestration.run_validation(panel(), run_id=approved.run_id, authorization=approved)
    assert writes[-1] == "run_manifest.json"
    writer = object.__new__(ArtifactWriter)
    writer.directory = directory
    with pytest.raises(FileExistsError):
        writer.write_json("run_metadata.json", {})


def test_full_plan_counts_are_declarations_not_execution():
    assert integrity.plan_counts(scope()) == {"primary_fits": 1152, "supportive_fits": 32,
        "baseline_evaluations": 32, "total_evaluations": 1216, "configuration_summaries": 304}


@pytest.mark.parametrize("mutation", ["missing_prediction", "duplicate_prediction", "wrong_target", "wrong_fold"])
def test_prediction_semantic_corruption_is_rejected(complete_bundle, mutation):
    import csv
    path = complete_bundle / "predictions.csv"
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        columns, rows = reader.fieldnames, list(reader)
    if mutation == "missing_prediction":
        rows.pop()
    elif mutation == "duplicate_prediction":
        rows[-1] = rows[0].copy()
    elif mutation == "wrong_target":
        rows[0]["observed_target"] = "999999"
    else:
        rows[0]["fold_id"] = "99"
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(integrity.IntegrityError):
        integrity.verify_scientific(complete_bundle)


def test_changed_source_at_finalization_blocks_manifest(tmp_path, monkeypatch, prepared_folds):
    install_synthetic_runner_mocks(monkeypatch, tmp_path, prepared_folds)
    approved = authorization(supplied_scope=scope(primary=(), supportive=("ridge",), horizons=(1,), baselines=()))
    real = type(approved).validate
    calls = []
    def validate(self, root, run_id):
        calls.append(run_id)
        if len(calls) == 2:
            from src.forecasting.authorization import ExecutionBlocked
            raise ExecutionBlocked("Controlled changed source at finalization.")
        return real(self, root, run_id)
    monkeypatch.setattr(type(approved), "validate", validate)
    with pytest.raises(PermissionError, match="changed source"):
        orchestration.run_validation(panel(), run_id=approved.run_id, authorization=approved)
    directory = RepositoryLayout(tmp_path).run_directory(approved.run_id)
    assert not (directory / "run_manifest.json").exists()
    assert json.loads((directory / "run_metadata.json").read_text())["run_status"] == "failed"


def test_csv_parser_error_is_wrapped_as_integrity_error(complete_bundle):
    path = complete_bundle / "fold_metrics.csv"
    with path.open("a", encoding="utf-8") as stream:
        stream.write("x" * (csv.field_size_limit() + 1) + "\n")
    with pytest.raises(integrity.IntegrityError, match="Missing, corrupt or inconsistent") as caught:
        integrity.verify_scientific(complete_bundle)
    assert isinstance(caught.value.__cause__, csv.Error)


@pytest.mark.parametrize("error", [
    integrity.UnpicklingError("invalid pickle"), EOFError("truncated model"),
    integrity.XGBoostError("invalid model"), integrity.LightGBMError("invalid model"),
    integrity.CatBoostError("invalid model"),
])
def test_expected_model_load_error_is_wrapped_with_original_cause(complete_bundle, monkeypatch, error):
    def fail(*args, **kwargs):
        raise error
    monkeypatch.setattr(model_artifacts, "_load_estimator", fail)
    with pytest.raises(integrity.IntegrityError, match="could not be loaded or replayed") as caught:
        integrity.verify_scientific(complete_bundle)
    assert caught.value.__cause__ is error


@pytest.mark.parametrize("error", [integrity.XGBoostError("replay failed"),
    integrity.LightGBMError("replay failed"), integrity.CatBoostError("replay failed")])
def test_expected_native_prediction_error_is_wrapped(complete_bundle, monkeypatch, error):
    class FailingModel:
        def predict(self, *args, **kwargs):
            raise error
    monkeypatch.setattr(model_artifacts, "_load_estimator", lambda *args: FailingModel())
    with pytest.raises(integrity.IntegrityError, match="could not be loaded or replayed") as caught:
        integrity.verify_scientific(complete_bundle)
    assert caught.value.__cause__ is error


def test_preprocessor_restore_error_keeps_original_cause(complete_bundle, monkeypatch):
    original = ValueError("invalid persisted preprocessing state")
    def fail(*args, **kwargs):
        raise original
    monkeypatch.setattr(model_artifacts, "restore_preprocessor", fail)
    with pytest.raises(integrity.IntegrityError) as caught:
        integrity.verify_scientific(complete_bundle)
    assert caught.value.__cause__ is original


@pytest.mark.parametrize("error", [RuntimeError("programming failure"), AssertionError("programming failure")])
def test_unexpected_replay_programming_error_is_not_hidden(complete_bundle, monkeypatch, error):
    def fail(*args, **kwargs):
        raise error
    monkeypatch.setattr(model_artifacts, "_load_estimator", fail)
    with pytest.raises(type(error)) as caught:
        integrity.verify_scientific(complete_bundle)
    assert caught.value is error


def storage_directories(directory):
    layout = RepositoryLayout.from_artifact_directory(directory)
    return {"artifacts": layout.run_directory(directory.name),
            "models": layout.model_run_directory(directory.name),
            "reports": layout.draft_report_directory(directory.name)}


@pytest.mark.parametrize("kind", ["model", "descriptor", "preprocessor", "origin_features"])
def test_corrupt_model_evidence_rejected_across_owners(complete_bundle, monkeypatch, kind):
    metadata = json.loads((complete_bundle / "run_metadata.json").read_text())
    path = model_artifacts.safe_path(complete_bundle, metadata["model_artifacts"][0][f"{kind}_path"])
    path.write_bytes(path.read_bytes() + b"corrupt")
    loader = Mock(side_effect=AssertionError("Corrupt model evidence cannot be loaded"))
    monkeypatch.setattr(model_artifacts, "_load_estimator", loader)
    with pytest.raises(integrity.IntegrityError):
        integrity.verify_completed(complete_bundle)
    with pytest.raises(integrity.IntegrityError):
        integrity.verify_scientific(complete_bundle)
    loader.assert_not_called()


@pytest.mark.parametrize("owner,extra", [
    (owner, extra) for owner in ("artifacts", "models", "reports")
    for extra in ("extra.json", "unfinished.tmp", "model.tmp.joblib", "empty-directory", "run_manifest.json")
    if (owner, extra) != ("artifacts", "run_manifest.json")
])
def test_extra_and_unfinished_evidence_blocks_completion_and_manifest_build(complete_bundle, owner, extra):
    root = storage_directories(complete_bundle)[owner]
    path = root / extra
    if extra == "empty-directory":
        path.mkdir()
    else:
        path.write_text("unexpected run-owned evidence")
    with pytest.raises(integrity.IntegrityError):
        integrity.verify_completed(complete_bundle)
    manifest_path = complete_bundle / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    metadata = json.loads((complete_bundle / "run_metadata.json").read_text())
    manifest_path.unlink()
    with pytest.raises(integrity.IntegrityError):
        integrity.build_manifest(complete_bundle, metadata, manifest["integrity_result"])
    assert path.exists() and not manifest_path.exists()


@pytest.mark.parametrize("owner", ["artifacts", "models", "reports"])
def test_cross_run_manifest_reference_rejected_with_matching_bytes_and_hash(complete_bundle, owner):
    layout = RepositoryLayout.from_artifact_directory(complete_bundle)
    path = complete_bundle / "run_manifest.json"
    manifest = json.loads(path.read_text())
    entry = next(record for record in manifest["artifacts"] if record["owner"] == owner)
    original = layout.root / entry["path"]
    entry["path"] = entry["path"].replace(f"/{complete_bundle.name}/", "/other-run/")
    other = layout.root / entry["path"]
    other.parent.mkdir(parents=True, exist_ok=True)
    other.write_bytes(original.read_bytes())
    assert file_hash(other) == entry["sha256"]
    path.write_text(json.dumps(manifest))
    with pytest.raises(integrity.IntegrityError, match="declared run owner"):
        integrity.verify_completed(complete_bundle)


@pytest.mark.parametrize("mutation", ["wrong_owner", "unknown_owner", "legacy_path", "missing_entry", "duplicate_entry", "version_1"])
def test_invalid_completion_manifest_contract_is_rejected(complete_bundle, mutation):
    path = complete_bundle / "run_manifest.json"
    manifest = json.loads(path.read_text())
    entry = manifest["artifacts"][0]
    if mutation == "wrong_owner":
        entry["owner"] = "models"
    elif mutation == "unknown_owner":
        entry["owner"] = "data"
    elif mutation == "legacy_path":
        entry["path"] = "run_metadata.json"
    elif mutation == "missing_entry":
        manifest["artifacts"].pop()
    elif mutation == "duplicate_entry":
        manifest["artifacts"].append(entry.copy())
    else:
        manifest["manifest_version"] = 1
    path.write_text(json.dumps(manifest))
    with pytest.raises(integrity.IntegrityError):
        integrity.verify_completed(complete_bundle)


@pytest.mark.parametrize("kind", ["model", "descriptor", "preprocessor", "origin_features"])
@pytest.mark.parametrize("destination", ["other_run", "wrong_owner", "wrong_fold"])
def test_model_reference_requires_exact_run_owner_and_candidate_fold(complete_bundle, monkeypatch, kind, destination):
    path = complete_bundle / "run_metadata.json"
    metadata = json.loads(path.read_text())
    record = metadata["model_artifacts"][0]
    if destination == "other_run":
        record[f"{kind}_path"] = record[f"{kind}_path"].replace(f"/{complete_bundle.name}/", "/other-run/")
    elif destination == "wrong_owner":
        record[f"{kind}_path"] = (complete_bundle / Path(record[f"{kind}_path"]).name).relative_to(
            RepositoryLayout.from_artifact_directory(complete_bundle).root).as_posix()
    else:
        record[f"{kind}_path"] = record[f"{kind}_path"].replace("fold-1/", "fold-2/")
    path.write_text(json.dumps(metadata))
    loader = Mock(side_effect=AssertionError("Misowned model evidence cannot be loaded"))
    monkeypatch.setattr(model_artifacts, "_load_estimator", loader)
    with pytest.raises(integrity.IntegrityError):
        integrity.verify_scientific(complete_bundle)
    loader.assert_not_called()


@pytest.mark.parametrize("owner", ["artifacts", "models", "reports", "manifest"])
def test_symlinked_evidence_rejected_even_with_identical_bytes(complete_bundle, owner):
    layout = RepositoryLayout.from_artifact_directory(complete_bundle)
    if owner == "manifest":
        path = complete_bundle / "run_manifest.json"
    else:
        manifest = json.loads((complete_bundle / "run_manifest.json").read_text())
        entry = next(record for record in manifest["artifacts"] if record["owner"] == owner)
        path = layout.root / entry["path"]
    external = layout.root / "unowned-evidence"
    external.write_bytes(path.read_bytes())
    path.unlink()
    path.symlink_to(external)
    with pytest.raises(integrity.IntegrityError):
        integrity.verify_completed(complete_bundle)


@pytest.mark.parametrize("owner", ["artifacts", "models", "reports"])
@pytest.mark.parametrize("condition", ["symlink", "non_directory"])
def test_invalid_run_storage_ancestor_rejected(complete_bundle, owner, condition):
    root = storage_directories(complete_bundle)[owner]
    retained = root.parent / "retained-run"
    root.rename(retained)
    if condition == "symlink":
        root.symlink_to(retained, target_is_directory=True)
    else:
        root.write_text("not a directory")
    with pytest.raises(integrity.IntegrityError):
        integrity.verify_completed(complete_bundle)
    assert retained.is_dir()


@pytest.mark.parametrize("owner", ["models", "reports"])
def test_only_artifact_anchor_manifest_can_establish_completion(complete_bundle, owner):
    root = storage_directories(complete_bundle)[owner]
    manifest_path = complete_bundle / "run_manifest.json"
    (root / "run_manifest.json").write_bytes(manifest_path.read_bytes())
    manifest_path.unlink()
    with pytest.raises(integrity.IntegrityError):
        integrity.verify_completed(complete_bundle)
    with pytest.raises(integrity.IntegrityError):
        reporting.comparison_text(complete_bundle)


@pytest.mark.parametrize("record", ["metadata", "manifest"])
def test_completion_identity_must_match_artifact_anchor(complete_bundle, record):
    manifest_path = complete_bundle / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if record == "metadata":
        path = complete_bundle / "run_metadata.json"
        metadata = json.loads(path.read_text())
        metadata["run_id"] = "other-run"
        path.write_text(json.dumps(metadata))
        manifest["metadata_hash"] = file_hash(path)
        with pytest.raises(integrity.IntegrityError, match="Run identity"):
            integrity.verify_scientific(complete_bundle)
    else:
        manifest["run_id"] = "other-run"
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(integrity.IntegrityError):
        integrity.verify_completed(complete_bundle)


def test_published_manifest_cannot_be_rebuilt(complete_bundle):
    metadata = json.loads((complete_bundle / "run_metadata.json").read_text())
    manifest = json.loads((complete_bundle / "run_manifest.json").read_text())
    with pytest.raises(integrity.IntegrityError, match="cannot be rebuilt"):
        integrity.build_manifest(complete_bundle, metadata, manifest["integrity_result"])


def test_artifact_receipt_cannot_redirect_draft_report(complete_bundle):
    path = complete_bundle / "run_metadata.json"
    metadata = json.loads(path.read_text())
    entry = next(row for row in metadata["artifact_manifest"] if row["artifact_path"].endswith("/comparison.md"))
    entry["artifact_path"] = entry["artifact_path"].replace(f"/{complete_bundle.name}/", "/other-run/")
    path.write_text(json.dumps(metadata))
    with pytest.raises(integrity.IntegrityError, match="Artifact receipts"):
        integrity.verify_scientific(complete_bundle)
