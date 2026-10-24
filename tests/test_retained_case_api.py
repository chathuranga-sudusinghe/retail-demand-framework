"""Issue #183 — read-only retained research-case slice.

Synthetic export and inventory evidence only; no project data, model or
experiment is used. The sealed-file loaders keep their own existing tests.
"""

from __future__ import annotations

from datetime import date, timedelta
import hashlib
import json

from fastapi.testclient import TestClient
import pytest

from src.api.main import create_app
from src.decision_support.assessment import PAIRS
from src.decision_support.retained_cases import (
    CASE_SCHEMA,
    CaseSourceUnavailable,
    build_catalog,
)
from src.forecasting.export import (
    EXPORT_SCHEMA,
    ORIGIN,
    PRODUCERS,
    RUN_ID,
    SOURCE_SCHEMA,
    TRAINING_START,
)
from src.forecasting.inference import InferenceError
from src.inventory_risk.forecast_handoff import (
    MANIFEST_SHA256,
    RECEIPT_SHA256,
    ForecastHandoff,
)

HASH = "a" * 64
INVENTORY_FIELDS = (
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
RETROSPECTIVE_NAMES = (
    "observed_target",
    "retrospective_margin",
    "retrospective_exposure_state",
    "wape",
    "mae",
    "rmse",
    "bias",
)
# One roster pair without an origin snapshot, to exercise "unavailable".
MISSING_SNAPSHOT_PAIR = ("SKU_10", "WH_3")


def _export() -> ForecastHandoff:
    """A synthetic 250-series x 4-horizon export that passes the real validator."""
    mapping = {h: (model, config) for h, model, config in PRODUCERS}
    forecasts = []
    for sku_number in range(1, 51):
        for wh_number in range(1, 6):
            for horizon in (1, 7, 14, 28):
                forecasts.append(
                    {
                        "SKU_ID": f"SKU_{sku_number}",
                        "Warehouse_ID": f"WH_{wh_number}",
                        "forecast_origin": ORIGIN,
                        "horizon": horizon,
                        "target_start_date": (
                            date.fromisoformat(ORIGIN) + timedelta(days=1)
                        ).isoformat(),
                        "target_end_date": (
                            date.fromisoformat(ORIGIN) + timedelta(days=horizon)
                        ).isoformat(),
                        "prediction": float(2 * horizon + sku_number / 100),
                        "model": mapping[horizon][0],
                        "configuration_id": mapping[horizon][1],
                        "forecast_type": "next_day"
                        if horizon == 1
                        else "cumulative_window",
                        "unit": "units",
                        "producer_status": "designated_producer",
                        "forecast_status": "available",
                        "uncertainty": {
                            "status": "unavailable",
                            "reason": "no_agreed_method",
                        },
                    }
                )
    document = {
        "export_schema": EXPORT_SCHEMA,
        "source": {
            "run_id": RUN_ID,
            "evaluation_stage": "final_evaluation",
            "source_schema": SOURCE_SCHEMA,
            "run_manifest_path": f"artifacts/forecasting/{RUN_ID}/run_manifest.json",
            "run_manifest_sha256": MANIFEST_SHA256,
            "prediction_receipt_sha256": RECEIPT_SHA256,
            "integrity_result": {
                "status": "passed",
                "evaluations": 28,
                "learned_refits": 20,
                "baseline_evaluations": 8,
                "predictions": 7000,
                "models_replayed": 20,
            },
        },
        "forecast_origin": ORIGIN,
        "training_start": TRAINING_START,
        "training_end": ORIGIN,
        "producers": [
            {
                "horizon": h,
                "model": model,
                "configuration_id": config,
                "forecast_type": "next_day" if h == 1 else "cumulative_window",
                "model_reference": {
                    f"{name}_{kind}": HASH if kind == "hash" else f"models/{name}"
                    for name in (
                        "model",
                        "descriptor",
                        "preprocessor",
                        "origin_features",
                    )
                    for kind in ("path", "hash")
                },
            }
            for h, model, config in PRODUCERS
        ],
        "series_count": 250,
        "record_count": 1000,
        "forecasts": forecasts,
    }
    payload = json.dumps(document, sort_keys=True).encode()
    return ForecastHandoff(payload, hashlib.sha256(payload).hexdigest())


def _inventory(handoff: ForecastHandoff) -> dict:
    """Synthetic prospective inventory rows for the roster keys only."""
    rows = {}
    for sku, warehouse in PAIRS:
        available = (sku, warehouse) != MISSING_SNAPSHOT_PAIR
        for horizon in (1, 7, 14, 28):
            rows[(sku, warehouse, ORIGIN, horizon)] = {
                **{name: f"synthetic-{name}" for name in INVENTORY_FIELDS},
                "analysis_inventory_state_available": available,
                "origin_snapshot_reason": None
                if available
                else "origin_inventory_record_missing",
                "downstream_use_reason": "28_day_downstream_use_requires_separate_approval",
                "method_assumptions": ["Synthetic no-receipt scenario assumption."],
                "method_limitations": ["Synthetic scenario proxy, not a stockout."],
            }
    return {
        "rows": rows,
        "provenance": {
            "prospective_sha256": "b" * 64,
            "manifest_sha256": "c" * 64,
            "dataset_provenance_sha256": "d" * 64,
            "operator": "synthetic-test",
            "source": {"forecast_export_sha256": handoff.sha256},
        },
    }


@pytest.fixture(scope="module")
def handoff() -> ForecastHandoff:
    return _export()


@pytest.fixture(scope="module")
def catalog(handoff):
    return build_catalog(handoff, _inventory(handoff))


def _unused_predictor(_repository):
    raise InferenceError("source_unverified", "predictor deliberately unavailable")


@pytest.fixture()
def client(catalog):
    app = create_app(loader=_unused_predictor, case_loader=lambda _repo: catalog)
    with TestClient(app) as test_client:
        yield test_client


def _walk_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _walk_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)


def test_list_presents_exactly_the_20_case_roster_in_order(client):
    body = client.get("/research-cases").json()
    assert body["evidence_mode"] == "fixed_origin_retained_research"
    assert body["case_count"] == 20
    assert [c["assessment_id"] for c in body["cases"]] == [
        f"F{n:02d}" for n in range(1, 21)
    ]
    assert [(c["SKU_ID"], c["Warehouse_ID"], c["horizon"]) for c in body["cases"]] == [
        (sku, wh, h) for sku, wh in PAIRS for h in (1, 7, 14, 28)
    ]
    assert {c["forecast_origin"] for c in body["cases"]} == {ORIGIN}


@pytest.mark.parametrize("assessment_id", ["F01", "F02", "F03"])
def test_h1_h7_h14_join_forecast_inventory_scenario_and_record(
    client, handoff, assessment_id
):
    case = client.get(f"/research-cases/{assessment_id}").json()
    assert case["case_schema"] == CASE_SCHEMA
    row = next(
        r
        for r in handoff.document["forecasts"]
        if (r["SKU_ID"], r["Warehouse_ID"], r["horizon"])
        == (case["SKU_ID"], case["Warehouse_ID"], case["horizon"])
    )
    # Retained forecast: unchanged quantity, interval and producer.
    assert case["forecast"]["prediction"] == row["prediction"]
    assert case["forecast"]["target_start_date"] == row["target_start_date"]
    assert case["forecast"]["target_end_date"] == row["target_end_date"]
    assert case["forecast"]["provenance"]["export_sha256"] == handoff.sha256
    # Linked inventory scenario.
    scenario = case["inventory_scenario"]
    assert scenario["status"] == "available" and scenario["reason"] is None
    assert set(scenario["evidence"]) == set(INVENTORY_FIELDS)
    assert scenario["provenance"]["prospective_sha256"] == "b" * 64
    # Decision-support record carries the same evidence and component sources.
    record = case["decision_support_record"]
    assert record["inventory_risk_evidence"] == scenario["evidence"]
    assert record["component_provenance"] == {
        "forecast": "forecasting",
        "decision_support": "responsible_decision_support",
        "inventory_risk": "inventory_risk",
    }


def test_h28_shows_forecast_but_keeps_inventory_gated(client):
    case = client.get("/research-cases/F04").json()
    assert case["horizon"] == 28
    assert isinstance(case["forecast"]["prediction"], float)
    scenario = case["inventory_scenario"]
    assert scenario["status"] == "gated"
    assert scenario["evidence"] is None and scenario["provenance"] is None
    assert "28_day_downstream_use_requires_separate_approval" in scenario["reason"]
    record = case["decision_support_record"]
    assert record["inventory_risk_evidence"] is None
    assert record["unavailable_fields"]["inventory_risk_evidence"] == scenario["reason"]
    assert any("28-day case" in item for item in record["limitations"])


def test_every_h28_case_is_gated(client):
    cases = client.get("/research-cases").json()["cases"]
    assert {c["inventory_status"] for c in cases if c["horizon"] == 28} == {"gated"}


def test_missing_origin_snapshot_stays_unavailable_with_reason(client):
    case = client.get(f"/research-cases/SKU_10/WH_3/{ORIGIN}/7").json()
    scenario = case["inventory_scenario"]
    assert scenario["status"] == "unavailable"
    assert scenario["reason"] == "origin_inventory_record_missing"
    assert scenario["evidence"] is None


@pytest.mark.parametrize(
    "path",
    [
        "/research-cases/F00",
        "/research-cases/F21",
        "/research-cases/f01",
        f"/research-cases/SKU_2/WH_1/{ORIGIN}/7",  # real export key, not in roster
        f"/research-cases/SKU_1/WH_2/{ORIGIN}/1",  # roster SKU, other warehouse
        "/research-cases/SKU_1/WH_1/2024-11-04/1",  # roster pair, other origin
        f"/research-cases/SKU_1/WH_1/{ORIGIN}/3",  # unapproved horizon
    ],
)
def test_outside_cases_return_explicit_404(client, path):
    response = client.get(path)
    assert response.status_code == 404
    assert response.json()["detail"]["reason_code"] == "case_not_in_retained_roster"


def test_unavailability_reasons_and_review_status_are_preserved(client):
    for summary in client.get("/research-cases").json()["cases"]:
        case = client.get(f"/research-cases/{summary['assessment_id']}").json()
        record = case["decision_support_record"]
        assert case["forecast"]["uncertainty"] == {
            "status": "unavailable",
            "reason": "no_agreed_method",
        }
        assert record["uncertainty_or_error"] is None
        assert record["unavailable_fields"]["uncertainty_or_error"].startswith(
            "no_agreed_method"
        )
        assert record["replenishment_recommendation"] is None
        assert record["unavailable_fields"]["replenishment_recommendation"]
        assert record["human_review_status"] == "not_assessed"
        assert record["human_review_reasons"]
        assert record["assumptions"] and record["limitations"]
        assert "Advisory" in record["management_consideration"]
        assert case["advisory_notice"]


def test_no_retrospective_fields_are_presented(client):
    for summary in client.get("/research-cases").json()["cases"]:
        case = client.get(f"/research-cases/{summary['assessment_id']}").json()
        keys = set(_walk_keys(case))
        assert not keys & set(RETROSPECTIVE_NAMES)


def test_routes_are_read_only_and_separate_from_request_time_inference(client):
    case = client.get("/research-cases/F01").json()
    assert case["evidence_mode"] == "fixed_origin_retained_research"
    assert "inference_mode" not in case
    for method in ("post", "put", "patch", "delete"):
        assert getattr(client, method)("/research-cases/F01").status_code == 405
    assert client.post("/research-cases").status_code == 405
    # The predictor is unavailable, yet research cases still serve, and
    # POST /forecasts keeps its own unchanged 503 behaviour.
    assert client.get("/health").json()["status"] == "unavailable"
    forecast = client.post("/forecasts", json={})
    assert forecast.status_code in (422, 503)


def test_responses_are_fresh_copies(client):
    first = client.get("/research-cases/F01").json()
    first["forecast"]["prediction"] = -1
    assert client.get("/research-cases/F01").json()["forecast"]["prediction"] != -1


def test_unverified_sources_return_503_without_affecting_forecast_routes():
    def failing(_repo):
        raise CaseSourceUnavailable("inventory_evidence_unconfigured", "not set")

    app = create_app(loader=_unused_predictor, case_loader=failing)
    with TestClient(app) as test_client:
        for path in ("/research-cases", "/research-cases/F01"):
            response = test_client.get(path)
            assert response.status_code == 503
            assert (
                response.json()["detail"]["reason_code"]
                == "inventory_evidence_unconfigured"
            )
        assert test_client.get("/health").status_code == 200


def test_catalog_requires_linked_inventory_evidence(handoff):
    with pytest.raises(ValueError, match="Linked inventory evidence is required"):
        build_catalog(handoff, None)


def test_catalog_rejects_inventory_evidence_on_a_gated_case(handoff, monkeypatch):
    import src.decision_support.retained_cases as module

    original = module.build_review_records

    def leaky(*args, **kwargs):
        bundle = original(*args, **kwargs)
        bundle["records"][3]["record"]["inventory_risk_evidence"] = {"x": 1}
        return bundle

    monkeypatch.setattr(module, "build_review_records", leaky)
    with pytest.raises(ValueError, match="gated 28-day case"):
        build_catalog(handoff, _inventory(handoff))
