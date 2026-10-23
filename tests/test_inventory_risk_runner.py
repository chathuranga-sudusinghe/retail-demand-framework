"""Synthetic runner/consumer checks; never execute retained research evidence."""

from copy import deepcopy
import hashlib
import json
from types import SimpleNamespace

import pandas as pd
import pytest

from src.decision_support import assessment
from src.inventory_risk import runner
from src.inventory_risk.evaluation import SCENARIO_LIMITATION, evaluate_inventory_risk
from src.inventory_risk.forecast_handoff import forecast_inventory_inputs
from test_inventory_risk_forecast_handoff import handoff, synthetic_export


@pytest.fixture(scope="module")
def inputs():
    inventory = pd.DataFrame(
        [
            {
                "SKU_ID": f"SKU_{sku}",
                "Warehouse_ID": f"WH_{wh}",
                "Date": "2024-12-02",
                "Inventory_Level": 5 if (sku, wh) == (50, 5) else 20,
                "Reorder_Point": 10,
                "Supplier_Lead_Time_Days": 7,
                "Order_Quantity": 999,
            }
            for sku in range(1, 51)
            for wh in range(1, 6)
        ]
    )
    sales = pd.DataFrame(
        [
            {
                "SKU_ID": f"SKU_{sku}",
                "Warehouse_ID": f"WH_{wh}",
                "Date": day,
                "Units_Sold": 2,
            }
            for sku in range(1, 51)
            for wh in range(1, 6)
            for day in pd.date_range("2024-12-03", "2024-12-16")
        ]
    )
    return handoff(), inventory, sales


def evaluate(inputs, policy="constructed-origin", basis=""):
    source, inventory, sales = inputs
    return runner.evaluate_handoff(
        source, inventory, sales, snapshot_policy=policy, snapshot_basis=basis
    )


@pytest.fixture(scope="module")
def constructed_result(inputs):
    return evaluate(inputs)


@pytest.fixture(scope="module")
def policy_results(inputs, constructed_result):
    return {
        "constructed-origin": constructed_result,
        "unknown": evaluate(inputs, "unknown"),
        "source-confirmed": evaluate(
            inputs, "source-confirmed", "Synthetic timing basis."
        ),
    }


def test_constructed_scenario_has_expected_counts_without_verifying_source_timing(
    constructed_result,
):
    result = constructed_result
    cases = result["evaluation"]["cases"]
    assert len(cases) == 750
    assert {r["horizon"] for r in cases} == {1, 7, 14}
    for row in cases:
        assert row["origin_snapshot_available"] is None
        assert row["origin_snapshot_status"] == "unknown"
        assert row["inventory_state_available"] is False
        assert row["analysis_inventory_state_available"] is True
        assert row["scenario_inventory_state_available"] is True
        assert row["inventory_basis"] == "constructed_origin_scenario"
        assert row["snapshot_assumption"] == runner.CONSTRUCTED_BASIS
    summaries = {r["horizon"]: r for r in result["evaluation"]["summary"]}
    assert len(summaries) == 3
    assert (
        summaries[1]["TP"],
        summaries[1]["TN"],
        summaries[1]["FP"],
        summaries[1]["FN"],
    ) == (0, 5, 244, 0)
    for horizon in (7, 14):
        assert (
            summaries[horizon]["TP"],
            summaries[horizon]["TN"],
            summaries[horizon]["FP"],
            summaries[horizon]["FN"],
        ) == (244, 0, 0, 5)
    for row in summaries.values():
        assert row["N"] == 249
        assert row["scenario_at_or_below_count"] == 1
        assert row["origin_known_at_or_below_count"] == 0
    assert summaries[1]["recall"] is None
    assert summaries[1]["balanced_accuracy"] is None
    assert len(result["prospective"]["records"]) == 1000
    for row in result["prospective"]["records"]:
        assert not {
            "observed_target",
            "target_status",
            "comparison_case",
            "confusion_cell",
            "retrospective_margin",
        } & set(row)
        if row["horizon"] == 28:
            assert row["forecast_exposure_state"] == "unavailable"
            assert row["inventory_buffer"] is None
            assert row["predicted_margin"] is None
            assert row["analysis_inventory_state_available"] is False
            assert runner.CONSTRUCTED_BASIS in row["method_assumptions"]
            assert SCENARIO_LIMITATION in row["method_limitations"]


def test_unknown_policy_never_turns_matching_dates_into_exposure(inputs):
    result = evaluate(inputs, "unknown")
    assert all(
        r["forecast_exposure_state"] == "unavailable"
        for r in result["evaluation"]["cases"]
    )
    assert all(
        r["N"] == 0 and r["unavailable_case_count"] == 250
        for r in result["evaluation"]["summary"]
    )


def test_confirmed_policy_requires_an_explicit_source_timing_basis(inputs):
    with pytest.raises(ValueError, match="actual timing basis"):
        evaluate(inputs, "source-confirmed")
    result = evaluate(inputs, "source-confirmed", "Synthetic source timing evidence.")
    assert all(
        r["origin_snapshot_status"] == "available"
        for r in result["evaluation"]["cases"]
    )
    assert all(
        r["origin_known_at_or_below_count"] == 1
        and r["scenario_at_or_below_count"] == 0
        for r in result["evaluation"]["summary"]
    )


def test_missing_daily_record_invalidates_only_its_exact_windows(inputs):
    source, _, sales = inputs
    remove = (
        (sales.SKU_ID == "SKU_2")
        & (sales.Warehouse_ID == "WH_1")
        & (sales.Date == pd.Timestamp("2024-12-10"))
    )
    targets = runner.retrospective_targets(source, sales.loc[~remove]).set_index(
        ["SKU_ID", "Warehouse_ID", "horizon"]
    )
    assert targets.loc[("SKU_2", "WH_1", 1), "observed_target"] == 2
    assert targets.loc[("SKU_2", "WH_1", 7), "observed_target"] == 14
    assert pd.isna(targets.loc[("SKU_2", "WH_1", 14), "observed_target"])
    assert targets.loc[("SKU_2", "WH_1", 14), "target_status"] == "unavailable"
    assert targets.loc[("SKU_2", "WH_1", 14), "target_present_days"] == 13
    assert targets.loc[("SKU_3", "WH_1", 14), "observed_target"] == 28


@pytest.mark.parametrize("bad", [-1, 0.5, float("nan"), True, "2"])
def test_invalid_daily_sales_remain_unavailable_not_zero_or_partial(inputs, bad):
    source, _, sales = inputs
    sales = sales.copy()
    sales["Units_Sold"] = sales["Units_Sold"].astype(object)
    sales.at[0, "Units_Sold"] = bad
    targets = runner.retrospective_targets(source, sales)
    rows = targets.loc[(targets.SKU_ID == "SKU_1") & (targets.Warehouse_ID == "WH_1")]
    assert rows["observed_target"].isna().all()
    assert rows["target_status"].eq("unavailable").all()
    assert rows["target_unavailable_reason"].eq("invalid_daily_units_sold").all()


def test_duplicate_and_out_of_scope_daily_records_fail_explicitly(inputs):
    source, _, sales = inputs
    with pytest.raises(ValueError, match="Duplicate daily"):
        runner.retrospective_targets(source, pd.concat([sales, sales.iloc[:1]]))
    changed = sales.copy()
    changed.at[0, "Date"] = pd.Timestamp("2024-12-17")
    with pytest.raises(ValueError, match="exceeds"):
        runner.retrospective_targets(source, changed)


def test_retrospective_changes_cannot_change_prospective_evidence(
    inputs, constructed_result
):
    source, inventory, sales = inputs
    first = constructed_result
    changed = sales.copy()
    changed["Units_Sold"] = 999
    second = evaluate((source, inventory, changed))
    assert first["prospective"] == second["prospective"]
    assert first["evaluation"]["summary"] != second["evaluation"]["summary"]


def test_missing_origin_does_not_borrow_a_future_snapshot(inputs):
    source, inventory, sales = inputs
    inventory = inventory.copy()
    inventory.loc[0, "Date"] = "2024-12-03"
    result = evaluate((source, inventory, sales))
    rows = [
        r
        for r in result["evaluation"]["cases"]
        if r["SKU_ID"] == "SKU_1" and r["Warehouse_ID"] == "WH_1"
    ]
    assert len(rows) == 3
    assert all(
        r["comparison_case"] == "unavailable"
        and not r["scenario_inventory_state_available"]
        for r in rows
    )


def test_raw_negative_forecast_is_preserved_and_not_scored(inputs):
    _, inventory, sales = inputs
    document = synthetic_export()
    document["forecasts"][5]["prediction"] = -0.25
    result = evaluate((handoff(document), inventory, sales))
    row = result["evaluation"]["cases"][5]
    assert row["prediction"] == -0.25
    assert row["forecast_input_status"] == "unavailable"
    assert row["predicted_margin"] is None
    assert row["comparison_case"] == "unavailable"


def publish(result, tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "REPOSITORY", tmp_path)
    monkeypatch.setattr(assessment, "REPOSITORY", tmp_path)
    output = tmp_path / "research-materials/inventory/synthetic"
    runner.write_result(
        result, output, "Synthetic human operator", runner.PROVENANCE_SHA256
    )
    return output, result


def test_exclusive_bundle_has_json_markdown_and_manifest_bound_files(
    constructed_result, tmp_path, monkeypatch
):
    output, result = publish(constructed_result, tmp_path, monkeypatch)
    assert {p.name for p in output.iterdir()} == {
        "prospective.json",
        "evaluation.json",
        "report.md",
        "manifest.json",
    }
    manifest = json.loads((output / "manifest.json").read_bytes())
    for name, digest in manifest["files"].items():
        assert hashlib.sha256((output / name).read_bytes()).hexdigest() == digest
    report = (output / "report.md").read_text()
    assert "constructed-origin" in report and "not verified source timing" in report
    assert "Denominator" in report and "prior validation exposure" in report
    with pytest.raises(FileExistsError):
        runner.write_result(
            result, output, "Synthetic operator", runner.PROVENANCE_SHA256
        )
    with pytest.raises(ValueError, match="research-materials"):
        runner.write_result(
            result,
            tmp_path / "reports/unsafe",
            "Synthetic operator",
            runner.PROVENANCE_SHA256,
        )


def test_prospective_bridge_populates_only_available_inventory_and_binds_review_to_records(
    inputs, constructed_result, tmp_path, monkeypatch
):
    output, _ = publish(constructed_result, tmp_path, monkeypatch)
    source = inputs[0]
    inventory = assessment.load_inventory_evidence(output / "prospective.json", source)
    bundle = assessment.build_review_records(source, inventory)
    assert len(bundle["records"]) == 20
    for case in bundle["records"]:
        record = case["record"]
        assert record["replenishment_recommendation"] is None
        assert record["uncertainty_or_error"] is None
        assert record["human_review_status"] == "not_assessed"
        if case["horizon"] == 28:
            assert record["inventory_risk_evidence"] is None
            assert "28_day" in record["unavailable_fields"]["inventory_risk_evidence"]
        else:
            risk = record["inventory_risk_evidence"]
            assert risk["inventory_basis"] == "constructed_origin_scenario"
            assert risk["origin_snapshot_status"] == "unknown"
            assert (
                json.loads(record["inventory_risk_provenance"])["prospective_sha256"]
                == inventory["provenance"]["prospective_sha256"]
            )
            assert "inventory_risk_evidence" not in record["unavailable_fields"]
            assert "confusion_cell" not in risk and "observed_target" not in risk
    baseline = assessment.build_review_records(source)
    assert (
        assessment.review_template(baseline)["records_sha256"]
        != assessment.review_template(bundle)["records_sha256"]
    )
    assert all(
        not row["outcome"] for row in assessment.review_template(bundle)["checks"]
    )
    with pytest.raises(ValueError, match="records_sha256"):
        assessment.summarize_reviews(
            bundle, json.dumps(assessment.review_template(baseline))
        )
    monkeypatch.setattr(assessment, "load_forecast_handoff", lambda path: source)
    prepared = tmp_path / "research-materials/decision-support/synthetic-inventory"
    assert (
        assessment.main(
            [
                "prepare",
                "--operator",
                "Synthetic operator",
                "--inventory-evidence",
                str(output / "prospective.json"),
                "--output",
                str(prepared),
            ]
        )
        == 0
    )
    linked = json.loads((prepared / "records.json").read_bytes())
    assert linked == bundle


@pytest.mark.parametrize(
    "tamper",
    [
        "unsealed",
        "retrospective",
        "wrong-source",
        "duplicate",
        "false-source-timing",
        "boolean-prediction",
    ],
)
def test_bridge_rejects_tampering_retrospective_fields_wrong_sources_and_duplicate_keys(
    inputs, constructed_result, tmp_path, monkeypatch, tamper
):
    output, _ = publish(constructed_result, tmp_path, monkeypatch)
    path = output / "prospective.json"
    document = json.loads(path.read_bytes())
    if tamper == "retrospective":
        document["records"][0]["confusion_cell"] = "TP"
    elif tamper == "wrong-source":
        document["source"]["forecast_export_sha256"] = "0" * 64
    elif tamper == "duplicate":
        document["records"][1] = deepcopy(document["records"][0])
    elif tamper == "false-source-timing":
        document["records"][0]["origin_snapshot_status"] = "available"
    elif tamper == "boolean-prediction":
        document["records"][0]["prediction"] = False
    else:
        document["records"][0]["prediction"] = 999
    path.write_text(json.dumps(document))
    if tamper != "unsealed":
        manifest_path = output / "manifest.json"
        manifest = json.loads(manifest_path.read_bytes())
        manifest["source"] = document["source"]
        manifest["files"][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        assessment.load_inventory_evidence(path, inputs[0])


def test_cli_uses_separate_origin_and_retrospective_projections_only(
    inputs, tmp_path, monkeypatch
):
    source, inventory, sales = inputs
    monkeypatch.setattr(runner, "REPOSITORY", tmp_path)
    monkeypatch.setattr(runner, "load_forecast_handoff", lambda path: source)
    calls = []

    def projection(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(
            frame=sales if "Units_Sold" in kwargs["columns"] else inventory,
            provenance_sha256=runner.PROVENANCE_SHA256,
        )

    monkeypatch.setattr(runner, "read_validated_projection", projection)
    output = tmp_path / "research-materials/cli-synthetic"
    assert (
        runner.main(
            [
                "--operator",
                "Synthetic operator",
                "--snapshot-policy",
                "constructed-origin",
                "--output",
                str(output),
            ]
        )
        == 0
    )
    assert len(calls) == 2
    assert calls[0]["start"] == calls[0]["end"] == "2024-12-02"
    assert "Units_Sold" not in calls[0]["columns"]
    assert calls[1]["columns"] == ("SKU_ID", "Warehouse_ID", "Date", "Units_Sold")
    assert calls[1]["start"] == "2024-12-03" and calls[1]["end"] == "2024-12-16"
    assert all(
        "Stockout_Flag" not in c["columns"] and "Demand_Forecast" not in c["columns"]
        for c in calls
    )


@pytest.mark.parametrize("basis", ["", "  ", False, 123])
def test_blank_or_invalid_constructed_basis_is_rejected_before_calculation(basis):
    from src.inventory_risk.evaluation import evaluate_inventory_risk

    with pytest.raises(ValueError, match="nonblank snapshot basis"):
        evaluate_inventory_risk(pd.DataFrame(), scenario_basis=basis)


def test_cli_rejects_missing_source_basis_and_existing_outputs_before_reading_data(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(runner, "REPOSITORY", tmp_path)

    def forbidden(path):
        pytest.fail("Invalid run arguments must fail before reading source data.")

    monkeypatch.setattr(runner, "load_forecast_handoff", forbidden)
    output = tmp_path / "research-materials/guarded"
    with pytest.raises(SystemExit):
        runner.main(
            [
                "--operator",
                "Synthetic operator",
                "--snapshot-policy",
                "source-confirmed",
                "--output",
                str(output),
            ]
        )
    output.mkdir(parents=True)
    with pytest.raises(SystemExit):
        runner.main(
            [
                "--operator",
                "Synthetic operator",
                "--snapshot-policy",
                "constructed-origin",
                "--output",
                str(output),
            ]
        )
    assert not list(output.iterdir())


@pytest.mark.parametrize(
    "policy", ["unknown", "source-confirmed", "constructed-origin"]
)
def test_loader_accepts_consistent_source_and_scenario_policies(
    inputs, policy_results, tmp_path, monkeypatch, policy
):
    output, _ = publish(policy_results[policy], tmp_path, monkeypatch)
    loaded = assessment.load_inventory_evidence(output / "prospective.json", inputs[0])
    assert len(loaded["rows"]) == 1000
    assert all(
        row["forecast_input_reason"] == ""
        for row in loaded["rows"].values()
        if row["forecast_input_status"] == "available"
    )
    gated = loaded["rows"][("SKU_1", "WH_1", "2024-12-02", 28)]
    assert gated["analysis_inventory_state_available"] is False
    if policy == "source-confirmed":
        # A supplied source snapshot and gated downstream analysis are distinct.
        assert gated["inventory_state_available"] is True
        assert gated["origin_snapshot_status"] == "available"


@pytest.mark.parametrize(
    "policy", ["unknown", "source-confirmed", "constructed-origin"]
)
@pytest.mark.parametrize("horizon", [1, 7, 14, 28])
@pytest.mark.parametrize(
    "change, message",
    [
        ({"methodology_status": "approved"}, "Methodology status differs"),
        ({"downstream_use_status": "approved"}, "Downstream use status/reason differs"),
        ({"downstream_use_reason": ""}, "Downstream use status/reason differs"),
        ({"evidence_role": "supportive"}, "Forecast evidence role differs"),
    ],
)
def test_status_and_role_validation_preserves_contract_across_policies_and_horizons(
    policy_results, policy, horizon, change, message
):
    document = policy_results[policy]["prospective"]
    row = deepcopy(next(r for r in document["records"] if r["horizon"] == horizon))
    row.update(change)
    with pytest.raises(ValueError, match=message):
        runner.validate_prospective_state(row, document["source"])


@pytest.mark.parametrize(
    "field, value, message",
    [
        ("methodology_status", "approved", "Methodology status differs"),
        ("downstream_use_status", "approved", "Downstream use status/reason differs"),
        ("downstream_use_reason", "", "Downstream use status/reason differs"),
        ("evidence_role", "supportive", "Forecast evidence role differs"),
    ],
)
def test_loader_rejects_resealed_status_and_role_changes(
    inputs, constructed_result, tmp_path, monkeypatch, field, value, message
):
    output, _ = publish(constructed_result, tmp_path, monkeypatch)
    path = output / "prospective.json"
    document = json.loads(path.read_bytes())
    document["records"][0][field] = value
    path.write_text(json.dumps(document))
    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest["files"][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match=message):
        assessment.load_inventory_evidence(path, inputs[0])


@pytest.mark.parametrize(
    "policy", ["unknown", "source-confirmed", "constructed-origin"]
)
@pytest.mark.parametrize(
    "change",
    [
        {"inventory_basis": "invented_basis"},
        {"origin_snapshot_status": "invented_status"},
        {"origin_snapshot_available": "true"},
        {"analysis_inventory_state_available": 1},
        {"scenario_inventory_state_available": True, "Inventory_Level": None},
        {"analysis_inventory_state_available": True, "Reorder_Point": None},
        {"inventory_buffer": 999},
        {"predicted_margin": 999},
        {"forecast_exposure_state": "invented_state"},
        {"origin_exposure_state": "invented_state"},
    ],
)
def test_cross_field_validation_rejects_inconsistent_policies_balances_and_states(
    policy_results, policy, change
):
    document = policy_results[policy]["prospective"]
    row = deepcopy(document["records"][5])
    row.update(change)
    with pytest.raises(ValueError):
        runner.validate_prospective_state(row, document["source"])


def test_unknown_policy_cannot_claim_scenario_evidence_after_manifest_is_resealed(
    inputs, policy_results, tmp_path, monkeypatch
):
    output, _ = publish(policy_results["unknown"], tmp_path, monkeypatch)
    path = output / "prospective.json"
    document = json.loads(path.read_bytes())
    document["records"][0].update(
        analysis_inventory_state_available=True,
        inventory_basis="constructed_origin_scenario",
        Inventory_Level=None,
    )
    path.write_text(json.dumps(document))
    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest["files"][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        assessment.load_inventory_evidence(path, inputs[0])


@pytest.mark.parametrize("name", ["evaluation.json", "report.md"])
def test_loader_checks_companion_hashes_without_decoding_retrospective_data(
    inputs, constructed_result, tmp_path, monkeypatch, name
):
    output, _ = publish(constructed_result, tmp_path, monkeypatch)
    (output / name).write_bytes(
        b"Synthetic opaque bytes; not JSON or research evidence."
    )
    with pytest.raises(ValueError, match="manifest/file hash differs"):
        assessment.load_inventory_evidence(output / "prospective.json", inputs[0])
    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest["files"][name] = hashlib.sha256((output / name).read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest))
    # The consumer hashes these bytes; it does not interpret future observations.
    assert assessment.load_inventory_evidence(output / "prospective.json", inputs[0])


def test_source_confirmed_missing_origin_has_explicit_reason_and_stays_unavailable(
    inputs, tmp_path, monkeypatch
):
    source, inventory, sales = inputs
    result = evaluate(
        (source, inventory.iloc[1:], sales),
        "source-confirmed",
        "Synthetic timing basis.",
    )
    rows = [
        r
        for r in result["evaluation"]["cases"]
        if r["SKU_ID"] == "SKU_1" and r["Warehouse_ID"] == "WH_1"
    ]
    assert len(rows) == 3
    for row in rows:
        assert row["origin_snapshot_available"] is False
        assert row["origin_snapshot_status"] == "unavailable"
        assert row["origin_snapshot_reason"] == "origin_inventory_record_missing"
        assert row["comparison_case"] == "unavailable"
    output, _ = publish(result, tmp_path, monkeypatch)
    record = assessment.build_review_records(
        source, assessment.load_inventory_evidence(output / "prospective.json", source)
    )["records"][0]["record"]
    assert record["inventory_risk_evidence"] is None
    assert (
        record["unavailable_fields"]["inventory_risk_evidence"]
        == "origin_inventory_record_missing"
    )


def test_library_counterfactual_keeps_explicit_source_unavailability_visible(inputs):
    source, inventory, _ = inputs
    prepared = forecast_inventory_inputs(
        source,
        inventory.assign(
            origin_snapshot_available=False,
            origin_snapshot_unavailable_reason="Synthetic source known unavailable at issuance.",
        ),
    )
    row = evaluate_inventory_risk(
        prepared.iloc[5:6], scenario_basis="Synthetic counterfactual starting balances."
    )["cases"].iloc[0]
    assert (
        row["origin_snapshot_available"] is False
        or not row["origin_snapshot_available"]
    )
    assert row["origin_snapshot_status"] == "unavailable"
    assert (
        row["origin_snapshot_reason"]
        == "Synthetic source known unavailable at issuance."
    )
    assert not row["inventory_state_available"]
    assert row["analysis_inventory_state_available"]
    assert row["origin_exposure_state"] == "scenario_initially_above_threshold"
    assert SCENARIO_LIMITATION in row["method_limitations"]
