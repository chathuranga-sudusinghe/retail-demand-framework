"""Source/environment provenance, scoped approval manifest and pending gates."""
from __future__ import annotations

import importlib
import importlib.metadata
import platform
import subprocess
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.forecasting.artifacts import PROTOCOL_VERSION, SCHEMA_VERSION, file_hash
from src.forecasting.baselines import BASELINE_FORMULAS
from src.forecasting.configuration import PRIMARY_GRID
from src.forecasting.features import CATEGORICAL_FEATURE_COLUMNS, CONCEPTUAL_FEATURE_COLUMNS, FEATURE_COLUMNS

from src.forecasting.paths import REPOSITORY as REPOSITORY, RepositoryLayout
from src.forecasting.execution import ExecutionBlocked, RunScope as RunScope, ValidationAuthorization  # re-export existing API
LIBRARIES = ("numpy", "pandas", "scikit-learn", "xgboost", "lightgbm", "catboost", "threadpoolctl", "joblib", "scipy")
DECISION_REFERENCES = tuple(f"docs/decisions/{name}" for name in (
    "DR-002-forecasting-analytical-unit.md", "DR-004-forecast-horizons.md",
    "DR-005-forecast-validation-design.md", "DR-006-forecasting-metrics-and-model-selection.md",
    "DR-008-multi-step-forecasting-strategy.md", "DR-013-matched-gradient-boosting-comparison.md",
))


def source_hashes(repository: Path) -> dict[str, str]:
    layout = RepositoryLayout(repository)
    paths = [*sorted(layout.repository_path("src").rglob("*.py")),
             *sorted(layout.repository_path("tests").rglob("*.py")),
             layout.repository_path("requirements.txt"), layout.repository_path("requirements-dev.txt"),
             layout.repository_path("AGENTS.md"), layout.feature_contract,
             *(layout.repository_path(reference) for reference in DECISION_REFERENCES)]
    return {str(path.relative_to(layout.root)): file_hash(path) for path in paths}


def git_state(repository: Path) -> dict[str, Any]:
    def read(*args: str) -> str:
        return subprocess.check_output(["git", *args], cwd=repository, text=True).strip()
    return {"git_commit_sha": read("rev-parse", "HEAD"),
            "git_branch": read("branch", "--show-current"),
            "git_dirty": bool(read("status", "--porcelain"))}


def runtime_versions(repository: Path) -> dict[str, str]:
    versions = {name: importlib.metadata.version(name) for name in LIBRARIES}
    for line in RepositoryLayout(repository).repository_path("requirements.txt").read_text().splitlines():
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
        binaries = sorted(p for pattern in ("*.so", "*.dll", "*.dylib") for p in package.rglob(pattern))
        builds[name] = {"package_version": versions[name],
                        "native_library_hashes": {str(p.relative_to(package)): file_hash(p) for p in binaries}}
        if name == "xgboost":
            builds[name]["build_info"] = module.build_info()
    return {**git_state(repository), "source_hashes": source_hashes(repository),
            "python_version": platform.python_version(), "library_versions": versions,
            "library_builds": builds, "requirements_hash": file_hash(RepositoryLayout(repository).repository_path("requirements.txt")),
            "installed_distributions": {d.metadata["Name"]: d.version for d in sorted(
                importlib.metadata.distributions(), key=lambda d: d.metadata["Name"].lower())},
            "operating_system": platform.platform(),
            "hardware": {"machine": platform.machine(), "processor": platform.processor()},
            "execution_environment": {"python_executable": sys.executable,
                                      "python_build": platform.python_build(),
                                      "python_compiler": platform.python_compiler(),
                                      "worker_count": 1, "device": "CPU", "thread_count": 1,
                                      "blas_thread_limit": 1}}


def initial_metadata(authorization: ValidationAuthorization, repository: Path) -> dict[str, Any]:
    """Manifest exists before input preparation, fitting or scoring."""
    layout = RepositoryLayout(repository)
    return {
        "run_id": authorization.run_id, "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "evaluation_stage": "validation", "run_status": "preflight",
        "schema_version": SCHEMA_VERSION, "protocol_version": PROTOCOL_VERSION,
        "protocol_path": "docs/protocol.md", "protocol_hash": file_hash(layout.protocol),
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
        "feature_contract_hash": file_hash(layout.feature_contract),
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
