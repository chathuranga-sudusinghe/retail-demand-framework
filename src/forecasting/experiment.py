"""CLI entry point for human-authorized validation under the frozen Issue #65 contract.

Imports never execute a run. Final fitting, preprocessing and evaluation remain blocked.
"""
from __future__ import annotations

import argparse

from src.forecasting.authorization import resolve_execution
from src.forecasting.execution import load_dataset
# Preserve public runner/planning imports with direct aliases to their sole owner.
from src.forecasting.orchestration import (
    Candidate as Candidate,
    planned_candidates as planned_candidates,
    run_final_evaluation as run_final_evaluation,
    run_validation as run_validation,
)
from src.forecasting.paths import DEFAULT_LAYOUT


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", default="validation")
    arguments = parser.parse_args(argv)
    if arguments.stage != "validation":
        run_final_evaluation()
    context = resolve_execution(DEFAULT_LAYOUT)
    data = load_dataset(context.dataset_path)
    run_validation(data, run_id=context.authorization.run_id, authorization=context.authorization,
                   execution_context=context)


if __name__ == "__main__":
    main()
