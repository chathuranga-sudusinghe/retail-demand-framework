"""Issue #108: validation-scoped model-ready data handoffs; no estimator or experiment."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import re
from typing import Any

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from src.forecasting.artifacts import PROTOCOL_VERSION, file_hash, json_text
from src.forecasting.authorization import ExecutionBlocked
from src.forecasting.configuration import PRIMARY_MODELS, SUPPORTIVE_MODELS
from src.forecasting.evaluation import frame_hash, prepare_fold
from src.forecasting.execution import FORECAST_INPUT_COLUMNS, forecasting_projection, load_projection
from src.forecasting.features import CONCEPTUAL_FEATURE_COLUMNS, FEATURE_COLUMNS, KEY_COLUMNS
from src.forecasting.metadata import git_state, source_hashes
from src.forecasting.paths import REPOSITORY, RepositoryLayout, confined_path
from src.forecasting.preprocessing import preprocessor_state, restore_preprocessor
from src.forecasting.targets import FORECAST_HORIZONS
from src.forecasting.validation import FINAL_HOLDOUT, VALIDATION_FOLDS

SCHEMA_VERSION = "forecasting-model-ready-v1"
METADATA_VERSION = "forecasting-model-ready-metadata-v1"
METADATA_FILE = "model-ready.json"
MODELS = (*PRIMARY_MODELS, *SUPPORTIVE_MODELS)


@dataclass(frozen=True)
class ModelReadyResult:
    directory: Path
    metadata_sha256: str


def _directory(layout: RepositoryLayout, representation_id: str) -> Path:
    if not isinstance(representation_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", representation_id):
        raise ValueError("representation_id must be a safe single path component.")
    if representation_id.endswith(".") or representation_id.split(".")[0].upper() in {
        "CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(1, 10)], *[f"LPT{i}" for i in range(1, 10)],
    }:
        raise ValueError("representation_id must not be a reserved path component.")
    directory = layout.repository_path(f"data/processed/model-ready/{representation_id}")
    if directory.resolve() != directory:
        raise ValueError("Model-ready data paths must not redirect through symlinks.")
    return directory


def _parquet(directory: Path, relative: str, frame: pd.DataFrame, kind: str) -> dict[str, Any]:
    if frame.isna().any().any() or frame.duplicated(list(KEY_COLUMNS)).any():
        raise ValueError("Model-ready tables require complete unique native keys; no repair is allowed.")
    fields = [pa.field(field.name, pa.date32() if field.name == "Date" else field.type, nullable=False)
              for field in pa.Schema.from_pandas(frame, preserve_index=False)]
    table = pa.Table.from_pandas(frame, schema=pa.schema(fields), preserve_index=False, safe=True)
    table = table.replace_schema_metadata(None)
    path = confined_path(directory, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, path, compression="snappy", version="2.6")
    record = {"kind": kind, "row_count": len(frame), "columns": list(frame.columns),
              "schema": [{"name": field.name, "storage_type": str(field.type), "nullable": field.nullable,
                          "pandas_dtype": str(frame[field.name].dtype)} for field in table.schema],
              "logical_fingerprint": frame_hash(frame), "sha256": file_hash(path), "size_bytes": path.stat().st_size}
    pd.testing.assert_frame_equal(frame, _read_table(path, record), check_exact=True)
    return record


def _read_table(path: Path, record: dict[str, Any]) -> pd.DataFrame:
    if path.is_symlink() or file_hash(path) != record["sha256"] or path.stat().st_size != record["size_bytes"]:
        raise ValueError("Model-ready Parquet hash/size mismatch.")
    table = pq.ParquetFile(path).read()
    if table.schema.names != record["columns"] or table.schema.metadata or len(table) != record["row_count"]:
        raise ValueError("Model-ready schema/population mismatch.")
    frame = table.to_pandas(date_as_object=False)
    for field, definition in zip(table.schema, record["schema"], strict=True):
        if (field.name != definition["name"] or str(field.type) != definition["storage_type"]
                or field.nullable or definition["nullable"] is not False or table[field.name].null_count):
            raise ValueError("Model-ready physical schema/missingness mismatch.")
        frame[field.name] = frame[field.name].astype(definition["pandas_dtype"])
    if frame.duplicated(list(KEY_COLUMNS)).any() or frame_hash(frame) != record["logical_fingerprint"]:
        raise ValueError("Model-ready key/fingerprint mismatch.")
    if frame.Date.ge(pd.Timestamp(FINAL_HOLDOUT.start)).any():
        raise ExecutionBlocked("Reserved final-evaluation data cannot be read as model-ready validation data.")
    return frame


def prepare_model_ready(*, repository: Path, representation_id: str, fold_number: int,
                        stage: str = "validation", expected_provenance_sha256: str | None = None) -> ModelReadyResult:
    """Prepare one frozen fold/all horizons, with training-only learned representations.

    This data-preparation command grants no execution gate, selection freeze or
    final-period access. The project owner must authorize a real preparation run.
    """
    if stage != "validation" or type(fold_number) is not int or fold_number not in (1, 2, 3, 4):
        raise ExecutionBlocked("Only validation folds 1 through 4 may be prepared; final evaluation is blocked.")
    layout = RepositoryLayout(repository)
    directory = _directory(layout, representation_id)
    if directory.exists():
        raise FileExistsError("Model-ready representation already exists; no overwrite or resume is allowed.")
    loaded = load_projection(layout, fold_number=fold_number,
                             expected_provenance_sha256=expected_provenance_sha256)
    # Delegates ALL feature, target, eligibility, chronology and preprocessing logic.
    prepared = prepare_fold(loaded.frame, fold_number)
    fold = prepared.fold
    metadata: dict[str, Any] = {
        "metadata_version": METADATA_VERSION, "schema_version": SCHEMA_VERSION,
        "representation_id": representation_id, "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "forecasting model-ready preparation", "evaluation_stage": "validation",
        "human_review": {"status": "pending_human_review", "reference": None},
        "experiment_execution": "not_performed", "model_training": "not_performed",
        "scope": {"fold_id": fold_number, "training_start": fold.training.start.isoformat(),
                  "training_end": fold.training.end.isoformat(), "forecast_origin": fold.training.end.isoformat(),
                  "validation_start": fold.validation.start.isoformat(), "validation_end": fold.validation.end.isoformat(),
                  "horizons": list(FORECAST_HORIZONS), "date_key_meaning": "first_target_day_not_origin",
                  "reserved_final": {"start": FINAL_HOLDOUT.start.isoformat(), "end": FINAL_HOLDOUT.end.isoformat(),
                                     "status": "blocked_not_materialized"}},
        "parent": {"directory": layout.dataset.parent.relative_to(layout.root).as_posix(),
                   "data_version": loaded.provenance["data_version"],
                   "schema_version": loaded.provenance["schema_version"], "rule_version": loaded.provenance["rule_version"],
                   "metadata_version": loaded.provenance["metadata_version"],
                   "provenance_sha256": loaded.provenance_sha256,
                   "files": loaded.provenance["files"], "source_receipt": loaded.provenance["source"],
                   "scope": loaded.scope, "projection_fingerprint": frame_hash(loaded.frame)},
        "protocol": {"version": PROTOCOL_VERSION, "path": "docs/protocol.md", "sha256": file_hash(layout.protocol),
                     "feature_contract_path": "docs/forecasting-feature-engineering.md",
                     "feature_contract_sha256": file_hash(layout.feature_contract)},
        "implementation": {**git_state(layout.root), "source_hashes": source_hashes(layout.root)},
        "environment": {"python": platform.python_version(), "pandas": pd.__version__,
                        "numpy": np.__version__, "pyarrow": pa.__version__},
        "native_key": list(KEY_COLUMNS), "row_order": list(KEY_COLUMNS),
        "forecast_input_columns": list(FORECAST_INPUT_COLUMNS),
        "conceptual_predictors": list(CONCEPTUAL_FEATURE_COLUMNS), "numerical_predictors": list(FEATURE_COLUMNS),
        "pair_key_hash": prepared.pair_key_hash, "files": {}, "horizons": {},
    }
    directory.parent.mkdir(parents=True, exist_ok=True)
    directory.mkdir(exist_ok=False)
    # Failure leaves an incomplete exclusive version with no completed metadata.
    files = metadata["files"]
    files["projection.parquet"] = _parquet(directory, "projection.parquet", loaded.frame, "forecasting_projection")
    files["origin-features.parquet"] = _parquet(directory, "origin-features.parquet", prepared.origin_features, "conceptual_features")
    for horizon in FORECAST_HORIZONS:
        population = prepared.horizons[horizon]
        prefix = f"h{horizon}"
        target_column = f"target_{horizon}_day"
        features = population.features
        training_targets = features.loc[:, list(KEY_COLUMNS)].copy()
        training_targets[target_column] = population.labels
        validation_targets = prepared.origin_features.loc[:, list(KEY_COLUMNS)].copy()
        validation_targets[target_column] = population.observed_targets
        tables = (("training-features.parquet", features, "conceptual_features"),
                  ("training-targets.parquet", training_targets, "historical_targets"),
                  ("validation-targets.parquet", validation_targets, "validation_outcomes"))
        for name, frame, kind in tables:
            relative = f"{prefix}/{name}"
            files[relative] = _parquet(directory, relative, frame, kind)
        horizon_metadata: dict[str, Any] = {
            "training_population_hash": population.training_population_hash,
            "target_column": target_column, "target_start": fold.validation.start.isoformat(),
            "target_end": (pd.Timestamp(fold.training.end) + pd.Timedelta(days=horizon)).date().isoformat(),
            "eligibility": population.eligibility_records, "representations": {},
        }
        metadata["horizons"][str(horizon)] = horizon_metadata
        for model in MODELS:
            state = population.preprocessors[model]
            state_path = f"{prefix}/{model}/preprocessing.json"
            destination = confined_path(directory, state_path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(json_text(preprocessor_state(state)), encoding="utf-8")
            restored = restore_preprocessor(json.loads(destination.read_text(encoding="utf-8")))
            if restored != state:
                raise ValueError("Persisted preprocessing state changed during readback.")
            files[state_path] = {"kind": "fitted_preprocessing", "sha256": file_hash(destination),
                                 "size_bytes": destination.stat().st_size}
            for name, raw in (("training-matrix.parquet", features), ("origin-matrix.parquet", prepared.origin_features)):
                matrix = pd.concat([raw.loc[:, list(KEY_COLUMNS)], restored.transform(raw)], axis=1)
                relative = f"{prefix}/{model}/{name}"
                files[relative] = _parquet(directory, relative, matrix, "encoded_predictors")
            horizon_metadata["representations"][model] = {
                "preprocessing_path": state_path, "training_row_count": state.training_row_count,
                "training_population_hash": population.training_population_hash,
                "physical_feature_names": list(state.physical_feature_names),
                "physical_feature_count": state.physical_feature_count,
                "training_matrix": f"{prefix}/{model}/training-matrix.parquet",
                "origin_matrix": f"{prefix}/{model}/origin-matrix.parquet",
            }
    current = load_projection(layout, fold_number=fold_number, expected_provenance_sha256=loaded.provenance_sha256)
    if frame_hash(current.frame) != metadata["parent"]["projection_fingerprint"]:
        raise ValueError("Validated forecasting projection changed during preparation.")
    metadata.update(publication_status="complete", readback_status="passed")
    # Preparation metadata is published last, never a forecasting run manifest.
    with (directory / METADATA_FILE).open("x", encoding="utf-8") as stream:
        stream.write(json_text(metadata))
    result = ModelReadyResult(directory, file_hash(directory / METADATA_FILE))
    read_model_ready(repository=repository, representation_id=representation_id, expected_metadata_sha256=result.metadata_sha256)
    return result


def read_model_ready(*, repository: Path, representation_id: str,
                     expected_metadata_sha256: str | None = None) -> tuple[dict[str, Any], dict[str, pd.DataFrame]]:
    """Verify persisted preparation files; no parent outcomes, fitting, or experiments."""
    directory = _directory(RepositoryLayout(repository), representation_id)
    path = directory / METADATA_FILE
    if path.is_symlink() or not path.is_file():
        raise ValueError("Incomplete model-ready representation.")
    if expected_metadata_sha256 is not None and file_hash(path) != expected_metadata_sha256:
        raise ValueError("Model-ready metadata hash mismatch.")
    metadata = json.loads(path.read_text(encoding="utf-8"))
    if (metadata["schema_version"] != SCHEMA_VERSION or metadata["metadata_version"] != METADATA_VERSION
            or metadata["representation_id"] != representation_id or metadata["evaluation_stage"] != "validation"
            or metadata.get("publication_status") != "complete" or metadata.get("readback_status") != "passed"):
        raise ValueError("Unsupported or incomplete model-ready metadata.")
    number = metadata["scope"]["fold_id"]
    if type(number) is not int or number not in (1, 2, 3, 4):
        raise ExecutionBlocked("Model-ready final evaluation is blocked.")
    fold = VALIDATION_FOLDS[number - 1]
    for key, value in (("training_start", fold.training.start.isoformat()),
                       ("training_end", fold.training.end.isoformat()),
                       ("forecast_origin", fold.training.end.isoformat()),
                       ("validation_start", fold.validation.start.isoformat()),
                       ("validation_end", fold.validation.end.isoformat()),
                       ("horizons", list(FORECAST_HORIZONS))):
        if metadata["scope"].get(key) != value:
            raise ValueError("Model-ready chronology differs from the frozen validation fold.")
    expected = {*metadata["files"], METADATA_FILE}
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    if actual != expected:
        raise ValueError("Model-ready file set mismatch.")
    tables = {}
    for relative, record in metadata["files"].items():
        data_path = confined_path(directory, relative)
        if data_path.is_symlink() or file_hash(data_path) != record["sha256"] or data_path.stat().st_size != record["size_bytes"]:
            raise ValueError("Model-ready file hash/size mismatch.")
        if record["kind"] == "fitted_preprocessing":
            restore_preprocessor(json.loads(data_path.read_text(encoding="utf-8")))
        else:
            tables[relative] = _read_table(data_path, record)
    projection = tables["projection.parquet"]
    pd.testing.assert_frame_equal(projection, forecasting_projection(projection), check_exact=True)
    if (not projection.Date.between(pd.Timestamp(fold.training.start), pd.Timestamp(fold.validation.end)).all()
            or frame_hash(projection) != metadata["parent"]["projection_fingerprint"]):
        raise ValueError("Model-ready projection scope/parent fingerprint differs.")
    origin = tables["origin-features.parquet"]
    feature_columns = [*KEY_COLUMNS, *FEATURE_COLUMNS]
    if list(origin.columns) != feature_columns or not origin.Date.eq(pd.Timestamp(fold.validation.start)).all():
        raise ValueError("Model-ready origin features differ from the frozen contract.")
    for horizon in FORECAST_HORIZONS:
        prefix = f"h{horizon}"
        features = tables[f"{prefix}/training-features.parquet"]
        labels = tables[f"{prefix}/training-targets.parquet"]
        outcomes = tables[f"{prefix}/validation-targets.parquet"]
        target_column = f"target_{horizon}_day"
        if (list(features.columns) != feature_columns or list(labels.columns) != [*KEY_COLUMNS, target_column]
                or list(outcomes.columns) != [*KEY_COLUMNS, target_column]
                or not features.Date.between(pd.Timestamp(fold.training.start), pd.Timestamp(fold.training.end)).all()
                or (features.Date + pd.Timedelta(days=horizon - 1)).gt(pd.Timestamp(fold.training.end)).any()):
            raise ValueError("Model-ready feature/target separation or training chronology differs.")
        if frame_hash(labels) != metadata["horizons"][str(horizon)]["training_population_hash"]:
            raise ValueError("Model-ready training population fingerprint differs.")
        pd.testing.assert_frame_equal(features.loc[:, list(KEY_COLUMNS)], labels.loc[:, list(KEY_COLUMNS)], check_exact=True)
        pd.testing.assert_frame_equal(origin.loc[:, list(KEY_COLUMNS)], outcomes.loc[:, list(KEY_COLUMNS)], check_exact=True)
        for model in MODELS:
            state_path = metadata["horizons"][str(horizon)]["representations"][model]["preprocessing_path"]
            state = restore_preprocessor(json.loads(confined_path(directory, state_path).read_text(encoding="utf-8")))
            if state.model != model or state.horizon != horizon or state.training_end != pd.Timestamp(fold.training.end) or state.training_row_count != len(features):
                raise ValueError("Model-ready preprocessing identity/population differs.")
            for name, raw in (("training-matrix.parquet", features), ("origin-matrix.parquet", origin)):
                matrix = tables[f"{prefix}/{model}/{name}"]
                expected_matrix = pd.concat([raw.loc[:, list(KEY_COLUMNS)], state.transform(raw)], axis=1)
                pd.testing.assert_frame_equal(matrix, expected_matrix, check_exact=True)
    return metadata, tables


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=REPOSITORY)
    parser.add_argument("--representation-id", required=True)
    parser.add_argument("--fold", type=int, required=True)
    parser.add_argument("--stage", default="validation")
    args = parser.parse_args(argv)
    result = prepare_model_ready(repository=args.repository, representation_id=args.representation_id,
                                 fold_number=args.fold, stage=args.stage)
    print(f"Model-ready preparation: {result.directory}; metadata SHA-256: {result.metadata_sha256}")


if __name__ == "__main__":
    main()
