"""Versioned lifecycle views over verified Phase 4 data; no preparation or experiment.

Callers supply the four reviewed model-ready identities and external metadata
hashes. Reserved-final publication is metadata-only and grants no outcome access.
"""
from __future__ import annotations

import argparse
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
from typing import Any

from src.data import validated_handoff
from src.forecasting import model_ready
from src.forecasting.artifacts import PROTOCOL_VERSION, file_hash, json_text
from src.forecasting.evaluation import frame_hash
from src.forecasting.features import KEY_COLUMNS, SERIES_COLUMNS
from src.forecasting.metadata import git_state, source_hashes
from src.forecasting.paths import REPOSITORY, RepositoryLayout, confined_path
from src.forecasting.targets import FORECAST_HORIZONS
from src.forecasting.validation import FINAL_HOLDOUT, VALIDATION_FOLDS

VALIDATION_SCHEMA = "forecasting-validation-views-v1"
RESERVED_FINAL_SCHEMA = "forecasting-reserved-final-view-v1"
VALIDATION_FILE = "views.json"
RESERVED_FINAL_FILE = "view.json"


@dataclass(frozen=True)
class ModelReadyReference:
    representation_id: str
    metadata_sha256: str


@dataclass(frozen=True)
class LifecycleResult:
    validation_directory: Path
    reserved_final_directory: Path
    validation_sha256: str
    reserved_final_sha256: str


def _component(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", value):
        raise ValueError("Lifecycle versions and representation IDs require safe single path components.")
    if value.endswith(".") or value.split(".")[0].upper() in {
        "CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(1, 10)], *[f"LPT{i}" for i in range(1, 10)],
    }:
        raise ValueError("Reserved path components are not allowed.")
    return value


def _digest(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError("An external SHA-256 receipt is required.")
    return value


def _path(layout: RepositoryLayout, relative: str) -> Path:
    # Reuse the Phase 5 owner check, including redirects within the repository.
    return layout._owned_path(layout.repository_path(relative))


def _directories(layout: RepositoryLayout, version: str) -> tuple[Path, Path]:
    version = _component(version)
    return (_path(layout, f"data/processed/validation/{version}"),
            _path(layout, f"data/processed/reserved-final/{version}"))


def _references(representations: Mapping[int, ModelReadyReference]) -> None:
    if (any(type(number) is not int for number in representations)
            or set(representations) != {fold.number for fold in VALIDATION_FOLDS}):
        raise ValueError("Exactly the four authoritative validation folds are required.")
    for reference in representations.values():
        _component(reference.representation_id)
        _digest(reference.metadata_sha256)
    if len({reference.representation_id for reference in representations.values()}) != len(VALIDATION_FOLDS):
        raise ValueError("Each fold requires its own explicit model-ready representation.")


def _parent(layout: RepositoryLayout, metadata: dict[str, Any]) -> dict[str, Any]:
    """Verify receipt/byte identity without decoding or fingerprinting parent outcomes."""
    directory = _path(layout, layout.dataset.parent.relative_to(layout.root).as_posix())
    if metadata["directory"] != directory.relative_to(layout.root).as_posix():
        raise ValueError("Validated parent is not at the authoritative handoff path.")
    paths = {name: _path(layout, (directory / name).relative_to(layout.root).as_posix())
             for name in validated_handoff.FILES}
    if {p.name for p in directory.iterdir()} != set(paths):
        raise ValueError("Incomplete or unexpected validated parent files.")
    if file_hash(paths["provenance.json"]) != _digest(metadata["provenance_sha256"]):
        raise ValueError("Validated parent provenance hash differs.")
    provenance = json.loads(paths["provenance.json"].read_text(encoding="utf-8"))
    expected = {"data_version": validated_handoff.PROJECT_DATA_VERSION,
                "schema_version": validated_handoff.SCHEMA_VERSION,
                "rule_version": validated_handoff.RULE_VERSION,
                "metadata_version": validated_handoff.METADATA_VERSION}
    for key, value in expected.items():
        if metadata[key] != value or provenance[key] != value:
            raise ValueError("Validated parent identity/schema differs.")
    if (provenance.get("publication_status") != "complete"
            or provenance.get("readback_status") != "passed" or provenance.get("validation_status") != "passed"
            or metadata["files"] != provenance["files"] or metadata["source_receipt"] != provenance["source"]):
        raise ValueError("Incomplete or inconsistent validated parent receipts.")
    if (provenance["scope"]["start_date"] > VALIDATION_FOLDS[0].training.start.isoformat()
            or provenance["scope"]["end_date"] < FINAL_HOLDOUT.end.isoformat()):
        raise ValueError("Validated parent does not identify the complete lifecycle interval.")
    for name in validated_handoff.FILES[:-1]:
        record = provenance["files"][name]
        if (record["path"] != name or file_hash(paths[name]) != _digest(record["sha256"])
                or paths[name].stat().st_size != record["size_bytes"]):
            raise ValueError("Validated parent file hash/size/path differs.")
    # Intentionally exclude whole-year logical fingerprints, quantities and audit contents.
    return {"directory": metadata["directory"], **expected,
            "provenance_sha256": metadata["provenance_sha256"],
            "files": metadata["files"], "source_receipt": metadata["source_receipt"]}


def _file_reference(layout: RepositoryLayout, directory: Path, relative: str,
                    metadata: dict[str, Any]) -> dict[str, Any]:
    path = confined_path(directory, relative)
    _path(layout, path.relative_to(layout.root).as_posix())
    record = metadata["files"][relative]
    if record.get("path", relative) != relative:
        raise ValueError("Model-ready file receipt path differs.")
    return {**record, "path": path.relative_to(layout.root).as_posix()}


def _fold_view(layout: RepositoryLayout, number: int, reference: ModelReadyReference) -> tuple[dict[str, Any], dict[str, Any]]:
    directory = _path(layout, f"data/processed/model-ready/{reference.representation_id}")
    metadata_path = _path(layout, (directory / model_ready.METADATA_FILE).relative_to(layout.root).as_posix())
    if file_hash(metadata_path) != reference.metadata_sha256:
        raise ValueError("Model-ready metadata hash differs.")
    receipt = json.loads(metadata_path.read_text(encoding="utf-8"))
    for relative in receipt["files"]:
        _file_reference(layout, directory, relative, receipt)
    metadata, tables = model_ready.read_model_ready(
        repository=layout.root, representation_id=reference.representation_id,
        expected_metadata_sha256=reference.metadata_sha256,
    )
    if metadata["scope"]["fold_id"] != number:
        raise ValueError("Model-ready representation is assigned to the wrong fold.")
    if metadata["native_key"] != list(KEY_COLUMNS) or metadata["row_order"] != list(KEY_COLUMNS):
        raise ValueError("Model-ready native key/order differs.")
    origin = tables["origin-features.parquet"]
    if metadata["pair_key_hash"] != frame_hash(origin.loc[:, list(SERIES_COLUMNS)]):
        raise ValueError("Model-ready origin population identity differs.")
    fold = VALIDATION_FOLDS[number - 1]
    horizons = {}
    for horizon in FORECAST_HORIZONS:
        record = metadata["horizons"][str(horizon)]
        start = fold.validation.start.isoformat()
        end = (fold.training.end + timedelta(days=horizon)).isoformat()
        if (record["target_column"] != f"target_{horizon}_day"
                or record["target_start"] != start or record["target_end"] != end):
            raise ValueError("Model-ready horizon/target interval differs.")
        for model in model_ready.MODELS:
            representation = record["representations"][model]
            prefix = f"h{horizon}/{model}"
            if any(representation[key] != f"{prefix}/{name}" for key, name in (
                ("preprocessing_path", "preprocessing.json"), ("training_matrix", "training-matrix.parquet"),
                ("origin_matrix", "origin-matrix.parquet"),
            )):
                raise ValueError("Model-ready preprocessing/matrix references differ.")
        horizons[str(horizon)] = {
            "target_column": record["target_column"], "target_start": start, "target_end": end,
            "training_population_hash": record["training_population_hash"],
            "validation_targets": _file_reference(layout, directory, f"h{horizon}/validation-targets.parquet", metadata),
            # Paths below are relative to the hash-anchored model-ready directory.
            "representations": record["representations"],
        }
    if file_hash(metadata_path) != reference.metadata_sha256:
        raise ValueError("Model-ready metadata changed during lifecycle verification.")
    return ({"fold_id": number,
             "model_ready": {"representation_id": reference.representation_id,
                             "directory": directory.relative_to(layout.root).as_posix(),
                             "metadata_path": metadata_path.relative_to(layout.root).as_posix(),
                             "metadata_sha256": reference.metadata_sha256,
                             "schema_version": metadata["schema_version"], "metadata_version": metadata["metadata_version"]},
             "scope": metadata["scope"], "native_key": metadata["native_key"], "row_order": metadata["row_order"],
             "pair_key_hash": metadata["pair_key_hash"],
             "projection_fingerprint": metadata["parent"]["projection_fingerprint"],
             "origin_features": _file_reference(layout, directory, "origin-features.parquet", metadata),
             "horizons": horizons}, metadata)


def _definitions(layout: RepositoryLayout, version: str, representations: Mapping[int, ModelReadyReference],
                 generation: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    _references(representations)
    views = []
    parents = []
    protocol = {"version": PROTOCOL_VERSION, "path": "docs/protocol.md", "sha256": file_hash(layout.protocol),
                "feature_contract_path": "docs/forecasting-feature-engineering.md",
                "feature_contract_sha256": file_hash(layout.feature_contract)}
    for fold in VALIDATION_FOLDS:
        view, metadata = _fold_view(layout, fold.number, representations[fold.number])
        if metadata["protocol"] != protocol:
            raise ValueError("Model-ready protocol/feature-contract provenance differs.")
        parents.append({key: metadata["parent"][key] for key in (
            "directory", "data_version", "schema_version", "rule_version", "metadata_version",
            "provenance_sha256", "files", "source_receipt",
        )})
        views.append(view)
    if any(parent != parents[0] for parent in parents[1:]):
        raise ValueError("The four model-ready folds must share the exact validated parent.")
    parent = _parent(layout, parents[0])
    common = {"lifecycle_version": version, "generation": generation, "protocol": protocol,
              "validated_parent": parent, "publication_status": "complete",
              "human_review": {"status": "pending_human_review", "reference": None}}
    validation = {**common, "schema_version": VALIDATION_SCHEMA, "evaluation_stage": "validation", "folds": views}
    reserved = {**common, "schema_version": RESERVED_FINAL_SCHEMA, "evaluation_stage": "reserved-final",
                "interval": {"start": FINAL_HOLDOUT.start.isoformat(), "end": FINAL_HOLDOUT.end.isoformat()},
                "forecast_origin": (FINAL_HOLDOUT.start - timedelta(days=1)).isoformat(),
                "horizons": list(FORECAST_HORIZONS),
                "access_status": "blocked_pending_separate_human_authorization",
                "evaluation_status": "blocked", "outcomes_status": "not_materialized"}
    return validation, reserved


def publish_lifecycle(*, repository: Path, version: str,
                      representations: Mapping[int, ModelReadyReference]) -> LifecycleResult:
    """Publish views of existing parents only; never prepare, fit, score or grant access.

    Both stage directories are exclusive. Interrupted publication stays incomplete;
    the same version cannot be overwritten, resumed or automatically cleaned up.
    """
    layout = RepositoryLayout(repository)
    validation_directory, reserved_directory = _directories(layout, version)
    if validation_directory.exists() or reserved_directory.exists():
        raise FileExistsError("Lifecycle version already exists; no overwrite or resume is allowed.")
    generation = {"created_at_utc": datetime.now(timezone.utc).isoformat(),
                  "implementation": {**git_state(layout.root), "source_hashes": source_hashes(layout.root)}}
    validation, reserved = _definitions(layout, version, representations, generation)
    for directory in (validation_directory, reserved_directory):
        directory.parent.mkdir(parents=True, exist_ok=True)
        _path(layout, directory.relative_to(layout.root).as_posix()).mkdir(exist_ok=False)
    for directory, name, definition in ((validation_directory, VALIDATION_FILE, validation),
                                        (reserved_directory, RESERVED_FINAL_FILE, reserved)):
        with confined_path(directory, name).open("x", encoding="utf-8") as stream:
            stream.write(json_text(definition))
    result = LifecycleResult(validation_directory, reserved_directory,
                             file_hash(validation_directory / VALIDATION_FILE),
                             file_hash(reserved_directory / RESERVED_FINAL_FILE))
    read_lifecycle(repository=layout.root, version=version, expected_validation_sha256=result.validation_sha256,
                   expected_reserved_final_sha256=result.reserved_final_sha256)
    return result


def read_lifecycle(*, repository: Path, version: str, expected_validation_sha256: str,
                   expected_reserved_final_sha256: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Verify the two definitions and existing parents; never resolve the final view."""
    layout = RepositoryLayout(repository)
    validation_directory, reserved_directory = _directories(layout, version)
    definitions = []
    for directory, name, digest in ((validation_directory, VALIDATION_FILE, expected_validation_sha256),
                                    (reserved_directory, RESERVED_FINAL_FILE, expected_reserved_final_sha256)):
        path = _path(layout, (directory / name).relative_to(layout.root).as_posix())
        if {p.name for p in directory.iterdir()} != {name} or file_hash(path) != _digest(digest):
            raise ValueError("Lifecycle file set/hash differs or publication is incomplete.")
        definitions.append(json.loads(path.read_text(encoding="utf-8")))
    validation, reserved = definitions
    references = {view["fold_id"]: ModelReadyReference(view["model_ready"]["representation_id"],
                                                     view["model_ready"]["metadata_sha256"])
                  for view in validation["folds"]}
    if len(validation["folds"]) != len(VALIDATION_FOLDS):
        raise ValueError("Lifecycle requires exactly four distinct folds.")
    generation = validation["generation"]
    if (set(generation) != {"created_at_utc", "implementation"}
            or datetime.fromisoformat(generation["created_at_utc"]).utcoffset() != timedelta(0)
            or set(generation["implementation"]) != {"git_commit_sha", "git_branch", "git_dirty", "source_hashes"}):
        raise ValueError("Unsupported lifecycle generation metadata.")
    expected = _definitions(layout, version, references, generation)
    if (validation, reserved) != expected:
        raise ValueError("Lifecycle definition differs from verified parents or protected stage contract.")
    return validation, reserved


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=REPOSITORY)
    parser.add_argument("--version", required=True)
    parser.add_argument("--fold-reference", nargs=3, action="append", required=True, metavar=("FOLD", "ID", "SHA256"))
    args = parser.parse_args(argv)
    references = {}
    for number, identity, digest in args.fold_reference:
        fold = int(number)
        if fold in references:
            parser.error("Duplicate fold reference.")
        references[fold] = ModelReadyReference(identity, digest)
    result = publish_lifecycle(repository=args.repository, version=args.version, representations=references)
    print(f"Validation views: {result.validation_directory}; SHA-256: {result.validation_sha256}")
    print(f"Blocked reserved-final view: {result.reserved_final_directory}; SHA-256: {result.reserved_final_sha256}")


if __name__ == "__main__":
    main()
