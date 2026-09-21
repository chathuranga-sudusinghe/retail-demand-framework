# Shared Data Foundation Workflow

## Goal

Create one reproducible, documented data foundation used by all COMP1884 components.

## Workflow

```text
Local High-Dimensional Supply Chain Inventory file
        |
        v
Schema validation
        |
        v
Data-quality profiling
        |
        v
Date / identifier validation
        |
        v
Leakage and source-variable review
        |
        v
Demand time-series preparation
        |
        v
Inventory-state preparation
        |
        v
Shared processed datasets
        |
        +--> Forecasting
        +--> Inventory-risk / replenishment analytics
        +--> Responsible decision support
```

## Required decisions before implementation

1. Confirm exact downloaded filename, schema, row count, and datatypes.
2. Confirm the primary forecasting unit: SKU-day, SKU-warehouse-day, or another justified unit.
3. Define handling of duplicate or invalid records.
4. Define date continuity and missing-period handling.
5. Define product/history eligibility.
6. Define chronological train/validation/test cut points.
7. Define whether `Promotion_Flag` is available at prediction time.
8. Explicitly exclude or isolate source `Demand_Forecast` to prevent leakage.
9. Profile `Stockout_Flag` and other fields for zero/low variance.
10. Define how inventory variables are aligned in time with forecast periods.
11. Define the handoff contract from forecasting to inventory analysis.
12. Define the handoff contract from inventory analysis to responsible decision support.

## Reproducibility rule

All shared cleaning, validation, alignment, and aggregation logic must live in code under `src/data/` rather than only inside notebooks.

## Output contracts

Forecasting view, at minimum:

```text
SKU_ID
period
demand
```

Inventory-analysis view may additionally include:

```text
Warehouse_ID
Supplier_ID
Region
Inventory_Level
Reorder_Point
Supplier_Lead_Time_Days
Order_Quantity
Stockout_Flag
```

The final schemas must be documented before cross-component integration.

## Data ownership

The raw dataset remains local. No member should commit raw or processed full datasets to GitHub.
