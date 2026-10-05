"""Thin CLI wiring and direct compatibility aliases; no experiment execution."""
from unittest.mock import Mock

import pytest

from src.forecasting import authorization as authorization_module, execution, experiment, metadata, orchestration
from src.forecasting.authorization import ExecutionBlocked, ExecutionContext
from test_forecasting_orchestration import authorization


def test_argument_free_entrypoint_wires_resolved_context(monkeypatch):
    approved = authorization()
    context = ExecutionContext(approved, None, "synthetic", {}, None)
    frame = object()
    resolver = Mock(return_value=context)
    monkeypatch.setattr(experiment, "resolve_execution", resolver)
    loader, runner = Mock(return_value=frame), Mock()
    monkeypatch.setattr(experiment, "load_dataset", loader)
    monkeypatch.setattr(experiment, "run_validation", runner)
    experiment.main([])
    resolver.assert_called_once_with(experiment.DEFAULT_LAYOUT)
    runner.assert_called_once_with(frame, run_id=approved.run_id, authorization=approved, execution_context=context)
    loader.assert_called_once_with(context.dataset_path)


def test_final_cli_blocks_before_resolution_or_loading(monkeypatch):
    resolver, loader = Mock(), Mock()
    monkeypatch.setattr(experiment, "resolve_execution", resolver)
    monkeypatch.setattr(experiment, "load_dataset", loader)
    with pytest.raises(ExecutionBlocked, match="Gate 6"):
        experiment.main(["--stage", "final_evaluation"])
    resolver.assert_not_called()
    loader.assert_not_called()


def test_cli_cannot_load_or_run_without_authorization(monkeypatch):
    blocked = ExecutionBlocked("Missing human authorization")
    resolver = Mock(side_effect=blocked)
    loader, runner = Mock(), Mock()
    monkeypatch.setattr(experiment, "resolve_execution", resolver)
    monkeypatch.setattr(experiment, "load_dataset", loader)
    monkeypatch.setattr(experiment, "run_validation", runner)
    with pytest.raises(ExecutionBlocked) as caught:
        experiment.main([])
    assert caught.value is blocked
    loader.assert_not_called()
    runner.assert_not_called()


def test_legacy_public_imports_are_direct_authoritative_aliases():
    for name in ("ExecutionBlocked", "ExecutionContext", "RunScope", "ValidationAuthorization", "resolve_execution"):
        assert getattr(execution, name) is getattr(authorization_module, name)
    for name in ("ExecutionBlocked", "RunScope", "ValidationAuthorization"):
        assert getattr(metadata, name) is getattr(authorization_module, name)
    for name in ("Candidate", "planned_candidates", "run_validation", "run_final_evaluation"):
        assert getattr(experiment, name) is getattr(orchestration, name)
