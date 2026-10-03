"""Synthetic final authorization fixtures; no project dataset or real run record."""
import json
import shutil
from unittest.mock import Mock

import pandas as pd
import pytest

from src.forecasting import final_authorization as authority
from src.forecasting.artifacts import file_hash, json_text
from src.forecasting.authorization import ExecutionBlocked
from src.forecasting.evaluation import frame_hash
from src.forecasting.metadata import REPOSITORY, runtime_versions, source_hashes
from src.forecasting.paths import RepositoryLayout


def historical_panel():
    return pd.DataFrame([
        {"SKU_ID": sku, "Warehouse_ID": warehouse, "Date": day, "Units_Sold": base + offset % 5}
        for sku, warehouse, base in (("A", "W1", 2), ("B", "W2", 8))
        for offset, day in enumerate(pd.date_range("2024-01-01", authority.TRAINING_END))
    ])


@pytest.fixture
def final_context(tmp_path, monkeypatch):
    layout = RepositoryLayout(tmp_path)
    # Copy source/contracts only, never data, models or real authorization records.
    paths = {*source_hashes(REPOSITORY), authority.FREEZE_PATH, authority.POLICY_PATH, "docs/protocol.md"}
    for relative in paths:
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPOSITORY / relative, destination)
    freeze = authority.read_freeze(tmp_path / authority.FREEZE_PATH)
    anchor = layout.run_directory(freeze.validation_run_id)
    anchor.mkdir(parents=True)
    retained = {
        "protocol_hash": file_hash(tmp_path / "docs/protocol.md"),
        "feature_contract_hash": file_hash(tmp_path / "docs/forecasting-feature-engineering.md"),
        "requirements_hash": file_hash(tmp_path / "requirements.txt"),
        "python_version": "3.12.3", "library_versions": runtime_versions(tmp_path),
        "dataset_reference": layout.dataset.relative_to(tmp_path).as_posix(),
    }
    (anchor / "run_metadata.json").write_text(json_text(retained))
    (anchor / "run_manifest.json").write_text(json_text({
        "metadata_hash": file_hash(anchor / "run_metadata.json"),
        "run_id": freeze.validation_run_id, "final_status": "verified_completed",
        "fixture": "synthetic authorization binding only",
    }))
    manifest_hash = file_hash(anchor / "run_manifest.json")
    path = tmp_path / authority.FREEZE_PATH
    path.write_text(path.read_text().replace(freeze.validation_manifest_sha256, manifest_hash))
    freeze = authority.read_freeze(path)
    payload = {
        "run_id": "synthetic-final", "evaluation_stage": "final_evaluation", "final_run_authorized": True,
        "freeze_hash": file_hash(path), "policy_hash": file_hash(tmp_path / authority.POLICY_PATH),
        "protocol_hash": file_hash(tmp_path / "docs/protocol.md"),
        "feature_contract_hash": file_hash(tmp_path / "docs/forecasting-feature-engineering.md"),
        "requirements_hash": file_hash(tmp_path / "requirements.txt"), "source_hashes": source_hashes(tmp_path),
        "validation_run_id": freeze.validation_run_id, "validation_manifest_sha256": manifest_hash,
        "input_view_hash": frame_hash(historical_panel()), "validated_provenance_hash": "a" * 64,
        "python_version": "3.12.3", "library_versions": runtime_versions(tmp_path),
        "approval_references": {key: "Synthetic fixture only" for key in authority.REFERENCE_NAMES},
        "temporal_policy": dict(authority.TEMPORAL_POLICY),
        "candidates": authority.candidate_payload(freeze.candidates),
        "producer_mapping": list(freeze.producer_mapping), "worker_count": 1,
    }
    record = tmp_path / authority.FINAL_RECORD_PATH
    record.parent.mkdir(parents=True)
    record.write_text(json_text(payload))
    verify = Mock(return_value={"status": "passed", "fixture": "synthetic"})
    monkeypatch.setattr(authority, "verify_completed", verify)
    return {"layout": layout, "payload": payload, "record": record, "freeze": freeze, "validation_check": verify}


def test_exact_scope_and_producer_mapping_are_read_from_reviewed_decision(final_context):
    fixture = final_context
    context = authority.resolve_final_execution(fixture["layout"])
    candidates = context.authorization.candidates
    assert len(candidates) == 28
    assert len({c.key for c in candidates}) == 28
    assert sum(c.model in authority.PRIMARY_MODELS for c in candidates) == 12
    assert sum(c.model in authority.SUPPORTIVE_MODELS for c in candidates) == 8
    assert sum(not c.learned for c in candidates) == 8
    assert context.authorization.producer_mapping == fixture["freeze"].producer_mapping
    fixture["validation_check"].assert_called_once_with(
        fixture["layout"].run_directory(context.authorization.validation_run_id))


@pytest.mark.parametrize("field", [
    "freeze_hash", "policy_hash", "protocol_hash", "feature_contract_hash", "requirements_hash",
    "validation_manifest_sha256", "input_view_hash", "validated_provenance_hash",
])
def test_authorization_hashes_must_be_well_formed(final_context, field):
    payload = dict(final_context["payload"], **{field: "not-a-hash"})
    with pytest.raises(ExecutionBlocked):
        authority.FinalAuthorization.from_payload(payload)


@pytest.mark.parametrize("mutation", [
    "missing", "extra", "duplicate", "reordered", "configuration", "horizon", "role", "producer", "false_permission",
    "boolean_worker", "threads", "dates", "references", "reference_pending", "environment",
])
def test_malformed_or_different_scope_authorization_is_blocked(final_context, mutation):
    payload = json.loads(json_text(final_context["payload"]))
    if mutation == "missing":
        del payload["approval_references"]["specific_final_run"]
    elif mutation == "extra":
        payload["unexpected"] = True
    elif mutation == "duplicate":
        payload["candidates"][-1] = payload["candidates"][0]
    elif mutation == "reordered":
        payload["candidates"].reverse()
    elif mutation == "configuration":
        payload["candidates"][0]["configuration_id"] = "GBM001"
    elif mutation == "horizon":
        payload["candidates"][0]["horizon"] = True
    elif mutation == "role":
        payload["candidates"][0]["model"] = "ridge"
    elif mutation == "producer":
        payload["producer_mapping"][0]["configuration_id"] = "GBM001"
    elif mutation == "false_permission":
        payload["final_run_authorized"] = False
    elif mutation == "boolean_worker":
        payload["worker_count"] = True
    elif mutation == "threads":
        payload["worker_count"] = 2
    elif mutation == "dates":
        payload["temporal_policy"]["training_end"] = "2024-12-03"
    elif mutation == "references":
        payload["approval_references"] = {}
    elif mutation == "reference_pending":
        payload["approval_references"]["specific_final_run"] = "pending"
    elif mutation == "environment":
        payload["library_versions"]["numpy"] = "0"
    final_context["record"].write_text(json_text(payload))
    with pytest.raises(ExecutionBlocked):
        authority.resolve_final_execution(final_context["layout"])


@pytest.mark.parametrize("path", [
    authority.FREEZE_PATH, authority.POLICY_PATH, "docs/protocol.md",
    "docs/forecasting-feature-engineering.md", "requirements.txt",
])
def test_changed_approved_scientific_document_blocks_execution(final_context, path):
    with (final_context["layout"].root / path).open("a") as stream:
        stream.write("\n# synthetic change\n")
    with pytest.raises(ExecutionBlocked):
        authority.resolve_final_execution(final_context["layout"])


def test_missing_record_and_unverifiable_validation_block_before_run_creation(final_context):
    record = final_context["record"]
    record.unlink()
    with pytest.raises(ExecutionBlocked):
        authority.resolve_final_execution(final_context["layout"])
    record.write_text(json_text(final_context["payload"]))
    final_context["validation_check"].side_effect = ValueError("Synthetic invalid validation bundle")
    with pytest.raises(ExecutionBlocked):
        authority.resolve_final_execution(final_context["layout"])
    assert not final_context["layout"].run_directory("synthetic-final").exists()


def test_duplicate_json_and_consumed_storage_are_rejected(final_context):
    record = final_context["record"]
    record.write_text('{"run_id":"a","run_id":"b"}')
    with pytest.raises(ExecutionBlocked):
        authority.resolve_final_execution(final_context["layout"])
    record.write_text(json_text(final_context["payload"]))
    final_context["layout"].model_run_directory("synthetic-final").mkdir(parents=True)
    with pytest.raises(ExecutionBlocked, match="consumed"):
        authority.resolve_final_execution(final_context["layout"])


def test_authorization_change_during_run_is_blocked(final_context):
    context = authority.resolve_final_execution(final_context["layout"])
    final_context["record"].write_text(json_text(final_context["payload"]) + "\n")
    with pytest.raises(ExecutionBlocked, match="changed during"):
        context.revalidate()


def test_reviewed_primary_and_producer_tables_cannot_diverge(final_context):
    path = final_context["layout"].root / authority.FREEZE_PATH
    text = path.read_text()
    heading = "## Separate downstream forecasting-framework producer decision"
    before, after = text.split(heading)
    path.write_text(before + heading + after.replace("GBM018", "GBM001", 1))
    with pytest.raises(ExecutionBlocked):
        authority.read_freeze(path)


def test_rebinding_current_feature_contract_cannot_replace_completed_validation_science(final_context):
    fixture = final_context
    path = fixture["layout"].root / "docs/forecasting-feature-engineering.md"
    path.write_text(path.read_text() + "\nSynthetic changed contract\n")
    payload = fixture["payload"]
    payload["feature_contract_hash"] = file_hash(path)
    payload["source_hashes"] = source_hashes(fixture["layout"].root)
    fixture["record"].write_text(json_text(payload))
    with pytest.raises(ExecutionBlocked, match="completed validation"):
        authority.resolve_final_execution(fixture["layout"])


@pytest.mark.parametrize("provenance_change", ["source_bytes", "recorded_source"])
def test_source_provenance_does_not_bind_final_execution_permission(final_context, provenance_change):
    fixture = final_context
    if provenance_change == "source_bytes":
        path = fixture["layout"].root / "src/forecasting/final_artifacts.py"
        path.write_text(path.read_text() + "\n# Synthetic implementation correction\n")
    else:
        fixture["payload"]["source_hashes"]["src/forecasting/final_artifacts.py"] = "b" * 64
        fixture["record"].write_text(json_text(fixture["payload"]))
    context = authority.resolve_final_execution(fixture["layout"])
    context.revalidate()
    assert context.authorization.candidates == fixture["freeze"].candidates
    assert context.authorization.producer_mapping == fixture["freeze"].producer_mapping


def test_source_change_after_resolution_does_not_revoke_scientific_authorization(final_context):
    context = authority.resolve_final_execution(final_context["layout"])
    path = final_context["layout"].root / "src/forecasting/final_evaluation.py"
    path.write_text(path.read_text() + "\n# Synthetic correction\n")
    context.revalidate()


@pytest.mark.parametrize("owner", ["artifacts", "models", "reports"])
def test_defect_rerun_requires_an_unused_new_id_and_keeps_frozen_scope(final_context, owner):
    fixture, layout = final_context, final_context["layout"]
    previous = {"artifacts": layout.run_directory, "models": layout.model_run_directory,
                "reports": layout.draft_report_directory}[owner]("synthetic-final")
    previous.mkdir(parents=True)
    evidence = previous / "retained.txt"
    evidence.write_text("Synthetic failed historical evidence")
    before = evidence.read_bytes()
    with pytest.raises(ExecutionBlocked, match="consumed"):
        authority.resolve_final_execution(layout)
    fixture["payload"]["run_id"] = "synthetic-corrected"
    fixture["payload"]["approval_references"]["specific_final_run"] = "Synthetic explicit defect-correction approval"
    fixture["record"].write_text(json_text(fixture["payload"]))
    context = authority.resolve_final_execution(layout)
    assert context.authorization.run_id == "synthetic-corrected"
    assert context.authorization.candidates == fixture["freeze"].candidates
    assert context.authorization.producer_mapping == fixture["freeze"].producer_mapping
    assert evidence.read_bytes() == before
    assert not layout.run_directory("synthetic-corrected").exists()
