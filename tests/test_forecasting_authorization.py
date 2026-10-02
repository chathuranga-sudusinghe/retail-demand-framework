"""Human gate parsing/resolution checks with synthetic records only; no real run."""
from dataclasses import asdict, replace
import hashlib
import json

import pytest

from src.forecasting import authorization as authorization_module
from src.forecasting.authorization import ExecutionBlocked, ValidationAuthorization
from src.forecasting.paths import REPOSITORY, RepositoryLayout, approved_dataset, execution_record
from test_forecasting_orchestration import authorization, scope


def local_record(tmp_path, monkeypatch):
    approved = authorization()
    path = execution_record(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(asdict(approved)))
    monkeypatch.setattr(authorization_module.ValidationAuthorization, "validate", lambda self, root, run_id: None)
    return approved, path


def test_resolves_exact_reviewed_id_and_consumed_run(tmp_path, monkeypatch):
    approved, path = local_record(tmp_path, monkeypatch)
    dataset = approved_dataset(tmp_path)
    dataset.parent.mkdir(parents=True)
    dataset.write_bytes(b"synthetic existence marker; resolution never decodes data")
    context = authorization_module.resolve_execution(tmp_path)
    assert context.authorization.run_id == approved.run_id
    assert context.authorization_path == path and context.dataset_path == dataset
    destination = RepositoryLayout(tmp_path).run_directory(approved.run_id)
    destination.mkdir(parents=True)
    with pytest.raises(authorization_module.ExecutionBlocked, match="consumed"):
        authorization_module.resolve_execution(tmp_path)


def test_missing_dataset(tmp_path, monkeypatch):
    local_record(tmp_path, monkeypatch)
    with pytest.raises(authorization_module.ExecutionBlocked, match="dataset is missing"):
        authorization_module.resolve_execution(tmp_path)


@pytest.mark.parametrize("payload", [None, "{", "[]", "{}", '{"scope": null}'])
def test_missing_malformed_record(tmp_path, payload):
    if payload is not None:
        path = execution_record(tmp_path)
        path.parent.mkdir(parents=True)
        path.write_text(payload)
    with pytest.raises(authorization_module.ExecutionBlocked):
        authorization_module.resolve_execution(tmp_path)


def test_stale_record_does_not_read_dataset(tmp_path):
    approved = replace(authorization(), source_hashes={})
    path = execution_record(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(asdict(approved)))
    with pytest.raises(authorization_module.ExecutionBlocked, match="changed"):
        authorization_module.ValidationAuthorization.from_json(path).validate(REPOSITORY, approved.run_id)


def test_duplicate_execution_record_fields_rejected(tmp_path):
    path = tmp_path / "synthetic.json"
    path.write_text('{"run_id":"one","run_id":"two"}')
    with pytest.raises(authorization_module.ExecutionBlocked, match="malformed"):
        authorization_module.ValidationAuthorization.from_json(path)


def test_authorization_digest_uses_verified_snapshot_without_another_read(tmp_path, monkeypatch):
    approved, path = local_record(tmp_path, monkeypatch)
    payload = path.read_bytes()
    dataset = approved_dataset(tmp_path)
    dataset.parent.mkdir(parents=True)
    dataset.write_bytes(b"synthetic existence marker; resolution never decodes data")
    reads = []
    original_read = type(path).read_bytes

    def read_bytes(self):
        if self == path:
            reads.append(self)
            if len(reads) > 2:
                raise AssertionError("Authorization was reread after snapshot verification.")
        return original_read(self)

    monkeypatch.setattr(type(path), "read_bytes", read_bytes)
    context = authorization_module.resolve_execution(tmp_path)
    assert len(reads) == 2
    assert context.authorization == approved
    assert context.authorization_payload == json.loads(payload)
    assert context.authorization_digest == hashlib.sha256(payload).hexdigest()


def test_resolution_retains_supplied_layout_and_legacy_path_argument(tmp_path, monkeypatch):
    approved, path = local_record(tmp_path, monkeypatch)
    layout = RepositoryLayout(tmp_path)
    layout.dataset.parent.mkdir(parents=True)
    layout.dataset.write_bytes(b"synthetic existence marker; resolution never decodes data")
    context = authorization_module.resolve_execution(layout)
    assert context.layout is layout
    assert context.authorization_path == layout.execution_record == path
    assert context.dataset_path == layout.dataset
    assert context.authorization == approved
    assert authorization_module.resolve_execution(tmp_path).layout == layout


@pytest.mark.parametrize("change", [
    {"evaluation_stage": "final_evaluation"}, {"validation_run_authorized": False},
    {"run_id": "other"}, {"worker_count": 2}, {"worker_count": True},
    {"protocol_hash": "0" * 64}, {"protocol_version": "old"}, {"schema_version": "old"},
    {"source_hashes": {}}, {"input_view_hash": "not-a-hash"},
    {"implementation_acceptance_reference": "pending"}, {"specific_run_reference": ""},
])
def test_authorization_is_specific_and_source_bound(change):
    approved = authorization()
    with pytest.raises(ExecutionBlocked):
        replace(approved, **change).validate(REPOSITORY, approved.run_id)


@pytest.mark.parametrize("change", [
    {"primary_models": ("catboost", "xgboost")}, {"primary_models": ("ridge",)},
    {"primary_models": ("xgboost", "xgboost")}, {"horizons": (28, 1)}, {"horizons": (True,)},
    {"baselines": ("naive",), "baseline_exclusions": ()},
    {"baseline_approval_references": ()}, {"horizons": ()},
])
def test_scope_has_no_grid_expansion_no_silent_baseline_omission(change):
    with pytest.raises(ExecutionBlocked):
        replace(scope(), **change).validate()


def test_scope_json_roundtrip_and_no_approval_record_is_generated_by_runner(tmp_path):
    from dataclasses import asdict
    original = authorization()
    path = tmp_path / "synthetic-approval.json"
    path.write_text(json.dumps(asdict(original)))
    loaded = ValidationAuthorization.from_json(path)
    assert loaded == original
    loaded.validate(REPOSITORY, loaded.run_id)
    layout = RepositoryLayout(REPOSITORY)
    for directory in (layout.run_directory(loaded.run_id), layout.model_run_directory(loaded.run_id),
                      layout.draft_report_directory(loaded.run_id)):
        assert not directory.exists()


@pytest.mark.parametrize("method", ["run_directory", "model_run_directory", "draft_report_directory"])
@pytest.mark.parametrize("kind", ["empty_directory", "partial_directory", "file"])
def test_any_existing_run_location_blocks_before_dataset_check(tmp_path, monkeypatch, method, kind):
    approved, record = local_record(tmp_path, monkeypatch)
    payload = record.read_bytes()
    layout = RepositoryLayout(tmp_path)
    destination = getattr(layout, method)(approved.run_id)
    destination.parent.mkdir(parents=True)
    if kind == "file":
        destination.write_bytes(b"original evidence")
    else:
        destination.mkdir()
        if kind == "partial_directory":
            (destination / "partial.tmp").write_bytes(b"interrupted evidence")
    before = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    original_is_file = type(layout.dataset).is_file
    def check_file(path):
        if path == layout.dataset:
            raise AssertionError("Consumed storage must block before the dataset check")
        return original_is_file(path)
    with monkeypatch.context() as guard:
        guard.setattr(type(layout.dataset), "is_file", check_file)
        with pytest.raises(ExecutionBlocked, match="consumed"):
            authorization_module.resolve_execution(layout)
    assert record.read_bytes() == payload
    assert before == {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert not (layout.run_directory(approved.run_id) / "run_manifest.json").exists()


@pytest.mark.parametrize("method", ["run_directory", "model_run_directory", "draft_report_directory"])
@pytest.mark.parametrize("target_kind", ["inside", "outside", "missing"])
def test_redirected_run_locations_block_before_dataset_check(tmp_path, monkeypatch, method, target_kind):
    repository = tmp_path / "repository"
    repository.mkdir()
    approved, record = local_record(repository, monkeypatch)
    payload = record.read_bytes()
    layout = RepositoryLayout(repository)
    destination = getattr(layout, method)(approved.run_id)
    destination.parent.mkdir(parents=True)
    target = (repository if target_kind == "inside" else tmp_path) / "redirected"
    if target_kind != "missing":
        target.mkdir()
    destination.symlink_to(target, target_is_directory=True)
    before = set(tmp_path.rglob("*"))
    original_is_file = type(layout.dataset).is_file
    def check_file(path):
        if path == layout.dataset:
            raise AssertionError("Redirected storage must block before the dataset check")
        return original_is_file(path)
    with monkeypatch.context() as guard:
        guard.setattr(type(layout.dataset), "is_file", check_file)
        with pytest.raises(ExecutionBlocked, match="invalid or redirected") as caught:
            authorization_module.resolve_execution(layout)
    assert isinstance(caught.value.__cause__, ValueError)
    assert record.read_bytes() == payload
    assert set(tmp_path.rglob("*")) == before
    if target.exists():
        assert not list(target.iterdir())


@pytest.mark.parametrize("relative,method", [
    ("artifacts", "run_directory"),
    ("artifacts/forecasting", "run_directory"),
    ("models", "model_run_directory"),
    ("models/forecasting", "model_run_directory"),
    ("reports", "draft_report_directory"),
    ("reports/forecasting", "draft_report_directory"),
    ("reports/forecasting/drafts", "draft_report_directory"),
])
def test_non_directory_storage_ancestor_blocks_before_dataset_check(tmp_path, monkeypatch, relative, method):
    approved, record = local_record(tmp_path, monkeypatch)
    payload = record.read_bytes()
    layout = RepositoryLayout(tmp_path)
    destination = getattr(layout, method)(approved.run_id)
    blocker = tmp_path / relative
    blocker.parent.mkdir(parents=True, exist_ok=True)
    blocker.write_bytes(b"original file")
    before = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    original_is_file = type(layout.dataset).is_file
    def check_file(path):
        if path == layout.dataset:
            raise AssertionError("Invalid storage ancestors must block before the dataset check")
        return original_is_file(path)
    with monkeypatch.context() as guard:
        guard.setattr(type(layout.dataset), "is_file", check_file)
        with pytest.raises(ExecutionBlocked, match="invalid or redirected") as caught:
            authorization_module.resolve_execution(layout)
    assert isinstance(caught.value.__cause__, ValueError)
    assert "ancestors must be directories" in str(caught.value.__cause__)
    assert record.read_bytes() == payload
    assert before == {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert not destination.exists()
