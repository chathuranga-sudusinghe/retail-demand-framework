import pytest

from src.decision_support.records import DecisionSupportRecord


def test_default_human_review_status_is_not_assessed():
    record = DecisionSupportRecord(
        sku_id="SKU-001",
        warehouse_id="WH-01",
        forecast_origin="2026-10-01",
        forecast_horizon="7-day",
        unavailable_fields={
            "forecast_demand": "Forecast output not supplied for this test.",
            "forecast_provenance": "Forecast provenance not supplied for this test.",
            "inventory_risk_evidence": "Inventory-risk evidence not supplied for this test.",
            "inventory_risk_provenance": "Inventory-risk provenance not supplied for this test.",
            "replenishment_recommendation": "Replenishment recommendation not supplied for this test.",
            "uncertainty_or_error": "Uncertainty information not supplied for this test.",
        },
        forecast_demand=0.0,
        forecast_provenance="forecasting",
        inventory_risk_evidence=False,
        inventory_risk_provenance="inventory_risk",
        replenishment_recommendation=0,
        uncertainty_or_error=0.0,
        component_provenance={
            "forecast": "forecasting",
            "inventory_risk": "inventory_risk",
        },
    )

    assert record.human_review_status == "not_assessed"
    assert record.human_review_reasons == ["Human review has not yet been assessed."]


def test_review_required_must_have_reason():
    with pytest.raises(ValueError):
        DecisionSupportRecord(
            sku_id="SKU-001",
            warehouse_id="WH-01",
            forecast_origin="2026-10-01",
            forecast_horizon="7-day",
            human_review_status="review_required",
            human_review_reasons=[],
        )


def test_not_assessed_must_have_reason():
    with pytest.raises(ValueError):
        DecisionSupportRecord(
            sku_id="SKU-001",
            warehouse_id="WH-01",
            forecast_origin="2026-10-01",
            forecast_horizon="7-day",
            forecast_demand=0.0,
            forecast_provenance="forecasting",
            inventory_risk_evidence=False,
            inventory_risk_provenance="inventory_risk",
            replenishment_recommendation=0,
            uncertainty_or_error=0.0,
            component_provenance={
                "forecast": "forecasting",
                "inventory_risk": "inventory_risk",
            },
            human_review_status="not_assessed",
            human_review_reasons=[],
        )


@pytest.mark.parametrize("status", ["automatic_approval", "no_additional_review"])
def test_invalid_human_review_status_is_rejected(status):
    with pytest.raises(ValueError, match="Unsupported human_review_status"):
        DecisionSupportRecord(
            sku_id="SKU-001",
            warehouse_id="WH-01",
            forecast_origin="2026-10-01",
            forecast_horizon="7-day",
            human_review_status=status,
        )


def test_missing_upstream_evidence_requires_explicit_reason():
    with pytest.raises(ValueError):
        DecisionSupportRecord(
            sku_id="SKU-001",
            warehouse_id="WH-01",
            forecast_origin="2026-10-01",
            forecast_horizon="7-day",
            forecast_demand=None,
        )


def test_missing_component_provenance_is_rejected():
    with pytest.raises(ValueError):
        DecisionSupportRecord(
            sku_id="SKU-001",
            warehouse_id="WH-01",
            forecast_origin="2026-10-01",
            forecast_horizon="7-day",
            forecast_demand=25.0,
            forecast_provenance="forecasting",
            inventory_risk_evidence={"risk": "low"},
            inventory_risk_provenance="inventory_risk",
            replenishment_recommendation=10,
            uncertainty_or_error=1.5,
            component_provenance={},
        )


def test_identity_origin_and_horizon_are_preserved():
    record = DecisionSupportRecord(
        sku_id="SKU-001",
        warehouse_id="WH-01",
        forecast_origin="2026-10-01",
        forecast_horizon="7-day",
        forecast_demand=25.0,
        forecast_provenance="forecasting",
        component_provenance={"forecast": "forecasting"},
        unavailable_fields={
            "inventory_risk_evidence": "Not supplied for this preservation test.",
            "inventory_risk_provenance": "Not supplied for this preservation test.",
            "replenishment_recommendation": "Not supplied for this preservation test.",
            "uncertainty_or_error": "Not supplied for this preservation test.",
        },
    )

    assert record.sku_id == "SKU-001"
    assert record.warehouse_id == "WH-01"
    assert record.forecast_origin == "2026-10-01"
    assert record.forecast_horizon == "7-day"


def test_component_provenance_is_preserved():
    provenance = {
        "forecast": "forecasting",
        "inventory_risk": "inventory_risk",
    }

    record = DecisionSupportRecord(
        sku_id="SKU-001",
        warehouse_id="WH-01",
        forecast_origin="2026-10-01",
        forecast_horizon="7-day",
        forecast_demand=25.0,
        forecast_provenance="forecasting",
        inventory_risk_evidence=False,
        inventory_risk_provenance="inventory_risk",
        replenishment_recommendation=0,
        uncertainty_or_error=0.0,
        component_provenance=provenance,
    )

    assert record.component_provenance == provenance
    assert record.forecast_provenance == "forecasting"
    assert record.inventory_risk_provenance == "inventory_risk"


def test_assumptions_and_limitations_are_preserved():
    assumptions = ["Forecast assumes normal trading conditions."]
    limitations = ["Promotion effects are not modelled."]

    record = DecisionSupportRecord(
        sku_id="SKU-001",
        warehouse_id="WH-01",
        forecast_origin="2026-10-01",
        forecast_horizon="7-day",
        forecast_demand=25.0,
        forecast_provenance="forecasting",
        inventory_risk_evidence=False,
        inventory_risk_provenance="inventory_risk",
        replenishment_recommendation=0,
        uncertainty_or_error=0.0,
        assumptions=assumptions,
        limitations=limitations,
        component_provenance={
            "forecast": "forecasting",
            "inventory_risk": "inventory_risk",
        },
    )

    assert record.assumptions == assumptions
    assert record.limitations == limitations


def test_zero_and_false_values_are_not_treated_as_missing():
    record = DecisionSupportRecord(
        sku_id="SKU-001",
        warehouse_id="WH-01",
        forecast_origin="2026-10-01",
        forecast_horizon="7-day",
        forecast_demand=0.0,
        forecast_provenance="forecasting",
        inventory_risk_evidence=False,
        inventory_risk_provenance="inventory_risk",
        replenishment_recommendation=0,
        uncertainty_or_error=0.0,
        component_provenance={
            "forecast": "forecasting",
            "inventory_risk": "inventory_risk",
        },
    )

    assert record.forecast_demand == 0.0
    assert record.inventory_risk_evidence is False
    assert record.replenishment_recommendation == 0
    assert record.uncertainty_or_error == 0.0
