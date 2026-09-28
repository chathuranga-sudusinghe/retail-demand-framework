# DR-007 — Forecasting Model Set

> **DR-007 revision — 2026-09-28:** The approved model-family set remains unchanged. The revised forecasting direction adds a 28-day horizon, whose exact baseline definitions are proposed and still require explicit human approval. The repository-wide horizon revision remains under human review; see the [central methodology-revision record](../forecasting-methodology-revision.md).

**Original decision date:** 2026-09-22
**Original decision status:** Accepted for the earlier 1/7/14-day baseline
**Revision date:** 2026-09-28
**Revision status:** Under human review
**Owner:** Chathuranga
**Related issue:** [#40 — Formalise forecasting model set and multi-step strategy](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/40)
**Supervisor confirmation:** Not required to record the current team methodology baseline. This record does not claim separate supervisor approval; any programme-required supervisor review remains subject to the team's review process.

## Context

DR-002 fixes the forecasting grain as `SKU_ID + Warehouse_ID + Date` with `Units_Sold` as the target. Revised DR-004 records the human-selected 1-day, 7-day, 14-day, and 28-day forecasting direction currently under repository-wide human review. DR-005 defines the common four-fold expanding-window validation schedule, and DR-006 defines WAPE as the primary selection metric with MAE, RMSE, and Bias as supporting metrics.

A fixed candidate set is required before training so model families are not added or removed in response to validation or results from the revised final evaluation interval. The set must include meaningful baselines and increasing levels of modelling complexity without assuming that greater complexity produces better forecasts.

## Decision

The approved candidate model set is:

| Role | Model | Purpose |
| --- | --- | --- |
| Simple baseline | Naive | Test whether more complex models improve on a simple recent-demand benchmark. |
| Seasonal baseline | Seasonal Naive using lag 7 | Test whether repeating weekly demand provides a useful benchmark. |
| Linear ML baseline | Ridge Regression | Provide a regularised linear baseline for relationships between engineered features and demand. |
| Tree-based ML | Random Forest | Capture non-linear relationships and feature interactions. |
| Gradient-boosting ML | LightGBM | Provide a stronger boosted-tree candidate for comparison with simpler models. |

[DR-009](DR-009-gradient-boosting-model-choice.md) selects LightGBM as the single implementation for the approved gradient-boosting role. This is a project-specific methodology and scope decision, not a claim that LightGBM is universally better than XGBoost or evidence that it will outperform another candidate.

## Rationale

The set creates an interpretable progression of modelling complexity:

1. Naive establishes whether any learned model improves on a simple recent-demand benchmark.
2. Seasonal Naive using lag 7 tests whether weekly repetition alone is competitive.
3. Ridge Regression tests regularised linear relationships between approved engineered features and demand.
4. Random Forest tests whether non-linear relationships and feature interactions improve forecasting.
5. LightGBM provides one gradient-boosting candidate for comparison with the simpler approaches.

No model is expected to perform better merely because it is more complex. Suitability will be determined from common out-of-sample evidence.

## Common evaluation requirements

All candidate roles follow the revised 1/7/14/28 horizon direction once that revision is accepted. The Naive and Seasonal Naive roles additionally require explicit approval of their proposed 28-day formulas before 28-day baseline execution. This baseline-formula approval requirement does not apply to Ridge Regression, Random Forest or LightGBM 28-day target support.

Once the horizon revision is accepted, every candidate must:

- use the same DR-005 four-fold validation schedule;
- evaluate the same human-selected 1-day, 7-day, 14-day, and 28-day horizons recorded in revised DR-004, with the additional formula-approval requirement applying only to 28-day Naive and Seasonal Naive baseline execution;
- follow the direct horizon-specific strategy in DR-008;
- use mean WAPE across folds as the primary comparison statistic under DR-006;
- report supporting MAE, RMSE, and Bias;
- retain fold-level results so stability can be reviewed; and
- exclude results from the revised final evaluation interval from model and model-setting selection.

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

## Proposed 28-day baseline extensions — approval pending

The model families remain approved. The September 22 exact baseline definitions
covered only 1/7/14 days. Extending the forecasting horizon does not silently
approve these additional baseline definitions:

**Naive 28-day — APPROVAL PENDING:**

$$
\widehat{Y}^{\text{Naive}}_{o,28}=28y_o
$$

**Seasonal Naive 28-day — APPROVAL PENDING:**

$$
\widehat{Y}^{\text{Seasonal Naive}}_{o,28}=4\sum_{j=0}^{6}y_{o-j}
$$

The proposed Naive baseline holds the latest observed demand level constant for
28 days. The proposed Seasonal Naive baseline conceptually repeats the most recent
complete historical seven-day observed demand pattern across four future weeks;
its 28-day cumulative forecast is four times that observed weekly total. Neither
proposal uses realised future demand or claims predictive skill.

Implementation must continue to block execution of the proposed 28-day baseline
definitions until explicit human approval. Earlier 1/7/14 definitions remain
operational and unchanged.

## Alternatives considered

### Baselines only

Using only Naive and Seasonal Naive would provide clear reference points but would not test whether learned linear or non-linear relationships improve forecasts.

### Machine-learning models only

Using only machine-learning models would remove the simple benchmarks needed to determine whether added complexity provides meaningful improvement.

### Both LightGBM and XGBoost

Including both would broaden the boosted-tree comparison but add overlapping dependency, implementation, and tuning scope without a clear research need for this MSc project. DR-009 selects LightGBM as the single candidate while retaining XGBoost as a mature and capable alternative for the same general tabular-regression role.

### Assuming the most complex model will be selected

Rejected. Model selection must follow DR-006 evidence, not an assumption that model complexity implies forecast quality.

## Limitations

- LightGBM still requires a separately approved dependency addition and implementation; neither is introduced by this decision record.
- Model hyperparameters and search strategy remain open.
- The final lag set and `Promotion_Flag` treatment remain open.
- The dataset contains one simulated year, which limits the evidence available to every candidate.
- The candidate set does not guarantee that any machine-learning model will outperform the baselines.
- This decision defines model roles, not training code or model results.

## Impact

- `docs/research-design.md` and `docs/workflows/demand-forecasting.md` now use this fixed candidate set.
- DR-009 resolves the gradient-boosting implementation as LightGBM while keeping the approved model roles unchanged.
- Naive and Seasonal Naive retain their existing exact, leakage-safe 1/7/14-day calculations; both proposed 28-day definitions remain APPROVAL PENDING.
- Model training must compare all approved roles under the same validation and metric policies.
- No candidate may be called best before out-of-sample results exist.
- No model training, hyperparameter choice, dependency addition, or metric result is introduced by this decision.
