# DR-007 — Forecasting Model Set

**Status:** PARTIALLY SUPERSEDED BY DR-013

## Current status and effect

[DR-013](DR-013-matched-gradient-boosting-comparison.md) is the current authority for the learned-model comparison. DR-007 no longer defines the current learned-model set.

| Current evidence role | Models |
|---|---|
| PRIMARY RQ2 comparison | XGBoost Regressor, LightGBM Regressor, CatBoost Regressor |
| SUPPORTIVE benchmarks | Ridge Regression, Random Forest Regressor |
| Separate simple forecasting baselines | Naive, Seasonal Naive (weekly period 7) |

Only the three primary implementations determine the matched RQ2 answer. Ridge and Random Forest provide supportive/contextual evidence. Their configuration policy remains pending separate human approval under DR-013.

## Retained provisions still in force

- **Naive baseline role:** provide a simple recent-demand benchmark by extending the latest origin-observed demand level.
- **Seasonal Naive baseline role:** provide a weekly-repeat benchmark using the latest complete observed seven-day pattern.
- The approved leakage-safe 1-day, 7-day and 14-day formulas below remain unchanged.
- Both proposed 28-day baseline formulas remain approval-pending; a learned-model 28-day horizon does not approve baseline execution.

### Approved leakage-safe 1-day, 7-day and 14-day baseline formulas

All baseline calculations operate independently within the same `SKU_ID + Warehouse_ID` series. The forecast origin is the last date whose `Units_Sold` value is observed and available to the forecaster.

#### Naive baseline

Let the latest observed `Units_Sold` value at the forecast origin be the recent-demand level. The direct horizon forecasts are:

- **1-day forecast:** the latest observed `Units_Sold` value;
- **7-day cumulative forecast:** 7 multiplied by the latest observed `Units_Sold` value; and
- **14-day cumulative forecast:** 14 multiplied by the latest observed `Units_Sold` value.

This baseline holds the latest observed demand level constant across the requested horizon.

#### Seasonal Naive baseline with weekly period 7

Use only the most recent complete observed 7-day demand pattern available at the forecast origin. The pattern consists of seven consecutive observed daily values from the same SKU-warehouse series; no future or partially observed week may be used.

The direct horizon forecasts are:

- **1-day forecast:** the value for the corresponding weekday from that previous weekly pattern;
- **7-day cumulative forecast:** the sum of the most recent complete observed 7-day pattern; and
- **14-day cumulative forecast:** repeat that same observed 7-day pattern twice and sum the resulting 14 values, which is twice the 7-day pattern sum.

These definitions keep the two baselines distinct: Naive extends the latest observed demand level, while Seasonal Naive repeats the most recent weekly pattern. Both use only information available at the forecast origin and produce the approved targets directly without feeding predictions into later steps, so they remain compatible with DR-008 direct horizon-specific evaluation.

### Proposed 28-day baseline extensions — approval pending

The approved exact baseline definitions
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

### Common evaluation requirements

For any separately authorised baseline evaluation:

- retain the SKU_ID + Warehouse_ID identity and Units_Sold demand source under DR-002;
- use the four chronological expanding-window folds in [DR-005](DR-005-forecast-validation-design.md), with fixed origins and no updates from realised demand inside the forecast window;
- produce direct next-day or cumulative targets under [DR-008](DR-008-multi-step-forecasting-strategy.md), with complete outcomes inside the assigned interval;
- apply [DR-006](DR-006-forecasting-metrics-and-model-selection.md): mean WAPE across the four folds separately by horizon, supporting MAE/RMSE/Bias and fold-level evidence, with no cross-horizon composite;
- keep final-evaluation outcomes out of fitting and all subsequent selection decisions; and
- retain DR-013's separate primary, supportive and simple-baseline evidence roles. Naive and Seasonal Naive remain untuned; 28-day baseline execution still requires explicit approval of the proposed formulas.

This record authorises no experiment execution. Protocol approval, implementation acceptance and specific run authorisation remain separate human gates.

## Historical original decision body

> The content below is retained verbatim as historical provenance and is non-operative where superseded by DR-013.

<details>
<summary>Show superseded historical DR-007 body</summary>

# DR-007 — Forecasting Model Set

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

DR-002 fixes the forecasting grain as `SKU_ID + Warehouse_ID + Date` with `Units_Sold` as the target. Revised DR-004 records the human-selected 1-day, 7-day, 14-day, and 28-day forecasting design approved by the project owner. DR-005 defines the common four-fold expanding-window validation schedule, and DR-006 defines WAPE as the primary selection metric with MAE, RMSE, and Bias as supporting metrics.

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

The three learned models follow the approved 1/7/14/28-day design and common fourteen-predictor contract. The Naive and Seasonal Naive roles additionally require explicit approval of their proposed 28-day formulas before 28-day baseline execution. This baseline-formula approval requirement does not apply to Ridge Regression, Random Forest or LightGBM 28-day target support.

For any separately authorised execution, every approved candidate must:

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

- Current `requirements.txt` contains `lightgbm==4.6.0` as a pre-existing local change; this documentation alignment does not accept/install dependencies or implement a model.
- DR-010 settles the bounded model grids/search policy; the revised executable protocol and implementation remain separately reviewed.
- The frozen feature contract settles lags, rolling windows, categorical identities and promotion exclusion for all learned models/horizons.
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

</details>
