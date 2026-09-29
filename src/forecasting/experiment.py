"""Gate-protected sequential validation runner for the frozen Issue #65 contract.

No import-time execution. Gate 2 supplies capability, not Gate 3/4 acceptance.
Final fitting, preprocessing and evaluation deliberately have no implementation.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, cast

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from src.forecasting.artifacts import (
    SCHEMA_VERSION, ArtifactWriter,
)
from src.forecasting.baselines import BASELINE_FORMULAS, BASELINE_MODELS, baseline_predictions
from src.forecasting.configuration import (
    PRIMARY_GRID, PRIMARY_MODELS, SUPPORTIVE_MODELS, CanonicalConfiguration, ModelName,
    supportive_model_parameters,
)
from src.forecasting.evaluation import (
    PreparedFold, PreflightError, frame_hash, prepare_fold, require_native_roster, validation_view,
)
from src.forecasting.metadata import (
    REPOSITORY, ExecutionBlocked, RunScope, ValidationAuthorization, environment_metadata,
    initial_metadata,
)
from src.forecasting.metrics import METRIC_NAMES, forecasting_metrics
from src.forecasting.models import (
    construct_estimator, effective_iterations, effective_parameters, estimator_parameters, fit_estimator,
    parameter_metadata,
)
from src.forecasting.progress import RunProgress
from src.forecasting.reporting import comparison_text
from src.forecasting.selection import MODEL_ORDER, ROLES, record_order, select_primary, summarize_configurations
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
            "candidate_status": "running", "failure_reason": None,
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
                candidate_record.update(fitted)
                with threadpool_limits(limits=1):
                    predicted = np.asarray(estimator.predict(origin_matrix.copy()), dtype=float)
            else:
                predicted = baseline_predictions(fold.baseline_evidence, model, candidate.horizon)
            if predicted.shape != population.observed_targets.shape or not np.isfinite(predicted).all():
                raise ValueError("Prediction population is misaligned or nonfinite.")
            metrics = forecasting_metrics(population.observed_targets, predicted)
            if metrics["metric_status"] == "failed":
                raise ValueError(metrics["failure_reason"])
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
            progress.fail_candidate(exc)
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
            writer.write_json("diagnostics.json", {"candidate": candidate_record, "failure_reason": str(exc)})
            raise  # No automatic retry, replacement prediction or partial-fold comparison.
        # Checkpoint inside this run only, so interruption preserves completed evidence.
        if candidate.fold_id == 4:
            writer.write_json("run_metadata.json", metadata)


def _write_results(
    writer: ArtifactWriter, metadata: dict[str, Any], predictions: list[dict[str, Any]],
    scope: RunScope, *, allow_selection: bool,
) -> None:
    summaries = summarize_configurations(metadata["metric_records"])
    selections, ties = select_primary(summaries, metadata["candidate_records"]) if allow_selection else ([], {})
    by_key = {(r["model"], r["horizon"], r["configuration_id"]): r for r in summaries}
    for record in predictions:
        summary = by_key.get((record["model"], record["horizon"], record["configuration_id"]))
        if summary:
            record["selected_configuration"] = summary["selected_configuration"]
            record["selection_status"] = summary["selection_status"]
    metadata["selection_records"] = selections
    metadata["configuration_summary_records"] = summaries
    metadata["tied_primary_models"] = {str(h): models for h, models in ties.items()}
    writer.write_csv("fold_metrics.csv", metadata["metric_records"])
    writer.write_csv("configuration_summary.csv", summaries)
    writer.write_csv("predictions.csv", predictions)
    eligibility = []
    for record in metadata["eligibility_records"]:
        base = {key: record[key] for key in (
            "run_id", "evaluation_stage", "evidence_role", "model", "horizon", "fold_id", "SKU_ID",
            "Warehouse_ID", "raw_row_count", "feature_eligible_count", "label_eligible_count",
            "training_row_count", "expected_origin_count", "scored_origin_count", "overlapping_reasons")}
        for reason, count in record["exclusion_counts"].items():
            eligibility.append({**base, "exclusion_reason": reason, "reason_count": count})
    writer.write_csv("eligibility_counts.csv", eligibility)
    selected = {
        "run_id": metadata["run_id"], "schema_version": SCHEMA_VERSION, "selections": selections,
        "supportive_configurations": [{"model": model, "evidence_role": "supportive", "configuration_id": "fixed",
                                       "canonical_config_id": None, "selection_status": "fixed_supportive",
                                       "requested_api_parameters": estimator_parameters(cast(ModelName, model)),
                                       "fixed_parameters": supportive_model_parameters(model),  # type: ignore[arg-type]
                                       "execution_status": "in_scope" if model in scope.supportive_models else "not_executed"}
                                      for model in SUPPORTIVE_MODELS],
        "baseline_policies": [{"model": model, "evidence_role": "simple_baseline", "configuration_id": "not_tuned",
                               "formula_reference": BASELINE_FORMULAS[model], "approved_horizons": [1, 7, 14, 28],
                               "executed_horizons": sorted({r["horizon"] for r in metadata["metric_records"]
                                                            if r["model"] == model and r["n_predictions"] > 0}),
                               "approval_status": "formula_approved", "approval_reference": "docs/protocol.md Sections 10/18",
                               "run_approval_reference": dict(scope.baseline_approval_references).get(model),
                               "exclusion_reason": dict(scope.baseline_exclusions).get(model),
                               "execution_status": "in_scope" if model in scope.baselines else "not_executed"}
                              for model in BASELINE_MODELS],
    }
    writer.write_json("selected_configurations.json", selected)
    for key in ("candidate_records", "metric_records", "representation_records", "eligibility_records"):
        metadata[key].sort(key=record_order)
    # Persist the current status/selection before the renderer reads its evidence.
    writer.write_json("run_metadata.json", metadata)
    writer.write_comparison(comparison_text(writer.directory))
    metadata["artifact_manifest"] = writer.manifest()
    writer.write_json("run_metadata.json", metadata)


def run_validation(
    data: pd.DataFrame, *, run_id: str, authorization: ValidationAuthorization | None = None,
) -> Path:
    """Only a separately human-authorised, source/input-bound Gate 4 run may fit.

    No default approval or public synthetic bypass is provided. All four folds and
    all 24 configurations remain mandatory for every in-scope primary horizon.
    """
    if authorization is None:
        raise ExecutionBlocked("Gate 3 acceptance and explicit Gate 4 validation scope are required.")
    authorization.validate(REPOSITORY, run_id)
    scope = authorization.scope
    writer = ArtifactWriter(REPOSITORY, run_id)
    metadata = initial_metadata(authorization, REPOSITORY)
    writer.write_json("run_metadata.json", metadata)
    predictions: list[dict[str, Any]] = []
    progress = RunProgress(writer.directory, run_id,
                           primary_fits=sum(c.model in PRIMARY_MODELS for c in planned_candidates(scope)),
                           supportive_fits=sum(c.model in SUPPORTIVE_MODELS for c in planned_candidates(scope)),
                           baseline_evaluations=sum(c.model in BASELINE_MODELS for c in planned_candidates(scope)))
    try:
        metadata.update(environment_metadata(REPOSITORY))
        scoped = validation_view(data)
        if frame_hash(scoped) != authorization.input_view_hash:
            raise ExecutionBlocked("Validation input differs from the specifically authorised input view.")
        # Never derive a training roster from future categories.
        first_training = scoped.loc[scoped.Date.le(pd.Timestamp(VALIDATION_FOLDS[0].training.end))]
        require_native_roster(first_training)
        prepared = {fold.number: prepare_fold(scoped, fold.number, horizons=scope.horizons) for fold in VALIDATION_FOLDS}
        first_roster = prepared[1].pair_key_hash
        if any(fold.pair_key_hash != first_roster for fold in prepared.values()):
            raise PreflightError("Pair roster changed between frozen validation folds.")
        metadata["representation_records"] = _representation_records(prepared, scope)
        metadata["eligibility_records"] = _eligibility_records(prepared, scope, run_id)
        metadata["planned_primary_fits"] = sum(1 for c in planned_candidates(scope) if c.model in PRIMARY_MODELS)
        metadata["planned_supportive_fits"] = sum(1 for c in planned_candidates(scope) if c.model in SUPPORTIVE_MODELS)
        metadata["planned_baseline_evaluations"] = sum(1 for c in planned_candidates(scope) if c.model in BASELINE_MODELS)
        metadata["run_status"] = "running"
        writer.write_json("run_metadata.json", metadata)
        progress.operation = "preprocessing"
        _execute_candidates(prepared, scope, metadata, predictions, writer, progress)
        metadata["run_status"] = "completed" if all(r["metric_status"] == "valid" for r in metadata["metric_records"]) else "completed_with_unavailable_metrics"
        progress.operation = "artifact_reporting"
        _write_results(writer, metadata, predictions, scope, allow_selection=True)
        progress.complete_run(metadata["run_status"])
    except BaseException as exc:
        progress.fail_run(exc)
        metadata.update(run_status="failed", failure_reason=str(exc) or type(exc).__name__)
        diagnostic = {"failure_reason": metadata["failure_reason"],
                      "eligibility_diagnostics": exc.diagnostics if isinstance(exc, PreflightError) else []}
        if not (writer.directory / "diagnostics.json").exists():
            writer.write_json("diagnostics.json", diagnostic)
        _write_results(writer, metadata, predictions, scope, allow_selection=False)
        raise
    finally:
        progress.close()
    return writer.directory


def run_final_evaluation(*args: Any, **kwargs: Any) -> None:
    """No estimator/preprocessor refit or final-outcome access before Gate 6."""
    raise ExecutionBlocked("Final evaluation and final refit/preprocessing remain blocked for Gate 6.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--stage", default="validation")
    arguments = parser.parse_args(argv)
    if arguments.stage != "validation":
        run_final_evaluation()
    authorization = ValidationAuthorization.from_json(arguments.authorization)
    authorization.validate(REPOSITORY, arguments.run_id)  # BEFORE reading the dataset.
    data = pd.read_csv(arguments.input, usecols=["Date", "SKU_ID", "Warehouse_ID", "Units_Sold"],
                       dtype={"SKU_ID": str, "Warehouse_ID": str, "Units_Sold": object})
    run_validation(data, run_id=arguments.run_id, authorization=authorization)


if __name__ == "__main__":
    main()
