"""Exact human authorization for the separate Issue #130 final path.

Imports and record parsing never authorize fitting or reveal outcomes.
DR-014 is the sole source of primary selections and the producer mapping.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from datetime import timedelta
import json
from pathlib import Path
import re
from typing import Any

from src.forecasting.artifacts import file_hash
from src.forecasting.authorization import ExecutionBlocked
from src.forecasting.baselines import BASELINE_MODELS
from src.forecasting.configuration import PRIMARY_GRID, PRIMARY_MODELS, SUPPORTIVE_MODELS, CanonicalConfiguration
from src.forecasting.integrity import verify_completed
from src.forecasting.metadata import LIBRARIES, runtime_versions
from src.forecasting.paths import DEFAULT_LAYOUT, RepositoryLayout
from src.forecasting.targets import FORECAST_HORIZONS
from src.forecasting.validation import FINAL_HOLDOUT, VALIDATION_FOLDS

FREEZE_PATH = "docs/decisions/DR-014-forecasting-selection-and-final-refit.md"
POLICY_PATH = "docs/forecasting-final-evaluation.md"
FINAL_RECORD_PATH = "data/processed/forecasting/final_authorization.json"
FINAL_SCHEMA = "issue-130-final-v1"
TRAINING_START = VALIDATION_FOLDS[0].training.start.isoformat()
TRAINING_END = (FINAL_HOLDOUT.start - timedelta(days=1)).isoformat()
TEMPORAL_POLICY = {
    "training_start": TRAINING_START, "training_end": TRAINING_END,
    "forecast_origin": TRAINING_END, "target_start_date": FINAL_HOLDOUT.start.isoformat(),
    "outcome_window_end": FINAL_HOLDOUT.end.isoformat(),
}
REFERENCE_NAMES = {"protocol", "human_freeze", "refit_policy", "implementation_acceptance", "specific_final_run"}


def read_json(path: Path) -> Any:
    """Reject duplicate keys and nonfinite JSON rather than silently normalizing."""
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON field.")
            result[key] = value
        return result

    def invalid_constant(value: str) -> Any:
        raise ValueError("Nonfinite JSON constant: " + value)

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique,
                      parse_constant=invalid_constant)


@dataclass(frozen=True)
class FinalCandidate:
    model: str
    horizon: int
    configuration_id: str

    @property
    def configuration(self) -> CanonicalConfiguration | None:
        if self.model in PRIMARY_MODELS:
            return next(c for c in PRIMARY_GRID if c.canonical_config_id == self.configuration_id)
        return None

    @property
    def learned(self) -> bool:
        return self.model in (*PRIMARY_MODELS, *SUPPORTIVE_MODELS)

    @property
    def key(self) -> tuple[str, int, str]:
        return self.model, self.horizon, self.configuration_id


@dataclass(frozen=True)
class ReviewedFreeze:
    candidates: tuple[FinalCandidate, ...]
    producer_mapping: tuple[dict[str, Any], ...]
    validation_run_id: str
    validation_manifest_sha256: str


def _table(text: str, heading: str, columns: tuple[str, ...]) -> list[list[str]]:
    parts = text.split("## " + heading + "\n")
    if len(parts) != 2:
        raise ValueError("Missing or repeated DR-014 section.")
    section = parts[1].split("\n## ", 1)[0]
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")]
            for line in section.splitlines() if line.startswith("|")]
    if len(rows) < 3 or tuple(rows[0]) != columns or any(len(r) != len(columns) for r in rows):
        raise ValueError("DR-014 table schema differs.")
    if any(not re.fullmatch(r":?-+:?", cell) for cell in rows[1]):
        raise ValueError("DR-014 table separator differs.")
    return rows[2:]


def read_freeze(path: Path) -> ReviewedFreeze:
    """Read the reviewed tables, never select from scores or duplicate their IDs."""
    try:
        text = path.read_text(encoding="utf-8")
        primary = _table(text, "Frozen primary research configurations",
                         ("Horizon", "XGBoost", "LightGBM", "CatBoost"))
        producers = _table(text, "Separate downstream forecasting-framework producer decision",
                           ("Horizon", "Producer model", "Configuration"))
        expected_days = [f"{h} day" if h == 1 else f"{h} days" for h in FORECAST_HORIZONS]
        # Reviewed tables use singular 'day' in the 1-day row.
        if [r[0] for r in primary] != expected_days or [r[0] for r in producers] != expected_days:
            raise ValueError("DR-014 must contain exactly the four ordered horizons.")
        ids = {c.canonical_config_id for c in PRIMARY_GRID}
        if any(c not in ids for row in primary for c in row[1:]):
            raise ValueError("DR-014 configuration is outside the frozen grid.")
        candidates = tuple(
            FinalCandidate(model, h, primary[i][j + 1])
            for j, model in enumerate(PRIMARY_MODELS) for i, h in enumerate(FORECAST_HORIZONS)
        ) + tuple(FinalCandidate(model, h, "fixed") for model in SUPPORTIVE_MODELS for h in FORECAST_HORIZONS
                  ) + tuple(FinalCandidate(model, h, "not_tuned") for model in BASELINE_MODELS for h in FORECAST_HORIZONS)
        names = dict(zip(("XGBoost", "LightGBM", "CatBoost"), PRIMARY_MODELS, strict=True))
        mapping = tuple({"horizon": h, "model": names[row[1]], "configuration_id": row[2]}
                        for h, row in zip(FORECAST_HORIZONS, producers, strict=True))
        if any((r["model"], r["horizon"], r["configuration_id"]) not in {c.key for c in candidates} for r in mapping):
            raise ValueError("Producer must be a frozen primary candidate at its horizon.")
        runs = re.findall(r"^\| Run ID \| `([A-Za-z0-9][A-Za-z0-9_.-]{0,63})` \|$", text, re.MULTILINE)
        hashes = re.findall(r"```text\n([0-9a-f]{64})\n```", text)
        if len(runs) != 1 or len(hashes) != 1:
            raise ValueError("DR-014 must identify one exact validation manifest.")
        return ReviewedFreeze(candidates, mapping, runs[0], hashes[0])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ExecutionBlocked("Malformed or unavailable reviewed DR-014 freeze.") from exc


def _digest(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch("[0-9a-f]{64}", value) is not None


@dataclass(frozen=True)
class FinalAuthorization:
    run_id: str
    evaluation_stage: str
    final_run_authorized: bool
    freeze_hash: str
    policy_hash: str
    protocol_hash: str
    feature_contract_hash: str
    requirements_hash: str
    source_hashes: dict[str, str]  # Creation-time provenance, never an execution-permission binding.
    validation_run_id: str
    validation_manifest_sha256: str
    input_view_hash: str
    validated_provenance_hash: str
    python_version: str
    library_versions: dict[str, str]
    approval_references: dict[str, str]
    temporal_policy: dict[str, str]
    candidates: tuple[FinalCandidate, ...]
    producer_mapping: tuple[dict[str, Any], ...]
    worker_count: int

    @classmethod
    def from_payload(cls, payload: Any) -> FinalAuthorization:
        try:
            if not isinstance(payload, dict) or set(payload) != {f.name for f in fields(cls)}:
                raise ValueError("Final authorization fields differ.")
            value = dict(payload)
            if not isinstance(value["candidates"], list) or any(
                not isinstance(c, dict) or set(c) != {"model", "horizon", "configuration_id"}
                or type(c["horizon"]) is not int for c in value["candidates"]
            ):
                raise ValueError("Final candidate declarations differ.")
            value["candidates"] = tuple(FinalCandidate(**c) for c in value["candidates"])
            if not isinstance(value["producer_mapping"], list) or any(
                not isinstance(r, dict) or set(r) != {"model", "horizon", "configuration_id"}
                or type(r["horizon"]) is not int for r in value["producer_mapping"]
            ):
                raise ValueError("Producer declarations differ.")
            value["producer_mapping"] = tuple(value["producer_mapping"])
            result = cls(**value)
            result.check_types()
            return result
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            raise ExecutionBlocked("Missing or malformed human final authorization.") from exc

    def check_types(self) -> None:
        if (self.evaluation_stage != "final_evaluation" or self.final_run_authorized is not True
                or not isinstance(self.run_id, str) or not isinstance(self.validation_run_id, str)
                or self.run_id == self.validation_run_id or self.python_version != "3.12.3"
                or type(self.worker_count) is not int or self.worker_count != 1):
            raise ExecutionBlocked("An exact separately authorized final run with frozen runtime controls is required.")
        for name in ("freeze_hash", "policy_hash", "protocol_hash", "feature_contract_hash", "requirements_hash",
                     "validation_manifest_sha256", "input_view_hash", "validated_provenance_hash"):
            if not _digest(getattr(self, name)):
                raise ExecutionBlocked("Final authorization needs exact SHA-256 bindings.")
        if (not isinstance(self.source_hashes, dict) or not self.source_hashes
                or any(not isinstance(k, str) or not _digest(v) for k, v in self.source_hashes.items())
                or not isinstance(self.library_versions, dict) or set(self.library_versions) != set(LIBRARIES)
                or any(not isinstance(v, str) or not v.strip() for v in self.library_versions.values())
                or self.temporal_policy != TEMPORAL_POLICY):
            raise ExecutionBlocked("Malformed final provenance, environment or temporal record.")
        if (not isinstance(self.approval_references, dict) or set(self.approval_references) != REFERENCE_NAMES
                or any(not isinstance(v, str) or not v.strip() or v.strip().lower() in {"pending", "none", "null"}
                       for v in self.approval_references.values())):
            raise ExecutionBlocked("Human freeze, refit approval, implementation acceptance and specific final-run references are required.")

    def validate(self, layout: RepositoryLayout, *, verify_validation: bool = False,
                 require_unused: bool = False) -> ReviewedFreeze:
        self.check_types()
        freeze = read_freeze(layout.repository_path(FREEZE_PATH))
        if (self.candidates != freeze.candidates or self.producer_mapping != freeze.producer_mapping
                or self.validation_run_id != freeze.validation_run_id
                or self.validation_manifest_sha256 != freeze.validation_manifest_sha256):
            raise ExecutionBlocked("Final authorization differs from the exact reviewed candidate/evidence freeze.")
        paths = {"freeze_hash": FREEZE_PATH, "policy_hash": POLICY_PATH, "protocol_hash": "docs/protocol.md",
                 "feature_contract_hash": "docs/forecasting-feature-engineering.md", "requirements_hash": "requirements.txt"}
        if any(file_hash(layout.repository_path(p)) != getattr(self, field) for field, p in paths.items()):
            raise ExecutionBlocked("Reviewed final documentation or scientific bindings changed.")
        validation = layout.run_directory(self.validation_run_id)
        if file_hash(layout._owned_path(validation / "run_manifest.json")) != self.validation_manifest_sha256:
            raise ExecutionBlocked("Completed validation manifest differs from the human freeze.")
        manifest = read_json(layout._owned_path(validation / "run_manifest.json"))
        retained_path = layout._owned_path(validation / "run_metadata.json")
        if file_hash(retained_path) != manifest["metadata_hash"]:
            raise ExecutionBlocked("Retained validation provenance differs from its frozen manifest.")
        retained = read_json(retained_path)
        for field in ("protocol_hash", "feature_contract_hash", "requirements_hash",
                      "python_version", "library_versions"):
            if retained[field] != getattr(self, field):
                raise ExecutionBlocked("Final scientific/environment bindings differ from completed validation.")
        if retained["dataset_reference"] != layout.dataset.relative_to(layout.root).as_posix():
            raise ExecutionBlocked("Final history must use the accepted validated-data source.")
        if verify_validation:
            verify_completed(validation)
        if self.library_versions != runtime_versions(layout.root):
            raise ExecutionBlocked("Final authorization environment differs from the pinned runtime.")
        if require_unused and any(p.exists() for p in (
            layout.run_directory(self.run_id), layout.model_run_directory(self.run_id),
            layout.draft_report_directory(self.run_id),
        )):
            raise ExecutionBlocked("Final run storage is consumed; use a separately authorized unused ID, never resume or overwrite.")
        return freeze


@dataclass(frozen=True)
class FinalExecutionContext:
    layout: RepositoryLayout
    authorization: FinalAuthorization
    authorization_path: Path
    authorization_bytes: bytes

    def revalidate(self) -> None:
        if self.layout._owned_path(self.authorization_path).read_bytes() != self.authorization_bytes:
            raise ExecutionBlocked("Human final authorization changed during execution.")
        self.authorization.validate(self.layout)


def resolve_final_execution(layout: RepositoryLayout = DEFAULT_LAYOUT) -> FinalExecutionContext:
    """Read only the fixed human record; no dataset load or generated authorization."""
    try:
        path = layout._owned_path(layout.repository_path(FINAL_RECORD_PATH))
        payload = path.read_bytes()
        authorization = FinalAuthorization.from_payload(read_json(path))
        authorization.validate(layout, verify_validation=True, require_unused=True)
        if path.read_bytes() != payload:
            raise ExecutionBlocked("Human final authorization changed while resolving.")
        return FinalExecutionContext(layout, authorization, path, payload)
    except ExecutionBlocked:
        raise
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise ExecutionBlocked("Missing, stale or unverifiable human final authorization.") from exc


def candidate_payload(candidates: tuple[FinalCandidate, ...]) -> list[dict[str, Any]]:
    return [asdict(c) for c in candidates]
