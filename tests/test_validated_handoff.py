"""Synthetic validated handoffs only; no project data or experiments."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from src.data import data_cleaning as cleaning
from src.data import validated_handoff as handoff


@pytest.fixture
def source(tmp_path):
    rows = []
    for day, date in enumerate(pd.date_range("2024-01-01", periods=4)):
        for sku in ("001", "002"):
            rows.append({**dict.fromkeys(cleaning.COLUMNS, 0), "Date": date.strftime("%Y-%m-%d"),
                         "SKU_ID": sku, "Warehouse_ID": "01", "Supplier_ID": "NA", "Region": "001",
                         "Units_Sold": day, "Inventory_Level": 100, "Supplier_Lead_Time_Days": 2,
                         "Reorder_Point": 20, "Unit_Cost": 1.2345678901234567,
                         "Unit_Price": np.nextafter(2.0, 3.0), "Demand_Forecast": -0.0})
    path = tmp_path / "data/raw/source.csv"
    path.parent.mkdir(parents=True)
    pd.DataFrame(rows).sample(frac=1, random_state=17).to_csv(path, index=False)
    return path


def receipt(source):
    return {"identity": "synthetic", "citation": "synthetic test fixture", "snapshot_reference": "data/raw/source.csv",
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "size_bytes": source.stat().st_size,
            "receipt_reference": "synthetic-acquisition-review", "verification_method": "verified_acquisition_receipt"}


def publish(source, version="synthetic", **overrides):
    arguments = {"repository": source.parents[2], "input_path": source, "data_version": version,
                 "start": "2024-01-01", "end": "2024-01-04", "purpose": "synthetic tests only",
                 "authorization_reference": "synthetic test authorization", "source_receipt": receipt(source)}
    arguments.update(overrides)
    return handoff.prepare_validated_handoff(**arguments)


def metadata(result, name):
    return json.loads((result.directory / name).read_text())


def rewrite_json(result, name, value):
    (result.directory / name).write_text(json.dumps(value))


def rehash(result, name):
    provenance = metadata(result, "provenance.json")
    provenance["files"][name] = handoff._file_record(result.directory, name)
    rewrite_json(result, "provenance.json", provenance)


def test_programmatic_pipeline_exact_readback_and_provenance(source):
    before = source.read_bytes()
    expected, audit = cleaning.build_validated_dataset(cleaning.load_raw_source(source, start="2024-01-01", end="2024-01-04"))
    result = publish(source)
    actual = handoff.read_validated_handoff(source.parents[2], "synthetic", expected_provenance_sha256=result.provenance_sha256)
    pd.testing.assert_frame_equal(actual, expected, check_exact=True)
    assert source.read_bytes() == before
    assert list(actual.columns) == cleaning.COLUMNS
    assert set(actual.SKU_ID) == {"001", "002"}
    assert actual.Supplier_ID.eq("NA").all()
    assert actual.Date.dtype == expected.Date.dtype
    assert actual.isna().equals(expected.isna())
    assert {p.name for p in result.directory.iterdir()} == set(handoff.FILES)
    schema = metadata(result, "schema.json")
    assert schema["schema_version"] == handoff.SCHEMA_VERSION
    assert schema["format"] == "parquet" and schema["engine"] == "pyarrow"
    assert schema["native_key"] == cleaning.KEY and schema["row_order"] == handoff.ROW_ORDER
    assert schema["columns"][0]["logical_type"] == "date32[day]"
    table = pq.ParquetFile(result.directory / "validated.parquet").read()
    assert table.schema.names == cleaning.COLUMNS and table.schema.field("Date").type == pa.date32()
    assert not table.schema.metadata
    provenance = metadata(result, "provenance.json")
    assert provenance["source"] == receipt(source)
    assert provenance["human_review"] == {"status": "pending_human_review", "reference": None}
    assert provenance["output"]["row_count"] == provenance["input"]["row_count"] == 8
    assert provenance["output"]["logical_fingerprint"] == cleaning.frame_fingerprint(expected)
    assert provenance["environment"]["pyarrow"] == pa.__version__
    assert provenance["code"]["source_sha256"]["src/data/data_cleaning.py"]
    persisted_audit = metadata(result, "validation-audit.json")
    assert persisted_audit["validation"] == audit
    assert persisted_audit["scope"] == provenance["scope"]
    assert persisted_audit["output_ordered"]
    assert list((source.parents[2] / "data/processed/interim").iterdir()) == []


def test_two_versions_have_same_data_and_different_preparation_identity(source):
    first, second = publish(source, "v1"), publish(source, "v2")
    assert (first.directory / "validated.parquet").read_bytes() == (second.directory / "validated.parquet").read_bytes()
    assert metadata(first, "provenance.json")["preparation_id"] != metadata(second, "provenance.json")["preparation_id"]


@pytest.mark.parametrize("version", ["", "..", "../escape", "/absolute", "a/b", "a\\b", "CON", "name."])
def test_unsafe_version_blocks_before_source_loading(source, version, monkeypatch):
    monkeypatch.setattr(cleaning, "load_raw_source", lambda *a, **kw: pytest.fail("loaded before metadata validation"))
    with pytest.raises(ValueError):
        publish(source, version)


@pytest.mark.parametrize("field,value", [("sha256", "invalid"), ("sha256", "a" * 63),
    ("size_bytes", 0), ("size_bytes", True), ("identity", ""), ("verification_method", "not_verified"),
    ("snapshot_reference", "data/raw/another.csv")])
def test_source_receipt_validation(source, field, value):
    supplied = receipt(source)
    supplied[field] = value
    with pytest.raises(ValueError):
        publish(source, source_receipt=supplied)


def test_source_size_mismatch_and_missing_authorization_block(source):
    supplied = receipt(source)
    supplied["size_bytes"] += 1
    with pytest.raises(ValueError, match="size mismatch"):
        publish(source, source_receipt=supplied)
    with pytest.raises(ValueError, match="authorization_reference"):
        publish(source, authorization_reference="")


@pytest.mark.parametrize("defect", ["missing", "negative", "duplicate", "conflict", "gap"])
def test_bad_source_blocks_without_repair_or_publication(source, defect):
    raw = pd.read_csv(source, dtype=str, keep_default_na=False)
    if defect == "missing":
        raw.loc[0, "Units_Sold"] = ""
    elif defect == "negative":
        raw.loc[0, "Units_Sold"] = "-1"
    elif defect in {"duplicate", "conflict"}:
        extra = raw.iloc[[0]].copy()
        if defect == "conflict":
            extra["Units_Sold"] = "99"
        raw = pd.concat([raw, extra], ignore_index=True)
    else:
        raw = raw.drop(index=0)
    raw.to_csv(source, index=False)
    before = source.read_bytes()
    with pytest.raises(ValueError):
        publish(source)
    assert not (source.parents[2] / "data/processed/validated/synthetic").exists()
    assert source.read_bytes() == before


def test_scope_before_validation_and_no_implicit_source_hash(source, monkeypatch):
    raw = pd.read_csv(source, dtype=str, keep_default_na=False)
    raw.loc[raw.Date.eq("2024-01-04"), "Units_Sold"] = "excluded-defect"
    raw.to_csv(source, index=False)
    supplied = receipt(source)
    original_hash = handoff.file_sha256
    def confined_hash(path):
        assert path != source, "whole-source hashing is not authorized by scoped preparation"
        return original_hash(path)
    monkeypatch.setattr(handoff, "file_sha256", confined_hash)
    result = publish(source, end="2024-01-03", source_receipt=supplied)
    frame = handoff.read_validated_handoff(source.parents[2], "synthetic")
    assert len(frame) == 6 and frame.Date.max() == pd.Timestamp("2024-01-03")
    assert metadata(result, "provenance.json")["source"]["sha256"] == supplied["sha256"]


def test_existing_version_including_empty_directory_never_overwritten(source):
    result = publish(source)
    before = {p.name: p.read_bytes() for p in result.directory.iterdir()}
    with pytest.raises(FileExistsError):
        publish(source)
    assert before == {p.name: p.read_bytes() for p in result.directory.iterdir()}
    empty = result.directory.parent / "empty"
    empty.mkdir()
    with pytest.raises(FileExistsError):
        publish(source, "empty")
    assert not list(empty.iterdir())


def test_concurrent_publication_has_one_winner(source):
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(publish, source) for _ in range(2)]
        outcomes = []
        for future in futures:
            try:
                outcomes.append(future.result())
            except FileExistsError:
                outcomes.append(None)
    assert sum(result is not None for result in outcomes) == 1
    assert len(handoff.read_validated_handoff(source.parents[2], "synthetic")) == 8


@pytest.mark.parametrize("location", ["raw", "processed", "validated", "interim"])
def test_symlink_roots_rejected(source, tmp_path, location):
    repository = source.parents[2]
    outside = tmp_path / "outside"
    outside.mkdir()
    target = repository / "data" / location if location in {"raw", "processed"} else repository / "data/processed" / location
    if target.exists():
        if location == "raw":
            source.rename(outside / "source.csv")
        target.rmdir()
    target.parent.mkdir(exist_ok=True, parents=True)
    target.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        publish(source)
    assert not (outside / "synthetic").exists()


@pytest.mark.parametrize("filename", handoff.FILES)
def test_incomplete_bundle_rejected(source, filename):
    result = publish(source)
    (result.directory / filename).unlink()
    with pytest.raises(ValueError):
        handoff.read_validated_handoff(source.parents[2], "synthetic")


@pytest.mark.parametrize("filename", handoff.FILES[:-1])
def test_file_hash_mismatch_rejected(source, filename):
    result = publish(source)
    with (result.directory / filename).open("ab") as stream:
        stream.write(b"corrupt")
    with pytest.raises(ValueError, match="mismatch"):
        handoff.read_validated_handoff(source.parents[2], "synthetic")


def test_corrupt_parquet_rejected_even_if_manifest_rehashed(source):
    result = publish(source)
    (result.directory / "validated.parquet").write_bytes(b"not parquet")
    rehash(result, "validated.parquet")
    with pytest.raises(ValueError):
        handoff.read_validated_handoff(source.parents[2], "synthetic")


@pytest.mark.parametrize("defect", ["schema", "audit", "fingerprint", "approval", "scope", "version"])
def test_semantic_corruption_rejected(source, defect):
    result = publish(source)
    name = "provenance.json"
    value = metadata(result, name)
    if defect == "schema":
        name = "schema.json"
        value = metadata(result, name)
        value["columns"][0]["storage_type"] = "timestamp[ns]"
    elif defect == "audit":
        name = "validation-audit.json"
        value = metadata(result, name)
        value["validation"]["checks"]["missing_cells"] = 1
    elif defect == "fingerprint":
        value["output"]["logical_fingerprint"] = "a" * 64
    elif defect == "approval":
        value["human_review"]["status"] = "approved"
    elif defect == "scope":
        value["scope"]["end_date"] = "2024-01-02"
    else:
        value["data_version"] = "different"
    rewrite_json(result, name, value)
    if name != "provenance.json":
        rehash(result, name)
    with pytest.raises(ValueError):
        handoff.read_validated_handoff(source.parents[2], "synthetic")


def test_external_provenance_hash_detects_otherwise_valid_metadata_change(source):
    result = publish(source)
    provenance = metadata(result, "provenance.json")
    provenance["source"]["identity"] = "changed-identity"
    rewrite_json(result, "provenance.json", provenance)
    with pytest.raises(ValueError, match="external receipt"):
        handoff.read_validated_handoff(source.parents[2], "synthetic", expected_provenance_sha256=result.provenance_sha256)


def test_row_order_corruption_is_not_sorted_into_validity(source):
    result = publish(source)
    path = result.directory / "validated.parquet"
    table = pq.ParquetFile(path).read()
    pq.write_table(table.take(pa.array(list(reversed(range(len(table)))))), path)
    rehash(result, "validated.parquet")
    with pytest.raises((ValueError, AssertionError)):
        handoff.read_validated_handoff(source.parents[2], "synthetic")


@pytest.mark.parametrize("phase", ["write", "readback", "publish"])
def test_failure_cleans_only_owned_staging(source, monkeypatch, phase):
    repository = source.parents[2]
    other = repository / "data/processed/interim/other/validated-handoff"
    other.mkdir(parents=True)
    sentinel = other / "keep.txt"
    sentinel.write_text("unrelated")
    function = {"write": "_write_parquet", "readback": "_verify_bundle", "publish": "_publish"}[phase]
    def fail(*args, **kwargs):
        raise RuntimeError("injected")
    monkeypatch.setattr(handoff, function, fail)
    with pytest.raises(RuntimeError, match="injected"):
        publish(source)
    assert sentinel.read_text() == "unrelated"
    assert [p.name for p in other.parents[1].iterdir()] == ["other"]
    assert not (repository / "data/processed/validated/synthetic").exists()


def test_interrupted_final_copy_is_incomplete_not_deleted_or_reused(source, monkeypatch):
    original = handoff.shutil.copyfileobj
    calls = 0
    def interrupt(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("interrupted publication")
        return original(*args, **kwargs)
    monkeypatch.setattr(handoff.shutil, "copyfileobj", interrupt)
    with pytest.raises(RuntimeError):
        publish(source)
    destination = source.parents[2] / "data/processed/validated/synthetic"
    assert destination.is_dir() and not (destination / "provenance.json").exists()
    with pytest.raises(ValueError):
        handoff.read_validated_handoff(source.parents[2], "synthetic")
    with pytest.raises(FileExistsError):
        publish(source)


def test_cli_executes_one_complete_stage(source, tmp_path, capsys):
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(json.dumps(receipt(source)))
    handoff.main(["--repository", str(source.parents[2]), "--input", "data/raw/source.csv",
                  "--data-version", "cli", "--start", "2024-01-01", "--end", "2024-01-04",
                  "--purpose", "synthetic", "--authorization-reference", "test authorization",
                  "--source-receipt", str(receipt_path)])
    result = json.loads(capsys.readouterr().out)
    assert Path(result["directory"]).name == "cli"
    assert len(handoff.read_validated_handoff(source.parents[2], "cli", expected_provenance_sha256=result["provenance_sha256"])) == 8


def test_cli_missing_arguments_and_invalid_scope_fail(source, tmp_path):
    with pytest.raises(SystemExit) as exc:
        handoff.main([])
    assert exc.value.code == 2
    with pytest.raises(ValueError):
        publish(source, start="2024-01-05", end="2024-01-01")


@pytest.mark.parametrize("field", ["code", "environment", "missingness", "input_algorithm"])
def test_required_metadata_and_missingness_corruption_rejected(source, field):
    result = publish(source)
    name = "validation-audit.json" if field == "missingness" else "provenance.json"
    value = metadata(result, name)
    if field == "missingness":
        value["missingness"] = []
    elif field == "input_algorithm":
        value["input"]["fingerprint_algorithm"] = "unknown"
    else:
        del value[field]
    rewrite_json(result, name, value)
    if name != "provenance.json":
        rehash(result, name)
    with pytest.raises(ValueError):
        handoff.read_validated_handoff(source.parents[2], "synthetic")


@pytest.mark.parametrize("unavailable", [("citation",), ("receipt_reference",), ("citation", "receipt_reference")])
def test_unavailable_source_provenance_persisted_as_null(source, unavailable):
    supplied = receipt(source)
    for field in unavailable:
        supplied[field] = None
    result = publish(source, source_receipt=supplied)
    assert metadata(result, "provenance.json")["source"] == supplied
    assert len(handoff.read_validated_handoff(source.parents[2], "synthetic",
        expected_provenance_sha256=result.provenance_sha256)) == 8


@pytest.mark.parametrize("field", ["identity", "snapshot_reference", "sha256", "size_bytes", "verification_method"])
def test_required_source_receipt_fields_cannot_be_null(source, field):
    supplied = receipt(source)
    supplied[field] = None
    with pytest.raises(ValueError):
        publish(source, source_receipt=supplied)


@pytest.mark.parametrize("field", ["citation", "receipt_reference"])
@pytest.mark.parametrize("value", ["", "   ", 123])
def test_optional_source_provenance_requires_text_when_available(source, field, value):
    supplied = receipt(source)
    supplied[field] = value
    with pytest.raises(ValueError):
        publish(source, source_receipt=supplied)
