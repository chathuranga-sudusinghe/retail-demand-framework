# Chathuranga — COMP1884 Group Project Contribution

> **Component revision — 2026-09-28:** The forecasting component is being revised to the human-selected 1/7/14/28-day direction; the revised methodology remains under repository-wide human review. Final feature freeze, proposed 28-day baseline definitions and the revised executable protocol remain pending. No experiment execution is authorised by this overview. See the [central methodology-revision record](../../forecasting-methodology-revision.md).

## Member details

**Name:** Chathuranga Indrajith Sudusinghe  
**Student ID:** 001559279

## Role

**Model Training, Model Selection, Demand Forecasting, and Forecast Evaluation**

## Purpose in the group system

This component produces the future-demand forecast that becomes the input to Didilani's inventory-risk and replenishment analysis.

## Component research question

**How do temporal characteristics of SKU demand affect the performance and suitability of different forecasting approaches?**

## Secondary forecasting hypothesis

This component uses a secondary hypothesis under the project's primary group-level hypothesis.

### H0

Forecasting performance does not significantly differ across temporal demand conditions.

### H1

Forecasting performance significantly differs across temporal demand conditions.

This remains provisional until temporal demand conditions and the statistical testing procedure are operationally defined.

## Inputs

Primary inputs:

- `Date`;
- `SKU_ID`;
- `Warehouse_ID`;
- `Units_Sold`;
- selected leakage-safe supporting variables where justified.

DR-002 has fixed the primary forecasting analytical unit as `SKU_ID + Warehouse_ID + Date`. The target at this grain is `Units_Sold`.

The source `Demand_Forecast` field is not the project's forecasting target and must not be used in a way that leaks target/future information.

## Responsibilities

1. Implement the approved forecasting target and analytical grain defined by DR-002.
2. Build chronological training, validation, and test datasets.
3. Train appropriate forecasting models and benchmarks.
4. Compare model performance using agreed metrics.
5. Select a suitable model based on out-of-sample evidence rather than complexity alone.
6. Generate future demand forecasts for each selected SKU-warehouse series.
7. Measure forecast error, bias, and uncertainty where feasible.
8. Produce a stable forecast-output contract for Didilani's component.
9. Document assumptions and limitations.

## Candidate outputs

```text
SKU_ID
Warehouse_ID
forecast_origin
target_start_date
target_end_date
forecast_horizon (1/7/14/28 days; 7/14/28 cumulative)
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

- the approved target and SKU-warehouse-day analytical grain are preserved;
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

## Revised forecasting responsibility

The human-selected revised forecasting direction under repository-wide review
uses direct 1/7/14/28-day targets and four expanding 28-day validation windows. The fourth window retains November–early December recovery
evidence beyond the feasible three-fold alternative. Final feature freeze and
proposed 28-day baseline definitions still need approval. The December 3–30 final
window has prior December 3–16 validation exposure and is protected from subsequent
selection. Didilani and Dewmi retain independent downstream decisions; no 28-day
inventory or human-review rule is silently approved. No experiment execution is authorised by this overview.
