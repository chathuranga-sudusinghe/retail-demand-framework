# Demand Forecasting Workflow

## Owner

Primary COMP1884 owner: **Chathuranga**

## Goal

Train and compare forecasting approaches, select a suitable model using time-aware evaluation, generate future SKU-warehouse-day demand forecasts, and provide a reproducible forecast-output contract for Didilani's downstream inventory-risk and replenishment analysis.

## Workflow

```text
Shared demand series
        |
        v
Temporal behaviour analysis
        |
        v
Leakage-safe feature engineering
        |
        v
Benchmark model
        |
        v
Statistical / regression / ML alternatives
        |
        v
Expanding-window validation (DR-005)
        |
        v
Forecast metrics
        |
        v
Model comparison and selection
        |
        v
Final holdout evaluation (after selection)
        |
        v
Future demand forecast
        |
        v
Bias / uncertainty analysis
        |
        v
Forecast-output contract
        |
        v
Didilani inventory-risk / replenishment analysis
```

## Approved analytical unit and target

DR-002 selects:

```text
analytical unit = SKU_ID + Warehouse_ID + Date
target = Units_Sold
```

This grain must be retained in forecast outputs so downstream inventory analysis can align each prediction with warehouse-specific inventory state.

## Temporal analysis

The first profiling stage has already established complete 365-day SKU-warehouse series with very low median zero-demand frequency. Further modelling-stage analysis may investigate:

- trend;
- seasonality;
- autocorrelation;
- volatility;
- intermittency;
- demand sparsity;
- SKU heterogeneity.

## Feature-engineering baseline

The current feature-engineering baseline is documented in `docs/research-design.md` and DR-003.

### Calendar

Primary candidate calendar features:

- `day_of_week`;
- `month`;
- `quarter`.

`week_of_year` is excluded from the primary feature set because the dataset contains only one year of observations and therefore does not provide repeated year-over-year evidence for numbered-week effects.

### Lagged demand

Candidate lag features include:

- `lag_1`;
- `lag_7`;
- `lag_14`;
- `lag_28`.

The final lag set remains open until modelling evidence supports it.

### Rolling demand

Initial approved rolling windows:

- 7 days;
- 14 days.

Candidate statistics for each window:

- rolling mean;
- rolling median;
- rolling standard deviation.

The current target value must never be included in its own rolling feature.

### Other candidates

- recent growth / decline indicator — calculation still open;
- `Promotion_Flag` — treatment still open and must be known at prediction origin if used.

No additional composite forecasting feature formed from inventory, cost, price, or replenishment variables is currently approved.

## Forecast horizons

The approved decision-support horizons are:

- **1 day** — next-day demand;
- **7 days** — cumulative demand over the next week;
- **14 days** — cumulative demand over the next two weeks.

These horizons do not change the daily analytical grain. Forecast rows remain aligned to `SKU_ID + Warehouse_ID + Date`; 7-day and 14-day demand views are horizon-level summaries or multi-step outputs derived from daily forecasting.

The 7-day and 14-day forecast horizons are also distinct from the 7-day and 14-day rolling **feature windows**:

- rolling window = how much historical demand is summarised as an input feature;
- forecast horizon = how far into the future demand is predicted.

The horizon choice is supported by periodic-review inventory literature and by the project dataset's verified 2-14 day supplier lead-time range. The exact multi-step forecasting strategy remains open.

## Approved validation workflow

[DR-005](../decisions/DR-005-forecast-validation-design.md), governed by [Issue #31](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/31), requires expanding-window time-series validation (rolling-origin / walk-forward evaluation with expanding history). Random train/test splitting must not be used. **All candidate models must be evaluated on the same fold schedule**, retaining the approved native grain and target.

All dates are inclusive. Training begins on 2024-01-01 in every fold, and the calendar history expands as follows:

| Fold | Training start | Training end / origin cutoff | Training days | Validation start | Validation end | Validation days |
| --- | --- | --- | ---: | --- | --- | ---: |
| 1 | 2024-01-01 | 2024-03-31 | 91 | 2024-04-01 | 2024-04-14 | 14 |
| 2 | 2024-01-01 | 2024-06-30 | 182 | 2024-07-01 | 2024-07-14 | 14 |
| 3 | 2024-01-01 | 2024-09-30 | 274 | 2024-10-01 | 2024-10-14 | 14 |
| 4 | 2024-01-01 | 2024-12-02 | 337 | 2024-12-03 | 2024-12-16 | 14 |

**Final model-evaluation holdout:** 2024-12-17 to 2024-12-30 inclusive, exactly **14 calendar days**.

For each fold, use its training history for fitting and its 14-day validation window to evaluate the approved 1-, 7- and 14-day horizons. Training-day counts precede any approved lag/feature-history loss. Earlier validation observations become historical inputs for later folds only as permitted by the later cutoff; they cannot be used retrospectively in an earlier fold.

The training window is the fitting history; the validation window is the future comparison interval; the forecast horizon is how far ahead a prediction extends; the final test is reserved for evaluation after selection. The 14-day validation-window length is distinct from the 14-day cumulative-demand horizon. At each fold cutoff, the next 1, 7 and 14 days fit inside its validation interval. Multi-step strategy and detailed scoring/update policies remain open and must respect those boundaries.

Fit any learned preprocessing only on the fold's training data, apply the leakage rules below at each prediction origin, and compare candidates using the common schedule. The approved metric and model-selection policy is defined in [DR-006](../decisions/DR-006-forecasting-metrics-and-model-selection.md) and summarised below. Once selection is complete, evaluate the final holdout without using it for model fitting, feature/model selection, hyperparameter tuning or validation decisions. Do not revise choices in response to final-test forecasting results.

**EDA disclosure:** full-year descriptive EDA already inspected all dates, including the final holdout. “Untouched” refers to its exclusion from fitting/selection/tuning and the protection of final-test forecasting results, not to absence of prior descriptive inspection. Fold 4 validation ends on December 16; final testing begins on December 17, so there is no overlap.

The EDA's March/September and first-/second-half demand-level differences support temporally separated origins; they do not establish recurring annual seasonality. Four folds provide the approved balance of temporal coverage, initial history and holdout preservation. DR-005 explains why two folds are less informative, three remain reasonable, and five or more add complexity and potential validation over-tuning rather than automatically causing model overfitting.

## Leakage control

Features at time `t` may only use information that would be available before the prediction being made.

In particular:

- lagged demand must use earlier observations only;
- rolling calculations must exclude the current target value and all future values;
- source `Demand_Forecast` must not be used as a normal model feature;
- inventory or source-generated variables must not be aligned from a future state;
- realised validation/test demand must not be used as an unavailable future input for an earlier-origin multi-step forecast;
- complete horizon outcomes must remain inside the assigned evaluation window; validation scoring must not borrow final-holdout outcomes.

## Evaluation outputs

At minimum:

```text
SKU_ID
Warehouse_ID
period
actual_demand
forecast_demand
error
absolute_error
model_id
```

Where possible, also include forecast uncertainty or prediction-interval fields.

## Approved metric and model-selection policy

**WAPE (Weighted Absolute Percentage Error) is the primary model-selection metric.** MAE (Mean Absolute Error), RMSE (Root Mean Squared Error), and Forecast Bias / Mean Forecast Error are supporting metrics.

Every candidate model must use the same DR-005 folds and the approved 1-day, 7-day, and 14-day horizons. For each model and horizon:

1. calculate WAPE, MAE, RMSE, and Bias separately for each of the four folds;
2. calculate the arithmetic mean of each metric across those folds;
3. compare candidates primarily using mean WAPE across folds; and
4. review the individual fold results and supporting mean MAE, RMSE, and Bias before selection.

Comparisons are horizon-specific; this workflow does not silently average or weight results across the three horizons. The selected model will be the candidate with the lowest mean WAPE across the approved validation folds for the relevant horizon, subject to acceptable fold-to-fold stability and supporting-metric review.

A low mean WAPE from unstable fold results is not sufficient evidence of robustness and must be discussed. Selection must never rely on one fold alone. WAPE has no universal project quality band, and candidates must be judged relative to the same baselines, folds, horizons, and evaluation design. Final-holdout results must not be used to revise model-selection decisions.

## Model-selection principle

Do not select a model only because it is more complex. Compare every candidate with the same simple baseline and shared evaluation protocol. Use mean validation-fold WAPE as the primary statistic, then confirm that fold-to-fold behaviour and supporting MAE, RMSE, and Bias do not reveal material weaknesses that the mean WAPE alone would hide.

## Downstream handoff

The selected forecast output is the primary analytical input to Didilani's component. `Warehouse_ID` must be preserved in the handoff.

Didilani does not retrain or repeat the demand-forecasting task. Her component combines the forecast with inventory-state and replenishment variables.
