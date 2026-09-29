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
- Issue #66 records the owner-approved primary controlled comparison of XGBoost, LightGBM and CatBoost in [DR-013](decisions/DR-013-matched-gradient-boosting-comparison.md); Ridge/Random Forest are supportive references only. The [feature contract](forecasting-feature-engineering.md) retains its fourteen conceptual predictors, numerical definitions/order and complete 28-day history. Primary models share full one-hot SKU/warehouse inputs plus the twelve unscaled numerical predictors (67 columns under full training coverage). The matched primary grid searches learning rate, boosting iterations, maximum depth and row fraction; no extra feature or model-specific search dimension is approved.

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

Issue #62 is merged through PR #64 and implements the frozen features, targets, revised fold utilities and earlier preprocessing contract. Model/metrics/runner modules remain absent. The preprocessor supports only Ridge/Random Forest/native-categorical LightGBM; Issue #66 requires later common primary encoding and XGBoost/CatBoost interfaces/tests after design approval. No source/tests/dependencies change here. Model fitting, tuning, validation scoring, ablation and final evaluation remain **NOT authorised**. Every later run requires specific human authorisation under AGENTS.md.

[Issue #65](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/65) remains pending alignment with the revised Issue #66 research design. Its protocol remains **DRAFT FOR HUMAN APPROVAL — EXECUTION NOT AUTHORISED**. Protocol approval and experiment execution remain separately gated; Gate 1 is incomplete. Its prior draft must later be aligned, including artifact schemas and the runtime recipe, and its previous four unresolved items reassessed.

## Computational scope

The primary matched grid has 24 configurations per model × horizon. **24 × 3 primary models × 4 horizons × 4 folds = 1,152 planned primary validation fits**. These are planned workload counts, not executed results. The supportive Ridge Regression / Random Forest configuration policy remains unresolved and requires separate human approval. Historical 5/12 configuration grids are not automatically reused. Supportive fits and later final refits are excluded from 1,152.

Simple baselines remain untuned: 2 baseline roles × 3 currently defined horizons × 4 folds = 24 evaluations. Both 28-day definitions need explicit approval before a fourth horizon adds 8, giving 32 baseline evaluations. No baseline is silently removed or redefined.

**Earlier planning provenance:** the former Ridge/Random Forest/LightGBM search had 5/12/24 configurations, 41 configurations per horizon and 656 planned fits over four horizons/folds (492 for three horizons). DR-010 retains that superseded planning unchanged; those counts are not the current primary workload.

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
- Feature-review Options A/B/C and the earlier thirteen-column catalogue are superseded historical proposals. Issue #62 implemented the frozen conceptual features; its native LightGBM preprocessing is now an alignment gap for Issue #66, not an active primary representation alternative.
- DR-007/009/010 bodies retain earlier learned roles, single-boosting selection, unequal grids, representation and workload beneath explicit DR-013 supersession notices. Retained Naive/Seasonal Naive definitions and 28-day approval boundaries are still in force.
- Issue #62 source/tests preserve the accepted earlier model/representation contract; their native categorical references are intentional implementation evidence awaiting a separate alignment task.
- DR-001/002 and DR-003's explicitly historical body retain independent decision meanings; active data dictionaries, literature applicability and workflow summaries now link the frozen contract. Git/workflow governance remains unchanged. A 14-day supplier
  limit or rolling window is not an obsolete 14-day maximum forecast horizon.
