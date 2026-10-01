"""Deterministic operational/reporting checks with synthetic saved evidence only."""
import subprocess
import sys
import json
import logging
from unittest.mock import Mock

import pytest

from src.forecasting import progress, reporting
from src.forecasting.artifacts import CSV_SCHEMAS, PROTOCOL_VERSION, ArtifactWriter


def keys(**extra):
    return {"fold_id": 1, "horizon": 7, "evidence_role": "primary", "model": "xgboost",
            "configuration_id": "GBM001", **extra}


def test_terminal_file_setup_counts_elapsed_and_handler_cleanup(tmp_path, monkeypatch, capsys):
    execute = Mock(side_effect=AssertionError("Logging must not execute experiments"))
    monkeypatch.setattr("src.forecasting.experiment.run_validation", execute)
    monkeypatch.setattr("src.forecasting.models.construct_estimator", execute)
    clock = iter(range(30))
    monkeypatch.setattr(progress, "perf_counter", lambda: next(clock))
    root_handlers = logging.getLogger().handlers[:]
    logger = progress.RunProgress(tmp_path, "synthetic", primary_fits=1, supportive_fits=0, baseline_evaluations=1)
    assert len(logger.logger.handlers) == 2
    assert isinstance(logger.logger.handlers[0], logging.StreamHandler)
    assert isinstance(logger.logger.handlers[1], logging.FileHandler)
    assert logger.logger.propagate is False
    assert (tmp_path / "run.log").is_file()
    logger.start_candidate(keys(Units_Sold=[918273645], matrix=[[918273645]], prediction=918273645), learned=True)
    logger.complete_fit()
    logger.complete_candidate(learned=True)
    logger.start_candidate(keys(evidence_role="simple_baseline", model="naive", configuration_id="not_tuned"), learned=False)
    logger.complete_candidate(learned=False)
    logger.complete_run("completed")
    handlers = logger.logger.handlers[:]
    logger.close()
    assert not logger.logger.handlers
    assert all(handler._closed for handler in handlers)
    assert logging.getLogger().handlers == root_handlers
    text = (tmp_path / "run.log").read_text()
    assert capsys.readouterr().out == text
    lines = text.splitlines()
    assert [line.split("event=")[1].split()[0] for line in lines] == [
        "run_start", "fit_start", "fit_complete", "evaluation_complete", "baseline_start", "baseline_complete", "run_complete"]
    assert "completed_fits=0/1" in lines[1]
    assert "completed_fits=1/1 fit_progress=100.00% completed_evaluations=0/2 progress=0.00%" in lines[2]
    assert "completed_evaluations=1/2 progress=50.00%" in lines[3]
    assert "completed_fits=1/1" in lines[5] and "completed_evaluations=2/2 progress=100.00%" in lines[5]
    assert "elapsed_seconds=1.000" in lines[0]
    assert "total_elapsed_seconds=" in lines[-1]
    assert not any(value in text for value in ("918273645", "Units_Sold", "matrix", "prediction="))
    execute.assert_not_called()


@pytest.mark.parametrize("after_fit,exception", [(False, ValueError("raw row [918273645]; secret=credential-sentinel")),
                                                (True, RuntimeError("prediction=[918273645]")),
                                                (False, KeyboardInterrupt())])
def test_failures_keep_context_without_exception_payloads(tmp_path, after_fit, exception, capsys):
    logger = progress.RunProgress(tmp_path, "synthetic", primary_fits=2, supportive_fits=0, baseline_evaluations=0)
    logger.start_candidate(keys(), learned=True)
    if after_fit:
        logger.complete_fit()
    logger.fail_run(exception)
    logger.close()
    text = (tmp_path / "run.log").read_text()
    assert capsys.readouterr().out == text
    assert "event=evaluation_failure" in text if after_fit else "event=fit_failure" in text
    assert f"exception_type={type(exception).__name__}" in text
    assert "reason=" in text and "diagnostics.json" in text
    assert "event=run_failure" in text
    assert "fold=1 horizon=7 evidence_role=primary model=xgboost configuration_id=GBM001" in text
    assert "completed_fits=1/2" in text if after_fit else "completed_fits=0/2" in text
    assert "918273645" not in text and "credential-sentinel" not in text


def test_repeated_setup_has_no_duplicate_logs_or_root_configuration(tmp_path, capsys):
    for number in range(2):
        directory = tmp_path / str(number)
        directory.mkdir()
        logger = progress.RunProgress(directory, "same-id", primary_fits=0, supportive_fits=0, baseline_evaluations=1)
        logger.close()
        assert (directory / "run.log").read_text().count("event=run_start") == 1
    assert capsys.readouterr().out.count("event=run_start") == 2


def test_known_failure_reason_is_logged_explicitly_without_model_payload(tmp_path, capsys):
    logger = progress.RunProgress(tmp_path, "synthetic", primary_fits=1, supportive_fits=0, baseline_evaluations=0)
    logger.start_candidate(keys(), learned=True)
    logger.fail_candidate(ValueError("Iteration mismatch: requested 100, effective 17."))
    logger.fail_run(ValueError("Iteration mismatch: requested 100, effective 17."))
    logger.close()
    text = (tmp_path / "run.log").read_text()
    assert capsys.readouterr().out == text
    assert "reason=Iteration mismatch: requested 100, effective 17." in text
    assert text.count("event=fit_failure ") == 1
    assert "completed_fits=0/1" in text


def test_module_imports_do_not_setup_logging_or_execute(tmp_path):
    from src.forecasting.paths import REPOSITORY
    # A fresh interpreter also checks first imports without rebinding shared classes.
    code = f"""
import sys
sys.path.insert(0, {str(REPOSITORY)!r})
import importlib
import logging
from pathlib import Path
from unittest.mock import Mock, patch

forbidden = Mock(side_effect=AssertionError("Import must not execute or write"))
with patch("src.forecasting.models.construct_estimator", forbidden), \
     patch.object(logging, "FileHandler", forbidden), \
     patch.object(Path, "mkdir", forbidden), \
     patch.object(Path, "write_text", forbidden), \
     patch.object(Path, "write_bytes", forbidden):
    for name in ("progress", "reporting", "authorization", "execution", "persistence", "orchestration", "experiment"):
        importlib.import_module("src.forecasting." + name)
forbidden.assert_not_called()
"""
    subprocess.run([sys.executable, "-c", code], cwd=tmp_path, check=True)
    assert list(tmp_path.iterdir()) == []


@pytest.fixture
def saved_evidence(tmp_path):
    writer = ArtifactWriter(tmp_path, "synthetic-report")
    metadata = {"run_id": "synthetic-report", "protocol_version": PROTOCOL_VERSION,
                "git_commit_sha": "1234567890abcdef", "evaluation_stage": "validation", "run_status": "completed",
                "run_scope": {"primary_models": list(reporting.PRIMARY), "supportive_models": ["ridge", "random_forest"],
                              "horizons": [1, 7, 14, 28], "baselines": ["naive", "seasonal_naive"], "baseline_exclusions": []},
                "final_evaluation_status": "blocked_gate_6", "tied_primary_models": {"1": ["xgboost", "lightgbm"]}}
    summaries, folds, selections = [], [], []
    for horizon in (1, 7, 14, 28):
        for model in (*reporting.PRIMARY, "ridge", "random_forest", "naive", "seasonal_naive"):
            role = "primary" if model in reporting.PRIMARY else "supportive" if model in ("ridge", "random_forest") else "simple_baseline"
            configurations = ("GBM001", "GBM002") if model == "xgboost" and horizon == 1 else (
                "GBM001" if role == "primary" else "fixed" if role == "supportive" else "not_tuned",)
            if role == "primary":
                selections.append({"model": model, "horizon": horizon, "configuration_id": "GBM001",
                                   "tied_configuration_ids": list(configurations) if len(configurations) == 2 else [],
                                   "administrative_representative_id": "GBM001" if len(configurations) == 2 else None})
            for configuration in configurations:
                common = {"run_id": metadata["run_id"], "evaluation_stage": "validation", "model": model,
                          "horizon": horizon, "evidence_role": role, "configuration_id": configuration,
                          "canonical_config_id": configuration if role == "primary" else None}
                # Intentionally distinct stored means/fold values prove rendering never recomputes means.
                summaries.append({**dict.fromkeys(CSV_SCHEMAS["configuration_summary.csv"]), **common,
                                  "expected_fold_count": 4, "valid_fold_count": 4, "n_predictions": 1000,
                                  "mean_wape": 0.3141592653589793, "mean_mae": 2.75, "mean_rmse": 3.125, "mean_bias": -0.5,
                                  "metric_status": "valid", "selected_configuration": True if role == "primary" else None,
                                  "selection_status": "tied_configuration" if configuration == "GBM002" else "validation_leader" if role == "primary" else "fixed_supportive" if role == "supportive" else "not_applicable",
                                  "review_status": "pending_human_review"})
                for fold_id in (1, 2, 3, 4):
                    folds.append({**dict.fromkeys(CSV_SCHEMAS["fold_metrics.csv"]), **common, "fold_id": fold_id,
                                  "n_predictions": 250, "wape": 0.0123456789012345, "mae": 2.0, "rmse": 3.0,
                                  "bias": -0.25, "metric_status": "valid"})
    writer.write_json("run_metadata.json", metadata)
    writer.write_json("selected_configurations.json", {"run_id": metadata["run_id"], "selections": selections})
    writer.write_csv("configuration_summary.csv", summaries)
    writer.write_csv("fold_metrics.csv", folds)
    return writer


def test_report_required_summary_matrices_and_horizon_evidence(saved_evidence):
    text = reporting.comparison_text(saved_evidence.directory, require_verified=False)
    for value in ("synthetic-report", PROTOCOL_VERSION, "1234567890abcdef", "Validation folds: 1, 2, 3, 4",
                  "Authorised horizons (days): 1, 7, 14, 28", "Primary model roles: XGBoost, LightGBM, CatBoost",
                  "Supportive model roles: Ridge, Random Forest", "Baseline model roles: Naive, Seasonal Naive",
                  "Final-evaluation status: blocked_gate_6; blocked/not executed", "No cross-horizon overall winner"):
        assert value in text
    configurations = text.split("## Selected-configuration matrix\n", 1)[1].split("## Primary WAPE comparison matrix", 1)[0]
    assert "| Horizon | XGBoost | LightGBM | CatBoost |" in configurations
    assert "| 1-day | GBM001 (administrative tie representative) | GBM001 | GBM001 |" in configurations
    for horizon in (7, 14, 28):
        assert f"| {horizon}-day | GBM001 | GBM001 | GBM001 |" in configurations
    matrix = text.split("## Primary WAPE comparison matrix\n", 1)[1].split("## 1-day", 1)[0]
    assert "| Horizon | XGBoost WAPE | LightGBM WAPE | CatBoost WAPE |" in matrix
    for horizon in (1, 7, 14, 28):
        assert f"| {horizon}-day | 0.3141592653589793 | 0.3141592653589793 | 0.3141592653589793 |" in matrix
        section = text.split(f"## {horizon}-day\n", 1)[1].split("\n## ", 1)[0]
        primary = section.split("### Supportive comparison", 1)[0]
        supportive = section.split("### Supportive comparison", 1)[1].split("### Baseline comparison", 1)[0]
        baseline = section.split("### Baseline comparison", 1)[1].split("### Tie information", 1)[0]
        for model in reporting.PRIMARY:
            assert f"| {model} | primary | GBM001 |" in primary
            assert f"Selected configuration — {reporting.NAMES[model]}: GBM001" in primary
        assert "| ridge | supportive | fixed |" in supportive
        assert "| random_forest | supportive | fixed |" in supportive
        assert "| naive | simple_baseline | not_tuned |" in baseline
        assert "| seasonal_naive | simple_baseline | not_tuned |" in baseline
        assert "| ridge |" not in primary and "| naive |" not in primary and "| naive |" not in supportive
        assert "mean_wape | mean_mae | mean_rmse | mean_bias" in primary
        assert "0.3141592653589793 | 2.75 | 3.125 | -0.5" in primary
        for fold_id in (1, 2, 3, 4):
            assert f"| {fold_id} | 0.0123456789012345 | 0.0123456789012345 | 0.0123456789012345 |" in primary
        assert "### Limitations and status" in section
        assert "Final evaluation remains blocked/not executed" in section
    assert "Primary model tie: XGBoost, LightGBM; no representative model is chosen." in text
    assert "XGBoost configuration ties: GBM001, GBM002; administrative representative: GBM001." in text
    assert "| xgboost | primary | GBM002 |" in text
    assert "| xgboost | GBM002 | 4 | 0.0123456789012345" in text
    assert "LightGBM configuration ties: none recorded." in text


def test_report_reads_artifacts_without_recalculation_or_changes(saved_evidence, monkeypatch):
    from src.forecasting import metrics, selection
    forbidden = Mock(side_effect=AssertionError("Report must not calculate scientific results"))
    monkeypatch.setattr(metrics, "forecasting_metrics", forbidden)
    monkeypatch.setattr(metrics, "four_fold_means", forbidden)
    monkeypatch.setattr(selection, "summarize_configurations", forbidden)
    monkeypatch.setattr(selection, "select_primary", forbidden)
    directory = saved_evidence.directory
    before = {path.name: path.read_bytes() for path in directory.iterdir()}
    text = reporting.comparison_text(directory, require_verified=False)
    assert {path.name: path.read_bytes() for path in directory.iterdir()} == before
    assert reporting.comparison_text(directory, require_verified=False) == text
    forbidden.assert_not_called()
    # Change a recorded display value, not a computed value: the report must follow the CSV.
    path = directory / "configuration_summary.csv"
    path.write_text(path.read_text().replace("0.3141592653589793", "0.8765432109876543"))
    assert "0.8765432109876543" in reporting.comparison_text(directory, require_verified=False)
    (directory / "selected_configurations.json").unlink()
    with pytest.raises(FileNotFoundError):
        reporting.comparison_text(directory, require_verified=False)


def test_report_failed_partial_scope_keeps_all_sections_and_unavailable_status(saved_evidence):
    directory = saved_evidence.directory
    metadata = json.loads((directory / "run_metadata.json").read_text())
    metadata.update(run_status="failed", failure_reason="Synthetic preflight failure")
    metadata["run_scope"].update(primary_models=["xgboost"], supportive_models=[], baselines=[], horizons=[1],
                                 baseline_exclusions=[["naive", "Synthetic explicit exclusion"]])
    metadata["tied_primary_models"] = {}
    saved_evidence.write_json("run_metadata.json", metadata)
    saved_evidence.write_json("selected_configurations.json", {"selections": []})
    saved_evidence.write_csv("configuration_summary.csv", [])
    saved_evidence.write_csv("fold_metrics.csv", [])
    text = reporting.comparison_text(directory, require_verified=False)
    assert "Run status at rendering: failed" in text and "Failure: Synthetic preflight failure" in text
    assert "Recorded fold IDs: none; not executed" in text
    assert "| 1-day | not selected | not authorised | not authorised |" in text
    assert "| 1-day | unavailable | unavailable | unavailable |" in text
    assert "| 7-day | not authorised | not authorised | not authorised |" in text
    for horizon in (1, 7, 14, 28):
        assert f"## {horizon}-day" in text
    assert text.count("This horizon was not authorised and was not executed.") == 3
    assert "Baseline exclusion — Naive: Synthetic explicit exclusion" in text
    assert "blocked_gate_6; blocked/not executed" in text


def test_cleanup_attempts_every_flush_and_close_and_reports_first_error(tmp_path):
    logger = progress.RunProgress(tmp_path, "cleanup", primary_fits=0, supportive_fits=0, baseline_evaluations=1)
    logger.close()
    handlers = [Mock(spec=logging.Handler), Mock(spec=logging.Handler)]
    original = OSError("flush failed")
    handlers[0].flush.side_effect = original
    handlers[0].close.side_effect = RuntimeError("close failed")
    for handler in handlers:
        logger.logger.addHandler(handler)
    with pytest.raises(OSError) as caught:
        logger.close()
    assert caught.value is original
    assert "Additional progress cleanup failure: RuntimeError." in original.__notes__
    assert logger.logger.handlers == []
    for handler in handlers:
        handler.flush.assert_called_once_with()
        handler.close.assert_called_once_with()


def test_cleanup_does_not_mask_active_primary_exception(tmp_path):
    logger = progress.RunProgress(tmp_path, "cleanup", primary_fits=0, supportive_fits=0, baseline_evaluations=1)
    logger.close()
    handler = Mock(spec=logging.Handler)
    handler.flush.side_effect = OSError("flush failed")
    handler.close.side_effect = RuntimeError("close failed")
    logger.logger.addHandler(handler)
    original = ValueError("primary failure")
    with pytest.raises(ValueError) as caught:
        try:
            raise original
        finally:
            logger.close()
    assert caught.value is original
    assert original.__notes__ == [
        "Progress handler cleanup failed: OSError.",
        "Progress handler cleanup failed: RuntimeError.",
    ]
    assert logger.logger.handlers == []
    handler.flush.assert_called_once_with()
    handler.close.assert_called_once_with()


@pytest.mark.parametrize("point", ["file_constructor", "formatter", "initial_event"])
def test_initialization_failure_closes_all_acquired_handlers_and_preserves_error(tmp_path, monkeypatch, point):
    terminal, file_handler = Mock(spec=logging.Handler), Mock(spec=logging.Handler)
    terminal.flush.side_effect = OSError("cleanup failure")
    original = RuntimeError("initialization failure")
    monkeypatch.setattr(progress.logging, "StreamHandler", Mock(return_value=terminal))
    factory = Mock(side_effect=original) if point == "file_constructor" else Mock(return_value=file_handler)
    monkeypatch.setattr(progress.logging, "FileHandler", factory)
    if point == "formatter":
        terminal.setFormatter.side_effect = original
    elif point == "initial_event":
        monkeypatch.setattr(progress.RunProgress, "_emit", Mock(side_effect=original))
    with pytest.raises(RuntimeError) as caught:
        progress.RunProgress(tmp_path, "setup", primary_fits=0, supportive_fits=0, baseline_evaluations=1)
    assert caught.value is original
    assert "Progress handler cleanup failed: OSError." in original.__notes__
    terminal.flush.assert_called_once_with()
    terminal.close.assert_called_once_with()
    if point != "file_constructor":
        file_handler.flush.assert_called_once_with()
        file_handler.close.assert_called_once_with()
