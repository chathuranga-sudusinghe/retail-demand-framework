# Chathuranga — COMP1884 Group Project Contribution

## Member details

**Name:** Chathuranga Indrajith Sudusinghe  
**Student ID:** 001559279

## Role

**Model Training, Model Selection, Demand Forecasting, and Forecast Evaluation**

## Purpose in the group system

This component produces the future-demand forecast that becomes the input to Didilani's inventory-risk and replenishment analysis.

## Component research question

**How do temporal characteristics of SKU demand affect the performance and suitability of different forecasting approaches?**

## Working hypothesis

### H0

Forecasting performance does not significantly vary across different temporal demand behaviours.

### H1

Forecasting performance varies significantly across different temporal demand behaviours, and different forecasting approaches show different suitability across demand regimes.

This remains a working hypothesis until demand-regime definitions and statistical testing are formally specified.

## Inputs

Primary inputs:

- `Date`;
- `SKU_ID`;
- `Units_Sold`;
- selected leakage-safe supporting variables where justified.

The source `Demand_Forecast` field is not the project's forecasting target and must not be used in a way that leaks target/future information.

## Responsibilities

1. Define the forecasting target and aggregation level with the group.
2. Build chronological training, validation, and test datasets.
3. Train appropriate forecasting models and benchmarks.
4. Compare model performance using agreed metrics.
5. Select a suitable model based on out-of-sample evidence rather than complexity alone.
6. Generate future demand forecasts for each selected SKU/analytical unit.
7. Measure forecast error, bias, and uncertainty where feasible.
8. Produce a stable forecast-output contract for Didilani's component.
9. Document assumptions and limitations.

## Candidate outputs

```text
SKU_ID
period
actual_demand
forecast_demand
forecast_error
absolute_error
model_id
forecast uncertainty / interval fields, if available
```

## Evaluation

Candidate metrics:

- MAE;
- RMSE;
- WAPE;
- MAPE with zero-demand safeguards;
- Bias / Mean Forecast Error.

## Downstream dependency

Didilani's component receives the selected forecast output and combines it with inventory-state and replenishment variables such as `Inventory_Level`, `Reorder_Point`, `Supplier_Lead_Time_Days`, and `Order_Quantity`.

## Definition of done

This component is complete for COMP1884 when:

- the target and aggregation are documented;
- at least one benchmark and justified forecasting alternatives are evaluated;
- validation is time-aware;
- a suitable model is selected using reproducible evidence;
- future demand forecasts are generated;
- forecast outputs follow an agreed schema;
- error/bias analysis is available;
- outputs can be consumed by the inventory-risk component;
- limitations are documented.

## Scope boundary

This component is limited to the forecasting work required by the integrated COMP1884 group product. It should produce a defensible, evaluated forecast output without absorbing Didilani's inventory-risk/replenishment responsibilities or Dewmi's responsible decision-support responsibilities.
