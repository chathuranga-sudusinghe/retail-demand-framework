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
Time-aware validation
        |
        v
Forecast metrics
        |
        v
Model comparison and selection
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

## Leakage control

Features at time `t` may only use information that would be available before the prediction being made.

In particular:

- lagged demand must use earlier observations only;
- rolling calculations must exclude the current target value and all future values;
- source `Demand_Forecast` must not be used as a normal model feature;
- inventory or source-generated variables must not be aligned from a future state.

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

## Model-selection principle

Do not select a model only because it is more complex. Compare candidate models with a simple benchmark and select a suitable model using reproducible out-of-sample evidence, agreed metrics, and research relevance.

## Downstream handoff

The selected forecast output is the primary analytical input to Didilani's component. `Warehouse_ID` must be preserved in the handoff.

Didilani does not retrain or repeat the demand-forecasting task. Her component combines the forecast with inventory-state and replenishment variables.
