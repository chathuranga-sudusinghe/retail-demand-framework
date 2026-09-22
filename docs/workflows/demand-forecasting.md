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
Feature engineering
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

## Leakage control

Features at time `t` may only use information that would be available at or before the prediction origin.

The source-provided `Demand_Forecast` field must not be used in a way that leaks future or target information into the project's own forecasting models.

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
