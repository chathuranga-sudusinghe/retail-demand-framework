"""Prepare the Issue #168 records and summarize a completed human checklist.

The CLI is for the human executor. It does not assess transparency, infer
inventory risk, or produce review outcomes automatically. Tests use synthetic
exports; project-evidence preparation and assessment are separate human runs.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from src.decision_support.records import DecisionSupportRecord
from src.forecasting.export import DESTINATION
from src.forecasting.paths import REPOSITORY
from src.inventory_risk.forecast_handoff import (
    MAPPING_VERSION,
    ForecastHandoff,
    load_forecast_handoff,
)
from src.inventory_risk.runner import (
    PROSPECTIVE_FIELDS,
    PROSPECTIVE_SCHEMA,
    PROVENANCE_SHA256,
    RUN_SCHEMA,
    validate_prospective_state,
)

CRITERIA = (
    "Forecast visibility",
    "Risk visibility",
    "Recommendation traceability",
    "Uncertainty visibility",
    "Assumption visibility",
    "Limitation visibility",
    "Human-review transparency",
    "Source distinction",
)
PAIRS = (
    ("SKU_1", "WH_1"),
    ("SKU_5", "WH_2"),
    ("SKU_10", "WH_3"),
    ("SKU_15", "WH_4"),
    ("SKU_20", "WH_5"),
)
REVIEW_FIELDS = (
    "assessment_id",
    "sku_id",
    "warehouse_id",
    "forecast_origin",
    "horizon",
    "criterion",
    "applicable",
    "outcome",
    "reason",
    "evidence",
    "assessor",
    "assessed_on",
)
REVIEW_SCHEMA = "issue-168-review-v2"
LEGACY_REVIEW_SCHEMA = "issue-168-review-v1"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode()


def load_inventory_evidence(path: Path, handoff: ForecastHandoff) -> dict[str, Any]:
    """Consume only sealed prospective evidence, never evaluation-only outputs."""
    path = _destination(path)
    _require(
        path.name == "prospective.json",
        "Supply the prospective.json inventory handoff.",
    )
    payload = path.read_bytes()
    manifest_payload = (path.parent / "manifest.json").read_bytes()
    manifest = _json_document(manifest_payload.decode("utf-8"))
    document = _json_document(payload.decode("utf-8"))
    _require(
        set(document) == {"schema", "source", "scope", "records"},
        "Unexpected inventory prospective envelope fields.",
    )
    digest = hashlib.sha256(payload).hexdigest()
    _require(
        manifest["schema"] == RUN_SCHEMA and manifest["files"][path.name] == digest,
        "Inventory manifest/file binding differs.",
    )
    _require(
        isinstance(manifest["files"], dict)
        and set(manifest["files"])
        == {"prospective.json", "evaluation.json", "report.md"},
        "Inventory manifest must bind all three expected output files.",
    )
    for name, expected_hash in manifest["files"].items():
        candidate = _destination(path.parent / name)
        candidate_bytes = payload if name == path.name else candidate.read_bytes()
        _require(
            hashlib.sha256(candidate_bytes).hexdigest() == expected_hash,
            f"Inventory manifest/file hash differs: {name}",
        )
    _require(
        manifest["dataset_provenance_sha256"] == PROVENANCE_SHA256,
        "Unexpected inventory dataset provenance.",
    )
    _require(
        document["schema"] == PROSPECTIVE_SCHEMA
        and document["source"] == manifest["source"],
        "Inventory prospective source differs.",
    )
    source = document["source"]
    _require(
        source["forecast_export_sha256"] == handoff.sha256
        and source["forecast_source"] == handoff.document["source"],
        "Inventory and forecast source bindings differ.",
    )
    _require(
        source["snapshot_policy"]
        in ("unknown", "source-confirmed", "constructed-origin")
        and isinstance(source["snapshot_basis"], str)
        and bool(source["snapshot_basis"].strip()),
        "Invalid inventory snapshot policy/basis.",
    )
    _require(
        isinstance(document["records"], list) and len(document["records"]) == 1000,
        "Inventory handoff must retain all 1000 forecast keys.",
    )
    forecasts = {
        (r["SKU_ID"], r["Warehouse_ID"], r["forecast_origin"], r["horizon"]): r
        for r in handoff.document["forecasts"]
    }
    indexed = {}
    for row in document["records"]:
        _require(
            isinstance(row, dict) and set(row) == set(PROSPECTIVE_FIELDS),
            "Inventory prospective fields differ; retrospective information is forbidden.",
        )
        _require(type(row["horizon"]) is int, "Invalid inventory horizon.")
        key = row["SKU_ID"], row["Warehouse_ID"], row["forecast_origin"], row["horizon"]
        _require(
            key in forecasts and key not in indexed,
            "Unknown or duplicate inventory key.",
        )
        _require(
            type(row["prediction"]) in (int, float),
            "Inventory forecast prediction must remain a JSON number.",
        )
        for name in (
            "prediction",
            "unit",
            "model",
            "configuration_id",
            "target_start_date",
            "target_end_date",
        ):
            _require(
                row[name] == forecasts[key][name],
                f"Inventory forecast identity/value changed: {name}",
            )
        _require(
            row["source_export_sha256"] == handoff.sha256,
            "Inventory row source differs.",
        )
        validate_prospective_state(row, source)
        indexed[key] = row
    return {
        "rows": indexed,
        "provenance": {
            "prospective_sha256": digest,
            "manifest_sha256": hashlib.sha256(manifest_payload).hexdigest(),
            "dataset_provenance_sha256": manifest["dataset_provenance_sha256"],
            "operator": manifest["operator"],
            "source": source,
        },
    }


def build_review_records(
    handoff: ForecastHandoff, inventory_evidence: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Map F01–F20 to existing records; missing inventory evidence stays explicit."""
    document = handoff.document
    indexed = {
        (row["SKU_ID"], row["Warehouse_ID"], row["horizon"]): row
        for row in document["forecasts"]
    }
    records: list[dict[str, Any]] = []
    for sku, warehouse in PAIRS:
        for horizon in (1, 7, 14, 28):
            key = sku, warehouse, horizon
            _require(key in indexed, f"Selected forecast key is missing: {key}")
            row = indexed[key]
            assessment_id = f"F{len(records) + 1:02d}"
            provenance = {
                "export_sha256": handoff.sha256,
                "export_schema": document["export_schema"],
                "source": document["source"],
                "SKU_ID": sku,
                "Warehouse_ID": warehouse,
                "forecast_origin": row["forecast_origin"],
                "horizon": horizon,
                "model": row["model"],
                "configuration_id": row["configuration_id"],
                "producer_status": row["producer_status"],
                "forecast_status": row["forecast_status"],
            }
            inventory_reason = (
                "28_day_downstream_use_requires_separate_approval; no reviewed inventory evidence linked."
                if horizon == 28
                else "pending upstream output; no reviewed inventory evidence linked for this forecast key."
            )
            inventory_risk = None
            inventory_provenance = None
            inventory_assumptions: list[str] = []
            inventory_limitations: list[str] = []
            if inventory_evidence is not None:
                inventory_key = sku, warehouse, row["forecast_origin"], horizon
                _require(
                    inventory_key in inventory_evidence["rows"],
                    f"Missing inventory key: {inventory_key}",
                )
                upstream = inventory_evidence["rows"][inventory_key]
                inventory_assumptions = list(upstream["method_assumptions"])
                inventory_limitations = list(upstream["method_limitations"])
                if horizon != 28 and upstream["analysis_inventory_state_available"]:
                    inventory_risk = {
                        name: upstream[name]
                        for name in (
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
                    }
                    inventory_provenance = json.dumps(
                        inventory_evidence["provenance"], sort_keys=True
                    )
                else:
                    inventory_reason = (
                        upstream["downstream_use_reason"]
                        if horizon == 28
                        else upstream["origin_snapshot_reason"]
                        or "inventory_snapshot_missing_or_invalid"
                    )
            limitations = [
                "Publisher-simulated Kaggle data; no demonstrated real-retailer effectiveness.",
                "Stockout_Flag is zero-variance and cannot validate stockout predictions.",
                "Limited purposive selection of 20 forecasts; not statistically representative.",
                "Replenishment evidence is not supplied; inventory exposure is linked from the hash-bound prospective handoff."
                if inventory_evidence is not None
                else "Inventory/replenishment evidence is not supplied by this preparation.",
                "The final interval had December 3–16 prior validation exposure and full-year exploratory exposure.",
                "Record contents alone do not establish visibility/readability in a rendered prototype.",
            ]
            if row["prediction"] < 0:
                limitations.append(
                    "Raw finite negative forecast retained; inventory-dependent use is unavailable without a separate handling decision."
                )
            if horizon == 28:
                limitations.append(
                    "28-day case is in forecast-transparency scope only; inventory interpretation and review triggers remain gated."
                )
            record = DecisionSupportRecord(
                sku_id=sku,
                warehouse_id=warehouse,
                forecast_origin=row["forecast_origin"],
                forecast_horizon=f"{horizon}-day",
                forecast_demand=row["prediction"],
                forecast_provenance=json.dumps(provenance, sort_keys=True),
                inventory_risk_evidence=inventory_risk,
                inventory_risk_provenance=inventory_provenance,
                assumptions=[
                    f"Target interval {row['target_start_date']} through {row['target_end_date']} is inclusive.",
                    "One day means next-day demand; 7/14/28 days mean cumulative-window demand, not a daily path.",
                    *inventory_assumptions,
                ],
                limitations=[*limitations, *inventory_limitations],
                evidence=[
                    f"Assessment ID: {assessment_id}",
                    f"Mapping version: {MAPPING_VERSION}",
                    json.dumps(
                        {
                            name: row[name]
                            for name in (
                                "target_start_date",
                                "target_end_date",
                                "horizon",
                                "forecast_type",
                                "unit",
                                "uncertainty",
                            )
                        },
                        sort_keys=True,
                    ),
                    f"Retained export SHA-256: {handoff.sha256}",
                    *(
                        [
                            f"Inventory prospective SHA-256: {inventory_evidence['provenance']['prospective_sha256']}"
                        ]
                        if inventory_evidence is not None
                        else []
                    ),
                ],
                management_consideration="Advisory information for human consideration; unavailable evidence is not an instruction to purchase or a no-risk finding.",
                unavailable_fields={
                    **(
                        {
                            "inventory_risk_evidence": inventory_reason,
                            "inventory_risk_provenance": inventory_reason,
                        }
                        if inventory_risk is None
                        else {}
                    ),
                    "replenishment_recommendation": "not produced; no approved numerical replenishment output supplied for this case.",
                    "uncertainty_or_error": "no_agreed_method; source forecast uncertainty is unavailable. Retrospective errors are excluded.",
                },
                component_provenance={
                    "forecast": "forecasting",
                    "decision_support": "responsible_decision_support",
                    **(
                        {"inventory_risk": "inventory_risk"}
                        if inventory_evidence is not None
                        else {}
                    ),
                },
            )
            records.append(
                {
                    "assessment_id": assessment_id,
                    "horizon": horizon,
                    "record": asdict(record),
                }
            )
    return {
        "mapping_version": MAPPING_VERSION,
        "source": {
            "export_sha256": handoff.sha256,
            "export_schema": document["export_schema"],
            **document["source"],
            **(
                {"inventory_evidence": inventory_evidence["provenance"]}
                if inventory_evidence is not None
                else {}
            ),
        },
        "scope": "20 purposive decision-support records; inventory evidence is conditional on its recorded snapshot basis; missing inventory/replenishment evidence remains explicit; h=28 downstream use gated"
        if inventory_evidence is not None
        else "20 purposive forecast-transparency records; missing inventory/replenishment evidence remains explicit; h=28 downstream use gated",
        "records": records,
    }


def review_template(bundle: dict[str, Any]) -> dict[str, Any]:
    """Return 160 unassessed JSON checks, with no preassigned outcomes."""
    checks = []
    for case in bundle["records"]:
        record = case["record"]
        for criterion in CRITERIA:
            checks.append(
                {
                    **dict.fromkeys(REVIEW_FIELDS, ""),
                    "assessment_id": case["assessment_id"],
                    "sku_id": record["sku_id"],
                    "warehouse_id": record["warehouse_id"],
                    "forecast_origin": record["forecast_origin"],
                    "horizon": case["horizon"],
                    "criterion": criterion,
                }
            )
    return {
        "review_schema": REVIEW_SCHEMA,
        "mapping_version": bundle["mapping_version"],
        "source_export_sha256": bundle["source"]["export_sha256"],
        "records_sha256": hashlib.sha256(_json_bytes(bundle)).hexdigest(),
        "checks": checks,
    }


def _legacy_review_template(bundle: dict[str, Any]) -> dict[str, Any]:
    template = review_template(bundle)
    template.pop("records_sha256")
    template["review_schema"] = LEGACY_REVIEW_SCHEMA
    return template


def records_markdown(bundle: dict[str, Any]) -> str:
    """Render the same populated records for reading alongside review.json."""
    lines = [
        "# Decision-support records — Issue #168",
        "",
        bundle["scope"],
        "",
        f"Source export SHA-256: `{bundle['source']['export_sha256']}`.",
        "",
        "These are prepared records, not completed transparency assessments. "
        "Enter the eight criterion outcomes per record in [review.json](review.json).",
        "",
        "Use applicability `yes` or `no`; for applicable checks use `met`, "
        "`not met` or `not assessable`. Supply evidence for met checks and reasons "
        "for other outcomes/non-applicability, plus the assessor and ISO date.",
    ]
    for case in bundle["records"]:
        # JSON fences preserve every value, including nulls and source reasons.
        rendered = _json_bytes(case).decode().rstrip()
        fence = "```"
        while fence in rendered:
            fence += "`"
        lines.extend(
            ["", f"## {case['assessment_id']}", "", f"{fence}json", rendered, fence]
        )
    return "\n".join(lines) + "\n"


def _json_document(text: str) -> dict[str, Any]:
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            _require(key not in result, f"Duplicate review JSON field: {key}")
            result[key] = value
        return result

    def reject_constant(value: str) -> None:
        raise ValueError(f"Invalid review JSON constant: {value}")

    document = json.loads(
        text, object_pairs_hook=unique_object, parse_constant=reject_constant
    )
    _require(isinstance(document, dict), "Review JSON must be an object.")
    return document


def summarize_reviews(
    bundle: dict[str, Any],
    review_text: str,
    *,
    legacy_records_sha256: str | None = None,
) -> dict[str, Any]:
    """Validate and count human-entered outcomes; pending reviews are rejected."""
    template = review_template(bundle)
    expected = {
        (row["assessment_id"], row["criterion"]): row for row in template["checks"]
    }
    review = _json_document(review_text)
    if review.get("review_schema") == LEGACY_REVIEW_SCHEMA:
        _require(
            legacy_records_sha256 is not None
            and legacy_records_sha256 == template["records_sha256"],
            "Legacy reviews require a verified original record-manifest binding.",
        )
        _require(
            "inventory_evidence" not in bundle["source"]
            and all(
                case["record"]["inventory_risk_evidence"] is None
                and case["record"]["inventory_risk_provenance"] is None
                for case in bundle["records"]
            ),
            "Legacy reviews support only the original forecast-only records.",
        )
        template = _legacy_review_template(bundle)
    _require(
        set(review) == set(template), "Review JSON fields differ from the template."
    )
    for name in (name for name in template if name != "checks"):
        _require(
            review[name] == template[name], f"Review source/version changed: {name}"
        )
    _require(isinstance(review["checks"], list), "Review checks must be a JSON array.")
    counts: dict[str, dict[str, Any]] = {
        criterion: {
            "applicable": 0,
            "not_applicable": 0,
            "met": 0,
            "not met": 0,
            "not assessable": 0,
        }
        for criterion in CRITERIA
    }
    seen = set()
    assessors = set()
    for row in review["checks"]:
        _require(
            isinstance(row, dict)
            and set(row) == set(REVIEW_FIELDS)
            and type(row["horizon"]) is int
            and all(
                isinstance(row[name], str)
                for name in REVIEW_FIELDS
                if name != "horizon"
            ),
            "Malformed review JSON check.",
        )
        key = row["assessment_id"], row["criterion"]
        _require(
            key in expected and key not in seen,
            f"Unknown or duplicate review key: {key}",
        )
        seen.add(key)
        for name in ("sku_id", "warehouse_id", "forecast_origin", "horizon"):
            _require(
                row[name] == expected[key][name],
                f"Review identity changed: {key}, {name}",
            )
        _require(row["assessor"].strip() != "", f"Missing assessor: {key}")
        _require(
            date.fromisoformat(row["assessed_on"]).isoformat() == row["assessed_on"],
            f"Invalid assessment date: {key}",
        )
        assessors.add(row["assessor"])
        _require(
            row["applicable"] in ("yes", "no"),
            f"Assessment still pending or invalid applicability: {key}",
        )
        counter = counts[row["criterion"]]
        if row["applicable"] == "no":
            _require(
                row["outcome"] == "" and bool(row["reason"].strip()),
                f"Non-applicable check needs a reason and no outcome: {key}",
            )
            counter["not_applicable"] += 1
            continue
        outcome = row["outcome"]
        _require(
            outcome in ("met", "not met", "not assessable"),
            f"Assessment outcome still pending or invalid: {key}",
        )
        if outcome == "met":
            _require(
                bool(row["evidence"].strip()),
                f"Met outcome needs an evidence reference: {key}",
            )
        else:
            _require(
                bool(row["reason"].strip()),
                f"Unmet/unassessable check needs a reason: {key}",
            )
        counter["applicable"] += 1
        counter[outcome] += 1
    _require(
        seen == set(expected), "Review JSON does not cover every record/criterion."
    )
    for counter in counts.values():
        denominator = counter["applicable"]
        counter["met_proportion"] = (
            counter["met"] / denominator if denominator else None
        )
    return {
        "review_schema": review["review_schema"],
        "mapping_version": bundle["mapping_version"],
        "source": bundle["source"],
        "selected_forecasts": len(bundle["records"]),
        "prepared_records": len(bundle["records"]),
        "reviewed_records": len(bundle["records"]),
        "reviewed_check_rows": len(seen),
        "assessors": sorted(assessors),
        "criteria": counts,
        "proportion_denominator": "All applicable checks, including not assessable; non-applicable checks excluded.",
        "interpretation": "Counts of human-entered record-level assessments, not automated assessment, prototype acceptance or proven business effectiveness.",
    }


def summary_markdown(summary: dict[str, Any]) -> str:
    """Render the validated counts with the same denominator as summary.json."""
    lines = [
        "# Decision-support assessment — Issue #168",
        "",
        f"Selected forecasts: {summary['selected_forecasts']}. "
        f"Prepared records: {summary['prepared_records']}. "
        f"Reviewed records: {summary['reviewed_records']}. "
        f"Reviewed checks: {summary['reviewed_check_rows']}.",
        "",
        f"Source export SHA-256: `{summary['source']['export_sha256']}`.",
        "",
        "| Criterion | Applicable | Not applicable | Met | Not met | Not assessable | Met proportion |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for criterion, counter in summary["criteria"].items():
        proportion = counter["met_proportion"]
        displayed = (
            "N/A (zero applicable checks)"
            if proportion is None
            else f"{proportion:.4f}"
        )
        lines.append(
            f"| {criterion} | {counter['applicable']} | {counter['not_applicable']} "
            f"| {counter['met']} | {counter['not met']} | {counter['not assessable']} | {displayed} |"
        )
    lines.extend(
        [
            "",
            f"Proportion denominator: {summary['proportion_denominator']}",
            "",
            summary["interpretation"],
            "",
            "Record SHA-256: `" + summary["records_sha256"] + "`.",
            "",
            "Human assessment JSON SHA-256: `" + summary["review_sha256"] + "`.",
            "",
            "Case-specific outcomes, evidence, reasons, assessors and dates are retained "
            "in the source review.json bound by the hash above. The source records.json "
            "retains the forecast provenance, assumptions and limitations.",
        ]
    )
    return "\n".join(lines) + "\n"


def _destination(path: Path) -> Path:
    destination = path.resolve()
    root = (REPOSITORY / "research-materials").resolve()
    _require(
        destination != root and destination.is_relative_to(root),
        "Generated assessment files must stay inside ignored research-materials/.",
    )
    return destination


def prepare_files(
    handoff: ForecastHandoff,
    destination: Path,
    operator: str,
    inventory_evidence: dict[str, Any] | None = None,
) -> None:
    """Publish a new local-only preparation directory; never overwrite evidence."""
    _require(bool(operator.strip()), "A human operator is required.")
    destination = _destination(destination)
    bundle = build_review_records(handoff, inventory_evidence)
    records = _json_bytes(bundle)
    markdown = records_markdown(bundle).encode()
    template = _json_bytes(review_template(bundle))
    manifest = {
        "mapping_version": MAPPING_VERSION,
        "operator": operator,
        "prepared_at": datetime.now(timezone.utc).isoformat(),
        "records_sha256": hashlib.sha256(records).hexdigest(),
        "records_markdown_sha256": hashlib.sha256(markdown).hexdigest(),
        "review_schema": REVIEW_SCHEMA,
        "initial_review_template_sha256": hashlib.sha256(template).hexdigest(),
        "source_export_sha256": handoff.sha256,
        "code_sha256": {
            name: hashlib.sha256(
                (Path(__file__).resolve().parents[2] / name).read_bytes()
            ).hexdigest()
            for name in (
                "src/decision_support/assessment.py",
                "src/inventory_risk/forecast_handoff.py",
                "src/decision_support/records.py",
            )
        },
        "assessment_status": "not performed; review.json contains blank human-entered fields",
    }
    destination.mkdir(parents=True, exist_ok=False)
    for name, payload in (
        ("records.json", records),
        ("records.md", markdown),
        ("review.json", template),
        ("manifest.json", _json_bytes(manifest)),
    ):
        with (destination / name).open("xb") as stream:
            stream.write(payload)


def summarize_files(directory: Path, report_path: Path) -> None:
    """Bind a completed human JSON checklist to records; write JSON and Markdown."""
    directory = _destination(directory)
    report_path = _destination(report_path)
    _require(
        report_path.suffix == ".json", "The summary report path must end in .json."
    )
    markdown_path = report_path.with_suffix(".md")
    for target in (report_path, markdown_path):
        if target.exists():
            raise FileExistsError(f"Report already exists: {target}")
    manifest = _json_document((directory / "manifest.json").read_text())
    payload = (directory / "records.json").read_bytes()
    _require(
        hashlib.sha256(payload).hexdigest() == manifest["records_sha256"],
        "Prepared records changed after publication.",
    )
    _require(
        manifest.get("review_schema") in (LEGACY_REVIEW_SCHEMA, REVIEW_SCHEMA),
        "Unsupported review bundle schema.",
    )
    _require(
        hashlib.sha256((directory / "records.md").read_bytes()).hexdigest()
        == manifest["records_markdown_sha256"],
        "Readable records changed after publication.",
    )
    bundle = json.loads(payload)
    _require(
        bundle["source"]["export_sha256"] == manifest["source_export_sha256"],
        "Prepared source binding differs.",
    )
    if manifest["review_schema"] == LEGACY_REVIEW_SCHEMA:
        _require(
            hashlib.sha256(_json_bytes(_legacy_review_template(bundle))).hexdigest()
            == manifest["initial_review_template_sha256"],
            "Original legacy review template differs from its preparation manifest.",
        )
    review = (directory / "review.json").read_bytes()
    review_text = review.decode("utf-8-sig")
    _require(
        _json_document(review_text).get("review_schema") == manifest["review_schema"],
        "Review schema differs from its original preparation manifest.",
    )
    summary = summarize_reviews(
        bundle,
        review_text,
        legacy_records_sha256=manifest["records_sha256"]
        if manifest["review_schema"] == LEGACY_REVIEW_SCHEMA
        else None,
    )
    summary["records_sha256"] = manifest["records_sha256"]
    summary["review_sha256"] = hashlib.sha256(review).hexdigest()
    summary["preparation_code_sha256"] = manifest["code_sha256"]
    summary["prepared_at"] = manifest["prepared_at"]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("xb") as stream:
        stream.write(_json_bytes(summary))
    with markdown_path.open("xb") as stream:
        stream.write(summary_markdown(summary).encode())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser(
        "prepare", help="Human-run record preparation; no assessment outcomes assigned."
    )
    prepare.add_argument("--export", type=Path, default=REPOSITORY / DESTINATION)
    prepare.add_argument("--output", type=Path, required=True)
    prepare.add_argument("--operator", required=True)
    prepare.add_argument(
        "--inventory-evidence",
        type=Path,
        help="Optional hash-bound prospective.json from the inventory runner.",
    )
    summarize = commands.add_parser(
        "summarize", help="Count a completed human assessment; reject pending rows."
    )
    summarize.add_argument("--directory", type=Path, required=True)
    summarize.add_argument(
        "--report",
        type=Path,
        required=True,
        help="Summary .json path; a matching .md report is also written.",
    )
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            handoff = load_forecast_handoff(args.export)
            inventory = (
                load_inventory_evidence(args.inventory_evidence, handoff)
                if args.inventory_evidence
                else None
            )
            prepare_files(handoff, args.output, args.operator, inventory)
            print(
                f"Prepared records.json, records.md, blank review.json and manifest.json in {args.output}; assessment not performed."
            )
        else:
            summarize_files(args.directory, args.report)
            print(
                f"Wrote human-assessment summaries to {args.report} and {args.report.with_suffix('.md')}."
            )
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"Decision-support assessment failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
