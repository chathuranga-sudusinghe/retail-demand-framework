"""Synthetic preparation and human-checklist validation, not research evidence."""

from copy import deepcopy
import hashlib
import json

import pytest

from src.decision_support import assessment
from src.decision_support.assessment import (
    CRITERIA,
    build_review_records,
    prepare_files,
    records_markdown,
    review_template,
    summarize_files,
    summarize_reviews,
)
from test_inventory_risk_forecast_handoff import handoff, synthetic_export


def reviews(bundle, rows):
    document = review_template(bundle)
    document["checks"] = rows
    return json.dumps(document)


def completed_reviews(bundle, *, outcome="met"):
    rows = review_template(bundle)["checks"]
    for row in rows:
        row.update(
            applicable="yes",
            outcome=outcome,
            reason="Synthetic evidence reason.",
            evidence="Synthetic record reference.",
            assessor="Synthetic test assessor",
            assessed_on="2026-10-23",
        )
    return rows


def test_twenty_records_preserve_scope_values_and_unavailable_reasons():
    source = handoff()
    bundle = build_review_records(source)
    assert len(bundle["records"]) == 20
    assert [case["assessment_id"] for case in bundle["records"]] == [
        f"F{i:02d}" for i in range(1, 21)
    ]
    assert [case["horizon"] for case in bundle["records"][:4]] == [1, 7, 14, 28]
    first = bundle["records"][0]["record"]
    assert first["forecast_demand"] == 0
    assert first["forecast_horizon"] == "1-day"
    assert first["human_review_status"] == "not_assessed"
    assert first["human_review_reasons"]
    provenance = json.loads(first["forecast_provenance"])
    assert provenance["export_sha256"] == source.sha256
    assert provenance["source"] == source.document["source"]
    for case in bundle["records"]:
        record = case["record"]
        assert record["inventory_risk_evidence"] is None
        assert record["inventory_risk_provenance"] is None
        assert record["replenishment_recommendation"] is None
        assert record["uncertainty_or_error"] is None
        assert (
            "no_agreed_method" in record["unavailable_fields"]["uncertainty_or_error"]
        )
        assert "inventory_risk" not in record["component_provenance"]
        assert all(record["unavailable_fields"].values())
        if case["horizon"] == 28:
            assert (
                "28_day_downstream_use_requires_separate_approval"
                in record["unavailable_fields"]["inventory_risk_evidence"]
            )


def test_missing_selected_identity_fails_instead_of_silently_replacing_it():
    document = synthetic_export()
    for row in document["forecasts"]:
        if row["SKU_ID"] == "SKU_20":
            row["SKU_ID"] = "SKU_99"
    source = handoff(document)
    with pytest.raises(ValueError, match="Selected forecast key is missing"):
        build_review_records(source)


def test_raw_negative_prediction_is_visible_with_a_limitation_not_repaired():
    document = synthetic_export()
    document["forecasts"][0]["prediction"] = -2.5
    first = build_review_records(handoff(document))["records"][0]["record"]
    assert first["forecast_demand"] == -2.5
    assert any("negative forecast" in value for value in first["limitations"])


def test_checklist_is_blank_and_cannot_be_counted_as_completed():
    bundle = build_review_records(handoff())
    template = review_template(bundle)
    rows = template["checks"]
    assert len(rows) == 20 * len(CRITERIA) == 160
    assert all(
        row[key] == ""
        for row in rows
        for key in ("outcome", "reason", "applicable", "assessor", "assessed_on")
    )
    with pytest.raises(ValueError):
        summarize_reviews(bundle, json.dumps(template))


@pytest.mark.parametrize(
    "change",
    [
        {"outcome": ""},
        {"applicable": ""},
        {"applicable": "maybe"},
        {"outcome": "pass"},
        {"evidence": ""},
        {"assessor": ""},
        {"assessed_on": ""},
        {"assessed_on": "2026-02-30"},
        {"sku_id": "WRONG"},
        {"horizon": "28"},
        {"horizon": "1"},
        {"horizon": True},
        {"horizon": 1.0},
        {"applicable": True},
        {"outcome": None},
        {"evidence": ["not a string"]},
    ],
)
def test_incomplete_or_mismatched_human_rows_cannot_produce_results(change):
    bundle = build_review_records(handoff())
    rows = completed_reviews(bundle)
    rows[0].update(change)
    with pytest.raises(ValueError):
        summarize_reviews(bundle, reviews(bundle, rows))


@pytest.mark.parametrize("outcome", ["not met", "not assessable"])
def test_non_met_outcomes_require_reasons(outcome):
    bundle = build_review_records(handoff())
    rows = completed_reviews(bundle, outcome=outcome)
    rows[0]["reason"] = ""
    with pytest.raises(ValueError, match="needs a reason"):
        summarize_reviews(bundle, reviews(bundle, rows))


def test_duplicate_and_omitted_checks_are_rejected():
    bundle = build_review_records(handoff())
    rows = completed_reviews(bundle)
    with pytest.raises(ValueError, match="every record/criterion"):
        summarize_reviews(bundle, reviews(bundle, rows[:-1]))
    rows[-1] = deepcopy(rows[0])
    with pytest.raises(ValueError, match="duplicate review"):
        summarize_reviews(bundle, reviews(bundle, rows))


def test_counts_include_unassessable_cases_and_keep_zero_denominators_null():
    bundle = build_review_records(handoff())
    rows = completed_reviews(bundle)
    for row in rows:
        if row["criterion"] == "Risk visibility":
            row.update(
                outcome="not assessable", reason="Synthetic missing upstream evidence."
            )
        elif row["criterion"] == "Recommendation traceability":
            row.update(
                applicable="no",
                outcome="",
                reason="Synthetic human-reviewed non-applicability.",
            )
    result = summarize_reviews(bundle, reviews(bundle, rows))
    assert result["reviewed_records"] == 20
    assert result["reviewed_check_rows"] == 160
    assert result["criteria"]["Risk visibility"]["not assessable"] == 20
    assert result["criteria"]["Risk visibility"]["met_proportion"] == 0
    assert result["criteria"]["Forecast visibility"]["met_proportion"] == 1
    assert result["criteria"]["Recommendation traceability"]["not_applicable"] == 20
    assert result["criteria"]["Recommendation traceability"]["met_proportion"] is None


def test_local_only_files_are_exclusive_and_summary_is_bound_to_records(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(assessment, "REPOSITORY", tmp_path)
    destination = tmp_path / "research-materials/assessment/synthetic"
    source = handoff()
    prepare_files(source, destination, "Synthetic test operator")
    bundle = json.loads((destination / "records.json").read_bytes())
    with pytest.raises(FileExistsError):
        prepare_files(source, destination, "Another operator")
    with pytest.raises(ValueError, match="research-materials"):
        prepare_files(source, tmp_path / "docs/unsafe", "Synthetic test operator")
    assert {p.name for p in destination.iterdir()} == {
        "records.json",
        "records.md",
        "review.json",
        "manifest.json",
    }
    manifest = json.loads((destination / "manifest.json").read_bytes())
    assert (
        manifest["records_markdown_sha256"]
        == hashlib.sha256((destination / "records.md").read_bytes()).hexdigest()
    )
    (destination / "review.json").write_text(reviews(bundle, completed_reviews(bundle)))
    report = destination / "summary.json"
    summarize_files(destination, report)
    result = json.loads(report.read_bytes())
    assert result["reviewed_check_rows"] == 160
    assert (
        result["review_sha256"]
        == hashlib.sha256((destination / "review.json").read_bytes()).hexdigest()
    )
    markdown = (destination / "summary.md").read_text()
    assert "Reviewed records: 20. Reviewed checks: 160." in markdown
    assert result["review_sha256"] in markdown
    assert "| Forecast visibility | 20 | 0 | 20 | 0 | 0 | 1.0000 |" in markdown
    assert result["proportion_denominator"] in markdown
    with pytest.raises(FileExistsError):
        summarize_files(destination, report)
    (destination / "records.json").write_bytes(b"{}")
    with pytest.raises(ValueError, match="records changed"):
        summarize_files(destination, destination / "tampered-summary.json")


def test_cli_prepare_and_summary_use_only_synthetic_files(tmp_path, monkeypatch):
    monkeypatch.setattr(assessment, "REPOSITORY", tmp_path)
    synthetic = handoff()
    monkeypatch.setattr(assessment, "load_forecast_handoff", lambda path: synthetic)
    output = tmp_path / "research-materials/synthetic-cli"
    assert (
        assessment.main(
            ["prepare", "--output", str(output), "--operator", "Synthetic operator"]
        )
        == 0
    )
    bundle = json.loads((output / "records.json").read_bytes())
    (output / "review.json").write_text(reviews(bundle, completed_reviews(bundle)))
    assert (
        assessment.main(
            [
                "summarize",
                "--directory",
                str(output),
                "--report",
                str(output / "summary.json"),
            ]
        )
        == 0
    )
    assert (output / "summary.md").is_file()


@pytest.mark.parametrize(
    "change",
    [
        {"review_schema": "wrong-version"},
        {"mapping_version": "wrong-mapping"},
        {"source_export_sha256": "0" * 64},
        {"extra": "unexpected"},
        {"checks": {}},
        {"checks": [None]},
    ],
)
def test_json_review_rejects_wrong_source_version_and_malformed_checks(change):
    bundle = build_review_records(handoff())
    document = json.loads(reviews(bundle, completed_reviews(bundle)))
    document.update(change)
    with pytest.raises(ValueError):
        summarize_reviews(bundle, json.dumps(document))


@pytest.mark.parametrize(
    "text", ["[]", '{"checks": [], "checks": []}', '{"checks": NaN}']
)
def test_json_review_rejects_non_objects_duplicate_fields_and_nonfinite_values(text):
    with pytest.raises(ValueError):
        summarize_reviews(build_review_records(handoff()), text)


def test_markdown_preserves_every_record_and_missing_evidence():
    bundle = build_review_records(handoff())
    markdown = records_markdown(bundle)
    assert markdown.count("\n## F") == 20
    assert "[review.json](review.json)" in markdown
    assert bundle["source"]["export_sha256"] in markdown
    assert '"inventory_risk_evidence": null' in markdown
    assert "28_day_downstream_use_requires_separate_approval" in markdown
    assert "not completed transparency assessments" in markdown
    for case in bundle["records"]:
        assert json.dumps(case, indent=2, sort_keys=True) in markdown


def test_existing_markdown_report_cannot_be_overwritten(tmp_path, monkeypatch):
    monkeypatch.setattr(assessment, "REPOSITORY", tmp_path)
    destination = tmp_path / "research-materials/synthetic-report"
    prepare_files(handoff(), destination, "Synthetic operator")
    bundle = json.loads((destination / "records.json").read_bytes())
    (destination / "review.json").write_text(reviews(bundle, completed_reviews(bundle)))
    markdown = destination / "summary.md"
    markdown.write_text("Preserve this existing report.")
    with pytest.raises(FileExistsError):
        summarize_files(destination, destination / "summary.json")
    assert markdown.read_text() == "Preserve this existing report."
    assert not (destination / "summary.json").exists()


def test_summary_rejects_changed_readable_records_and_bad_output_extension(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(assessment, "REPOSITORY", tmp_path)
    destination = tmp_path / "research-materials/synthetic-report"
    prepare_files(handoff(), destination, "Synthetic operator")
    bundle = json.loads((destination / "records.json").read_bytes())
    (destination / "review.json").write_text(reviews(bundle, completed_reviews(bundle)))
    with pytest.raises(ValueError, match="must end in .json"):
        summarize_files(destination, destination / "summary.csv")
    (destination / "records.md").write_text("Altered displayed evidence.")
    with pytest.raises(ValueError, match="Readable records changed"):
        summarize_files(destination, destination / "summary.json")
    assert not (destination / "summary.json").exists()


def test_markdown_reports_zero_denominator_without_a_percentage(tmp_path, monkeypatch):
    monkeypatch.setattr(assessment, "REPOSITORY", tmp_path)
    destination = tmp_path / "research-materials/synthetic-report"
    prepare_files(handoff(), destination, "Synthetic operator")
    bundle = json.loads((destination / "records.json").read_bytes())
    rows = completed_reviews(bundle)
    for row in rows:
        if row["criterion"] == "Recommendation traceability":
            row.update(
                applicable="no", outcome="", reason="Synthetic non-applicability."
            )
    (destination / "review.json").write_text(reviews(bundle, rows))
    summarize_files(destination, destination / "summary.json")
    assert (
        "| Recommendation traceability | 0 | 20 | 0 | 0 | 0 | N/A (zero applicable checks) |"
        in (destination / "summary.md").read_text()
    )


def legacy_bundle(tmp_path, monkeypatch):
    """Recreate the original forecast-only format using synthetic evidence."""
    monkeypatch.setattr(assessment, "REPOSITORY", tmp_path)
    directory = tmp_path / "research-materials/synthetic-legacy"
    prepare_files(handoff(), directory, "Synthetic original operator")
    bundle = json.loads((directory / "records.json").read_bytes())
    template = assessment._legacy_review_template(bundle)
    manifest_path = directory / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest["review_schema"] = assessment.LEGACY_REVIEW_SCHEMA
    manifest["initial_review_template_sha256"] = hashlib.sha256(
        assessment._json_bytes(template)
    ).hexdigest()
    # A historical generator digest is metadata, not a match to today's source.
    manifest["code_sha256"]["src/decision_support/assessment.py"] = "0" * 64
    manifest_path.write_bytes(assessment._json_bytes(manifest))
    template["checks"] = completed_reviews(bundle)
    (directory / "review.json").write_bytes(assessment._json_bytes(template))
    return directory, bundle, manifest


def test_legacy_forecast_only_bundle_summarizes_without_migrating_original_files(
    tmp_path, monkeypatch
):
    directory, _, manifest = legacy_bundle(tmp_path, monkeypatch)
    before = {p.name: p.read_bytes() for p in directory.iterdir()}
    report = directory / "legacy-summary.json"
    summarize_files(directory, report)
    result = json.loads(report.read_bytes())
    assert result["review_schema"] == assessment.LEGACY_REVIEW_SCHEMA
    assert result["reviewed_check_rows"] == 160
    assert result["preparation_code_sha256"] == manifest["code_sha256"]
    assert result["records_sha256"] == manifest["records_sha256"]
    for name, payload in before.items():
        assert (directory / name).read_bytes() == payload


def test_legacy_review_requires_verified_record_and_original_template_bindings(
    tmp_path, monkeypatch
):
    directory, bundle, manifest = legacy_bundle(tmp_path, monkeypatch)
    review_text = (directory / "review.json").read_text()
    with pytest.raises(ValueError, match="verified original record-manifest"):
        summarize_reviews(bundle, review_text)
    with pytest.raises(ValueError, match="verified original record-manifest"):
        summarize_reviews(bundle, review_text, legacy_records_sha256="f" * 64)
    manifest["initial_review_template_sha256"] = "f" * 64
    (directory / "manifest.json").write_bytes(assessment._json_bytes(manifest))
    with pytest.raises(ValueError, match="Original legacy review template"):
        summarize_files(directory, directory / "summary.json")
    assert not (directory / "summary.json").exists()


def test_legacy_review_cannot_be_reused_for_inventory_evidence(tmp_path, monkeypatch):
    directory, bundle, _ = legacy_bundle(tmp_path, monkeypatch)
    bundle["source"]["inventory_evidence"] = {"synthetic": "changed source context"}
    with pytest.raises(ValueError, match="original forecast-only records"):
        summarize_reviews(
            bundle,
            (directory / "review.json").read_text(),
            legacy_records_sha256=hashlib.sha256(
                assessment._json_bytes(bundle)
            ).hexdigest(),
        )


@pytest.mark.parametrize(
    "manifest_schema,review_schema",
    [
        (assessment.LEGACY_REVIEW_SCHEMA, assessment.REVIEW_SCHEMA),
        (assessment.REVIEW_SCHEMA, assessment.LEGACY_REVIEW_SCHEMA),
    ],
)
def test_manifest_and_review_schema_must_agree(
    tmp_path, monkeypatch, manifest_schema, review_schema
):
    directory, _, manifest = legacy_bundle(tmp_path, monkeypatch)
    manifest["review_schema"] = manifest_schema
    (directory / "manifest.json").write_bytes(assessment._json_bytes(manifest))
    review = json.loads((directory / "review.json").read_bytes())
    review["review_schema"] = review_schema
    (directory / "review.json").write_bytes(assessment._json_bytes(review))
    with pytest.raises(ValueError, match="schema differs"):
        summarize_files(directory, directory / "summary.json")
