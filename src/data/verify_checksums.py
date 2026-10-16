"""Read-only identity checks for tracked content and explicitly pinned artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
from typing import Any

REPOSITORY = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = REPOSITORY / "docs/checksums/2026-10-06.json"


def sha256(path: Path) -> str:
    """Stream bytes without deserializing data or loading saved models."""
    if not path.exists():
        raise FileNotFoundError(path)
    if not path.is_file():
        raise ValueError("Expected a regular file.")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _digest(value: object) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError("Expected a lowercase SHA-256 digest.")
    return value


def _relative_path(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("Expected a nonempty repository-relative POSIX path.")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or path.as_posix() != value
        or ".." in path.parts
        or "\\" in value
        or ":" in value
        or not path.parts
        or any(ord(character) < 32 for character in value)
    ):
        raise ValueError("Unsafe or noncanonical checksum path.")
    return value


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    document: dict[str, Any] = {}
    for key, value in pairs:
        if key in document:
            raise ValueError(f"Duplicate JSON key: {key}")
        document[key] = value
    return document


def _document(data: str | bytes) -> dict[str, Any]:
    document = json.loads(data, object_pairs_hook=_unique_object)
    if not isinstance(document, dict):
        raise ValueError("Expected a JSON object.")
    return document


def _reference(manifest: Path, data: bytes | None = None) -> dict[str, Any]:
    document = _document(manifest.read_bytes() if data is None else data)
    if (
        type(document.get("schema_version")) is not int
        or document["schema_version"] != 1
    ):
        raise ValueError("Unsupported checksum reference schema.")
    return document


def _records(files: object) -> dict[str, str]:
    if not isinstance(files, list) or not files:
        raise ValueError("Expected a nonempty file inventory.")
    records: dict[str, str] = {}
    for record in files:
        if not isinstance(record, dict):
            raise ValueError("Invalid checksum record.")
        relative = _relative_path(record.get("path"))
        if relative in records:
            raise ValueError("Duplicate file in a checksum inventory.")
        records[relative] = _digest(record.get("sha256"))
    return records


def load_profile(
    manifest: Path, profile: str, *, data: bytes | None = None
) -> tuple[dict[str, str], dict[str, str]]:
    """Validate profiles before checking any selected file."""
    profiles = _reference(manifest, data).get("profiles")
    if not isinstance(profiles, dict) or not profiles or "all" in profiles:
        raise ValueError("Expected named checksum profiles; all is reserved.")
    if profile != "all" and profile not in profiles:
        raise ValueError(f"Unknown profile: {profile}")
    selected: dict[str, str] = {}
    archives: dict[str, str] = {}
    for name, entry in profiles.items():
        if not isinstance(entry, dict):
            raise ValueError("Invalid checksum profile.")
        records = _records(entry.get("files"))
        archive = entry.get("archive")
        archive_records: dict[str, str] = {}
        if archive is not None:
            if not isinstance(archive, dict):
                raise ValueError("Invalid archive reference.")
            archive_name = _relative_path(archive.get("name"))
            if len(PurePosixPath(archive_name).parts) != 1:
                raise ValueError("Archive name must be a filename.")
            archive_records[archive_name] = _digest(archive.get("sha256"))
        if name == profile or profile == "all":
            for relative, expected in records.items():
                if relative in selected and selected[relative] != expected:
                    raise ValueError("Conflicting hashes across selected profiles.")
                selected[relative] = expected
        if name == profile:
            archives = archive_records
    return selected, archives


def _payload_path(root: Path, relative: str) -> Path:
    """Reject files or directory components redirected through symlinks."""
    current = root.resolve()
    for component in PurePosixPath(_relative_path(relative)).parts:
        current = current / component
        if current.is_symlink():
            raise ValueError("Symlink redirection is not allowed.")
    return current


def load_bundle(
    manifest: Path, bundle: str, root: Path, *, data: bytes | None = None
) -> dict[str, str]:
    """Verify a pinned completion manifest before reading its byte inventory."""
    bundles = _reference(manifest, data).get("bundles")
    if not isinstance(bundles, dict) or bundle not in bundles:
        raise ValueError(f"Unknown bundle: {bundle}")
    entry = bundles[bundle]
    if not isinstance(entry, dict):
        raise ValueError("Invalid bundle reference.")
    relative = _relative_path(entry.get("path"))
    expected = _digest(entry.get("sha256"))
    data = _payload_path(root, relative).read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError("Bundle manifest does not match its pinned SHA-256.")
    document = _document(data)
    if (
        document.get("run_id") != entry.get("run_id")
        or not isinstance(entry.get("run_id"), str)
        or document.get("final_status") != "verified_completed"
        or document.get("manifest_version") != 2
    ):
        raise ValueError("Bundle identity/completion metadata does not match.")
    inventory_key = entry.get("inventory_key")
    if inventory_key not in ("files", "artifacts"):
        raise ValueError("Unsupported bundle inventory key.")
    records = _records(document.get(inventory_key))
    if relative in records:
        raise ValueError("Completion manifest must not inventory itself.")
    return {relative: expected, **records}


def check_files(root: Path, records: dict[str, str]) -> bool:
    passed = 0
    for relative, expected in sorted(records.items()):
        try:
            actual = sha256(_payload_path(root, relative))
            if actual == _digest(expected):
                passed += 1
                print(f"OK  {relative}")
            else:
                print(f"MISMATCH  {relative}: expected={expected} actual={actual}")
        except FileNotFoundError:
            print(f"MISSING  {relative}")
        except (OSError, ValueError) as error:
            print(f"ERROR  {relative}: {error}")
    print(f"Files matched: {passed}/{len(records)}")
    return passed == len(records) and bool(records)


def check_tracked(root: Path, reference: str) -> bool:
    """Compare tracked content with an independently supplied full commit SHA."""
    if not re.fullmatch(r"[0-9a-f]{40}", reference):
        raise ValueError("--tracked-ref requires a full 40-character Git commit SHA.")
    command = ["git", "-C", str(root)]
    top = subprocess.run(
        [*command, "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if top.returncode or Path(top.stdout.strip()).resolve() != root.resolve():
        raise ValueError("--root must be the repository top-level directory.")
    flags = subprocess.run(
        [*command, "ls-files", "-v", "-z"],
        capture_output=True,
        text=True,
        check=False,
    )
    if flags.returncode:
        raise ValueError("Cannot inspect Git index flags.")
    hidden = [
        entry[2:]
        for entry in flags.stdout.split("\0")
        if entry and (entry[0].islower() or entry[0] == "S")
    ]
    if hidden:
        raise ValueError(
            "Git index flags can hide changes (assume-unchanged/skip-worktree): "
            + ", ".join(hidden)
        )
    commit = subprocess.run(
        [*command, "rev-parse", "--verify", f"{reference}^{{commit}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if commit.returncode or commit.stdout.strip() != reference:
        raise ValueError("Reference must identify an available Git commit.")
    result = subprocess.run(
        [
            *command,
            "diff",
            "--no-ext-diff",
            "--no-textconv",
            "--name-only",
            reference,
            "--",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise ValueError("Cannot compare tracked files; check the root and commit.")
    untracked = subprocess.run(
        [*command, "ls-files", "--others", "--exclude-standard"],
        capture_output=True,
        text=True,
        check=False,
    )
    if untracked.returncode:
        raise ValueError("Cannot inspect untracked-file coverage.")
    if untracked.stdout.strip():
        print(
            f"Untracked files (outside tracked comparison):\n{untracked.stdout.rstrip()}"
        )
    if result.stdout.strip():
        print(f"MISMATCH  tracked files against {reference}:\n{result.stdout.rstrip()}")
        return False
    print(f"OK  tracked Git content matches {reference}")
    return True


def report_reference(
    root: Path, manifest: Path, data: bytes, reviewed_commit: str | None
) -> None:
    """Identify the exact bytes consumed and distinguish local from reviewed trust."""
    print(f"Reference: {manifest.resolve()}")
    print(f"Reference SHA-256: {hashlib.sha256(data).hexdigest()}")
    command = ["git", "-C", str(root)]
    try:
        head = subprocess.run(
            [*command, "rev-parse", "--verify", "HEAD^{commit}"],
            capture_output=True,
            text=True,
            check=False,
        )
        print(
            f"Repository HEAD: {head.stdout.strip() if not head.returncode else 'unavailable'}"
        )
        top = subprocess.run(
            [*command, "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
        if head.returncode or top.returncode:
            raise ValueError("Reference is not in an available Git working tree.")
        relative = manifest.resolve().relative_to(Path(top.stdout.strip()).resolve())
        revision = reviewed_commit or head.stdout.strip()
        recorded = subprocess.run(
            [*command, "show", f"{revision}:{relative.as_posix()}"],
            capture_output=True,
            check=False,
        )
        if recorded.returncode or recorded.stdout != data:
            raise ValueError(
                "Reference is untracked, outside the checkout, or differs from the commit."
            )
    except (OSError, ValueError) as error:
        if reviewed_commit:
            raise ValueError(
                f"Reference unverified against {reviewed_commit}: {error}"
            ) from error
        print(f"WARNING  Reference unverified: {error}")
    else:
        print(f"Reference revision: {revision}")
        if reviewed_commit:
            print("Reference status: matches the supplied reviewed commit bytes.")
            return
        print(
            "Reference status: matches local HEAD bytes; independent review NOT CHECKED."
        )
    print(
        "WARNING  PROVISIONAL: payload matches alone do not verify reference provenance."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument(
        "--profile", help="dewmi, didilani, tinosh, source, validated, anchors, all"
    )
    selection.add_argument(
        "--bundle", help="Opt-in full retained bundle: validation or final."
    )
    selection.add_argument("--tracked-only", action="store_true")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--root", type=Path, default=REPOSITORY)
    parser.add_argument("--archive", type=Path, help="Optional original member ZIP.")
    parser.add_argument(
        "--tracked-ref", help="Independently reviewed full Git commit SHA."
    )
    args = parser.parse_args(argv)
    try:
        if args.archive and (not args.profile or args.profile == "all"):
            raise ValueError("--archive requires one named member profile.")
        if args.tracked_only and not args.tracked_ref:
            raise ValueError("--tracked-only requires --tracked-ref.")
        if args.tracked_ref:
            if not check_tracked(args.root, args.tracked_ref):
                print(
                    "Stopped before using checksum references; review tracked changes."
                )
                return 1
        else:
            print("Tracked files: NOT CHECKED (supply --tracked-ref to compare).")
        if args.tracked_only:
            return 0
        reference_data = args.manifest.read_bytes()
        report_reference(args.root, args.manifest, reference_data, args.tracked_ref)
        archives: dict[str, str] = {}
        if args.bundle:
            records = load_bundle(
                args.manifest, args.bundle, args.root, data=reference_data
            )
        else:
            records, archives = load_profile(
                args.manifest, args.profile, data=reference_data
            )
        if args.archive and not archives:
            raise ValueError("This profile has no ZIP reference.")
        print(f"Root: {args.root.resolve()}")
        passed = check_files(args.root, records)
        if args.archive:
            expected = next(iter(archives.values()))
            archive_passed = check_files(
                args.archive.absolute().parent, {args.archive.name: expected}
            )
            passed = archive_passed and passed
        print("Identity only; human acceptance and research approvals are separate.")
        return 0 if passed else 1
    except (OSError, ValueError) as error:
        print(f"ERROR  {error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
