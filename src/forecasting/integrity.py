"""Readback validation of scientific evidence and immutable completion manifests."""
from __future__ import annotations

from collections import defaultdict
import csv
from datetime import timedelta
import json
from pathlib import Path
from pickle import UnpicklingError
from typing import Any

import numpy as np
from catboost import CatBoostError
from lightgbm.basic import LightGBMError
from xgboost.core import XGBoostError

from src.forecasting.artifacts import ARTIFACT_NAMES, CSV_SCHEMAS, PROTOCOL_VERSION, SCHEMA_VERSION, file_hash, json_value
from src.forecasting.baselines import BASELINE_MODELS
from src.forecasting.configuration import PRIMARY_GRID, PRIMARY_MODELS, SUPPORTIVE_MODELS
from src.forecasting.authorization import RunScope, ValidationAuthorization
from src.forecasting.metrics import forecasting_metrics
from src.forecasting.model_artifacts import FORMATS, replay_model, safe_path
from src.forecasting.paths import RepositoryLayout
from src.forecasting.selection import ROLES, select_primary, summarize_configurations
from src.forecasting.validation import VALIDATION_FOLDS

MANIFEST_VERSION = 2
KEY = ("model", "horizon", "configuration_id", "fold_id")
INTS = {"horizon", "fold_id", "n_predictions", "expected_fold_count", "valid_fold_count",
        "raw_row_count", "feature_eligible_count", "label_eligible_count", "training_row_count",
        "expected_origin_count", "scored_origin_count", "reason_count"}
FLOATS = {"wape", "mae", "rmse", "bias", "wape_denominator", "mean_wape", "mean_mae", "mean_rmse", "mean_bias", "prediction", "observed_target"}


class IntegrityError(ValueError):
    """Evidence must not be consumed as completed research output."""


def _owner_directories(directory: Path) -> dict[str, Path]:
    layout = RepositoryLayout.from_artifact_directory(directory)
    return {"artifacts": layout.run_directory(directory.name),
            "models": layout.model_run_directory(directory.name),
            "reports": layout.draft_report_directory(directory.name)}


def _evidence_path(directory: Path, owner: str, relative: str) -> Path:
    """Resolve only normalized repository references within the declared run owner."""
    layout = RepositoryLayout.from_artifact_directory(directory)
    reference = Path(relative)
    if (reference.is_absolute() or ".." in reference.parts or "\\" in relative
            or reference.as_posix() != relative):
        raise IntegrityError("Evidence reference escapes its declared run owner.")
    roots = _owner_directories(directory)
    if owner not in roots:
        raise IntegrityError("Unknown evidence owner.")
    path = layout._owned_path(layout.repository_path(relative))
    if not path.is_relative_to(roots[owner]):
        raise IntegrityError("Evidence reference escapes its declared run owner.")
    if owner == "artifacts" and (path.parent != directory or path.name not in (
            *(name for name in ARTIFACT_NAMES if name != "comparison.md"),
            "authorization.json", "run.log", "diagnostics.json")):
        raise IntegrityError("Reference is not a declared machine-readable artifact.")
    if owner == "reports" and path != roots[owner] / "comparison.md":
        raise IntegrityError("Reference is not the run's draft comparison.")
    return path


def _model_files(directory: Path, record: dict[str, Any]) -> list[Path]:
    """Bind every model reference to its exact candidate or shared fold state."""
    layout = RepositoryLayout.from_artifact_directory(directory)
    if record["run_id"] != directory.name or record["evaluation_stage"] != "validation":
        raise IntegrityError("Model identity differs from the artifact run.")
    folder = layout.candidate_model_directory(
        directory, record["model"], record["horizon"], record["configuration_id"], record["fold_id"])
    state = layout.preprocessing_state_directory(directory, record["model"], record["horizon"], record["fold_id"])
    expected = {"model": folder / f"model.{FORMATS[record['model']]}",
                "descriptor": folder / "descriptor.json",
                "preprocessor": state / "state.json", "origin_features": state / "origin_features.json"}
    for key, path in expected.items():
        if safe_path(directory, record[f"{key}_path"]) != path:
            raise IntegrityError("Model reference differs from its candidate/fold owner.")
    return list(expected.values())


def _run_files(directory: Path, metadata: dict[str, Any], *, include_report: bool = True) -> dict[Path, str]:
    """Inventory exactly the run-owned files; reject redirects, extras and leftovers."""
    layout = RepositoryLayout.from_artifact_directory(directory)
    if metadata["run_id"] != directory.name:
        raise IntegrityError("Run identity differs from the artifact anchor.")
    roots = _owner_directories(directory)
    expected = {directory / name: "artifacts" for name in ARTIFACT_NAMES if name != "comparison.md"}
    expected.update({directory / "authorization.json": "artifacts", directory / "run.log": "artifacts"})
    diagnostics = layout._owned_path(directory / "diagnostics.json")
    if diagnostics.exists():
        expected[diagnostics] = "artifacts"
    report = layout._owned_path(roots["reports"] / "comparison.md")
    if include_report or report.exists():
        expected[report] = "reports"
    for record in metadata["model_artifacts"]:
        expected.update({path: "models" for path in _model_files(directory, record)})
    allowed_directories = set(roots.values())
    for path, owner in expected.items():
        for parent in path.parents:
            allowed_directories.add(parent)
            if parent == roots[owner]:
                break
    files = {}
    for owner, root in roots.items():
        if not root.is_dir():
            raise IntegrityError("Required run-owned directory is missing or invalid.")
        pending = [root]
        while pending:
            for path in sorted(pending.pop().iterdir()):
                path = layout._owned_path(path)
                if path.name.endswith(".tmp") or ".tmp." in path.name:
                    raise IntegrityError("Unfinished temporary artifacts remain.")
                if path.is_dir():
                    if path not in allowed_directories:
                        raise IntegrityError("Unexpected run-owned directory.")
                    pending.append(path)
                elif path.is_file():
                    if path != directory / "run_manifest.json":
                        files[path] = owner
                else:
                    raise IntegrityError("Run-owned evidence must be regular files.")
    if files != expected:
        raise IntegrityError("Run-owned file set differs from declared evidence.")
    return files


def _verify_artifact_receipts(directory: Path, metadata: dict[str, Any]) -> None:
    layout = RepositoryLayout.from_artifact_directory(directory)
    roots = _owner_directories(directory)
    diagnostics = directory / "diagnostics.json"
    expected = {}
    for name in ARTIFACT_NAMES:
        path = (roots["reports"] if name == "comparison.md" else directory) / name
        relative = path.relative_to(layout.root).as_posix()
        expected[relative] = {"artifact_path": relative,
                             "artifact_hash": None if name == "run_metadata.json" else file_hash(path),
                             "artifact_status": "self_reference" if name == "run_metadata.json" else "written",
                             "diagnostic_paths": [diagnostics.relative_to(layout.root).as_posix()] if diagnostics.exists() else []}
    actual = {key[0]: value for key, value in _index(metadata["artifact_manifest"], ("artifact_path",)).items()}
    if actual != expected:
        raise IntegrityError("Artifact receipts differ from run-owned evidence.")


def scope_from_metadata(metadata: dict[str, Any]) -> RunScope:
    value = metadata["run_scope"]
    scope = RunScope(tuple(value["primary_models"]), tuple(value["supportive_models"]),
                     tuple(value["horizons"]), tuple(value["baselines"]),
                     tuple(tuple(pair) for pair in value["baseline_exclusions"]),
                     tuple(tuple(pair) for pair in value["baseline_approval_references"]))
    scope.validate()
    return scope


def expected_keys(scope: RunScope) -> set[tuple[Any, ...]]:
    return {(model, horizon, configuration, fold.number)
            for model in (*scope.primary_models, *scope.supportive_models, *scope.baselines)
            for horizon in scope.horizons
            for configuration in ([c.canonical_config_id for c in PRIMARY_GRID] if model in PRIMARY_MODELS
                                  else ["fixed" if model in SUPPORTIVE_MODELS else "not_tuned"])
            for fold in VALIDATION_FOLDS}


def plan_counts(scope: RunScope) -> dict[str, int]:
    keys = expected_keys(scope)
    primary = sum(k[0] in PRIMARY_MODELS for k in keys)
    supportive = sum(k[0] in SUPPORTIVE_MODELS for k in keys)
    baseline = sum(k[0] in BASELINE_MODELS for k in keys)
    return {"primary_fits": primary, "supportive_fits": supportive, "baseline_evaluations": baseline,
            "total_evaluations": len(keys), "configuration_summaries": len(keys) // 4}


def read_csv(directory: Path, name: str) -> list[dict[str, Any]]:
    with (directory / name).open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != list(CSV_SCHEMAS[name]):
            raise IntegrityError(f"Artifact schema mismatch: {name}.")
        result = []
        for row in reader:
            if set(row) != set(CSV_SCHEMAS[name]) or None in row.values():
                raise IntegrityError("Malformed CSV record.")
            decoded: dict[str, Any] = {}
            for key, value in row.items():
                if value == "":
                    decoded[key] = None
                elif key in INTS:
                    decoded[key] = int(value)
                elif key in FLOATS:
                    decoded[key] = float(value)
                    if not np.isfinite(decoded[key]):
                        raise IntegrityError("Nonfinite persisted metric/prediction.")
                elif key == "selected_configuration":
                    if value not in ("true", "false"):
                        raise IntegrityError("Invalid selection flag.")
                    decoded[key] = value == "true"
                elif key == "overlapping_reasons":
                    decoded[key] = json.loads(value)
                else:
                    decoded[key] = value
            result.append(decoded)
    return result


def _index(records: list[dict[str, Any]], keys: tuple[str, ...]) -> dict[tuple[Any, ...], dict[str, Any]]:
    result = {tuple(r[k] for k in keys): r for r in records}
    if len(result) != len(records):
        raise IntegrityError("Duplicate evidence keys.")
    return result


def verify_scientific(directory: Path, *, include_report: bool = True) -> dict[str, Any]:
    """Verify finalized scientific evidence before completion; no model fitting."""
    try:
        layout = RepositoryLayout.from_artifact_directory(directory)
        metadata = json.loads(layout._owned_path(directory / "run_metadata.json").read_text(encoding="utf-8"))
        if metadata["run_status"] not in ("finalizing", "verified_completed"):
            raise IntegrityError("Failed, interrupted or running evidence is not complete.")
        if metadata["evaluation_stage"] != "validation" or metadata["schema_version"] != SCHEMA_VERSION or metadata["protocol_version"] != PROTOCOL_VERSION:
            raise IntegrityError("Evidence stage/schema/protocol differs.")
        _run_files(directory, metadata, include_report=include_report)
        auth_path = directory / "authorization.json"
        authorization = ValidationAuthorization.from_json(auth_path)
        if file_hash(auth_path) != metadata["authorization_digest"]:
            raise IntegrityError("Retained authorization digest differs.")
        if (authorization.run_id != metadata["run_id"] or authorization.input_view_hash != metadata["input_view_hash"]
                or authorization.source_hashes != metadata["source_hashes"]
                or authorization.protocol_hash != metadata["protocol_hash"]
                or authorization.validation_run_authorized is not True or type(authorization.worker_count) is not int
                or authorization.worker_count != 1 or authorization.schema_version != metadata["schema_version"]
                or authorization.protocol_version != metadata["protocol_version"]):
            raise IntegrityError("Authorization/provenance relationship differs.")
        if metadata["source_hashes"].get("docs/forecasting-feature-engineering.md") != metadata["feature_contract_hash"]:
            raise IntegrityError("Feature contract hash differs from reviewed source.")
        scope = scope_from_metadata(metadata)
        if authorization.scope != scope:
            raise IntegrityError("Executed scope differs from authorization.")
        expected = expected_keys(scope)
        if metadata["expected_counts"] != plan_counts(scope) or metadata["completed_counts"] != metadata["expected_counts"]:
            raise IntegrityError("Expected/completed counts differ from the approved plan.")
        for name in ARTIFACT_NAMES:
            if name != "comparison.md" or include_report:
                path = (layout.draft_report_directory(directory.name) if name == "comparison.md" else directory) / name
                if not path.is_file():
                    raise IntegrityError(f"Required artifact missing: {name}.")
        tables = {name: read_csv(directory, name) for name in CSV_SCHEMAS}
        metrics, summaries, predictions = (tables[name] for name in ("fold_metrics.csv", "configuration_summary.csv", "predictions.csv"))
        candidates = _index(metadata["candidate_records"], KEY)
        metric_index = _index(metrics, KEY)
        if set(candidates) != expected or set(metric_index) != expected:
            raise IntegrityError("Candidate/fold/configuration plan is incomplete.")
        if any(r["candidate_status"] != "completed" for r in candidates.values()):
            raise IntegrityError("Incomplete candidate evidence.")
        if _index(json_value(metadata["metric_records"]), KEY) != metric_index:
            raise IntegrityError("CSV metrics differ from metadata.")
        if _index(summaries, KEY[:3]) != _index(json_value(metadata["configuration_summary_records"]), KEY[:3]):
            raise IntegrityError("CSV summaries differ from metadata.")
        recomputed = summarize_configurations(metrics)
        selections, ties = select_primary(recomputed, metadata["candidate_records"])
        if _index(recomputed, KEY[:3]) != _index(summaries, KEY[:3]):
            raise IntegrityError("Configuration summaries/selection differ from fold evidence.")
        selected = json.loads((directory / "selected_configurations.json").read_text(encoding="utf-8"))
        if selected["run_id"] != metadata["run_id"] or selected["schema_version"] != SCHEMA_VERSION:
            raise IntegrityError("Selection artifact identity differs.")
        if json_value(selections) != selected["selections"] or selected["selections"] != metadata["selection_records"]:
            raise IntegrityError("Selection references differ from complete evidence.")
        if {str(k): v for k, v in ties.items()} != metadata["tied_primary_models"]:
            raise IntegrityError("Recorded primary ties differ.")
        pair_count = metadata["expected_pair_count"]
        if type(pair_count) is not int or pair_count <= 0 or len(predictions) != len(expected) * pair_count:
            raise IntegrityError("Prediction count differs from the complete plan.")
        _index(predictions, (*KEY, "SKU_ID", "Warehouse_ID"))
        grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
        for row in predictions:
            grouped[tuple(row[k] for k in KEY)].append(row)
        if set(grouped) != expected:
            raise IntegrityError("Prediction candidate keys differ.")
        roster = None
        observed: dict[tuple[Any, ...], dict[tuple[str, str], float]] = {}
        for key, rows in grouped.items():
            pairs = {(r["SKU_ID"], r["Warehouse_ID"]) for r in rows}
            if len(pairs) != pair_count or (roster is not None and pairs != roster):
                raise IntegrityError("Prediction pair roster differs.")
            roster = pairs
            candidate = candidates[key]
            fold = VALIDATION_FOLDS[key[3] - 1]
            for row in [*rows, candidate, metric_index[key]]:
                if row["run_id"] != metadata["run_id"] or row["evaluation_stage"] != "validation" or row["evidence_role"] != ROLES[key[0]]:
                    raise IntegrityError("Evidence identity/role differs.")
                if row["canonical_config_id"] != (key[2] if key[0] in PRIMARY_MODELS else None):
                    raise IntegrityError("Canonical configuration identity differs.")
                if row["training_start"] != fold.training.start.isoformat() or row["training_end"] != fold.training.end.isoformat():
                    raise IntegrityError("Training interval differs from the frozen fold.")
                if row["forecast_origin"] != candidate["forecast_origin"] or row["target_start_date"] != fold.validation.start.isoformat():
                    raise IntegrityError("Prediction origin/target alignment differs.")
                if row["target_end_date"] != (fold.training.end + timedelta(days=key[1])).isoformat():
                    raise IntegrityError("Target interval differs from the frozen horizon.")
            if candidate["forecast_origin"] != fold.training.end.isoformat():
                raise IntegrityError("Candidate origin differs.")
            values = {(r["SKU_ID"], r["Warehouse_ID"]): r["observed_target"] for r in rows}
            identity = (key[1], key[3])
            if identity in observed and observed[identity] != values:
                raise IntegrityError("Candidates were scored on different observed targets.")
            observed[identity] = values
            calculated = forecasting_metrics([r["observed_target"] for r in rows], [r["prediction"] for r in rows])
            for name, value in calculated.items():
                if metric_index[key][name] != value:
                    raise IntegrityError("Persisted metrics differ from predictions/targets.")
            summary = _index(summaries, KEY[:3])[key[:3]]
            for row in rows:
                if (row["prediction_status"] != "available" or row["target_status"] != "complete" or row["eligibility_status"] != "eligible"
                        or row["representation_id"] != candidate["representation_id"]
                        or row["selection_status"] != summary["selection_status"]
                        or row["selected_configuration"] != summary["selected_configuration"]):
                    raise IntegrityError("Prediction status/representation/selection differs.")
        eligibility = tables["eligibility_counts.csv"]
        expected_eligibility: list[dict[str, Any]] = []
        for row in metadata["eligibility_records"]:
            base = {k: row[k] for k in CSV_SCHEMAS["eligibility_counts.csv"] if k not in ("exclusion_reason", "reason_count")}
            expected_eligibility.extend({**base, "exclusion_reason": reason, "reason_count": count}
                                        for reason, count in row["exclusion_counts"].items())
        eligibility_keys = ("model", "horizon", "fold_id", "SKU_ID", "Warehouse_ID", "exclusion_reason")
        if _index(eligibility, eligibility_keys) != _index(json_value(expected_eligibility), eligibility_keys):
            raise IntegrityError("Eligibility artifact differs from recorded populations.")
        if any(r["scored_origin_count"] != r["expected_origin_count"] or r["scored_origin_count"] != 1 for r in eligibility):
            raise IntegrityError("Eligibility population was not fully scored.")
        representations = _index(metadata["representation_records"], ("representation_id",))
        model_index = _index(metadata["model_artifacts"], KEY)
        if set(model_index) != {k for k in expected if k[0] not in BASELINE_MODELS}:
            raise IntegrityError("Missing validation model descriptors.")
        for key, record in model_index.items():
            candidate = candidates[key]
            if record["representation_id"] != candidate["representation_id"]:
                raise IntegrityError("Model representation link differs.")
            descriptor = json.loads(safe_path(directory, record["descriptor_path"]).read_text(encoding="utf-8"))
            for field in ("training_start", "training_end", "target_start_date", "target_end_date", "training_population_hash",
                          "requested_api_parameters", "effective_api_parameters"):
                if descriptor[field] != candidate[field]:
                    raise IntegrityError("Model descriptor differs from candidate evidence.")
            if descriptor["validation_start"] != candidate["outcome_window_start"] or descriptor["validation_end"] != candidate["outcome_window_end"]:
                raise IntegrityError("Model validation interval differs.")
            representation = representations[(record["representation_id"],)]
            state = json.loads(safe_path(directory, record["preprocessor_path"]).read_text(encoding="utf-8"))
            if state["physical_feature_names"] != representation["physical_feature_names"] or state["training_row_count"] != representation["training_row_count"]:
                raise IntegrityError("Preprocessor representation differs.")
            for position, field in enumerate(("SKU_ID", "Warehouse_ID")):
                if state["vocabularies"][position] != representation["category_vocabularies"][field]:
                    raise IntegrityError("Persisted vocabulary differs from training representation.")
            if key[0] == "ridge" and (state["numerical_means"] != representation["numerical_means"] or state["numerical_scales"] != representation["numerical_scales"]):
                raise IntegrityError("Persisted scaler differs from training representation.")
            try:
                features, replayed = replay_model(directory, record, metadata)
            except (UnpicklingError, EOFError, XGBoostError, LightGBMError, CatBoostError) as exc:
                raise IntegrityError("Persisted model evidence could not be loaded or replayed.") from exc
            expected_values = {(r["SKU_ID"], r["Warehouse_ID"]): r["prediction"] for r in grouped[key]}
            replay_pairs = list(features.loc[:, ["SKU_ID", "Warehouse_ID"]].itertuples(index=False, name=None))
            if len(set(replay_pairs)) != pair_count or set(replay_pairs) != set(expected_values):
                raise IntegrityError("Replay origin population differs.")
            if not np.array_equal(replayed, np.asarray([expected_values[p] for p in replay_pairs])):
                raise IntegrityError("Reloaded predictions differ from persisted validation predictions.")
        if include_report:
            _verify_artifact_receipts(directory, metadata)
        return {"status": "passed", "evaluations": len(expected), "predictions": len(predictions),
                "configuration_summaries": len(summaries), "models_replayed": len(model_index)}
    except IntegrityError:
        raise
    except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError, csv.Error) as exc:
        raise IntegrityError("Missing, corrupt or inconsistent run evidence.") from exc



def build_manifest(directory: Path, metadata: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    """Index all three owners using version-2 repository-relative references."""
    try:
        layout = RepositoryLayout.from_artifact_directory(directory)
        if metadata["run_status"] != "verified_completed" or result.get("status") != "passed":
            raise IntegrityError("Completion requires verified evidence.")
        if layout._owned_path(directory / "run_manifest.json").exists():
            raise IntegrityError("A published completion manifest cannot be rebuilt.")
        files = _run_files(directory, metadata)
        _verify_artifact_receipts(directory, metadata)
        return {"manifest_version": MANIFEST_VERSION, "run_id": directory.name, "schema_version": SCHEMA_VERSION,
                "final_status": "verified_completed", "completed_at_utc": metadata["completed_at_utc"],
                "metadata_hash": file_hash(directory / "run_metadata.json"), "integrity_result": result,
                "artifacts": [{"owner": files[path], "path": path.relative_to(layout.root).as_posix(),
                               "sha256": file_hash(path)} for path in sorted(files)]}
    except IntegrityError:
        raise
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise IntegrityError("Cannot build a manifest for invalid run-owned evidence.") from exc


def verify_completed(directory: Path) -> dict[str, Any]:
    """Only the artifact anchor's manifest can establish completion across owners."""
    try:
        layout = RepositoryLayout.from_artifact_directory(directory)
        manifest = json.loads(layout._owned_path(directory / "run_manifest.json").read_text(encoding="utf-8"))
        metadata = json.loads(layout._owned_path(directory / "run_metadata.json").read_text(encoding="utf-8"))
        if (manifest["manifest_version"] != MANIFEST_VERSION or manifest["final_status"] != "verified_completed"
                or manifest["run_id"] != directory.name or metadata["run_id"] != directory.name
                or manifest["schema_version"] != SCHEMA_VERSION or metadata["run_status"] != "verified_completed"
                or manifest["metadata_hash"] != file_hash(directory / "run_metadata.json")
                or manifest["completed_at_utc"] != metadata["completed_at_utc"]):
            raise IntegrityError("Completion manifest/metadata differs.")
        index = _index(manifest["artifacts"], ("path",))
        references = {_evidence_path(directory, record["owner"], record["path"]): record for record in index.values()}
        files = _run_files(directory, metadata)
        if files != {path: record["owner"] for path, record in references.items()}:
            raise IntegrityError("Completion manifest file set differs.")
        for path, record in references.items():
            if file_hash(path) != record["sha256"]:
                raise IntegrityError("Completion artifact hash mismatch.")
        result = verify_scientific(directory)
        if result != manifest["integrity_result"] or result != metadata["integrity_result"]:
            raise IntegrityError("Completion integrity result differs.")
        return result
    except IntegrityError:
        raise
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise IntegrityError("No valid completion manifest exists.") from exc
