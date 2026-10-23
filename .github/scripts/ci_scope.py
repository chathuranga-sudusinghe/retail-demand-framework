"""Identify presentation-only changes before installing Python dependencies.

Uses only the standard library and local Git history. Missing event/history
information conservatively enables all checks. No Git state is changed.
"""

from __future__ import annotations

from collections.abc import Iterable
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Any


# Keep source/contract Markdown referenced by implementation/tests in full CI.
PYTHON_INPUTS = frozenset(
    {
        "AGENTS.md",
        "docs/protocol.md",
        "docs/forecasting-feature-engineering.md",
        "docs/data-cleaning-and-validation.md",
        "docs/decisions/DR-014-forecasting-selection-and-final-refit.md",
        "docs/forecasting-final-evaluation.md",
    }
)


def requires_python(paths: Iterable[str]) -> bool:
    """Skip only ordinary Markdown and report JSON; unknown paths run checks."""
    seen = False
    for path in paths:
        seen = True
        if path in PYTHON_INPUTS or path.startswith(
            ("src/", "tests/", "scripts/", ".github/")
        ):
            return True
        suffix = PurePosixPath(path).suffix
        if suffix == ".md" or (path.startswith("reports/") and suffix == ".json"):
            continue
        return True
    return not seen


def event_requires_python(event_name: str, event: dict[str, Any]) -> bool:
    """Check the entire PR changeset or every commit in a main-branch push."""
    try:
        if event_name == "pull_request":
            base = event["pull_request"]["base"]["sha"]
            head = event["pull_request"]["head"]["sha"]
            separator = "..."
        elif event_name == "push":
            base, head = event["before"], event["after"]
            separator = ".."
        else:
            return True
        for revision in (base, head):
            if (
                not isinstance(revision, str)
                or re.fullmatch(r"[0-9a-fA-F]{40}", revision) is None
                or revision == "0" * 40
            ):
                return True
        result = subprocess.run(
            [
                "git",
                "diff",
                "--name-only",
                "--no-renames",
                "-z",
                f"{base}{separator}{head}",
                "--",
            ],
            check=False,
            capture_output=True,
        )
    except (KeyError, TypeError, OSError):
        return True
    if result.returncode != 0 or not result.stdout.endswith(b"\0"):
        return True
    # NUL delimiters preserve spaces/newlines, and --no-renames exposes both
    # sides of renames so moving code into/out of a docs path cannot hide it.
    return requires_python(
        os.fsdecode(path) for path in result.stdout.split(b"\0")[:-1]
    )


def main() -> None:
    try:
        event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_bytes())
        run_python = (
            event_requires_python(os.environ.get("GITHUB_EVENT_NAME", ""), event)
            if isinstance(event, dict)
            else True
        )
    except (KeyError, OSError, ValueError):
        run_python = True
    print(f"run_python={str(run_python).lower()}")
    print(
        "Python checks required (code/test inputs or uncertain change scope)."
        if run_python
        else "Documentation/report-only changes: Python checks skipped.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
