# DR-006 — Forecasting Metrics and Model-Selection Policy

> **Current status cross-reference — Issue #94:** [The frozen protocol](../protocol.md) resolves prior pending supportive settings, baseline and runtime decisions. Issue #89 was merged through PR #90. [Runner operations](../forecasting-runner.md) distinguish approved storage policy from unchanged runtime behavior. Original decision/development wording below remains historical provenance; this status note changes no decision or authorizes any run.

> **Documentation alignment — 2026-09-29:** The project owner has approved the current 1/7/14/28-day forecasting design and [frozen feature contract](../forecasting-feature-engineering.md). This record's original date and decision history remain intact. Proposed 28-day baseline formulas, the executable protocol and downstream methods retain separate approval boundaries; experiment execution is NOT authorised. See [current approval and provenance](../forecasting-methodology-revision.md).

**Original decision date:** 2026-09-22
**Original decision status:** Accepted for the earlier 1/7/14-day baseline
**Revision date:** 2026-09-28
**Revision status:** Current forecasting design human-approved; separate execution/implementation gates remain
**Documentation alignment:** 2026-09-29, on the project owner's explicit instruction
**Owner:** Chathuranga
**Supervisor confirmation:** Not required to record the current team methodology baseline. This record does not claim separate supervisor approval; any programme-required supervisor review remains subject to the team's review process.

## Context

DR-002 fixes the forecasting grain as `SKU_ID + Warehouse_ID + Date` with `Units_Sold` as the target. Revised DR-004 records the human-selected 1-day, 7-day, 14-day, and 28-day forecasting design approved by the project owner. DR-005 defines the common four expanding-window validation folds and reserves the revised final evaluation interval for evaluation after model selection; see DR-005 for the December 3–16 prior-validation-exposure limitation.

Those decisions establish what is forecast and where it is evaluated, but they do not define the primary metric or how fold-level results determine model selection. A common policy is required so candidate models are compared consistently without selecting from one favourable fold or using results from the revised final evaluation interval to revise earlier choices.

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

**Issue #66 role clarification:** DR-013 limits the primary RQ2 answer to XGBoost/LightGBM/CatBoost. Ridge/Random Forest are supportive evidence and Naive/Seasonal Naive are simple baselines. The equations, arithmetic fold means and horizon-specific WAPE-led policy below are unchanged; RQ2 hypotheses are comparative and interpreted descriptively by horizon, using magnitude, direction, all four fold-level results and supporting metrics as recorded in DR-013. No statistical-significance procedure or universal numerical decision threshold is approved; the folds are not independent experimental replicates. A small aggregate difference driven primarily by one fold is not strong evidence of a general performance difference. Do not mechanically accept/reject H0_RQ2 using an arbitrary threshold or collapse horizon-dependent model ordering into an overall winner.

Under the current human-approved forecasting design, every candidate model must be evaluated using the same four DR-005 validation folds and the human-selected 1-day, 7-day, 14-day, and 28-day horizons recorded in revised DR-004.

For each model and each horizon independently:

1. calculate MAE, RMSE, WAPE, and Bias separately for every fold;
2. calculate the arithmetic mean of each metric across the four folds;
3. use mean WAPE across folds as the primary model-selection statistic; and
4. review mean MAE, RMSE, and Bias together with the individual fold results before final selection.

Comparisons are made separately for each horizon. The 1-, 7-, 14-, and 28-day metrics must not be silently averaged into one cross-horizon overall score. This decision introduces no horizon weights or composite metric.

The selected model will be the candidate with the lowest mean WAPE across the approved validation folds for the relevant horizon, subject to acceptable fold-to-fold stability and supporting-metric review. A candidate must not be selected using one fold only. A low mean WAPE with highly unstable fold performance must be discussed rather than automatically treated as robust. This decision does not create an arbitrary numerical stability threshold.

Results from the revised final evaluation interval must not be used for model fitting, feature or model selection, hyperparameter tuning, metric-policy decisions, or revision of the selected model. They are examined only after model selection is complete.

## Limitations

- WAPE is undefined when the sum of absolute actual demand is zero. Any such case must be reported explicitly rather than silently divided by zero.
- WAPE aggregates absolute errors and does not show error direction; Bias is therefore required as a supporting metric.
- Mean values can hide fold-to-fold variation, so individual fold results must also be reviewed.
- The policy does not define a universal WAPE quality band or guarantee performance in a real retailer.
- The dataset is simulated and covers one observed year; the four folds cannot represent every future demand condition.
- The original metric decision did not resolve models, features, strategy or search. DR-008, [DR-013](DR-013-matched-gradient-boosting-comparison.md) and the frozen feature contract define the direct strategy, revised primary models/grid and predictor membership, including promotion exclusion; complete runtime controls and supportive configuration policy remain pending. Uncertainty and formal demand-regime definitions remain separate.

## Impact

- `docs/research-design.md` defines WAPE as primary and documents the equations, metric roles, fold averaging, stability review, and protection of the revised final evaluation interval.
- `docs/workflows/demand-forecasting.md` applies the same policy to the modelling workflow.
- `docs/decisions/README.md` records this policy as formalised rather than open.
- Future model evaluation must retain fold-level metrics and their four-fold arithmetic means for each horizon included in the current methodology at execution time.
- The original metric decision introduced no training or results. The current human-approved design applies it to 28 days and the revised common schedule; metric equations and horizon-specific selection remain unchanged.
