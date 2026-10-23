"""Synthetic export-contract checks; no retained files or research runs."""

from copy import deepcopy
from datetime import date, timedelta
import hashlib
import json

import pandas as pd
import pytest

from src.forecasting.export import ORIGIN, PRODUCERS, RUN_ID
from src.inventory_risk.forecast_handoff import (
    ForecastHandoff,
    MANIFEST_SHA256,
    RECEIPT_SHA256,
    forecast_inventory_inputs,
    load_forecast_handoff,
)
from src.inventory_risk import forecast_handoff as handoff_module


def synthetic_export():
    rows = []
    producers = []
    for horizon, model, configuration in PRODUCERS:
        forecast_type = "next_day" if horizon == 1 else "cumulative_window"
        producers.append(
            {
                "horizon": horizon,
                "model": model,
                "configuration_id": configuration,
                "forecast_type": forecast_type,
                "model_reference": {
                    key: value
                    for name in (
                        "model",
                        "descriptor",
                        "preprocessor",
                        "origin_features",
                    )
                    for key, value in (
                        (name + "_path", "models/synthetic/" + name),
                        (name + "_hash", "a" * 64),
                    )
                },
            }
        )
        for sku in range(1, 51):
            for warehouse in range(1, 6):
                rows.append(
                    {
                        "SKU_ID": f"SKU_{sku}",
                        "Warehouse_ID": f"WH_{warehouse}",
                        "forecast_origin": ORIGIN,
                        "horizon": horizon,
                        "target_start_date": "2024-12-03",
                        "target_end_date": (
                            date.fromisoformat(ORIGIN) + timedelta(days=horizon)
                        ).isoformat(),
                        "prediction": 0 if sku == 1 else 12.5,
                        "model": model,
                        "configuration_id": configuration,
                        "forecast_type": forecast_type,
                        "unit": "units",
                        "producer_status": "designated_producer",
                        "forecast_status": "available",
                        "uncertainty": {
                            "status": "unavailable",
                            "reason": "no_agreed_method",
                        },
                    }
                )
    return {
        "export_schema": "issue-132-forecast-export-v1",
        "source": {
            "run_id": RUN_ID,
            "evaluation_stage": "final_evaluation",
            "source_schema": "issue-130-final-v1",
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
        "training_start": "2024-01-01",
        "training_end": ORIGIN,
        "producers": producers,
        "series_count": 250,
        "record_count": 1000,
        "forecasts": rows,
    }


def handoff(document=None):
    payload = json.dumps(
        document if document is not None else synthetic_export()
    ).encode()
    return ForecastHandoff(payload, hashlib.sha256(payload).hexdigest())


def test_source_mapping_preserves_zero_raw_values_provenance_and_missing_snapshot():
    source = handoff()
    original = source.document
    prepared = forecast_inventory_inputs(source)
    assert len(prepared) == 1000
    assert prepared.loc[0, "prediction"] == 0
    assert prepared.loc[5, "prediction"] == 12.5
    assert prepared.evidence_role.eq("primary").all()
    assert prepared.prediction_status.eq("available").all()
    assert prepared.eligibility_status.eq("eligible").all()
    assert prepared.forecast_input_status.eq("available").all()
    assert prepared.origin_snapshot_status.eq("unknown").all()
    assert not prepared.inventory_state_available.any()
    assert prepared.source_export_sha256.eq(source.sha256).all()
    assert json.loads(prepared.loc[0, "source_provenance"]) == original["source"]
    assert (
        prepared.loc[750:, "downstream_use_status"]
        .eq("not_approved_for_downstream_use")
        .all()
    )
    assert source.document == original
    modified = source.document
    modified["forecasts"][0]["prediction"] = 999
    assert source.document["forecasts"][0]["prediction"] == 0


@pytest.mark.parametrize(
    "value", [None, True, "2", float("nan"), float("inf"), 10**400]
)
def test_invalid_source_quantities_fail_without_partial_records(value):
    document = synthetic_export()
    document["forecasts"][0]["prediction"] = value
    with pytest.raises(ValueError):
        handoff(document)


@pytest.mark.parametrize(
    "changes",
    [
        {"horizon": True},
        {"horizon": 2},
        {"target_start_date": ORIGIN},
        {"target_end_date": "2024-12-04"},
        {"forecast_status": "unavailable"},
        {"model": "ridge"},
        {"unit": "daily units"},
        {"observed_target": 0},
    ],
)
def test_contract_errors_and_retrospective_leakage_are_rejected(changes):
    document = synthetic_export()
    document["forecasts"][0].update(changes)
    with pytest.raises(ValueError):
        handoff(document)


def test_missing_and_duplicate_population_cannot_pass_by_count_alone():
    document = synthetic_export()
    document["forecasts"][0] = deepcopy(document["forecasts"][1])
    with pytest.raises(ValueError, match="Duplicate forecast"):
        handoff(document)
    document = synthetic_export()
    document["forecasts"] = document["forecasts"][:-1]
    with pytest.raises(ValueError, match="population"):
        handoff(document)


def test_negative_forecasts_are_retained_without_clipping_or_eligibility():
    document = synthetic_export()
    document["forecasts"][0]["prediction"] = -4.5
    result = forecast_inventory_inputs(handoff(document))
    assert result.loc[0, "prediction"] == -4.5
    assert result.loc[0, "eligibility_status"] == "ineligible"
    assert result.loc[0, "forecast_input_status"] == "unavailable"
    assert (
        "negative_forecast_handling_not_approved"
        in result.loc[0, "preparation_unavailable_reasons"]
    )


def test_mixed_json_number_types_do_not_round_raw_integer_forecasts():
    document = synthetic_export()
    raw = 2**53 + 1
    document["forecasts"][0]["prediction"] = raw
    result = forecast_inventory_inputs(handoff(document))
    assert result.loc[0, "prediction"] == raw
    assert type(result.loc[0, "prediction"]) is int
    assert (
        json.loads(
            json.dumps(handoff_module._json_value(result.to_dict(orient="records")))
        )[0]["prediction"]
        == raw
    )


def test_exact_origin_join_never_infers_availability_or_uses_future_snapshots():
    inventory = pd.DataFrame(
        [
            {
                "SKU_ID": "SKU_1",
                "Warehouse_ID": "WH_1",
                "Date": ORIGIN,
                "Inventory_Level": 100,
                "Reorder_Point": 20,
            },
            {
                "SKU_ID": "SKU_2",
                "Warehouse_ID": "WH_1",
                "Date": "2024-12-03",
                "Inventory_Level": 999,
                "Reorder_Point": 1,
            },
        ]
    )
    before = inventory.copy(deep=True)
    result = forecast_inventory_inputs(handoff(), inventory)
    assert result.loc[0, "Inventory_Level"] == 100
    assert result.loc[0, "origin_snapshot_status"] == "unknown"
    assert pd.isna(result.loc[5, "Inventory_Level"])
    assert result.loc[5, "origin_snapshot_status"] == "unavailable"
    assert result.loc[5, "origin_snapshot_reason"] == "origin_inventory_record_missing"
    assert not result.inventory_state_available.any()
    pd.testing.assert_frame_equal(before, inventory)
    inventory["origin_snapshot_available"] = True
    result = forecast_inventory_inputs(handoff(), inventory)
    assert result.loc[0, "inventory_state_available"]
    assert not result.loc[5, "inventory_state_available"]
    assert result.loc[5, "origin_snapshot_status"] == "unavailable"
    assert result.loc[5, "origin_snapshot_reason"] == "origin_inventory_record_missing"


def test_duplicate_snapshot_and_invented_hash_cannot_be_consumed(tmp_path):
    source = handoff()
    path = tmp_path / "export.json"
    path.write_bytes(source.payload)
    with pytest.raises(ValueError, match="SHA-256"):
        load_forecast_handoff(path)
    assert (
        load_forecast_handoff(path, expected_sha256=source.sha256).document
        == source.document
    )
    inventory = pd.DataFrame(
        [
            {
                "SKU_ID": "SKU_1",
                "Warehouse_ID": "WH_1",
                "Date": ORIGIN,
                "Inventory_Level": 100,
                "Reorder_Point": 20,
            }
        ]
        * 2
    )
    with pytest.raises(ValueError, match="Duplicate inventory"):
        forecast_inventory_inputs(source, inventory)


def test_duplicate_json_keys_are_rejected():
    payload = b'{"source": {}, "source": {}}'
    with pytest.raises(ValueError, match="Duplicate JSON"):
        ForecastHandoff(payload, hashlib.sha256(payload).hexdigest())


@pytest.mark.parametrize(
    "value", ["NaT", "2024-12-02T12:00:00", "2024-12-02T00:00:00Z", None]
)
def test_non_calendar_snapshot_dates_are_not_normalized_into_origin(value):
    inventory = pd.DataFrame(
        [
            {
                "SKU_ID": "SKU_1",
                "Warehouse_ID": "WH_1",
                "Date": value,
                "Inventory_Level": 100,
                "Reorder_Point": 20,
            }
        ]
    )
    with pytest.raises(ValueError):
        forecast_inventory_inputs(handoff(), inventory)


def test_inventory_cli_decodes_only_origin_inventory_and_preserves_precision(
    tmp_path, monkeypatch
):
    from types import SimpleNamespace
    from src.data import validated_handoff

    monkeypatch.setattr(handoff_module, "REPOSITORY", tmp_path)
    document = synthetic_export()
    document["forecasts"][0]["prediction"] = 1.234567891234567
    source = handoff(document)
    monkeypatch.setattr(handoff_module, "load_forecast_handoff", lambda path: source)
    inventory = pd.DataFrame(
        [
            {
                "SKU_ID": "SKU_1",
                "Warehouse_ID": "WH_1",
                "Date": ORIGIN,
                "Inventory_Level": 100,
                "Reorder_Point": 20,
            }
        ]
    )

    def projection(**kwargs):
        assert kwargs["start"] == kwargs["end"] == ORIGIN
        assert "Units_Sold" not in kwargs["columns"]
        assert kwargs["expected_provenance_sha256"]
        return SimpleNamespace(frame=inventory.copy(), provenance_sha256="b" * 64)

    monkeypatch.setattr(validated_handoff, "read_validated_projection", projection)
    output = tmp_path / "research-materials/synthetic/inputs.json"
    arguments = ["--operator", "Synthetic operator", "--output", str(output)]
    assert handoff_module.main(arguments) == 0
    prepared = json.loads(output.read_bytes())
    assert prepared["snapshot_availability"] == "unknown"
    assert len(prepared["records"]) == 1000
    assert prepared["records"][0]["prediction"] == 1.234567891234567
    assert prepared["records"][0]["origin_snapshot_status"] == "unknown"
    assert "forecast_exposure_state" not in prepared["records"][0]
    original = output.read_bytes()
    with pytest.raises(SystemExit):
        handoff_module.main(arguments)
    assert output.read_bytes() == original
    with pytest.raises(SystemExit):
        handoff_module.main([*arguments, "--snapshot-availability", "confirmed"])
    confirmed = output.with_name("confirmed.json")
    assert (
        handoff_module.main(
            [
                "--operator",
                "Synthetic operator",
                "--output",
                str(confirmed),
                "--snapshot-availability",
                "confirmed",
                "--snapshot-basis",
                "Explicit synthetic test availability.",
            ]
        )
        == 0
    )
    assert (
        json.loads(confirmed.read_bytes())["records"][0]["inventory_state_available"]
        is True
    )
