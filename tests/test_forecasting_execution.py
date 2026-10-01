"""Execution resolution uses synthetic records/data only; no real run."""
from dataclasses import asdict, replace
import hashlib
import json
from unittest.mock import Mock
import pytest
from src.forecasting import execution, experiment
from src.forecasting.paths import approved_dataset, execution_record
from test_forecasting_experiment import authorization


def local_record(tmp_path, monkeypatch):
    approved = authorization()
    path = execution_record(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(asdict(approved)))
    monkeypatch.setattr(execution.ValidationAuthorization, "validate", lambda self, root, run_id: None)
    return approved, path


def test_resolves_exact_reviewed_id_and_consumed_run(tmp_path, monkeypatch):
    approved, path = local_record(tmp_path, monkeypatch)
    dataset = approved_dataset(tmp_path)
    dataset.parent.mkdir(parents=True)
    dataset.write_text("Date,SKU_ID,Warehouse_ID,Units_Sold\n2024-01-01,A,W1,1\n")
    context = execution.resolve_execution(tmp_path)
    assert context.authorization.run_id == approved.run_id
    assert context.authorization_path == path and context.dataset_path == dataset
    destination = tmp_path / "outputs/revised-forecasting" / approved.run_id
    destination.mkdir(parents=True)
    with pytest.raises(execution.ExecutionBlocked, match="consumed"):
        execution.resolve_execution(tmp_path)


def test_missing_dataset(tmp_path, monkeypatch):
    local_record(tmp_path, monkeypatch)
    with pytest.raises(execution.ExecutionBlocked, match="dataset is missing"):
        execution.resolve_execution(tmp_path)


@pytest.mark.parametrize("payload", [None, "{", "[]", "{}", '{"scope": null}'])
def test_missing_malformed_record(tmp_path, payload):
    if payload is not None:
        path = execution_record(tmp_path)
        path.parent.mkdir(parents=True)
        path.write_text(payload)
    with pytest.raises(execution.ExecutionBlocked):
        execution.resolve_execution(tmp_path)


def test_stale_record_does_not_read_dataset(tmp_path):
    approved = replace(authorization(), source_hashes={})
    path = execution_record(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(asdict(approved)))
    from src.forecasting.paths import REPOSITORY
    with pytest.raises(execution.ExecutionBlocked, match="changed"):
        execution.ValidationAuthorization.from_json(path).validate(REPOSITORY, approved.run_id)


@pytest.mark.parametrize("header", ["Date,SKU_ID,Warehouse_ID,Units_Sold,Units_Sold", "Date,SKU_ID,Units_Sold"])
def test_required_headers_must_be_unique(tmp_path, header):
    path = tmp_path / "synthetic.csv"
    path.write_text(header + "\n")
    with pytest.raises(execution.ExecutionBlocked, match="exactly once"):
        execution.load_dataset(path)


def test_csv_loader_preserves_text_ids_and_excludes_source_fields(tmp_path):
    path = tmp_path / "synthetic.csv"
    path.write_text("Date,SKU_ID,Warehouse_ID,Units_Sold,Demand_Forecast\n2024-01-01,001,02,5,999\n")
    data = execution.load_dataset(path)
    assert data.SKU_ID.iloc[0] == "001" and data.Warehouse_ID.iloc[0] == "02"
    assert "Demand_Forecast" not in data


def test_argument_free_entrypoint_wires_resolved_context(monkeypatch):
    approved = authorization()
    context = execution.ExecutionContext(approved, None, "synthetic", {}, None)
    frame = object()
    resolver = Mock(return_value=context)
    monkeypatch.setattr(experiment, "resolve_execution", resolver)
    loader, runner = Mock(return_value=frame), Mock()
    monkeypatch.setattr(experiment, "load_dataset", loader)
    monkeypatch.setattr(experiment, "run_validation", runner)
    experiment.main([])
    resolver.assert_called_once_with(experiment.DEFAULT_LAYOUT)
    runner.assert_called_once_with(frame, run_id=approved.run_id, authorization=approved, execution_context=context)



def test_duplicate_execution_record_fields_rejected(tmp_path):
    path = tmp_path / "synthetic.json"
    path.write_text('{"run_id":"one","run_id":"two"}')
    with pytest.raises(execution.ExecutionBlocked, match="malformed"):
        execution.ValidationAuthorization.from_json(path)


def test_authorization_digest_uses_verified_snapshot_without_another_read(tmp_path, monkeypatch):
    approved, path = local_record(tmp_path, monkeypatch)
    payload = path.read_bytes()
    dataset = approved_dataset(tmp_path)
    dataset.parent.mkdir(parents=True)
    dataset.write_text("Date,SKU_ID,Warehouse_ID,Units_Sold\n2024-01-01,A,W1,1\n")
    reads = []
    original_read = type(path).read_bytes

    def read_bytes(self):
        if self == path:
            reads.append(self)
            if len(reads) > 2:
                raise AssertionError("Authorization was reread after snapshot verification.")
        return original_read(self)

    monkeypatch.setattr(type(path), "read_bytes", read_bytes)
    context = execution.resolve_execution(tmp_path)
    assert len(reads) == 2
    assert context.authorization == approved
    assert context.authorization_payload == json.loads(payload)
    assert context.authorization_digest == hashlib.sha256(payload).hexdigest()


def test_csv_header_parser_error_is_wrapped_before_pandas_loading(tmp_path, monkeypatch):
    path = tmp_path / "synthetic.csv"
    path.write_text("x" * (execution.csv.field_size_limit() + 1) + "\n")
    loader = Mock(side_effect=AssertionError("Malformed header must fail before data loading."))
    monkeypatch.setattr(execution.pd, "read_csv", loader)
    with pytest.raises(execution.ExecutionBlocked, match="CSV could not be loaded") as caught:
        execution.load_dataset(path)
    assert isinstance(caught.value.__cause__, execution.csv.Error)
    loader.assert_not_called()


def test_resolution_retains_supplied_layout_and_legacy_path_argument(tmp_path, monkeypatch):
    approved, path = local_record(tmp_path, monkeypatch)
    layout = execution.RepositoryLayout(tmp_path)
    layout.dataset.parent.mkdir(parents=True)
    layout.dataset.write_text("Date,SKU_ID,Warehouse_ID,Units_Sold\n2024-01-01,A,W1,1\n")
    context = execution.resolve_execution(layout)
    assert context.layout is layout
    assert context.authorization_path == layout.execution_record == path
    assert context.dataset_path == layout.dataset
    assert context.authorization == approved
    assert execution.resolve_execution(tmp_path).layout == layout
