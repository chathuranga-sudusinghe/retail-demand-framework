"""Four-fold summaries and descriptive primary leaders; no human freeze implied."""
from __future__ import annotations

from collections import defaultdict
from math import isfinite
from typing import Any

from src.forecasting.baselines import BASELINE_MODELS
from src.forecasting.configuration import PRIMARY_GRID, PRIMARY_MODELS, SUPPORTIVE_MODELS
from src.forecasting.metrics import four_fold_means
from src.forecasting.targets import FORECAST_HORIZONS

MODEL_ORDER = (*PRIMARY_MODELS, *SUPPORTIVE_MODELS, *BASELINE_MODELS)
ROLES = {m: "primary" for m in PRIMARY_MODELS} | {
    m: "supportive" for m in SUPPORTIVE_MODELS
} | {m: "simple_baseline" for m in BASELINE_MODELS}


def record_order(record: dict[str, Any]) -> tuple[Any, ...]:
    """Protocol stage/model/horizon/configuration/fold/pair order, not score order."""
    return (
        ("validation", "final_evaluation").index(record.get("evaluation_stage", "validation")),
        MODEL_ORDER.index(record["model"]), FORECAST_HORIZONS.index(record["horizon"]),
        record.get("configuration_id", ""), record.get("fold_id") or 5,
        record.get("SKU_ID", ""), record.get("Warehouse_ID", ""),
        record.get("exclusion_reason", ""),
    )


def summarize_configurations(folds: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Retain missing/invalid fold summaries, never rank a subset of folds."""
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    if len({r["run_id"] for r in folds}) > 1:
        raise ValueError("Evidence from different runs cannot be combined.")
    for record in folds:
        if record["evaluation_stage"] != "validation":
            raise ValueError("Final evidence cannot enter validation selection.")
        model = record["model"]
        if type(record["horizon"]) is not int or record["horizon"] not in FORECAST_HORIZONS:
            raise ValueError("Unapproved horizon in validation evidence.")
        if record["evidence_role"] != ROLES[model]:
            raise ValueError("Evidence role does not match the frozen model role.")
        expected_ids = {c.canonical_config_id for c in PRIMARY_GRID} if model in PRIMARY_MODELS else {
            "fixed" if model in SUPPORTIVE_MODELS else "not_tuned"
        }
        if record["configuration_id"] not in expected_ids or record["canonical_config_id"] != (
            record["configuration_id"] if model in PRIMARY_MODELS else None
        ):
            raise ValueError("Invalid configuration/canonical identity.")
        key = tuple(record[k] for k in ("run_id", "evaluation_stage", "evidence_role", "model",
                                       "horizon", "configuration_id", "canonical_config_id"))
        groups[key].append(record)
    result = []
    for key, records in groups.items():
        base = dict(zip(("run_id", "evaluation_stage", "evidence_role", "model", "horizon",
                         "configuration_id", "canonical_config_id"), key, strict=True))
        primary = base["evidence_role"] == "primary"
        result.append({**base, **four_fold_means(records),
                       "selected_configuration": False if primary else None,
                       "selection_status": "candidate" if primary else (
                           "fixed_supportive" if base["evidence_role"] == "supportive"
                           else "not_applicable"),
                       "review_status": "pending_human_review"})
    return sorted(result, key=record_order)


def select_primary(
    summaries: list[dict[str, Any]], candidate_records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[int, list[str]]]:
    """Exact WAPE ties only; all 24 complete configurations required per leader.

    Mutates summary selection flags for artifact generation. Supportive and
    baseline scores cannot affect either configuration leaders or model ties.
    No stability threshold, overall winner or scientific tie breaker is invented.
    """
    if len({r["run_id"] for r in summaries}) > 1:
        raise ValueError("Evidence from different runs cannot be combined.")
    selections = []
    best_by_horizon: dict[int, dict[str, float]] = defaultdict(dict)
    for model in PRIMARY_MODELS:
        for horizon in FORECAST_HORIZONS:
            rows = [r for r in summaries if r["model"] == model and r["horizon"] == horizon]
            if not rows:
                continue
            if any(r["evaluation_stage"] != "validation" or r["evidence_role"] != "primary" for r in rows):
                raise ValueError("Only primary validation summaries may enter RQ2 selection.")
            ids = [r["canonical_config_id"] for r in rows]
            complete = (len(ids) == 24 and set(ids) == {c.canonical_config_id for c in PRIMARY_GRID}
                        and all(r["metric_status"] == "valid" and r["valid_fold_count"] == 4
                                and r["expected_fold_count"] == 4 and r["mean_wape"] is not None
                                and isfinite(r["mean_wape"]) for r in rows))
            if not complete:
                continue  # No leader from an incomplete or undefined comparison.
            minimum = min(r["mean_wape"] for r in rows)
            tied = sorted(r["canonical_config_id"] for r in rows if r["mean_wape"] == minimum)
            representative = tied[0]
            configuration = next(c for c in PRIMARY_GRID if c.canonical_config_id == representative)
            for row in rows:
                if row["canonical_config_id"] in tied:
                    row["selected_configuration"] = True
                    row["selection_status"] = "validation_leader" if len(tied) == 1 else (
                        "tied_administrative_representative" if row["canonical_config_id"] == representative
                        else "tied_configuration")
            candidates = [r for r in candidate_records if r["model"] == model
                          and r["horizon"] == horizon and r["configuration_id"] == representative]
            candidates = sorted(candidates, key=record_order)
            selections.append({
                "model": model, "evidence_role": "primary", "horizon": horizon,
                "configuration_id": representative, "canonical_config_id": representative,
                "canonical_parameters": configuration.canonical_parameters,
                "requested_api_parameters": candidates[0]["requested_api_parameters"] if candidates else None,
                "effective_api_parameters": {str(r["fold_id"]): r["effective_api_parameters"] for r in candidates},
                "selection_status": "validation_leader" if len(tied) == 1 else "tied_administrative_representative",
                "tied_configuration_ids": tied if len(tied) > 1 else [],
                "administrative_representative_id": representative if len(tied) > 1 else None,
                "metric_references": {"artifact": "fold_metrics.csv", "model": model,
                                      "horizon": horizon, "configuration_ids": tied, "fold_ids": [1, 2, 3, 4]},
                "human_review_reference": None,
                "selection_rationale": "Lowest arithmetic four-fold WAPE; human supporting-metric and fold-stability review pending.",
                "freeze_reference": None,
                "review_status": "pending_human_review", "selected_configuration": True,
            })
            best_by_horizon[horizon][model] = minimum
    ties: dict[int, list[str]] = {}
    for horizon, scores in best_by_horizon.items():
        # Missing/unauthorised primary models cannot establish a three-model leader.
        if set(scores) != set(PRIMARY_MODELS):
            ties[horizon] = []
            continue
        minimum = min(scores.values())
        tied_models: list[str] = [m for m in PRIMARY_MODELS if scores[m] == minimum]
        ties[horizon] = tied_models if len(tied_models) > 1 else []
    for selection in selections:
        selection["tied_primary_models"] = ties.get(selection["horizon"], [])
    return selections, ties
