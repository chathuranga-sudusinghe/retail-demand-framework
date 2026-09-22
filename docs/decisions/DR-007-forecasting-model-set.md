# DR-007 — Forecasting Model Set

**Date:** 2026-09-22
**Status:** Accepted for the current forecasting-methodology baseline
**Owner:** Chathuranga
**Decision owners:** COMP1884 group
**Related issue:** [#40 — Formalise forecasting model set and multi-step strategy](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/40)
**Supervisor confirmation:** Not required to record the current team methodology baseline. This record does not claim separate supervisor approval; any programme-required supervisor review remains subject to the team's review process.

## Context

DR-002 fixes the forecasting grain as `SKU_ID + Warehouse_ID + Date` with `Units_Sold` as the target. DR-004 defines the 1-day, 7-day, and 14-day horizons. DR-005 defines the common four-fold expanding-window validation schedule, and DR-006 defines WAPE as the primary selection metric with MAE, RMSE, and Bias as supporting metrics.

A fixed candidate set is required before training so model families are not added or removed in response to validation or final-holdout results. The set must include meaningful baselines and increasing levels of modelling complexity without assuming that greater complexity produces better forecasts.

## Decision

The approved candidate model set is:

| Role | Model | Purpose |
| --- | --- | --- |
| Simple baseline | Naive | Test whether more complex models improve on a simple recent-demand benchmark. |
| Seasonal baseline | Seasonal Naive using lag 7 | Test whether repeating weekly demand provides a useful benchmark. |
| Linear ML baseline | Ridge Regression | Provide a regularised linear baseline for relationships between engineered features and demand. |
| Tree-based ML | Random Forest | Capture non-linear relationships and feature interactions. |
| Gradient-boosting ML | LightGBM or XGBoost | Provide a stronger boosted-tree candidate for comparison with simpler models. |

The gradient-boosting role is approved, but the specific choice between LightGBM and XGBoost remains open. That choice must be documented before implementation rather than inferred silently during training.

## Rationale

The set creates an interpretable progression of modelling complexity:

1. Naive establishes whether any learned model improves on a simple recent-demand benchmark.
2. Seasonal Naive using lag 7 tests whether weekly repetition alone is competitive.
3. Ridge Regression tests regularised linear relationships between approved engineered features and demand.
4. Random Forest tests whether non-linear relationships and feature interactions improve forecasting.
5. LightGBM or XGBoost provides one gradient-boosting candidate for comparison with the simpler approaches.

No model is expected to perform better merely because it is more complex. Suitability will be determined from common out-of-sample evidence.

## Common evaluation requirements

Every candidate must:

- use the same DR-005 four-fold validation schedule;
- evaluate the same DR-004 1-day, 7-day, and 14-day horizons;
- follow the direct horizon-specific strategy in DR-008;
- use mean WAPE across folds as the primary comparison statistic under DR-006;
- report supporting MAE, RMSE, and Bias;
- retain fold-level results so stability can be reviewed; and
- exclude final-holdout results from model and model-setting selection.

## Exact horizon-specific baseline calculations

All baseline calculations operate independently within the same `SKU_ID + Warehouse_ID` series. The forecast origin is the last date whose `Units_Sold` value is observed and available to the forecaster.

### Naive baseline

Let the latest observed `Units_Sold` value at the forecast origin be the recent-demand level. The direct horizon forecasts are:

- **1-day forecast:** the latest observed `Units_Sold` value;
- **7-day cumulative forecast:** 7 multiplied by the latest observed `Units_Sold` value; and
- **14-day cumulative forecast:** 14 multiplied by the latest observed `Units_Sold` value.

This baseline holds the latest observed demand level constant across the requested horizon.

### Seasonal Naive baseline with weekly period 7

Use only the most recent complete observed 7-day demand pattern available at the forecast origin. The pattern consists of seven consecutive observed daily values from the same SKU-warehouse series; no future or partially observed week may be used.

The direct horizon forecasts are:

- **1-day forecast:** the value for the corresponding weekday from that previous weekly pattern;
- **7-day cumulative forecast:** the sum of the most recent complete observed 7-day pattern; and
- **14-day cumulative forecast:** repeat that same observed 7-day pattern twice and sum the resulting 14 values, which is twice the 7-day pattern sum.

These definitions keep the two baselines distinct: Naive extends the latest observed demand level, while Seasonal Naive repeats the most recent weekly pattern. Both use only information available at the forecast origin and produce the approved targets directly without feeding predictions into later steps, so they remain compatible with DR-008 direct horizon-specific evaluation.

## Alternatives considered

### Baselines only

Using only Naive and Seasonal Naive would provide clear reference points but would not test whether learned linear or non-linear relationships improve forecasts.

### Machine-learning models only

Using only machine-learning models would remove the simple benchmarks needed to determine whether added complexity provides meaningful improvement.

### Both LightGBM and XGBoost

Including both would broaden the boosted-tree comparison but add implementation and tuning scope. The approved model set requires one gradient-boosting candidate; the specific library remains open until feasibility and dependency considerations are documented.

### Assuming the most complex model will be selected

Rejected. Model selection must follow DR-006 evidence, not an assumption that model complexity implies forecast quality.

## Limitations

- The exact LightGBM-versus-XGBoost choice remains open.
- Model hyperparameters and search strategy remain open.
- The final lag set and `Promotion_Flag` treatment remain open.
- The dataset contains one simulated year, which limits the evidence available to every candidate.
- The candidate set does not guarantee that any machine-learning model will outperform the baselines.
- This decision defines model roles, not training code or model results.

## Impact

- `docs/research-design.md` and `docs/workflows/demand-forecasting.md` now use this fixed candidate set.
- Naive and Seasonal Naive now have exact, leakage-safe calculations for every approved horizon.
- Model training must compare all approved roles under the same validation and metric policies.
- No candidate may be called best before out-of-sample results exist.
- No model training, hyperparameter choice, dependency addition, or metric result is introduced by this decision.
