"""Synthetic CI routing checks; no research runs or repository mutations."""

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / ".github/scripts/ci_scope.py"
SPEC = importlib.util.spec_from_file_location("ci_scope", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
scope = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scope)

BASE, HEAD = "a" * 40, "b" * 40


@pytest.mark.parametrize(
    "path",
    [
        "README.md",
        "CONTRIBUTING.md",
        "docs/research/responsible-decision-support-evaluation.md",
        "docs/team/dewmi/group-project-overview.md",
        "docs/meetings/notes.md",
        "reports/README.md",
        "reports/decision-support/issue-168-inventory-v1/review.json",
        "reports/inventory-risk/issue-164/evaluation-v1/evaluation.json",
        "docs/notes with spaces.md",
        "docs/notes\nwith newline.md",
    ],
)
def test_presentation_only_changes_skip_python(path):
    assert scope.requires_python([path]) is False


@pytest.mark.parametrize(
    "path",
    [
        "src/inventory_risk/runner.py",
        "tests/test_ci_scope.py",
        "requirements.txt",
        "requirements-dev.txt",
        "mypy.ini",
        "pyproject.toml",
        "Dockerfile",
        ".gitattributes",
        ".github/workflows/ci-tests.yml",
        ".github/scripts/ci_scope.py",
        ".github/PULL_REQUEST_TEMPLATE.md",
        "src/templates/prompt.md",
        "tests/fixtures/input.md",
        "scripts/instructions.md",
        "reports/unexpected.py",
        "docs/checksums/2026-10-06.json",
        "notebooks/analysis.ipynb",
        "unknown.json",
        "unknown",
    ],
)
def test_code_configuration_and_unknown_paths_keep_python_checks(path):
    assert scope.requires_python(["README.md", path]) is True


@pytest.mark.parametrize(
    "path",
    [
        "AGENTS.md",
        "docs/protocol.md",
        "docs/forecasting-feature-engineering.md",
        "docs/data-cleaning-and-validation.md",
        "docs/decisions/DR-014-forecasting-selection-and-final-refit.md",
        "docs/forecasting-final-evaluation.md",
    ],
)
def test_markdown_used_by_implementation_keeps_python_checks(path):
    assert scope.requires_python([path]) is True


def test_empty_change_scope_conservatively_runs_checks():
    assert scope.requires_python([]) is True


@pytest.mark.parametrize(
    "paths", [["src/old.py", "docs/moved.md"], ["docs/old.md", "src/new.py"]]
)
def test_moves_between_code_and_docs_keep_python_checks(paths):
    assert scope.requires_python(paths) is True


@pytest.mark.parametrize(
    "event_name, separator", [("pull_request", "..."), ("push", "..")]
)
def test_diff_covers_entire_pr_or_push_and_preserves_null_delimited_paths(
    monkeypatch, event_name, separator
):
    commands = []

    def git_diff(command, **kwargs):
        commands.append(command)
        assert kwargs == {"check": False, "capture_output": True}
        return SimpleNamespace(returncode=0, stdout=b"docs/notes\nwith spaces.md\0")

    monkeypatch.setattr(scope.subprocess, "run", git_diff)
    event = {
        "pull_request": {"base": {"sha": BASE}, "head": {"sha": HEAD}},
        "before": BASE,
        "after": HEAD,
    }
    assert scope.event_requires_python(event_name, event) is False
    assert commands == [
        [
            "git",
            "diff",
            "--name-only",
            "--no-renames",
            "-z",
            f"{BASE}{separator}{HEAD}",
            "--",
        ]
    ]


def test_doc_only_latest_commit_cannot_hide_earlier_code_changes_in_pr(monkeypatch):
    event = {
        "pull_request": {"base": {"sha": BASE}, "head": {"sha": HEAD}},
        "commits": [{"modified": ["README.md"]}],
    }

    def git_diff(command, **kwargs):
        assert command[-2] == f"{BASE}...{HEAD}"
        return SimpleNamespace(returncode=0, stdout=b"README.md\0src/api/main.py\0")

    monkeypatch.setattr(scope.subprocess, "run", git_diff)
    assert scope.event_requires_python("pull_request", event) is True


@pytest.mark.parametrize(
    "event_name, event",
    [
        ("workflow_dispatch", {}),
        ("pull_request", {}),
        ("pull_request", {"pull_request": None}),
        ("push", {"before": "0" * 40, "after": HEAD}),
        ("push", {"before": BASE, "after": "0" * 40}),
        ("push", {"before": "--bad-option", "after": HEAD}),
        ("push", {"before": None, "after": HEAD}),
    ],
)
def test_missing_or_invalid_event_scope_runs_all_checks_without_git(
    monkeypatch, event_name, event
):
    def unexpected_git(*args, **kwargs):
        pytest.fail("Invalid scope must not be passed to Git")

    monkeypatch.setattr(scope.subprocess, "run", unexpected_git)
    assert scope.event_requires_python(event_name, event) is True


@pytest.mark.parametrize(
    "returncode, output",
    [(128, b""), (0, b""), (0, b"README.md"), (0, b"\0")],
)
def test_missing_history_empty_or_incomplete_diff_runs_all_checks(
    monkeypatch, returncode, output
):
    monkeypatch.setattr(
        scope.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=returncode, stdout=output),
    )
    assert scope.event_requires_python("push", {"before": BASE, "after": HEAD}) is True


def test_unavailable_git_runs_all_checks(monkeypatch):
    def missing_git(*args, **kwargs):
        raise OSError("Git unavailable")

    monkeypatch.setattr(scope.subprocess, "run", missing_git)
    assert scope.event_requires_python("push", {"before": BASE, "after": HEAD}) is True


@pytest.mark.parametrize("requires_python", [True, False])
def test_cli_writes_only_valid_github_output(
    monkeypatch, tmp_path, capsys, requires_python
):
    path = tmp_path / "event.json"
    path.write_text(json.dumps({"before": BASE, "after": HEAD}))
    monkeypatch.setenv("GITHUB_EVENT_NAME", "push")
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(path))
    monkeypatch.setattr(scope, "event_requires_python", lambda *args: requires_python)
    scope.main()
    captured = capsys.readouterr()
    assert captured.out == f"run_python={str(requires_python).lower()}\n"
    assert captured.err


@pytest.mark.parametrize("content", ["{bad JSON", "[]", "null"])
def test_invalid_event_file_defaults_to_running_checks(
    monkeypatch, tmp_path, capsys, content
):
    path = tmp_path / "event.json"
    path.write_text(content)
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(path))
    scope.main()
    assert capsys.readouterr().out == "run_python=true\n"


def test_missing_event_file_defaults_to_running_checks(monkeypatch, capsys):
    monkeypatch.delenv("GITHUB_EVENT_PATH", raising=False)
    scope.main()
    assert capsys.readouterr().out == "run_python=true\n"
