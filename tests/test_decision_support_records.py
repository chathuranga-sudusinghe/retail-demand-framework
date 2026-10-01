import pytest

from src.decision_support.records import DecisionSupportRecord

def test_default_human_review_status_is_not_assessed():
    record = DecisionSupportRecord(
        sku_id="SKU-001",
        warehouse_id="WH-01",
        forecast_origin="2026-10-01",
        forecast_horizon="7-day",
    )

    assert record.human_review_status == "not_assessed"

def test_review_required_must_have_reason():
        with pytest.raises(ValueError):
            DecisionSupportRecord(
            sku_id="SKU-001",
            warehouse_id="WH-01",
            forecast_origin="2026-10-01",
            forecast_horizon="7-day",
            human_review_status="review_required",
        )

def test_invalid_human_review_status_is_rejected():
    with pytest.raises(ValueError):
        DecisionSupportRecord(
            sku_id="SKU-001",
            warehouse_id="WH-01",
            forecast_origin="2026-10-01",
            forecast_horizon="7-day",
            human_review_status="automatic_approval",
        )