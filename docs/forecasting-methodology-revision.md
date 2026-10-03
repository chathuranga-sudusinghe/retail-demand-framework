# Forecasting methodology revision — current approval and provenance

Repository-wide authorities: [data lifecycle](workflows/shared-data-foundation.md), [storage and retention](artifact-storage-policy.md), [applied MLOps](workflows/applied-mlops.md), [research reporting](../reports/README.md), and [continuous progress log](research-progress.md). These connect existing scientific/component contracts without replacing them.

> **Current forecasting status — 2026-10-03 / Issue #131:** Retained validation evidence is `validation-20261002-01`. [DR-014](decisions/DR-014-forecasting-selection-and-final-refit.md) records the approved scientific freeze/refit policy. Phase 1 runtime is merged in [PR #133](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/133) and explicitly accepted by the owner under Issue #131. Historical-only preflight completed successfully on 2026-10-03: `READY FOR AUTHORIZATION PREPARATION`. The real `final-20261003-01` execution revealed reserved outcomes and failed during final replay verification. PR #141 fixed the verified implementation defect. The owner explicitly authorized `final-20261003-02` as a defect-correction rerun with the same frozen 28 evaluations and producer mapping; it has not been executed. The original failed bundle remains preserved. Source/Git hashes are provenance only; scientific bindings, explicit specific-run approval and overwrite protection remain enforced. Result-driven retries, search, retuning, reselection and candidate substitution remain prohibited.

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

- completed historical-only preflight versus exact specific-run authorization; the owner has now explicitly authorized corrected run `final-20261003-02` under Issue #131;
- implementation-readiness acceptance, already established for merged PR #133, versus permission to create a real final authorization record or execute final evaluation;
- DR-012 group approval and **component-owner/human approval for 28-day downstream use**;
- uncertainty, human-review rules, numerical replenishment and final integration contracts.

Issue #62/PR #64 supplied the earlier features, targets, folds and preprocessing. Later primary alignment and PR #76 supplied common one-hot representations, models, metrics and the runner. Issue #89 extended operational orchestration and was merged through PR #90. That acceptance does not implement Issues #92/#93 storage boundaries or authorize a new run.

Issue #65 now has a human-approved/frozen protocol. Supportive settings, 28-day baseline formulas and numeric runtime controls are resolved there. Protocol approval, implementation acceptance and specific-run authorization are separate controls. Implementation acceptance for PR #133 is now established; historical-only preflight completed successfully on 2026-10-03 with outcome `READY FOR AUTHORIZATION PREPARATION`. The owner has subsequently explicitly authorized `final-20261003-02` as a defect-correction rerun; implementation identities are provenance only and scientific safeguards remain enforced.

## Historical validation provenance — Issue #94

The project owner's Issue #94 instruction confirms that a real forecasting validation
run has occurred; active documentation must not describe the repository as never run.
The local record inspected for that Issue #94 alignment,
`data/processed/forecasting/validation_authorization.json`,
identified `validation-20261001-01`, validation-only scope, implementation acceptance
reference PR #90 and specific owner authorization dated 2026-10-01. PR #90 is merged.
The authorization record is permission/provenance, not proof of completed execution.

The former generated directory was intentionally removed. At that Issue #94
inspection, this checkout had no corresponding completion manifest,
metric/prediction tables or model bundle available
for independent verification; no archive, score, reviewed result or selection freeze
is inferred. Locating retained original evidence and confirming completion/review are
human follow-up requirements before a report can substantiate findings. Do not
regenerate missing evidence and label it the original run, or reuse that authorization
against the changed protocol/document hashes. This note records the supplied status
and inspected authorization only; it does not approve another experiment.

Merged Issues #92/#93 govern future lifecycle, storage, MLOps and report/progress
handoffs. Issue #94 aligned documentation while the code then remained on the legacy layout.
No storage migration erases prior final-period exposure or changes scientific rules.

## Current retained validation and final readiness — 2026-10-03

The retained completed validation run is `validation-20261002-01`, distinct from
the removed earlier run above. [DR-014](decisions/DR-014-forecasting-selection-and-final-refit.md)
records its exact completion-manifest SHA-256 and frozen scientific decisions.
PR #133 records successful verification of 1,216 evaluations, 304,000 predictions,
304 configuration summaries and 1,184 saved-model replays. This correction records
that existing evidence; it does not rerun validation or claim a new verification.

The owner approved DR-014 and Documentation Step 1 under Issue #130. The separate
final runtime was merged in PR #133 and explicitly accepted under Issue #131 on
2026-10-03, including its recorded test/integrity evidence. That acceptance is
implementation readiness only. Historical-only preflight completed successfully
on 2026-10-03: `READY FOR AUTHORIZATION PREPARATION`. Retained validation
verification, environment/dependency matching and historical eligibility/origin/
baseline checks passed; the frozen 28-candidate scope and DR-014 producer mapping
remained unchanged. No estimator was fitted or reserved-final outcome accessed.
Those statements describe the historical preflight, before final execution.
Subsequently the owner authorized `final-20261003-01`, which ran once, revealed
reserved outcomes and failed during final replay verification. Its retained
bundle remains failed and unchanged; it is not completed final evidence.
[PR #141](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/141)
fixed the verified prediction-layout defect. The owner's explicit Issue #131
governance amendment authorizes `final-20261003-02` as the corrected rerun with
the same scientific scope. It has not been executed. Source/Git/implementation
identities are provenance only. Scientific bindings and overwrite protection
remain enforced; result-driven retries, search, retuning, reselection and
substitution remain prohibited. Preserve and disclose prior final-outcome access.

See [final operations](forecasting-final-evaluation.md) for the protected ordering.
The accepted storage layout is described in [runner operations](forecasting-runner.md);
older migration-pending statements above describe the earlier Issue #94 state.

## Computational scope

The primary matched grid has 24 configurations per model × horizon. **24 × 3 primary models × 4 horizons × 4 folds = 1,152 planned primary validation fits**. This formula records the frozen primary-validation workload design; completed-run evidence is reported separately above and must not be inferred from the formula alone. The fixed supportive Ridge Regression / Random Forest configurations are approved in the frozen protocol. Historical 5/12 configuration grids are not automatically reused. Supportive fits and later final refits are excluded from 1,152.

Simple baselines remain untuned: the protocol approves both formulas over four horizons, giving 32 planned baseline evaluations. Planned counts are not completion evidence; no baseline is silently removed or redefined.

**Earlier planning provenance:** the former Ridge/Random Forest/LightGBM search had 5/12/24 configurations, 41 configurations per horizon and 656 planned fits over four horizons/folds (492 for three horizons). DR-010 retains that superseded planning unchanged; those counts are not the current primary workload.

## Audit classification of intentionally retained references

- `notebooks/eda/demand_eda.ipynb`, `reports/demand-eda.md`,
  `reports/temporal-demand-profile.md` and `src/analysis/demand_exploratory_analysis.py` retain the
  historical exploratory context, including then-approved 1/7/14 horizons and
  then-proposed untouched-test wording. They are not instructions for the revised
  final evaluation. No notebook, raw data or descriptive result was regenerated.
- DR-005 retains the exact superseded fold table and December 17–30 holdout wording
  in its explicitly historical section; DR-004/007/010 retain original scope/counts
  where labelled as provenance. DR-007's 1/7/14 baseline definitions remain valid.
- The archived [Issue #52 protocol](issue-52-forecasting-protocol.md) retains its original body beneath historical notices. Its former local `outputs/issue-52-validation/comparison.md` path is historical only; the directory was removed and no accessible archive is established. Its metadata, candidate metrics, selected configurations/predictions, eligibility records and artifact audit belong to that earlier run, not the revised study. No historical score selects the current feature contract or model.
- There is no tracked Issue #52 comparison report under `reports/`, and the historical reproduction command requires the matching historical version of `src/forecasting/experiment.py`, rather than the current incompatible runner. The run metadata records Git HEAD `ec1296ecebeae359222036c93b4dd482fe977e23` and source fingerprints; reproducing it would require the matching historical source snapshot and separate authorisation. Compiled caches are not that source archive.
- Feature-review Options A/B/C and the earlier thirteen-column catalogue are superseded historical proposals. Issue #62 implemented the frozen conceptual features; its native LightGBM preprocessing was the earlier alignment gap identified under Issue #66 and is now historical provenance, superseded by the implemented common primary representation.
- DR-007/009/010 bodies retain earlier learned roles, single-boosting selection, unequal grids, representation and workload beneath explicit DR-013 supersession notices. Retained Naive/Seasonal Naive definitions remain valid; the frozen protocol records the later approval of 28-day formulas.
- Issue #62 source/tests preserve the accepted earlier model/representation contract; the earlier native-categorical contract is historical provenance, superseded by the implemented common primary representation.
- DR-001/002 and DR-003's explicitly historical body retain independent decision meanings; active data dictionaries, literature applicability and workflow summaries now link the frozen contract. Git/workflow governance remains unchanged. A 14-day supplier
  limit or rolling window is not an obsolete 14-day maximum forecast horizon.
