# Forecasting methodology revision — human review, 2026-09-28

## Authority and scope

This records the human-selected horizon and validation revision supplied by the
project owner on 2026-09-28. The revised methodology remains under repository-wide
human review. It does not claim separate supervisor approval.
The earlier September 22–23 decisions remain part of the methodological history.
No previous model scores were used to choose or justify this revision.

## Current revised forecasting direction under review

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
  Historical preprocessing/completeness rules are provenance; final feature and
  revised executable preprocessing details remain subject to feature freeze and
  protocol approval. No new search dimension or automatic feature addition is approved.

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
The EDA notebook, reports and analysis source retain their historical wording.

## Human decisions still open

- Final ordered feature set, calculation rules and horizon/model feature policy.
- Calendar review direction: replace raw integer `day_of_week`; prefer paired
  `dow_sin`/`dow_cos` for 1 day; drop month and quarter from the initial set;
  defer month sine/cosine and weekday dummies. This is not a complete feature freeze.
- Explicit approval of the proposed 28-day Naive and Seasonal Naive extensions
  recorded in DR-007; no new baseline is silently accepted.
- **28-day downstream use requires component-owner/human approval.** DR-012 remains
  proposed; its formula, origin snapshots, threshold and lead-time meanings are
  unchanged. A longer no-receipt scenario requires separate interpretation review.
- Uncertainty, human-review rules, numerical replenishment and final integration
  contracts remain with their respective component owners.
- Acceptance of implementation/tests and a revised executable experiment protocol.
  The revised runner remains blocked while the feature freeze and required
  28-day baseline approvals for the proposed Naive and Seasonal Naive definitions
  are pending.
  Any future experiment still requires specific human authorisation and manual
  execution under AGENTS.md. No experiments were run for this revision.

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
- The archived Issue #52 protocol and report preserve their entire original bodies
  under historical notices. Their 13-feature list, scores, dates, counts and earlier
  approval history are unchanged and do not choose the redesigned methodology.
- Feature-review Options A/B are retained as historical proposals incompatible with
  the partial calendar direction; Option C remains unselected. The old 13-column
  source feature catalogue is preserved until the full revised freeze.
- DR-001/002/003, data dictionaries, literature/reference material and Git/workflow
  governance retain independent historical/data/window meanings. A 14-day supplier
  limit or rolling window is not an obsolete 14-day maximum forecast horizon.
