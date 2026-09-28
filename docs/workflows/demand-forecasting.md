# Demand Forecasting Workflow

> **Workflow revision — 2026-09-28:** The forecasting workflow is being revised to a human-selected 1/7/14/28-day direction; the revised methodology remains under repository-wide human review. The final feature set, proposed 28-day baseline definitions and revised executable protocol remain pending. No experiment is authorised by this workflow revision. See the [central methodology-revision record](../forecasting-methodology-revision.md).

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
Evaluation on revised final evaluation interval (after selection)
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

DR-003 documents the initial feature catalogue; the revised full experimental set is not frozen. Human calendar direction replaces integer weekday, prefers paired sine/cosine for 1 day, drops month/quarter and defers annual encodings/dummies. See `docs/forecasting-feature-engineering.md`; no final list is selected here.

### Calendar

Historical implemented calendar candidates (not the revised final set):

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

The final lag set requires human review and freeze before experiments; previous scores do not choose it.

### Rolling demand

Initial approved rolling windows:

- 7 days;
- 14 days.

The new 28-day forecast horizon does not approve a new historical rolling window.

Candidate statistics for each window:

- rolling mean;
- rolling median;
- rolling standard deviation.

The current target value must never be included in its own rolling feature.

### Other candidates

- recent growth / decline indicator — calculation still open;
- `Promotion_Flag` — treatment still open and must be known at prediction origin if used.

No additional composite forecasting feature formed from inventory, cost, price, or replenishment variables is currently approved.

## Approved candidate model set

[DR-007](../decisions/DR-007-forecasting-model-set.md) approves five candidate roles for comparison:

| Role | Model | Purpose |
| --- | --- | --- |
| Simple baseline | Naive | Recent-demand benchmark. |
| Seasonal baseline | Seasonal Naive using lag 7 | Weekly-repeat benchmark. |
| Linear ML baseline | Ridge Regression | Regularised linear feature-demand relationships. |
| Tree-based ML | Random Forest | Non-linear relationships and feature interactions. |
| Gradient-boosting ML | LightGBM | Boosted-tree comparison with simpler candidates. |

[DR-009](../decisions/DR-009-gradient-boosting-model-choice.md) selects LightGBM as the single gradient-boosting implementation to keep dependency and tuning scope controlled. This project-specific choice does not claim universal superiority over XGBoost or forecast performance before evaluation. No candidate is assumed to outperform another because it is more complex. All candidates must use the same DR-005 folds, DR-008 horizon targets, and DR-006 metrics.

## Approved hyperparameter-search workflow

[DR-010](../decisions/DR-010-hyperparameter-search-strategy.md) defines small, predefined search spaces for Ridge Regression, Random Forest, and LightGBM. Naive and Seasonal Naive are fixed baselines and must not be tuned.

For each learned model and each horizon included in the current methodology at execution time:

1. generate only the DR-010 parameter combinations;
2. evaluate every combination on the same four DR-005 expanding-window folds;
3. calculate WAPE, MAE, RMSE, and Bias for every fold and their arithmetic means across folds;
4. use mean WAPE as the primary tuning statistic;
5. review fold-level stability and supporting metrics;
6. select one configuration for that model and horizon; and
7. freeze the configuration before evaluation on the revised final evaluation interval.

Do not average results across horizons into one tuning score. Ordinary random K-fold cross-validation is not permitted. Search spaces must not be expanded ad hoc in response to validation results, and the revised final evaluation interval must not be used for tuning, search-space revision, or model selection. The implementation must record seeds, versions, feature order, fold definitions, candidate grids, selected settings, horizons, and the metric evidence used for selection.

## Forecast horizons

Under the revised forecasting direction currently under human review, the intended decision-support horizons are:

- **1 day** — next-day demand;
- **7 days** — cumulative demand over the next week;
- **14 days** — cumulative demand over the next two weeks;
- **28 days** — cumulative demand over four weeks / approximately monthly planning, not an exact calendar month.

These horizons do not change the daily analytical grain. Forecast outputs retain `SKU_ID` and `Warehouse_ID`; the 7-day, 14-day and 28-day outputs are cumulative-demand targets aligned to their forecast origin.

All four forecast horizons are distinct from the 7-day and 14-day rolling **feature windows**:

- rolling window = how much historical demand is summarised as an input feature;
- forecast horizon = how far into the future demand is predicted.

The initial 1/7/14 horizons were informed by periodic-review literature and verified 2–14-day lead times. Human review adds 28 days for four-week / approximately monthly planning; it is not an exact calendar month or justified by lead time alone.

[DR-008](../decisions/DR-008-multi-step-forecasting-strategy.md) selects **direct horizon-specific forecasting** as the primary multi-step strategy. Separate models or horizon-specific outputs predict next-day demand, 7-day cumulative demand, 14-day cumulative demand, and 28-day cumulative demand directly from information available at the forecast origin. Earlier predictions are not fed into later horizon predictions.

## Revised validation workflow under review

Random train/test splitting is not permitted; validation must preserve temporal order through the revised expanding-window design recorded in DR-005.

Use four expanding-window chronological folds, with one fixed forecast origin
at the training cutoff for every SKU–warehouse and horizon. There is no updating
with realised demand inside a validation window. All dates are inclusive and
calendar-day counts precede feature warm-up and complete-target exclusions.

| Fold | Training start | Training end / origin | Training days | Validation start | Validation end | Validation days |
|---|---|---|---:|---|---|---:|
| 1 | 2024-01-01 | 2024-03-31 | 91 | 2024-04-01 | 2024-04-28 | 28 |
| 2 | 2024-01-01 | 2024-06-30 | 182 | 2024-07-01 | 2024-07-28 | 28 |
| 3 | 2024-01-01 | 2024-09-30 | 274 | 2024-10-01 | 2024-10-28 | 28 |
| 4 | 2024-01-01 | 2024-11-04 | 309 | 2024-11-05 | 2024-12-02 | 28 |

**Revised final evaluation:** 2024-12-03 to 2024-12-30 inclusive, 28 days;
forecast origin 2024-12-02. No December 31 observation is invented.

### Evidence and the three-fold alternative

Historical EDA reports March/April means of 29.8834/29.8391, July 17.4084,
September/October 10.1739/10.2708 and November 13.0807 units per native observation.
The saved notebook's monthly/quarterly tables and retrospective daily chart
support high levels, decline, low demand and recovery within this simulated year;
they do not establish recurring annual seasonality or formal demand regimes.

Three folds were considered and remain methodologically feasible: April high
demand, July decline and October low demand. They omit separate recovery validation.
**Four folds provide broader validation evidence across distinct observed temporal
demand conditions while preserving expanding-window chronological evaluation.**
The recovery-period evidence in November–early December was considered useful
for this one-year dataset. November 5 is the latest complete 28-day placement
before the revised final interval, not an EDA-established change point.

Four is a project-specific human choice, not statistically optimal. Expanding
folds share training history and are not independent replicates. More folds
increase computational workload and validation-selection exposure; validation
folds do not make models learn more patterns. Training length and evaluation
conditions change together, so differences cannot automatically be attributed
to demand conditions alone. Fold 3/4 origins are only 35 days apart, with seven
unscored days between their validation windows.

### Target completeness, warm-up and non-overlap

At each cutoff, next-day and cumulative 7-, 14- and 28-day targets fit completely
inside its 28-day evaluation window. In this project's selected fixed-origin
protocol, a 28-day validation window is not treated as 28 forecast origins;
one origin and one target per series/horizon are used.
All training labels must end by their training cutoff. Features use only history
available at the row's own origin; scalers/learned transformations fit only training
rows. Never use realised future demand or target labels as predictors.

The four validation windows do not overlap each other or the revised final interval.
Earlier validation outcomes may enter later training only once historical to the
later cutoff. Unscored gaps may enter later training; no final-evaluation observations
may enter fitting or subsequent selection. Missing/incomplete outcomes remain
unavailable, not zero, shortened labels or reasons to borrow later dates.

A 28-day feature warm-up is feasible even in the initial 91-day history. With a
complete 28-day look-back and horizon h, eligibility is N − 28 − h + 1 rows per
series before other exclusions: 63/57/50/36 for h=1/7/14/28 in fold 1. This is
feasibility, not a guarantee of model adequacy; the final feature set remains open.

### Final-evaluation provenance and protection

The revised 28-day final evaluation window is reserved from all subsequent
feature, model and hyperparameter decisions and fitting. However, December 3–16
had prior validation exposure under the earlier 14-day methodology, so the revised
window is not fully unseen from the historical research process. Full-year
historical EDA also inspected those dates. Final forecasting results must not feed
back into selection, and this prior exposure must be disclosed in reporting.


Historical boundaries are preserved in DR-005 and the archived Issue #52 evidence.

## Leakage control

Features at time `t` may only use information that would be available before the prediction being made.

In particular:

- lagged demand must use earlier observations only;
- rolling calculations must exclude the current target value and all future values;
- source `Demand_Forecast` must not be used as a normal model feature;
- inventory or source-generated variables must not be aligned from a future state;
- realised validation/test demand must not be used as an unavailable future input for an earlier-origin multi-step forecast;
- complete horizon outcomes must remain inside the assigned evaluation window; validation scoring must not borrow outcomes from the revised final evaluation interval.

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

Every candidate model must use the same validation folds included in the current methodology at execution time, as recorded in DR-005, for each horizon included in the current methodology at execution time. For each model and horizon:

1. calculate WAPE, MAE, RMSE, and Bias separately for each of the four folds;
2. calculate the arithmetic mean of each metric across those folds;
3. compare candidates primarily using mean WAPE across folds; and
4. review the individual fold results and supporting mean MAE, RMSE, and Bias before selection.

Comparisons are horizon-specific; this workflow does not silently average or weight results across the four horizons. The selected model will be the candidate with the lowest mean WAPE across the validation folds included in the current methodology at execution time for the relevant horizon, subject to acceptable fold-to-fold stability and supporting-metric review.

A low mean WAPE from unstable fold results is not sufficient evidence of robustness and must be discussed. Selection must never rely on one fold alone. WAPE has no universal project quality band, and candidates must be judged relative to the same baselines, folds, horizons, and evaluation design. Results from the revised final evaluation interval must not be used to revise model-selection decisions.

## Model-selection principle

Do not select a model only because it is more complex. Compare every candidate with the same simple baseline and shared evaluation protocol. Use mean validation-fold WAPE as the primary statistic, then confirm that fold-to-fold behaviour and supporting MAE, RMSE, and Bias do not reveal material weaknesses that the mean WAPE alone would hide.

## Downstream handoff

The selected forecast output is the primary analytical input to Didilani's component. `Warehouse_ID` must be preserved in the handoff.

Didilani does not retrain or repeat the demand-forecasting task. Her component combines the forecast with inventory-state and replenishment variables.

## Issue #52 provenance and experiment stop point

The earlier [Issue #52 protocol](../issue-52-forecasting-protocol.md) and report
retain their original 1/7/14-day, 14-day-window and 13-feature provenance. They are
not the revised research baseline. Final feature freeze, proposed 28-day baseline
approval and a reviewed revised executable protocol are pending. The runner is
blocked; no further experiment command is authorised here. The owner must approve
and manually execute any later run under AGENTS.md after code/protocol review.
