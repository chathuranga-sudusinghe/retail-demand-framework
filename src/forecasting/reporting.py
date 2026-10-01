"""Read-only Markdown rendering of persisted validation evidence, without scoring."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable

PRIMARY = ("xgboost", "lightgbm", "catboost")
NAMES = {"xgboost": "XGBoost", "lightgbm": "LightGBM", "catboost": "CatBoost",
         "ridge": "Ridge", "random_forest": "Random Forest", "naive": "Naive",
         "seasonal_naive": "Seasonal Naive"}


def _cell(value: Any) -> str:
    return "unavailable" if value is None or value == "" else str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def _table(columns: Iterable[str], rows: Iterable[Iterable[Any]]) -> list[str]:
    header = list(columns)
    return ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |",
            *("| " + " | ".join(_cell(value) for value in row) + " |" for row in rows), ""]


def comparison_text(directory: Path, *, require_verified: bool = True) -> str:
    """Render stored values/status/ties only; no means, differences or winners computed."""
    if require_verified:
        from src.forecasting.integrity import verify_completed
        verify_completed(directory)
    metadata = json.loads((directory / "run_metadata.json").read_text(encoding="utf-8"))
    selected = json.loads((directory / "selected_configurations.json").read_text(encoding="utf-8"))
    with (directory / "configuration_summary.csv").open(newline="", encoding="utf-8") as stream:
        summaries = list(csv.DictReader(stream))
    with (directory / "fold_metrics.csv").open(newline="", encoding="utf-8") as stream:
        folds = list(csv.DictReader(stream))
    scope = metadata["run_scope"]
    selections = {(str(s["horizon"]), s["model"]): s for s in selected["selections"]}
    by_configuration = {(r["horizon"], r["model"], r["configuration_id"]): r for r in summaries}
    fold_index = {(r["horizon"], r["model"], r["configuration_id"], r["fold_id"]): r for r in folds}

    def selected_summary(horizon: int, model: str) -> dict[str, str]:
        selection = selections.get((str(horizon), model))
        return by_configuration.get((str(horizon), model, selection["configuration_id"]), {}) if selection else {}

    def selected_id(horizon: int, model: str) -> str:
        selection = selections.get((str(horizon), model))
        if not selection:
            return "not authorised" if horizon not in scope["horizons"] or model not in scope["primary_models"] else "not selected"
        suffix = " (administrative tie representative)" if selection.get("tied_configuration_ids") else ""
        return str(selection["configuration_id"]) + suffix

    lines = ["# Validation comparison — pending human review", "", "## Run summary", "",
             f"- Run ID: {_cell(metadata['run_id'])}",
             f"- Protocol version: {_cell(metadata['protocol_version'])}",
             f"- Git commit SHA: {_cell(metadata.get('git_commit_sha'))}",
             f"- Evaluation stage: {_cell(metadata['evaluation_stage'])}",
             f"- Run status at rendering: {_cell(metadata['run_status'])}",
             "- Completion authority: [run manifest](run_manifest.json); metadata alone does not establish completion.",
             "- Validation folds: 1, 2, 3, 4 (frozen protocol plan).",
             "- Recorded fold IDs: " + (", ".join(sorted({r["fold_id"] for r in folds})) or "none; not executed"),
             "- Authorised horizons (days): " + ", ".join(map(str, scope["horizons"]))]
    for label, key in (("Primary", "primary_models"), ("Supportive", "supportive_models"), ("Baseline", "baselines")):
        lines.append(f"- {label} model roles: " + (", ".join(NAMES[m] for m in scope[key]) or "none authorised"))
    lines += [f"- Final-evaluation status: {_cell(metadata['final_evaluation_status'])}; blocked/not executed until separate Gate 6 authorisation.", ""]
    if metadata.get("failure_reason"):
        lines += [f"Failure: {_cell(metadata['failure_reason'])}", ""]
    lines += ["WAPE (Weighted Absolute Percentage Error) values are stored ratios. All displayed metrics are copied",
              "from the result artifacts; no metric, tie or selection is recalculated here.",
              "[Run metadata](run_metadata.json) · [Configuration summary](configuration_summary.csv) ·",
              "[Selected configurations](selected_configurations.json) · [Fold metrics](fold_metrics.csv) ·",
              "[Predictions](predictions.csv) · [Eligibility counts](eligibility_counts.csv)", "",
              "## Selected-configuration matrix", ""]
    lines += _table(("Horizon", "XGBoost", "LightGBM", "CatBoost"),
                    ([f"{h}-day", *(selected_id(h, m) for m in PRIMARY)] for h in (1, 7, 14, 28)))
    lines += ["## Primary WAPE comparison matrix", ""]
    lines += _table(("Horizon", "XGBoost WAPE", "LightGBM WAPE", "CatBoost WAPE"),
                    ([f"{h}-day", *(selected_summary(h, m).get("mean_wape") for m in PRIMARY)] for h in (1, 7, 14, 28)))
    lines += ["Matrices use the recorded selected configuration (administrative representative where tied).",
              "No cross-horizon overall winner is calculated. Canonical ordering implies no scientific superiority.", ""]

    columns = ("model", "evidence_role", "configuration_id", "canonical_config_id", "selection_status",
               "fold_count", "n_predictions", "mean_wape", "mean_mae", "mean_rmse", "mean_bias",
               "metric_status", "review_status", "artifact_paths")
    for horizon in (1, 7, 14, 28):
        lines += [f"## {horizon}-day", "", "### Primary model comparison", ""]
        for model in PRIMARY:
            lines.append(f"- Selected configuration — {NAMES[model]}: {selected_id(horizon, model)}.")
        lines += [""]
        for role, heading, models in (
            ("primary", None, PRIMARY),
            ("supportive", "Supportive comparison — Ridge and Random Forest", ("ridge", "random_forest")),
            ("simple_baseline", "Baseline comparison — Naive and Seasonal Naive", ("naive", "seasonal_naive")),
        ):
            if heading:
                lines += [f"### {heading}", ""]
            rendered = []
            for model in models:
                rows = [r for r in summaries if r["horizon"] == str(horizon) and r["model"] == model and r["evidence_role"] == role
                        and (role != "primary" or r["selected_configuration"] == "true")]
                if not rows:
                    authorised_models = scope[{"primary": "primary_models", "supportive": "supportive_models", "simple_baseline": "baselines"}[role]]
                    status = "not authorised" if horizon not in scope["horizons"] or model not in authorised_models else "not selected / unavailable"
                    rows = [{"model": model, "evidence_role": role, "selection_status": status, "metric_status": "unavailable",
                             "review_status": "pending_human_review"}]
                for row in rows:
                    record = {**row, "fold_count": row.get("valid_fold_count"),
                              "artifact_paths": "[summary](configuration_summary.csv); [folds](fold_metrics.csv); [predictions](predictions.csv)"}
                    rendered.append([record.get(column) for column in columns])
            lines += _table(columns, rendered)
            if role == "primary":
                lines += ["### Fold-level primary WAPE comparison", ""]
                fold_rows = []
                for fold_id in ("1", "2", "3", "4"):
                    values = []
                    for model in PRIMARY:
                        selection = selections.get((str(horizon), model), {})
                        record = fold_index.get((str(horizon), model, selection.get("configuration_id", ""), fold_id), {})
                        values.append(record.get("wape"))
                    fold_rows.append([fold_id, *values])
                lines += _table(("Fold", "XGBoost WAPE", "LightGBM WAPE", "CatBoost WAPE"), fold_rows)
                lines += ["All four stored fold metrics for every displayed configuration (including ties):", ""]
                displayed_keys = {(str(horizon), r["model"], r["configuration_id"]) for r in summaries
                                  if r["horizon"] == str(horizon) and r["evidence_role"] == "primary" and r["selected_configuration"] == "true"}
                lines += _table(("Model", "Configuration", "Fold", "WAPE", "MAE", "RMSE", "Bias", "Metric status"),
                                ([r["model"], r["configuration_id"], r["fold_id"], r["wape"], r["mae"], r["rmse"], r["bias"], r["metric_status"]]
                                 for r in folds if (r["horizon"], r["model"], r["configuration_id"]) in displayed_keys))
        lines += ["### Tie information", ""]
        model_ties = metadata.get("tied_primary_models", {}).get(str(horizon), [])
        lines += ["Primary model tie: " + (", ".join(NAMES[m] for m in model_ties) + "; no representative model is chosen." if model_ties else "none recorded."), ""]
        for model in PRIMARY:
            selection = selections.get((str(horizon), model), {})
            tied_ids = selection.get("tied_configuration_ids", [])
            lines += [f"- {NAMES[model]} configuration ties: " + (", ".join(tied_ids) +
                      f"; administrative representative: {selection.get('administrative_representative_id')}." if tied_ids else "none recorded." )]
        lines += ["", "### Limitations and status", "",
                  "Human selection/freeze remains pending; supportive and baseline evidence cannot establish a primary-model winner.",
                  "Human review should compare recorded error magnitudes, signed Bias and the direction/consistency of fold WAPE values.",
                  "Unavailable cells denote absent, unselected or undefined evidence; inspect CSV status/reason fields.",
                  "Selection unavailable unless all 24 complete four-fold configurations meet the existing selection rules.",
                  "Final evaluation remains blocked/not executed until separately authorised.", ""]
        if horizon not in scope["horizons"]:
            lines += ["This horizon was not authorised and was not executed.", ""]
        for model, reason in scope.get("baseline_exclusions", []):
            lines += [f"Baseline exclusion — {NAMES[model]}: {_cell(reason)}", ""]
    lines += ["## Shared limitations", "",
              "The dataset is simulated. Validation leaders are not frozen scientific conclusions.",
              "Supporting metrics and fold stability require human review; no significance test is produced.",
              "Overlapping training labels and shared training histories make folds dependent.",
              "December 3–16 had prior validation exposure; full-year EDA also inspected the final interval.",
              "Human selection/freeze and Gate 4/6 approval references must be reviewed in run_metadata.json.", ""]
    return "\n".join(lines)
