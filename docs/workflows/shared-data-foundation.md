# Shared Data Foundation Workflow

## Goal

Create one reproducible, documented data foundation used by all COMP1884 components.

## Workflow

```text
Local raw UCI Online Retail file
        |
        v
Schema validation
        |
        v
Data-quality profiling
        |
        v
Cancellation / return handling
        |
        v
Missing / invalid value handling
        |
        v
Temporal standardisation
        |
        v
Demand aggregation
        |
        v
Shared processed dataset
        |
        +--> Forecasting
        +--> Inventory-risk analytics
        +--> Responsible decision support
```

## Required decisions before implementation

1. Define cancellation detection.
2. Define treatment of returns and negative quantities.
3. Define treatment of non-positive prices.
4. Define handling of missing product descriptions.
5. Define whether `CustomerID` is required for each analysis.
6. Select daily or weekly primary aggregation.
7. Define product-history eligibility.
8. Define zero-demand periods in the regular time grid.
9. Define how net demand versus gross demand is represented.
10. Define train/validation/test cut points.

## Reproducibility rule

All shared cleaning and aggregation logic must live in code under `src/data/` rather than only inside notebooks.

## Output contract

The first shared analytical table should include, at minimum:

```text
StockCode
period
demand
```

plus additional documented columns needed by downstream work.

## Data ownership

The raw dataset remains local. No member should commit raw or processed full datasets to GitHub.
