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

## Current foundation decisions

The following foundation decisions/checks are complete:

1. downloaded schema, row count, date coverage, and key field behaviour have been verified;
2. DR-002 selects **SKU-warehouse-day** as the primary forecasting analytical unit;
3. the verified native grain is one row per `Date + SKU_ID + Warehouse_ID`;
4. `Stockout_Flag` is zero-variance and excluded from predictive/validation use as a stockout label;
5. source `Demand_Forecast` is leakage-sensitive and excluded from ordinary forecasting use;
6. warehouse-level inventory alignment has been profiled.

## Decisions still required before later modelling/integration stages

1. define handling of any invalid records discovered by the reproducible pipeline;
2. define missing-period handling if future processed views introduce gaps;
3. define product/history eligibility if any exclusion is required;
4. define chronological train/validation/test cut points;
5. define whether and how `Promotion_Flag` is available at prediction time;
6. define exact temporal alignment between forecast periods and inventory state;
7. finalise the forecasting-to-inventory output contract;
8. finalise the inventory-to-decision-support output contract.

## Reproducibility rule

All shared cleaning, validation, alignment, and aggregation logic must live in code under `src/data/` rather than only inside notebooks.

## Output contracts

Forecasting view, at minimum:

```text
SKU_ID
Warehouse_ID
period
demand
```

Inventory-analysis view may additionally include:

```text
Supplier_ID
Region
Inventory_Level
Reorder_Point
Supplier_Lead_Time_Days
Order_Quantity
Stockout_Flag
```

`Stockout_Flag` is retained only as a documented source field/limitation and must not be used as stockout ground truth.

The final cross-component schemas must be documented before integration.

## Data ownership

The raw dataset remains local. No member should commit raw or processed full datasets to GitHub.
