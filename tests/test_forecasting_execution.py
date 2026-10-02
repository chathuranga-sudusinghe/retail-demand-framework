"""Scoped validated Parquet input; temporary synthetic data only."""
import json
from unittest.mock import Mock

import pandas as pd
import pytest

from src.data import data_cleaning as cleaning, validated_handoff as handoff
from src.forecasting import execution
from src.forecasting.authorization import ExecutionBlocked
from src.forecasting.paths import VALIDATED_DATASET_RELATIVE_PATH, RepositoryLayout
from forecasting_handoff_helpers import panel, publish_forecasting_handoff


@pytest.fixture
def validated_input(tmp_path):
    source = panel().replace({"SKU_ID": {"A": "001", "B": "002"}, "Warehouse_ID": {"W1": "01", "W2": "02"}})
    return publish_forecasting_handoff(tmp_path, source)


def test_parquet_loader_preserves_identity_dates_values_and_projection(tmp_path, validated_input, monkeypatch):
    forbidden = Mock(side_effect=AssertionError("Forecasting must not access raw CSV or revalidate full data"))
    monkeypatch.setattr(cleaning, "load_raw_source", forbidden)
    monkeypatch.setattr(cleaning, "build_validated_dataset", forbidden)
    monkeypatch.setattr(handoff, "_read_parquet", forbidden)
    monkeypatch.setattr(pd, "read_csv", forbidden)
    source = panel().replace({"SKU_ID": {"A": "001", "B": "002"}, "Warehouse_ID": {"W1": "01", "W2": "02"}})
    expected = source.loc[source.Date.le(pd.Timestamp("2024-12-02")), list(execution.FORECAST_INPUT_COLUMNS)].reset_index(drop=True)
    data = execution.load_dataset(RepositoryLayout(tmp_path).dataset)
    pd.testing.assert_frame_equal(data, expected, check_exact=True)
    assert set(data.SKU_ID) == {"001", "002"} and set(data.Warehouse_ID) == {"01", "02"}
    forbidden.assert_not_called()


def test_loader_pushes_projection_and_scope_into_arrow(tmp_path, validated_input, monkeypatch):
    original = handoff.pq.read_table
    calls = []
    def read(path, **kwargs):
        calls.append(kwargs)
        table = original(path, **kwargs)
        assert table.column("Date").to_pandas(date_as_object=False).max() <= pd.Timestamp("2024-04-28")
        return table
    monkeypatch.setattr(handoff.pq, "read_table", read)
    loaded = execution.load_projection(RepositoryLayout(tmp_path), fold_number=1)
    assert calls == [{"columns": list(execution.FORECAST_INPUT_COLUMNS), "filters": [
        ("Date", ">=", pd.Timestamp("2024-01-01").date()), ("Date", "<=", pd.Timestamp("2024-04-28").date())]}]
    assert loaded.provenance_sha256 == validated_input.provenance_sha256
    assert loaded.scope["parent_data_hash_verification"] == "whole_file_sha256_verified"


@pytest.mark.parametrize("column", execution.FORECAST_INPUT_COLUMNS)
def test_required_projection_columns_cannot_be_missing(tmp_path, validated_input, column):
    data = execution.load_projection(RepositoryLayout(tmp_path), fold_number=1).frame
    with pytest.raises(ValueError, match="required forecasting projection"):
        execution.forecasting_projection(data.drop(columns=column))


@pytest.mark.parametrize("defect", ["duplicate", "disorder", "missing", "negative", "fractional", "padded_id"])
def test_projection_rejects_defects_without_repair(tmp_path, validated_input, defect):
    data = execution.load_projection(RepositoryLayout(tmp_path), fold_number=1).frame
    if defect == "duplicate":
        data = pd.concat([data, data.iloc[[0]]], ignore_index=True)
    elif defect == "disorder":
        data = data.iloc[::-1].reset_index(drop=True)
    elif defect == "missing":
        data.loc[0, "Units_Sold"] = float("nan")
    elif defect == "negative":
        data.loc[0, "Units_Sold"] = -1
    elif defect == "fractional":
        data["Units_Sold"] = data.Units_Sold.astype(float)
        data.loc[0, "Units_Sold"] = 1.5
    else:
        data.loc[0, "SKU_ID"] = " 001"
    before = data.copy(deep=True)
    with pytest.raises((ValueError, AssertionError)):
        execution.forecasting_projection(data)
    pd.testing.assert_frame_equal(data, before, check_exact=True)


def test_raw_csv_is_never_a_forecasting_fallback(tmp_path):
    path = tmp_path / "data/raw/supply_chain_dataset1.csv"
    path.parent.mkdir(parents=True)
    panel().to_csv(path, index=False)
    with pytest.raises(ExecutionBlocked, match="validated Parquet"):
        execution.load_dataset(path)
    with pytest.raises(ExecutionBlocked, match="Parquet could not be loaded"):
        execution.load_dataset(RepositoryLayout(tmp_path).dataset)


@pytest.mark.parametrize("name", ["validated.parquet", "schema.json", "validation-audit.json", "provenance.json"])
def test_corrupt_validated_bundle_blocks_loading(tmp_path, validated_input, name):
    path = validated_input.directory / name
    path.write_bytes(path.read_bytes() + b"corruption")
    with pytest.raises(ExecutionBlocked):
        execution.load_dataset(RepositoryLayout(tmp_path).dataset)


def test_scoped_loader_hashes_actual_parent_bytes_before_arrow_consumption(tmp_path, validated_input, monkeypatch):
    original_hash = handoff.file_sha256
    original_read = handoff.pq.read_table
    hashed = []
    def hash_file(path):
        hashed.append(path)
        return original_hash(path)
    def read(path, **kwargs):
        assert path in hashed
        return original_read(path, **kwargs)
    monkeypatch.setattr(handoff, "file_sha256", hash_file)
    monkeypatch.setattr(handoff.pq, "read_table", read)
    loaded = execution.load_projection(RepositoryLayout(tmp_path), fold_number=4)
    assert RepositoryLayout(tmp_path).dataset in hashed
    assert loaded.scope["parent_data_hash_verification"] == "whole_file_sha256_verified"


def test_projection_and_loader_block_final_period_before_quantity_checks(tmp_path, monkeypatch):
    future = pd.DataFrame({"SKU_ID": ["001"], "Warehouse_ID": ["01"],
                           "Date": [pd.Timestamp("2024-12-03")], "Units_Sold": ["must-not-inspect"]})
    with pytest.raises(ExecutionBlocked, match="Reserved final"):
        execution.forecasting_projection(future)
    forbidden = Mock(side_effect=AssertionError("No final-period read"))
    monkeypatch.setattr(execution, "read_validated_projection", forbidden)
    for number in (0, 5, True, "final_evaluation"):
        with pytest.raises(ExecutionBlocked):
            execution.load_projection(RepositoryLayout(tmp_path), fold_number=number)
    forbidden.assert_not_called()


def test_inconsistent_declared_dtype_cannot_silently_cast_validated_projection(tmp_path, validated_input):
    directory = validated_input.directory
    schema_path = directory / "schema.json"
    schema = json.loads(schema_path.read_text())
    next(c for c in schema["columns"] if c["name"] == "Units_Sold")["pandas_dtype"] = "int8"
    schema_path.write_text(json.dumps(schema))
    provenance_path = directory / "provenance.json"
    provenance = json.loads(provenance_path.read_text())
    provenance["files"]["schema.json"] = {"path": "schema.json", "size_bytes": schema_path.stat().st_size,
                                          "sha256": handoff.file_sha256(schema_path)}
    provenance_path.write_text(json.dumps(provenance))
    with pytest.raises(ExecutionBlocked) as caught:
        execution.load_projection(RepositoryLayout(tmp_path), fold_number=1)
    assert "dtypes disagree" in str(caught.value.__cause__)


def test_same_size_parent_tampering_is_rejected_before_any_arrow_consumption(tmp_path, validated_input, monkeypatch):
    path = RepositoryLayout(tmp_path).dataset
    original = path.read_bytes()
    tampered = bytearray(original)
    tampered[8] ^= 1
    path.write_bytes(tampered)
    assert path.stat().st_size == len(original)
    forbidden = Mock(side_effect=AssertionError("Tampered bytes must fail before Arrow consumption"))
    monkeypatch.setattr(handoff.pq, "ParquetFile", forbidden)
    monkeypatch.setattr(handoff.pq, "read_table", forbidden)
    with pytest.raises(ValueError, match="File SHA-256/size/path mismatch: validated.parquet"):
        handoff.read_validated_projection(repository=tmp_path, data_version=handoff.PROJECT_DATA_VERSION,
            columns=execution.FORECAST_INPUT_COLUMNS, start="2024-01-01", end="2024-04-28")
    forbidden.assert_not_called()


@pytest.mark.parametrize("relative", [
    "validated.parquet",
    "data/raw/validated.parquet",
    "data/processed/validated/other-version/validated.parquet",
    "data/processed/validated/supply-chain-dataset1-validated-v1/other.parquet",
    "data/processed/validated/supply-chain-dataset1-validated-v1/extra/validated.parquet",
])
def test_approved_handoff_path_remains_strict_before_loading(tmp_path, monkeypatch, relative):
    forbidden = Mock(side_effect=AssertionError("Unapproved paths must not load data"))
    monkeypatch.setattr(execution, "load_projection", forbidden)
    with pytest.raises(ExecutionBlocked, match="approved validated Parquet handoff"):
        execution.load_dataset(tmp_path / relative)
    forbidden.assert_not_called()


def test_root_derivation_uses_declared_suffix_for_nested_and_relative_repositories(tmp_path, monkeypatch):
    root = tmp_path / "nested/alternate-repository"
    root.mkdir(parents=True)
    expected = panel().iloc[:1]
    loader = Mock(return_value=handoff.ValidatedProjection(expected, {}, "synthetic", {}))
    monkeypatch.setattr(execution, "load_projection", loader)
    monkeypatch.chdir(root)
    pd.testing.assert_frame_equal(execution.load_dataset(VALIDATED_DATASET_RELATIVE_PATH), expected)
    loader.assert_called_once_with(RepositoryLayout(root))
