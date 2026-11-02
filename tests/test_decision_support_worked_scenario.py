"""Synthetic multi-horizon scenario contracts; no retained datasets, models or inference runs."""

from __future__ import annotations

from contextlib import nullcontext
from copy import deepcopy
import hashlib
import json
from json import dumps
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

from fastapi.testclient import TestClient
import numpy as np
import pandas as pd
import pytest

from src.api.main import create_app
from src.data.validated_handoff import ValidatedProjection
from src.decision_support import worked_scenario as scenario
from src.decision_support.assessment import PAIRS
from src.decision_support.retained_cases import RetainedCaseSourceError, _projection
from src.forecasting.export import ORIGIN, RUN_ID, TRAINING_START
from src.inventory_risk.runner import PROVENANCE_SHA256
from src.inventory_risk.forecast_handoff import ForecastHandoff
from test_decision_support_retained_cases import (
    _fixture_record,
    _inventory_source,
    _prospective_row,
)
from test_forecasting_inference import service
from test_inventory_risk_forecast_handoff import handoff, synthetic_export


class Reply:
    def __init__(self, status: int, body: dict[str, Any]):
        self.status_code, self.body = status, body

    def json(self) -> dict[str, Any]:
        return deepcopy(self.body)


class FakeClient:
    def __init__(self, document: dict[str, Any]):
        self.document = document
        self.requests: list[dict[str, Any]] = []
        self.status = 200
        self.ready = True
        self.mutate: Any = lambda value: None

    def get(self, path: str) -> Reply:
        assert path == "/health"
        return Reply(
            200,
            {
                "status": "ready" if self.ready else "unavailable",
                "available_horizons": [1, 7, 14, 28],
            },
        )

    def post(self, path: str, *, json: dict[str, Any]) -> Reply:
        assert path == "/forecasts"
        self.requests.append(deepcopy(json))
        producer = next(
            p for p in self.document["producers"] if p["horizon"] == json["horizon"]
        )
        forecast = next(
            r
            for r in self.document["forecasts"]
            if r["horizon"] == json["horizon"]
            and r["SKU_ID"] == json["SKU_ID"]
            and r["Warehouse_ID"] == json["Warehouse_ID"]
        )
        source = self.document["source"]
        value = {
            "SKU_ID": json["SKU_ID"],
            "Warehouse_ID": json["Warehouse_ID"],
            "forecast_origin": ORIGIN,
            "horizon": json["horizon"],
            "target_start_date": "2024-12-03",
            "target_end_date": forecast["target_end_date"],
            "forecast_type": forecast["forecast_type"],
            "model": producer["model"],
            "configuration_id": producer["configuration_id"],
            "model_source_run_id": RUN_ID,
            "manifest_reference": source["run_manifest_path"],
            "manifest_sha256": source["run_manifest_sha256"],
            "inference_schema": "forecast-inference-v1",
            "inference_mode": "request_time",
            "input_kind": "supplied_history",
            "status": "available",
            "producer_designation": "frozen_designated_producer",
            "unavailable_reasons": [],
            "forecast_quantity": forecast["prediction"],
            "assumptions": [],
            "limitations": [],
            "provenance": {
                **{
                    k: producer["model_reference"][k]
                    for k in (
                        "model_path",
                        "model_hash",
                        "preprocessor_path",
                        "preprocessor_hash",
                    )
                },
                "input_sha256": hashlib.sha256(
                    dumps(json, sort_keys=True, separators=(",", ":")).encode()
                ).hexdigest(),
            },
        }
        self.mutate(value)
        return Reply(self.status, value)


@pytest.fixture
def setup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    document = synthetic_export()
    for p in document["producers"]:
        p["model_reference"].update(
            {
                "model_path": f"models/{p['model']}/{p['configuration_id']}",
                "preprocessor_path": f"models/{p['model']}/{p['configuration_id']}/state.json",
                "preprocessor_hash": "b" * 64,
            }
        )
    for row in document["forecasts"]:
        row["prediction"] = 27.375
    metadata = json.dumps({"validated_provenance_hash": PROVENANCE_SHA256}).encode()
    prefix = tmp_path / "artifacts" / "forecasting" / RUN_ID
    prefix.mkdir(parents=True)
    (prefix / "run_metadata.json").write_bytes(metadata)
    manifest = json.dumps(
        {
            "files": [
                {
                    "path": f"artifacts/forecasting/{RUN_ID}/run_metadata.json",
                    "owner": "artifacts",
                    "sha256": hashlib.sha256(metadata).hexdigest(),
                }
            ]
        }
    ).encode()
    (prefix / "run_manifest.json").write_bytes(manifest)
    document["source"]["run_manifest_sha256"] = hashlib.sha256(manifest).hexdigest()
    # Synthetic sources must have their own pinned parent, never production bytes.
    import src.inventory_risk.forecast_handoff as handoff_module

    monkeypatch.setattr(
        handoff_module, "MANIFEST_SHA256", document["source"]["run_manifest_sha256"]
    )
    export = handoff(document)
    source = _inventory_source(export)
    cases = []
    for i, (sku, warehouse) in enumerate(PAIRS):
        for j, horizon in enumerate(scenario.HORIZONS):
            forecast = next(
                r
                for r in document["forecasts"]
                if (r["SKU_ID"], r["Warehouse_ID"], r["horizon"])
                == (sku, warehouse, horizon)
            )
            prospective = _prospective_row(forecast, source)
            assessment_id = f"F{1 + j + 4 * i:02d}"
            record = _fixture_record(forecast, prospective, {}, assessment_id)
            cases.append(
                {
                    "assessment_id": assessment_id,
                    "horizon": horizon,
                    "prospective_record": _projection(prospective, horizon),
                    "record": record,
                }
            )
    frame = pd.DataFrame(
        [
            {"Date": day, "SKU_ID": sku, "Warehouse_ID": warehouse, "Units_Sold": 15}
            for sku, warehouse in PAIRS
            for day in pd.date_range(TRAINING_START, ORIGIN)
        ]
    )
    projection = ValidatedProjection(
        frame,
        {},
        PROVENANCE_SHA256,
        {
            "start_date": TRAINING_START,
            "end_date": ORIGIN,
            "columns": list(scenario.HISTORY_COLUMNS),
        },
    )
    client = FakeClient(document)
    reads = []

    def reader(**kwargs: Any) -> ValidatedProjection:
        reads.append(kwargs)
        return projection

    arguments = {
        "repository": tmp_path,
        "seed": "reviewed-demo-seed",
        "output": Path("research-materials/issue-214/example.json"),
        "case_loader": lambda root: {"records": cases},
        "forecast_loader": lambda path: export,
        "history_reader": reader,
        "client_factory": lambda root: nullcontext(client),
        "observation_loader": lambda root, export: (
            [
                {k: r[k] for k in ("SKU_ID", "Warehouse_ID", "horizon")}
                | {"observed_target": 30.0}
                for r in document["forecasts"]
            ],
            "c" * 64,
        ),
    }
    return {
        "arguments": arguments,
        "cases": cases,
        "projection": projection,
        "client": client,
        "reads": reads,
        "document": document,
        "export": export,
        "root": tmp_path,
    }


def test_success_preserves_records_and_binds_only_pre_origin_history(
    setup: dict[str, Any],
) -> None:
    before = deepcopy(setup["cases"])
    trace = scenario.run_scenario(**setup["arguments"])
    assert setup["cases"] == before
    request = setup["client"].requests[1]
    assert len(request["history"]) == 337
    assert request["history"][0]["Date"] == TRAINING_START
    assert request["history"][-1]["Date"] == ORIGIN
    assert all(
        set(row) == {"Date", "Units_Sold"} and type(row["Units_Sold"]) is int
        for row in request["history"]
    )
    assert request["horizon"] == 7 and request["input_kind"] == "supplied_history"
    assert setup["reads"][0]["columns"] == scenario.HISTORY_COLUMNS
    assert setup["reads"][0]["end"] == ORIGIN
    assert setup["reads"][0]["expected_provenance_sha256"] == PROVENANCE_SHA256
    record = trace["forecast_results"][1]["retained_case"]["record"]
    assert record["human_review_status"] == "not_assessed"
    assert record["inventory_risk_evidence"]["methodology_status"] == "group_approved"
    assert trace["current_method_approval"]["status"] == "group_approved"
    assert record["replenishment_recommendation"] is None
    assert "uncertainty_or_error" in record["unavailable_fields"]
    assert trace["selection"]["pool"] == ["F02", "F06", "F10", "F14", "F18"]
    encoded = json.dumps(trace)
    for prohibited in (
        '"history": [',
        '"observed_target"',
        '"Demand_Forecast"',
        '"Stockout_Flag"',
        '"Order_Quantity"',
    ):
        assert prohibited not in encoded
    saved = setup["root"] / setup["arguments"]["output"]
    assert json.loads(saved.read_bytes()) == trace
    original_bytes = saved.read_bytes()
    with pytest.raises(scenario.ScenarioError, match="overwrite"):
        scenario.run_scenario(**setup["arguments"])
    assert saved.read_bytes() == original_bytes


def test_selection_is_repeatable_order_independent_and_not_outcome_based(
    setup: dict[str, Any],
) -> None:
    first, ids = scenario.select_case(
        {"records": [c for c in setup["cases"] if c["horizon"] == 7]}, "seed"
    )
    changed = deepcopy([c for c in setup["cases"] if c["horizon"] == 7][::-1])
    for case in changed:
        case["prospective_record"]["prediction"] += 100
        case["prospective_record"]["forecast_exposure_state"] = "different_outcome"
    second, other_ids = scenario.select_case({"records": changed}, "seed")
    assert first["assessment_id"] == second["assessment_id"] and ids == other_ids
    # Golden selections for the project's supported Python 3.12.3 environment.
    assert (
        scenario.select_case(
            {"records": [c for c in setup["cases"] if c["horizon"] == 7]}, "a"
        )[0]["assessment_id"]
        == "F10"
    )
    assert (
        scenario.select_case(
            {"records": [c for c in setup["cases"] if c["horizon"] == 7]}, "b"
        )[0]["assessment_id"]
        == "F02"
    )
    changed[0]["horizon"] = 28
    changed[1]["prospective_record"]["analysis_inventory_state_available"] = False
    changed[2]["prospective_record"]["forecast_input_status"] = "unavailable"
    changed[3]["record"]["inventory_risk_evidence"] = None
    _, eligible = scenario.select_case({"records": changed}, "seed")
    assert (
        changed[0]["assessment_id"] not in eligible
        and changed[1]["assessment_id"] not in eligible
        and changed[2]["assessment_id"] not in eligible
        and changed[3]["assessment_id"] not in eligible
    )
    with pytest.raises(scenario.ScenarioError):
        scenario.select_case({"records": []}, "seed")
    with pytest.raises(scenario.ScenarioError):
        scenario.select_case(
            {"records": [c for c in setup["cases"] if c["horizon"] == 7]}, " "
        )


@pytest.mark.parametrize(
    "problem", ["gap", "duplicate", "future", "wrong_start", "fraction", "negative"]
)
def test_invalid_history_stops_before_api_and_creates_no_trace(
    setup: dict[str, Any], problem: str
) -> None:
    frame = setup["projection"].frame
    if problem == "gap":
        frame.drop(frame.index[frame.Date == pd.Timestamp("2024-05-01")], inplace=True)
    elif problem == "wrong_start":
        frame.drop(
            frame.index[frame.Date == pd.Timestamp(TRAINING_START)], inplace=True
        )
    elif problem in {"fraction", "negative"}:
        frame["Units_Sold"] = 1.5 if problem == "fraction" else -1
    else:
        frame.loc[len(frame)] = frame.iloc[-1].copy()
        if problem == "future":
            frame.loc[len(frame) - 1, "Date"] = pd.Timestamp("2024-12-03")
        # Ensure every possible selected pair contains the bad final row.
        for sku, warehouse in PAIRS:
            frame.loc[len(frame)] = {
                "Date": pd.Timestamp("2024-12-03")
                if problem == "future"
                else pd.Timestamp(ORIGIN),
                "SKU_ID": sku,
                "Warehouse_ID": warehouse,
                "Units_Sold": 99999,
            }
    with pytest.raises(scenario.ScenarioError):
        scenario.run_scenario(**setup["arguments"])
    assert not setup["client"].requests
    assert not (setup["root"] / setup["arguments"]["output"]).exists()


@pytest.mark.parametrize(
    "field,value",
    [
        ("SKU_ID", "wrong"),
        ("Warehouse_ID", "wrong"),
        ("forecast_origin", "2024-12-03"),
        ("horizon", True),
        ("target_start_date", ORIGIN),
        ("target_end_date", "2024-12-10"),
        ("forecast_type", "wrong"),
        ("model", "wrong"),
        ("configuration_id", "wrong"),
        ("model_source_run_id", "wrong"),
        ("manifest_reference", "wrong"),
        ("manifest_sha256", "f" * 64),
        ("inference_schema", "wrong"),
        ("inference_mode", "retained"),
        ("input_kind", "synthetic_demo"),
        ("status", "unavailable"),
        ("producer_designation", "wrong"),
        ("unavailable_reasons", ["missing"]),
        ("forecast_quantity", float(np.nextafter(27.375, np.inf))),
        ("forecast_quantity", float("nan")),
        ("forecast_quantity", float("inf")),
        ("forecast_quantity", True),
        ("forecast_quantity", "27.375"),
    ],
)
def test_each_response_mismatch_stops_without_fallback_or_trace(
    setup: dict[str, Any], field: str, value: Any
) -> None:
    setup["client"].mutate = (
        lambda response: response.update({field: value})
        if response["horizon"] == 7
        else None
    )
    with pytest.raises(scenario.ScenarioError) as error:
        scenario.run_scenario(**setup["arguments"])
    assert error.value.reason_code == "reconciliation_failed"
    assert "[reconciliation]" in str(error.value)
    assert not (setup["root"] / setup["arguments"]["output"]).exists()


@pytest.mark.parametrize(
    "field",
    [
        "model_path",
        "model_hash",
        "preprocessor_path",
        "preprocessor_hash",
        "input_sha256",
    ],
)
def test_each_provenance_mismatch_is_rejected(
    setup: dict[str, Any], field: str
) -> None:
    setup["client"].mutate = lambda response: response["provenance"].update(
        {field: "wrong"}
    )
    with pytest.raises(scenario.ScenarioError) as error:
        scenario.run_scenario(**setup["arguments"])
    assert error.value.reason_code == "reconciliation_failed"
    assert "[reconciliation]" in str(error.value)
    assert not (setup["root"] / setup["arguments"]["output"]).exists()


@pytest.mark.parametrize(
    "failure",
    [
        "health",
        "422",
        "503",
        "retained",
        "reader",
        "manifest",
        "metadata",
        "provenance",
    ],
)
def test_unavailable_sources_never_produce_a_success_trace(
    setup: dict[str, Any], failure: str
) -> None:
    if failure == "health":
        setup["client"].ready = False
    elif failure in {"422", "503"}:
        setup["client"].status = int(failure)
    elif failure == "retained":

        def missing(root: Path) -> Any:
            raise RetainedCaseSourceError("synthetic missing bundle")

        setup["arguments"]["case_loader"] = missing
    elif failure == "reader":

        def bad_reader(**kwargs: Any) -> Any:
            raise ValueError("synthetic invalid projection")

        setup["arguments"]["history_reader"] = bad_reader
    elif failure == "provenance":
        projection = setup["projection"]
        setup["arguments"]["history_reader"] = lambda **kwargs: ValidatedProjection(
            projection.frame, {}, "f" * 64, projection.scope
        )
    else:
        prefix = setup["root"] / "artifacts" / "forecasting" / RUN_ID
        (
            prefix
            / ("run_manifest.json" if failure == "manifest" else "run_metadata.json")
        ).write_text("{}")
    with pytest.raises(scenario.ScenarioError):
        scenario.run_scenario(**setup["arguments"])
    assert not (setup["root"] / setup["arguments"]["output"]).exists()


@pytest.mark.parametrize(
    "output",
    [
        "docs/scenario.json",
        "research-materials/issue-214/file.csv",
        "research-materials/issue-214/../../escape.json",
    ],
)
def test_output_is_confined_to_ignored_json_traces(
    setup: dict[str, Any], output: str
) -> None:
    setup["arguments"]["output"] = Path(output)
    with pytest.raises(scenario.ScenarioError):
        scenario.run_scenario(**setup["arguments"])
    assert not setup["client"].requests


def test_actual_api_path_uses_synthetic_model_spy_only(
    setup: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    import src.forecasting.inference as inference

    engine = service()
    monkeypatch.setattr(
        inference, "MANIFEST_SHA256", setup["document"]["source"]["run_manifest_sha256"]
    )
    setup["arguments"]["case_loader"] = lambda root: {
        "records": [
            c
            for c in setup["cases"]
            if c["prospective_record"]["SKU_ID"] == PAIRS[0][0]
            and c["prospective_record"]["Warehouse_ID"] == PAIRS[0][1]
        ]
    }
    setup["arguments"]["client_factory"] = lambda root: TestClient(
        create_app(repository=root, loader=lambda repository: engine)
    )
    trace = scenario.run_scenario(**setup["arguments"])
    assert trace["forecast_results"][1]["api_response"]["forecast_quantity"] == 27.375
    assert len(engine.producers[7].estimator.calls) == 1
    assert all(
        len(producer.estimator.calls) == 1 for producer in engine.producers.values()
    )


def test_cli_requires_seed_and_reports_stage_failures(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit) as error:
        scenario.main(["--output", "research-materials/issue-214/example.json"])
    assert error.value.code == 2

    def fail(**kwargs: Any) -> Any:
        raise scenario.ScenarioError("source_unverified", "synthetic missing source")

    monkeypatch.setattr(scenario, "run_scenario", fail)
    with pytest.raises(SystemExit) as error:
        scenario.main(
            [
                "--seed",
                "chosen",
                "--output",
                "research-materials/issue-214/example.json",
            ]
        )
    assert error.value.code == 1
    assert "source_unverified" in capsys.readouterr().err


def test_shuffled_history_and_unrelated_pair_do_not_change_the_request(
    setup: dict[str, Any],
) -> None:
    projection = setup["projection"]
    frame = projection.frame.sample(frac=1, random_state=3).reset_index(drop=True)
    frame.loc[len(frame)] = {
        "Date": pd.Timestamp("2024-12-03"),
        "SKU_ID": "OTHER",
        "Warehouse_ID": "OTHER",
        "Units_Sold": 99999,
    }
    setup["arguments"]["history_reader"] = lambda **kwargs: ValidatedProjection(
        frame, {}, PROVENANCE_SHA256, projection.scope
    )
    scenario.run_scenario(**setup["arguments"])
    history = setup["client"].requests[0]["history"]
    assert len(history) == 337 and all(row["Units_Sold"] == 15 for row in history)
    assert history[0]["Date"] == TRAINING_START and history[-1]["Date"] == ORIGIN


@pytest.mark.parametrize(
    "section,key,value",
    [
        ("record", "sku_id", "wrong"),
        ("record", "warehouse_id", "wrong"),
        ("record", "forecast_origin", "wrong"),
        ("record", "forecast_horizon", "14-day"),
        ("record", "forecast_demand", 99.0),
        ("prospective_record", "prediction", 99.0),
        ("prospective_record", "source_export_sha256", "f" * 64),
        ("prospective_record", "unit", "wrong"),
    ],
)
def test_mismatched_retained_case_cannot_be_attached(
    setup: dict[str, Any], section: str, key: str, value: Any
) -> None:
    for case in setup["cases"]:
        case[section][key] = value
    with pytest.raises(scenario.ScenarioError) as error:
        scenario.run_scenario(**setup["arguments"])
    expected = (
        "source_unverified"
        if key == "source_export_sha256"
        else "reconciliation_failed"
    )
    assert error.value.reason_code == expected
    assert "[reconciliation]" in str(error.value)
    assert not (setup["root"] / setup["arguments"]["output"]).exists()


def test_current_approval_is_separate_from_unchanged_historical_labels(
    setup: dict[str, Any],
) -> None:
    for case in setup["cases"]:
        if case["horizon"] == 28:
            continue
        case["record"]["inventory_risk_evidence"]["methodology_status"] = (
            "proposed_for_group_approval"
        )
        case["prospective_record"]["methodology_status"] = "proposed_for_group_approval"
    before = deepcopy(setup["cases"])
    trace = scenario.run_scenario(**setup["arguments"])
    assert trace["current_method_approval"]["decision_date"] == "2026-10-12"
    assert (
        trace["forecast_results"][1]["retained_case"]["record"][
            "inventory_risk_evidence"
        ]["methodology_status"]
        == "proposed_for_group_approval"
    )
    assert setup["cases"] == before


def test_producer_metadata_cannot_bind_a_different_validated_source(
    setup: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    import src.inventory_risk.forecast_handoff as handoff_module

    prefix = setup["root"] / "artifacts" / "forecasting" / RUN_ID
    metadata = json.dumps({"validated_provenance_hash": "f" * 64}).encode()
    (prefix / "run_metadata.json").write_bytes(metadata)
    manifest = json.loads((prefix / "run_manifest.json").read_bytes())
    manifest["files"][0]["sha256"] = hashlib.sha256(metadata).hexdigest()
    payload = json.dumps(manifest).encode()
    (prefix / "run_manifest.json").write_bytes(payload)
    document = deepcopy(setup["document"])
    document["source"]["run_manifest_sha256"] = hashlib.sha256(payload).hexdigest()
    monkeypatch.setattr(
        handoff_module, "MANIFEST_SHA256", document["source"]["run_manifest_sha256"]
    )
    export = handoff(document)
    setup["arguments"]["forecast_loader"] = lambda path: export
    with pytest.raises(scenario.ScenarioError, match="History provenance differs"):
        scenario.run_scenario(**setup["arguments"])
    assert not setup["reads"] and not setup["client"].requests


def test_output_symlink_is_refused_before_source_consumption(
    setup: dict[str, Any],
) -> None:
    base = setup["root"] / "research-materials"
    base.mkdir()
    (base / "issue-214").symlink_to(setup["root"], target_is_directory=True)
    with pytest.raises(scenario.ScenarioError):
        scenario.run_scenario(**setup["arguments"])
    assert not setup["reads"] and not setup["client"].requests


def test_failed_trace_write_removes_only_its_new_partial_file(
    setup: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    target = setup["root"] / setup["arguments"]["output"]
    real_open = Path.open

    class BrokenStream:
        def __init__(self, stream: Any):
            self.stream = stream

        def __enter__(self) -> BrokenStream:
            return self

        def __exit__(self, *args: Any) -> None:
            self.stream.close()

        def write(self, payload: bytes) -> None:
            self.stream.write(payload[:10])
            raise OSError("synthetic disk failure")

    def broken_open(path: Path, *args: Any, **kwargs: Any) -> Any:
        stream = real_open(path, *args, **kwargs)
        return BrokenStream(stream) if path == target and args == ("xb",) else stream

    monkeypatch.setattr(Path, "open", broken_open)
    with pytest.raises(scenario.ScenarioError, match="Could not create"):
        scenario.run_scenario(**setup["arguments"])
    assert not target.exists()


def test_loader_failure_reports_stage_and_cause_in_cli_stderr(
    setup: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def missing(root: Path) -> Any:
        raise RetainedCaseSourceError("synthetic missing bundle")

    arguments = {**setup["arguments"], "case_loader": missing}
    with pytest.raises(scenario.ScenarioError) as error:
        scenario.run_scenario(**arguments)
    assert error.value.reason_code == "source_unverified"
    assert "[retained_source] RetainedCaseSourceError: synthetic missing bundle" in str(
        error.value
    )
    assert isinstance(error.value.__cause__, RetainedCaseSourceError)
    real_run = scenario.run_scenario

    def invoke(**kwargs: Any) -> Any:
        return real_run(**{**arguments, **kwargs})

    monkeypatch.setattr(scenario, "run_scenario", invoke)
    with pytest.raises(SystemExit) as exit_error:
        scenario.main(["--seed", "chosen", "--output", str(arguments["output"])])
    assert exit_error.value.code == 1
    assert (
        "source_unverified: [retained_source] RetainedCaseSourceError: synthetic missing bundle"
        in capsys.readouterr().err
    )
    assert not setup["client"].requests
    assert not (setup["root"] / arguments["output"]).exists()


@pytest.mark.parametrize(
    "field,value",
    [
        ("target_end_date", "2024-12-10"),
        ("model", "wrong"),
        ("configuration_id", "wrong"),
        ("SKU_ID", "wrong"),
    ],
)
def test_prospective_identity_mismatch_has_the_expected_reason(
    setup: dict[str, Any],
    field: str,
    value: Any,
) -> None:
    case, _ = scenario.select_case({"records": setup["cases"]}, "chosen")
    request = scenario.build_request(case, setup["projection"])
    response = setup["client"].post("/forecasts", json=request).json()
    case["prospective_record"][field] = value
    with pytest.raises(scenario.ScenarioError) as error:
        scenario.reconcile(response, request, case, setup["export"])
    assert error.value.reason_code == "reconciliation_failed"
    assert f"Retained field differs: {field}" in str(error.value)


@pytest.mark.parametrize(
    "problem",
    [
        "forecast_type",
        "unit",
        "missing_forecast",
        "duplicate_forecast",
        "missing_producer",
        "duplicate_producer",
    ],
)
def test_export_meaning_and_uniqueness_guards(
    setup: dict[str, Any],
    problem: str,
) -> None:
    case, _ = scenario.select_case({"records": setup["cases"]}, "chosen")
    request = scenario.build_request(case, setup["projection"])
    response = setup["client"].post("/forecasts", json=request).json()
    document = deepcopy(setup["document"])
    forecast = next(
        row
        for row in document["forecasts"]
        if all(
            row[key] == request[key] for key in ("SKU_ID", "Warehouse_ID", "horizon")
        )
    )
    producer = next(row for row in document["producers"] if row["horizon"] == 7)
    if problem in {"forecast_type", "unit"}:
        forecast[problem] = "wrong"
    elif problem == "missing_forecast":
        document["forecasts"].remove(forecast)
    elif problem == "duplicate_forecast":
        document["forecasts"].append(deepcopy(forecast))
    elif problem == "missing_producer":
        document["producers"].remove(producer)
    else:
        document["producers"].append(deepcopy(producer))
    # Exercise this helper's defensive guards directly. The default export loader
    # would reject these malformed sources before returning a ForecastHandoff.
    export = cast(
        ForecastHandoff,
        SimpleNamespace(document=document, sha256=setup["export"].sha256),
    )
    with pytest.raises(scenario.ScenarioError) as error:
        scenario.reconcile(response, request, case, export)
    expected = (
        "reconciliation_failed"
        if problem in {"forecast_type", "unit"}
        else "source_unverified"
    )
    assert error.value.reason_code == expected


def test_exclusive_create_race_preserves_the_other_writers_file(
    setup: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = setup["root"] / setup["arguments"]["output"]
    real_open = Path.open
    sentinel = b"another writer's existing trace"

    def racing_open(path: Path, *args: Any, **kwargs: Any) -> Any:
        if path == target and args == ("xb",):
            with real_open(path, "wb") as stream:
                stream.write(sentinel)
            raise FileExistsError("synthetic exclusive-create race")
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", racing_open)
    with pytest.raises(scenario.ScenarioError) as error:
        scenario.run_scenario(**setup["arguments"])
    assert error.value.reason_code == "output_write_failed"
    assert "[trace_write]" in str(error.value)
    assert "synthetic exclusive-create race" in str(error.value)
    assert target.read_bytes() == sentinel


def test_all_horizons_share_history_and_keep_comparison_separate(
    setup: dict[str, Any],
) -> None:
    original_loader = setup["arguments"]["observation_loader"]

    def outcomes(root: Path, export: ForecastHandoff) -> Any:
        assert [r["horizon"] for r in setup["client"].requests] == [1, 7, 14, 28]
        return original_loader(root, export)

    setup["arguments"]["observation_loader"] = outcomes
    trace = scenario.run_scenario(**setup["arguments"])
    requests = setup["client"].requests
    assert all(r["history"] == requests[0]["history"] for r in requests)
    assert all(
        set(r)
        == {
            "SKU_ID",
            "Warehouse_ID",
            "forecast_origin",
            "horizon",
            "input_kind",
            "history",
        }
        for r in requests
    )
    assert len(set(trace["history"]["input_sha256_by_horizon"].values())) == 4
    results = trace["forecast_results"]
    assert [r["horizon"] for r in results] == [1, 7, 14, 28]
    assert [r["api_response"]["target_end_date"] for r in results] == [
        "2024-12-03",
        "2024-12-09",
        "2024-12-16",
        "2024-12-30",
    ]
    assert results[0]["api_response"]["forecast_type"] == "next_day"
    assert all(
        r["api_response"]["forecast_type"] == "cumulative_window" for r in results[1:]
    )
    assert results[3]["retained_case"]["record"]["inventory_risk_evidence"] is None
    assert (
        results[3]["retained_case"]["prospective_record"]["downstream_use_reason"]
        == "28_day_downstream_use_requires_separate_approval"
    )
    assert (
        "analysis_inventory_state_available"
        not in results[3]["retained_case"]["prospective_record"]
    )
    assert (
        "forecast_exposure_state"
        not in results[3]["retained_case"]["prospective_record"]
    )
    rows = trace["retrospective_comparison"]["rows"]
    assert all(
        r["actual_units_sold"] == 30
        and r["absolute_error"] == 2.625
        and r["signed_error_prediction_minus_actual"] == -2.625
        and r["absolute_percentage_error"] == 8.75
        for r in rows
    )
    assert all("actual_units_sold" not in json.dumps(r) for r in results)


@pytest.mark.parametrize("horizon", scenario.HORIZONS)
def test_mismatch_at_any_horizon_prevents_outcome_access(
    setup: dict[str, Any], horizon: int
) -> None:
    setup["client"].mutate = (
        lambda response: response.update({"forecast_quantity": -99})
        if response["horizon"] == horizon
        else None
    )

    def forbidden(*args: Any) -> Any:
        pytest.fail("Actuals must not be accessed after a failed replay")

    setup["arguments"]["observation_loader"] = forbidden
    with pytest.raises(scenario.ScenarioError) as error:
        scenario.run_scenario(**setup["arguments"])
    assert error.value.reason_code == "reconciliation_failed"
    assert not (setup["root"] / setup["arguments"]["output"]).exists()


@pytest.mark.parametrize(
    "problem", ["missing", "duplicate", "wrong_pair", "h28_inventory"]
)
def test_incomplete_or_unapproved_horizon_set_fails(
    setup: dict[str, Any], problem: str
) -> None:
    for case in list(setup["cases"]):
        if case["horizon"] != 28:
            continue
        if problem == "missing":
            setup["cases"].remove(case)
        elif problem == "duplicate":
            setup["cases"].append(deepcopy(case))
        elif problem == "wrong_pair":
            case["prospective_record"]["SKU_ID"] = "wrong"
        else:
            case["record"]["inventory_risk_evidence"] = {"invented": True}
    with pytest.raises(scenario.ScenarioError) as error:
        scenario.run_scenario(**setup["arguments"])
    assert "[case_alignment]" in str(error.value)
    assert not setup["client"].requests


@pytest.mark.parametrize(
    "problem",
    ["missing", "duplicate", "negative", "bool", "fraction", "wrong_horizon", "zero"],
)
def test_retrospective_target_validation_and_zero_denominator(
    setup: dict[str, Any], problem: str
) -> None:
    case, _ = scenario.select_case({"records": setup["cases"]}, "a")
    request = scenario.build_request(case, setup["projection"])
    response = setup["client"].post("/forecasts", json=request).json()
    row = {k: request[k] for k in ("SKU_ID", "Warehouse_ID", "horizon")} | {
        "observed_target": 0
    }
    rows = [row]
    if problem == "missing":
        rows = []
    elif problem == "duplicate":
        rows.append(deepcopy(row))
    elif problem == "wrong_horizon":
        row["horizon"] = True
    elif problem != "zero":
        row["observed_target"] = {"negative": -1, "bool": True, "fraction": 3.5}[
            problem
        ]
    if problem == "zero":
        result = scenario.retrospective_comparison([response], rows)[0]
        assert result["absolute_percentage_error"] is None
        assert result["percentage_error_unavailable_reason"] == "actual_sales_zero"
        assert result["absolute_error"] == 27.375
    else:
        with pytest.raises(scenario.ScenarioError):
            scenario.retrospective_comparison([response], rows)


def test_observations_read_only_hash_bound_bytes(setup: dict[str, Any]) -> None:
    prefix = setup["root"] / "artifacts" / "forecasting" / RUN_ID
    rows = [
        {"horizon": 7, "SKU_ID": "SKU_1", "Warehouse_ID": "WH_1", "observed_target": 30}
    ]
    raw = json.dumps(rows).encode()
    (prefix / "observations.json").write_bytes(raw)
    manifest = json.loads((prefix / "run_manifest.json").read_bytes())
    manifest["files"].append(
        {
            "path": f"artifacts/forecasting/{RUN_ID}/observations.json",
            "owner": "artifacts",
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
    )
    payload = json.dumps(manifest).encode()
    (prefix / "run_manifest.json").write_bytes(payload)
    document = deepcopy(setup["document"])
    document["source"]["run_manifest_sha256"] = hashlib.sha256(payload).hexdigest()
    export = cast(ForecastHandoff, SimpleNamespace(document=document))
    assert scenario.load_observations(setup["root"], export) == (
        rows,
        hashlib.sha256(raw).hexdigest(),
    )
    # The production reader checks exact bytes; changing the target cannot silently pass.
    (prefix / "observations.json").write_text("[]")
    with pytest.raises(ValueError):
        scenario.load_observations(setup["root"], export)


def test_neutral_seed_selects_the_recorded_anchor(setup: dict[str, Any]) -> None:
    anchor, ids = scenario.select_case({"records": setup["cases"]}, "demo-01")
    assert ids == ["F02", "F06", "F10", "F14", "F18"]
    assert anchor["assessment_id"] == "F10"
    assert (
        anchor["prospective_record"]["SKU_ID"],
        anchor["prospective_record"]["Warehouse_ID"],
    ) == ("SKU_10", "WH_3")


@pytest.mark.parametrize(
    "field,value",
    [
        ("downstream_use_status", "approved_method"),
        ("downstream_use_reason", ""),
    ],
)
def test_h28_cannot_claim_downstream_approval(
    setup: dict[str, Any], field: str, value: str
) -> None:
    for case in setup["cases"]:
        if case["horizon"] == 28:
            case["prospective_record"][field] = value
    with pytest.raises(scenario.ScenarioError) as error:
        scenario.run_scenario(**setup["arguments"])
    assert error.value.reason_code == "unapproved_inventory"
    assert "[case_alignment]" in str(error.value)
    assert not setup["client"].requests
    assert not (setup["root"] / setup["arguments"]["output"]).exists()


@pytest.mark.parametrize("horizon", [1, 14])
def test_approved_horizon_still_requires_available_evidence(
    setup: dict[str, Any], horizon: int
) -> None:
    for case in setup["cases"]:
        if case["horizon"] == horizon:
            case["prospective_record"]["analysis_inventory_state_available"] = False
    with pytest.raises(scenario.ScenarioError) as error:
        scenario.run_scenario(**setup["arguments"])
    assert error.value.reason_code == "source_unverified"
    assert "[case_alignment]" in str(error.value)
    assert not setup["client"].requests
    assert not (setup["root"] / setup["arguments"]["output"]).exists()


@pytest.mark.parametrize(
    "value", [float("nan"), float("inf"), float("-inf"), "30", None]
)
def test_nonfinite_or_nonnumeric_actuals_fail_without_a_trace(
    setup: dict[str, Any], value: Any
) -> None:
    original = setup["arguments"]["observation_loader"]

    def invalid(root: Path, export: ForecastHandoff) -> Any:
        rows, digest = original(root, export)
        for row in rows:
            row["observed_target"] = value
        return rows, digest

    setup["arguments"]["observation_loader"] = invalid
    with pytest.raises(scenario.ScenarioError) as error:
        scenario.run_scenario(**setup["arguments"])
    assert error.value.reason_code == "source_unverified"
    assert "[retrospective_comparison]" in str(error.value)
    assert len(setup["client"].requests) == 4
    assert not (setup["root"] / setup["arguments"]["output"]).exists()


@pytest.mark.parametrize("dangling", [False, True])
def test_output_file_symlink_is_refused_before_reads(
    setup: dict[str, Any], dangling: bool
) -> None:
    target = setup["root"] / setup["arguments"]["output"]
    target.parent.mkdir(parents=True)
    victim = setup["root"] / "existing-evidence.json"
    if not dangling:
        victim.write_bytes(b"preserve existing evidence")
    target.symlink_to(victim)
    with pytest.raises(scenario.ScenarioError) as error:
        scenario.run_scenario(**setup["arguments"])
    assert error.value.reason_code == "invalid_output"
    assert not setup["reads"] and not setup["client"].requests
    assert target.is_symlink()
    assert (
        not victim.exists()
        if dangling
        else victim.read_bytes() == b"preserve existing evidence"
    )


def test_distinct_dates_pairs_and_horizons_remain_aligned(
    setup: dict[str, Any],
) -> None:
    # Values deliberately differ across all three dimensions so an accidental
    # permutation cannot pass merely because every fixture value is identical.
    offsets = {1: 1.5, 7: -3.5, 14: 7.5, 28: -10.5}
    document = setup["document"]
    observations = []
    for row in document["forecasts"]:
        sku_number = int(row["SKU_ID"].split("_")[1])
        warehouse_number = int(row["Warehouse_ID"].split("_")[1])
        actual = sku_number * 100 + warehouse_number * 10 + row["horizon"]
        row["prediction"] = actual + offsets[row["horizon"]]
        observations.append(
            {key: row[key] for key in ("SKU_ID", "Warehouse_ID", "horizon")}
            | {"observed_target": float(actual)}
        )
    export = handoff(document)
    source = _inventory_source(export)
    cases = []
    for i, (sku, warehouse) in enumerate(PAIRS):
        for j, horizon in enumerate(scenario.HORIZONS):
            forecast = next(
                row
                for row in document["forecasts"]
                if (row["SKU_ID"], row["Warehouse_ID"], row["horizon"])
                == (sku, warehouse, horizon)
            )
            full = _prospective_row(forecast, source)
            assessment_id = f"F{1 + 4 * i + j:02d}"
            cases.append(
                {
                    "assessment_id": assessment_id,
                    "horizon": horizon,
                    "prospective_record": _projection(full, horizon),
                    "record": _fixture_record(forecast, full, {}, assessment_id),
                }
            )
    dates = list(pd.date_range(TRAINING_START, ORIGIN))
    frame = (
        pd.DataFrame(
            [
                {
                    "Date": day,
                    "SKU_ID": sku,
                    "Warehouse_ID": warehouse,
                    "Units_Sold": 1000 * (pair_index + 1) + day_index,
                }
                for pair_index, (sku, warehouse) in enumerate(PAIRS)
                for day_index, day in enumerate(dates)
            ]
        )
        .sample(frac=1, random_state=11)
        .reset_index(drop=True)
    )
    projection = ValidatedProjection(
        frame, {}, PROVENANCE_SHA256, setup["projection"].scope
    )
    setup["arguments"].update(
        {
            "seed": "demo-01",
            "case_loader": lambda root: {"records": cases},
            "forecast_loader": lambda path: export,
            "history_reader": lambda **kwargs: projection,
            "observation_loader": lambda root, parent: (
                list(reversed(observations)),
                "d" * 64,
            ),
        }
    )
    trace = scenario.run_scenario(**setup["arguments"])
    assert trace["selection"]["assessment_id"] == "F10"
    expected_history = [
        {"Date": day.strftime("%Y-%m-%d"), "Units_Sold": 3000 + index}
        for index, day in enumerate(dates)
    ]
    for request in setup["client"].requests:
        assert request["SKU_ID"] == "SKU_10" and request["Warehouse_ID"] == "WH_3"
        assert request["history"] == expected_history
    rows = trace["retrospective_comparison"]["rows"]
    assert [row["horizon"] for row in rows] == [1, 7, 14, 28]
    for result, row, horizon in zip(
        trace["forecast_results"], rows, scenario.HORIZONS, strict=True
    ):
        actual = 1030 + horizon
        prediction = actual + offsets[horizon]
        assert result["api_response"]["forecast_quantity"] == prediction
        assert result["retained_case"]["record"]["forecast_demand"] == prediction
        assert row["forecast_quantity"] == prediction
        assert row["actual_units_sold"] == actual
        assert row["signed_error_prediction_minus_actual"] == offsets[horizon]
        assert row["absolute_error"] == abs(offsets[horizon])
        assert row["absolute_percentage_error"] == pytest.approx(
            abs(offsets[horizon]) / actual * 100
        )
