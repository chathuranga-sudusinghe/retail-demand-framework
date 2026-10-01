"""Gate 2 runner evidence: synthetic panels/mocks only, no research dataset."""
from dataclasses import replace
import csv
import importlib
import json
import re
from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest

from src.forecasting import experiment, model_artifacts
from src.forecasting.artifacts import (
    ARTIFACT_NAMES, CSV_SCHEMAS, PROTOCOL_VERSION, SCHEMA_VERSION, ArtifactWriter, file_hash,
)
from src.forecasting.configuration import PRIMARY_GRID, PRIMARY_MODELS, SUPPORTIVE_MODELS
from src.forecasting.evaluation import frame_hash, prepare_fold, validation_view
from src.forecasting.metadata import (
    REPOSITORY, ExecutionBlocked, RunScope, ValidationAuthorization, environment_metadata,
    initial_metadata, source_hashes,
)
from src.forecasting.execution import ExecutionContext, load_dataset, resolve_execution
from src.forecasting.paths import RepositoryLayout
from src.forecasting.metrics import forecasting_metrics
from src.forecasting.models import estimator_parameters
from src.forecasting.selection import record_order, select_primary, summarize_configurations
from src.forecasting.validation import VALIDATION_FOLDS


def scope(primary=PRIMARY_MODELS, supportive=SUPPORTIVE_MODELS, horizons=(1, 7, 14, 28), baselines=("naive", "seasonal_naive")):
    return RunScope(tuple(primary), tuple(supportive), tuple(horizons), tuple(baselines),
                    tuple((model, "Explicit synthetic-test exclusion") for model in ("naive", "seasonal_naive") if model not in baselines),
                    tuple((model, "Synthetic-test-only baseline scope") for model in baselines))


def panel():
    return pd.DataFrame([{"SKU_ID": sku, "Warehouse_ID": warehouse, "Date": day,
                          "Units_Sold": base + offset % 5}
                         for sku, warehouse, base in (("A", "W1", 2), ("B", "W2", 8))
                         for offset, day in enumerate(pd.date_range("2024-01-01", "2024-12-30"))])


def authorization(run_id="synthetic-unit-test", supplied_scope=None, data=None):
    return ValidationAuthorization(
        run_id=run_id, evaluation_stage="validation", protocol_version=PROTOCOL_VERSION,
        schema_version=SCHEMA_VERSION, protocol_hash=file_hash(REPOSITORY / "docs/protocol.md"),
        source_hashes=source_hashes(REPOSITORY), input_view_hash=frame_hash(validation_view(panel() if data is None else data)),
        protocol_approval_reference="Synthetic test fixture only",
        implementation_acceptance_reference="Synthetic test fixture only",
        specific_run_reference="Synthetic test fixture only", validation_run_authorized=True,
        scope=scope() if supplied_scope is None else supplied_scope,
    )


def test_full_plan_has_exact_fit_budget_and_protocol_iteration_order_without_execution():
    candidates = list(experiment.planned_candidates(scope()))
    assert len(candidates) == 1216
    assert sum(c.model in PRIMARY_MODELS for c in candidates) == 1152
    assert sum(c.model in SUPPORTIVE_MODELS for c in candidates) == 32
    assert sum(c.model in ("naive", "seasonal_naive") for c in candidates) == 32
    assert [(c.model, c.horizon, c.configuration_id, c.fold_id) for c in candidates[:8]] == [
        ("xgboost", 1, configuration, fold) for configuration in ("GBM001", "GBM002") for fold in (1, 2, 3, 4)]
    assert (candidates[384].model, candidates[768].model, candidates[1152].model) == ("lightgbm", "catboost", "ridge")


def fold_metric_records():
    # Different horizons have different model ordering; scores are synthetic.
    records = []
    for model in PRIMARY_MODELS:
        for horizon in (1, 7):
            for configuration in PRIMARY_GRID:
                for fold in (1, 2, 3, 4):
                    error = (1 if configuration.canonical_config_id in ("GBM002", "GBM010") else 2)
                    if horizon == 7 and model == "catboost":
                        error /= 2
                    records.append({"run_id": "synthetic", "evaluation_stage": "validation",
                                    "evidence_role": "primary", "model": model, "horizon": horizon,
                                    "configuration_id": configuration.canonical_config_id,
                                    "canonical_config_id": configuration.canonical_config_id,
                                    "fold_id": fold, **forecasting_metrics([10], [10 + error])})
    for model, role, configuration in (("ridge", "supportive", "fixed"), ("naive", "simple_baseline", "not_tuned")):
        for fold in (1, 2, 3, 4):
            records.append({"run_id": "synthetic", "evaluation_stage": "validation", "evidence_role": role,
                            "model": model, "horizon": 1, "configuration_id": configuration,
                            "canonical_config_id": None, "fold_id": fold, **forecasting_metrics([10], [10])})
    return records


def test_exact_configuration_and_model_ties_retain_all_ids_and_horizon_separation():
    records = fold_metric_records()
    summaries = summarize_configurations(records[::-1])
    selections, ties = select_primary(summaries, [])
    assert len(selections) == 6
    for selection in selections:
        assert selection["tied_configuration_ids"] == ["GBM002", "GBM010"]
        assert selection["administrative_representative_id"] == "GBM002"
        assert selection["configuration_id"] == "GBM002"
        assert selection["freeze_reference"] is None
    assert ties[1] == list(PRIMARY_MODELS)
    assert ties[7] == []  # CatBoost alone leads at this horizon; no overall winner.
    assert not any(s["model"] in ("ridge", "naive") for s in selections)
    assert all(r["selected_configuration"] is None for r in summaries if r["evidence_role"] != "primary")
    tied = [r for r in summaries if r["canonical_config_id"] == "GBM010"]
    assert all(r["selection_status"] == "tied_configuration" for r in tied)
    permutation = np.random.default_rng(42).permutation(len(records))
    again = summarize_configurations([records[i] for i in permutation])
    assert select_primary(again, []) == (selections, ties)
    assert again == summaries


def test_no_near_tie_tolerance_and_supporting_metrics_do_not_break_ties():
    records = fold_metric_records()
    for r in records:
        if r["canonical_config_id"] == "GBM010":
            r["wape"] = np.nextafter(r["wape"], np.inf)
        if r["canonical_config_id"] == "GBM002":
            r["mae"] = 1000
    summaries = summarize_configurations(records)
    selections, _ = select_primary(summaries, [])
    assert all(s["configuration_id"] == "GBM002" and not s["tied_configuration_ids"] for s in selections)
    assert all(s["administrative_representative_id"] is None for s in selections)


@pytest.mark.parametrize("problem", ["missing_fold", "undefined_wape", "missing_configuration", "failed_fit"])
def test_incomplete_primary_search_cannot_be_ranked(problem):
    records = fold_metric_records()
    affected = [r for r in records if r["model"] == "xgboost" and r["horizon"] == 1 and r["configuration_id"] == "GBM024"]
    if problem == "missing_fold":
        records.remove(affected[-1])
    elif problem == "missing_configuration":
        records = [r for r in records if r not in affected]
    else:
        affected[-1]["metric_status"] = "failed" if problem == "failed_fit" else "undefined_zero_actual_total"
        affected[-1]["wape"] = None
    selections, ties = select_primary(summarize_configurations(records), [])
    assert not any(s["model"] == "xgboost" and s["horizon"] == 1 for s in selections)
    assert ties[1] == []  # No complete three-model comparison.


def test_selection_rejects_final_evidence_mislabelled_roles_and_duplicate_folds():
    records = fold_metric_records()
    with pytest.raises(ValueError, match="Final evidence"):
        summarize_configurations([{**records[0], "evaluation_stage": "final_evaluation"}])
    with pytest.raises(ValueError, match="Evidence role"):
        summarize_configurations([{**records[0], "evidence_role": "supportive"}])
    with pytest.raises(ValueError, match="Duplicate"):
        summarize_configurations(records + [records[0]])
    with pytest.raises(ValueError, match="different runs"):
        summarize_configurations(records + [{**records[0], "run_id": "other-run"}])


def test_default_execution_and_final_entry_are_blocked_before_data_or_estimator_access(monkeypatch):
    constructor = Mock(side_effect=AssertionError("Cannot construct an estimator"))
    monkeypatch.setattr(experiment, "construct_estimator", constructor)
    with pytest.raises(ExecutionBlocked, match="Gate 3"):
        experiment.run_validation(None, run_id="unauthorised")
    with pytest.raises(ExecutionBlocked, match="Gate 6"):
        experiment.run_final_evaluation(object(), authorization=object())
    with pytest.raises(ExecutionBlocked, match="Gate 6"):
        experiment.main(["--stage", "final_evaluation"])
    importlib.reload(experiment)
    constructor.assert_not_called()


@pytest.mark.parametrize("change", [
    {"evaluation_stage": "final_evaluation"}, {"validation_run_authorized": False},
    {"run_id": "other"}, {"worker_count": 2}, {"worker_count": True},
    {"protocol_hash": "0" * 64}, {"protocol_version": "old"}, {"schema_version": "old"},
    {"source_hashes": {}}, {"input_view_hash": "not-a-hash"},
    {"implementation_acceptance_reference": "pending"}, {"specific_run_reference": ""},
])
def test_authorization_is_specific_and_source_bound(change):
    approved = authorization()
    with pytest.raises(ExecutionBlocked):
        replace(approved, **change).validate(REPOSITORY, approved.run_id)


@pytest.mark.parametrize("change", [
    {"primary_models": ("catboost", "xgboost")}, {"primary_models": ("ridge",)},
    {"primary_models": ("xgboost", "xgboost")}, {"horizons": (28, 1)}, {"horizons": (True,)},
    {"baselines": ("naive",), "baseline_exclusions": ()},
    {"baseline_approval_references": ()}, {"horizons": ()},
])
def test_scope_has_no_grid_expansion_no_silent_baseline_omission(change):
    with pytest.raises(ExecutionBlocked):
        replace(scope(), **change).validate()


def test_scope_json_roundtrip_and_no_approval_record_is_generated_by_runner(tmp_path):
    from dataclasses import asdict
    original = authorization()
    path = tmp_path / "synthetic-approval.json"
    path.write_text(json.dumps(asdict(original)))
    loaded = ValidationAuthorization.from_json(path)
    assert loaded == original
    loaded.validate(REPOSITORY, loaded.run_id)
    assert not list((REPOSITORY / "outputs/revised-forecasting").glob("synthetic-unit-test*"))


@pytest.fixture
def prepared_folds():
    return {fold.number: prepare_fold(panel(), fold.number) for fold in VALIDATION_FOLDS}


def install_synthetic_runner_mocks(monkeypatch, tmp_path, prepared_folds, *, fail_at=None):
    """Only this test harness substitutes native coverage/estimators; no public bypass."""
    constructed, fitting = [], []

    class SyntheticEstimator:
        def __init__(self, model, configuration):
            self.model, self.configuration = model, configuration

        def get_params(self, deep=True):
            return estimator_parameters(self.model, self.configuration)

        def predict(self, matrix, **kwargs):
            return np.ones(len(matrix))  # All primary configurations tie by construction.

    def construct(model, configuration):
        result = SyntheticEstimator(model, configuration)
        constructed.append(result)
        return result

    def fit(estimator, model, configuration, matrix, labels):
        fitting.append((model, configuration, matrix.copy(), labels.copy()))
        if fail_at and len(fitting) == fail_at:
            raise ValueError("Synthetic controlled fit failure")
        # Check all library fits are isolated from mutation of the cached evidence.
        matrix[:] = -999
        labels[:] = -999
        params = estimator_parameters(model, configuration)
        return {"requested_api_parameters": params, "effective_api_parameters": params,
                "requested_iterations": configuration.boosting_iterations if configuration else 300 if model == "random_forest" else None,
                "effective_iterations": configuration.boosting_iterations if configuration else 300 if model == "random_forest" else None}

    writes = []
    real_write = ArtifactWriter.write_json

    def write(self, name, value):
        writes.append((name, value.get("run_status")))
        # Hundreds of checkpoint rewrites add no test evidence; test initial/final
        # persistence separately while exercising all candidate iterations.
        if name == "run_metadata.json" and value.get("run_status") == "running":
            return
        real_write(self, name, value)

    # Native I/O is substituted only in the synthetic harness; descriptors,
    # preprocessing, hashes and replay validation use their actual implementation.
    def save_mock(estimator, model, path):
        path.write_text("synthetic constant model")

    def load_mock(model, path):
        return SyntheticEstimator(model, None)

    monkeypatch.setattr(model_artifacts, "_save_estimator", save_mock)
    monkeypatch.setattr(model_artifacts, "_load_estimator", load_mock)
    monkeypatch.setattr(experiment, "construct_estimator", construct)
    monkeypatch.setattr(experiment, "fit_estimator", fit)
    monkeypatch.setattr(experiment, "prepare_fold", lambda data, number, **kwargs: prepared_folds[number])
    monkeypatch.setattr(experiment, "require_native_roster", lambda data: None)
    monkeypatch.setattr(experiment, "ArtifactWriter", lambda repository, run_id: ArtifactWriter(tmp_path, run_id))
    monkeypatch.setattr(ArtifactWriter, "write_json", write)
    monkeypatch.setattr(experiment, "environment_metadata", lambda root: {
        "git_commit_sha": "synthetic-test", "git_branch": "synthetic-test", "git_dirty": True,
        "source_hashes": source_hashes(root), "python_version": "3.12.3", "library_versions": {},
        "library_builds": {}, "requirements_hash": file_hash(root / "requirements.txt"),
        "operating_system": "synthetic test", "hardware": {}, "execution_environment": {"worker_count": 1},
    })
    return constructed, fitting, writes


def read_csv(path):
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def test_mocked_full_plan_writes_exact_artifacts_metadata_and_same_candidate_populations(monkeypatch, tmp_path, prepared_folds, capsys):
    constructed, fitting, writes = install_synthetic_runner_mocks(monkeypatch, tmp_path, prepared_folds)
    approved = authorization()
    directory = experiment.run_validation(panel(), run_id=approved.run_id, authorization=approved)
    assert directory == tmp_path / "outputs/revised-forecasting" / approved.run_id
    assert set(p.name for p in directory.iterdir()) == set(ARTIFACT_NAMES) | {"run.log", "run_manifest.json", "authorization.json", "models"}
    assert len(constructed) == len(fitting) == 1184  # 1,152 mocked primary + 32 mocked supportive.
    assert writes[0] == ("run_metadata.json", "preflight")
    assert writes[-1] == ("run_manifest.json", None)
    assert not any(status == "completed" for _, status in writes)
    metadata = json.loads((directory / "run_metadata.json").read_text())
    assert metadata["run_status"] == "verified_completed"
    assert metadata["planned_primary_fits"] == 1152
    assert metadata["planned_supportive_fits"] == metadata["planned_baseline_evaluations"] == 32
    assert metadata["schema_version"] == SCHEMA_VERSION
    assert metadata["protocol_version"] == PROTOCOL_VERSION
    assert metadata["final_evaluation_status"] == "blocked_gate_6"
    assert metadata["final_refit_policy"] is None
    assert metadata["approval_references"]["final_refit"] is None
    assert metadata["approval_references"]["selection_freeze"] is None
    for key in ("git_commit_sha", "git_branch", "git_dirty", "source_hashes", "python_version", "library_versions",
                "library_builds", "requirements_hash", "operating_system", "hardware", "execution_environment",
                "feature_contract_path", "feature_contract_hash", "random_seeds", "run_scope", "created_at_utc"):
        assert key in metadata
    assert len(metadata["candidate_records"]) == len(metadata["metric_records"]) == 1216
    assert len(metadata["canonical_grid"]) == 24
    for records_key in ("candidate_records", "metric_records", "representation_records", "eligibility_records"):
        assert metadata[records_key] == sorted(metadata[records_key], key=record_order)
    for record in metadata["candidate_records"]:
        assert record["worker_count"] == record["thread_count"] == 1
        assert record["device"] == "CPU"
        assert record["forecast_origin"] == VALIDATION_FOLDS[record["fold_id"] - 1].training.end.isoformat()
        assert record["target_end_date"] <= "2024-12-02"
        assert record["canonical_config_id"] is not None if record["evidence_role"] == "primary" else record["canonical_config_id"] is None
    for model in PRIMARY_MODELS:
        for horizon in (1, 7, 14, 28):
            records = [r for r in metadata["selection_records"] if r["model"] == model and r["horizon"] == horizon]
            assert len(records) == 1
            assert records[0]["tied_configuration_ids"] == [c.canonical_config_id for c in PRIMARY_GRID]
            assert records[0]["freeze_reference"] is None
            assert records[0]["tied_primary_models"] == list(PRIMARY_MODELS)
    for name, columns in CSV_SCHEMAS.items():
        header, rows = read_csv(directory / name)
        assert header == list(columns)
        assert rows
    _, predictions = read_csv(directory / "predictions.csv")
    assert len(predictions) == 2432
    prediction_keys = [tuple(r[k] for k in ("run_id", "evaluation_stage", "evidence_role", "model", "horizon",
                                          "configuration_id", "fold_id", "SKU_ID", "Warehouse_ID")) for r in predictions]
    assert len(prediction_keys) == len(set(prediction_keys))
    assert all(r["selected_configuration"] == "true" for r in predictions if r["evidence_role"] == "primary")
    assert all(r["selected_configuration"] == "" for r in predictions if r["evidence_role"] != "primary")
    assert all(r["representation_id"] == "" for r in predictions if r["evidence_role"] == "simple_baseline")
    _, eligibility = read_csv(directory / "eligibility_counts.csv")
    assert all(json.loads(r["overlapping_reasons"]) == [] for r in eligibility)
    assert all(r["scored_origin_count"] == "1" for r in eligibility)
    for entry in metadata["artifact_manifest"]:
        path = tmp_path / entry["artifact_path"]
        if path.name == "run_metadata.json":
            assert entry["artifact_hash"] is None and entry["artifact_status"] == "self_reference"
        else:
            assert entry["artifact_hash"] == file_hash(path) and entry["artifact_status"] == "written"
    assert not any(r["human_review_reference"] for r in metadata["selection_records"])
    text = (directory / "comparison.md").read_text()
    assert "December 3–16" in text and "full-year EDA" in text
    assert "Primary model tie" in text and "Fold-level primary WAPE comparison" in text
    assert "fold differences" not in text
    # Operational logs count actual learned fits separately from baseline evaluations.
    log = (directory / "run.log").read_text()
    assert capsys.readouterr().out == log
    lines = log.splitlines()
    assert "event=run_start" in lines[0]
    assert "primary_fits=1152 supportive_fits=32 baseline_evaluations=32" in lines[0]
    assert "planned_fits=1184 planned_evaluations=1216" in lines[0]
    starts = [line for line in lines if "event=fit_start " in line]
    completions = [line for line in lines if "event=fit_complete " in line]
    evaluations = [line for line in lines if "event=evaluation_complete " in line or "event=baseline_complete " in line]
    assert len(starts) == len(completions) == 1184
    assert len(evaluations) == 1216
    plan = list(experiment.planned_candidates(scope()))
    for number, (line, candidate) in enumerate(zip(evaluations, plan, strict=True), 1):
        for field, value in (("fold", candidate.fold_id), ("horizon", candidate.horizon),
                             ("model", candidate.model), ("configuration_id", candidate.configuration_id)):
            assert f"{field}={value} " in line
        assert f"completed_evaluations={number}/1216 " in line
        assert f"completed_fits={min(number, 1184)}/1184 " in line
    for number, line in enumerate(completions, 1):
        assert f"completed_fits={number}/1184 " in line
    assert "event=finalization_verified" in lines[-1]
    assert "fit_progress=100.00%" in lines[-1] and "progress=100.00%" in lines[-1]
    assert "total_elapsed_seconds=" in lines[-1]
    assert not any(value in log for value in ("SKU_ID", "Warehouse_ID", "Units_Sold", "prediction=", "matrix", "-999", "get_params"))
    # Same model/horizon/fold uses identical matrix/labels for every config;
    # all three primary models use the identical evidence as well.
    for index, candidate in enumerate(c for c in experiment.planned_candidates(scope()) if c.model in (*PRIMARY_MODELS, *SUPPORTIVE_MODELS)):
        model, config, matrix, labels = fitting[index]
        pop = prepared_folds[candidate.fold_id].horizons[candidate.horizon]
        np.testing.assert_array_equal(matrix, pop.preprocessors[model].transform(pop.features).to_numpy())
        np.testing.assert_array_equal(labels, pop.labels)


def test_failed_fit_retains_diagnostics_and_never_selects_partial_fold_evidence(monkeypatch, tmp_path, prepared_folds, capsys):
    constructed, _, _ = install_synthetic_runner_mocks(monkeypatch, tmp_path, prepared_folds, fail_at=6)
    approved = authorization(supplied_scope=scope(primary=("xgboost",), supportive=(), horizons=(1,), baselines=()))
    with pytest.raises(ValueError, match="Synthetic controlled fit failure"):
        experiment.run_validation(panel(), run_id=approved.run_id, authorization=approved)
    directory = tmp_path / "outputs/revised-forecasting" / approved.run_id
    metadata = json.loads((directory / "run_metadata.json").read_text())
    assert len(constructed) == 6  # No retry or continued search after failure.
    assert metadata["run_status"] == "failed"
    assert metadata["selection_records"] == []
    assert len(metadata["candidate_records"]) == len(metadata["metric_records"]) == 6
    assert metadata["metric_records"][-1]["wape"] is None
    assert metadata["metric_records"][-1]["metric_status"] == "failed"
    assert (directory / "diagnostics.json").exists()
    _, predictions = read_csv(directory / "predictions.csv")
    assert len(predictions) == 10  # No fabricated failed-candidate predictions.
    assert all(r["selection_status"] == "candidate" for r in predictions)
    log = (directory / "run.log").read_text()
    assert capsys.readouterr().out == log
    assert log.count("event=fit_start ") == 6
    assert log.count("event=fit_complete ") == 5
    failure = next(line for line in log.splitlines() if "event=fit_failure " in line)
    assert "fold=2 horizon=1 evidence_role=primary model=xgboost configuration_id=GBM002" in failure
    assert "completed_fits=5/96" in failure and "exception_type=ValueError" in failure
    assert "reason=ValueError during estimator_fit" in failure
    assert "diagnostics.json" in failure and "elapsed_seconds=" in failure
    assert "event=run_failure" in log.splitlines()[-1]
    assert "event=run_complete" not in log


def test_logging_leaves_all_result_artifact_bytes_unchanged(monkeypatch, tmp_path, prepared_folds):
    approved = authorization(supplied_scope=scope(primary=("xgboost",), supportive=(), horizons=(1,), baselines=()))
    initial = experiment.initial_metadata
    real_progress = experiment.RunProgress

    def fixed_metadata(*args):
        metadata = initial(*args)
        metadata["created_at_utc"] = "2024-01-01T00:00:00+00:00"
        return metadata

    def muted_progress(*args, **kwargs):
        result = real_progress(*args, **kwargs)
        result.logger.disabled = True
        return result

    results = []
    for muted in (False, True):
        with monkeypatch.context() as patch:
            install_synthetic_runner_mocks(patch, tmp_path / str(muted), prepared_folds)
            patch.setattr(experiment, "initial_metadata", fixed_metadata)
            if muted:
                patch.setattr(experiment, "RunProgress", muted_progress)
            directory = experiment.run_validation(panel(), run_id=approved.run_id, authorization=approved)
            results.append({name: (directory / name).read_bytes() for name in CSV_SCHEMAS} |
                           {"selected_configurations.json": (directory / "selected_configurations.json").read_bytes()})
    assert results[0] == results[1]


def test_input_mismatch_is_blocked_before_preparation_and_preserves_failed_manifest(monkeypatch, tmp_path):
    monkeypatch.setattr(experiment, "ArtifactWriter", lambda root, run_id: ArtifactWriter(tmp_path, run_id))
    monkeypatch.setattr(experiment, "environment_metadata", lambda root: {})
    prep = Mock(side_effect=AssertionError("Must not prepare unapproved inputs"))
    monkeypatch.setattr(experiment, "prepare_fold", prep)
    approved = replace(authorization(), input_view_hash="0" * 64)
    with pytest.raises(ExecutionBlocked, match="authorised input view"):
        experiment.run_validation(panel(), run_id=approved.run_id, authorization=approved)
    prep.assert_not_called()
    directory = tmp_path / "outputs/revised-forecasting" / approved.run_id
    metadata = json.loads((directory / "run_metadata.json").read_text())
    assert metadata["run_status"] == "failed"
    assert not metadata["candidate_records"]
    log = (directory / "run.log").read_text()
    assert "reason=Validation input differs from the specifically authorised input view." in log
    assert "event=run_failure" in log and "event=fit_start" not in log


def test_preflight_missing_outcome_persists_calendar_diagnostics_without_any_fit(monkeypatch, tmp_path):
    source = panel()
    source.loc[source.SKU_ID.eq("A") & source.Date.eq(pd.Timestamp("2024-04-28")), "Units_Sold"] = np.nan
    approved = authorization(data=source)
    monkeypatch.setattr(experiment, "ArtifactWriter", lambda root, run_id: ArtifactWriter(tmp_path, run_id))
    monkeypatch.setattr(experiment, "environment_metadata", lambda root: {})
    monkeypatch.setattr(experiment, "require_native_roster", lambda data: None)
    constructor = Mock(side_effect=AssertionError("Fit cannot precede preflight"))
    monkeypatch.setattr(experiment, "construct_estimator", constructor)
    with pytest.raises(ValueError, match="target population"):
        experiment.run_validation(source, run_id=approved.run_id, authorization=approved)
    constructor.assert_not_called()
    directory = tmp_path / "outputs/revised-forecasting" / approved.run_id
    diagnostics = json.loads((directory / "diagnostics.json").read_text())
    assert diagnostics["eligibility_diagnostics"][0]["Date"] == "2024-04-01"
    metadata = json.loads((directory / "run_metadata.json").read_text())
    assert metadata["run_status"] == "failed"
    assert metadata["selection_records"] == []
    assert "Run status at rendering: failed" in (directory / "comparison.md").read_text()


def test_exact_csv_column_order_is_checked_against_the_frozen_protocol():
    protocol = (REPOSITORY / "docs/protocol.md").read_text()
    for name, expected in CSV_SCHEMAS.items():
        if name == "predictions.csv":
            section = protocol.split("## 14. Prediction-level records", 1)[1]
        else:
            section = protocol.split(f"`{name}` required column order:", 1)[1]
        block = re.search(r"```(?:text)?\n(.*?)\n```", section, re.DOTALL).group(1)
        assert tuple(value.strip() for value in block.replace("\n", "").split(",")) == expected


def test_artifacts_are_exclusive_safe_and_reject_schema_drift(tmp_path):
    writer = ArtifactWriter(tmp_path, "unique")
    writer.write_json("run_metadata.json", {"status": "synthetic"})
    before = (writer.directory / "run_metadata.json").read_bytes()
    with pytest.raises(FileExistsError):
        ArtifactWriter(tmp_path, "unique")
    assert (writer.directory / "run_metadata.json").read_bytes() == before
    for run_id in ("../bad", "", "/tmp/bad", "..", "a/b"):
        with pytest.raises(ValueError):
            ArtifactWriter(tmp_path, run_id)
    with pytest.raises(ValueError, match="frozen schema"):
        writer.write_csv("fold_metrics.csv", [{"model": "xgboost", "horizon": 1}])


def test_runtime_and_metadata_capture_actual_pinned_environment_without_fitting():
    environment = environment_metadata(REPOSITORY)
    assert environment["python_version"] == "3.12.3"
    assert environment["library_versions"]["lightgbm"] == "4.7.0"
    assert environment["library_builds"]["xgboost"]["native_library_hashes"]
    assert environment["execution_environment"]["worker_count"] == 1
    assert environment["execution_environment"]["blas_thread_limit"] == 1
    metadata = initial_metadata(authorization(), REPOSITORY)
    assert metadata["approval_references"]["final_run"] is None
    assert metadata["approval_references"]["final_refit"] is None
    assert metadata["run_status"] == "preflight"
    assert len(metadata["conceptual_feature_names"]) == 14
    assert len(metadata["numerical_feature_names"]) == 12


@pytest.mark.parametrize("point", ["fit", "persistence", "metrics"])
@pytest.mark.parametrize("logging_error", [OSError("controlled log failure"), KeyboardInterrupt()])
def test_candidate_logging_failure_preserves_original_and_recovery(
    tmp_path, monkeypatch, prepared_folds, point, logging_error,
):
    install_synthetic_runner_mocks(monkeypatch, tmp_path, prepared_folds)
    approved = authorization(supplied_scope=scope(primary=(), supportive=("ridge",), horizons=(1,), baselines=()))
    original = ValueError("controlled candidate failure")

    def fail(*args, **kwargs):
        raise original

    def fail_logging(*args, **kwargs):
        raise logging_error

    target = {"fit": "fit_estimator", "persistence": "persist_model", "metrics": "forecasting_metrics"}[point]
    monkeypatch.setattr(experiment, target, fail)
    monkeypatch.setattr(experiment.RunProgress, "fail_candidate", fail_logging)
    with pytest.raises(ValueError) as caught:
        experiment.run_validation(panel(), run_id=approved.run_id, authorization=approved)
    assert caught.value is original
    assert f"Candidate failure logging failed: {type(logging_error).__name__}." in original.__notes__
    directory = tmp_path / "outputs/revised-forecasting" / approved.run_id
    metadata = json.loads((directory / "run_metadata.json").read_text())
    assert metadata["failure_type"] == "ValueError"
    assert metadata["failure_reason"] == str(original)
    assert metadata["candidate_records"][0]["candidate_status"] == "failed"
    assert metadata["metric_records"][0]["metric_status"] == "failed"
    assert (directory / "diagnostics.json").is_file()
    assert not (directory / "run_manifest.json").exists()


def test_candidate_diagnostic_interrupt_preserves_original_failure(tmp_path, monkeypatch, prepared_folds):
    install_synthetic_runner_mocks(monkeypatch, tmp_path, prepared_folds)
    approved = authorization(supplied_scope=scope(primary=(), supportive=("ridge",), horizons=(1,), baselines=()))
    original = ValueError("controlled candidate failure")
    interrupted_writes = []
    write_json = ArtifactWriter.write_json

    def fail_fit(*args, **kwargs):
        raise original

    def write(self, name, value):
        if name == "diagnostics.json" and "candidate" in value:
            interrupted_writes.append(name)
            raise KeyboardInterrupt("controlled diagnostic interruption")
        return write_json(self, name, value)

    monkeypatch.setattr(experiment, "fit_estimator", fail_fit)
    monkeypatch.setattr(ArtifactWriter, "write_json", write)
    with pytest.raises(ValueError) as caught:
        experiment.run_validation(panel(), run_id=approved.run_id, authorization=approved)
    assert caught.value is original
    assert interrupted_writes == ["diagnostics.json"]
    assert "Candidate diagnostic persistence failed: KeyboardInterrupt." in original.__notes__
    directory = tmp_path / "outputs/revised-forecasting" / approved.run_id
    assert not (directory / "run_manifest.json").exists()


@pytest.mark.parametrize("use_context", [False, True])
def test_alternate_layout_is_used_consistently_without_global_root_patching(
    tmp_path, monkeypatch, prepared_folds, use_context,
):
    from dataclasses import asdict
    layout = RepositoryLayout(tmp_path / "alternate-repository")
    # Copy only approval-bound source/configuration records, never project data.
    for relative in (*source_hashes(REPOSITORY), "docs/protocol.md"):
        destination = layout.repository_path(relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((REPOSITORY / relative).read_bytes())
    source = panel()
    layout.dataset.parent.mkdir(parents=True)
    source.to_csv(layout.dataset, index=False)
    approved = replace(
        authorization(supplied_scope=scope(primary=(), supportive=("ridge",), horizons=(1,), baselines=())),
        protocol_hash=file_hash(layout.protocol), source_hashes=source_hashes(layout.root),
    )
    layout.execution_record.parent.mkdir(parents=True)
    layout.execution_record.write_text(json.dumps(asdict(approved)))
    install_synthetic_runner_mocks(monkeypatch, layout.root, prepared_folds)
    # Use the real writer/layout; only estimator computation and environment collection are synthetic.
    monkeypatch.setattr(experiment, "ArtifactWriter", ArtifactWriter)
    environments = []
    environment = experiment.environment_metadata
    def collect(root):
        environments.append(root)
        return environment(root)
    monkeypatch.setattr(experiment, "environment_metadata", collect)
    validations = []
    validate = type(approved).validate
    def check(self, root, run_id):
        validations.append(root)
        return validate(self, root, run_id)
    monkeypatch.setattr(type(approved), "validate", check)
    context = resolve_execution(layout) if use_context else None
    data = load_dataset(context.dataset_path) if context else source
    directory = experiment.run_validation(
        data, run_id=approved.run_id, authorization=approved,
        execution_context=context, layout=None if context else layout,
    )
    assert directory == layout.run_directory(approved.run_id)
    assert environments == [layout.root]
    assert validations == [layout.root] * (3 if use_context else 2)
    metadata = json.loads((directory / "run_metadata.json").read_text())
    assert metadata["protocol_hash"] == file_hash(layout.protocol)
    assert metadata["feature_contract_hash"] == file_hash(layout.feature_contract)
    assert metadata["source_hashes"] == source_hashes(layout.root)
    assert (directory / "run_manifest.json").is_file()
    assert (directory / "authorization.json").is_file()
    assert layout.validation_model_directory(directory).is_dir()
    assert layout.preprocessing_state_directory(directory, "ridge", 1, 1).is_dir()
    assert not (REPOSITORY / "outputs/revised-forecasting" / approved.run_id).exists()


def test_context_layout_conflict_is_rejected_before_run_creation(tmp_path):
    approved = authorization()
    original = RepositoryLayout(tmp_path / "original")
    conflicting = RepositoryLayout(tmp_path / "conflicting")
    context = ExecutionContext(approved, original.execution_record, "synthetic", {}, original.dataset, original)
    with pytest.raises(ExecutionBlocked, match="repository layout differ"):
        experiment.run_validation(None, run_id=approved.run_id, authorization=approved,
                                  execution_context=context, layout=conflicting)
    assert not original.output_root.exists()
    assert not conflicting.output_root.exists()
