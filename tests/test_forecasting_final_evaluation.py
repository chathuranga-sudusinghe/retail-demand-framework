"""Synthetic final preparation/orchestration/artifact tests; no project outcomes."""
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest

from src.forecasting import final_artifacts as artifacts, final_evaluation as final
from src.forecasting.artifacts import file_hash, json_text
from src.forecasting.authorization import ExecutionBlocked
from src.forecasting.evaluation import PreflightError
from src.forecasting.final_authorization import TRAINING_END, read_json
from src.forecasting.models import estimator_parameters
from test_forecasting_final_authorization import final_context as _final_context, historical_panel


@pytest.fixture
def final_context(tmp_path, monkeypatch):
    return _final_context.__wrapped__(tmp_path, monkeypatch)


class SyntheticEstimator:
    def __init__(self, value=0.0):
        self.value = value

    def predict(self, matrix, **kwargs):
        return np.full(len(matrix), self.value)


def synthetic_outcomes():
    return pd.DataFrame([
        {"SKU_ID": sku, "Warehouse_ID": warehouse, "Date": day, "Units_Sold": base + offset % 3}
        for sku, warehouse, base in (("A", "W1", 4), ("B", "W2", 10))
        for offset, day in enumerate(pd.date_range("2024-12-03", "2024-12-30"))
    ])


@pytest.fixture
def synthetic_runner(final_context, monkeypatch):
    fixture = final_context
    layout = fixture["layout"]
    events, constructed, fits = [], [], []

    def read_projection(**kwargs):
        assert kwargs["expected_provenance_sha256"] == fixture["payload"]["validated_provenance_hash"]
        assert tuple(kwargs["columns"]) == final.PROJECTION_COLUMNS
        if kwargs["start"] == "2024-01-01" and kwargs["end"] == TRAINING_END:
            events.append("historical_read")
            data = historical_panel()
        else:
            assert kwargs["start"] == "2024-12-03" and kwargs["end"] == "2024-12-30"
            directory = layout.run_directory("synthetic-final")
            receipt = read_json(directory / "run_metadata.json")["prediction_receipt_hash"]
            assert len(artifacts.verify_sealed_predictions(directory, receipt)) == 56
            assert len(fits) == 20
            events.append("synthetic_outcome_read")
            data = synthetic_outcomes()
        return SimpleNamespace(frame=data)

    def construct(model, configuration):
        estimator = SyntheticEstimator()
        constructed.append(estimator)
        events.append("construct")
        return estimator

    def fit(estimator, model, configuration, matrix, labels):
        assert len(matrix) == len(labels) and np.isfinite(matrix).all() and np.isfinite(labels).all()
        fits.append((model, configuration, matrix.copy(), labels.copy()))
        estimator.value = float(np.mean(labels))
        events.append("fit")
        params = estimator_parameters(model, configuration)
        iterations = configuration.boosting_iterations if configuration else (300 if model == "random_forest" else None)
        # Deliberately mutate passed arrays; later candidates must use intact populations.
        matrix[:] = -999
        labels[:] = -999
        return {"requested_api_parameters": params, "effective_api_parameters": params,
                "requested_iterations": iterations, "effective_iterations": iterations}

    def save(estimator, model, path):
        assert len(fits) == 20  # All fresh fits precede prediction persistence.
        path.write_text(json_text({"synthetic_value": estimator.value}))
        events.append("persist_model")

    def load(model, path):
        events.append("replay")
        return SyntheticEstimator(read_json(path)["synthetic_value"])

    monkeypatch.setattr(final, "read_validated_projection", read_projection)
    monkeypatch.setattr(final, "require_native_roster", lambda data: None)
    monkeypatch.setattr(final, "environment_metadata", lambda root: {
        "source_hashes": fixture["payload"]["source_hashes"],
        "library_versions": fixture["payload"]["library_versions"], "git_commit_sha": "synthetic",
    })
    monkeypatch.setattr(final, "construct_estimator", construct)
    monkeypatch.setattr(final, "fit_estimator", fit)
    monkeypatch.setattr(artifacts, "_save_estimator", save)
    monkeypatch.setattr(artifacts, "_load_estimator", load)
    fixture.update(events=events, constructed=constructed, fits=fits)
    return fixture


def test_final_preprocessing_uses_identical_eligible_labelled_populations():
    prepared = final.prepare_final_training(historical_panel())
    counts = {1: 309, 7: 303, 14: 296, 28: 282}
    last = {1: "2024-12-02", 7: "2024-11-26", 14: "2024-11-19", 28: "2024-11-05"}
    assert prepared.origin.Date.eq(pd.Timestamp("2024-12-03")).all()
    for h, population in prepared.populations.items():
        assert len(population.features) == 2 * counts[h] == len(population.labels)
        assert population.features.Date.min() == pd.Timestamp("2024-01-29")
        assert population.features.Date.max() == pd.Timestamp(last[h])
        assert (population.features.Date + pd.Timedelta(days=h - 1)).le(TRAINING_END).all()
        assert all(s.training_row_count == len(population.labels) for s in population.preprocessors.values())
        primary = [population.preprocessors[m] for m in ("xgboost", "lightgbm", "catboost")]
        assert all(s.vocabularies == primary[0].vocabularies for s in primary)
        ridge = population.preprocessors["ridge"]
        numerical = ridge.transform(population.features).loc[:, list(ridge.numerical_feature_names)]
        np.testing.assert_allclose(numerical.mean(axis=0), 0, atol=1e-12)
        original = population.features.loc[:, list(ridge.numerical_feature_names)].to_numpy(dtype=float)
        np.testing.assert_array_equal(ridge.numerical_means, original.mean(axis=0))
        scales = np.where(original.std(axis=0) == 0, 1, original.std(axis=0))
        np.testing.assert_array_equal(ridge.numerical_scales, scales)
    baseline = prepared.baseline_evidence
    history = historical_panel()
    for row in baseline.itertuples(index=False):
        week = history.loc[history.SKU_ID.eq(row.SKU_ID) & history.Date.between("2024-11-26", TRAINING_END)]
        assert row.week_sum == week.Units_Sold.sum()


def test_missing_historical_labels_are_excluded_before_vocabulary_and_scaler_fit():
    data = historical_panel()
    data.loc[data.SKU_ID.eq("A") & data.Date.eq("2024-01-30"), "Units_Sold"] = np.nan
    prepared = final.prepare_final_training(data)
    population = prepared.populations[7]
    assert not (population.features.SKU_ID.eq("A") & population.features.Date.eq("2024-01-29")).any()
    assert all(s.training_row_count == len(population.labels) for s in population.preprocessors.values())
    diagnostic = prepared.eligibility[1]["per_pair"][0]
    assert diagnostic["exclusion_counts"]["missing_observed_training_target"] > 0


def test_future_synthetic_demand_is_rejected_before_quantity_validation():
    data = historical_panel()
    extra = pd.DataFrame([{"SKU_ID": "A", "Warehouse_ID": "W1", "Date": pd.Timestamp("2024-12-03"),
                           "Units_Sold": "must never be parsed"}])
    with pytest.raises(ExecutionBlocked, match="historical training"):
        final.prepare_final_training(pd.concat([data, extra], ignore_index=True))


def test_incomplete_origin_history_stops_preparation():
    data = historical_panel()
    data.loc[data.Date.eq(TRAINING_END), "Units_Sold"] = np.nan
    with pytest.raises((PreflightError, ValueError)):
        final.prepare_final_training(data)


def test_missing_authorization_blocks_before_any_input_or_estimator_access(tmp_path, monkeypatch):
    reader, constructor = Mock(), Mock()
    monkeypatch.setattr(final, "read_validated_projection", reader)
    monkeypatch.setattr(final, "construct_estimator", constructor)
    with pytest.raises(ExecutionBlocked):
        final.run_final_evaluation(final.RepositoryLayout(tmp_path))
    reader.assert_not_called()
    constructor.assert_not_called()


def test_full_synthetic_final_sequence_seals_before_reveal_and_publishes_manifest_last(synthetic_runner, monkeypatch):
    fixture = synthetic_runner
    writes = []
    original_write = artifacts.FinalArtifactWriter.write_text

    def write(self, name, text):
        writes.append(name)
        return original_write(self, name, text)

    monkeypatch.setattr(artifacts.FinalArtifactWriter, "write_text", write)
    directory = final.run_final_evaluation(fixture["layout"])
    assert writes[-1] == "run_manifest.json"
    assert len(fixture["constructed"]) == len({id(e) for e in fixture["constructed"]}) == 20
    assert len(fixture["fits"]) == 20
    assert fixture["events"].count("synthetic_outcome_read") == 1
    reveal = fixture["events"].index("synthetic_outcome_read")
    assert fixture["events"][:reveal].count("persist_model") == 20
    assert fixture["events"][:reveal].count("fit") == 20
    assert fixture["events"][reveal:].count("fit") == 0
    result = artifacts.verify_final_completed(directory)
    assert result == {"status": "passed", "evaluations": 28, "learned_refits": 20,
                      "baseline_evaluations": 8, "predictions": 56, "models_replayed": 20}
    predictions = read_json(directory / "predictions.json")
    assert all("observed_target" not in r and "fold_id" not in r and "wape" not in r for r in predictions)
    assert len(read_json(directory / "observations.json")) == 8
    assert len(read_json(directory / "metrics.json")) == 28
    assert read_json(directory / "run_metadata.json")["producer_mapping"] == fixture["payload"]["producer_mapping"]
    assert all(r["candidate_status"] == "completed" for r in read_json(directory / "candidates.json"))
    assert "Seasonal Naive outperformed" in (fixture["layout"].draft_report_directory(directory.name) / "comparison.md").read_text()
    files = [fixture["layout"].root / r["path"] for r in read_json(directory / "run_manifest.json")["files"]]
    before = {p: p.read_bytes() for p in [*files, directory / "run_manifest.json"]}
    artifacts.verify_final_completed(directory)
    assert before == {p: p.read_bytes() for p in before}


@pytest.mark.parametrize("name", [
    "predictions.json", "prediction_receipt.json", "authorization.json", "freeze.md",
    "candidates.json", "eligibility.json", "baseline_history.json", "observations.json", "metrics.json",
    "run_metadata.json", "run.log",
])
def test_completed_final_artifact_tampering_is_rejected(synthetic_runner, name):
    directory = final.run_final_evaluation(synthetic_runner["layout"])
    with (directory / name).open("a") as stream:
        stream.write(" ")
    with pytest.raises(artifacts.FinalIntegrityError):
        artifacts.verify_final_completed(directory)


@pytest.mark.parametrize("name", ["model", "descriptor", "preprocessor", "origin_features"])
def test_final_model_dependency_tampering_is_rejected(synthetic_runner, name):
    directory = final.run_final_evaluation(synthetic_runner["layout"])
    record = read_json(directory / "candidates.json")[0]["model_artifact"]
    path = synthetic_runner["layout"].root / record[name + "_path"]
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(artifacts.FinalIntegrityError):
        artifacts.verify_final_completed(directory)


def test_final_replay_mismatch_is_rejected(synthetic_runner, monkeypatch):
    directory = final.run_final_evaluation(synthetic_runner["layout"])
    monkeypatch.setattr(artifacts, "_load_estimator", lambda model, path: SyntheticEstimator(-999))
    with pytest.raises(artifacts.FinalIntegrityError, match="replay"):
        artifacts.verify_final_completed(directory)


@pytest.mark.parametrize("owner", ["artifacts", "models", "reports"])
def test_extra_run_owned_files_and_post_completion_writes_are_rejected(synthetic_runner, owner):
    fixture = synthetic_runner
    directory = final.run_final_evaluation(fixture["layout"])
    roots = {"artifacts": directory, "models": fixture["layout"].model_run_directory(directory.name),
             "reports": fixture["layout"].draft_report_directory(directory.name)}
    (roots[owner] / "unexpected.tmp").write_text("synthetic")
    with pytest.raises(artifacts.FinalIntegrityError):
        artifacts.verify_final_completed(directory)
    writer = object.__new__(artifacts.FinalArtifactWriter)
    writer.layout, writer.directory = fixture["layout"], directory
    with pytest.raises(FileExistsError):
        writer.write_json("run_metadata.json", {})


@pytest.mark.parametrize("name", ["predictions.json", "prediction_receipt.json"])
def test_prediction_tampering_before_reveal_blocks_outcome_reader(synthetic_runner, monkeypatch, name):
    original = artifacts.FinalArtifactWriter.seal

    def tamper(self, *args):
        digest = original(self, *args)
        path = self.path(name)
        if name == "predictions.json":
            rows = read_json(path)
            rows[0]["prediction"] += 1
            path.write_text(json_text(rows))
        else:
            path.write_bytes(path.read_bytes() + b" ")
        return digest

    monkeypatch.setattr(artifacts.FinalArtifactWriter, "seal", tamper)
    with pytest.raises(artifacts.FinalIntegrityError):
        final.run_final_evaluation(synthetic_runner["layout"])
    assert "synthetic_outcome_read" not in synthetic_runner["events"]
    assert not synthetic_runner["layout"].run_directory("synthetic-final").joinpath("run_manifest.json").exists()


@pytest.mark.parametrize("point", ["fit", "prediction", "serialization", "seal", "outcomes", "scoring", "replay"])
def test_failure_stops_once_preserves_diagnostics_and_never_completes(synthetic_runner, monkeypatch, point):
    fixture = synthetic_runner
    error = ValueError("Synthetic controlled final failure")

    def fail(*args, **kwargs):
        raise error

    if point == "fit":
        monkeypatch.setattr(final, "fit_estimator", fail)
    elif point == "prediction":
        monkeypatch.setattr(SyntheticEstimator, "predict", fail)
    elif point == "serialization":
        monkeypatch.setattr(artifacts, "_save_estimator", fail)
    elif point == "seal":
        monkeypatch.setattr(artifacts.FinalArtifactWriter, "seal", fail)
    elif point == "outcomes":
        monkeypatch.setattr(final, "read_reserved_outcomes", fail)
    elif point == "scoring":
        monkeypatch.setattr(final, "forecasting_metrics", fail)
    elif point == "replay":
        monkeypatch.setattr(artifacts, "_load_estimator", fail)
    with pytest.raises(ValueError) as caught:
        final.run_final_evaluation(fixture["layout"])
    assert caught.value is error or caught.value.__cause__ is error
    directory = fixture["layout"].run_directory("synthetic-final")
    assert read_json(directory / "run_metadata.json")["run_status"] == "failed"
    assert read_json(directory / "diagnostics.json")["exception_type"] == type(caught.value).__name__
    assert not (directory / "run_manifest.json").exists()
    if point in ("fit", "prediction", "serialization", "seal", "outcomes"):
        assert "synthetic_outcome_read" not in fixture["events"]
    assert len(fixture["constructed"]) == (1 if point == "fit" else 20)
    with pytest.raises(artifacts.FinalIntegrityError):
        artifacts.verify_final_completed(directory)


def test_secondary_diagnostic_failure_preserves_original_error(synthetic_runner, monkeypatch):
    error = ValueError("Synthetic primary failure")
    original = artifacts.FinalArtifactWriter.write_json

    def write(self, name, value):
        if name == "diagnostics.json":
            raise OSError("Synthetic diagnostics failure")
        return original(self, name, value)

    def fit(*args, **kwargs):
        raise error

    monkeypatch.setattr(artifacts.FinalArtifactWriter, "write_json", write)
    monkeypatch.setattr(final, "fit_estimator", fit)
    with pytest.raises(ValueError) as caught:
        final.run_final_evaluation(synthetic_runner["layout"])
    assert caught.value is error
    assert any("OSError" in note for note in error.__notes__)


def test_receipt_cannot_be_rewritten_and_manifest_hashes_include_every_owner(synthetic_runner):
    directory = final.run_final_evaluation(synthetic_runner["layout"])
    manifest = read_json(directory / "run_manifest.json")
    assert {r["owner"] for r in manifest["files"]} == {"artifacts", "models", "reports"}
    assert all(file_hash(synthetic_runner["layout"].root / r["path"]) == r["sha256"] for r in manifest["files"])
    assert all(r["path"] != str(directory / "run_manifest.json") for r in manifest["files"])


def test_prediction_receipt_is_write_once_before_outcome_access(synthetic_runner, monkeypatch):
    original = artifacts.FinalArtifactWriter.seal

    def seal(self, *args):
        digest = original(self, *args)
        with pytest.raises(artifacts.FinalIntegrityError, match="cannot be rewritten"):
            self.write_json("prediction_receipt.json", {})
        with pytest.raises(artifacts.FinalIntegrityError, match="cannot be rewritten"):
            self.write_json("predictions.json", [])
        return digest

    monkeypatch.setattr(artifacts.FinalArtifactWriter, "seal", seal)
    directory = final.run_final_evaluation(synthetic_runner["layout"])
    assert artifacts.verify_final_completed(directory)["evaluations"] == 28


def test_reconciled_metrics_cannot_change_without_prediction_changes(synthetic_runner):
    directory = final.run_final_evaluation(synthetic_runner["layout"])
    path = directory / "metrics.json"
    rows = read_json(path)
    rows[0]["mae"] += 1
    path.write_text(json_text(rows))
    with pytest.raises(artifacts.FinalIntegrityError, match="metrics differ"):
        artifacts.verify_final_scientific(directory)
