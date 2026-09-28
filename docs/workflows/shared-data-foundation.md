# Shared Data Foundation Workflow

> **Shared-data revision — 2026-09-28:** The human-selected revised forecasting direction remains under repository-wide human review. The shared-data contract is being prepared to represent 1/7/14/28-day forecast outputs; interface support does not approve downstream use. Final feature freeze and proposed 28-day baseline definitions remain pending. Downstream 28-day inventory/decision-support use requires separate component-owner/human approval. See the [central forecasting-methodology revision record](../forecasting-methodology-revision.md).

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
6. warehouse-level inventory alignment has been profiled;
7. [DR-005](../decisions/DR-005-forecast-validation-design.md) fixes the expanding-window validation schedule and separate final holdout.

Pending group approval, [DR-012](../decisions/DR-012-inventory-risk-replenishment-methodology.md) proposes origin-available inventory and policy snapshots for origin reorder-threshold exposure, with fixed origin policy and a no-receipt scenario.

## Decisions still required before later modelling/integration stages

1. define handling of any invalid records discovered by the reproducible pipeline;
2. define missing-period handling if future processed views introduce gaps;
3. define product/history eligibility if any exclusion is required;
4. define whether and how `Promotion_Flag` is available at prediction time;
5. document source snapshot within-day semantics and resolve availability/invalid-input handling under DR-012's origin timing contract;
6. finalise the forecasting-to-inventory output contract;
7. finalise the inventory-to-decision-support output contract.

## Reproducibility rule

All shared cleaning, validation, alignment, and aggregation logic must live in code under `src/data/` rather than only inside notebooks.

## Output contracts

### Forecast-to-inventory timing

The shared forecast interface is intended to represent next-day and cumulative 7-, 14- and proposed 28-day forecast quantities under the revised forecasting direction. Retain `SKU_ID`, `Warehouse_ID`, forecast origin `t` and horizon `h` separately, with the explicit target interval `t+1` through `t+h`, inclusive. A target-start date must not be mistaken for the origin date.

DR-012 remains Proposed for group approval; its original downstream scope covers 1/7/14-day forecast inputs. Carrying an `h=28` record through the shared-data schema does not approve 28-day inventory interpretation or the longer no-receipt scenario. **28-day downstream use requires separate component-owner/human approval.** The following inventory timing and scenario requirements remain subject to DR-012 group approval.

Join the same SKU-warehouse's `Inventory_Level` and `Reorder_Point` available at that origin, retain the snapshot date and availability assumption, and keep the threshold fixed within the scenario. Same-date availability does not establish before/after-sales semantics; document that interpretation before integration. Do not use future inventory or silently substitute a different snapshot when origin evidence is unavailable.

The exposure scenario assumes no receipts, transfers, returns, losses or other adjustments. Origin-available lead time is context only. Order quantity is context only after its availability at the forecast origin is established; it must not be added as received inventory. Missing/invalid required evidence remains unavailable/not assessed with a reason. Final schemas and handling of problematic forecasts remain open.

Keep realised cumulative `Units_Sold`, retrospective exposure states and errors in a distinguishable evaluation view. They must not enter origin-time forecast or decision inputs. Preserve DR-011's source distinction and unavailable-information semantics in the downstream handoff.

### Data views

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
