"""Issue #102: scoped validated Parquet handoff, with no forecasting execution.

A verified acquisition receipt is caller-supplied evidence, not an approval or a
fresh whole-source hash. Only the cleaner inspects scoped source quantities.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
from typing import Any
from uuid import uuid4

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from src.data import data_cleaning as cleaning

SCHEMA_VERSION = "validated-shared-data-v1"
RULE_VERSION = "shared-data-cleaning-v1"
METADATA_VERSION = "validated-handoff-metadata-v1"
FINGERPRINT_ALGORITHM = "sha256-pandas-hash-pandas-object-v1"
FILES = ("validated.parquet", "schema.json", "validation-audit.json", "provenance.json")
ROW_ORDER = ["SKU_ID", "Warehouse_ID", "Date"]
CONTRACT_REFERENCE = "docs/data-cleaning-and-validation.md"

# Reviewed project defaults; overrides remain available for synthetic/development use.
PROJECT_INPUT = Path("data/raw/supply_chain_dataset1.csv")
PROJECT_SOURCE_RECEIPT = Path("data/raw/source-receipt.json")
PROJECT_START = "2024-01-01"
PROJECT_END = "2024-12-30"
PROJECT_PURPOSE = "shared validated source preparation"
PROJECT_DATA_VERSION = "supply-chain-dataset1-validated-v1"
PROJECT_AUTHORIZATION_REFERENCE = "https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/102"


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class HandoffResult:
    directory: Path
    provenance_sha256: str


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Explicit {name} is required.")
    return value


def _component(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", value):
        raise ValueError("data_version must be a safe single path component.")
    # Keep the same version safe on Windows as well as WSL/Linux.
    if value.endswith(".") or value.split(".")[0].upper() in {
        "CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(1, 10)],
        *[f"LPT{i}" for i in range(1, 10)],
    }:
        raise ValueError("data_version is a reserved path component.")
    return value


def _scope(start: str, end: str, purpose: str, authorization_reference: str) -> dict[str, Any]:
    for value in (start, end):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError("Scope dates require YYYY-MM-DD.")
    dates = pd.to_datetime([start, end], format="%Y-%m-%d", errors="raise")
    if dates[0] > dates[1]:
        raise ValueError("Scope start must not follow end.")
    return {"start_date": start, "end_date": end, "columns": cleaning.COLUMNS,
            "validation_mode": "shared-source-quality", "purpose": _text(purpose, "purpose"),
            "authorization_reference": _text(authorization_reference, "authorization_reference")}


def _confined(root: Path, path: Path) -> Path:
    """Reject traversal and every symlink component, including dangling links."""
    root = root.absolute()
    path = path.absolute()
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise ValueError("Path escapes repository data area.") from exc
    if ".." in relative.parts or root.resolve() != root:
        raise ValueError("Repository path must not redirect through symlinks.")
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("Data paths must not redirect through symlinks.")
    if not path.resolve().is_relative_to(root):
        raise ValueError("Path escapes repository data area.")
    return path


def _source_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    keys = {"identity", "citation", "snapshot_reference", "sha256", "size_bytes",
            "receipt_reference", "verification_method"}
    if set(receipt) != keys:
        raise ValueError("Source receipt must contain exactly the required source fields.")
    for key in {"identity", "snapshot_reference", "sha256", "verification_method"}:
        _text(receipt[key], f"source.{key}")
    for key in {"citation", "receipt_reference"}:
        if receipt[key] is not None:
            _text(receipt[key], f"source.{key}")
    if not re.fullmatch(r"[0-9a-f]{64}", receipt["sha256"]):
        raise ValueError("Source SHA-256 must be a lowercase 64-digit receipt.")
    if type(receipt["size_bytes"]) is not int or receipt["size_bytes"] <= 0:
        raise ValueError("Source size_bytes must be a positive integer.")
    if receipt["verification_method"] not in {"verified_acquisition_receipt", "explicit_verified_metadata",
                                               "manual-sha256-and-size-verification"}:
        raise ValueError("Source identity requires explicitly verified receipt metadata.")
    return dict(receipt)


def _json_read(path: Path) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON metadata key.")
            result[key] = value
        return result
    def invalid_constant(value: str) -> None:
        raise ValueError(f"Nonfinite JSON metadata: {value}")
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs,
                       parse_constant=invalid_constant)
    if not isinstance(value, dict):
        raise ValueError("Metadata must be a JSON object.")
    return value


def _json_write(path: Path, value: dict[str, Any]) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def _arrow_schema(frame: pd.DataFrame) -> pa.Schema:
    fields = []
    for column in cleaning.COLUMNS:
        dtype = (pa.date32() if column == "Date" else pa.string() if column in cleaning.IDS
                 else pa.from_numpy_dtype(frame[column].dtype))
        fields.append(pa.field(column, dtype, nullable=False))
    return pa.schema(fields)


def _schema_metadata(frame: pd.DataFrame) -> dict[str, Any]:
    arrow = _arrow_schema(frame)
    return {"schema_version": SCHEMA_VERSION, "ordered_columns": cleaning.COLUMNS,
            "columns": [{"name": f.name, "logical_type": str(f.type), "storage_type": str(f.type),
                         "pandas_dtype": str(frame[f.name].dtype), "nullable": False} for f in arrow],
            "native_key": cleaning.KEY, "row_order": ROW_ORDER,
            "date_representation": "date32: timezone-naive calendar day",
            "missing_representation": "Arrow null; missing/blank source values block shared publication",
            "format": "parquet", "engine": "pyarrow", "index": False}


def _write_parquet(frame: pd.DataFrame, path: Path) -> None:
    table = pa.Table.from_pandas(frame, schema=_arrow_schema(frame), preserve_index=False, safe=True)
    table = table.replace_schema_metadata(None)
    pq.write_table(table, path, compression="snappy", version="2.6")
    with path.open("rb") as stream:
        os.fsync(stream.fileno())


def _read_parquet(path: Path, schema: dict[str, Any]) -> pd.DataFrame:
    # ParquetFile reads exactly one file, never neighboring partitions/directories.
    table = pq.ParquetFile(path).read()
    if table.schema.names != cleaning.COLUMNS or table.schema.metadata:
        raise ValueError("Unexpected Parquet columns/index/schema metadata.")
    if schema.get("ordered_columns") != cleaning.COLUMNS:
        raise ValueError("Unexpected declared schema columns.")
    definitions = schema.get("columns", [])
    if [c.get("name") for c in definitions] != cleaning.COLUMNS:
        raise ValueError("Invalid column definitions.")
    for field, definition in zip(table.schema, definitions, strict=True):
        if str(field.type) != definition.get("storage_type") or field.nullable:
            raise ValueError("Parquet schema differs from declared storage types.")
        if table[field.name].null_count:
            raise ValueError("Shared validated data cannot contain missing values.")
    # Date conversion is declared decoding of date32, not normalization/repair.
    frame = table.to_pandas(date_as_object=False)
    for definition in definitions:
        column = definition["name"]
        frame[column] = frame[column].astype(definition["pandas_dtype"])
    if _schema_metadata(frame) != schema or not table.schema.equals(_arrow_schema(frame)):
        raise ValueError("Unsupported or inconsistent logical/schema metadata.")
    return frame


def _exact_equal(expected: pd.DataFrame, actual: pd.DataFrame) -> None:
    pd.testing.assert_frame_equal(expected, actual, check_dtype=True, check_exact=True,
                                  check_like=False, check_index_type=True)
    if cleaning.frame_fingerprint(expected) != cleaning.frame_fingerprint(actual):
        raise ValueError("Readback logical fingerprint differs.")


def _code_metadata() -> dict[str, Any]:
    implementation_root = Path(__file__).resolve().parents[2]
    def git(*args: str) -> str | None:
        result = subprocess.run(["git", "-C", str(implementation_root), *args],
                                text=True, capture_output=True, check=False)
        return result.stdout.strip() if result.returncode == 0 else None
    revision = git("rev-parse", "HEAD")
    status = git("status", "--porcelain")
    return {"git_commit_sha": revision, "dirty": bool(status) if status is not None else None,
            "source_sha256": {name: file_sha256(implementation_root / name) for name in
                              ("src/data/data_cleaning.py", "src/data/validated_handoff.py")}}


def _output(frame: pd.DataFrame) -> dict[str, Any]:
    return {"row_count": len(frame), "unique_key_count": len(frame[cleaning.KEY].drop_duplicates()),
            "date_min": frame.Date.min().date().isoformat(), "date_max": frame.Date.max().date().isoformat(),
            "logical_fingerprint": cleaning.frame_fingerprint(frame), "fingerprint_algorithm": FINGERPRINT_ALGORITHM}


def _file_record(directory: Path, name: str) -> dict[str, Any]:
    return {"path": name, "size_bytes": (directory / name).stat().st_size,
            "sha256": file_sha256(directory / name)}


def _verify_bundle_receipts(directory: Path, *, expected_provenance_sha256: str | None = None) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Verify publication metadata and actual file hashes against the published receipts."""
    if {p.name for p in directory.iterdir()} != set(FILES):
        raise ValueError("Incomplete or unexpected validated bundle files.")
    if any((directory / name).is_symlink() or not (directory / name).is_file() for name in FILES):
        raise ValueError("Bundle files must be regular non-symlink files.")
    if expected_provenance_sha256 is not None and file_sha256(directory / "provenance.json") != expected_provenance_sha256:
        raise ValueError("Provenance SHA-256 differs from external receipt.")
    provenance = _json_read(directory / "provenance.json")
    if (provenance.get("metadata_version"), provenance.get("schema_version"), provenance.get("rule_version")) != (
        METADATA_VERSION, SCHEMA_VERSION, RULE_VERSION
    ):
        raise ValueError("Unsupported handoff metadata/schema/rule version.")
    _component(provenance["data_version"])
    _source_receipt(provenance["source"])
    scope = provenance["scope"]
    if _scope(scope["start_date"], scope["end_date"], scope["purpose"], scope["authorization_reference"]) != scope:
        raise ValueError("Unsupported scope metadata.")
    if any(provenance.get(key) != "passed" for key in ("validation_status", "readback_status")):
        raise ValueError("Bundle validation/readback is incomplete.")
    if provenance.get("publication_status") != "complete":
        raise ValueError("Bundle publication is incomplete.")
    if provenance.get("human_review") != {"status": "pending_human_review", "reference": None}:
        raise ValueError("This schema cannot manufacture or rewrite human approval.")
    for key in ("preparation_id", "created_at_utc", "contract_reference"):
        _text(provenance[key], key)
    if provenance["contract_reference"] != CONTRACT_REFERENCE:
        raise ValueError("Unexpected validation contract reference.")
    if not re.fullmatch(r"[0-9a-f]{64}", provenance["input"]["scoped_fingerprint"]):
        raise ValueError("Invalid scoped input fingerprint.")
    for value in (provenance["contract_sha256"],):
        if value is not None and not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError("Invalid provenance fingerprint/hash.")
    if provenance["input"]["fingerprint_algorithm"] != FINGERPRINT_ALGORITHM:
        raise ValueError("Unsupported input fingerprint algorithm.")
    code = provenance["code"]
    if code["dirty"] is not None and type(code["dirty"]) is not bool:
        raise ValueError("Invalid code dirty-state disclosure.")
    if code["git_commit_sha"] is not None:
        _text(code["git_commit_sha"], "code revision")
    for name in ("src/data/data_cleaning.py", "src/data/validated_handoff.py"):
        if not re.fullmatch(r"[0-9a-f]{64}", code["source_sha256"][name]):
            raise ValueError("Invalid implementation source hash.")
    for name in ("python", "pandas", "numpy", "pyarrow"):
        _text(provenance["environment"][name], f"environment.{name}")
    records = provenance.get("files")
    if not isinstance(records, dict) or set(records) != set(FILES):
        raise ValueError("Bundle file identities are incomplete.")
    for name in FILES[:-1]:
        if records[name] != _file_record(directory, name):
            raise ValueError(f"File SHA-256/size/path mismatch: {name}")
    if records["provenance.json"] != {"path": "provenance.json", "size_bytes": None,
                                     "sha256": None, "hash_status": "self_reference"}:
        raise ValueError("Invalid provenance self-reference marker.")
    schema = _json_read(directory / "schema.json")
    audit = _json_read(directory / "validation-audit.json")
    for key in ("schema_version", "rule_version", "scope", "input_fingerprint", "output_fingerprint"):
        target = {"schema_version": SCHEMA_VERSION, "rule_version": RULE_VERSION, "scope": scope,
                  "input_fingerprint": provenance["input"]["scoped_fingerprint"],
                  "output_fingerprint": provenance["output"]["logical_fingerprint"]}[key]
        if audit.get(key) != target:
            raise ValueError("Audit/provenance identity mismatch.")
    evidence = audit["validation"]
    cleaning.require_valid_audit(evidence)
    if audit.get("output_ordered") is not True:
        raise ValueError("Invalid population/order evidence.")
    return provenance, schema, audit


def _verify_bundle(directory: Path, *, expected: pd.DataFrame | None = None,
                   expected_provenance_sha256: str | None = None) -> pd.DataFrame:
    """Fail closed; never reorder or repair records before comparing them."""
    provenance, schema, audit = _verify_bundle_receipts(
        directory, expected_provenance_sha256=expected_provenance_sha256,
    )
    scope = provenance["scope"]
    frame = _read_parquet(directory / "validated.parquet", schema)
    if expected is not None:
        _exact_equal(expected, frame)
    if not frame.Date.between(pd.Timestamp(scope["start_date"]), pd.Timestamp(scope["end_date"])).all():
        raise ValueError("Validated data exceed authorized scope.")
    # Verify equality to shared validation output; sorting cannot conceal disorder.
    accepted, current_audit = cleaning.build_validated_dataset(frame)
    _exact_equal(frame, accepted)
    if provenance["output"] != _output(frame):
        raise ValueError("Output population/fingerprint mismatch.")
    evidence = audit["validation"]
    for key in ("status", "checks", "input_rows", "output_rows", "unique_native_keys",
                "defective_row_positions", "distinct_values", "numeric_ranges"):
        if evidence.get(key) != current_audit[key]:
            raise ValueError(f"Audit evidence mismatch: {key}")
    missingness = cleaning.quality_tables(frame, current_audit)["missingness"].to_dict(orient="records")
    if audit.get("missingness") != missingness:
        raise ValueError("Audit missingness evidence mismatch.")
    if audit.get("output_ordered") is not True or provenance["input"]["row_count"] != len(frame):
        raise ValueError("Invalid population/order evidence.")
    return frame


def read_validated_handoff(repository: Path, data_version: str, *,
                           expected_provenance_sha256: str | None = None) -> pd.DataFrame:
    """Verify a named completed bundle; no source access or automatic discovery."""
    directory = _confined(repository / "data" / "processed" / "validated",
                          repository / "data" / "processed" / "validated" / _component(data_version))
    try:
        frame = _verify_bundle(directory, expected_provenance_sha256=expected_provenance_sha256)
        if _json_read(directory / "provenance.json")["data_version"] != data_version:
            raise ValueError("Bundle version does not match requested directory.")
        return frame
    except (KeyError, TypeError, AssertionError, OSError, pa.ArrowException) as exc:
        raise ValueError("Invalid or unreadable validated handoff.") from exc


@dataclass(frozen=True)
class ValidatedProjection:
    frame: pd.DataFrame
    provenance: dict[str, Any]
    provenance_sha256: str
    scope: dict[str, Any]


def read_validated_projection(*, repository: Path, data_version: str, columns: tuple[str, ...],
                              start: str, end: str,
                              expected_provenance_sha256: str | None = None) -> ValidatedProjection:
    """Decode only selected fields/dates; never rerun a whole-source outcome audit.

    The complete Parquet byte hash is recomputed before Arrow consumption.
    Byte hashing never decodes or evaluates reserved outcomes. Arrow projection
    and date filters restrict decoded data to the requested scope.
    """
    bounds = _scope(start, end, "scoped validated projection", "caller-specified scope")
    if not columns or len(set(columns)) != len(columns) or set(columns) - set(cleaning.COLUMNS):
        raise ValueError("Projection columns must be a unique subset of the validated schema.")
    directory = _confined(repository / "data" / "processed" / "validated",
                          repository / "data" / "processed" / "validated" / _component(data_version))
    try:
        path = directory / "validated.parquet"
        before = path.stat()
        anchor = file_sha256(directory / "provenance.json")
        provenance, schema, audit = _verify_bundle_receipts(
            directory, expected_provenance_sha256=expected_provenance_sha256 or anchor,
        )
        if provenance["data_version"] != data_version:
            raise ValueError("Bundle version does not match requested directory.")
        if start < provenance["scope"]["start_date"] or end > provenance["scope"]["end_date"]:
            raise ValueError("Projection scope exceeds the validated handoff scope.")
        parquet = pq.ParquetFile(path)
        physical = parquet.schema_arrow
        definitions = schema["columns"]
        if (physical.names != cleaning.COLUMNS or physical.metadata
                or schema.get("ordered_columns") != cleaning.COLUMNS
                or [d.get("name") for d in definitions] != cleaning.COLUMNS
                or schema.get("schema_version") != SCHEMA_VERSION
                or schema.get("native_key") != cleaning.KEY or schema.get("row_order") != ROW_ORDER
                or parquet.metadata.num_rows != provenance["output"]["row_count"]
                or audit["validation"]["output_rows"] != provenance["output"]["row_count"]):
            raise ValueError("Invalid declared Parquet schema/population.")
        for field, definition in zip(physical, definitions, strict=True):
            if (field.nullable or str(field.type) != definition.get("storage_type")
                    or definition.get("logical_type") != str(field.type) or definition.get("nullable") is not False):
                raise ValueError("Parquet schema differs from declared storage types.")
        if physical.field("Date").type != pa.date32():
            raise ValueError("Validated Date must use date32 calendar days.")
        # Push bounds and fields into Arrow BEFORE decoding to pandas or examining demand.
        table = pq.read_table(path, columns=list(columns), filters=[
            ("Date", ">=", pd.Timestamp(bounds["start_date"]).date()),
            ("Date", "<=", pd.Timestamp(bounds["end_date"]).date()),
        ])
        if any(table[column].null_count for column in columns):
            raise ValueError("Validated projection cannot contain missing values.")
        frame = table.to_pandas(date_as_object=False)
        for definition in definitions:
            if definition["name"] in columns:
                frame[definition["name"]] = frame[definition["name"]].astype(definition["pandas_dtype"])
        decoded_schema = pa.Schema.from_pandas(frame, preserve_index=False)
        for field in table.schema:
            if field.name == "Date":
                if not pd.api.types.is_datetime64_dtype(frame.Date.dtype):
                    raise ValueError("Declared Date decoding must preserve calendar datetime values.")
            elif field.name in cleaning.IDS:
                decoded = decoded_schema.field(field.name).type
                if field.type != pa.string() or not (pa.types.is_string(decoded) or pa.types.is_large_string(decoded)):
                    raise ValueError("Declared identifiers must preserve string values.")
            elif decoded_schema.field(field.name).type != field.type:
                raise ValueError("Declared projection dtypes disagree with physical storage types.")
        after = path.stat()
        if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
            raise ValueError("Validated Parquet changed during scoped loading.")
        if file_sha256(directory / "provenance.json") != anchor:
            raise ValueError("Validated provenance changed during scoped loading.")
        return ValidatedProjection(frame, provenance, anchor, {
            "start_date": start, "end_date": end, "columns": list(columns),
            "parent_data_hash_verification": "whole_file_sha256_verified",
        })
    except (KeyError, TypeError, AssertionError, OSError, pa.ArrowException) as exc:
        raise ValueError("Invalid or unreadable validated projection.") from exc


def _publish(staging: Path, destination: Path) -> None:
    """Portable exclusive reservation; provenance-last marks completed publication.

    There is no atomic directory rename claim. A crash after reservation leaves
    an incomplete version for human investigation, never an accepted handoff.
    """
    destination.mkdir(exist_ok=False)
    for name in FILES:  # provenance is always last
        with (staging / name).open("rb") as source, (destination / name).open("xb") as target:
            shutil.copyfileobj(source, target)
            target.flush()
            os.fsync(target.fileno())
        if file_sha256(destination / name) != file_sha256(staging / name):
            raise ValueError("Publication copy hash differs.")


def prepare_validated_handoff(*, repository: Path, input_path: Path, data_version: str,
                              start: str, end: str, purpose: str, authorization_reference: str,
                              source_receipt: dict[str, Any]) -> HandoffResult:
    """One scoped load/validate/serialize/readback/publish stage; no training."""
    repository = repository.absolute()
    _component(data_version)
    scope = _scope(start, end, purpose, authorization_reference)
    receipt = _source_receipt(source_receipt)
    raw_root = repository / "data" / "raw"
    source = _confined(raw_root, input_path)
    reference = Path(receipt["snapshot_reference"])
    if reference.is_absolute() or _confined(raw_root, repository / reference) != source:
        raise ValueError("Source receipt snapshot reference differs from input.")
    if source.stat().st_size != receipt["size_bytes"]:
        raise ValueError("Source receipt size mismatch; acquisition evidence requires review.")
    before = source.stat()
    destination = _confined(repository / "data" / "processed", repository / "data" / "processed" / "validated" / data_version)
    if destination.exists():
        raise FileExistsError("Validated data_version already exists; no overwrite permitted.")
    raw = cleaning.load_raw_source(source, start=start, end=end)
    validated, evidence = cleaning.build_validated_dataset(raw)
    after = source.stat()
    if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
        raise ValueError("Source changed during scoped preparation.")
    preparation_id = uuid4().hex
    interim = _confined(repository / "data" / "processed", repository / "data" / "processed" / "interim" / preparation_id)
    interim.parent.mkdir(parents=True, exist_ok=True)
    interim.mkdir(exist_ok=False)
    staging = interim / "validated-handoff"
    staging.mkdir()
    try:
        _write_parquet(validated, staging / "validated.parquet")
        _json_write(staging / "schema.json", _schema_metadata(validated))
        audit = {"schema_version": SCHEMA_VERSION, "rule_version": RULE_VERSION, "scope": scope,
                 "input_fingerprint": cleaning.frame_fingerprint(raw),
                 "output_fingerprint": cleaning.frame_fingerprint(validated), "validation": evidence,
                 "missingness": cleaning.quality_tables(validated, evidence)["missingness"].to_dict(orient="records"),
                 "output_ordered": True,
                 "not_performed": [{"check": "semantic_inventory_relationships", "reason": "No approved rejection rule; descriptive analysis remains separate"},
                                   {"check": "historical_eda_baseline", "reason": "Analysis-local context, not source validation"}]}
        _json_write(staging / "validation-audit.json", audit)
        contract = Path(__file__).resolve().parents[2] / CONTRACT_REFERENCE
        provenance: dict[str, Any] = {"metadata_version": METADATA_VERSION, "schema_version": SCHEMA_VERSION,
                      "rule_version": RULE_VERSION, "data_version": data_version, "preparation_id": preparation_id,
                      "created_at_utc": datetime.now(timezone.utc).isoformat(), "source": receipt, "scope": scope,
                      "input": {"row_count": len(raw), "scoped_fingerprint": cleaning.frame_fingerprint(raw),
                                "fingerprint_algorithm": FINGERPRINT_ALGORITHM}, "output": _output(validated),
                      "contract_reference": CONTRACT_REFERENCE,
                      "contract_sha256": file_sha256(contract) if contract.is_file() else None,
                      "code": _code_metadata(),
                      "environment": {"python": platform.python_version(), "pandas": pd.__version__,
                                      "numpy": np.__version__, "pyarrow": pa.__version__},
                      "files": {name: _file_record(staging, name) for name in FILES[:-1]},
                      "validation_status": "passed", "readback_status": "passed", "publication_status": "complete",
                      "human_review": {"status": "pending_human_review", "reference": None}}
        provenance["files"]["provenance.json"] = {"path": "provenance.json", "size_bytes": None,
                                                  "sha256": None, "hash_status": "self_reference"}
        _json_write(staging / "provenance.json", provenance)
        _verify_bundle(staging, expected=validated)
        receipt_hash = file_sha256(staging / "provenance.json")
        _confined(repository / "data" / "processed", destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        _publish(staging, destination)
        read_validated_handoff(repository, data_version, expected_provenance_sha256=receipt_hash)
        return HandoffResult(destination, receipt_hash)
    finally:
        # Only this unpublished staging attempt is ours to clean.
        shutil.rmtree(staging)
        interim.rmdir()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=repository_root())
    parser.add_argument("--input", type=Path, default=PROJECT_INPUT)
    parser.add_argument("--data-version", default=PROJECT_DATA_VERSION)
    parser.add_argument("--start", default=PROJECT_START)
    parser.add_argument("--end", default=PROJECT_END)
    parser.add_argument("--purpose", default=PROJECT_PURPOSE)
    parser.add_argument("--authorization-reference", default=PROJECT_AUTHORIZATION_REFERENCE)
    parser.add_argument("--source-receipt", type=Path, default=PROJECT_SOURCE_RECEIPT,
                        help="JSON containing externally verified source identity/hash metadata")
    args = parser.parse_args(argv)
    try:
        input_path = args.input if args.input.is_absolute() else args.repository / args.input
        receipt_path = (args.source_receipt if args.source_receipt.is_absolute()
                        else args.repository / args.source_receipt)
        result = prepare_validated_handoff(repository=args.repository, input_path=input_path,
            data_version=args.data_version, start=args.start, end=args.end, purpose=args.purpose,
            authorization_reference=args.authorization_reference, source_receipt=_json_read(receipt_path))
    except (ValueError, OSError, AssertionError, KeyError, TypeError, pa.ArrowException) as exc:
        parser.exit(2, f"Validated handoff failed: {exc}\n")
    print(json.dumps({"directory": str(result.directory), "provenance_sha256": result.provenance_sha256}))


if __name__ == "__main__":
    main()
