# DR-002 — Forecasting Analytical Unit

**Date:** 2026-09-22  
**Status:** Accepted  
**Decision owners:** COMP1884 group  
**Related issue:** #16

## Decision

The primary forecasting analytical unit for the COMP1884 project is:

```text
SKU_ID + Warehouse_ID + Date
```

In other words, the project will forecast **SKU-warehouse-day demand** derived from `Units_Sold`.

SKU-day and SKU-week aggregations may still be used for descriptive comparison, visualisation, sensitivity analysis, or secondary reporting, but they are not the primary modelling grain.

## Evidence

Temporal profiling showed:

- 250 SKU-warehouse series;
- 365 observations per series;
- median temporal completeness = 1.0;
- median zero-demand share = 0.005479;
- median coefficient of variation = 0.452184;
- median lag-1 autocorrelation = 0.640139.

The source data has one unique row per:

```text
Date + SKU_ID + Warehouse_ID
```

All five warehouses are present for every SKU-day.

Inventory alignment profiling showed that, within the same SKU-day:

- `Inventory_Level` varies across warehouses in 100% of groups;
- `Reorder_Point` varies across warehouses in 100% of groups;
- `Supplier_Lead_Time_Days` varies across warehouses in 100% of groups;
- `Order_Quantity` varies across warehouses in 24.33% of groups.

`Promotion_Flag` also conflicts across warehouses in approximately 41.62% of SKU-day groups.

## Reason

The project is an integrated framework:

```text
forecasting
    -> inventory-risk / replenishment analysis
    -> responsible decision support
```

A SKU-day forecast aggregated across warehouses would lose the warehouse-specific operational context required by the downstream inventory component. It would also require an additional allocation rule to connect aggregate SKU demand back to warehouse-level inventory, reorder point, and supplier lead time.

SKU-warehouse-day preserves the native source grain and downstream compatibility while still providing a complete 365-day time series for each SKU-warehouse combination.

SKU-week was not selected as the primary unit because it reduces each series to only 53 observations in the one-year dataset.

## Alternatives considered

### SKU-day

Advantages:

- 50 series;
- 365 observations per series;
- lower variation than warehouse-level demand;
- strong lag-1 autocorrelation.

Rejected as the primary unit because warehouse-specific inventory state and lead time differ for every SKU-day, and promotion status frequently differs by warehouse.

### SKU-week

Advantages:

- smoother aggregated series;
- high lag-1 autocorrelation;
- no median zero-demand problem.

Rejected as the primary unit because only 53 observations per series remain, limiting training and time-aware evaluation within the one-year dataset.

## Impact

The forecasting data foundation should construct regular series at:

```text
SKU_ID
Warehouse_ID
Date
demand
```

where:

```text
demand = Units_Sold
```

at the verified native grain, subject to reproducible validation.

Forecast outputs passed downstream should retain `Warehouse_ID` so that Didilani's inventory-risk analysis can align each forecast with warehouse-specific inventory variables.

## What this decision does not settle

DR-002 does not determine:

- model family;
- feature set;
- lag windows;
- promotion treatment;
- validation cut points;
- evaluation metrics;
- inventory-risk thresholds;
- replenishment formula;
- human-review rules.

Those remain separate research decisions.

## Limitations

The decision is specific to the current simulated dataset and integrated COMP1884 architecture. It does not establish that SKU-warehouse-day is universally preferable for retail forecasting.
