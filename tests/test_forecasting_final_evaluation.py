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
            directory = layout.run_directory(fixture["payload"]["run_id"])
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


class LayoutCheckedEstimator(SyntheticEstimator):
    """Exercise each prediction API; Ridge uses real linear algebra without fit."""

    def __init__(self, model, calls, phase, value=0.0):
        super().__init__(value)
        self.model, self.calls, self.phase = model, calls, phase

    def predict(self, matrix, **kwargs):
        assert matrix.flags.c_contiguous
        assert matrix.dtype == np.float64
        expected = ({"num_threads": 1} if self.model == "lightgbm" else
                    {"thread_count": 1} if self.model == "catboost" else {})
        assert kwargs == (expected if self.phase == "replay" else {})
        self.calls.append((self.model, self.phase))
        if self.model == "ridge":
            from sklearn.linear_model import Ridge

            # Set synthetic persisted coefficients directly: never call fit.
            ridge = Ridge()
            ridge.coef_ = np.linspace(-0.3, 0.3, matrix.shape[1])
            ridge.intercept_ = self.value
            ridge.n_features_in_ = matrix.shape[1]
            return ridge.predict(matrix)
        return super().predict(matrix, **kwargs)


def test_final_original_and_replay_use_c_order_for_all_learned_models(synthetic_runner, monkeypatch):
    from sklearn.linear_model import Ridge
    from src.forecasting.preprocessing import ForecastPreprocessor

    calls, transformed_layouts = [], []
    transform = ForecastPreprocessor.transform

    def fortran_transform(self, features):
        frame = transform(self, features)
        matrix = np.asfortranarray(frame.to_numpy(dtype=float))
        result = pd.DataFrame(matrix, columns=frame.columns, index=frame.index, copy=False)
        pd.testing.assert_frame_equal(result, frame)
        assert result.to_numpy(dtype=float).flags.f_contiguous
        assert not result.to_numpy(dtype=float).flags.c_contiguous
        transformed_layouts.append(self.model)
        return result

    monkeypatch.setattr(ForecastPreprocessor, "transform", fortran_transform)
    monkeypatch.setattr(Ridge, "fit", Mock(side_effect=AssertionError("No real model fitting")))
    monkeypatch.setattr(final, "construct_estimator", lambda model, configuration:
                        LayoutCheckedEstimator(model, calls, "original"))
    monkeypatch.setattr(artifacts, "_load_estimator", lambda model, path:
                        LayoutCheckedEstimator(model, calls, "replay", read_json(path)["synthetic_value"]))
    directory = final.run_final_evaluation(synthetic_runner["layout"])
    assert artifacts.verify_final_completed(directory)["models_replayed"] == 20
    for model in ("xgboost", "lightgbm", "catboost", "ridge", "random_forest"):
        assert model in transformed_layouts
        assert calls.count((model, "original")) == 4
        assert calls.count((model, "replay")) == 8


def failed_bundle_files(fixture):
    layout, directory = fixture["layout"], fixture["directory"]
    roots = (directory, layout.model_run_directory(directory.name), layout.draft_report_directory(directory.name))
    return sorted(p for folder in roots for p in folder.rglob("*") if p.is_file())


def failed_bundle_hashes(fixture):
    root = fixture["layout"].root
    return {p.relative_to(root).as_posix(): file_hash(p) for p in failed_bundle_files(fixture)}


@pytest.fixture
def failed_final_bundle(synthetic_runner, monkeypatch):
    fixture = synthetic_runner
    load = artifacts._load_estimator
    with monkeypatch.context() as scoped:
        scoped.setattr(artifacts, "_load_estimator", lambda model, path:
                       SyntheticEstimator(-999) if model == "ridge" else load(model, path))
        with pytest.raises(artifacts.FinalIntegrityError, match="Final model replay differs"):
            final.run_final_evaluation(fixture["layout"])
    fixture["directory"] = fixture["layout"].run_directory("synthetic-final")
    fixture["evidence_hashes"] = failed_bundle_hashes(fixture)
    return fixture


def test_failed_final_recovery_is_read_only_and_does_not_complete(failed_final_bundle, monkeypatch):
    import builtins
    from pathlib import Path
    from src.forecasting import models, preprocessing

    fixture, forbidden = failed_final_bundle, Mock(side_effect=AssertionError("Forbidden recovery operation"))
    directory = fixture["directory"]
    before = {p: p.read_bytes() for p in failed_bundle_files(fixture)}
    path_open, builtin_open = Path.open, builtins.open

    def check_open(path, mode):
        assert not any(c in mode for c in "wax+")
        if isinstance(path, (str, Path)):
            assert not Path(path).resolve().is_relative_to(fixture["layout"].root / "data")

    def open_path(self, mode="r", *args, **kwargs):
        check_open(self, mode)
        return path_open(self, mode, *args, **kwargs)

    def open_builtin(file, mode="r", *args, **kwargs):
        check_open(file, mode)
        return builtin_open(file, mode, *args, **kwargs)

    for module, names in ((final, ("run_final_evaluation", "construct_estimator", "fit_estimator",
                                  "read_final_history", "read_reserved_outcomes", "read_validated_projection")),
                          (models, ("construct_estimator", "fit_estimator")),
                          (preprocessing, ("fit_preprocessor", "fit_primary_preprocessors")),
                          (artifacts.FinalArtifactWriter, ("__init__", "write_json", "write_text", "event", "persist_model")),
                          (artifacts, ("finalize_final_run",))):
        for name in names:
            monkeypatch.setattr(module, name, forbidden)
    monkeypatch.setattr(Path, "open", open_path)
    monkeypatch.setattr(builtins, "open", open_builtin)
    result = artifacts.verify_failed_final_recovery(directory, expected_evidence_hashes=fixture["evidence_hashes"])
    assert result == {
        "status": "recovery_verified", "verification_kind": "failed_final_evidence", "run_id": directory.name,
        "original_run_status": "failed", "final_run_completed": False,
        "original_diagnostics": read_json(directory / "diagnostics.json"),
        "scientific_verification": {"status": "passed", "evaluations": 28, "learned_refits": 20,
                                    "baseline_evaluations": 8, "predictions": 56, "models_replayed": 20},
        "evidence_hashes": fixture["evidence_hashes"],
    }
    forbidden.assert_not_called()
    assert before == {p: p.read_bytes() for p in failed_bundle_files(fixture)}
    assert read_json(directory / "run_metadata.json")["run_status"] == "failed"
    assert not (directory / "run_manifest.json").exists()
    with pytest.raises(artifacts.FinalIntegrityError, match="Unfinished"):
        artifacts.verify_final_scientific(directory)
    with pytest.raises(artifacts.FinalIntegrityError):
        artifacts.verify_final_completed(directory)


@pytest.mark.parametrize("name", [
    "predictions.json", "prediction_receipt.json", "observations.json", "metrics.json", "run.log", "comparison.md",
    "model", "descriptor", "preprocessor", "origin_features",
])
def test_failed_final_recovery_rejects_changed_bytes_before_model_loading(failed_final_bundle, monkeypatch, name):
    fixture, directory = failed_final_bundle, failed_final_bundle["directory"]
    if name in ("model", "descriptor", "preprocessor", "origin_features"):
        record = read_json(directory / "candidates.json")[0]["model_artifact"]
        path = fixture["layout"].root / record[name + "_path"]
    elif name == "comparison.md":
        path = fixture["layout"].draft_report_directory(directory.name) / name
    else:
        path = directory / name
    path.write_bytes(path.read_bytes() + b" ")
    before = {p: p.read_bytes() for p in failed_bundle_files(fixture)}
    loader = Mock(side_effect=AssertionError("Changed evidence must block model loading"))
    monkeypatch.setattr(artifacts, "_load_estimator", loader)
    with pytest.raises(artifacts.FinalIntegrityError, match="caller-held inventory"):
        artifacts.verify_failed_final_recovery(directory, expected_evidence_hashes=fixture["evidence_hashes"])
    loader.assert_not_called()
    assert before == {p: p.read_bytes() for p in failed_bundle_files(fixture)}


@pytest.mark.parametrize("name", ["predictions.json", "observations.json", "metrics.json", "model"])
def test_failed_final_recovery_reconciles_evidence_even_with_a_replaced_inventory(failed_final_bundle, name):
    fixture, directory = failed_final_bundle, failed_final_bundle["directory"]
    if name == "model":
        record = read_json(directory / "candidates.json")[0]["model_artifact"]
        path = fixture["layout"].root / record["model_path"]
        path.write_bytes(path.read_bytes() + b" ")
    else:
        path = directory / name
        rows = read_json(path)
        field = {"predictions.json": "prediction", "observations.json": "observed_target", "metrics.json": "mae"}[name]
        rows[0][field] += 1
        path.write_text(json_text(rows))
    with pytest.raises(artifacts.FinalIntegrityError):
        artifacts.verify_failed_final_recovery(directory, expected_evidence_hashes=failed_bundle_hashes(fixture))


def test_failed_final_recovery_rejects_coordinated_observation_and_metric_changes(failed_final_bundle):
    fixture, directory = failed_final_bundle, failed_final_bundle["directory"]
    observations = read_json(directory / "observations.json")
    observations[0]["observed_target"] += 1
    (directory / "observations.json").write_text(json_text(observations))
    actuals = {(r["horizon"], r["SKU_ID"], r["Warehouse_ID"]): r["observed_target"] for r in observations}
    predictions, metrics = read_json(directory / "predictions.json"), read_json(directory / "metrics.json")
    for metric in metrics:
        rows = [r for r in predictions if (r["model"], r["horizon"], r["configuration_id"]) ==
                (metric["model"], metric["horizon"], metric["configuration_id"])]
        metric.update(final.forecasting_metrics([actuals[r["horizon"], r["SKU_ID"], r["Warehouse_ID"]] for r in rows],
                                               [r["prediction"] for r in rows]))
    (directory / "metrics.json").write_text(json_text(metrics))
    with pytest.raises(artifacts.FinalIntegrityError, match="caller-held inventory"):
        artifacts.verify_failed_final_recovery(directory, expected_evidence_hashes=fixture["evidence_hashes"])


@pytest.mark.parametrize("mutation", ["status", "completion", "integrity", "timestamp", "manifest", "operation",
                                      "exception", "reason", "candidate", "count", "extra_file", "missing_hash"])
def test_failed_final_recovery_requires_exact_retained_failure(failed_final_bundle, mutation):
    fixture, directory = failed_final_bundle, failed_final_bundle["directory"]
    metadata, diagnostics = read_json(directory / "run_metadata.json"), read_json(directory / "diagnostics.json")
    if mutation in ("status", "completion", "integrity", "timestamp"):
        field, value = {"status": ("run_status", "running"), "completion": ("completed_at_utc", "synthetic"),
                        "integrity": ("integrity_result", {}), "timestamp": ("failed_at_utc", None)}[mutation]
        metadata[field] = value
        (directory / "run_metadata.json").write_text(json_text(metadata))
    elif mutation in ("operation", "exception", "reason", "candidate", "count"):
        field, value = {"operation": ("operation", "fresh_estimator_fit"), "exception": ("exception_type", "ValueError"),
                        "reason": ("failure_reason", "Other failure"), "candidate": ("candidate", {}),
                        "count": ("completed_predictions", 55)}[mutation]
        diagnostics[field] = value
        (directory / "diagnostics.json").write_text(json_text(diagnostics))
    elif mutation == "manifest":
        (directory / "run_manifest.json").write_text("{}")
    elif mutation == "extra_file":
        (directory / "unexpected.tmp").write_text("synthetic")
    hashes = failed_bundle_hashes(fixture)
    if mutation == "missing_hash":
        del hashes[next(iter(hashes))]
    with pytest.raises(artifacts.FinalIntegrityError):
        artifacts.verify_failed_final_recovery(directory, expected_evidence_hashes=hashes)


def test_failed_final_recovery_keeps_exact_prediction_equality(failed_final_bundle, monkeypatch):
    load = artifacts._load_estimator

    def changed_prediction(model, path):
        estimator = load(model, path)
        if model == "ridge":
            estimator.value = float(np.nextafter(estimator.value, np.inf))
        return estimator

    monkeypatch.setattr(artifacts, "_load_estimator", changed_prediction)
    with pytest.raises(artifacts.FinalIntegrityError, match="replay differs"):
        artifacts.verify_failed_final_recovery(failed_final_bundle["directory"],
                                               expected_evidence_hashes=failed_final_bundle["evidence_hashes"])


def test_failed_final_recovery_uses_original_snapshots_not_current_source(failed_final_bundle):
    fixture = failed_final_bundle
    source = fixture["layout"].root / "src/forecasting/final_artifacts.py"
    source.write_text(source.read_text() + "\n# Synthetic verifier revision\n")
    fixture["record"].unlink()  # Recovery never opens the current authorization or data tree.
    result = artifacts.verify_failed_final_recovery(fixture["directory"],
                                                    expected_evidence_hashes=fixture["evidence_hashes"])
    assert result["status"] == "recovery_verified"
    assert result["evidence_hashes"] == fixture["evidence_hashes"]


def test_saved_ridge_replays_original_c_order_predictions_without_fit(tmp_path, monkeypatch):
    from sklearn.linear_model import Ridge
    from src.forecasting.model_artifacts import _load_estimator, _save_estimator

    prepared = final.prepare_final_training(historical_panel())
    state = prepared.populations[1].preprocessors["ridge"]
    matrix = np.asfortranarray(state.transform(prepared.origin).to_numpy(dtype=float))
    assert matrix.flags.f_contiguous and not matrix.flags.c_contiguous
    monkeypatch.setattr(Ridge, "fit", Mock(side_effect=AssertionError("No real model fitting")))
    ridge = Ridge()
    ridge.coef_ = np.linspace(-0.3, 0.3, matrix.shape[1])
    ridge.intercept_ = 4.0
    ridge.n_features_in_ = matrix.shape[1]
    original = ridge.predict(matrix.copy())
    path = tmp_path / "synthetic-ridge.joblib"
    _save_estimator(ridge, "ridge", path)
    restored = _load_estimator("ridge", path)
    np.testing.assert_array_equal(restored.predict(matrix.copy(order="C")), original)


def test_failed_final_recovery_rejects_changes_during_verification(failed_final_bundle, monkeypatch):
    fixture, directory = failed_final_bundle, failed_final_bundle["directory"]
    verify = artifacts._verify_final_scientific

    def change_after_scientific_checks(*args):
        result = verify(*args)
        path = directory / "run.log"
        path.write_bytes(path.read_bytes() + b" ")
        return result

    monkeypatch.setattr(artifacts, "_verify_final_scientific", change_after_scientific_checks)
    with pytest.raises(artifacts.FinalIntegrityError, match="changed during recovery"):
        artifacts.verify_failed_final_recovery(directory, expected_evidence_hashes=fixture["evidence_hashes"])


def test_actual_runtime_source_and_git_are_provenance_not_permission(synthetic_runner, monkeypatch):
    fixture = synthetic_runner
    actual_sources = dict(fixture["payload"]["source_hashes"])
    actual_sources["src/forecasting/final_artifacts.py"] = "b" * 64
    monkeypatch.setattr(final, "environment_metadata", lambda root: {
        "source_hashes": actual_sources, "library_versions": fixture["payload"]["library_versions"],
        "git_commit_sha": "synthetic-current-commit", "git_branch": "synthetic-correction", "git_dirty": True,
    })
    directory = final.run_final_evaluation(fixture["layout"])
    metadata = read_json(directory / "run_metadata.json")
    retained_auth = read_json(directory / "authorization.json")
    assert retained_auth["source_hashes"] == fixture["payload"]["source_hashes"] != actual_sources
    assert metadata["source_hashes"] == metadata["runtime"]["source_hashes"] == actual_sources
    assert metadata["runtime"]["git_commit_sha"] == "synthetic-current-commit"
    assert metadata["runtime"]["git_dirty"] is True
    first = read_json(directory / "candidates.json")[0]["model_artifact"]
    descriptor = read_json(fixture["layout"].root / first["descriptor_path"])
    assert descriptor["provenance"]["source_hashes"] == actual_sources
    assert artifacts.verify_final_completed(directory)["evaluations"] == 28


def test_runtime_environment_mismatch_still_blocks_before_history_or_fit(synthetic_runner, monkeypatch):
    fixture = synthetic_runner
    versions = dict(fixture["payload"]["library_versions"], numpy="0")
    monkeypatch.setattr(final, "environment_metadata", lambda root: {
        "source_hashes": fixture["payload"]["source_hashes"], "library_versions": versions,
    })
    with pytest.raises(ExecutionBlocked, match="runtime environment"):
        final.run_final_evaluation(fixture["layout"])
    assert "historical_read" not in fixture["events"]
    assert not fixture["fits"]
    assert "synthetic_outcome_read" not in fixture["events"]


def test_recorded_execution_provenance_must_remain_internally_consistent(synthetic_runner):
    directory = final.run_final_evaluation(synthetic_runner["layout"])
    path = directory / "run_metadata.json"
    metadata = read_json(path)
    metadata["source_hashes"]["src/forecasting/final_artifacts.py"] = "b" * 64
    path.write_text(json_text(metadata))
    with pytest.raises(artifacts.FinalIntegrityError, match="runtime source provenance"):
        artifacts.verify_final_scientific(directory)


def test_explicit_corrected_run_preserves_prior_failed_storage_and_frozen_scope(synthetic_runner):
    fixture, layout = synthetic_runner, synthetic_runner["layout"]
    previous = layout.run_directory("synthetic-final")
    previous.mkdir(parents=True)
    evidence = previous / "retained.txt"
    evidence.write_text("Synthetic historical failure")
    before = evidence.read_bytes()
    fixture["payload"]["run_id"] = "synthetic-corrected"
    fixture["payload"]["approval_references"]["specific_final_run"] = "Synthetic explicit defect-correction approval"
    fixture["record"].write_text(json_text(fixture["payload"]))
    directory = final.run_final_evaluation(layout)
    assert directory.name == "synthetic-corrected"
    result = artifacts.verify_final_completed(directory)
    assert result["evaluations"] == 28 and result["models_replayed"] == 20 and result["baseline_evaluations"] == 8
    assert read_json(directory / "run_metadata.json")["producer_mapping"] == fixture["payload"]["producer_mapping"]
    assert evidence.read_bytes() == before
    assert not (previous / "run_manifest.json").exists()
