# Demand Forecasting Workflow

## Owner

Primary COMP1884 owner: **Chathuranga**

## Goal

Produce reproducible time-series forecasts and evaluation outputs for downstream inventory-risk analysis.

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
Bias / uncertainty analysis
        |
        v
Forecast-output contract
```

## Temporal analysis

Investigate:

- trend;
- seasonality;
- autocorrelation;
- volatility;
- intermittency;
- demand sparsity;
- product heterogeneity.

## Leakage control

Features at time `t` may only use information that would be available at or before the prediction origin.

## Evaluation outputs

At minimum:

```text
actual_demand
forecast_demand
error
absolute_error
model_id
StockCode
period
```

Where possible, also include uncertainty/confidence fields.

## Model-selection principle

Do not select a model only because it is more complex. Compare it with a simple benchmark and justify added complexity through out-of-sample evidence and research relevance.
