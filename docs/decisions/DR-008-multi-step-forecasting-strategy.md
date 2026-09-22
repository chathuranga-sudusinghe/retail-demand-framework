# DR-008 — Multi-Step Forecasting Strategy

**Date:** 2026-09-22
**Status:** Accepted for the current forecasting-methodology baseline
**Owner:** Chathuranga
**Decision owners:** COMP1884 group
**Related issue:** [#40 — Formalise forecasting model set and multi-step strategy](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/40)
**Supervisor confirmation:** Not required to record the current team methodology baseline. This record does not claim separate supervisor approval; any programme-required supervisor review remains subject to the team's review process.

## Context

DR-004 approves three forecast horizons while retaining the daily `SKU_ID + Warehouse_ID + Date` analytical grain:

- 1-day next-day demand;
- 7-day cumulative demand; and
- 14-day cumulative demand.

DR-005 requires the same four validation folds for every candidate, and DR-006 compares candidates separately by horizon using mean WAPE across folds with supporting MAE, RMSE, and Bias. A multi-step strategy is required before model training so horizon targets, leakage controls, and downstream quantities are aligned consistently.

## Candidate strategies

### Recursive forecasting

Recursive forecasting predicts the next step and then feeds earlier predictions into later forecast steps. It can generate a multi-day forecast from a one-step model.

Its main risk is error propagation: an inaccurate earlier prediction becomes an input to later steps, so forecast errors may accumulate across the horizon.

### Direct forecasting

Direct forecasting predicts each approved horizon directly from information available at the forecast origin. The approved targets are:

- 1-day next-day demand;
- 7-day cumulative demand; and
- 14-day cumulative demand.

Earlier forecast predictions are not fed into later horizon predictions. This aligns naturally with the project's horizon-specific evaluation policy.

## Decision

Use **direct horizon-specific forecasting** as the primary multi-step forecasting strategy.

Each approved horizon must have a directly aligned target and prediction generated only from information available at the forecast origin. The 7-day and 14-day predictions represent cumulative demand over their respective future windows rather than recursively generated daily predictions that are subsequently summed.

## Rationale

Direct horizon-specific forecasting is selected because:

1. the project evaluates the 1-day, 7-day, and 14-day horizons separately;
2. the 7-day and 14-day outputs are cumulative-demand quantities used by downstream inventory planning;
3. recursive forecasting can propagate earlier forecast errors into later steps;
4. direct forecasting provides a clearer alignment between training target, evaluation horizon, and downstream demand quantity; and
5. DR-006 already defines horizon-specific model comparison.

This is a project-specific decision. It does not establish that direct forecasting is universally superior to recursive forecasting.

## Evaluation and leakage requirements

For every candidate model:

- build each horizon target using only complete future outcomes contained within the relevant DR-005 validation interval;
- construct prediction features only from information available at the fold's forecast origin;
- do not feed realised validation or final-holdout demand into an earlier-origin prediction;
- do not feed earlier model predictions into later horizon predictions;
- evaluate each horizon separately under DR-006;
- retain the same fold boundaries and comparison protocol for every model; and
- keep final-holdout results out of model, feature, and hyperparameter selection.

## Alternatives considered

### Recursive forecasting as the primary strategy

Recursive forecasting offers one-step model reuse and can produce a complete daily forecast path. It was not selected as primary because accumulated prediction error can obscure the relationship between the model's training objective and the project's cumulative 7-day and 14-day planning quantities.

### Comparing recursive and direct strategies during model selection

Not included in the current approved scope because it would add another methodology dimension and tuning opportunity. A later sensitivity analysis would require explicit approval and must not use final-holdout results to justify the change.

## Limitations

- Direct forecasting requires horizon-specific targets and model outputs.
- A cumulative 7-day or 14-day prediction does not by itself provide the daily path within that horizon.
- Separate horizon models or outputs can differ in their selected candidate or error behaviour.
- The strategy does not resolve the LightGBM-versus-XGBoost choice, hyperparameter search, final lag set, uncertainty method, or demand-regime definitions.
- The decision is specific to this project's approved horizons and downstream planning quantities.

## Impact

- `docs/research-design.md` and `docs/workflows/demand-forecasting.md` now identify direct horizon-specific forecasting as primary.
- Future training code must construct separate 1-day, 7-day cumulative, and 14-day cumulative targets without future-data leakage.
- Recursive use of earlier predictions is not part of the primary modelling workflow.
- DR-004 horizons, DR-005 fold dates, and the DR-006 metric policy remain unchanged.
- No model training or modelling result is introduced by this decision.
