# Forecasting methodology revision — current approval and provenance

## Authority and scope

This records the horizon/validation revision supplied by the project owner on
2026-09-28 and the current human-approved forecasting position and feature freeze
aligned on 2026-09-29. Approval comes from the owner's explicit instructions, not AI-generated text. No separate supervisor or additional group approval is asserted.
The earlier September 22–23 decisions remain part of the methodological history.
No previous model scores were used to choose or justify this revision.

## Current human-approved forecasting design

- One-year simulated data at `SKU_ID + Warehouse_ID + Date`, using `Units_Sold`.
- Direct forecasts from the same fixed origin: next-day demand and cumulative
  demand over 7, 14 and 28 days. 28 days means four weeks / approximately monthly
  planning, not an exact calendar month and not a supplier lead-time estimate.
- Four expanding-window validation folds, each containing 28 complete days;
  one origin at each training cutoff, with no within-window updating.
- Training starts January 1, 2024 in every fold. See revised DR-005 for dates.
- Existing horizon-specific WAPE selection and supporting MAE, RMSE and Bias;
  arithmetic means across four folds, with no averaging across horizons.
- Existing model families and bounded hyperparameter grids remain unchanged.
  The [authoritative feature contract](forecasting-feature-engineering.md) freezes two categorical context and twelve numerical engineered predictors, fourteen conceptual predictors in the same order for all models/horizons, with 28 complete consecutive history days. Ridge/Random Forest use 67 physical columns; LightGBM uses 14 inputs, preserving equivalent underlying information. No search dimension or extra feature is approved.

Three folds were feasible: April high demand, July decline and October low demand.
Four folds were preferred because November–early December adds recovery evidence:
**Four folds provide broader validation evidence across distinct observed temporal
demand conditions while preserving expanding-window chronological evaluation.**
Four is project-specific, not statistically optimal. Folds share training history
and are not independent replicates. More folds increase workload and validation
selection exposure; they do not make models learn from validation outcomes.

## Revised final evaluation and prior exposure

The revised final evaluation window is **2024-12-03 to 2024-12-30**, 28 days,
with forecast origin December 2. It is reserved from all subsequent feature,
model and hyperparameter decisions and fitting. However, **December 3–16 had
prior validation exposure under the earlier 14-day methodology**, so the revised
window is not fully unseen from the historical research process. Full-year EDA
also previously inspected these dates. Prior exposure cannot be undone by changing
boundaries. Final results must disclose it and cannot independently establish
performance across the year or real-retailer effectiveness.

## Historical evidence

The earlier design used 1/7/14-day targets, April 1–14, July 1–14, October 1–14
and December 3–16 validation, and December 17–30 final evaluation. Earlier Issue
#52 protocol, feature snapshot and results describe that design only. They are
not the official baseline for the redesigned study and must not be relabelled.
The EDA notebook, reports and analysis source retain their historical wording beneath local provenance notices; no descriptive result is regenerated.

## Approval and execution boundaries

The final ordered features, formulas, categorical representation and common horizon/model policy are **frozen for feature/preprocessing implementation**. Date/Units_Sold have construction/alignment/target roles; the eleven other raw fields are excluded forecasting inputs but may retain wider project roles. Earlier Options A/B/C and the twelve-only intermediate contract are superseded provenance.

The following remain separate:

- explicit approval of proposed 28-day Naive and Seasonal Naive formulas in DR-007;
- implementation/test acceptance and a revised executable experiment protocol;
- DR-012 group approval and **component-owner/human approval for 28-day downstream use**;
- uncertainty, human-review rules, numerical replenishment and final integration contracts.

Current source still implements the historical feature catalogue; no current model/experiment/evaluation/metrics source modules are present. Their replacement is future implementation work, not authorised experiment execution. Model fitting, tuning, validation scoring, ablation and final evaluation remain **NOT authorised**. Every later run requires specific human authorisation under AGENTS.md. No experiment or test was run for this documentation alignment.

## Computational scope

Unchanged grids contain 41 learned configurations per horizon: 5 Ridge, 12 Random
Forest and 24 LightGBM. Four horizons × four folds gives **656 learned fits**;
fixed baselines would add **32 evaluations** after 28-day baseline approval.
These are planned counts, not executed results. Three folds × four horizons would
require 492 learned fits and 24 baseline evaluations but omit recovery validation.

## Audit classification of intentionally retained references

- `notebooks/eda/demand_eda.ipynb`, `reports/demand-eda.md`,
  `reports/temporal-demand-profile.md` and `src/data/demand_eda.py` retain the
  historical exploratory context, including then-approved 1/7/14 horizons and
  then-proposed untouched-test wording. They are not instructions for the revised
  final evaluation. No notebook, raw data or descriptive result was regenerated.
- DR-005 retains the exact superseded fold table and December 17–30 holdout wording
  in its explicitly historical section; DR-004/007/010 retain original scope/counts
  where labelled as provenance. DR-007's 1/7/14 baseline definitions remain valid.
- The archived [Issue #52 protocol](issue-52-forecasting-protocol.md) and ignored local `outputs/issue-52-validation/comparison.md` preserve their original bodies beneath historical notices. Its metadata, candidate metrics, selected configurations/predictions, eligibility records and artifact audit belong to that earlier run, not the revised study. No historical score selects the current feature contract or model.
- There is no tracked Issue #52 comparison report under `reports/`, and the historical reproduction command references absent `src/forecasting/experiment.py`. The run metadata records Git HEAD `ec1296ecebeae359222036c93b4dd482fe977e23` and source fingerprints; reproducing it would require the matching historical source snapshot and separate authorisation. Compiled caches are not that source archive.
- Feature-review Options A/B/C are superseded historical proposals. The old thirteen-column source catalogue remains an implementation gap until the frozen feature pipeline is implemented; it is not an active research alternative.
- DR-001/002 and DR-003's explicitly historical body retain independent decision meanings; active data dictionaries, literature applicability and workflow summaries now link the frozen contract. Git/workflow governance remains unchanged. A 14-day supplier
  limit or rolling window is not an obsolete 14-day maximum forecast horizon.
