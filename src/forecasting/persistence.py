"""High-level run persistence; artifact schemas and model I/O stay in their owners."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, cast

import pandas as pd

from src.forecasting.artifacts import SCHEMA_VERSION, ArtifactWriter, file_hash
from src.forecasting.authorization import ExecutionBlocked, ExecutionContext, RunScope, ValidationAuthorization
from src.forecasting.baselines import BASELINE_FORMULAS, BASELINE_MODELS
from src.forecasting.configuration import SUPPORTIVE_MODELS, ModelName, supportive_model_parameters
from src.forecasting.integrity import build_manifest, verify_scientific
from src.forecasting.model_artifacts import persist_model
from src.forecasting.models import estimator_parameters
from src.forecasting.preprocessing import ForecastPreprocessor
from src.forecasting.reporting import comparison_text
from src.forecasting.selection import record_order, select_primary, summarize_configurations


def persist_authorization(
    writer: ArtifactWriter, authorization: ValidationAuthorization,
    execution_context: ExecutionContext | None,
) -> str:
    """Retain the reviewed snapshot; never generate or refresh human approval."""
    if execution_context is None:
        writer.write_json("authorization.json", asdict(authorization))
    else:
        if execution_context.authorization != authorization:
            raise ExecutionBlocked("Resolved execution context differs from authorization.")
        payload = execution_context.authorization_path.read_bytes()
        if sha256(payload).hexdigest() != execution_context.authorization_digest:
            raise ExecutionBlocked("Execution record changed after resolution.")
        temporary = writer.directory / "authorization.json.tmp"
        temporary.write_bytes(payload)
        temporary.replace(writer.directory / "authorization.json")
    return file_hash(writer.directory / "authorization.json")


def persist_checkpoint(writer: ArtifactWriter, metadata: dict[str, Any]) -> None:
    """Checkpoint this run through the existing atomic artifact writer."""
    writer.write_json("run_metadata.json", metadata)


def persist_candidate_model(
    writer: ArtifactWriter, estimator: Any, candidate: dict[str, Any],
    state: ForecastPreprocessor, origin_features: pd.DataFrame, metadata: dict[str, Any],
) -> None:
    """Delegate serialization and append its descriptor only after successful persistence."""
    record = persist_model(writer.directory, estimator, candidate, state, origin_features, metadata)
    metadata["model_artifacts"].append(record)


def write_results(
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
    persist_checkpoint(writer, metadata)
    if allow_selection:
        verify_scientific(writer.directory, include_report=False)
    writer.write_comparison(comparison_text(writer.directory, require_verified=False))
    metadata["artifact_manifest"] = writer.manifest()
    persist_checkpoint(writer, metadata)


def finalize_run(writer: ArtifactWriter, metadata: dict[str, Any], result: dict[str, Any]) -> None:
    """Publish verified final metadata followed by the completion manifest as the last write."""
    metadata.update(run_status="verified_completed", integrity_result=result,
                    completed_at_utc=datetime.now(timezone.utc).isoformat())
    persist_checkpoint(writer, metadata)
    manifest = build_manifest(writer.directory, metadata, result)
    writer.write_json("run_manifest.json", manifest)  # LAST mutation; consumers require this manifest.
