# DR-008 — Multi-Step Forecasting Strategy

> **Documentation alignment — 2026-09-29:** The project owner has approved the current 1/7/14/28-day forecasting design and [frozen feature contract](../forecasting-feature-engineering.md). This record's original date and decision history remain intact. Proposed 28-day baseline formulas, the executable protocol and downstream methods retain separate approval boundaries; experiment execution is NOT authorised. See [current approval and provenance](../forecasting-methodology-revision.md).

**Original decision date:** 2026-09-22
**Original decision status:** Accepted for the earlier 1/7/14-day baseline
**Revision date:** 2026-09-28
**Revision status:** Current forecasting design human-approved; separate execution/implementation gates remain
**Documentation alignment:** 2026-09-29, on the project owner's explicit instruction
**Owner:** Chathuranga
**Related issue:** [#40 — Formalise forecasting model set and multi-step strategy](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/40)
**Supervisor confirmation:** Not required to record the current team methodology baseline. This record does not claim separate supervisor approval; any programme-required supervisor review remains subject to the team's review process.

## Context

Revised DR-004 records the human-approved 1/7/14/28-day forecasting design while retaining the daily `SKU_ID + Warehouse_ID + Date` analytical grain:

- 1-day next-day demand;
- 7-day cumulative demand;
- 14-day cumulative demand; and
- 28-day cumulative demand.

DR-005 requires the same four validation folds for every candidate, and DR-006 compares candidates separately by horizon using mean WAPE across folds with supporting MAE, RMSE, and Bias. A multi-step strategy is required before model training so horizon targets, leakage controls, and downstream quantities are aligned consistently.

## Candidate strategies

### Recursive forecasting

Recursive forecasting predicts the next step and then feeds earlier predictions into later forecast steps. It can generate a multi-day forecast from a one-step model.

Its main risk is error propagation: an inaccurate earlier prediction becomes an input to later steps, so forecast errors may accumulate across the horizon.

### Direct forecasting

Direct forecasting predicts each horizon directly from information available at the forecast origin. The approved direct targets are:

- 1-day next-day demand;
- 7-day cumulative demand;
- 14-day cumulative demand; and
- 28-day cumulative demand.

Earlier forecast predictions are not fed into later horizon predictions. This aligns naturally with the project's horizon-specific evaluation policy.

## Decision

Use **direct horizon-specific forecasting** as the primary multi-step forecasting strategy.

Each horizon included in the current methodology at execution time must have a directly aligned target and prediction generated only from information available at the forecast origin. The 7-day, 14-day and 28-day predictions represent cumulative demand over their respective future windows rather than recursively generated daily predictions that are subsequently summed.

## Rationale

Direct horizon-specific forecasting is selected because:

1. the project evaluates the 1-day, 7-day, 14-day, and 28-day horizons separately;
2. the 7-day, 14-day and 28-day outputs are cumulative-demand planning quantities; downstream use at 28 days still requires component-owner approval;
3. recursive forecasting can propagate earlier forecast errors into later steps;
4. direct forecasting provides a clearer alignment between training target, evaluation horizon, and downstream demand quantity; and
5. DR-006 already defines horizon-specific model comparison.

This is a project-specific decision. It does not establish that direct forecasting is universally superior to recursive forecasting.

## Evaluation and leakage requirements

For every candidate model:

- build each horizon target using only complete future outcomes contained within the relevant DR-005 validation interval;
- construct prediction features only from information available at the fold's forecast origin;
- do not feed realised validation or final-evaluation demand into an earlier-origin prediction;
- do not feed earlier model predictions into later horizon predictions;
- evaluate each horizon separately under DR-006;
- retain the same fold boundaries and comparison protocol for every model; and
- keep final-evaluation results out of model, feature, and hyperparameter selection.

## Alternatives considered

### Recursive forecasting as the primary strategy

Recursive forecasting offers one-step model reuse and can produce a complete daily forecast path. It was not selected as primary because accumulated prediction error can obscure the relationship between the model's training objective and the project's cumulative 7-day, 14-day and 28-day planning quantities.

### Comparing recursive and direct strategies during model selection

Not included in the current approved scope because it would add another methodology dimension and tuning opportunity. A later sensitivity analysis would require explicit approval and must not use final-evaluation results to justify the change.

## Limitations

- Direct forecasting requires horizon-specific targets and model outputs.
- A cumulative 7-day, 14-day or 28-day prediction does not by itself provide the daily path within that horizon.
- Separate horizon models or outputs can differ in their selected candidate or error behaviour.
- The strategy itself did not resolve those independent choices. DR-009/010 historically settled a single LightGBM candidate and unequal grids; [DR-013](DR-013-matched-gradient-boosting-comparison.md) now defines the primary matched boosting comparison. The frozen feature contract retains predictor membership; runtime and supportive configuration decisions remain pending. Uncertainty and formal demand-condition definitions remain open.
- The decision is specific to this project's horizons and downstream planning quantities; downstream 28-day use remains separately gated.

## Impact

- `docs/research-design.md` and `docs/workflows/demand-forecasting.md` now identify direct horizon-specific forecasting as primary.
- Future training code must construct separate 1-day, 7-day cumulative, 14-day cumulative, and 28-day cumulative targets without future-data leakage.
- Recursive use of earlier predictions is not part of the primary modelling workflow.
- The original September 22 strategy decision did not change DR-004/005/006. The September 28 horizon revision, now explicitly approved by the project owner, extends the direct strategy to the 28-day cumulative target, while revised DR-005 separately defines the updated validation and final-evaluation boundaries; direct prediction and metric policy remain.
- No model training or modelling result is introduced by this decision.
