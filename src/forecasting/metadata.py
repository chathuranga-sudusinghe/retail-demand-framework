"""Source/environment provenance, scoped approval manifest and pending gates."""
from __future__ import annotations

import importlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.forecasting.artifacts import PROTOCOL_VERSION, SCHEMA_VERSION, file_hash
from src.forecasting.baselines import BASELINE_FORMULAS, BASELINE_MODELS
from src.forecasting.configuration import PRIMARY_GRID, PRIMARY_MODELS, SUPPORTIVE_MODELS
from src.forecasting.features import CATEGORICAL_FEATURE_COLUMNS, CONCEPTUAL_FEATURE_COLUMNS, FEATURE_COLUMNS
from src.forecasting.targets import FORECAST_HORIZONS

REPOSITORY = Path(__file__).resolve().parents[2]
LIBRARIES = ("numpy", "pandas", "scikit-learn", "xgboost", "lightgbm", "catboost", "threadpoolctl")
DECISION_REFERENCES = tuple(f"docs/decisions/{name}" for name in (
    "DR-002-forecasting-analytical-unit.md", "DR-004-forecast-horizons.md",
    "DR-005-forecast-validation-design.md", "DR-006-forecasting-metrics-and-model-selection.md",
    "DR-008-multi-step-forecasting-strategy.md", "DR-013-matched-gradient-boosting-comparison.md",
))


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
        value = json.loads(path.read_text(encoding="utf-8"))
        scope = value.pop("scope")
        for key in ("primary_models", "supportive_models", "horizons", "baselines"):
            scope[key] = tuple(scope[key])
        for key in ("baseline_exclusions", "baseline_approval_references"):
            scope[key] = tuple(tuple(pair) for pair in scope[key])
        return cls(**value, scope=RunScope(**scope))

    def validate(self, repository: Path, run_id: str) -> None:
        if self.evaluation_stage != "validation":
            raise ExecutionBlocked("Final evaluation and Gate 6 refit/preprocessing are blocked.")
        if self.validation_run_authorized is not True or self.run_id != run_id:
            raise ExecutionBlocked("An explicit authorisation for this exact validation run is required.")
        if (self.protocol_version != PROTOCOL_VERSION or self.schema_version != SCHEMA_VERSION
                or self.protocol_hash != file_hash(repository / "docs/protocol.md")):
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


def source_hashes(repository: Path) -> dict[str, str]:
    paths = [*sorted((repository / "src").rglob("*.py")),
             *sorted((repository / "tests").rglob("*.py")),
             repository / "requirements.txt", repository / "requirements-dev.txt",
             repository / "AGENTS.md", repository / "docs/forecasting-feature-engineering.md",
             *(repository / reference for reference in DECISION_REFERENCES)]
    return {str(path.relative_to(repository)): file_hash(path) for path in paths}


def git_state(repository: Path) -> dict[str, Any]:
    def read(*args: str) -> str:
        return subprocess.check_output(["git", *args], cwd=repository, text=True).strip()
    return {"git_commit_sha": read("rev-parse", "HEAD"),
            "git_branch": read("branch", "--show-current"),
            "git_dirty": bool(read("status", "--porcelain"))}


def runtime_versions(repository: Path) -> dict[str, str]:
    versions = {name: importlib.metadata.version(name) for name in LIBRARIES}
    for line in (repository / "requirements.txt").read_text().splitlines():
        if "==" in line and not line.startswith("#"):
            name, expected = line.split("==", 1)
            actual = importlib.metadata.version(name)
            if actual != expected.strip():
                raise ExecutionBlocked(f"Pinned version mismatch for {name}: {actual} != {expected}.")
    if platform.python_version() != "3.12.3":
        raise ExecutionBlocked("The frozen Python runtime is 3.12.3; a mismatch requires review.")
    return versions


def environment_metadata(repository: Path) -> dict[str, Any]:
    versions = runtime_versions(repository)
    builds: dict[str, Any] = {}
    for name in ("xgboost", "lightgbm", "catboost"):
        module = importlib.import_module(name)
        if module.__file__ is None:
            builds[name] = {"package_version": versions[name], "build_status": "unavailable_module_path"}
            continue
        package = Path(module.__file__).resolve().parent
        binaries = sorted(package.rglob("*.so"))
        builds[name] = {"package_version": versions[name],
                        "native_library_hashes": {str(p.relative_to(package)): file_hash(p) for p in binaries}}
        if name == "xgboost":
            builds[name]["build_info"] = module.build_info()
    return {**git_state(repository), "source_hashes": source_hashes(repository),
            "python_version": platform.python_version(), "library_versions": versions,
            "library_builds": builds, "requirements_hash": file_hash(repository / "requirements.txt"),
            "operating_system": platform.platform(),
            "hardware": {"machine": platform.machine(), "processor": platform.processor()},
            "execution_environment": {"python_executable": sys.executable,
                                      "python_build": platform.python_build(),
                                      "python_compiler": platform.python_compiler(),
                                      "worker_count": 1, "device": "CPU", "thread_count": 1,
                                      "blas_thread_limit": 1}}


def initial_metadata(authorization: ValidationAuthorization, repository: Path) -> dict[str, Any]:
    """Manifest exists before input preparation, fitting or scoring."""
    return {
        "run_id": authorization.run_id, "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "evaluation_stage": "validation", "run_status": "preflight",
        "schema_version": SCHEMA_VERSION, "protocol_version": PROTOCOL_VERSION,
        "protocol_path": "docs/protocol.md", "protocol_hash": file_hash(repository / "docs/protocol.md"),
        "approval_references": {
            "protocol": authorization.protocol_approval_reference,
            "full_implementation": authorization.implementation_acceptance_reference,
            "specific_run": authorization.specific_run_reference,
            "tie": "docs/protocol.md Sections 9/18; owner decision 2026-09-29",
            "numeric_runtime": "docs/protocol.md Sections 7/18; owner decision 2026-09-29",
            "final_refit": None, "selection_freeze": None, "final_run": None,
        },
        "run_scope": asdict(authorization.scope),
        "canonical_grid": [{"canonical_config_id": c.canonical_config_id,
                            "canonical_parameters": c.canonical_parameters} for c in PRIMARY_GRID],
        "feature_contract_path": "docs/forecasting-feature-engineering.md",
        "feature_contract_hash": file_hash(repository / "docs/forecasting-feature-engineering.md"),
        "decision_record_references": list(DECISION_REFERENCES),
        "conceptual_feature_names": list(CONCEPTUAL_FEATURE_COLUMNS),
        "numerical_feature_names": list(FEATURE_COLUMNS),
        "categorical_feature_names": list(CATEGORICAL_FEATURE_COLUMNS),
        "candidate_records": [], "representation_records": [], "eligibility_records": [],
        "metric_records": [], "selection_records": [], "artifact_manifest": [],
        "random_seeds": {"xgboost": {"random_state": 42}, "lightgbm": {"random_state": 42},
                         "catboost": {"random_seed": 42}, "random_forest": {"random_state": 42},
                         "ridge": {}},
        "final_evaluation_status": "blocked_gate_6", "final_refit_policy": None,
        "prior_exposure": {"earlier_validation": "2024-12-03 through 2024-12-16",
                           "full_year_eda": True},
        "input_view_hash": authorization.input_view_hash,
        "baseline_formula_references": BASELINE_FORMULAS,
        "git_commit_sha": None, "git_branch": None, "git_dirty": None, "source_hashes": authorization.source_hashes,
        "python_version": None, "library_versions": {}, "library_builds": {}, "requirements_hash": None,
        "operating_system": None, "hardware": {}, "execution_environment": {},
    }
