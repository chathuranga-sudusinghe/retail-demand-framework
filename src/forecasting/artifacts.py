"""Exact protocol v2 artifact schemas, exclusive run creation and JSON safety."""
from __future__ import annotations

import csv
import json
from datetime import date, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np

from src.forecasting.selection import record_order
from src.forecasting.paths import RepositoryLayout

SCHEMA_VERSION = "issue-65-v2"
PROTOCOL_VERSION = "issue-65-matched-frozen-1"
FOLD_COLUMNS = (
    "run_id", "evaluation_stage", "evidence_role", "model", "horizon", "configuration_id",
    "canonical_config_id", "fold_id", "training_start", "training_end", "forecast_origin",
    "target_start_date", "target_end_date", "n_predictions", "wape", "mae", "rmse", "bias",
    "wape_denominator", "metric_status", "failure_reason",
)
SUMMARY_COLUMNS = (
    "run_id", "evaluation_stage", "evidence_role", "model", "horizon", "configuration_id",
    "canonical_config_id", "expected_fold_count", "valid_fold_count", "n_predictions",
    "mean_wape", "mean_mae", "mean_rmse", "mean_bias", "metric_status", "failure_reason",
    "selected_configuration", "selection_status", "review_status",
)
PREDICTION_COLUMNS = (
    "run_id", "evaluation_stage", "evidence_role", "fold_id", "model", "horizon",
    "configuration_id", "canonical_config_id", "SKU_ID", "Warehouse_ID", "training_start",
    "training_end", "forecast_origin", "target_start_date", "target_end_date", "prediction",
    "observed_target", "prediction_status", "target_status", "eligibility_status",
    "selected_configuration", "selection_status", "representation_id",
)
ELIGIBILITY_COLUMNS = (
    "run_id", "evaluation_stage", "evidence_role", "model", "horizon", "fold_id", "SKU_ID",
    "Warehouse_ID", "raw_row_count", "feature_eligible_count", "label_eligible_count",
    "training_row_count", "expected_origin_count", "scored_origin_count", "exclusion_reason",
    "reason_count", "overlapping_reasons",
)
CSV_SCHEMAS = {"fold_metrics.csv": FOLD_COLUMNS, "configuration_summary.csv": SUMMARY_COLUMNS,
               "predictions.csv": PREDICTION_COLUMNS, "eligibility_counts.csv": ELIGIBILITY_COLUMNS}
ARTIFACT_NAMES = ("run_metadata.json", "fold_metrics.csv", "configuration_summary.csv",
                  "selected_configurations.json", "predictions.csv", "eligibility_counts.csv", "comparison.md")


def file_hash(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_value(value: Any) -> Any:
    """Normalise numpy scalars/arrays; reject NaN/infinity rather than hiding them."""
    if isinstance(value, dict):
        return {str(k): json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(v) for v in value]
    if isinstance(value, np.ndarray):
        return json_value(value.tolist())
    if isinstance(value, np.generic):
        return json_value(value.item())
    if isinstance(value, datetime):
        return value.date().isoformat() if value.tzinfo is None and value.time() == datetime.min.time() else value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, float) and not np.isfinite(value):
        raise ValueError("Nonfinite number cannot be written to a protocol artifact.")
    return value


def json_text(value: Any) -> str:
    return json.dumps(json_value(value), indent=2, allow_nan=False, ensure_ascii=False) + "\n"


def require_mutable_run(directory: Path) -> None:
    """Use the completion manifest as the shared persistence boundary."""
    layout = RepositoryLayout.from_artifact_directory(directory)
    manifest = layout._owned_path(directory / "run_manifest.json")
    if manifest.exists():
        raise FileExistsError("A published run cannot be modified.")


class ArtifactWriter:
    """Own one artifact anchor and its model/draft directories; never reuse a run."""

    def __init__(self, repository: Path | RepositoryLayout, run_id: str):
        self.layout = RepositoryLayout(repository) if isinstance(repository, Path) else repository
        self.repository = self.layout.root
        self.directory = self.layout.run_directory(run_id)
        self.model_directory = self.layout.model_run_directory(run_id)
        self.report_directory = self.layout.draft_report_directory(run_id)
        directories = (self.directory, self.model_directory, self.report_directory)
        for directory in directories:
            if directory.exists():
                raise FileExistsError("Forecasting run storage already exists.")
        for directory in directories:
            directory.parent.mkdir(parents=True, exist_ok=True)
            directory.mkdir(exist_ok=False)

    def _require_mutable(self) -> None:
        require_mutable_run(self.directory)

    def _path(self, name: str) -> Path:
        directory = (self.layout.draft_report_directory(self.directory.name)
                     if name == "comparison.md" else self.layout.run_directory(self.directory.name))
        return self.layout._owned_path(directory / name)

    def write_json(self, name: str, value: Any) -> None:
        self._require_mutable()
        if name not in ("run_metadata.json", "selected_configurations.json", "diagnostics.json",
                        "authorization.json", "run_manifest.json"):
            raise ValueError("Unknown JSON artifact.")
        encoded = json_text(value)
        path = self._path(name)
        temporary = self.layout._owned_path(path.with_name(name + ".tmp"))
        temporary.write_text(encoded, encoding="utf-8")
        temporary.replace(path)

    def write_csv(self, name: str, rows: list[dict[str, Any]]) -> None:
        self._require_mutable()
        columns = CSV_SCHEMAS[name]
        ordered = sorted(rows, key=record_order)
        for row in ordered:
            if set(row) != set(columns):
                raise ValueError(f"Artifact {name} does not match the frozen schema.")
            json_value(row)
        path = self._path(name)
        temporary = self.layout._owned_path(path.with_name(name + ".tmp"))
        with temporary.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
            writer.writeheader()
            for row in ordered:
                values = json_value(row)
                for key, value in values.items():
                    if isinstance(value, bool):
                        values[key] = "true" if value else "false"
                    elif isinstance(value, list):
                        values[key] = json.dumps(value, allow_nan=False, separators=(",", ":"))
                writer.writerow(values)
        temporary.replace(path)

    def write_comparison(self, text: str) -> None:
        self._require_mutable()
        path = self._path("comparison.md")
        temporary = self.layout._owned_path(path.with_name("comparison.md.tmp"))
        temporary.write_text(text, encoding="utf-8")
        temporary.replace(path)

    def manifest(self) -> list[dict[str, Any]]:
        records = []
        for name in ARTIFACT_NAMES:
            path = self._path(name)
            exists = path.is_file()
            # A manifest cannot hash the full file that contains that same hash.
            # All other artifact hashes are complete byte hashes.
            records.append({"artifact_path": path.relative_to(self.repository).as_posix(),
                            "artifact_hash": file_hash(path) if exists and name != "run_metadata.json" else None,
                            "artifact_status": "self_reference" if exists and name == "run_metadata.json" else (
                                "written" if exists else "not_written"),
                            "diagnostic_paths": [str((self.directory / "diagnostics.json").relative_to(self.repository))]
                            if (self.directory / "diagnostics.json").exists() else []})
        return records
