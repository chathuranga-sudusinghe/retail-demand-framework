"""Fault injection against complete synthetic mocked bundles; no research runs."""
import csv
import json
import pytest
from src.forecasting import experiment, integrity, model_artifacts, reporting
from src.forecasting.artifacts import ArtifactWriter, file_hash
from test_forecasting_experiment import (authorization, install_synthetic_runner_mocks,
                                         panel, scope)
from test_forecasting_experiment import prepared_folds as _prepared_folds


@pytest.fixture
def prepared_folds():
    return _prepared_folds.__wrapped__()


@pytest.fixture
def complete_bundle(tmp_path, monkeypatch, prepared_folds):
    install_synthetic_runner_mocks(monkeypatch, tmp_path, prepared_folds)
    approved = authorization(supplied_scope=scope(primary=(), supportive=("ridge",), horizons=(1,)))
    return experiment.run_validation(panel(), run_id=approved.run_id, authorization=approved)


def test_completed_bundle_manifest_counts_hashes_and_readonly_reporting(complete_bundle):
    result = integrity.verify_completed(complete_bundle)
    assert result == {"status": "passed", "evaluations": 12, "predictions": 24,
                      "configuration_summaries": 3, "models_replayed": 4}
    manifest = json.loads((complete_bundle / "run_manifest.json").read_text())
    assert manifest["metadata_hash"] == file_hash(complete_bundle / "run_metadata.json")
    before = {p: p.read_bytes() for p in complete_bundle.rglob("*") if p.is_file()}
    assert "pending human review" in reporting.comparison_text(complete_bundle)
    assert before == {p: p.read_bytes() for p in before}


@pytest.mark.parametrize("name", ["run_manifest.json", "predictions.csv", "fold_metrics.csv", "comparison.md", "run.log", "authorization.json"])
def test_missing_artifact_rejected(complete_bundle, name):
    (complete_bundle / name).unlink()
    with pytest.raises(integrity.IntegrityError):
        integrity.verify_completed(complete_bundle)
    with pytest.raises(integrity.IntegrityError):
        reporting.comparison_text(complete_bundle)


@pytest.mark.parametrize("name", ["run_metadata.json", "fold_metrics.csv", "predictions.csv", "run.log"])
def test_corrupt_artifact_rejected(complete_bundle, name):
    path = complete_bundle / name
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


def test_missing_model_descriptor_rejected(complete_bundle):
    metadata = json.loads((complete_bundle / "run_metadata.json").read_text())
    (complete_bundle / metadata["model_artifacts"][0]["descriptor_path"]).unlink()
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


@pytest.mark.parametrize("point", ["startup", "report", "manifest", "model", "interrupt", "verification"])
def test_failure_never_publishes_completion_and_preserves_original(tmp_path, monkeypatch, prepared_folds, point):
    install_synthetic_runner_mocks(monkeypatch, tmp_path, prepared_folds)
    approved = authorization(supplied_scope=scope(primary=(), supportive=("ridge",), horizons=(1,), baselines=()))
    original = KeyboardInterrupt("controlled interrupt") if point == "interrupt" else OSError("controlled original")
    def fail(*args, **kwargs):
        raise original
    if point == "report":
        monkeypatch.setattr(ArtifactWriter, "write_comparison", fail)
    elif point == "model":
        monkeypatch.setattr(model_artifacts, "_save_estimator", fail)
    elif point == "interrupt":
        monkeypatch.setattr(experiment, "fit_estimator", fail)
    elif point == "verification":
        monkeypatch.setattr(experiment, "verify_scientific", fail)
    else:
        real = ArtifactWriter.write_json
        def write(self, name, value):
            if (point == "startup" and name == "run_metadata.json") or (point == "manifest" and name == "run_manifest.json"):
                raise original
            return real(self, name, value)
        monkeypatch.setattr(ArtifactWriter, "write_json", write)
    with pytest.raises(type(original)) as caught:
        experiment.run_validation(panel(), run_id=approved.run_id, authorization=approved)
    assert caught.value is original
    directory = tmp_path / "outputs/revised-forecasting" / approved.run_id
    assert not (directory / "run_manifest.json").exists()
    with pytest.raises(integrity.IntegrityError):
        integrity.verify_completed(directory)
    if point != "startup":
        metadata = json.loads((directory / "run_metadata.json").read_text())
        assert metadata["run_status"] == ("interrupted" if point == "interrupt" else "failed")
        assert metadata["selection_records"] == [] and metadata["completed_at_utc"] is None
        if point == "model":
            assert metadata["completed_counts"]["supportive_fits"] == 1


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
    directory = experiment.run_validation(panel(), run_id=approved.run_id, authorization=approved)
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
            from src.forecasting.execution import ExecutionBlocked
            raise ExecutionBlocked("Controlled changed source at finalization.")
        return real(self, root, run_id)
    monkeypatch.setattr(type(approved), "validate", validate)
    with pytest.raises(PermissionError, match="changed source"):
        experiment.run_validation(panel(), run_id=approved.run_id, authorization=approved)
    directory = tmp_path / "outputs/revised-forecasting" / approved.run_id
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
