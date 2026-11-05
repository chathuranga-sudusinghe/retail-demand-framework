"""Prepare display projections of retained results; never run research producers.

The additional hashes pin existing evidence, not human acceptance. The original
inventory loader remains the authority for its export and manifest contracts.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
from pathlib import Path
from typing import Any

from src.visualization.inventory_views import (
    IDENTITY_FIELDS,
    InventoryViewEvidence,
    InventoryViewSourceError,
    _json_document,
    build_availability_provenance,
    build_exposure_coverage,
    build_proxy_crossing_comparison,
    load_inventory_view_evidence,
)

WORKED_PATH = Path("research-materials/issue-214/worked-scenario-v1.json")
SUMMARY_PATH = Path("reports/decision-support/issue-168-inventory-v1/summary.json")
COMPARISON_PATH = Path("reports/forecasting/final-20261003-02/comparison.md")
SOURCE_HASHES = {
    WORKED_PATH: "c79c8a51debe0012048a341e71c76841c21f1065c0f2fdf62b81926c2dc584fb",
    SUMMARY_PATH: "6c3ba9308455c6df1de10f68b1afd8227797231738f490865fca14b99a9b8f5d",
    COMPARISON_PATH: "884edba6572bee6460750b86465ffd6e3d5276ac6ac9c395069eee1e45f44e4b",
}
MODELS = (
    "xgboost",
    "lightgbm",
    "catboost",
    "ridge",
    "random_forest",
    "naive",
    "seasonal_naive",
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


@dataclass(frozen=True)
class FigureEvidence:
    """One figure's purpose, full-precision data and explanatory caption."""

    name: str
    title: str
    purpose: str
    caption: str
    data: dict[str, Any]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise InventoryViewSourceError(message)


def _key(row: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(row[name] for name in IDENTITY_FIELDS)


def parse_final_comparison(text: str) -> list[dict[str, Any]]:
    """Read all 28 existing rows, retaining roles/configurations and all metrics."""
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 9 or cells[0] not in {
            "primary",
            "supportive",
            "simple_baseline",
        }:
            continue
        role, model, horizon, config, *metrics, status = cells
        _require(model in MODELS and status == "valid", "Invalid final comparison row.")
        values = dict(
            zip(("WAPE", "MAE", "RMSE", "Bias"), map(float, metrics), strict=True)
        )
        _require(
            all(math.isfinite(v) for v in values.values()), "Non-finite final metric."
        )
        rows.append(
            {
                "role": role,
                "model": model,
                "horizon": int(horizon),
                "configuration_id": config,
                "status": status,
                **values,
            }
        )
    expected = {(model, h) for model in MODELS for h in (1, 7, 14, 28)}
    _require(
        len(rows) == 28 and {(r["model"], r["horizon"]) for r in rows} == expected,
        "Final comparison must contain all 28 unique model/horizon rows.",
    )
    _require(all(r["WAPE"] >= 0 for r in rows), "Negative WAPE is invalid.")
    return rows


def build_figure_evidence(
    inventory: InventoryViewEvidence,
    trace: dict[str, Any],
    assessment: dict[str, Any],
    comparison: list[dict[str, Any]],
) -> tuple[FigureEvidence, ...]:
    """Join retained records for display only, without recalculating metrics."""
    forecast_hash = inventory.manifest["source"]["forecast_export_sha256"]
    _require(
        trace.get("schema") == "issue-214-worked-scenario-v1", "Unknown worked trace."
    )
    _require(
        trace["sources"]["forecast_export_sha256"] == forecast_hash,
        "Worked trace uses a different forecast export.",
    )
    _require(
        assessment["source"]["export_sha256"] == forecast_hash,
        "Assessment uses a different forecast export.",
    )
    _require(
        set(assessment["criteria"]) == set(CRITERIA), "Unexpected assessment criteria."
    )
    for counts in assessment["criteria"].values():
        fields = ("applicable", "not_applicable", "met", "not met", "not assessable")
        _require(
            all(type(counts[k]) is int and counts[k] >= 0 for k in fields),
            "Assessment counts must be nonnegative integers.",
        )
        _require(
            counts["met"] + counts["not met"] + counts["not assessable"]
            == counts["applicable"],
            "Assessment outcome counts do not reconcile.",
        )
        _require(
            counts["applicable"] + counts["not_applicable"]
            == assessment["reviewed_records"],
            "Assessment record denominator differs.",
        )

    cases = {_key(r): r for r in inventory.evaluation["cases"]}
    prospective = {_key(r): r for r in inventory.prospective["records"]}
    results = trace["forecast_results"]
    _require(
        len(results) == 4 and {r["horizon"] for r in results} == {1, 7, 14, 28},
        "Worked trace needs four unique horizons.",
    )
    observations = trace["retrospective_comparison"]["rows"]
    _require(
        len(observations) == 4
        and {r["horizon"] for r in observations} == {1, 7, 14, 28},
        "Worked observations need four unique horizons.",
    )
    observed = {r["horizon"]: r for r in observations}
    worked = []
    pair_keys = set()
    for result in sorted(results, key=lambda r: r["horizon"]):
        row = result["retained_case"]["prospective_record"]
        pair_keys.add((row["SKU_ID"], row["Warehouse_ID"], row["forecast_origin"]))
        key = _key(row)
        h = result["horizon"]
        _require(key in prospective, "Worked prospective record is missing.")
        expected = prospective[key]
        if h == 28:
            # The trace intentionally retains only the gated h28 projection.
            expected = {k: expected[k] for k in row if k in expected}
        _require(row == expected, "Worked prospective record differs.")
        obs = observed[h]
        api = result["api_response"]
        _require(h == row["horizon"] == api["horizon"], "Worked horizons differ.")
        _require(
            row["prediction"] == obs["forecast_quantity"] == api["forecast_quantity"],
            "Worked forecast quantities differ.",
        )
        for field in ("target_start_date", "target_end_date"):
            _require(
                row[field] == obs[field] == api[field], "Worked target windows differ."
            )
        evaluation = cases.get(key)
        if h != 28:
            _require(evaluation is not None, "Worked inventory case is missing.")
            assert evaluation is not None
            _require(
                evaluation["observed_target"] == obs["actual_units_sold"],
                "Worked actuals differ from retained evaluation.",
            )
        worked.append(
            {
                "prospective": row,
                "evaluation_only": evaluation,
                "observations_evaluation_only": obs,
            }
        )
    _require(len(pair_keys) == 1, "Worked horizons must describe one pair and origin.")

    producers = {
        (r["model"], r["configuration_id"], r["horizon"]) for r in inventory.forecasts
    }
    comparison = [
        {
            **r,
            "designated_producer": (r["model"], r["configuration_id"], r["horizon"])
            in producers,
        }
        for r in comparison
    ]
    origin = worked[0]["prospective"]["forecast_origin"]
    context = {"forecast_origin": origin, "historical_source_labels_unchanged": True}
    coverage = build_exposure_coverage(inventory)
    proxy = build_proxy_crossing_comparison(inventory)
    availability = build_availability_provenance(inventory)
    case_fields = (
        *IDENTITY_FIELDS,
        "target_start_date",
        "target_end_date",
        "model",
        "configuration_id",
        "comparison_case",
        "confusion_cell",
        "predicted_margin",
        "retrospective_margin",
        "evaluation_unavailable_reasons",
    )
    case_index = [
        {
            **{k: row[k] for k in case_fields},
            "source_pointer": f"reports/inventory-risk/issue-164/evaluation-v1/evaluation.json#/cases/{i}",
        }
        for i, row in enumerate(inventory.evaluation["cases"])
    ]
    return (
        FigureEvidence(
            "fig01_coverage_eligibility",
            "Analysis coverage and eligibility",
            "Identify the forecast and paired evaluation populations separately.",
            "Coverage at the retained origin. Scenario-at/below cases are outside the paired comparison; h28 forecasts have no inventory evaluation.",
            {
                **context,
                "horizon_population": coverage["horizon_population"],
                "evaluation_only": {"summary": coverage["evaluation_only"]["summary"]},
            },
        ),
        FigureEvidence(
            "fig02_proxy_crossings",
            "Forecast versus retrospective proxy crossings",
            "Explain crossing detections, missed events and denominator-defined rates.",
            "Retained confusion counts and rates, separately by horizon. High agreement can coexist with missed proxy events; these are not observed stockouts.",
            {**context, "summaries": proxy["summaries"], "label": proxy["label"]},
        ),
        FigureEvidence(
            "fig03_population_margins",
            "Predicted and retrospective scenario margins",
            "Locate retained paired margins relative to the zero reorder reference.",
            "Each mark is one eligible SKU-warehouse case, with identity in the accompanying case index. Zero is the reorder reference, not a physical-stock boundary.",
            {
                **context,
                "evaluation_only_cases": case_index,
                "summary": inventory.evaluation["summary"],
                "worked_identity": list(next(iter(pair_keys))),
            },
        ),
        FigureEvidence(
            "fig04_worked_forecast",
            "Worked case: forecast and actual sales",
            "Explain retained demand outputs and underprediction for the existing illustrative case.",
            "One illustrative, purposively sourced pair; not representative. Actual sales are retrospective. Overlapping cumulative windows are not additive.",
            {**context, "worked": worked, "trace_selection": trace["selection"]},
        ),
        FigureEvidence(
            "fig05_worked_margins",
            "Worked case: inventory interpretation",
            "Explain how the h14 forecast misses a retained scenario proxy crossing.",
            "Predicted and retrospective margins for the same illustrative case. Negative margin is arithmetic scenario exposure, not observed stockout or physical negative inventory.",
            {**context, "worked": worked},
        ),
        FigureEvidence(
            "fig06_evidence_status",
            "Evidence availability and approval context",
            "Distinguish evidence presence, method approval, unknown timing and deferred methods.",
            "Method approval does not establish source timing, consumer acceptance or operating benefit. Historical proposed labels are preserved as source metadata.",
            {
                **context,
                "current_method_approval": availability["current_method_approval"],
                "source": availability["source"],
                "dataset_provenance_sha256": availability["dataset_provenance_sha256"],
                "historical_methodology_labels": sorted(
                    {r["methodology_status"] for r in inventory.evaluation["cases"]}
                ),
            },
        ),
        FigureEvidence(
            "fig07_transparency_checks",
            "Responsible decision-support transparency checks",
            "Show existing human-entered criterion outcomes and unassessable methods.",
            "Twenty purposively selected records, eight checks each. Not assessable is distinct from not met; record transparency is not usability or decision quality.",
            {**context, "assessment": assessment},
        ),
        FigureEvidence(
            "fig08_forecasting_comparison",
            "Final-origin forecasting comparison",
            "Compare every frozen primary, supportive and baseline candidate by horizon.",
            "Retained final-origin WAPE; lower is better. All seven models are included. Designation was frozen before final results and is not a final-performance ranking.",
            {**context, "comparison": comparison},
        ),
    )


def load_figure_evidence(repository: Path) -> tuple[FigureEvidence, ...]:
    """Read pinned retained files only; reject mismatches rather than regenerate."""
    inventory = load_inventory_view_evidence(repository)
    payloads = {}
    for path, expected in SOURCE_HASHES.items():
        payload = (repository / path).read_bytes()
        _require(
            hashlib.sha256(payload).hexdigest() == expected,
            f"Figure source hash differs: {path}",
        )
        payloads[path] = payload
    return build_figure_evidence(
        inventory,
        _json_document(payloads[WORKED_PATH], "worked trace"),
        _json_document(payloads[SUMMARY_PATH], "assessment summary"),
        parse_final_comparison(payloads[COMPARISON_PATH].decode("utf-8")),
    )
