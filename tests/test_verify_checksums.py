"""Synthetic identity checks only; no retained datasets, models or research runs."""

import hashlib
import json
from pathlib import Path
import subprocess
import zlib
from unittest.mock import patch

import pytest

from src.data import verify_checksums as verify


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def reference(tmp_path: Path) -> Path:
    (tmp_path / "payload.bin").write_bytes(b"original")
    path = tmp_path / "reference.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profiles": {
                    "member": {
                        "archive": {"name": "member.zip", "sha256": digest(b"zip")},
                        "files": [
                            {"path": "payload.bin", "sha256": digest(b"original")}
                        ],
                    },
                    "source": {
                        "files": [
                            {"path": "payload.bin", "sha256": digest(b"original")}
                        ]
                    },
                },
            }
        )
    )
    return path


def invoke(tmp_path: Path, path: Path, *extra: str) -> int:
    return verify.main(
        [
            "--root",
            str(tmp_path),
            "--manifest",
            str(path),
            "--profile",
            "member",
            *extra,
        ]
    )


def test_member_success_and_read_only(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = reference(tmp_path)
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    assert invoke(tmp_path, path) == 0
    assert "Files matched: 1/1" in capsys.readouterr().out
    assert {p.name: p.read_bytes() for p in tmp_path.iterdir()} == before


@pytest.mark.parametrize("condition", ["missing", "changed", "directory"])
def test_missing_changed_or_nonregular_payload_fails(
    tmp_path: Path, condition: str
) -> None:
    path = reference(tmp_path)
    payload = tmp_path / "payload.bin"
    if condition == "changed":
        payload.write_bytes(b"changed")
    else:
        payload.unlink()
        if condition == "directory":
            payload.mkdir()
    assert invoke(tmp_path, path) == 1


@pytest.mark.parametrize(
    "relative",
    [
        "../outside",
        "/absolute",
        "a/../b",
        "./a",
        "a//b",
        "C:/file",
        "a\\b",
        ".",
        "",
        "a\nname",
    ],
)
def test_unsafe_reference_paths_fail(relative: str, tmp_path: Path) -> None:
    path = reference(tmp_path)
    doc = json.loads(path.read_text())
    doc["profiles"]["member"]["files"][0]["path"] = relative
    path.write_text(json.dumps(doc))
    assert invoke(tmp_path, path) == 2


@pytest.mark.parametrize(
    "case", ["bad_hash", "duplicate", "empty", "schema", "boolean_schema"]
)
def test_malformed_references_fail(tmp_path: Path, case: str) -> None:
    path = reference(tmp_path)
    doc = json.loads(path.read_text())
    files = doc["profiles"]["member"]["files"]
    if case == "bad_hash":
        files[0]["sha256"] = "not-a-hash"
    elif case == "duplicate":
        files.append(files[0].copy())
    elif case == "empty":
        files.clear()
    else:
        doc["schema_version"] = True if case == "boolean_schema" else 2
    path.write_text(json.dumps(doc))
    assert invoke(tmp_path, path) == 2


def test_duplicate_json_keys_fail(tmp_path: Path) -> None:
    path = reference(tmp_path)
    path.write_text('{"schema_version": 1, "schema_version": 1}')
    assert invoke(tmp_path, path) == 2


def test_symlink_payload_fails_even_when_bytes_match(tmp_path: Path) -> None:
    path = reference(tmp_path)
    payload = tmp_path / "payload.bin"
    payload.rename(tmp_path / "target.bin")
    payload.symlink_to(tmp_path / "target.bin")
    assert invoke(tmp_path, path) == 1


def test_symlink_directory_is_rejected(tmp_path: Path) -> None:
    target = tmp_path / "actual"
    target.mkdir()
    (target / "payload.bin").write_bytes(b"original")
    (tmp_path / "redirect").symlink_to(target, target_is_directory=True)
    assert not verify.check_files(
        tmp_path, {"redirect/payload.bin": digest(b"original")}
    )


def test_archive_is_checked_and_may_be_renamed(tmp_path: Path) -> None:
    path = reference(tmp_path)
    archive = tmp_path / "renamed.zip"
    archive.write_bytes(b"zip")
    assert invoke(tmp_path, path, "--archive", str(archive)) == 0
    archive.write_bytes(b"wrong")
    assert invoke(tmp_path, path, "--archive", str(archive)) == 1


def test_all_deduplicates_and_rejects_conflicting_references(tmp_path: Path) -> None:
    path = reference(tmp_path)
    records, _ = verify.load_profile(path, "all")
    assert len(records) == 1
    doc = json.loads(path.read_text())
    doc["profiles"]["source"]["files"][0]["sha256"] = digest(b"other")
    path.write_text(json.dumps(doc))
    with pytest.raises(ValueError, match="Conflicting"):
        verify.load_profile(path, "all")


def test_unknown_profile_and_inapplicable_archive_fail(tmp_path: Path) -> None:
    path = reference(tmp_path)
    with pytest.raises(ValueError, match="Unknown profile"):
        verify.load_profile(path, "unknown")
    assert (
        verify.main(
            [
                "--profile",
                "source",
                "--root",
                str(tmp_path),
                "--manifest",
                str(path),
                "--archive",
                str(tmp_path / "none.zip"),
            ]
        )
        == 2
    )


def bundle_reference(tmp_path: Path, inventory_key: str) -> Path:
    path = reference(tmp_path)
    completion = {
        "manifest_version": 2,
        "run_id": "synthetic",
        "final_status": "verified_completed",
        inventory_key: [{"path": "payload.bin", "sha256": digest(b"original")}],
    }
    data = json.dumps(completion).encode()
    (tmp_path / "completion.json").write_bytes(data)
    doc = json.loads(path.read_text())
    doc["bundles"] = {
        "synthetic": {
            "path": "completion.json",
            "sha256": digest(data),
            "run_id": "synthetic",
            "inventory_key": inventory_key,
        }
    }
    path.write_text(json.dumps(doc))
    return path


@pytest.mark.parametrize("inventory_key", ["files", "artifacts"])
def test_existing_manifest_formats_and_pin_before_parse(
    tmp_path: Path, inventory_key: str
) -> None:
    path = bundle_reference(tmp_path, inventory_key)
    args = ["--root", str(tmp_path), "--manifest", str(path), "--bundle", "synthetic"]
    assert verify.main(args) == 0
    (tmp_path / "completion.json").write_bytes(b"not even JSON")
    assert verify.main(args) == 2


def test_bundle_missing_payload_is_not_skipped(tmp_path: Path) -> None:
    path = bundle_reference(tmp_path, "files")
    (tmp_path / "payload.bin").unlink()
    assert (
        verify.main(
            [
                "--root",
                str(tmp_path),
                "--manifest",
                str(path),
                "--bundle",
                "synthetic",
            ]
        )
        == 1
    )


def test_pinned_bundle_still_requires_matching_run_identity(tmp_path: Path) -> None:
    path = bundle_reference(tmp_path, "files")
    doc = json.loads(path.read_text())
    doc["bundles"]["synthetic"]["run_id"] = "different"
    path.write_text(json.dumps(doc))
    with pytest.raises(ValueError, match="identity"):
        verify.load_bundle(path, "synthetic", tmp_path)


def git_result(
    stdout: str = "", returncode: int = 0
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(["git"], returncode, stdout, "")


@pytest.mark.parametrize("changed", ["", "src/module.py\n"])
def test_tracked_comparison_and_untracked_disclosure(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    changed: str,
) -> None:
    commit = "a" * 40
    with patch.object(
        verify.subprocess,
        "run",
        side_effect=[
            git_result(str(tmp_path) + "\n"),
            git_result("H src/module.py\0"),
            git_result(commit + "\n"),
            git_result(changed),
            git_result("local-notes.txt\n"),
        ],
    ) as mocked:
        assert verify.check_tracked(tmp_path, commit) is (not bool(changed))
    assert "outside tracked comparison" in capsys.readouterr().out
    assert "--no-ext-diff" in mocked.call_args_list[3].args[0]
    assert "--no-textconv" in mocked.call_args_list[3].args[0]


@pytest.mark.parametrize("reference_sha", ["HEAD", "main", "a" * 39, "-bad"])
def test_tracked_reference_requires_full_commit(
    reference_sha: str, tmp_path: Path
) -> None:
    with pytest.raises(ValueError, match="40-character"):
        verify.check_tracked(tmp_path, reference_sha)


def test_missing_git_commit_and_tracked_only_arguments_fail(tmp_path: Path) -> None:
    with patch.object(
        verify.subprocess,
        "run",
        side_effect=[
            git_result(str(tmp_path) + "\n"),
            git_result(""),
            git_result(returncode=128),
        ],
    ):
        with pytest.raises(ValueError, match="available Git commit"):
            verify.check_tracked(tmp_path, "a" * 40)
    assert verify.main(["--tracked-only", "--root", str(tmp_path)]) == 2


def test_tracked_mismatch_stops_before_loading_reference(tmp_path: Path) -> None:
    with (
        patch.object(verify, "check_tracked", return_value=False),
        patch.object(
            verify,
            "load_profile",
            side_effect=AssertionError("Must not load reference"),
        ),
    ):
        assert (
            verify.main(
                [
                    "--profile",
                    "member",
                    "--root",
                    str(tmp_path),
                    "--tracked-ref",
                    "a" * 40,
                ]
            )
            == 1
        )


def synthetic_git(tmp_path: Path) -> tuple[Path, str]:
    """Use real Git with synthetic objects in tmp_path; no project commits."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(
        ["git", "init", "--quiet", str(repo)], check=True, capture_output=True
    )
    reference(repo)
    (repo / "a.py").write_bytes(b"original\n")

    def object_id(kind: str, data: bytes) -> str:
        serialized = f"{kind} {len(data)}\0".encode() + data
        identity = hashlib.sha1(serialized, usedforsecurity=False).hexdigest()
        path = repo / ".git" / "objects" / identity[:2] / identity[2:]
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(zlib.compress(serialized))
        return identity

    entries = []
    for name in ("a.py", "payload.bin", "reference.json"):
        blob = object_id("blob", (repo / name).read_bytes())
        entries.append(b"100644 " + name.encode() + b"\0" + bytes.fromhex(blob))
    tree = object_id("tree", b"".join(entries))
    commit = object_id(
        "commit",
        (
            f"tree {tree}\n"
            "author Synthetic Fixture <fixture@example.invalid> 1 +0000\n"
            "committer Synthetic Fixture <fixture@example.invalid> 1 +0000\n"
            "\nSynthetic checksum fixture\n"
        ).encode(),
    )
    (repo / ".git" / "HEAD").write_text(commit + "\n")
    subprocess.run(["git", "-C", str(repo), "read-tree", commit], check=True)
    return repo, commit


@pytest.mark.parametrize("flag", ["--skip-worktree", "--assume-unchanged"])
def test_real_git_index_flags_cannot_hide_changed_file(
    tmp_path: Path, flag: str
) -> None:
    repo, commit = synthetic_git(tmp_path)
    subprocess.run(["git", "-C", str(repo), "update-index", flag, "a.py"], check=True)
    (repo / "a.py").write_bytes(b"tampered\n")
    # This is the old false-success path: diff alone says nothing changed.
    diff = subprocess.run(
        ["git", "-C", str(repo), "diff", "--name-only", commit],
        check=True,
        capture_output=True,
        text=True,
    )
    assert not diff.stdout.strip()
    with pytest.raises(ValueError, match="index flags can hide changes"):
        verify.check_tracked(repo, commit)


@pytest.mark.parametrize("condition", ["unchanged", "modified", "deleted", "staged"])
def test_real_git_tracked_changes(tmp_path: Path, condition: str) -> None:
    repo, commit = synthetic_git(tmp_path)
    if condition == "deleted":
        (repo / "a.py").unlink()
    elif condition in ("modified", "staged"):
        (repo / "a.py").write_bytes(b"changed\n")
        if condition == "staged":
            subprocess.run(["git", "-C", str(repo), "add", "a.py"], check=True)
    assert verify.check_tracked(repo, commit) is (condition == "unchanged")


def test_real_git_subdirectory_root_is_rejected(tmp_path: Path) -> None:
    repo, commit = synthetic_git(tmp_path)
    subdirectory = repo / "sub"
    subdirectory.mkdir()
    (repo / "untracked.txt").write_bytes(b"untracked")
    with pytest.raises(ValueError, match="repository top-level"):
        verify.check_tracked(subdirectory, commit)


def test_real_git_untracked_files_are_disclosed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, commit = synthetic_git(tmp_path)
    (repo / "local.txt").write_bytes(b"local")
    assert verify.check_tracked(repo, commit)
    assert "local.txt" in capsys.readouterr().out


def test_reference_output_identifies_exact_bytes_and_head(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, commit = synthetic_git(tmp_path)
    path = repo / "reference.json"
    assert invoke(repo, path) == 0
    output = capsys.readouterr().out
    assert f"Reference SHA-256: {digest(path.read_bytes())}" in output
    assert f"Repository HEAD: {commit}" in output
    assert "matches local HEAD bytes" in output
    assert "PROVISIONAL" in output
    assert invoke(repo, path, "--tracked-ref", commit) == 0
    output = capsys.readouterr().out
    assert "matches the supplied reviewed commit bytes" in output
    assert "PROVISIONAL" not in output


def test_checksum_reference_stays_lf_with_windows_autocrlf(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "--quiet", str(repo)], check=True)
    git = ["git", "-C", str(repo)]
    subprocess.run([*git, "config", "core.autocrlf", "true"], check=True)
    subprocess.run([*git, "config", "user.name", "Checksum Test"], check=True)
    subprocess.run(
        [*git, "config", "user.email", "checksum@example.invalid"], check=True
    )

    attributes = repo / ".gitattributes"
    attributes.write_bytes(b"/docs/checksums/2026-10-06.json text eol=lf\n")
    reference_path = repo / "docs" / "checksums" / "2026-10-06.json"
    reference_path.parent.mkdir(parents=True)
    reference_path.write_bytes(b'{"schema_version": 1}\n')
    unrelated = repo / "unrelated.txt"
    unrelated.write_bytes(b"ordinary text\n")

    subprocess.run([*git, "add", ".gitattributes", "docs", "unrelated.txt"], check=True)
    subprocess.run([*git, "commit", "--quiet", "-m", "fixture"], check=True)
    commit = subprocess.run(
        [*git, "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()

    reference_path.unlink()
    unrelated.unlink()
    subprocess.run(
        [*git, "checkout", "--", "docs/checksums/2026-10-06.json", "unrelated.txt"],
        check=True,
    )

    reference_bytes = reference_path.read_bytes()
    assert b"\n" in reference_bytes
    assert b"\r\n" not in reference_bytes
    assert b"\r\n" in unrelated.read_bytes()

    verify.report_reference(repo, reference_path, reference_bytes, commit)
    output = capsys.readouterr().out
    assert "Reference status: matches the supplied reviewed commit bytes." in output
    assert "Reference unverified" not in output


def test_rebaselined_local_reference_warns_even_if_payload_matches(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, _ = synthetic_git(tmp_path)
    path = repo / "reference.json"
    original_hash = digest(path.read_bytes())
    doc = json.loads(path.read_text())
    for entry in doc["profiles"].values():
        entry["files"][0]["sha256"] = digest(b"tampered")
    path.write_text(json.dumps(doc))
    (repo / "payload.bin").write_bytes(b"tampered")
    assert invoke(repo, path) == 0  # Byte matches only; explicitly provisional.
    output = capsys.readouterr().out
    assert "Reference unverified" in output and "PROVISIONAL" in output
    assert digest(path.read_bytes()) != original_hash
    assert f"Reference SHA-256: {digest(path.read_bytes())}" in output


def test_untracked_reference_cannot_be_verified_against_reviewed_commit(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, commit = synthetic_git(tmp_path)
    path = repo / "untracked-reference.json"
    path.write_bytes((repo / "reference.json").read_bytes())
    assert invoke(repo, path) == 0
    assert "Reference unverified" in capsys.readouterr().out
    assert invoke(repo, path, "--tracked-ref", commit) == 2
    assert "Reference unverified against" in capsys.readouterr().out


def test_reference_used_is_the_same_snapshot_that_was_identified(
    tmp_path: Path,
) -> None:
    path = reference(tmp_path)
    original = path.read_bytes()
    path.write_bytes(b"changed after read")
    records, _ = verify.load_profile(path, "member", data=original)
    assert records == {"payload.bin": digest(b"original")}


def test_missing_file_has_specific_diagnostic(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = reference(tmp_path)
    (tmp_path / "payload.bin").unlink()
    assert invoke(tmp_path, path) == 1
    assert "MISSING  payload.bin" in capsys.readouterr().out


@pytest.mark.parametrize("condition", ["status", "version", "self_inventory"])
def test_bundle_metadata_and_self_inventory_fail(
    tmp_path: Path, condition: str
) -> None:
    path = bundle_reference(tmp_path, "files")
    manifest = tmp_path / "completion.json"
    completion = json.loads(manifest.read_text())
    if condition == "status":
        completion["final_status"] = "incomplete"
    elif condition == "version":
        completion["manifest_version"] = 1
    else:
        completion["files"].append({"path": "completion.json", "sha256": "a" * 64})
    data = json.dumps(completion).encode()
    manifest.write_bytes(data)
    doc = json.loads(path.read_text())
    doc["bundles"]["synthetic"]["sha256"] = digest(data)
    path.write_text(json.dumps(doc))
    with pytest.raises(ValueError):
        verify.load_bundle(path, "synthetic", tmp_path)
