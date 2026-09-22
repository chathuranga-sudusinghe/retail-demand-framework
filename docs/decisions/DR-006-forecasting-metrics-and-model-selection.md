# DR-006 — Forecasting Metrics and Model-Selection Policy

**Date:** 2026-09-22
**Status:** Accepted for the current forecasting-methodology baseline
**Owner:** Chathuranga
**Decision owners:** COMP1884 group
**Supervisor confirmation:** Not required to record the current team methodology baseline. This record does not claim separate supervisor approval; any programme-required supervisor review remains subject to the team's review process.

## Context

DR-002 fixes the forecasting grain as `SKU_ID + Warehouse_ID + Date` with `Units_Sold` as the target. DR-004 approves the 1-day, 7-day, and 14-day forecast horizons. DR-005 requires every candidate model to use the same four expanding-window validation folds and reserves the final holdout for evaluation after model selection.

Those decisions establish what is forecast and where it is evaluated, but they do not define the primary metric or how fold-level results determine model selection. A common policy is required so candidate models are compared consistently without selecting from one favourable fold or using final-holdout results to revise earlier choices.

## Decision

**WAPE (Weighted Absolute Percentage Error) is the primary forecasting model-selection metric.**

The supporting metrics are:

- MAE (Mean Absolute Error);
- RMSE (Root Mean Squared Error); and
- Forecast Bias / Mean Forecast Error.

For the equations below:

- $y_i$ is actual demand;
- $\hat{y}_i$ is forecast demand; and
- $n$ is the number of observations.

### MAE

$$
\mathrm{MAE} =
\frac{1}{n}
\sum_{i=1}^{n}
\left|y_i-\hat{y}_i\right|
$$

### RMSE

$$
\mathrm{RMSE} =
\sqrt{
\frac{1}{n}
\sum_{i=1}^{n}
\left(y_i-\hat{y}_i\right)^2
}
$$

### WAPE

$$
\mathrm{WAPE} =
\frac{
\sum_{i=1}^{n}
\left|y_i-\hat{y}_i\right|
}{
\sum_{i=1}^{n}
\left|y_i\right|
}
$$

### Bias

$$
\mathrm{Bias} =
\frac{1}{n}
\sum_{i=1}^{n}
\left(\hat{y}_i-y_i\right)
$$

MAE, RMSE, and WAPE have a theoretical best value of 0; lower values are better. RMSE gives greater weight to larger errors because errors are squared. Bias is best when close to 0: positive bias indicates systematic overforecasting and negative bias indicates systematic underforecasting.

## Rationale

MAE and RMSE are scale-dependent and expressed in demand units. SKU-warehouse series may have different demand scales. WAPE normalises total absolute error relative to total actual demand and therefore provides a clearer primary relative comparison across candidate models for this project.

WAPE is not universally superior for every forecasting problem. This decision does not define arbitrary universal thresholds such as “WAPE below 10% is good.” Model quality must be judged relative to the same baseline models, folds, horizons, and evaluation design.

## Alternatives considered

### MAE as the primary metric

MAE is interpretable in demand units and remains a required supporting metric. It was not selected as primary because its scale dependence makes relative comparison across differently scaled SKU-warehouse demand less clear.

### RMSE as the primary metric

RMSE remains useful because it places more weight on relatively large errors. It was not selected as primary because it is also scale-dependent and can make a small number of large errors dominate the comparison.

### Bias as the primary metric

Bias is required to detect systematic overforecasting or underforecasting. It cannot serve as the primary accuracy metric because positive and negative errors can cancel and produce a value near zero despite material absolute errors.

### MAPE as the primary metric

MAPE was not selected because zero or near-zero actual demand requires special handling and can make percentage errors undefined or unstable. MAPE may be reported only as an optional supplementary metric with explicit safeguards; it is not part of the approved primary selection policy.

## Evaluation policy

Every candidate model must be evaluated using the same four DR-005 validation folds and the approved 1-day, 7-day, and 14-day horizons from DR-004.

For each model and horizon:

1. calculate MAE, RMSE, WAPE, and Bias separately for every fold;
2. calculate the arithmetic mean of each metric across the four folds;
3. use mean WAPE across folds as the primary model-selection statistic; and
4. review mean MAE, RMSE, and Bias together with the individual fold results before final selection.

Comparisons are made separately for each approved horizon. This decision does not introduce an additional averaging or weighting rule across horizons.

The selected model will be the candidate with the lowest mean WAPE across the approved validation folds for the relevant horizon, subject to acceptable fold-to-fold stability and supporting-metric review. A candidate must not be selected using one fold only. A low mean WAPE with highly unstable fold performance must be discussed rather than automatically treated as robust. This decision does not create an arbitrary numerical stability threshold.

Final-holdout results must not be used for model fitting, feature or model selection, hyperparameter tuning, metric-policy decisions, or revision of the selected model. They are examined only after model selection is complete.

## Limitations

- WAPE is undefined when the sum of absolute actual demand is zero. Any such case must be reported explicitly rather than silently divided by zero.
- WAPE aggregates absolute errors and does not show error direction; Bias is therefore required as a supporting metric.
- Mean values can hide fold-to-fold variation, so individual fold results must also be reviewed.
- The policy does not define a universal WAPE quality band or guarantee performance in a real retailer.
- The dataset is simulated and covers one observed year; the four folds cannot represent every future demand condition.
- This decision does not resolve the exact model set, final lag set, recursive versus direct forecasting, `Promotion_Flag` treatment, hyperparameter search, uncertainty representation, or demand-regime definitions.

## Impact

- `docs/research-design.md` defines WAPE as primary and documents the equations, metric roles, fold averaging, stability review, and holdout protection.
- `docs/workflows/demand-forecasting.md` applies the same policy to the modelling workflow.
- `docs/decisions/README.md` records this policy as formalised rather than open.
- Future model evaluation must retain fold-level metrics and their four-fold arithmetic means for every approved horizon.
- No model training, metric result, quality band, validation-date change, or forecast-horizon change is introduced by this decision.
