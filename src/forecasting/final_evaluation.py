"""Separate human-authorized final evaluation; imports never execute a run.

All origin predictions are persisted, hashed and verified before the only
reserved-outcome loading call. Synthetic tests use mocks, never project outcomes.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from src.data.validated_handoff import PROJECT_DATA_VERSION, read_validated_projection
from src.forecasting.artifacts import file_hash
from src.forecasting.authorization import ExecutionBlocked
from src.forecasting.baselines import BASELINE_FORMULAS, baseline_history, baseline_predictions
from src.forecasting.configuration import PRIMARY_MODELS, SUPPORTIVE_MODELS, ModelName
from src.forecasting.evaluation import PreflightError, frame_hash, require_native_roster
from src.forecasting.features import (
    KEY_COLUMNS, SERIES_COLUMNS, TARGET_COLUMN, build_features, build_origin_features,
    feature_eligibility, prepare_demand,
)
from src.forecasting.final_artifacts import (
    FinalArtifactWriter, candidate_keys, finalize_final_run, verify_sealed_predictions,
)
from src.forecasting.final_authorization import (
    FINAL_SCHEMA, FREEZE_PATH, POLICY_PATH, TRAINING_END, TRAINING_START,
    FinalExecutionContext, candidate_payload, resolve_final_execution,
)
from src.forecasting.metadata import environment_metadata
from src.forecasting.metrics import forecasting_metrics
from src.forecasting.models import construct_estimator, fit_estimator
from src.forecasting.paths import DEFAULT_LAYOUT, RepositoryLayout
from src.forecasting.preprocessing import ForecastPreprocessor, fit_preprocessor, fit_primary_preprocessors
from src.forecasting.targets import FORECAST_HORIZONS, build_horizon_targets
from src.forecasting.validation import FINAL_HOLDOUT

PROJECTION_COLUMNS = (*KEY_COLUMNS, TARGET_COLUMN)


@dataclass(frozen=True)
class FinalPopulation:
    features: pd.DataFrame
    labels: np.ndarray
    preprocessors: dict[str, ForecastPreprocessor]
    training_population_hash: str


@dataclass(frozen=True)
class PreparedFinal:
    origin: pd.DataFrame
    baseline_evidence: pd.DataFrame
    populations: dict[int, FinalPopulation]
    eligibility: list[dict[str, Any]]


def prepare_final_training(data: pd.DataFrame) -> PreparedFinal:
    """Pure historical preparation; no estimator or reserved outcome is needed."""
    if not data.columns.is_unique or set(PROJECTION_COLUMNS) - set(data.columns):
        raise PreflightError("Final training needs the four unique native projection columns.")
    dates = pd.to_datetime(data.Date, format="%Y-%m-%d", errors="raise")
    if (dates.isna().any() or dates.dt.tz is not None or dates.ne(dates.dt.normalize()).any()
            or not dates.between(TRAINING_START, TRAINING_END).all()):
        raise ExecutionBlocked("Only historical training dates through December 2 may enter final preparation.")
    history = prepare_demand(data)
    roster = history.loc[:, list(SERIES_COLUMNS)].drop_duplicates().reset_index(drop=True)
    expected_days = (pd.Timestamp(TRAINING_END) - pd.Timestamp(TRAINING_START)).days + 1
    if roster.empty or not history.groupby(list(SERIES_COLUMNS), observed=True).Date.nunique().eq(expected_days).all():
        raise PreflightError("Incomplete final historical calendar coverage.")
    origin = build_origin_features(history, origin=TRAINING_END)
    if not origin.loc[:, list(SERIES_COLUMNS)].equals(roster) or not feature_eligibility(origin).all():
        raise PreflightError("Incomplete fixed-origin predictor population.")
    baseline = baseline_history(history, origin=TRAINING_END)
    features = build_features(history)
    targets = build_horizon_targets(history, window_start=TRAINING_START, window_end=TRAINING_END)
    aligned = features.loc[:, list(KEY_COLUMNS)].merge(targets, on=list(KEY_COLUMNS),
                                                       how="left", validate="one_to_one", sort=False)
    feature_mask = feature_eligibility(features)
    populations: dict[int, FinalPopulation] = {}
    eligibility = []
    for h in FORECAST_HORIZONS:
        column = f"target_{h}_day"
        boundary = (aligned.Date + pd.Timedelta(days=h - 1)).le(pd.Timestamp(TRAINING_END))
        label_mask = boundary & aligned[column].notna()
        accepted = feature_mask & label_mask
        training = features.loc[accepted].reset_index(drop=True)
        labels = aligned.loc[accepted, column].to_numpy(dtype=float)
        if training.empty:
            raise PreflightError("No eligible final labelled training population.")
        states: dict[str, ForecastPreprocessor] = {model: state for model, state in
            fit_primary_preprocessors(training, training_end=TRAINING_END, horizon=h).items()}
        for supportive_model in SUPPORTIVE_MODELS:
            states[supportive_model] = fit_preprocessor(training, supportive_model, training_end=TRAINING_END, horizon=h)
        reference = states[PRIMARY_MODELS[0]].transform(origin)
        for model, state in states.items():
            if state.training_row_count != len(training):
                raise PreflightError("Final preprocessing changed the labelled fitting population.")
            transformed = state.transform(origin)  # Unknown identities fail before any model fit.
            if model in PRIMARY_MODELS:
                pd.testing.assert_frame_equal(reference, transformed)
        population = training.loc[:, list(KEY_COLUMNS)].copy()
        population[column] = labels
        digest = frame_hash(population)
        per_pair = []
        for pair in roster.itertuples(index=False, name=None):
            mask = aligned.SKU_ID.eq(pair[0]) & aligned.Warehouse_ID.eq(pair[1])
            per_pair.append({
                "SKU_ID": pair[0], "Warehouse_ID": pair[1], "raw_row_count": int(mask.sum()),
                "feature_eligible_count": int((mask & feature_mask).sum()),
                "label_eligible_count": int((mask & label_mask).sum()),
                "training_row_count": int((mask & accepted).sum()),
                "exclusion_counts": {
                    "incomplete_predictor_history": int((mask & ~feature_mask).sum()),
                    "target_after_training_cutoff": int((mask & ~boundary).sum()),
                    "missing_observed_training_target": int((mask & boundary & aligned[column].isna()).sum()),
                },
            })
        eligibility.append({"horizon": h, "training_row_count": len(training),
                            "training_population_hash": digest, "per_pair": per_pair})
        populations[h] = FinalPopulation(training, labels, states, digest)
    return PreparedFinal(origin, baseline, populations, eligibility)


def read_final_history(context: FinalExecutionContext) -> pd.DataFrame:
    projection = read_validated_projection(
        repository=context.layout.root, data_version=PROJECT_DATA_VERSION, columns=PROJECTION_COLUMNS,
        start=TRAINING_START, end=TRAINING_END,
        expected_provenance_sha256=context.authorization.validated_provenance_hash,
    )
    if frame_hash(projection.frame) != context.authorization.input_view_hash:
        raise ExecutionBlocked("Historical final training differs from its authorized fingerprint.")
    return projection.frame


def read_reserved_outcomes(context: FinalExecutionContext, directory: Path, receipt_hash: str) -> pd.DataFrame:
    """The only real outcome-read path checks authority and sealed evidence first."""
    context.revalidate()
    if directory != context.layout.run_directory(context.authorization.run_id):
        raise ExecutionBlocked("Prediction receipt does not belong to the authorized final run.")
    verify_sealed_predictions(directory, receipt_hash)
    return read_validated_projection(
        repository=context.layout.root, data_version=PROJECT_DATA_VERSION, columns=PROJECTION_COLUMNS,
        start=FINAL_HOLDOUT.start.isoformat(), end=FINAL_HOLDOUT.end.isoformat(),
        expected_provenance_sha256=context.authorization.validated_provenance_hash,
    ).frame


def align_final_observations(outcomes: pd.DataFrame, origin: pd.DataFrame) -> list[dict[str, Any]]:
    """Used only after reveal; direct horizon totals are separate from predictors."""
    frame = prepare_demand(outcomes)
    if not frame.Date.between(pd.Timestamp(FINAL_HOLDOUT.start), pd.Timestamp(FINAL_HOLDOUT.end)).all():
        raise PreflightError("Final outcomes must use the exact reserved interval.")
    roster = origin.loc[:, list(SERIES_COLUMNS)]
    outcome_roster = frame.loc[:, list(SERIES_COLUMNS)].drop_duplicates().reset_index(drop=True)
    counts = frame.groupby(list(SERIES_COLUMNS), observed=True).Date.nunique()
    if (not outcome_roster.equals(roster) or not counts.eq(28).all() or frame.Units_Sold.isna().any()):
        raise PreflightError("Incomplete final outcome coverage or changed historical pair roster.")
    targets = build_horizon_targets(frame, window_start=FINAL_HOLDOUT.start, window_end=FINAL_HOLDOUT.end)
    aligned = origin.loc[:, list(KEY_COLUMNS)].merge(targets, on=list(KEY_COLUMNS),
                                                    how="left", validate="one_to_one", sort=False)
    if aligned[[f"target_{h}_day" for h in FORECAST_HORIZONS]].isna().any().any():
        raise PreflightError("Incomplete final horizon targets.")
    return [{"horizon": h, "SKU_ID": r.SKU_ID, "Warehouse_ID": r.Warehouse_ID,
             "observed_target": float(getattr(r, f"target_{h}_day"))}
            for h in FORECAST_HORIZONS for r in aligned.itertuples(index=False)]


def run_final_evaluation(layout: RepositoryLayout = DEFAULT_LAYOUT) -> Path:
    """Resolve an existing human record; no public data/test-mode/estimator injection."""
    context = resolve_final_execution(layout)
    authorization = context.authorization
    writer = FinalArtifactWriter(layout, authorization.run_id)
    metadata = {
        **asdict(authorization), "scope": candidate_payload(authorization.candidates),
        "schema_version": FINAL_SCHEMA, "run_status": "preflight",
        "authorization_hash": file_hash(context.authorization_path),
        "created_at_utc": datetime.now(timezone.utc).isoformat(), "completed_at_utc": None,
        "integrity_result": None, "prediction_receipt_hash": None, "pair_roster": [],
    }
    predictions: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    operation, active = "initialization", None
    try:
        writer.write_text("authorization.json", context.authorization_bytes.decode("utf-8"))
        writer.write_text("freeze.md", layout.repository_path(FREEZE_PATH).read_bytes().decode("utf-8"))
        writer.write_text("policy.md", layout.repository_path(POLICY_PATH).read_bytes().decode("utf-8"))
        writer.write_json("run_metadata.json", metadata)
        operation = "runtime_preflight"
        writer.event(operation)
        runtime = environment_metadata(layout.root)
        if runtime["source_hashes"] != authorization.source_hashes or runtime["library_versions"] != authorization.library_versions:
            raise ExecutionBlocked("Final runtime provenance differs from authorization.")
        metadata["runtime"] = runtime
        operation = "historical_preparation"
        writer.event(operation)
        history = read_final_history(context)
        require_native_roster(history)
        prepared = prepare_final_training(history)
        metadata["pair_roster"] = prepared.origin.loc[:, list(SERIES_COLUMNS)].to_numpy().tolist()
        metadata["run_status"] = "running"
        writer.write_json("run_metadata.json", metadata)
        fitted: dict[tuple[str, int, str], Any] = {}
        for candidate in authorization.candidates:
            active = asdict(candidate)
            keys = candidate_keys(authorization.run_id, candidate)
            population = prepared.populations[candidate.horizon]
            record = {
                **keys, "candidate_status": "running", "fit": None, "model_artifact": None,
                "training_row_count": len(population.features),
                "training_population_hash": population.training_population_hash,
                "baseline_formula": BASELINE_FORMULAS.get(candidate.model),
            }
            candidates.append(record)
            if candidate.learned:
                operation = "fresh_estimator_fit"
                writer.event(operation, candidate=active)
                model = cast(ModelName, candidate.model)
                estimator = construct_estimator(model, candidate.configuration)
                state = population.preprocessors[model]
                matrix = state.transform(population.features).to_numpy(dtype=float)
                record["fit"] = fit_estimator(estimator, model, candidate.configuration, matrix.copy(), population.labels.copy())
                fitted[candidate.key] = estimator
        for candidate, record in zip(authorization.candidates, candidates, strict=True):
            active = asdict(candidate)
            keys = candidate_keys(authorization.run_id, candidate)
            population = prepared.populations[candidate.horizon]
            if candidate.learned:
                estimator = fitted[candidate.key]
                state = population.preprocessors[candidate.model]
                origin_matrix = state.transform(prepared.origin).to_numpy(dtype=float)
                operation = "origin_prediction"
                with threadpool_limits(limits=1):
                    predicted = np.asarray(estimator.predict(origin_matrix.copy()), dtype=float)
                if predicted.shape != (len(prepared.origin),) or not np.isfinite(predicted).all():
                    raise PreflightError("Prediction population is misaligned or nonfinite.")
                operation = "model_persistence"
                record["model_artifact"] = writer.persist_model(estimator, candidate, record, state, prepared.origin, metadata)
            else:
                operation = "baseline_prediction"
                predicted = baseline_predictions(prepared.baseline_evidence, candidate.model, candidate.horizon)
            record["candidate_status"] = "completed"
            for pair, prediction in zip(metadata["pair_roster"], predicted, strict=True):
                predictions.append({**keys, "SKU_ID": pair[0], "Warehouse_ID": pair[1], "prediction": float(prediction)})
            writer.event("prediction_complete", candidate=active)
        active = None
        operation = "prediction_persistence"
        receipt_hash = writer.seal(predictions, candidates, prepared.baseline_evidence, prepared.eligibility)
        metadata["prediction_receipt_hash"] = receipt_hash
        writer.write_json("run_metadata.json", metadata)
        writer.event("all_predictions_verified", prediction_count=len(predictions), receipt_hash=receipt_hash)
        context.revalidate()
        if frame_hash(read_final_history(context)) != authorization.input_view_hash:
            raise ExecutionBlocked("Historical final training changed during fitting.")
        operation = "reserved_outcome_read"
        outcomes = read_reserved_outcomes(context, writer.directory, receipt_hash)
        operation = "final_scoring"
        sealed_rows = verify_sealed_predictions(writer.directory, receipt_hash)
        observations = align_final_observations(outcomes, prepared.origin)
        actuals = {(r["horizon"], r["SKU_ID"], r["Warehouse_ID"]): r["observed_target"] for r in observations}
        metrics = []
        for candidate in authorization.candidates:
            rows = [r for r in sealed_rows if (r["model"], r["horizon"], r["configuration_id"]) == candidate.key]
            values = forecasting_metrics([actuals[candidate.horizon, r["SKU_ID"], r["Warehouse_ID"]] for r in rows],
                                         [r["prediction"] for r in rows])
            if values["metric_status"] == "failed":
                raise PreflightError(values["failure_reason"])
            metrics.append({**candidate_keys(authorization.run_id, candidate), **values})
        writer.write_json("observations.json", observations)
        writer.write_json("metrics.json", metrics)
        operation = "final_verification"
        context.revalidate()
        finalize_final_run(writer, metadata, before_publish=context.revalidate)
        return writer.directory
    except BaseException as exc:
        metadata.update(run_status="interrupted" if isinstance(exc, (KeyboardInterrupt, SystemExit)) else "failed",
                        failed_at_utc=datetime.now(timezone.utc).isoformat())
        original_error = exc
        recovery = [
            lambda: writer.write_json("run_metadata.json", metadata),
            lambda: writer.write_json("diagnostics.json", {
                "operation": operation, "candidate": active, "exception_type": type(original_error).__name__,
                "failure_reason": str(original_error), "completed_predictions": len(predictions),
            }),
            lambda: writer.event("run_failure", failed_operation=operation, exception_type=type(original_error).__name__),
        ]
        try:
            if not writer.path("prediction_receipt.json").exists():
                recovery.extend([lambda: writer.write_json("predictions.json", predictions),
                                 lambda: writer.write_json("candidates.json", candidates)])
        except BaseException as secondary:
            exc.add_note(f"Final failure recovery failed: {type(secondary).__name__}.")
        for action in recovery:
            try:
                action()
            except BaseException as secondary:
                exc.add_note(f"Final failure recovery failed: {type(secondary).__name__}.")
        raise


def main() -> None:
    run_final_evaluation()


if __name__ == "__main__":
    main()
