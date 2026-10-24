"""Synthetic retained-case API checks; no retained evidence is regenerated."""

from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient
import pytest

from src.api.main import create_app
from src.decision_support import assessment
from src.decision_support.records import DecisionSupportRecord
from src.decision_support import retained_cases
from src.inventory_risk import runner
from src.inventory_risk.forecast_handoff import (
    MAPPING_VERSION,
    load_forecast_handoff,
)
from test_inventory_risk_forecast_handoff import synthetic_export


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def _inventory_source(handoff: Any) -> dict[str, Any]:
    return {
        "forecast_export_sha256": handoff.sha256,
        "forecast_source": handoff.document["source"],
        "mapping_version": MAPPING_VERSION,
        "snapshot_policy": "constructed-origin",
        "snapshot_basis": (
            "Synthetic constructed-origin fixture; source timing remains unknown."
        ),
    }


def _prospective_row(forecast: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    horizon = forecast["horizon"]
    gated = horizon == 28
    return {
        "SKU_ID": forecast["SKU_ID"],
        "Warehouse_ID": forecast["Warehouse_ID"],
        "forecast_origin": forecast["forecast_origin"],
        "horizon": horizon,
        "target_start_date": forecast["target_start_date"],
        "target_end_date": forecast["target_end_date"],
        "prediction": forecast["prediction"],
        "unit": forecast["unit"],
        "model": forecast["model"],
        "configuration_id": forecast["configuration_id"],
        "run_id": source["forecast_source"]["run_id"],
        "evaluation_stage": source["forecast_source"]["evaluation_stage"],
        "evidence_role": "primary",
        "source_export_sha256": source["forecast_export_sha256"],
        "source_provenance": json.dumps(source["forecast_source"], sort_keys=True),
        "Date": forecast["forecast_origin"],
        "Inventory_Level": None if gated else 0,
        "Reorder_Point": None if gated else 0,
        "origin_snapshot_available": None,
        "origin_snapshot_status": "unknown",
        "origin_snapshot_reason": "origin_snapshot_availability_not_established",
        "inventory_state_available": False,
        "inventory_basis": "constructed_origin_scenario",
        "snapshot_assumption": source["snapshot_basis"],
        "scenario_inventory_state_available": not gated,
        "analysis_inventory_state_available": not gated,
        "origin_exposure_state": (
            "unavailable" if gated else "scenario_already_at_or_below_threshold"
        ),
        "forecast_exposure_state": (
            "unavailable" if gated else "not_needed_scenario_origin_state"
        ),
        "inventory_buffer": None if gated else 0,
        "predicted_margin": None,
        "forecast_input_status": "available",
        "forecast_input_reason": "",
        "downstream_use_status": (
            "not_approved_for_downstream_use"
            if gated
            else "approved_method"
        ),
        "downstream_use_reason": (
            "28_day_downstream_use_requires_separate_approval" if gated else ""
        ),
        "methodology_status": runner.METHOD_STATUS,
        "method_assumptions": [source["snapshot_basis"]],
        "method_limitations": [runner.SCENARIO_LIMITATION],
    }


def _fixture_record(
    forecast: dict[str, Any],
    row: dict[str, Any],
    inventory_provenance: dict[str, Any],
    assessment_id: str,
) -> dict[str, Any]:
    horizon = forecast["horizon"]
    risk = None
    provenance = None
    unavailable = {
        "replenishment_recommendation": "No numerical replenishment output is supplied.",
        "uncertainty_or_error": "No agreed uncertainty method is supplied.",
    }
    components = {
        "forecast": "forecasting",
        "decision_support": "responsible_decision_support",
        "inventory_risk": "inventory_risk",
    }
    if horizon == 28:
        unavailable["inventory_risk_evidence"] = (
            "28_day_downstream_use_requires_separate_approval; no reviewed inventory evidence linked."
        )
        unavailable["inventory_risk_provenance"] = unavailable["inventory_risk_evidence"]
    else:
        risk = {
            name: row[name]
            for name in (
                "inventory_basis",
                "snapshot_assumption",
                "origin_snapshot_status",
                "origin_exposure_state",
                "forecast_exposure_state",
                "inventory_buffer",
                "predicted_margin",
                "forecast_input_status",
                "forecast_input_reason",
                "methodology_status",
            )
        }
        provenance = json.dumps(inventory_provenance, sort_keys=True)

    forecast_provenance = {
        "export_sha256": row["source_export_sha256"],
        "export_schema": "issue-132-forecast-export-v1",
        "source": synthetic_export()["source"],
        "SKU_ID": forecast["SKU_ID"],
        "Warehouse_ID": forecast["Warehouse_ID"],
        "forecast_origin": forecast["forecast_origin"],
        "horizon": horizon,
        "model": forecast["model"],
        "configuration_id": forecast["configuration_id"],
        "producer_status": forecast["producer_status"],
        "forecast_status": forecast["forecast_status"],
    }
    record = DecisionSupportRecord(
        sku_id=forecast["SKU_ID"],
        warehouse_id=forecast["Warehouse_ID"],
        forecast_origin=forecast["forecast_origin"],
        forecast_horizon=f"{horizon}-day",
        forecast_demand=forecast["prediction"],
        forecast_provenance=json.dumps(forecast_provenance, sort_keys=True),
        inventory_risk_evidence=risk,
        inventory_risk_provenance=provenance,
        assumptions=[
            f"Target interval {forecast['target_start_date']} through {forecast['target_end_date']} is inclusive.",
            "One day means next-day demand; 7/14/28 days mean cumulative-window demand, not a daily path.",
            row["snapshot_assumption"],
        ],
        limitations=[runner.SCENARIO_LIMITATION],
        evidence=[f"Assessment ID: {assessment_id}"],
        management_consideration="Advisory information for human consideration.",
        human_review_status="not_assessed",
        human_review_reasons=["Human review has not yet been assessed."],
        unavailable_fields=unavailable,
        component_provenance=components,
    )
    return asdict(record)


def _write_synthetic_sources(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    mutate_records: Any = None,
) -> tuple[Any, dict[str, Any], dict[str, Any]]:
    """Write disposable synthetic sources that exercise the real validators."""
    repository = tmp_path.resolve()
    source_export_path = repository / retained_cases.DESTINATION
    source_export_path.parent.mkdir(parents=True)
    export_payload = _json_bytes(synthetic_export())
    source_export_path.write_bytes(export_payload)
    handoff = load_forecast_handoff(
        source_export_path, expected_sha256=hashlib.sha256(export_payload).hexdigest()
    )

    inventory_source = _inventory_source(handoff)
    inventory_records = [
        _prospective_row(forecast, inventory_source)
        for forecast in handoff.document["forecasts"]
    ]
    prospective = {
        "schema": runner.PROSPECTIVE_SCHEMA,
        "source": inventory_source,
        "scope": "Synthetic contract fixture only.",
        "records": inventory_records,
    }
    prospective_bytes = _json_bytes(prospective)
    evaluation_bytes = b"opaque synthetic retrospective companion; never decoded"
    report_bytes = b"Synthetic companion bytes."
    inventory_directory = repository / "research-materials/inventory-risk/issue-164/evaluation-v1"
    inventory_directory.mkdir(parents=True)
    prospective_path = inventory_directory / "prospective.json"
    prospective_path.write_bytes(prospective_bytes)
    (inventory_directory / "evaluation.json").write_bytes(evaluation_bytes)
    (inventory_directory / "report.md").write_bytes(report_bytes)
    inventory_manifest = {
        "schema": runner.RUN_SCHEMA,
        "files": {
            "prospective.json": hashlib.sha256(prospective_bytes).hexdigest(),
            "evaluation.json": hashlib.sha256(evaluation_bytes).hexdigest(),
            "report.md": hashlib.sha256(report_bytes).hexdigest(),
        },
        "dataset_provenance_sha256": runner.PROVENANCE_SHA256,
        "source": inventory_source,
        "operator": "Synthetic test fixture",
    }
    (inventory_directory / "manifest.json").write_bytes(_json_bytes(inventory_manifest))

    monkeypatch.setattr(assessment, "REPOSITORY", repository)
    monkeypatch.setattr(runner, "REPOSITORY", repository)
    inventory_evidence = assessment.load_inventory_evidence(prospective_path, handoff)

    records: list[dict[str, Any]] = []
    for index, (sku, warehouse) in enumerate(assessment.PAIRS, start=0):
        for offset, horizon in enumerate((1, 7, 14, 28)):
            case_index = index * 4 + offset + 1
            forecast = next(
                row
                for row in handoff.document["forecasts"]
                if row["SKU_ID"] == sku
                and row["Warehouse_ID"] == warehouse
                and row["horizon"] == horizon
            )
            key = sku, warehouse, forecast["forecast_origin"], horizon
            upstream = inventory_evidence["rows"][key]
            records.append(
                {
                    "assessment_id": f"F{case_index:02d}",
                    "horizon": horizon,
                    "record": _fixture_record(
                        forecast,
                        upstream,
                        inventory_evidence["provenance"],
                        f"F{case_index:02d}",
                    ),
                }
            )
    if mutate_records is not None:
        mutate_records(records)
    records_bundle = {
        "mapping_version": MAPPING_VERSION,
        "source": {
            "export_sha256": handoff.sha256,
            "export_schema": handoff.document["export_schema"],
            **handoff.document["source"],
            "inventory_evidence": inventory_evidence["provenance"],
        },
        "scope": "20 purposive synthetic decision-support records; h=28 inventory gated.",
        "records": records,
    }
    records_bytes = _json_bytes(records_bundle)
    records_directory = repository / retained_cases.DECISION_SUPPORT_DIRECTORY
    records_directory.mkdir(parents=True)
    (records_directory / "records.json").write_bytes(records_bytes)
    manifest = {
        "assessment_status": "synthetic; no checklist results",
        "code_sha256": {
            "src/decision_support/assessment.py": "a" * 64,
            "src/decision_support/records.py": "b" * 64,
            "src/inventory_risk/forecast_handoff.py": "c" * 64,
        },
        "initial_review_template_sha256": "d" * 64,
        "mapping_version": MAPPING_VERSION,
        "operator": "Synthetic test fixture",
        "prepared_at": "2026-10-24T00:00:00+00:00",
        "records_markdown_sha256": "e" * 64,
        "records_sha256": hashlib.sha256(records_bytes).hexdigest(),
        "review_schema": "issue-168-review-v2",
        "source_export_sha256": handoff.sha256,
    }
    manifest_bytes = _json_bytes(manifest)
    (records_directory / "manifest.json").write_bytes(manifest_bytes)
    monkeypatch.setattr(
        retained_cases,
        "DECISION_SUPPORT_MANIFEST_SHA256",
        hashlib.sha256(manifest_bytes).hexdigest(),
    )
    monkeypatch.setattr(
        retained_cases,
        "DECISION_SUPPORT_RECORDS_SHA256",
        hashlib.sha256(records_bytes).hexdigest(),
    )
    return handoff, inventory_evidence, records_bundle


def _synthetic_loader(root: Path) -> dict[str, Any]:
    def load_synthetic_export(path: Path) -> Any:
        return load_forecast_handoff(
            path, expected_sha256=hashlib.sha256(path.read_bytes()).hexdigest()
        )

    return retained_cases.load_retained_case_bundle(
        root, forecast_loader=load_synthetic_export
    )


def test_existing_validators_join_synthetic_twenty_case_roster_and_gate_h28(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_synthetic_sources(tmp_path, monkeypatch)
    app = create_app(
        repository=tmp_path,
        loader=lambda _: None,
        retained_case_loader=_synthetic_loader,
    )
    with TestClient(app) as client:
        response = client.get("/decision-support/cases")
        one = client.get("/decision-support/cases/F01")
        gated = client.get("/decision-support/cases/F04")

    assert response.status_code == 200
    body = response.json()
    assert len(body["records"]) == 20
    assert [case["assessment_id"] for case in body["records"]] == [
        f"F{index:02d}" for index in range(1, 21)
    ]
    assert body["records"][0]["record"]["human_review_status"] == "not_assessed"
    assert body["records"][0]["prospective_record"]["forecast_origin"] == "2024-12-02"
    assert body["records"][0]["prospective_record"]["run_id"] == "final-20261003-02"
    assert body["records"][0]["prospective_record"]["evaluation_stage"] == (
        "final_evaluation"
    )
    assert body["records"][0]["prospective_record"]["evidence_role"] == "primary"
    assert one.status_code == 200
    assert one.json()["assessment_id"] == "F01"
    assert one.json()["record"]["sku_id"] == "SKU_1"
    assert one.json()["prospective_record"]["target_start_date"] == "2024-12-03"
    for case in body["records"][1:3]:
        assert case["horizon"] in (7, 14)
        assert "cumulative-window demand, not a daily path" in case["record"][
            "assumptions"
        ][1]
    assert gated.status_code == 200
    gated_projection = gated.json()["prospective_record"]
    assert gated_projection["horizon"] == 28
    assert gated_projection["downstream_use_reason"] == (
        "28_day_downstream_use_requires_separate_approval"
    )
    assert not set(retained_cases._INVENTORY_PROSPECTIVE_FIELDS) & set(gated_projection)
    assert "28_day_downstream_use_requires_separate_approval" in gated.json()["record"][
        "unavailable_fields"
    ]["inventory_risk_evidence"]
    serialized = response.text + one.text + gated.text
    for forbidden in (
        "observed_target",
        "retrospective_margin",
        "confusion_cell",
        "evaluation.json",
        "review.json",
        "Stockout_Flag",
        "Demand_Forecast",
    ):
        assert forbidden not in serialized


def test_null_zero_false_unknown_and_reasons_are_preserved(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_synthetic_sources(tmp_path, monkeypatch)
    bundle = retained_cases.load_retained_case_bundle(
        tmp_path,
        forecast_loader=lambda path: load_forecast_handoff(
            path, expected_sha256=hashlib.sha256(path.read_bytes()).hexdigest()
        ),
    )
    projection = bundle["records"][0]["prospective_record"]
    assert projection["prediction"] == 0
    assert projection["Inventory_Level"] == 0
    assert projection["Reorder_Point"] == 0
    assert projection["inventory_buffer"] == 0
    assert projection["origin_snapshot_available"] is None
    assert projection["inventory_state_available"] is False
    assert projection["analysis_inventory_state_available"] is True
    assert projection["origin_snapshot_status"] == "unknown"
    assert projection["origin_snapshot_reason"] == (
        "origin_snapshot_availability_not_established"
    )
    assert bundle["records"][0]["record"]["human_review_status"] == "not_assessed"


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda records: records[0].update(horizon=7),
            "wrapper differs",
        ),
        (
            lambda records: records[0]["record"].update(sku_id="SKU_5"),
            "Nested forecast identity differs",
        ),
        (
            lambda records: records[0]["record"].update(forecast_origin="2024-12-03"),
            "Nested forecast identity differs",
        ),
        (
            lambda records: records[0]["record"].update(forecast_horizon="7-day"),
            "Nested forecast identity differs",
        ),
        (
            lambda records: records.pop(),
            "exactly 20 cases",
        ),
    ],
)
def test_wrapper_nested_identity_origin_and_horizon_mismatches_fail(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutate: Any,
    message: str,
) -> None:
    handoff, inventory, _ = _write_synthetic_sources(
        tmp_path, monkeypatch, mutate_records=mutate
    )
    with pytest.raises(retained_cases.RetainedCaseSourceError, match=message):
        retained_cases.load_decision_support_records(
            tmp_path / retained_cases.DECISION_SUPPORT_DIRECTORY,
            handoff=handoff,
            inventory_evidence=inventory,
        )


def test_changed_records_bytes_fail_the_pinned_and_manifest_hashes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    handoff, inventory, _ = _write_synthetic_sources(tmp_path, monkeypatch)
    records_path = tmp_path / retained_cases.DECISION_SUPPORT_DIRECTORY / "records.json"
    records_path.write_bytes(records_path.read_bytes() + b" ")
    with pytest.raises(retained_cases.RetainedCaseSourceError, match="records hash differs"):
        retained_cases.load_decision_support_records(
            records_path.parent, handoff=handoff, inventory_evidence=inventory
        )


def test_manifest_cannot_be_rebound_to_another_forecast_export(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    handoff, inventory, _ = _write_synthetic_sources(tmp_path, monkeypatch)
    manifest_path = tmp_path / retained_cases.DECISION_SUPPORT_DIRECTORY / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest["source_export_sha256"] = "0" * 64
    manifest_bytes = _json_bytes(manifest)
    manifest_path.write_bytes(manifest_bytes)
    monkeypatch.setattr(
        retained_cases,
        "DECISION_SUPPORT_MANIFEST_SHA256",
        hashlib.sha256(manifest_bytes).hexdigest(),
    )
    with pytest.raises(
        retained_cases.RetainedCaseSourceError,
        match="another forecast export",
    ):
        retained_cases.load_decision_support_records(
            manifest_path.parent, handoff=handoff, inventory_evidence=inventory
        )


def test_unknown_case_is_not_substituted_and_missing_sources_are_503(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_synthetic_sources(tmp_path, monkeypatch)
    app = create_app(
        repository=tmp_path,
        loader=lambda _: None,
        retained_case_loader=_synthetic_loader,
    )
    with TestClient(app) as client:
        unknown = client.get("/decision-support/cases/F99")
    assert unknown.status_code == 404
    assert unknown.json()["detail"]["reason_code"] == "unknown_case"

    empty_repository_app = create_app(repository=tmp_path / "empty")
    with TestClient(empty_repository_app) as client:
        absent = client.get("/decision-support/cases")
    assert absent.status_code == 503
    assert absent.json()["detail"]["reason_code"] == "source_unverified"

    unavailable_app = create_app(
        retained_case_loader=lambda _: (_ for _ in ()).throw(
            retained_cases.RetainedCaseSourceError("synthetic source missing")
        )
    )
    with TestClient(unavailable_app) as client:
        unavailable = client.get("/decision-support/cases")
    assert unavailable.status_code == 503
    assert unavailable.json()["detail"]["reason_code"] == "source_unverified"


def test_openapi_exposes_separate_read_only_retained_routes() -> None:
    paths = create_app().openapi()["paths"]
    assert set(paths["/decision-support/cases"]) == {"get"}
    assert set(paths["/decision-support/cases/{assessment_id}"]) == {"get"}
    assert set(paths["/forecasts"]) == {"post"}
