"""Final-specific persistence, prediction receipts and read-only verification.

No validation fold schemas, selection rules, fitting or parent-outcome reads.
"""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import os
from pathlib import Path
import re
from typing import Any, Callable

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from src.forecasting.artifacts import ArtifactWriter, file_hash, json_text, json_value, require_mutable_run
from src.forecasting.baselines import BASELINE_FORMULAS, baseline_predictions
from src.forecasting.configuration import PRIMARY_MODELS
from src.forecasting.final_authorization import (
    FINAL_SCHEMA, TEMPORAL_POLICY, TRAINING_END, FinalAuthorization, FinalCandidate,
    candidate_payload, read_freeze, read_json,
)
from src.forecasting.metrics import forecasting_metrics
from src.forecasting.features import FEATURE_COLUMNS, KEY_COLUMNS
from src.forecasting.model_artifacts import FORMATS, _load_estimator, _save_estimator
from src.forecasting.models import estimator_parameters
from src.forecasting.paths import RepositoryLayout
from src.forecasting.preprocessing import ForecastPreprocessor, preprocessor_state, restore_preprocessor
from src.forecasting.selection import ROLES
from src.forecasting.targets import FORECAST_HORIZONS

PREDICTION_FIELDS = {
    "run_id", "evaluation_stage", "evidence_role", "model", "horizon", "configuration_id",
    "canonical_config_id", "SKU_ID", "Warehouse_ID", "training_start", "training_end",
    "forecast_origin", "target_start_date", "target_end_date", "prediction",
}
SEALED_NAMES = ("authorization.json", "freeze.md", "policy.md", "predictions.json",
                "candidates.json", "baseline_history.json", "eligibility.json")
ARTIFACT_NAMES = (*SEALED_NAMES, "prediction_receipt.json", "observations.json",
                  "metrics.json", "run_metadata.json", "run.log")
WRITABLE_NAMES = {*ARTIFACT_NAMES, "diagnostics.json", "run_manifest.json", "comparison.md"}


class FinalIntegrityError(ValueError):
    """Final evidence is incomplete, inconsistent, redirected or changed."""


def candidate_keys(run_id: str, candidate: FinalCandidate) -> dict[str, Any]:
    return {
        "run_id": run_id, "evaluation_stage": "final_evaluation", "evidence_role": ROLES[candidate.model],
        **asdict(candidate),
        "canonical_config_id": candidate.configuration_id if candidate.model in PRIMARY_MODELS else None,
        **{k: v for k, v in TEMPORAL_POLICY.items() if k != "outcome_window_end"},
        "target_end_date": (pd.Timestamp(TRAINING_END) + pd.Timedelta(days=candidate.horizon)).date().isoformat(),
    }


def _roots(layout: RepositoryLayout, run_id: str) -> dict[str, Path]:
    return {"artifacts": layout.run_directory(run_id), "models": layout.model_run_directory(run_id),
            "reports": layout.draft_report_directory(run_id)}


def _path(directory: Path, owner: str, relative: str) -> Path:
    layout = RepositoryLayout.from_artifact_directory(directory)
    reference = Path(relative)
    if (owner not in _roots(layout, directory.name) or reference.is_absolute() or ".." in reference.parts
            or "\\" in relative or reference.as_posix() != relative):
        raise FinalIntegrityError("Invalid final evidence path.")
    path = layout.repository_path(relative)
    if not path.is_relative_to(_roots(layout, directory.name)[owner]):
        raise FinalIntegrityError("Final evidence crosses owner or run boundaries.")
    return layout._owned_path(path)


def _receipts(directory: Path, files: dict[Path, str]) -> list[dict[str, str]]:
    layout = RepositoryLayout.from_artifact_directory(directory)
    return [{"path": path.relative_to(layout.root).as_posix(), "owner": owner, "sha256": file_hash(path)}
            for path, owner in sorted(files.items())]


def _verify_receipts(directory: Path, receipts: Any, expected: dict[Path, str]) -> None:
    if not isinstance(receipts, list):
        raise FinalIntegrityError("Final file receipts must be a list.")
    actual = {}
    for row in receipts:
        if not isinstance(row, dict) or set(row) != {"path", "owner", "sha256"}:
            raise FinalIntegrityError("Final file receipt schema differs.")
        path = _path(directory, row["owner"], row["path"])
        if path in actual or row["owner"] != expected.get(path) or file_hash(path) != row["sha256"]:
            raise FinalIntegrityError("Final evidence hash, owner or uniqueness differs.")
        actual[path] = row["owner"]
    if actual != expected:
        raise FinalIntegrityError("Final evidence file set differs.")


def _model_paths(directory: Path, candidate: FinalCandidate) -> dict[str, Path]:
    layout = RepositoryLayout.from_artifact_directory(directory)
    base = layout.model_run_directory(directory.name) / "final" / candidate.model / f"h{candidate.horizon}" / candidate.configuration_id
    return {name: layout._owned_path(base / filename) for name, filename in {
        "model": f"model.{FORMATS[candidate.model]}", "descriptor": "descriptor.json",
        "preprocessor": "state.json", "origin_features": "origin_features.json",
    }.items()}


class FinalArtifactWriter:
    """Reuse exclusive run creation only; final writes have their own schemas."""
    def __init__(self, layout: RepositoryLayout, run_id: str):
        anchor = ArtifactWriter(layout, run_id)
        self.layout, self.directory = layout, anchor.directory

    def path(self, name: str) -> Path:
        if name not in WRITABLE_NAMES:
            raise ValueError("Unknown final artifact.")
        base = self.layout.draft_report_directory(self.directory.name) if name == "comparison.md" else self.directory
        return self.layout._owned_path(base / name)

    def write_text(self, name: str, text: str) -> None:
        require_mutable_run(self.directory)
        if name in (*SEALED_NAMES, "prediction_receipt.json") and self.path("prediction_receipt.json").exists():
            raise FinalIntegrityError("Sealed prediction evidence cannot be rewritten.")
        path = self.path(name)
        temporary = self.layout._owned_path(path.with_name(path.name + ".tmp"))
        with temporary.open("x", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)

    def write_json(self, name: str, value: Any) -> None:
        self.write_text(name, json_text(value))

    def event(self, operation: str, **details: Any) -> None:
        require_mutable_run(self.directory)
        with self.path("run.log").open("a", encoding="utf-8") as stream:
            stream.write(json_text({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                   "evaluation_stage": "final_evaluation", "operation": operation, **details}))

    def persist_model(self, estimator: Any, candidate: FinalCandidate, record: dict[str, Any],
                      state: ForecastPreprocessor, origin: pd.DataFrame, metadata: dict[str, Any]) -> dict[str, Any]:
        require_mutable_run(self.directory)
        if self.path("prediction_receipt.json").exists():
            raise FinalIntegrityError("Cannot replace a sealed final model.")
        paths = _model_paths(self.directory, candidate)
        paths["model"].parent.mkdir(parents=True, exist_ok=False)
        temporary = paths["model"].with_name(f"model.tmp.{FORMATS[candidate.model]}")
        _save_estimator(estimator, candidate.model, temporary)
        temporary.replace(paths["model"])
        paths["preprocessor"].write_text(json_text(preprocessor_state(state)), encoding="utf-8")
        paths["origin_features"].write_text(json_text(origin.to_dict("records")), encoding="utf-8")
        references = {f"{name}_path": p.relative_to(self.layout.root).as_posix() for name, p in paths.items()}
        hashes = {f"{name}_hash": file_hash(p) for name, p in paths.items() if name != "descriptor"}
        provenance = {k: metadata[k] for k in (
            "source_hashes", "freeze_hash", "policy_hash", "protocol_hash", "feature_contract_hash",
            "input_view_hash", "validated_provenance_hash", "python_version", "library_versions",
        )}
        descriptor = {
            "artifact_kind": "final_refit", "descriptor_version": 1, **candidate_keys(self.directory.name, candidate),
            "training_population_hash": record["training_population_hash"],
            "training_row_count": record["training_row_count"], "fit": record["fit"],
            "physical_feature_names": state.physical_feature_names, "provenance": provenance,
            **references, **hashes,
        }
        paths["descriptor"].write_text(json_text(descriptor), encoding="utf-8")
        return {**asdict(candidate), **references, **hashes, "descriptor_hash": file_hash(paths["descriptor"])}

    def seal(self, predictions: list[dict[str, Any]], candidates: list[dict[str, Any]],
             history: pd.DataFrame, eligibility: list[dict[str, Any]]) -> str:
        self.write_json("predictions.json", predictions)
        self.write_json("candidates.json", candidates)
        self.write_json("baseline_history.json", history.to_dict("records"))
        self.write_json("eligibility.json", eligibility)
        files = _sealed_files(self.directory, candidates)
        self.write_json("prediction_receipt.json", {
            "receipt_version": 1, "run_id": self.directory.name, "evaluation_stage": "final_evaluation",
            "candidate_count": len(candidates), "prediction_count": len(predictions),
            "files": _receipts(self.directory, files),
        })
        digest = file_hash(self.path("prediction_receipt.json"))
        verify_sealed_predictions(self.directory, digest)
        return digest


def _snapshot(directory: Path) -> tuple[FinalAuthorization, dict[str, Any]]:
    layout = RepositoryLayout.from_artifact_directory(directory)
    auth = FinalAuthorization.from_payload(read_json(layout._owned_path(directory / "authorization.json")))
    freeze = read_freeze(layout._owned_path(directory / "freeze.md"))
    metadata = read_json(layout._owned_path(directory / "run_metadata.json"))
    if (auth.run_id != directory.name or metadata["run_id"] != directory.name
            or metadata["evaluation_stage"] != "final_evaluation" or metadata["schema_version"] != FINAL_SCHEMA
            or auth.candidates != freeze.candidates or auth.producer_mapping != freeze.producer_mapping
            or auth.validation_run_id != freeze.validation_run_id
            or auth.validation_manifest_sha256 != freeze.validation_manifest_sha256
            or file_hash(directory / "freeze.md") != auth.freeze_hash
            or file_hash(directory / "policy.md") != auth.policy_hash
            or metadata["authorization_hash"] != file_hash(directory / "authorization.json")):
        raise FinalIntegrityError("Final snapshot identity or reviewed freeze differs.")
    for key in ("freeze_hash", "policy_hash", "protocol_hash", "feature_contract_hash",
                "input_view_hash", "validated_provenance_hash", "python_version", "library_versions",
                "producer_mapping", "temporal_policy", "validation_run_id", "validation_manifest_sha256",
                "requirements_hash", "approval_references"):
        if metadata[key] != json_value(getattr(auth, key)):
            raise FinalIntegrityError("Final metadata differs from retained authorization.")
    if metadata["source_hashes"] != metadata["runtime"]["source_hashes"]:
        raise FinalIntegrityError("Final recorded runtime source provenance differs from metadata.")
    if metadata["scope"] != candidate_payload(auth.candidates):
        raise FinalIntegrityError("Final metadata scope differs.")
    return auth, metadata


def _sealed_files(directory: Path, records: list[dict[str, Any]]) -> dict[Path, str]:
    layout = RepositoryLayout.from_artifact_directory(directory)
    files = {layout._owned_path(directory / name): "artifacts" for name in SEALED_NAMES}
    for record in records:
        c = FinalCandidate(record["model"], record["horizon"], record["configuration_id"])
        if c.learned:
            for name, path in _model_paths(directory, c).items():
                if record["model_artifact"][name + "_path"] != path.relative_to(layout.root).as_posix():
                    raise FinalIntegrityError("Final model is outside its exact candidate directory.")
                files[path] = "models"
    return files


def verify_sealed_predictions(directory: Path, receipt_hash: str) -> list[dict[str, Any]]:
    """The caller-held receipt hash prevents replacement before outcome access."""
    try:
        layout = RepositoryLayout.from_artifact_directory(directory)
        path = layout._owned_path(directory / "prediction_receipt.json")
        if file_hash(path) != receipt_hash:
            raise FinalIntegrityError("Prediction receipt changed.")
        auth, metadata = _snapshot(directory)
        receipt, records, rows = (read_json(directory / name) for name in
                                  ("prediction_receipt.json", "candidates.json", "predictions.json"))
        if (set(receipt) != {"receipt_version", "run_id", "evaluation_stage", "candidate_count", "prediction_count", "files"}
                or receipt["receipt_version"] != 1 or receipt["run_id"] != directory.name
                or receipt["evaluation_stage"] != "final_evaluation" or receipt["candidate_count"] != 28
                or [FinalCandidate(r["model"], r["horizon"], r["configuration_id"]) for r in records] != list(auth.candidates)):
            raise FinalIntegrityError("Incomplete or reordered frozen final candidate evidence.")
        _verify_receipts(directory, receipt["files"], _sealed_files(directory, records))
        roster = [tuple(pair) for pair in metadata["pair_roster"]]
        if not roster or sorted(set(roster)) != roster:
            raise FinalIntegrityError("Final roster must be sorted and unique.")
        expected = [(c, pair) for c in auth.candidates for pair in roster]
        if len(rows) != len(expected) or receipt["prediction_count"] != len(expected):
            raise FinalIntegrityError("Incomplete final prediction population.")
        for row, (c, pair) in zip(rows, expected, strict=True):
            if (set(row) != PREDICTION_FIELDS or {k: row[k] for k in candidate_keys(directory.name, c)} != candidate_keys(directory.name, c)
                    or (row["SKU_ID"], row["Warehouse_ID"]) != pair
                    or isinstance(row["prediction"], bool) or not isinstance(row["prediction"], (int, float))
                    or not np.isfinite(row["prediction"])):
                raise FinalIntegrityError("Final prediction schema, chronology, keys or values differ.")
        history = pd.DataFrame(read_json(directory / "baseline_history.json"))
        if list(history[["SKU_ID", "Warehouse_ID"]].itertuples(index=False, name=None)) != roster:
            raise FinalIntegrityError("Baseline roster differs from final predictions.")
        eligibility = read_json(directory / "eligibility.json")
        if [r["horizon"] for r in eligibility] != list(FORECAST_HORIZONS):
            raise FinalIntegrityError("Final horizon eligibility evidence differs.")
        populations = {r["horizon"]: r for r in eligibility}
        for population in eligibility:
            pairs = population["per_pair"]
            if ([(r["SKU_ID"], r["Warehouse_ID"]) for r in pairs] != roster
                    or type(population["training_row_count"]) is not int or population["training_row_count"] <= 0
                    or sum(r["training_row_count"] for r in pairs) != population["training_row_count"]
                    or not re.fullmatch("[0-9a-f]{64}", population["training_population_hash"])):
                raise FinalIntegrityError("Final eligible population inventory differs.")
            for pair in pairs:
                counts = [pair[k] for k in ("raw_row_count", "feature_eligible_count", "label_eligible_count", "training_row_count")]
                if (any(type(v) is not int or v < 0 for v in counts)
                        or counts[0] != (pd.Timestamp(TRAINING_END) - pd.Timestamp(TEMPORAL_POLICY["training_start"])).days + 1
                        or not 0 < counts[3] <= min(counts[1:3]) <= max(counts[1:3]) <= counts[0]
                        or set(pair["exclusion_counts"]) != {"incomplete_predictor_history", "target_after_training_cutoff", "missing_observed_training_target"}
                        or pair["exclusion_counts"]["incomplete_predictor_history"] != counts[0] - counts[1]
                        or pair["exclusion_counts"]["target_after_training_cutoff"] != population["horizon"] - 1
                        or pair["exclusion_counts"]["missing_observed_training_target"] != counts[0] - counts[2] - population["horizon"] + 1):
                    raise FinalIntegrityError("Final labelled eligibility counts differ.")
        common_origin: pd.DataFrame | None = None
        vocabulary: dict[int, Any] = {}
        for c, record in zip(auth.candidates, records, strict=True):
            if (set(record) != {*candidate_keys(directory.name, c), "candidate_status", "fit", "model_artifact",
                                "training_row_count", "training_population_hash", "baseline_formula"}
                    or record["training_row_count"] != populations[c.horizon]["training_row_count"]
                    or record["training_population_hash"] != populations[c.horizon]["training_population_hash"]
                    or record["candidate_status"] != "completed"
                    or {k: record[k] for k in candidate_keys(directory.name, c)} != candidate_keys(directory.name, c)):
                raise FinalIntegrityError("Final candidate is incomplete or misidentified.")
            predicted = [r["prediction"] for r in rows if (r["model"], r["horizon"], r["configuration_id"]) == c.key]
            if not c.learned:
                if (record["fit"] is not None or record["model_artifact"] is not None
                        or record["baseline_formula"] != BASELINE_FORMULAS[c.model]
                        or not np.array_equal(baseline_predictions(history, c.model, c.horizon), predicted)):
                    raise FinalIntegrityError("Final baseline evidence differs.")
                continue
            paths = _model_paths(directory, c)
            model_record = record["model_artifact"]
            if {k: model_record[k] for k in asdict(c)} != asdict(c):
                raise FinalIntegrityError("Final model index identity differs.")
            for name, p in paths.items():
                if file_hash(p) != model_record[name + "_hash"]:
                    raise FinalIntegrityError("Final model index hash differs.")
            descriptor = read_json(paths["descriptor"])
            state = restore_preprocessor(read_json(paths["preprocessor"]))
            origin = pd.DataFrame(read_json(paths["origin_features"]))
            if (descriptor["artifact_kind"] != "final_refit" or descriptor["descriptor_version"] != 1
                    or {k: descriptor[k] for k in candidate_keys(directory.name, c)} != candidate_keys(directory.name, c)
                    or descriptor["fit"] != record["fit"] or state.model != c.model or state.horizon != c.horizon
                    or state.training_end != pd.Timestamp(TRAINING_END)
                    or state.training_row_count != record["training_row_count"]
                    or record["training_row_count"] != populations[c.horizon]["training_row_count"]
                    or record["training_population_hash"] != populations[c.horizon]["training_population_hash"]
                    or descriptor["training_population_hash"] != record["training_population_hash"]
                    or descriptor["training_row_count"] != state.training_row_count
                    or descriptor["physical_feature_names"] != list(state.physical_feature_names)):
                raise FinalIntegrityError("Final fitted population, preprocessing or descriptor differs.")
            for name, p in paths.items():
                if descriptor[name + "_path"] != model_record[name + "_path"]:
                    raise FinalIntegrityError("Final descriptor path differs.")
                if name != "descriptor" and descriptor[name + "_hash"] != model_record[name + "_hash"]:
                    raise FinalIntegrityError("Final descriptor hash differs.")
            if descriptor["provenance"] != {k: metadata[k] for k in descriptor["provenance"]} or set(descriptor["provenance"]) != {
                "source_hashes", "freeze_hash", "policy_hash", "protocol_hash", "feature_contract_hash",
                "input_view_hash", "validated_provenance_hash", "python_version", "library_versions",
            }:
                raise FinalIntegrityError("Final model provenance differs.")
            fit = record["fit"]
            requested = estimator_parameters(c.model, c.configuration)  # type: ignore[arg-type]
            iterations = c.configuration.boosting_iterations if c.configuration else (300 if c.model == "random_forest" else None)
            if (set(fit) != {"requested_api_parameters", "effective_api_parameters", "requested_iterations", "effective_iterations"}
                    or not isinstance(fit["effective_api_parameters"], dict) or not fit["effective_api_parameters"]
                    or record["baseline_formula"] is not None
                    or fit["requested_api_parameters"] != requested or fit["requested_iterations"] != iterations
                    or fit["effective_iterations"] != iterations):
                raise FinalIntegrityError("Final frozen estimator recipe differs.")
            if (list(origin[["SKU_ID", "Warehouse_ID"]].itertuples(index=False, name=None)) != roster
                    or not origin.Date.eq(TEMPORAL_POLICY["target_start_date"]).all()):
                raise FinalIntegrityError("Final replay origin differs.")
            if set(origin.columns) != {*KEY_COLUMNS, *FEATURE_COLUMNS}:
                raise FinalIntegrityError("Final replay inputs differ from frozen predictor contract.")
            if common_origin is None:
                common_origin = origin
            elif not origin.equals(common_origin):
                raise FinalIntegrityError("All final candidates must share the same historical origin vector.")
            state.transform(origin)
            if c.model in PRIMARY_MODELS:
                previous = vocabulary.setdefault(c.horizon, state.vocabularies)
                if previous != state.vocabularies:
                    raise FinalIntegrityError("Primary final vocabularies differ.")
        return rows
    except FinalIntegrityError:
        raise
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        raise FinalIntegrityError("Invalid sealed final prediction evidence.") from exc


def verify_final_scientific(directory: Path) -> dict[str, Any]:
    """Reconcile consumable final evidence; failed runs require a separate audit."""
    try:
        auth, metadata = _snapshot(directory)
        if metadata["run_status"] not in {"finalizing", "verified_completed"}:
            raise FinalIntegrityError("Unfinished final run cannot be consumed.")
        return _verify_final_scientific(directory, auth, metadata)
    except FinalIntegrityError:
        raise
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        raise FinalIntegrityError("Invalid final scientific evidence.") from exc


def _verify_final_scientific(
    directory: Path, auth: FinalAuthorization, metadata: dict[str, Any],
) -> dict[str, Any]:
    """Reconcile final metrics and replay all saved models; never fit or reopen data."""
    try:
        rows = verify_sealed_predictions(directory, metadata["prediction_receipt_hash"])
        observations, metrics, records = (read_json(directory / name) for name in
                                         ("observations.json", "metrics.json", "candidates.json"))
        roster = [tuple(p) for p in metadata["pair_roster"]]
        expected_keys = [(h, *p) for h in FORECAST_HORIZONS for p in roster]
        if (len(observations) != len(expected_keys) or any(set(r) != {"horizon", "SKU_ID", "Warehouse_ID", "observed_target"}
                or type(r["horizon"]) is not int for r in observations)
                or [(r["horizon"], r["SKU_ID"], r["Warehouse_ID"]) for r in observations] != expected_keys):
            raise FinalIntegrityError("Final observed target population differs.")
        actuals = {(r["horizon"], r["SKU_ID"], r["Warehouse_ID"]): r["observed_target"] for r in observations}
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not np.isfinite(v) or v < 0 or v != int(v)
               for v in actuals.values()):
            raise FinalIntegrityError("Invalid final observed targets.")
        if len(metrics) != 28:
            raise FinalIntegrityError("Final metric scope differs.")
        replay_count = 0
        for c, metric, record in zip(auth.candidates, metrics, records, strict=True):
            predicted = [r["prediction"] for r in rows if (r["model"], r["horizon"], r["configuration_id"]) == c.key]
            calculated = forecasting_metrics([actuals[c.horizon, *p] for p in roster], predicted)
            if calculated["metric_status"] == "failed" or metric != {**candidate_keys(directory.name, c), **calculated}:
                raise FinalIntegrityError("Final metrics differ from immutable predictions/actuals.")
            if c.learned:
                paths = _model_paths(directory, c)
                origin = pd.DataFrame(read_json(paths["origin_features"]))
                state = restore_preprocessor(read_json(paths["preprocessor"]))
                estimator = _load_estimator(c.model, paths["model"])
                matrix = state.transform(origin).to_numpy(dtype=float).copy(order="C")
                with threadpool_limits(limits=1):
                    if c.model == "lightgbm":
                        replay = estimator.predict(matrix, num_threads=1)
                    elif c.model == "catboost":
                        replay = estimator.predict(matrix, thread_count=1)
                    else:
                        replay = estimator.predict(matrix)
                if not np.array_equal(np.asarray(replay, dtype=float), predicted):
                    raise FinalIntegrityError("Final model replay differs from sealed predictions.")
                replay_count += 1
        return {"status": "passed", "evaluations": 28, "learned_refits": 20,
                "baseline_evaluations": 8, "predictions": len(rows), "models_replayed": replay_count}
    except FinalIntegrityError:
        raise
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        raise FinalIntegrityError("Invalid final scientific evidence.") from exc


def verify_failed_final_recovery(
    directory: Path, *, expected_evidence_hashes: dict[str, str],
) -> dict[str, Any]:
    """Audit a retained replay failure without fitting, parent reads or writes.

    The caller must independently retain/review the full repository-relative
    SHA-256 inventory, including observations, metrics and failure diagnostics.
    These post-reveal files have no completion manifest; reconciliation alone
    cannot detect coordinated replacement. This function never creates that
    inventory, updates original source bindings or publishes completion.
    """
    try:
        layout = RepositoryLayout.from_artifact_directory(directory)
        auth, metadata = _snapshot(directory)
        diagnostics = read_json(layout._owned_path(directory / "diagnostics.json"))
        if (metadata["run_status"] != "failed" or metadata["completed_at_utc"] is not None
                or metadata["integrity_result"] is not None or not metadata["failed_at_utc"]
                or layout._owned_path(directory / "run_manifest.json").exists()
                or set(diagnostics) != {"operation", "candidate", "exception_type", "failure_reason", "completed_predictions"}
                or diagnostics["operation"] != "final_verification" or diagnostics["candidate"] is not None
                or diagnostics["exception_type"] != "FinalIntegrityError"
                or diagnostics["failure_reason"] != "Final model replay differs from sealed predictions."):
            raise FinalIntegrityError("Recovery requires retained final replay failure evidence.")
        files = _final_files(directory, include_diagnostics=True)
        hashes = {r["path"]: r["sha256"] for r in _receipts(directory, files)}
        if not isinstance(expected_evidence_hashes, dict) or hashes != expected_evidence_hashes:
            raise FinalIntegrityError("Failed final evidence differs from the caller-held inventory.")
        result = _verify_final_scientific(directory, auth, metadata)
        if (type(diagnostics["completed_predictions"]) is not int
                or diagnostics["completed_predictions"] != result["predictions"]):
            raise FinalIntegrityError("Failure diagnostics differ from the sealed prediction population.")
        after = {r["path"]: r["sha256"] for r in
                 _receipts(directory, _final_files(directory, include_diagnostics=True))}
        if after != hashes:
            raise FinalIntegrityError("Failed final evidence changed during recovery verification.")
        return {"status": "recovery_verified", "verification_kind": "failed_final_evidence",
                "run_id": directory.name, "original_run_status": "failed", "final_run_completed": False,
                "original_diagnostics": diagnostics, "scientific_verification": result, "evidence_hashes": hashes}
    except FinalIntegrityError:
        raise
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        raise FinalIntegrityError("Invalid failed final recovery evidence.") from exc


def _final_files(directory: Path, *, include_diagnostics: bool = False) -> dict[Path, str]:
    layout = RepositoryLayout.from_artifact_directory(directory)
    files = _sealed_files(directory, read_json(directory / "candidates.json"))
    files.update({layout._owned_path(directory / name): "artifacts" for name in ARTIFACT_NAMES})
    if include_diagnostics:
        files[layout._owned_path(directory / "diagnostics.json")] = "artifacts"
    files[layout._owned_path(layout.draft_report_directory(directory.name) / "comparison.md")] = "reports"
    found: dict[Path, str] = {}
    for owner, folder in _roots(layout, directory.name).items():
        for p in folder.rglob("*"):
            layout._owned_path(p)
            if p.is_file() and p != directory / "run_manifest.json":
                found[p] = owner
    if found != files:
        raise FinalIntegrityError("Missing, extra or unfinished final evidence.")
    return files


def finalize_final_run(writer: FinalArtifactWriter, metadata: dict[str, Any], *,
                       before_publish: Callable[[], None]) -> None:
    metadata["run_status"] = "finalizing"
    writer.write_json("run_metadata.json", metadata)
    metrics = read_json(writer.path("metrics.json"))
    lines = ["# Final forecasting comparison", "", "Generated draft; pending human review.", "",
             "All frozen candidates are reported; the downstream producer mapping is separate.",
             "Seasonal Naive outperformed learned models in validation at 14 and 28 days.",
             "Simulated data; December 3–16 had prior validation exposure and full-year EDA inspected the final interval.",
             "", "| Role | Model | Horizon | Configuration | WAPE | MAE | RMSE | Bias | Status |",
             "|---|---|---:|---|---|---|---|---|---|"]
    for r in metrics:
        lines.append("| " + " | ".join(str(r[k]) for k in
                                      ("evidence_role", "model", "horizon", "configuration_id", "wape", "mae", "rmse", "bias", "metric_status")) + " |")
    writer.write_text("comparison.md", "\n".join(lines) + "\n")
    result = verify_final_scientific(writer.directory)
    before_publish()
    writer.event("finalization_verified", result=result)
    metadata.update(run_status="verified_completed", integrity_result=result,
                    completed_at_utc=datetime.now(timezone.utc).isoformat())
    writer.write_json("run_metadata.json", metadata)
    files = _final_files(writer.directory)
    writer.write_json("run_manifest.json", {
        "manifest_version": 2, "schema_version": FINAL_SCHEMA, "evaluation_stage": "final_evaluation",
        "run_id": writer.directory.name, "final_status": "verified_completed",
        "completed_at_utc": metadata["completed_at_utc"], "integrity_result": result,
        "files": _receipts(writer.directory, files),
    })


def verify_final_completed(directory: Path) -> dict[str, Any]:
    """Validate historical final bundles against their snapshots, not current source."""
    try:
        layout = RepositoryLayout.from_artifact_directory(directory)
        manifest = read_json(layout._owned_path(directory / "run_manifest.json"))
        metadata = read_json(layout._owned_path(directory / "run_metadata.json"))
        if (manifest["manifest_version"] != 2 or manifest["schema_version"] != FINAL_SCHEMA
                or manifest["evaluation_stage"] != "final_evaluation" or manifest["run_id"] != directory.name
                or manifest["final_status"] != "verified_completed" or metadata["run_status"] != "verified_completed"
                or manifest["completed_at_utc"] != metadata["completed_at_utc"]):
            raise FinalIntegrityError("Final completion identity differs.")
        _verify_receipts(directory, manifest["files"], _final_files(directory))
        result = verify_final_scientific(directory)
        if result != manifest["integrity_result"] or result != metadata["integrity_result"]:
            raise FinalIntegrityError("Final completion reconciliation differs.")
        return result
    except FinalIntegrityError:
        raise
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        raise FinalIntegrityError("No valid final completion manifest.") from exc
