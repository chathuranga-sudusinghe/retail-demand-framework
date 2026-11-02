"""Synthetic contracts for retained inventory view data; no research runs."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from src.inventory_risk import runner
from src.inventory_risk.runner import PROSPECTIVE_SCHEMA, RUN_SCHEMA
from src.inventory_risk.forecast_handoff import ForecastHandoff
from src.visualization.inventory_views import (
    EVALUATION_FILE_NAMES,
    INVENTORY_EVIDENCE_DIRECTORY,
    InventoryViewEvidence,
    InventoryViewSourceError,
    build_availability_provenance,
    build_exposure_coverage,
    build_margin_comparison,
    build_proxy_crossing_comparison,
    load_inventory_view_evidence,
)
from test_decision_support_retained_cases import _inventory_source, _prospective_row
from test_inventory_risk_forecast_handoff import handoff, synthetic_export


def _json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode()


def _refresh_manifest_file_hash(directory: Path, name: str) -> None:
    manifest_path = directory / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest["files"][name] = hashlib.sha256(
        (directory / name).read_bytes()
    ).hexdigest()
    manifest_path.write_bytes(_json_bytes(manifest))


def _evaluation_case(
    forecast: dict[str, Any],
    prospective: dict[str, Any],
    observed_target: int,
    source: dict[str, Any],
) -> dict[str, Any]:
    buffer = prospective["inventory_buffer"]
    if prospective["origin_exposure_state"] == "scenario_already_at_or_below_threshold":
        comparison_case = "scenario_at_or_below_threshold"
        confusion_cell = None
        retrospective_state = "not_in_primary_comparison"
        retrospective_margin = None
    else:
        forecast_crossing = forecast["prediction"] >= buffer
        retrospective_crossing = observed_target >= buffer
        if forecast_crossing and retrospective_crossing:
            confusion_cell = "TP"
        elif not forecast_crossing and not retrospective_crossing:
            confusion_cell = "TN"
        elif not forecast_crossing and retrospective_crossing:
            confusion_cell = "FN"
        else:
            confusion_cell = "FP"
        comparison_case = "evaluable_paired_case"
        retrospective_state = (
            "realised_crossing" if retrospective_crossing else "no_realised_crossing"
        )
        retrospective_margin = buffer - observed_target

    return {
        "SKU_ID": forecast["SKU_ID"],
        "Warehouse_ID": forecast["Warehouse_ID"],
        "forecast_origin": forecast["forecast_origin"],
        "horizon": forecast["horizon"],
        "target_start_date": forecast["target_start_date"],
        "target_end_date": forecast["target_end_date"],
        "prediction": forecast["prediction"],
        "unit": forecast["unit"],
        "model": forecast["model"],
        "configuration_id": forecast["configuration_id"],
        "run_id": prospective["run_id"],
        "evaluation_stage": "final_evaluation",
        "evidence_role": "primary",
        "source_export_sha256": source["forecast_export_sha256"],
        "source_provenance": json.dumps(source["forecast_source"], sort_keys=True),
        "forecast_status": "available",
        "producer_status": "designated_producer",
        "prediction_status": "available",
        "eligibility_status": "eligible",
        "forecast_input_status": "available",
        "forecast_input_reason": "",
        "retrospective_input_status": "available",
        "retrospective_input_reason": "",
        "target_status": "complete",
        "target_unavailable_reason": "",
        "evaluation_unavailable_reasons": [],
        "origin_exposure_state": prospective["origin_exposure_state"],
        "forecast_exposure_state": prospective["forecast_exposure_state"],
        "retrospective_exposure_state": retrospective_state,
        "comparison_case": comparison_case,
        "confusion_cell": confusion_cell,
        "inventory_basis": prospective["inventory_basis"],
        "inventory_buffer": buffer,
        "predicted_margin": prospective["predicted_margin"],
        "retrospective_margin": retrospective_margin,
        "methodology_status": prospective["methodology_status"],
        "method_assumptions": prospective["method_assumptions"],
        "method_limitations": prospective["method_limitations"],
        "observed_target": observed_target,
    }


def _summary(horizon: int, cases: list[dict[str, Any]]) -> dict[str, Any]:
    group = [row for row in cases if row["horizon"] == horizon]
    cells = [row["confusion_cell"] for row in group]
    tp, tn, fp, fn = (cells.count(name) for name in ("TP", "TN", "FP", "FN"))
    n = tp + tn + fp + fn
    positive = tp + fn
    negative = fp + tn
    metric_values: dict[str, tuple[float | None, str]] = {
        "event_prevalence": (positive / n, "available"),
        "missed_crossing_rate": (fn / positive, "available"),
        "false_alert_rate": (fp / negative, "available"),
        "agreement": ((tp + tn) / n, "available"),
        "precision": (tp / (tp + fp), "available"),
        "recall": (tp / positive, "available"),
        "balanced_accuracy": (
            0.5 * (tp / positive + tn / negative),
            "available",
        ),
    }
    first = group[0]
    result: dict[str, Any] = {
        "inventory_basis": first["inventory_basis"],
        "run_id": first["run_id"],
        "evaluation_stage": first["evaluation_stage"],
        "evidence_role": first["evidence_role"],
        "model": first["model"],
        "configuration_id": first["configuration_id"],
        "horizon": horizon,
        "forecast_origin": first["forecast_origin"],
        "canonical_config_id": first["configuration_id"],
        "target_start_date": first["target_start_date"],
        "target_end_date": first["target_end_date"],
        "methodology_status": first["methodology_status"],
        "N": n,
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "origin_known_at_or_below_count": 0,
        "scenario_at_or_below_count": sum(
            row["comparison_case"] == "scenario_at_or_below_threshold" for row in group
        ),
        "initially_above_threshold_count": sum(
            row["origin_exposure_state"] == "scenario_initially_above_threshold"
            for row in group
        ),
        "evaluable_paired_case_count": n,
        "unavailable_case_count": sum(
            row["comparison_case"] == "unavailable" for row in group
        ),
        "forecast_unavailable_or_gated_count": 0,
        "retrospective_unavailable_or_gated_count": 0,
    }
    for name, (value, status) in metric_values.items():
        result[name] = value
        result[f"{name}_status"] = status
    return result


def _write_fixture(tmp_path: Path) -> tuple[Path, ForecastHandoff]:
    repository = tmp_path.resolve()
    export_document = synthetic_export()
    for forecast in export_document["forecasts"]:
        if (
            forecast["SKU_ID"] == "SKU_2"
            and forecast["Warehouse_ID"] == "WH_1"
            and forecast["horizon"] in {1, 7, 14}
        ):
            forecast["prediction"] = 12
    export = handoff(export_document)
    source = _inventory_source(export)
    export_rows = export.document["forecasts"]
    prospective_rows: list[dict[str, Any]] = []
    evaluation_cases: list[dict[str, Any]] = []
    for forecast in export_rows:
        prospective = _prospective_row(forecast, source)
        horizon = forecast["horizon"]
        sku, warehouse = forecast["SKU_ID"], forecast["Warehouse_ID"]
        if (sku, warehouse) == ("SKU_4", "WH_1"):
            prospective.update(
                {
                    "origin_snapshot_available": False,
                    "origin_snapshot_status": "unavailable",
                    "origin_snapshot_reason": "synthetic_source_unavailable",
                }
            )
        if horizon in {1, 7, 14} and (sku, warehouse) == ("SKU_1", "WH_1"):
            inventory, reorder = 0, 0
        elif horizon in {1, 7, 14} and (sku, warehouse) == ("SKU_2", "WH_1"):
            inventory, reorder = forecast["prediction"], 0
        else:
            inventory, reorder = 100, 0
        if horizon in {1, 7, 14}:
            prospective.update(
                {
                    "Inventory_Level": inventory,
                    "Reorder_Point": reorder,
                    "inventory_state_available": False,
                    "scenario_inventory_state_available": True,
                    "analysis_inventory_state_available": True,
                    "inventory_buffer": inventory - reorder,
                    "origin_exposure_state": (
                        "scenario_already_at_or_below_threshold"
                        if inventory - reorder <= 0
                        else "scenario_initially_above_threshold"
                    ),
                    "forecast_exposure_state": (
                        "not_needed_scenario_origin_state"
                        if inventory - reorder <= 0
                        else (
                            "forecast_crossing"
                            if forecast["prediction"] >= inventory - reorder
                            else "no_forecast_crossing"
                        )
                    ),
                    "predicted_margin": (
                        None
                        if inventory - reorder <= 0
                        else inventory - reorder - forecast["prediction"]
                    ),
                }
            )
        prospective_rows.append(prospective)
        if horizon in {1, 7, 14}:
            observed = 1000 if (sku, warehouse) == ("SKU_3", "WH_1") else 1
            evaluation_cases.append(
                _evaluation_case(forecast, prospective, observed, source)
            )

    summaries = [_summary(horizon, evaluation_cases) for horizon in (1, 7, 14)]
    prospective = {
        "schema": PROSPECTIVE_SCHEMA,
        "source": source,
        "scope": "Synthetic prospective fixture.",
        "records": prospective_rows,
    }
    evaluation = {
        "schema": RUN_SCHEMA,
        "source": source,
        "scope": "Synthetic retrospective fixture.",
        "cases": evaluation_cases,
        "summary": summaries,
    }
    directory = repository / INVENTORY_EVIDENCE_DIRECTORY
    directory.mkdir(parents=True)
    contents = {
        "prospective.json": _json_bytes(prospective),
        "evaluation.json": _json_bytes(evaluation),
        "report.md": b"Synthetic report companion.\n",
    }
    for name, payload in contents.items():
        (directory / name).write_bytes(payload)
    manifest = {
        "schema": RUN_SCHEMA,
        "files": {
            name: hashlib.sha256(payload).hexdigest()
            for name, payload in contents.items()
        },
        "dataset_provenance_sha256": runner.PROVENANCE_SHA256,
        "source": source,
        "operator": "Synthetic fixture only",
    }
    (directory / "manifest.json").write_bytes(_json_bytes(manifest))
    return repository, export


def _load(repository: Path, export: ForecastHandoff) -> InventoryViewEvidence:
    return load_inventory_view_evidence(
        repository,
        forecast_loader=lambda _path: export,
    )


def test_loader_validates_manifest_binding_and_separate_population(tmp_path):
    repository, export = _write_fixture(tmp_path)
    evidence = _load(repository, export)

    assert set(evidence.manifest["files"]) == EVALUATION_FILE_NAMES
    assert len(evidence.prospective["records"]) == 1000
    assert len(evidence.evaluation["cases"]) == 750
    assert {row["horizon"] for row in evidence.evaluation["summary"]} == {1, 7, 14}
    coverage = build_exposure_coverage(evidence)
    assert {
        row["horizon_forecast_population_count"]
        for row in coverage["horizon_population"]
    } == {250}
    assert len(coverage["horizon_population"]) == 4


@pytest.mark.parametrize(
    "failure", ["tampered_file", "source_hash_mismatch", "missing_file"]
)
def test_loader_rejects_missing_or_mismatched_retained_sources(tmp_path, failure):
    repository, export = _write_fixture(tmp_path)
    directory = repository / INVENTORY_EVIDENCE_DIRECTORY
    if failure == "tampered_file":
        (directory / "evaluation.json").write_bytes(b"{}")
    elif failure == "source_hash_mismatch":
        manifest_path = directory / "manifest.json"
        manifest = json.loads(manifest_path.read_bytes())
        manifest["source"]["forecast_export_sha256"] = "f" * 64
        manifest_path.write_bytes(_json_bytes(manifest))
    else:
        (directory / "report.md").unlink()

    with pytest.raises(InventoryViewSourceError):
        _load(repository, export)


def test_loader_rejects_identity_mismatch_with_valid_manifest_hash(tmp_path):
    repository, export = _write_fixture(tmp_path)
    directory = repository / INVENTORY_EVIDENCE_DIRECTORY
    prospective_path = directory / "prospective.json"
    prospective = json.loads(prospective_path.read_bytes())
    prospective["records"][0]["SKU_ID"] = "SKU_NOT_IN_FORECAST_EXPORT"
    prospective_path.write_bytes(_json_bytes(prospective))
    _refresh_manifest_file_hash(directory, "prospective.json")

    with pytest.raises(InventoryViewSourceError, match="identity is unknown"):
        _load(repository, export)


def test_views_preserve_identity_horizon_states_null_zero_false_and_gate(tmp_path):
    repository, export = _write_fixture(tmp_path)
    evidence = _load(repository, export)
    coverage = build_exposure_coverage(evidence)
    margins = build_margin_comparison(evidence)
    availability = build_availability_provenance(evidence)
    forecast = next(
        row
        for row in coverage["prospective_records"]
        if row["SKU_ID"] == "SKU_2"
        and row["Warehouse_ID"] == "WH_1"
        and row["horizon"] == 7
    )
    assert forecast["forecast_origin"] == "2024-12-02"
    assert forecast["target_start_date"] == "2024-12-03"
    assert forecast["target_end_date"] == "2024-12-09"
    assert forecast["horizon"] == 7

    prospective = margins["prospective"]["records"]
    at_or_below = next(
        row
        for row in prospective
        if row["SKU_ID"] == "SKU_1"
        and row["Warehouse_ID"] == "WH_1"
        and row["horizon"] == 1
    )
    zero_margin = next(
        row
        for row in prospective
        if row["SKU_ID"] == "SKU_2"
        and row["Warehouse_ID"] == "WH_1"
        and row["horizon"] == 1
    )
    assert at_or_below["inventory_buffer"] == 0
    assert at_or_below["predicted_margin"] is None
    assert zero_margin["predicted_margin"] == 0
    availability_row = next(
        row
        for row in availability["prospective"]["records"]
        if row["SKU_ID"] == "SKU_1"
        and row["Warehouse_ID"] == "WH_1"
        and row["horizon"] == 1
    )
    assert availability_row["origin_snapshot_available"] is None
    assert availability_row["inventory_state_available"] is False
    assert availability_row["origin_snapshot_status"] == "unknown"
    unavailable_row = next(
        row
        for row in availability["prospective"]["records"]
        if row["SKU_ID"] == "SKU_4"
        and row["Warehouse_ID"] == "WH_1"
        and row["horizon"] == 1
    )
    assert unavailable_row["origin_snapshot_available"] is False
    assert unavailable_row["origin_snapshot_status"] == "unavailable"
    assert unavailable_row["origin_snapshot_reason"] == "synthetic_source_unavailable"
    assert "human_review_status" not in unavailable_row

    assert availability_row["scenario_inventory_state_available"] is True
    assert availability_row["analysis_inventory_state_available"] is True
    assert (
        availability["dataset_provenance_sha256"]
        == evidence.manifest["dataset_provenance_sha256"]
    )

    gated = next(
        row
        for row in availability["prospective"]["records"]
        if row["SKU_ID"] == "SKU_1"
        and row["Warehouse_ID"] == "WH_1"
        and row["horizon"] == 28
    )
    assert gated["downstream_use_status"] == "not_approved_for_downstream_use"
    assert (
        gated["downstream_use_reason"]
        == "28_day_downstream_use_requires_separate_approval"
    )
    gated_exposure = next(
        row
        for row in coverage["prospective_records"]
        if row["SKU_ID"] == "SKU_1"
        and row["Warehouse_ID"] == "WH_1"
        and row["horizon"] == 28
    )
    assert set(gated_exposure) == {
        "SKU_ID",
        "Warehouse_ID",
        "forecast_origin",
        "horizon",
        "target_start_date",
        "target_end_date",
        "downstream_use_status",
        "downstream_use_reason",
    }
    assert not {
        "Inventory_Level",
        "Reorder_Point",
        "inventory_buffer",
        "origin_exposure_state",
        "forecast_exposure_state",
        "predicted_margin",
        "retrospective_margin",
        "observed_target",
        "confusion_cell",
    } & set(gated)


def test_retrospective_results_are_separate_and_not_in_prospective_views(tmp_path):
    repository, export = _write_fixture(tmp_path)
    evidence = _load(repository, export)
    coverage = build_exposure_coverage(evidence)
    comparison = build_proxy_crossing_comparison(evidence)
    margins = build_margin_comparison(evidence)
    availability = build_availability_provenance(evidence)

    assert "observed_target" not in coverage["prospective_records"][0]
    assert "retrospective_exposure_state" not in coverage["prospective_records"][0]
    assert "observed_target" not in comparison["cases"][0]
    assert "observed_target" not in margins["prospective"]["records"][0]
    assert "retrospective_margin" not in margins["prospective"]["records"][0]
    assert "observed_target" not in availability["prospective"]["records"][0]
    assert len(coverage["prospective_records"]) == 1000
    assert len(coverage["evaluation_only"]["cases"]) == 750
    assert len(margins["prospective"]["records"]) == 750
    assert len(margins["evaluation_only"]["records"]) == 750


def test_evaluation_projections_preserve_source_caveats(tmp_path):
    repository, export = _write_fixture(tmp_path)
    evidence = _load(repository, export)
    prospective_source = evidence.prospective["records"][0]
    source_case = evidence.evaluation["cases"][0]
    for source_row in (prospective_source, source_case):
        source_row["methodology_status"] = "proposed_for_group_approval"
        source_row["downstream_use_status"] = "proposed_method_not_group_approved"
        source_row["downstream_use_reason"] = (
            "DR-012_remains_proposed_for_group_approval"
        )

    proxy_case = build_proxy_crossing_comparison(evidence)["cases"][0]
    margin_case = build_margin_comparison(evidence)["evaluation_only"]["records"][0]
    availability = build_availability_provenance(evidence)
    availability_case = availability["evaluation_only"]["records"][0]
    availability_case_without_historical_status = availability["evaluation_only"][
        "records"
    ][1]
    availability_prospective = availability["prospective"]["records"][0]

    for projected in (proxy_case, margin_case, availability_case):
        assert projected["method_assumptions"] == source_case["method_assumptions"]
        assert projected["method_limitations"] == source_case["method_limitations"]

    for projected in (availability_case, availability_prospective):
        assert projected["methodology_status"] == "proposed_for_group_approval"
        assert projected["downstream_use_status"] == (
            "proposed_method_not_group_approved"
        )
        assert projected["downstream_use_reason"] == (
            "DR-012_remains_proposed_for_group_approval"
        )
    assert "downstream_use_status" not in availability_case_without_historical_status
    assert "downstream_use_reason" not in availability_case_without_historical_status
    assert availability["current_method_approval"]["status"] == (
        "Group-approved on 12 October 2026"
    )
    assert availability["current_method_approval"]["approved_scope"] == (
        "Fixed origin, fixed reorder point, and no receipts for horizons h1, h7, "
        "and h14 only."
    )


def test_proxy_label_and_existing_metric_status_and_denominators_are_preserved(
    tmp_path,
):
    repository, export = _write_fixture(tmp_path)
    comparison = build_proxy_crossing_comparison(_load(repository, export))
    assert comparison["label"] == (
        "Retrospective threshold-crossing proxy based on Units_Sold; not observed stockout."
    )
    summary = next(
        row for row in comparison["summaries"] if row["group"]["horizon"] == 1
    )
    assert summary["counts"]["N"] == 249
    assert summary["counts"]["scenario_at_or_below_count"] == 1
    assert summary["metrics"]["event_prevalence"]["denominator"] == 249
    assert summary["metrics"]["missed_crossing_rate"]["denominator"] == 1
    assert summary["metrics"]["false_alert_rate"]["denominator"] == 248
    assert summary["metrics"]["precision"]["denominator"] == 1
    assert summary["metrics"]["balanced_accuracy"]["denominator"] == (
        "positive=1; negative=248"
    )
    assert summary["metrics"]["agreement"]["status"] == "available"


def test_view_functions_do_not_mutate_source_documents(tmp_path):
    repository, export = _write_fixture(tmp_path)
    evidence = _load(repository, export)
    before = deepcopy((evidence.manifest, evidence.prospective, evidence.evaluation))

    build_exposure_coverage(evidence)
    build_proxy_crossing_comparison(evidence)
    build_margin_comparison(evidence)
    build_availability_provenance(evidence)

    assert (evidence.manifest, evidence.prospective, evidence.evaluation) == before
