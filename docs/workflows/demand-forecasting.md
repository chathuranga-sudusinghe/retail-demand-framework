# Demand Forecasting Workflow

Repository-wide authorities: [data lifecycle](../workflows/shared-data-foundation.md), [storage and retention](../artifact-storage-policy.md), [applied MLOps](../workflows/applied-mlops.md), [research reporting](../../reports/README.md), and [continuous progress log](../research-progress.md). These connect existing scientific/component contracts without replacing them.

> **Current operational alignment — Issue #94:** Issue #89 is closed and its orchestration implementation was merged in [PR #90](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/90). See the methodology revision record for validation-run provenance and evidence availability. Merged Issues #92/#93 define the lifecycle/storage/MLOps authorities; runtime migration remains separate. No new experiment or final evaluation is authorized.

> **Current documentation alignment — Issue #94:** The current 1/7/14/28-day forecasting design and [fourteen-predictor contract](../forecasting-feature-engineering.md) are human-approved. The revised executable protocol is frozen/approved under Issue #65, including the resolved 28-day baseline formulas. Issue #89 orchestration was accepted and merged through PR #90. Specific authorization remains run-bound; the methodology revision record distinguishes the recorded validation event from currently unavailable completion evidence. Storage migration, selection freeze and final evaluation remain separately reviewed. Experiments are NOT authorised. See [current approval and provenance](../forecasting-methodology-revision.md).

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

Chathuranga retains the forecasting-output contract and reviews its API representation with Tinosh. Their shared API work must preserve SKU, warehouse, forecast origin, horizon, target-window meaning and model provenance. Tinosh may implement the adapter and endpoint only against a reviewed contract; API integration does not alter model selection or forecasting evaluation.

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

## Frozen feature/preprocessing contract

Follow the [authoritative ordered contract](../forecasting-feature-engineering.md): two categorical identities (`SKU_ID`, `Warehouse_ID`) plus twelve numerical features comprising paired weekday encoding, lags 1/7/14, complete 7/14/28-day mean/sample-standard-deviation summaries and the fourteen-day slope. No model-specific or horizon-specific feature substitutions are approved.

Require 28 complete consecutive demand observations per SKU–warehouse, ending at the forecast origin. Calendar features refer to origin + 1. Fit learned preprocessing only on eligible training rows; complete training targets must end by the fitting cutoff. At evaluation, reuse one origin's vector across horizons without realised-demand updates.

Primary XGBoost, LightGBM and CatBoost share full one-hot identities (all eligible-training levels retained) followed by the same twelve unscaled numerical predictors: 67 physical columns under full coverage. Native categorical handling is excluded from the primary comparison. Supportive Ridge/Random Forest may reuse this representation; only Ridge scales numerical inputs. Primary mappings, order, origins, eligible rows, targets and folds are identical within each comparison.

`Date` and `Units_Sold` serve construction/alignment/target roles. All other raw fields are excluded forecasting inputs, while retaining appropriate descriptive/downstream roles. The contract lists excluded calendar, lag, median and composite alternatives. DR-003 and Issue #52 describe superseded historical catalogues, not active candidates.

## Revised model roles — Issue #66

[DR-013](../decisions/DR-013-matched-gradient-boosting-comparison.md) records the owner's approved direction:

| Evidence role | Models | Boundary |
|---|---|---|
| Primary controlled RQ2 comparison | XGBoost Regressor, LightGBM Regressor, CatBoost Regressor | Shared external representation/grid and evaluation controls; only these models answer RQ2. |
| Supportive benchmarks | Ridge Regression, Random Forest Regressor | Contextual linear/non-linear evidence, labelled separately. |
| Simple baselines | Naive, Seasonal Naive (period 7) | DR-007's 1/7/14 formulas retained; 28-day formulas are resolved in the frozen protocol. |

No candidate is presumed superior. DR-007/009/010 retain their earlier bodies as provenance, with explicit supersession notices for the learned roles, single-boosting choice and primary search. Internal algorithms and parameter effects are not identical despite matched external settings.

## Matched primary search workflow

Use the canonical Cartesian product in order: learning_rate [0.03, 0.05, 0.10], boosting_iterations [100, 300], max_depth [4, 8], subsample [0.8, 1.0], with subsample varying fastest. Map iterations to n_estimators for XGBoost/LightGBM and iterations for CatBoost; map depth to max_depth/max_depth/depth. Seed 42 is fixed (random_state/random_state/random_seed), never searched. Each primary model receives **24 configurations per horizon** and the same four DR-005 folds: **1,152 planned primary validation fits**, not executed evidence.

For later authorised execution, evaluate each canonical configuration across all four folds, fit preprocessing only on complete eligible training rows, calculate fold WAPE/MAE/RMSE/Bias and arithmetic fold means, then review horizon-specific mean WAPE and supporting/stability evidence. Record both canonical identity and effective library parameters. Do not add search dimensions, adapt grids to results, use random K-fold validation, average across horizons or use final-evaluation outcomes for selection.

DR-013 documents official API verification. The [frozen validation protocol](../protocol.md) resolves dependency pins, the fixed runtime recipe, subsampling controls and the fixed supportive Ridge Regression / Random Forest configuration policy. Historical 5/12 configuration grids are not reused. Naive/Seasonal Naive remain untuned. RQ2 interpretation follows the approved descriptive and comparative policy in DR-013, separately for each horizon.

Issue #62 remains provenance for the earlier preprocessing contract. The current source implements common primary representation, XGBoost/LightGBM/CatBoost interfaces and validation orchestration with tests. Issue #65 is frozen/approved and Gate 1 is complete; PR #76 accepted the preceding runner. Issue #89 added argument-free resolution, validation model persistence and manifest-last integrity and was merged through PR #90. Implementation acceptance and specific execution authorization remain separate; validation-run provenance and evidence availability are recorded in the methodology revision record.

## Forecast horizons

The approved forecasting horizons are:

- **1 day** — next-day demand;
- **7 days** — cumulative demand over the next week;
- **14 days** — cumulative demand over the next two weeks;
- **28 days** — cumulative demand over four weeks / approximately monthly planning, not an exact calendar month.

These horizons do not change the daily analytical grain. Forecast outputs retain `SKU_ID` and `Warehouse_ID`; the 7-day, 14-day and 28-day outputs are cumulative-demand targets aligned to their forecast origin.

All four forecast horizons are distinct from the independently approved 7-, 14- and 28-day rolling **feature windows**:

- rolling window = how much historical demand is summarised as an input feature;
- forecast horizon = how far into the future demand is predicted.

The initial 1/7/14 horizons were informed by periodic-review literature and verified 2–14-day lead times. Human review adds 28 days for four-week / approximately monthly planning; it is not an exact calendar month or justified by lead time alone.

[DR-008](../decisions/DR-008-multi-step-forecasting-strategy.md) selects **direct horizon-specific forecasting** as the primary multi-step strategy. Separate models or horizon-specific outputs predict next-day demand, 7-day cumulative demand, 14-day cumulative demand, and 28-day cumulative demand directly from information available at the forecast origin. Earlier predictions are not fed into later horizon predictions.

## Frozen validation workflow

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
feasibility, not a guarantee of model adequacy. The frozen feature contract requires this complete 28-day history for every learned model and horizon.

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
forecast_origin
target_start_date
target_end_date
forecast_horizon
actual_demand
forecast_demand
error
absolute_error
model_id
```

Where supported by a separately approved method, include uncertainty fields. Actual demand and errors are retrospective evaluation evidence, kept separate from prospective forecasts and downstream review inputs; Bias/error uses forecast − actual. Final schema names/types remain subject to the cross-component contract.

## Approved metric and model-selection policy

**WAPE (Weighted Absolute Percentage Error) is the primary model-selection metric.** MAE (Mean Absolute Error), RMSE (Root Mean Squared Error), and Forecast Bias / Mean Forecast Error are supporting metrics.

Every candidate model must use the same validation folds included in the current methodology at execution time, as recorded in DR-005, for each horizon included in the current methodology at execution time. For each model and horizon:

1. calculate WAPE, MAE, RMSE, and Bias separately for each of the four folds;
2. calculate the arithmetic mean of each metric across those folds;
3. compare candidates primarily using mean WAPE across folds; and
4. review the individual fold results and supporting mean MAE, RMSE, and Bias before selection.

Comparisons are horizon-specific; this workflow does not silently average or weight results across the four horizons. For the primary RQ2 comparison, the selected model will be the primary boosting candidate with the lowest mean WAPE across the validation folds for the relevant horizon, subject to fold-to-fold stability and supporting-metric review. Supportive benchmarks and simple baselines contextualise performance but cannot determine the RQ2 answer. This does not approve an additional downstream deployment-selection policy.

A low mean WAPE from unstable fold results is not sufficient evidence of robustness and must be discussed. Selection must never rely on one fold alone. WAPE has no universal project quality band, and candidates must be judged relative to the same baselines, folds, horizons, and evaluation design. Results from the revised final evaluation interval must not be used to revise model-selection decisions.

For RQ2, report the magnitude and direction of differences in arithmetic mean WAPE and inspect all four fold-level WAPE results for reasonable consistency, supported by MAE, RMSE and Bias. Relative differences may also be reported when clearly defined. The subordinate RQ2 hypotheses are comparative research hypotheses; no statistical-significance procedure or universal numerical decision threshold is approved, and the folds are not independent experimental replicates. A small aggregate difference driven mainly by one fold must not be presented as strong evidence of a general performance difference. Do not mechanically accept/reject H0_RQ2 using an arbitrary threshold. Report model ordering separately by horizon rather than collapsing it into an overall winner.

## Model-selection principle

Do not select a model only because it is more complex. Compare every candidate with the same simple baseline and shared evaluation protocol. Use mean validation-fold WAPE as the primary statistic, then confirm that fold-to-fold behaviour and supporting MAE, RMSE, and Bias do not reveal material weaknesses that the mean WAPE alone would hide.

## Downstream handoff

The selected forecast output is the primary analytical input to Didilani's component. `Warehouse_ID` must be preserved in the handoff.

Didilani does not retrain or repeat the demand-forecasting task. Her component combines the forecast with inventory-state and replenishment variables.

## Issue #52 provenance and experiment stop point

The earlier [Issue #52 protocol](../issue-52-forecasting-protocol.md) and ignored local artifacts retain their original 1/7/14-day, fourteen-day-window and thirteen-feature provenance. They are not the revised research baseline; [the central record](../forecasting-methodology-revision.md) documents artifact locations and the matching historical runner version.

The conceptual feature contract and Issue #65 protocol are frozen, including the 28-day baseline formulas. Issue #62 remains accepted provenance for the earlier representation. Current experiment runner source exists at `src/forecasting/experiment.py`, with common primary representation and validation orchestration implemented and tested. Issue #89 operational changes were merged through PR #90. A validation run has occurred; see the methodology revision record for evidence availability. The owner must separately authorise a specific run under AGENTS.md after implementation review. Final model/configuration freeze, final refit and final evaluation retain their separate approval gates.
