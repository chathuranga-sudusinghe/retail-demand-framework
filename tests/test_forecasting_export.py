"""Issue #132 regression tests using temporary synthetic evidence only."""

from copy import deepcopy
from dataclasses import replace
from datetime import date, timedelta
import hashlib
import json
import shutil
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

from src.forecasting import export

HORIZONS = (1, 7, 14, 28)
# Independent expectations from DR-014, not generated from the exporter mapping.
DESIGNATED = {
    1: ("lightgbm", "GBM018"),
    7: ("lightgbm", "GBM011"),
    14: ("xgboost", "GBM022"),
    28: ("xgboost", "GBM003"),
}
PRIMARY = {
    "xgboost": ("GBM006", "GBM009", "GBM022", "GBM003"),
    "lightgbm": ("GBM018", "GBM011", "GBM014", "GBM022"),
    "catboost": ("GBM017", "GBM007", "GBM021", "GBM015"),
}
RECORD_FIELDS = {
    "SKU_ID",
    "Warehouse_ID",
    "forecast_origin",
    "horizon",
    "target_start_date",
    "target_end_date",
    "prediction",
    "model",
    "configuration_id",
    "forecast_type",
    "unit",
    "producer_status",
    "forecast_status",
    "uncertainty",
}
EXCLUDED = {
    "observed_target",
    "mae",
    "rmse",
    "wape",
    "bias",
    "signed_error",
    "absolute_error",
    "Demand_Forecast",
    "metric_status",
    "target_28_day",
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2) + "\n").encode()


def identity(model, horizon, configuration):
    return {
        "model": model,
        "horizon": horizon,
        "configuration_id": configuration,
        "canonical_config_id": configuration if model in PRIMARY else None,
        "run_id": export.RUN_ID,
        "evaluation_stage": "final_evaluation",
        "evidence_role": "primary"
        if model in PRIMARY
        else (
            "supportive" if model in ("ridge", "random_forest") else "simple_baseline"
        ),
        "training_start": "2024-01-01",
        "training_end": "2024-12-02",
        "forecast_origin": "2024-12-02",
        "target_start_date": "2024-12-03",
        "target_end_date": (date(2024, 12, 2) + timedelta(days=horizon)).isoformat(),
    }


@pytest.fixture
def evidence(tmp_path, monkeypatch):
    root = tmp_path / "synthetic-repository"
    directory = root / "artifacts" / "forecasting" / export.RUN_ID
    directory.mkdir(parents=True)
    roster = [["SKU_A", "WH_1"], ["SKU_B", "WH_1"]]
    scope = [
        {"model": model, "horizon": h, "configuration_id": configs[i]}
        for model, configs in PRIMARY.items()
        for i, h in enumerate(HORIZONS)
    ] + [
        {"model": model, "horizon": h, "configuration_id": configuration}
        for model, configuration in (
            ("ridge", "fixed"),
            ("random_forest", "fixed"),
            ("naive", "not_tuned"),
            ("seasonal_naive", "not_tuned"),
        )
        for h in HORIZONS
    ]
    candidates, predictions, model_paths = [], [], []
    values = {1: 1.2345678901234567, 7: 123.45678901234567, 14: -2.875, 28: 0.0}
    for c in scope:
        common = identity(c["model"], c["horizon"], c["configuration_id"])
        artifact = None
        if DESIGNATED[c["horizon"]] == (c["model"], c["configuration_id"]):
            artifact = dict(c)
            filenames = {
                "model": "model.txt" if c["model"] == "lightgbm" else "model.ubj",
                "descriptor": "descriptor.json",
                "preprocessor": "state.json",
                "origin_features": "origin_features.json",
            }
            for name, filename in filenames.items():
                path = (
                    root
                    / "models"
                    / "forecasting"
                    / export.RUN_ID
                    / "final"
                    / c["model"]
                    / f"h{c['horizon']}"
                    / c["configuration_id"]
                    / filename
                )
                path.parent.mkdir(parents=True, exist_ok=True)
                # Deliberately not valid native models or descriptor/state JSON.
                # Success proves the exporter does not deserialize them.
                path.write_bytes(
                    f"opaque synthetic {name} for h{c['horizon']}".encode()
                )
                artifact[name + "_path"] = path.relative_to(root).as_posix()
                artifact[name + "_hash"] = digest(path.read_bytes())
                model_paths.append(path)
        candidates.append(
            {**common, "candidate_status": "completed", "model_artifact": artifact}
        )
        for sku, warehouse in reversed(roster):
            predictions.append(
                {
                    **common,
                    "SKU_ID": sku,
                    "Warehouse_ID": warehouse,
                    "prediction": values[c["horizon"]]
                    if artifact is not None
                    else 999.75,
                }
            )
    integrity = {
        "status": "passed",
        "evaluations": 28,
        "learned_refits": 20,
        "baseline_evaluations": 8,
        "predictions": 56,
        "models_replayed": 20,
    }
    metadata = {
        "run_id": export.RUN_ID,
        "schema_version": "issue-130-final-v1",
        "evaluation_stage": "final_evaluation",
        "run_status": "verified_completed",
        "completed_at_utc": "2026-10-03T15:34:19.963693+00:00",
        "integrity_result": deepcopy(integrity),
        "producer_mapping": [
            {
                "horizon": h,
                "model": DESIGNATED[h][0],
                "configuration_id": DESIGNATED[h][1],
            }
            for h in HORIZONS
        ],
        "temporal_policy": {
            "training_start": "2024-01-01",
            "training_end": "2024-12-02",
            "forecast_origin": "2024-12-02",
            "target_start_date": "2024-12-03",
            "outcome_window_end": "2024-12-30",
        },
        "scope": scope,
        "candidates": deepcopy(scope),
        "pair_roster": roster,
    }
    receipt = {
        "receipt_version": 1,
        "run_id": export.RUN_ID,
        "evaluation_stage": "final_evaluation",
        "candidate_count": 28,
        "prediction_count": 56,
    }
    manifest = {
        "manifest_version": 2,
        "schema_version": "issue-130-final-v1",
        "evaluation_stage": "final_evaluation",
        "run_id": export.RUN_ID,
        "final_status": "verified_completed",
        "completed_at_utc": metadata["completed_at_utc"],
        "integrity_result": deepcopy(integrity),
    }
    fixture = SimpleNamespace(
        root=root,
        directory=directory,
        metadata=metadata,
        receipt=receipt,
        manifest=manifest,
        candidates=candidates,
        predictions=predictions,
        model_paths=model_paths,
        roster=roster,
    )

    def bindings(paths):
        return [
            {
                "path": p.relative_to(root).as_posix(),
                "owner": "models" if p in model_paths else "artifacts",
                "sha256": digest(p.read_bytes()),
            }
            for p in paths
        ]

    def repin():
        anchor = export._SourceAnchor(
            digest((directory / "run_manifest.json").read_bytes()),
            digest((directory / "prediction_receipt.json").read_bytes()),
            2,
            2,
            1,
        )
        monkeypatch.setattr(export, "_VERIFIED_SOURCE", anchor)
        fixture.anchor = anchor

    def publish(prediction_bytes=None):
        (directory / "candidates.json").write_bytes(encoded(candidates))
        (directory / "predictions.json").write_bytes(
            encoded(predictions) if prediction_bytes is None else prediction_bytes
        )
        receipt["files"] = bindings(
            [
                directory / "candidates.json",
                directory / "predictions.json",
                *model_paths,
            ]
        )
        (directory / "prediction_receipt.json").write_bytes(encoded(receipt))
        metadata["prediction_receipt_hash"] = digest(
            (directory / "prediction_receipt.json").read_bytes()
        )
        (directory / "run_metadata.json").write_bytes(encoded(metadata))
        manifest["files"] = bindings(
            [
                directory / "candidates.json",
                directory / "predictions.json",
                directory / "prediction_receipt.json",
                directory / "run_metadata.json",
                *model_paths,
            ]
        )
        (directory / "run_manifest.json").write_bytes(encoded(manifest))
        repin()

    fixture.publish, fixture.repin = publish, repin
    publish()
    return fixture


def selected_row(evidence):
    return next(
        r
        for r in evidence.predictions
        if r["horizon"] == 1 and (r["model"], r["configuration_id"]) == DESIGNATED[1]
    )


def failure(evidence, match):
    with pytest.raises(export.ForecastExportError, match=match) as exc:
        export.write_forecast_export(evidence.root)
    assert exc.value.reason_code == "source_unverified"
    assert not (evidence.root / export.DESTINATION).exists()


def test_exact_producers_four_horizons_and_identity_timing(evidence):
    result = export.build_forecast_export(evidence.root)
    assert result["record_count"] == 8 and result["series_count"] == 2
    assert result["forecast_origin"] == result["training_end"] == "2024-12-02"
    assert result["training_start"] == "2024-01-01"
    for row in result["forecasts"]:
        h = row["horizon"]
        assert (row["model"], row["configuration_id"]) == DESIGNATED[h]
        assert row["forecast_type"] == ("next_day" if h == 1 else "cumulative_window")
        assert row["forecast_origin"] == "2024-12-02"
        assert row["target_start_date"] == "2024-12-03"
        assert (
            row["target_end_date"]
            == (date(2024, 12, 2) + timedelta(days=h)).isoformat()
        )
        assert [row["SKU_ID"], row["Warehouse_ID"]] in evidence.roster
        assert (
            row["forecast_status"] == "available"
            and row["producer_status"] == "designated_producer"
        )
        assert row["uncertainty"] == {
            "status": "unavailable",
            "reason": "no_agreed_method",
        }
    assert {r["horizon"] for r in result["forecasts"]} == {1, 7, 14, 28}
    # A comparator has the same series/origin/horizon key but is never returned.
    assert all(r["prediction"] != 999.75 for r in result["forecasts"])


def test_exact_quantities_including_zero_negative_and_fractional_values(evidence):
    result = export.build_forecast_export(evidence.root)
    for record in result["forecasts"]:
        original = next(
            r
            for r in evidence.predictions
            if all(
                r[k] == record[k]
                for k in (
                    "SKU_ID",
                    "Warehouse_ID",
                    "horizon",
                    "model",
                    "configuration_id",
                )
            )
        )
        assert record["prediction"] == original["prediction"]
        assert type(record["prediction"]) is type(original["prediction"])
    assert [r["prediction"] for r in result["forecasts"]][::2] == [
        1.2345678901234567,
        123.45678901234567,
        -2.875,
        0.0,
    ]


def test_explicit_allowlist_excludes_retrospective_fields_at_every_level(evidence):
    extras = {name: {"must_not_be_exported": 42} for name in EXCLUDED}
    for row in evidence.predictions:
        row.update(extras)
    evidence.metadata.update(extras)
    evidence.candidates[0].update(extras)
    for candidate in evidence.candidates:
        if candidate["model_artifact"]:
            candidate["model_artifact"].update(extras)
    evidence.publish()
    result = export.build_forecast_export(evidence.root)
    assert set(result) == {
        "export_schema",
        "source",
        "forecast_origin",
        "training_start",
        "training_end",
        "producers",
        "series_count",
        "record_count",
        "forecasts",
    }
    assert all(set(r) == RECORD_FIELDS for r in result["forecasts"])
    assert set(result["source"]) == {
        "run_id",
        "evaluation_stage",
        "source_schema",
        "run_manifest_path",
        "run_manifest_sha256",
        "prediction_receipt_sha256",
        "integrity_result",
    }
    assert result["source"]["integrity_result"] == evidence.manifest["integrity_result"]
    for producer in result["producers"]:
        assert set(producer) == {
            "horizon",
            "model",
            "configuration_id",
            "forecast_type",
            "model_reference",
        }
        assert set(producer["model_reference"]) == {
            name + suffix
            for name in ("model", "descriptor", "preprocessor", "origin_features")
            for suffix in ("_path", "_hash")
        }

    def check(value):
        if isinstance(value, dict):
            assert not set(value) & EXCLUDED
            for nested in value.values():
                check(nested)
        elif isinstance(value, list):
            for nested in value:
                check(nested)

    check(result)


def test_deterministic_ordering_and_bytes_despite_source_row_order(evidence, tmp_path):
    first = export.write_forecast_export(evidence.root)
    output = evidence.root / export.DESTINATION
    first_bytes = output.read_bytes()
    result = json.loads(first_bytes)
    assert [
        (r["horizon"], r["SKU_ID"], r["Warehouse_ID"]) for r in result["forecasts"]
    ] == [(h, sku, "WH_1") for h in HORIZONS for sku in ("SKU_A", "SKU_B")]
    assert first == {"path": export.DESTINATION, "sha256": digest(first_bytes)}
    assert (
        json.loads(first_bytes)["forecasts"]
        == export.build_forecast_export(evidence.root)["forecasts"]
    )
    # A different output root with identical retained bytes must produce identical output.
    other = tmp_path / "other-synthetic-repository"
    shutil.copytree(evidence.root, other, ignore=shutil.ignore_patterns("handoffs"))
    second = export.write_forecast_export(other)
    assert (other / export.DESTINATION).read_bytes() == first_bytes
    assert second == first
    # Row order is irrelevant to output record order (source provenance hashes change).
    evidence.predictions.reverse()
    evidence.candidates.reverse()
    evidence.publish()
    assert (
        export.build_forecast_export(evidence.root)["forecasts"] == result["forecasts"]
    )


def test_write_is_exclusive_preserves_source_and_creates_no_hash_sidecar(evidence):
    before = {p: p.read_bytes() for p in evidence.root.rglob("*") if p.is_file()}
    result = export.write_forecast_export(evidence.root)
    destination = evidence.root / result["path"]
    with pytest.raises(FileExistsError):
        export.write_forecast_export(evidence.root)
    assert digest(destination.read_bytes()) == result["sha256"]
    assert list(destination.parent.iterdir()) == [destination]
    assert all(p.read_bytes() == data for p, data in before.items())


@pytest.mark.parametrize(
    "name",
    [
        "run_manifest.json",
        "run_metadata.json",
        "prediction_receipt.json",
        "candidates.json",
        "predictions.json",
    ],
)
def test_missing_evidence_is_unavailable_without_fallback(evidence, name):
    (evidence.directory / name).unlink()
    failure(evidence, "missing or malformed")


@pytest.mark.parametrize(
    "name",
    [
        "run_manifest.json",
        "run_metadata.json",
        "prediction_receipt.json",
        "candidates.json",
        "predictions.json",
    ],
)
def test_changed_evidence_bytes_fail_independent_or_bound_hash(evidence, name):
    with (evidence.directory / name).open("ab") as stream:
        stream.write(b" ")
    failure(evidence, "hash differs")


def test_wrong_independent_receipt_pin_is_rejected(evidence, monkeypatch):
    monkeypatch.setattr(
        export, "_VERIFIED_SOURCE", replace(evidence.anchor, receipt_sha256="0" * 64)
    )
    failure(evidence, "pinned prediction receipt")


def test_real_population_requirement_rejects_inconsistent_recorded_counts(
    evidence, monkeypatch
):
    monkeypatch.setattr(
        export,
        "_VERIFIED_SOURCE",
        replace(evidence.anchor, series_count=250, sku_count=50, warehouse_count=5),
    )
    failure(evidence, "integrity result")


def test_real_roster_size_is_checked_after_consistent_integrity(evidence, monkeypatch):
    # Consistent source hashes and recorded counts let this reach the roster check.
    evidence.manifest["integrity_result"]["predictions"] = 7000
    evidence.metadata["integrity_result"]["predictions"] = 7000
    evidence.receipt["prediction_count"] = 7000
    evidence.publish()
    monkeypatch.setattr(
        export,
        "_VERIFIED_SOURCE",
        replace(evidence.anchor, series_count=250, sku_count=50, warehouse_count=5),
    )
    failure(evidence, "SKU/warehouse roster is incomplete")


def test_real_roster_cardinalities_are_checked_with_250_unique_pairs(
    evidence, monkeypatch
):
    roster = [[f"SKU_{s:02}", f"WH_{w}"] for s in range(50) for w in range(5)]
    # Still sorted, unique and 250 pairs, but now includes six warehouses.
    roster[-1][1] = "WH_5"
    evidence.metadata["pair_roster"] = roster
    evidence.manifest["integrity_result"]["predictions"] = 7000
    evidence.metadata["integrity_result"]["predictions"] = 7000
    evidence.receipt["prediction_count"] = 7000
    evidence.publish()
    monkeypatch.setattr(
        export,
        "_VERIFIED_SOURCE",
        replace(evidence.anchor, series_count=250, sku_count=50, warehouse_count=5),
    )
    failure(
        evidence, "SKU/warehouse population differs from the approved complete grid"
    )


def test_noncartesian_roster_is_rejected_despite_matching_declared_cardinalities(
    evidence, monkeypatch
):
    evidence.metadata["pair_roster"] = [["SKU_A", "WH_1"], ["SKU_B", "WH_2"]]
    evidence.publish()
    monkeypatch.setattr(
        export, "_VERIFIED_SOURCE", replace(evidence.anchor, warehouse_count=2)
    )
    failure(
        evidence, "SKU/warehouse population differs from the approved complete grid"
    )


@pytest.mark.parametrize(
    "field,value,reason",
    [
        ("run_id", "another-run", "Run or evaluation stage"),
        ("evaluation_stage", "validation", "Run or evaluation stage"),
        ("forecast_origin", "2024-12-03", "forecast origin"),
        ("forecast_origin", "abc", "forecast origin"),
        ("training_end", "2024-12-03", "forecast origin"),
        ("target_start_date", "2024-12-02", "Target interval"),
        ("target_end_date", "2024-12-04", "Target interval"),
        ("horizon", 2, "Unsupported evidence horizon"),
        ("horizon", True, "Unsupported evidence horizon"),
        ("horizon", 1.0, "Unsupported evidence horizon"),
        ("horizon", None, "Unsupported evidence horizon"),
        ("SKU_ID", "UNKNOWN", "SKU/warehouse identity"),
        ("Warehouse_ID", "UNKNOWN", "SKU/warehouse identity"),
        ("model", "xgboost", "no declared candidate"),
        ("configuration_id", "GBM001", "no declared candidate"),
        ("canonical_config_id", "GBM001", "designated producer identity"),
        ("evidence_role", "supportive", "designated producer identity"),
        ("prediction", None, "quantity"),
        ("prediction", "12.5", "quantity"),
        ("prediction", False, "quantity"),
    ],
)
def test_malformed_rows_rejected_after_valid_hash_bindings(
    evidence, field, value, reason
):
    selected_row(evidence)[field] = value
    # Rebind fixture hashes so each test reaches its intended content validation.
    evidence.publish()
    failure(evidence, reason)


@pytest.mark.parametrize("quantity", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_quantities_never_export(evidence, quantity):
    selected_row(evidence)["prediction"] = quantity
    evidence.publish()
    failure(evidence, "Non-finite JSON constant")


def test_raw_json_numeric_overflow_is_rejected_by_quantity_validation(evidence):
    row = selected_row(evidence)
    index = evidence.predictions.index(row)
    row["prediction"] = "__RAW_NUMERIC_OVERFLOW__"
    raw = encoded(evidence.predictions).replace(b'"__RAW_NUMERIC_OVERFLOW__"', b"1e309")
    assert b"1e309" in raw and b"Infinity" not in raw
    assert json.loads(raw)[index]["prediction"] == float("inf")
    # Bind every parent hash to these bytes so the test reaches quantity validation.
    evidence.publish(prediction_bytes=raw)
    failure(evidence, "Prediction quantity is missing, malformed or non-finite")


def test_duplicate_identity_cannot_replace_missing_series_with_same_count(evidence):
    chosen = selected_row(evidence)
    counterpart = next(
        r
        for r in evidence.predictions
        if r["model"] == chosen["model"]
        and r["horizon"] == chosen["horizon"]
        and r["SKU_ID"] != chosen["SKU_ID"]
    )
    counterpart.update(deepcopy(chosen))
    evidence.publish()
    failure(evidence, "Duplicate forecast identity")


def test_missing_designated_record_never_substitutes_comparator(evidence):
    evidence.predictions.remove(selected_row(evidence))
    evidence.publish()
    failure(evidence, "Incomplete forecast population")


@pytest.mark.parametrize(
    "change,reason",
    [
        ("failed_manifest", "completion identity or status"),
        ("failed_metadata", "Metadata and completion"),
        ("failed_integrity", "Recorded integrity"),
        ("failed_candidate", "Candidate is unavailable"),
        ("changed_mapping", "Frozen designated producer"),
        ("duplicate_candidate", "Candidate is unavailable"),
        ("missing_producer", "declared scope"),
        ("wrong_model_identity", "model reference identity"),
        ("wrong_model_path", "reference path or hash"),
        ("wrong_model_hash", "not bound"),
        ("duplicate_roster", "roster is incomplete"),
        ("invalid_roster", "Malformed SKU/warehouse"),
    ],
)
def test_unavailable_or_inconsistent_evidence_has_meaningful_failure(
    evidence, change, reason
):
    producer = next(
        c
        for c in evidence.candidates
        if (c["model"], c["configuration_id"]) == DESIGNATED[c["horizon"]]
    )
    if change == "failed_manifest":
        evidence.manifest["final_status"] = "failed"
    elif change == "failed_metadata":
        evidence.metadata["run_status"] = "failed"
    elif change == "failed_integrity":
        evidence.manifest["integrity_result"]["status"] = "failed"
    elif change == "failed_candidate":
        producer["candidate_status"] = "failed"
    elif change == "changed_mapping":
        evidence.metadata["producer_mapping"][0]["configuration_id"] = "GBM006"
    elif change == "duplicate_candidate":
        evidence.candidates[1] = deepcopy(evidence.candidates[0])
    elif change == "missing_producer":
        producer["configuration_id"] = "GBM001"
    elif change == "wrong_model_identity":
        producer["model_artifact"]["horizon"] = 7
    elif change == "wrong_model_path":
        producer["model_artifact"]["model_path"] = (
            "models/forecasting/another-run/model.txt"
        )
    elif change == "wrong_model_hash":
        producer["model_artifact"]["model_hash"] = "0" * 64
    elif change == "duplicate_roster":
        evidence.metadata["pair_roster"] = [["SKU_A", "WH_1"], ["SKU_A", "WH_1"]]
    elif change == "invalid_roster":
        evidence.metadata["pair_roster"] = [[None, "WH_1"], ["SKU_B", "WH_1"]]
    evidence.publish()
    failure(evidence, reason)


@pytest.mark.parametrize(
    "kind", ["duplicate", "missing", "redirected", "wrong_owner", "sealed_mismatch"]
)
def test_manifest_and_receipt_binding_errors(evidence, kind):
    if kind == "duplicate":
        evidence.manifest["files"].append(evidence.manifest["files"][0])
    elif kind == "missing":
        evidence.manifest["files"].pop(0)
    elif kind == "redirected":
        evidence.manifest["files"][0]["path"] = "../predictions.json"
    elif kind == "wrong_owner":
        evidence.manifest["files"][0]["owner"] = "models"
    else:
        evidence.receipt["files"][0]["sha256"] = "0" * 64
        receipt_bytes = encoded(evidence.receipt)
        (evidence.directory / "prediction_receipt.json").write_bytes(receipt_bytes)
        evidence.metadata["prediction_receipt_hash"] = digest(receipt_bytes)
        metadata_bytes = encoded(evidence.metadata)
        (evidence.directory / "run_metadata.json").write_bytes(metadata_bytes)
        for row in evidence.manifest["files"]:
            if row["path"].endswith("prediction_receipt.json"):
                row["sha256"] = digest(receipt_bytes)
            if row["path"].endswith("run_metadata.json"):
                row["sha256"] = digest(metadata_bytes)
    (evidence.directory / "run_manifest.json").write_bytes(encoded(evidence.manifest))
    evidence.repin()
    failure(evidence, "binding|path|owner|bound")


@pytest.mark.parametrize("name", ["model", "descriptor", "state", "origin_features"])
def test_changed_producer_reference_bytes_are_rejected(evidence, name):
    path = next(p for p in evidence.model_paths if p.stem == name)
    path.write_bytes(b"changed producer bytes")
    failure(evidence, "Producer reference bytes changed")


@pytest.mark.parametrize(
    "malformed",
    [
        b'{"manifest_version":2,"manifest_version":2}',
        b'{"broken":',
        b"[]",
    ],
)
def test_malformed_manifest_json_rejected_even_when_hash_matches_fixture(
    evidence, malformed
):
    (evidence.directory / "run_manifest.json").write_bytes(malformed)
    evidence.repin()
    failure(evidence, "Duplicate JSON|missing or malformed|completion identity")


def test_input_and_destination_symlinks_are_rejected(evidence, tmp_path):
    prediction = evidence.directory / "predictions.json"
    original = prediction.read_bytes()
    external = tmp_path / "redirected-predictions.json"
    external.write_bytes(original)
    prediction.unlink()
    prediction.symlink_to(external)
    failure(evidence, "missing or malformed")
    prediction.unlink()
    prediction.write_bytes(original)
    handoffs = evidence.root / "data" / "processed" / "forecasting" / "handoffs"
    handoffs.parent.mkdir(parents=True)
    external_output = tmp_path / "redirected-output"
    external_output.mkdir()
    handoffs.symlink_to(external_output, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink|escapes"):
        # RepositoryLayout may reject an escaping link before the symlink check.
        export.write_forecast_export(evidence.root)
    assert not list(external_output.iterdir())


def test_no_outcomes_reads_or_model_deserialization(evidence, monkeypatch):
    original_open = Path.open
    permitted_json = {
        "run_manifest.json",
        "run_metadata.json",
        "prediction_receipt.json",
        "candidates.json",
        "predictions.json",
    }
    read_paths = []

    def guarded_open(path, *args, **kwargs):
        assert path.name not in {"observations.json", "metrics.json"}
        assert path.is_relative_to(evidence.root)
        read_paths.append(path)
        return original_open(path, *args, **kwargs)

    original_json = export._json
    parsed_paths = []

    def guarded_json(data):
        # Parsing is limited to the five bound source documents. Opaque models
        # and descriptors/states cannot accidentally pass this assertion.
        matching = [
            p.name
            for p in evidence.directory.iterdir()
            if p.name in permitted_json and p.read_bytes() == data
        ]
        assert len(matching) == 1
        parsed_paths.extend(matching)
        return original_json(data)

    monkeypatch.setattr(Path, "open", guarded_open)
    monkeypatch.setattr(export, "_json", guarded_json)
    result = export.build_forecast_export(evidence.root)
    assert result["source"]["integrity_result"] == evidence.metadata["integrity_result"]
    assert set(parsed_paths) == permitted_json
    assert set(evidence.model_paths) <= set(read_paths)


def test_import_and_help_do_not_import_scientific_execution_modules():
    code = (
        "import sys; import src.forecasting.export; "
        "forbidden = ['numpy', 'pandas', 'sklearn', 'src.forecasting.models', "
        "'src.forecasting.metrics', 'src.forecasting.final_artifacts', "
        "'src.forecasting.final_authorization']; "
        "assert not any(m in sys.modules for m in forbidden)"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
    help_result = subprocess.run(
        [sys.executable, "-m", "src.forecasting.export", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert help_result.returncode == 0 and "--repository" in help_result.stdout
