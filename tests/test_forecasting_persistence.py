"""Persistence coordination checks using temporary synthetic authorization records."""
from dataclasses import asdict, replace
from hashlib import sha256
import json
from unittest.mock import Mock

import pytest

from src.forecasting import persistence
from src.forecasting.artifacts import ArtifactWriter, file_hash
from src.forecasting.authorization import ExecutionBlocked, ExecutionContext
from src.forecasting.paths import RepositoryLayout
from test_forecasting_orchestration import authorization


def snapshot_context(tmp_path):
    approved = authorization()
    layout = RepositoryLayout(tmp_path)
    path = layout.execution_record
    path.parent.mkdir(parents=True)
    # Noncanonical formatting proves the reviewed bytes survive without reserialization.
    payload = (json.dumps(asdict(approved), separators=(",", ":")) + "\n\n").encode()
    path.write_bytes(payload)
    context = ExecutionContext(approved, path, sha256(payload).hexdigest(), json.loads(payload), layout.dataset, layout)
    return approved, context, payload


def test_reviewed_authorization_snapshot_preserves_exact_bytes_and_source(tmp_path):
    approved, context, payload = snapshot_context(tmp_path)
    writer = ArtifactWriter(context.layout, approved.run_id)
    digest = persistence.persist_authorization(writer, approved, context)
    destination = writer.directory / "authorization.json"
    assert destination.read_bytes() == context.authorization_path.read_bytes() == payload
    assert digest == context.authorization_digest == file_hash(destination)
    assert not (writer.directory / "authorization.json.tmp").exists()


def test_changed_record_blocks_snapshot_without_refreshing_digest(tmp_path):
    approved, context, payload = snapshot_context(tmp_path)
    writer = ArtifactWriter(context.layout, approved.run_id)
    context.authorization_path.write_bytes(payload + b" ")
    with pytest.raises(ExecutionBlocked, match="changed after resolution"):
        persistence.persist_authorization(writer, approved, context)
    assert context.authorization_digest == sha256(payload).hexdigest()
    assert not list(writer.directory.iterdir())


def test_mismatched_context_blocks_before_reading_or_persisting(tmp_path, monkeypatch):
    approved, context, _ = snapshot_context(tmp_path)
    writer = ArtifactWriter(context.layout, approved.run_id)
    reader = Mock(side_effect=AssertionError("Cannot read a mismatched record"))
    monkeypatch.setattr(type(context.authorization_path), "read_bytes", reader)
    with pytest.raises(ExecutionBlocked, match="differs from authorization"):
        persistence.persist_authorization(writer, replace(approved, run_id="different"), context)
    reader.assert_not_called()
    assert not list(writer.directory.iterdir())


def test_supplied_authorization_is_retained_without_creating_a_local_approval(tmp_path):
    approved = authorization()
    layout = RepositoryLayout(tmp_path)
    writer = ArtifactWriter(layout, approved.run_id)
    digest = persistence.persist_authorization(writer, approved, None)
    snapshot = writer.directory / "authorization.json"
    assert json.loads(snapshot.read_text()) == json.loads(json.dumps(asdict(approved)))
    assert digest == file_hash(snapshot)
    assert not layout.execution_record.exists()


def test_failed_model_serialization_does_not_index_an_unpersisted_descriptor(tmp_path, monkeypatch):
    writer = ArtifactWriter(tmp_path, "synthetic-persistence")
    original = OSError("controlled serialization failure")
    serializer = Mock(side_effect=original)
    monkeypatch.setattr(persistence, "persist_model", serializer)
    metadata = {"model_artifacts": []}
    with pytest.raises(OSError) as caught:
        persistence.persist_candidate_model(writer, None, {}, None, None, metadata)
    assert caught.value is original
    assert metadata["model_artifacts"] == []
    serializer.assert_called_once_with(writer.directory, None, {}, None, None, metadata)
