"""Read human execution records, never manufacture or refresh approval."""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass, fields
from pathlib import Path

import pandas as pd

from src.forecasting.artifacts import PROTOCOL_VERSION, SCHEMA_VERSION, file_hash
from src.forecasting.baselines import BASELINE_MODELS
from src.forecasting.configuration import PRIMARY_MODELS, SUPPORTIVE_MODELS
from src.forecasting.paths import DEFAULT_LAYOUT, RepositoryLayout
from src.forecasting.targets import FORECAST_HORIZONS


class ExecutionBlocked(PermissionError):
    """Implementation/test permission never grants an experiment gate."""


@dataclass(frozen=True)
class RunScope:
    primary_models: tuple[str, ...]
    supportive_models: tuple[str, ...]
    horizons: tuple[int, ...]
    baselines: tuple[str, ...]
    baseline_exclusions: tuple[tuple[str, str], ...]
    baseline_approval_references: tuple[tuple[str, str], ...]

    def validate(self) -> None:
        for supplied, approved in ((self.primary_models, PRIMARY_MODELS),
                                   (self.supportive_models, SUPPORTIVE_MODELS),
                                   (self.horizons, FORECAST_HORIZONS), (self.baselines, BASELINE_MODELS)):
            if tuple(x for x in approved if x in supplied) != supplied:
                raise ExecutionBlocked("Run scope must be an ordered, unique subset of frozen models/horizons.")
        if not self.horizons or not any((self.primary_models, self.supportive_models, self.baselines)):
            raise ExecutionBlocked("Run scope is empty.")
        if any(type(h) is not int for h in self.horizons):
            raise ExecutionBlocked("Horizons must be integers.")
        exclusions = dict(self.baseline_exclusions)
        approvals = dict(self.baseline_approval_references)
        if (len(exclusions) != len(self.baseline_exclusions)
                or len(approvals) != len(self.baseline_approval_references)
                or set(exclusions) != set(BASELINE_MODELS) - set(self.baselines)
                or set(approvals) != set(self.baselines)
                or not all(isinstance(v, str) and v.strip() for v in (*exclusions.values(), *approvals.values()))):
            raise ExecutionBlocked("Every baseline needs explicit execution approval or an exclusion reason.")


@dataclass(frozen=True)
class ValidationAuthorization:
    """Owner-supplied Gate 3/4 record bound to this run, protocol, code and input.

    References are audit evidence supplied by a human, not approvals created by
    the runner. This is a local workflow guard, not a cryptographic identity system.
    No authorization record is bundled with the implementation.
    """

    run_id: str
    evaluation_stage: str
    protocol_version: str
    schema_version: str
    protocol_hash: str
    source_hashes: dict[str, str]
    input_view_hash: str
    protocol_approval_reference: str
    implementation_acceptance_reference: str
    specific_run_reference: str
    validation_run_authorized: bool
    scope: RunScope
    worker_count: int = 1

    @classmethod
    def from_json(cls, path: Path) -> ValidationAuthorization:
        try:
            def unique_object(pairs: list[tuple[str, object]]) -> dict:
                result: dict = {}
                for key, value in pairs:
                    if key in result:
                        raise ValueError("Duplicate execution-record field.")
                    result[key] = value
                return result
            value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
            required = {f.name for f in fields(cls)} - {"worker_count"}
            if not isinstance(value, dict) or not required <= set(value) or set(value) - required - {"worker_count"}:
                raise ValueError("Execution record fields differ.")
            scope = value.pop("scope")
            if not isinstance(scope, dict) or set(scope) != {f.name for f in fields(RunScope)}:
                raise ValueError("Scope fields differ.")
            for key in ("primary_models", "supportive_models", "horizons", "baselines"):
                if not isinstance(scope[key], list):
                    raise ValueError("Scope must use ordered lists.")
                scope[key] = tuple(scope[key])
            for key in ("baseline_exclusions", "baseline_approval_references"):
                if not isinstance(scope[key], list) or any(
                    not isinstance(pair, list) or len(pair) != 2 or not all(isinstance(v, str) for v in pair)
                    for pair in scope[key]
                ):
                    raise ValueError("Baseline references must be ordered pairs.")
                scope[key] = tuple(tuple(pair) for pair in scope[key])
            if not isinstance(value["input_view_hash"], str) or not isinstance(value["run_id"], str) or not isinstance(value["source_hashes"], dict):
                raise ValueError("Invalid execution-record types.")
            return cls(**value, scope=RunScope(**scope))
        except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
            raise ExecutionBlocked("Missing or malformed local validation execution record.") from exc

    def validate(self, repository: Path, run_id: str) -> None:
        from src.forecasting.metadata import source_hashes
        if self.evaluation_stage != "validation":
            raise ExecutionBlocked("Final evaluation and Gate 6 refit/preprocessing are blocked.")
        if self.validation_run_authorized is not True or self.run_id != run_id:
            raise ExecutionBlocked("An explicit authorisation for this exact validation run is required.")
        if (self.protocol_version != PROTOCOL_VERSION or self.schema_version != SCHEMA_VERSION
                or self.protocol_hash != file_hash(RepositoryLayout(repository).protocol)):
            raise ExecutionBlocked("Run approval does not match the frozen protocol.")
        if self.source_hashes != source_hashes(repository):
            raise ExecutionBlocked("Implementation changed since this run was authorised.")
        references = (self.protocol_approval_reference, self.implementation_acceptance_reference,
                      self.specific_run_reference)
        if not all(isinstance(r, str) and r.strip() and r.strip().lower() not in ("pending", "none", "null")
                   for r in references):
            raise ExecutionBlocked("Gate 1, Gate 3 and specific Gate 4 human references are required.")
        if type(self.worker_count) is not int or self.worker_count != 1:
            raise ExecutionBlocked("Frozen worker_count is exactly one.")
        if len(self.input_view_hash) != 64 or any(c not in "0123456789abcdef" for c in self.input_view_hash):
            raise ExecutionBlocked("Approval must bind the authorised validation input fingerprint.")
        self.scope.validate()



@dataclass(frozen=True)
class ExecutionContext:
    authorization: ValidationAuthorization
    authorization_path: Path
    authorization_digest: str
    authorization_payload: dict
    dataset_path: Path
    layout: RepositoryLayout = DEFAULT_LAYOUT


def resolve_execution(repository: Path | RepositoryLayout = DEFAULT_LAYOUT) -> ExecutionContext:
    layout = RepositoryLayout(repository) if isinstance(repository, Path) else repository
    path = layout.execution_record
    try:
        payload = path.read_bytes()
        approved = ValidationAuthorization.from_json(path)
        approved.validate(layout.root, approved.run_id)
        if layout.run_directory(approved.run_id).exists():
            raise ExecutionBlocked("Execution record is consumed: the approved run directory already exists.")
        dataset = layout.dataset
        if not dataset.is_file():
            raise ExecutionBlocked("Approved dataset is missing from data/raw/supply_chain_dataset1.csv.")
        # Detect replacement while parsing; the retained bytes are exactly those reviewed.
        if path.read_bytes() != payload:
            raise ExecutionBlocked("Execution record changed while resolving it.")
        return ExecutionContext(approved, path, hashlib.sha256(payload).hexdigest(), json.loads(payload), dataset, layout)
    except ExecutionBlocked:
        raise
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        raise ExecutionBlocked("Missing or malformed local validation execution record.") from exc


def load_dataset(path: Path) -> pd.DataFrame:
    columns = ["Date", "SKU_ID", "Warehouse_ID", "Units_Sold"]
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            header = next(csv.reader(stream), [])
        if any(header.count(column) != 1 for column in columns):
            raise ExecutionBlocked("Required CSV columns must each occur exactly once.")
        return pd.read_csv(path, usecols=columns,
                           dtype={"SKU_ID": str, "Warehouse_ID": str, "Units_Sold": object})
    except ExecutionBlocked:
        raise
    except (OSError, ValueError, pd.errors.ParserError, csv.Error) as exc:
        raise ExecutionBlocked("Approved forecasting CSV could not be loaded.") from exc
