# Chathuranga — COMP1884 Group Project Contribution

## Member details

**Name:** Chathuranga Indrajith Sudusinghe  
**Student ID:** 001559279

## Role

**Time-Series Demand Forecasting and Model Evaluation**

## Purpose in the group system

This component creates the forecasting foundation required by the downstream inventory-risk and decision-support components.

## Component research question

**How do temporal characteristics of retail demand affect the performance and suitability of different forecasting approaches?**

## Working hypothesis

### H0
Forecasting performance does not significantly vary across different temporal demand behaviours.

### H1
Forecasting performance varies significantly across different temporal demand behaviours, and different forecasting approaches show different suitability across demand regimes.

This is a working hypothesis until demand-regime definitions and statistical testing are formally specified.

## Inputs

- cleaned transaction data;
- `InvoiceDate`;
- `StockCode`;
- `Quantity`;
- selected supporting variables where justified.

## Responsibilities

1. Define the forecasting target and time aggregation with the group.
2. Analyse demand trend, seasonality, autocorrelation, volatility, and intermittency.
3. Develop leakage-safe temporal, lag, and rolling features.
4. Implement and compare appropriate forecasting baselines/methods.
5. Use time-aware train/validation/test procedures.
6. Evaluate forecasts using agreed metrics.
7. Measure directional forecast bias.
8. Produce forecast outputs required by inventory-risk analysis.
9. Document assumptions and model limitations.
10. Support integration and reproducibility.

## Candidate outputs

A standard forecast-output contract may contain:

```text
StockCode
period
actual_demand
forecast_demand
forecast_error
absolute_error
bias_direction
model_id
uncertainty fields, if available
```

## Evaluation

Candidate metrics:

- MAE;
- RMSE;
- WAPE;
- MAPE with zero-demand safeguards;
- Bias / Mean Forecast Error.

## Downstream dependency

Didilani's component depends on reproducible historical demand and forecast outputs. Dewmi's component may consume model uncertainty, limitations, and explanatory information.

## Definition of done

This component is complete for COMP1884 when:

- the group target and aggregation are documented;
- at least one benchmark and justified forecasting alternatives are evaluated;
- validation is time-aware;
- metrics are reproducibly calculated;
- forecast outputs follow an agreed schema;
- error/bias analysis is available;
- results can be consumed by the inventory-risk component;
- limitations are documented.

## Scope boundary

This COMP1884 component should be strong enough to support the group product, but it should not consume all advanced forecasting ideas reserved for the COMP1885 individual deep-dive.
