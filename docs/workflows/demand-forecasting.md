# Demand Forecasting Workflow

## Owner

Primary COMP1884 owner: **Chathuranga**

## Goal

Train and compare forecasting approaches, select a suitable model using time-aware evaluation, generate future SKU-level demand forecasts, and provide a reproducible forecast-output contract for Didilani's downstream inventory-risk and replenishment analysis.

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

## Temporal analysis

Investigate:

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

The selected forecast output is the primary analytical input to Didilani's component.

Didilani does not retrain or repeat the demand-forecasting task. Her component combines the forecast with inventory-state and replenishment variables.
