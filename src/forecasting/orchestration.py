"""Gate-protected sequential validation runner for the frozen Issue #65 contract.

No import-time execution. Gate 2 supplies capability, not Gate 3/4 acceptance.
Final fitting, preprocessing and evaluation deliberately have no implementation.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, cast

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from src.forecasting.artifacts import ArtifactWriter, file_hash
from src.forecasting.baselines import BASELINE_FORMULAS, BASELINE_MODELS, baseline_predictions
from src.forecasting.configuration import (
    PRIMARY_GRID, PRIMARY_MODELS, SUPPORTIVE_MODELS, CanonicalConfiguration, ModelName,
)
from src.forecasting.evaluation import (
    PreparedFold, PreflightError, frame_hash, prepare_fold, require_native_roster, validation_view,
)
from src.forecasting.authorization import ExecutionBlocked, ExecutionContext, RunScope, ValidationAuthorization
from src.forecasting.execution import load_dataset
from src.forecasting.integrity import plan_counts, verify_scientific
from src.forecasting.metadata import (
    environment_metadata,
    initial_metadata,
)
from src.forecasting.metrics import METRIC_NAMES, forecasting_metrics
from src.forecasting.models import (
    construct_estimator, effective_iterations, effective_parameters, estimator_parameters, fit_estimator,
    parameter_metadata,
)
from src.forecasting.paths import DEFAULT_LAYOUT, RepositoryLayout
from src.forecasting.persistence import (
    finalize_run, persist_authorization, persist_candidate_model, persist_checkpoint, write_results,
)
from src.forecasting.progress import RunProgress
from src.forecasting.selection import MODEL_ORDER, ROLES, summarize_configurations
from src.forecasting.validation import VALIDATION_FOLDS


@dataclass(frozen=True)
class Candidate:
    model: str
    horizon: int
    configuration: CanonicalConfiguration | None
    fold_id: int

    @property
    def configuration_id(self) -> str:
        if self.configuration:
            return self.configuration.canonical_config_id
        return "fixed" if self.model in SUPPORTIVE_MODELS else "not_tuned"


def planned_candidates(scope: RunScope) -> Iterator[Candidate]:
    """Declare an ordered plan only; no data access, estimators or experiments."""
    scope.validate()
    for model in MODEL_ORDER:
        if model not in (*scope.primary_models, *scope.supportive_models, *scope.baselines):
            continue
        for horizon in scope.horizons:
            configurations = PRIMARY_GRID if model in PRIMARY_MODELS else (None,)
            for configuration in configurations:
                for fold in VALIDATION_FOLDS:
                    yield Candidate(model, horizon, configuration, fold.number)


def _candidate_keys(run_id: str, candidate: Candidate) -> dict[str, Any]:
    return {"run_id": run_id, "evaluation_stage": "validation",
            "evidence_role": ROLES[candidate.model], "model": candidate.model,
            "horizon": candidate.horizon, "configuration_id": candidate.configuration_id,
            "canonical_config_id": candidate.configuration.canonical_config_id if candidate.configuration else None,
            "fold_id": candidate.fold_id}


def _temporal_keys(prepared: PreparedFold, horizon: int) -> dict[str, Any]:
    fold = prepared.fold
    return {"training_start": fold.training.start.isoformat(), "training_end": fold.training.end.isoformat(),
            "forecast_origin": fold.training.end.isoformat(), "target_start_date": fold.validation.start.isoformat(),
            "target_end_date": (pd.Timestamp(fold.training.end) + pd.Timedelta(days=horizon)).date().isoformat()}


def _representation_records(prepared: dict[int, PreparedFold], scope: RunScope) -> list[dict[str, Any]]:
    records = []
    for model in (*scope.primary_models, *scope.supportive_models):
        for horizon in scope.horizons:
            for fold_id, fold in prepared.items():
                population = fold.horizons[horizon]
                state = population.preprocessors[model]
                representation_id = f"validation-{model}-h{horizon}-f{fold_id}-{population.training_population_hash}"
                records.append({
                    "representation_id": representation_id, "model": model, "evidence_role": ROLES[model],
                    "evaluation_stage": "validation", "horizon": horizon, "fold_id": fold_id,
                    "physical_feature_names": state.physical_feature_names,
                    "physical_feature_count": state.physical_feature_count,
                    "conceptual_feature_names": state.conceptual_feature_names,
                    "numerical_feature_names": state.numerical_feature_names,
                    "categorical_feature_names": state.categorical_feature_names,
                    "category_vocabularies": state.category_vocabularies,
                    "category_mappings": state.category_mappings,
                    "training_row_count": state.training_row_count,
                    "training_population_hash": population.training_population_hash,
                    "shared_primary_vocabulary_id": f"primary-h{horizon}-f{fold_id}-{population.training_population_hash}"
                    if model in PRIMARY_MODELS else None,
                    "numerical_means": state.numerical_means if model == "ridge" else None,
                    "numerical_scales": state.numerical_scales if model == "ridge" else None,
                })
    return records


def _eligibility_records(prepared: dict[int, PreparedFold], scope: RunScope, run_id: str) -> list[dict[str, Any]]:
    records = []
    for model in MODEL_ORDER:
        if model not in (*scope.primary_models, *scope.supportive_models, *scope.baselines):
            continue
        for horizon in scope.horizons:
            for fold in prepared.values():
                for record in fold.horizons[horizon].eligibility_records:
                    records.append({"run_id": run_id, "evaluation_stage": "validation", "model": model,
                                    "evidence_role": ROLES[model], **record,
                                    "configuration_ids": [c.canonical_config_id for c in PRIMARY_GRID]
                                    if model in PRIMARY_MODELS else ["fixed" if model in SUPPORTIVE_MODELS else "not_tuned"]})
    return records


def _execute_candidates(
    prepared: dict[int, PreparedFold], scope: RunScope, metadata: dict[str, Any],
    predictions: list[dict[str, Any]], writer: ArtifactWriter, progress: RunProgress,
) -> None:
    """Private computation kernel; public entry checks approval and native coverage.

    Tests exercise this kernel with synthetic prepared folds and mocked estimators.
    Production has no injectable estimator, smaller grid or test-mode bypass.
    """
    representation_ids = {(r["model"], r["horizon"], r["fold_id"]): r["representation_id"]
                          for r in metadata["representation_records"]}
    matrices = {}
    for model in (*scope.primary_models, *scope.supportive_models):
        for horizon in scope.horizons:
            for fold_id, fold in prepared.items():
                population = fold.horizons[horizon]
                state = population.preprocessors[model]
                matrices[model, horizon, fold_id] = (state.transform(population.features).to_numpy(dtype=float),
                                                    state.transform(fold.origin_features).to_numpy(dtype=float))
    for candidate in planned_candidates(scope):
        fold = prepared[candidate.fold_id]
        population = fold.horizons[candidate.horizon]
        keys = _candidate_keys(metadata["run_id"], candidate)
        temporal = _temporal_keys(fold, candidate.horizon)
        model = cast(ModelName, candidate.model)
        learned = candidate.model not in BASELINE_MODELS
        requested = estimator_parameters(model, candidate.configuration) if learned else None
        candidate_record = {
            **keys, **temporal, "canonical_parameters": candidate.configuration.canonical_parameters
            if candidate.configuration else None,
            "requested_api_parameters": requested, "effective_api_parameters": None,
            "requested_iterations": candidate.configuration.boosting_iterations if candidate.configuration else (
                300 if model == "random_forest" else None), "effective_iterations": None,
            "random_seeds": metadata["random_seeds"].get(model, {}),
            "device": "CPU", "thread_count": 1, "worker_count": 1,
            "outcome_window_start": fold.fold.validation.start.isoformat(),
            "outcome_window_end": fold.fold.validation.end.isoformat(),
            "representation_id": representation_ids.get((model, candidate.horizon, candidate.fold_id)),
            "training_population_hash": population.training_population_hash,
            "pair_key_hash": fold.pair_key_hash, "input_view_hash": fold.input_view_hash,
            "candidate_status": "running", "fit_completed": False if learned else None, "failure_reason": None,
            "baseline_formula_reference": BASELINE_FORMULAS.get(model),
        }
        metadata["candidate_records"].append(candidate_record)
        estimator = None
        progress.start_candidate(keys, learned=learned)
        try:
            if learned:
                estimator = construct_estimator(model, candidate.configuration)
                # Failed fits still retain the requested API recipe/default declarations.
                candidate_record["effective_api_parameters"] = parameter_metadata(estimator.get_params(deep=True))
                train_matrix, origin_matrix = matrices[model, candidate.horizon, candidate.fold_id]
                # Copy shared arrays so a library cannot mutate another candidate's fitting evidence.
                fitted = fit_estimator(estimator, model, candidate.configuration,
                                       train_matrix.copy(), population.labels.copy())
                progress.complete_fit()
                candidate_record.update(fitted, fit_completed=True)
                with threadpool_limits(limits=1):
                    predicted = np.asarray(estimator.predict(origin_matrix.copy()), dtype=float)
            else:
                predicted = baseline_predictions(fold.baseline_evidence, model, candidate.horizon)
            if predicted.shape != population.observed_targets.shape or not np.isfinite(predicted).all():
                raise ValueError("Prediction population is misaligned or nonfinite.")
            metrics = forecasting_metrics(population.observed_targets, predicted)
            if metrics["metric_status"] == "failed":
                raise ValueError(metrics["failure_reason"])
            if learned:
                progress.operation = "model_persistence"
                persist_candidate_model(writer, estimator, candidate_record,
                                        population.preprocessors[model], fold.origin_features, metadata)
            metric_record = {**keys, **temporal, **metrics}
            metadata["metric_records"].append(metric_record)
            candidate_record.update(candidate_status="completed", metric_status=metrics["metric_status"])
            for pair, prediction, actual in zip(
                fold.origin_features.loc[:, ["SKU_ID", "Warehouse_ID"]].itertuples(index=False, name=None),
                predicted, population.observed_targets, strict=True,
            ):
                predictions.append({**keys, **temporal, "SKU_ID": pair[0], "Warehouse_ID": pair[1],
                                    "prediction": float(prediction), "observed_target": float(actual),
                                    "prediction_status": "available", "target_status": "complete",
                                    "eligibility_status": "eligible", "selected_configuration": False if model in PRIMARY_MODELS else None,
                                    "selection_status": "candidate" if model in PRIMARY_MODELS else (
                                        "fixed_supportive" if model in SUPPORTIVE_MODELS else "not_applicable"),
                                    "representation_id": candidate_record["representation_id"]})
            for record in metadata["eligibility_records"]:
                if record["model"] == model and record["horizon"] == candidate.horizon and record["fold_id"] == candidate.fold_id:
                    record["scored_origin_count"] = 1
            progress.complete_candidate(learned=learned)
        except Exception as exc:
            try:
                progress.fail_candidate(exc)
            except BaseException as logging_error:
                exc.add_note(f"Candidate failure logging failed: {type(logging_error).__name__}.")
            candidate_record.update(candidate_status="failed", metric_status="failed", failure_reason=str(exc))
            if estimator is not None:
                try:
                    candidate_record["effective_iterations"] = effective_iterations(estimator, model)
                    candidate_record["effective_api_parameters"] = effective_parameters(estimator, model)
                except Exception:
                    candidate_record["effective_parameter_status"] = "unavailable_after_failed_fit"
            metadata["metric_records"].append({
                **keys, **temporal, "n_predictions": 0, **dict.fromkeys(METRIC_NAMES),
                "wape_denominator": None, "metric_status": "failed", "failure_reason": str(exc),
            })
            try:
                writer.write_json("diagnostics.json", {"candidate": candidate_record, "failure_reason": str(exc)})
            except BaseException as recovery_error:
                exc.add_note(f"Candidate diagnostic persistence failed: {type(recovery_error).__name__}.")
            raise  # No automatic retry, replacement prediction or partial-fold comparison.
        # Checkpoint inside this run only, so interruption preserves completed evidence.
        if candidate.fold_id == 4:
            persist_checkpoint(writer, metadata)


def run_validation(
    data: pd.DataFrame, *, run_id: str, authorization: ValidationAuthorization | None = None,
    execution_context: ExecutionContext | None = None, layout: RepositoryLayout | None = None,
) -> Path:
    """Run only the exact human-authorised validation scope; completion is manifest-last."""
    if authorization is None:
        raise ExecutionBlocked("Gate 3 acceptance and explicit Gate 4 validation scope are required.")
    layout = layout if layout is not None else (execution_context.layout if execution_context else DEFAULT_LAYOUT)
    if execution_context is not None and execution_context.layout != layout:
        raise ExecutionBlocked("Execution context and supplied repository layout differ.")
    authorization.validate(layout.root, run_id)
    scope = authorization.scope
    writer = ArtifactWriter(layout, run_id)
    metadata = initial_metadata(authorization, layout.root)
    metadata.update(expected_counts=plan_counts(scope), completed_counts={}, model_artifacts=[],
                    integrity_result=None, completed_at_utc=None, failed_at_utc=None,
                    authorization_digest=None, dataset_reference=layout.dataset.relative_to(layout.root).as_posix())
    predictions: list[dict[str, Any]] = []
    progress: RunProgress | None = None
    try:
        persist_checkpoint(writer, metadata)
        metadata["authorization_digest"] = persist_authorization(writer, authorization, execution_context)
        progress = RunProgress(writer.directory, run_id,
                               primary_fits=metadata["expected_counts"]["primary_fits"],
                               supportive_fits=metadata["expected_counts"]["supportive_fits"],
                               baseline_evaluations=metadata["expected_counts"]["baseline_evaluations"])
        progress.phase("runtime_preflight")
        metadata.update(environment_metadata(layout.root))
        progress.phase("input_preflight")
        scoped = validation_view(data)
        if frame_hash(scoped) != authorization.input_view_hash:
            raise ExecutionBlocked("Validation input differs from the specifically authorised input view.")
        first_training = scoped.loc[scoped.Date.le(pd.Timestamp(VALIDATION_FOLDS[0].training.end))]
        require_native_roster(first_training)
        progress.phase("fold_preflight")
        prepared = {fold.number: prepare_fold(scoped, fold.number, horizons=scope.horizons) for fold in VALIDATION_FOLDS}
        first_roster = prepared[1].pair_key_hash
        if any(fold.pair_key_hash != first_roster for fold in prepared.values()):
            raise PreflightError("Pair roster changed between frozen validation folds.")
        metadata["expected_pair_count"] = len(prepared[1].origin_features)
        metadata["representation_records"] = _representation_records(prepared, scope)
        metadata["eligibility_records"] = _eligibility_records(prepared, scope, run_id)
        metadata["planned_primary_fits"] = metadata["expected_counts"]["primary_fits"]
        metadata["planned_supportive_fits"] = metadata["expected_counts"]["supportive_fits"]
        metadata["planned_baseline_evaluations"] = metadata["expected_counts"]["baseline_evaluations"]
        metadata["run_status"] = "running"
        persist_checkpoint(writer, metadata)
        progress.phase("preprocessing")
        _execute_candidates(prepared, scope, metadata, predictions, writer, progress)
        metadata["run_status"] = "finalizing"
        counts = {"primary_fits": sum(r["model"] in PRIMARY_MODELS and r["candidate_status"] == "completed" for r in metadata["candidate_records"]),
                  "supportive_fits": sum(r["model"] in SUPPORTIVE_MODELS and r["candidate_status"] == "completed" for r in metadata["candidate_records"]),
                  "baseline_evaluations": sum(r["model"] in BASELINE_MODELS and r["candidate_status"] == "completed" for r in metadata["candidate_records"]),
                  "total_evaluations": len(metadata["metric_records"]),
                  "configuration_summaries": len(summarize_configurations(metadata["metric_records"]))}
        metadata["completed_counts"] = counts
        metadata["metric_availability"] = "all_valid" if all(r["metric_status"] == "valid" for r in metadata["metric_records"]) else "unavailable_metrics_present"
        progress.phase("artifact_reporting")
        write_results(writer, metadata, predictions, scope, allow_selection=True)
        progress.phase("integrity_verification")
        result = verify_scientific(writer.directory)
        authorization.validate(layout.root, run_id)
        current_data = load_dataset(execution_context.dataset_path) if execution_context else data
        if frame_hash(validation_view(current_data)) != authorization.input_view_hash:
            raise ExecutionBlocked("Validation input changed during execution.")
        if execution_context and file_hash(execution_context.authorization_path) != execution_context.authorization_digest:
            raise ExecutionBlocked("Execution record changed during execution.")
        # No completion claim in the log before the final manifest exists.
        progress.complete_run("finalizing_verified")
        progress.close()
        progress = None
        finalize_run(writer, metadata, result)
    except BaseException as exc:
        metadata.update(run_status="interrupted" if isinstance(exc, (KeyboardInterrupt, SystemExit)) else "failed",
                        failure_reason=str(exc) or type(exc).__name__, failure_type=type(exc).__name__,
                        failed_at_utc=datetime.now(timezone.utc).isoformat(), completed_at_utc=None,
                        integrity_result=None, selection_records=[])
        for record in metadata["candidate_records"]:
            if record["candidate_status"] == "running":
                record.update(candidate_status=metadata["run_status"], failure_reason=type(exc).__name__)
        original_error = exc
        metadata["completed_counts"] = {
            "primary_fits": sum(r["model"] in PRIMARY_MODELS and r.get("fit_completed") is True for r in metadata["candidate_records"]),
            "supportive_fits": sum(r["model"] in SUPPORTIVE_MODELS and r.get("fit_completed") is True for r in metadata["candidate_records"]),
            "baseline_evaluations": sum(r["model"] in BASELINE_MODELS and r["candidate_status"] == "completed" for r in metadata["candidate_records"]),
            "total_evaluations": sum(r["candidate_status"] == "completed" for r in metadata["candidate_records"]),
        }
        # Recovery steps are independent and best effort: never hide the original exception.
        def recover(action: Any) -> None:
            try:
                action()
            except BaseException as secondary:
                original_error.add_note(f"Recovery failed: {type(secondary).__name__}.")
        if progress is not None:
            recover(lambda: progress.fail_run(original_error))
        recover(lambda: persist_checkpoint(writer, metadata))
        recover(lambda: writer.write_json("diagnostics.json", {
            "failure_type": type(original_error).__name__, "failure_reason": metadata["failure_reason"],
            "eligibility_diagnostics": original_error.diagnostics if isinstance(original_error, PreflightError) else []}))
        recover(lambda: write_results(writer, metadata, predictions, scope, allow_selection=False))
        raise
    finally:
        if progress is not None:
            try:
                progress.close()
            except BaseException:
                # Successful finalization closes explicitly above; this is failure cleanup only.
                pass
    return writer.directory


def run_final_evaluation(*args: Any, **kwargs: Any) -> None:
    """No estimator/preprocessor refit or final-outcome access before Gate 6."""
    raise ExecutionBlocked("Final evaluation and final refit/preprocessing remain blocked for Gate 6.")
