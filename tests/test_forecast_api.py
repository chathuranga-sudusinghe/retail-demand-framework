"""HTTP contract checks using supplied JSON and synthetic model spies."""

from __future__ import annotations

import json
from typing import Any

from fastapi.testclient import TestClient
import pytest

from src.api.main import create_app
from src.forecasting.inference import InferenceError
from test_forecasting_inference import example, service


@pytest.mark.parametrize("horizon", [1, 7, 14, 28])
def test_four_example_requests_compute_new_outputs(horizon: int) -> None:
    engine = service()
    with TestClient(create_app(loader=lambda root: engine)) as client:
        assert client.get("/health").json()["status"] == "ready"
        response = client.post("/forecasts", json=example(horizon))
    assert response.status_code == 200
    body = response.json()
    assert body["forecast_quantity"] == 27.375
    assert body["horizon"] == horizon
    assert body["status"] == "available"
    assert body["unavailable_reasons"] == []
    assert body["inference_mode"] == "request_time"
    assert len(engine.producers[horizon].estimator.calls) == 1


def test_api_passes_changed_history_to_model_on_every_request() -> None:
    engine = service()
    with TestClient(create_app(loader=lambda root: engine)) as client:
        payload = example()
        first = client.post("/forecasts", json=payload).json()
        payload["history"][-1]["Units_Sold"] += 50
        second = client.post("/forecasts", json=payload).json()
    assert second["forecast_quantity"] == first["forecast_quantity"] + 50
    assert len(engine.producers[1].estimator.calls) == 2


@pytest.mark.parametrize(
    "field,value",
    [
        ("horizon", "7"),
        ("horizon", True),
        ("horizon", 7.0),
        ("horizon", 3),
        ("forecast_origin", "2025-13-45"),
        ("forecast_origin", "abc"),
        ("SKU_ID", " SKU_1"),
        ("SKU_ID", "unknown"),
        ("Warehouse_ID", "unknown"),
        ("input_kind", "real_company_observation"),
        ("observed_target", 100),
        ("model", "catboost"),
        ("configuration_id", "GBM001"),
    ],
)
def test_invalid_requests_are_rejected_without_prediction(
    field: str, value: Any
) -> None:
    engine = service()
    payload = example()
    payload[field] = value
    with TestClient(create_app(loader=lambda root: engine)) as client:
        response = client.post("/forecasts", json=payload)
    assert response.status_code == 422
    assert all(not p.estimator.calls for p in engine.producers.values())


@pytest.mark.parametrize("value", [True, "100", 1.25, None, -1])
def test_non_integer_or_missing_demand_is_rejected(value: Any) -> None:
    engine = service()
    payload = example()
    payload["history"][0]["Units_Sold"] = value
    with TestClient(create_app(loader=lambda root: engine)) as client:
        response = client.post("/forecasts", json=payload)
    assert response.status_code == 422
    assert not engine.producers[1].estimator.calls


@pytest.mark.parametrize(
    "token,reported_input",
    [("NaN", "nan"), ("Infinity", "inf"), ("-Infinity", "-inf"), ("1e309", "inf")],
)
def test_nonfinite_request_input_returns_json_safe_validation_error(
    token: str, reported_input: str
) -> None:
    engine = service()
    payload = example()
    payload["history"][0]["Units_Sold"] = "__NONFINITE__"
    content = json.dumps(payload).replace('"__NONFINITE__"', token)
    with TestClient(
        create_app(loader=lambda root: engine), raise_server_exceptions=False
    ) as client:
        response = client.post(
            "/forecasts", content=content, headers={"Content-Type": "application/json"}
        )
    assert response.status_code == 422
    body = response.json()
    error = body["detail"][0]
    assert error["loc"] == ["body", "history", 0, "Units_Sold"]
    assert error["type"] == "int_type"
    assert error["msg"] == "Input should be a valid integer"
    assert error["input"] == reported_input
    json.dumps(body, allow_nan=False)
    assert "forecast_quantity" not in body
    assert all(not producer.estimator.calls for producer in engine.producers.values())


def test_unknown_identity_has_meaningful_reason() -> None:
    payload = example()
    payload["SKU_ID"] = "unknown"
    with TestClient(create_app(loader=lambda root: service())) as client:
        response = client.post("/forecasts", json=payload)
    assert response.json()["detail"]["reason_code"] == "unknown_sku"


def test_missing_artifacts_keep_docs_available_and_forecasts_unavailable() -> None:
    def unavailable(root: Any) -> Any:
        raise InferenceError("source_unverified", "missing models")

    with TestClient(create_app(loader=unavailable)) as client:
        health = client.get("/health").json()
        assert health == {
            "status": "unavailable",
            "available_horizons": [],
            "unavailable_reasons": ["source_unverified"],
        }
        assert client.get("/docs").status_code == 200
        response = client.post("/forecasts", json=example())
    assert response.status_code == 503
    assert response.json()["detail"]["reason_code"] == "source_unverified"


def test_model_failure_has_no_substitute_output() -> None:
    engine = service()
    engine.producers[1].estimator.value = float("nan")
    with TestClient(create_app(loader=lambda root: engine)) as client:
        response = client.post("/forecasts", json=example())
    assert response.status_code == 503
    assert response.json()["detail"]["reason_code"] == "unavailable_forecast"
    assert "forecast_quantity" not in response.json()


def test_openapi_documents_all_four_input_files_and_response_allowlist() -> None:
    schema = create_app(loader=lambda root: service()).openapi()
    content = schema["paths"]["/forecasts"]["post"]["requestBody"]["content"][
        "application/json"
    ]
    assert set(content["examples"]) == {"h1", "h7", "h14", "h28"}
    for h in (1, 7, 14, 28):
        assert content["examples"][f"h{h}"]["value"] == example(h)
    properties = schema["components"]["schemas"]["ForecastResponse"]["properties"]
    assert set(properties) == {
        "inference_schema",
        "inference_mode",
        "input_kind",
        "model_source_run_id",
        "manifest_reference",
        "manifest_sha256",
        "SKU_ID",
        "Warehouse_ID",
        "forecast_origin",
        "horizon",
        "target_start_date",
        "target_end_date",
        "forecast_type",
        "forecast_quantity",
        "model",
        "configuration_id",
        "producer_designation",
        "provenance",
        "status",
        "unavailable_reasons",
        "assumptions",
        "limitations",
    }
