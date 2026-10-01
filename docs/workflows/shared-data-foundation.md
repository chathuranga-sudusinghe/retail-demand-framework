# Shared Data Foundation Workflow

> **Issue #89 operational alignment:** Gate 1 is frozen/approved and PR #76 accepted the preceding runner. Common primary encoding and validation orchestration are implemented. Issue #89 adds argument-free resolution, validation model persistence and manifest-last integrity without changing scientific methodology. These changes await human implementation review and a matching specific authorization; no experiment was run. Earlier draft/implementation-pending wording below records previous stages and does not reopen approved forecasting decisions. Downstream and Gate 6 approvals remain separate. See [runner operations](../forecasting-runner.md).

> **Documentation alignment — 2026-09-29:** The human-approved forecast interface covers 1/7/14/28 days and the [frozen feature contract](../forecasting-feature-engineering.md). Interface support does not approve downstream use. The frozen protocol resolves the 28-day baseline formulas. Downstream/component-owner approvals remain separate; experiments are NOT authorised. See [revision and provenance](../forecasting-methodology-revision.md).

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
7. [DR-005](../decisions/DR-005-forecast-validation-design.md) fixes the four expanding 28-day windows and December 3–30 final evaluation at origin December 2, reserved from subsequent selection/fitting with prior December 3–16 validation and full-year EDA exposure disclosed.

Pending group approval, [DR-012](../decisions/DR-012-inventory-risk-replenishment-methodology.md) proposes origin-available inventory and policy snapshots for origin reorder-threshold exposure, with fixed origin policy and a no-receipt scenario.

## Decisions still required before later modelling/integration stages

1. define handling of any invalid records discovered by the reproducible pipeline;
2. define missing-period handling if future processed views introduce gaps;
3. implement the frozen 28-complete-day predictor history and complete-target eligibility without inventing extra product exclusions or imputation;
4. retain `Promotion_Flag` as descriptive context, excluded from the frozen forecasting inputs; any later predictor use requires a separate contract revision;
5. document source snapshot within-day semantics and resolve availability/invalid-input handling under DR-012's origin timing contract;
6. finalise the forecasting-to-inventory output contract;
7. finalise the inventory-to-decision-support output contract.

## Reproducibility rule

All shared cleaning, validation, alignment, and aggregation logic must live in code under `src/data/` rather than only inside notebooks.

## Output contracts

### Forecast-to-inventory timing

The approved shared forecast interface represents next-day and direct cumulative 7-, 14- and 28-day quantities from one fixed origin. Retain `SKU_ID`, `Warehouse_ID`, forecast origin `t` and horizon `h` separately, with the explicit target interval `t+1` through `t+h`, inclusive. A target-start date must not be mistaken for the origin date.

DR-012 remains Proposed for group approval; its original downstream scope covers 1/7/14-day forecast inputs. Carrying an `h=28` record through the shared-data schema does not approve 28-day inventory interpretation or the longer no-receipt scenario. **28-day downstream use requires separate component-owner/human approval.** The following inventory timing and scenario requirements remain subject to DR-012 group approval.

Join the same SKU-warehouse's `Inventory_Level` and `Reorder_Point` available at that origin, retain the snapshot date and availability assumption, and keep the threshold fixed within the scenario. Same-date availability does not establish before/after-sales semantics; document that interpretation before integration. Do not use future inventory or silently substitute a different snapshot when origin evidence is unavailable.

The exposure scenario assumes no receipts, transfers, returns, losses or other adjustments. Origin-available lead time is context only. Order quantity is context only after its availability at the forecast origin is established; it must not be added as received inventory. Missing/invalid required evidence remains unavailable/not assessed with a reason. Final schemas and handling of problematic forecasts remain open.

Keep realised cumulative `Units_Sold`, retrospective exposure states and errors in a distinguishable evaluation view. They must not enter origin-time forecast or decision inputs. Preserve DR-011's source distinction and unavailable-information semantics in the downstream handoff.

### Data views

The model-ready matrix follows the linked fourteen-predictor contract; other raw columns retained in shared/downstream views do not become forecasting predictors.

Historical demand view, at minimum (construction/alignment, not the predictor matrix):

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

Chathuranga and Tinosh share API integration design and review, with Chathuranga responsible for forecasting-facing contract meaning. Tinosh implements agreed adapters and delivery schemas after review by the relevant component owner. These technical contracts must preserve provenance, origin, horizon and unavailable-state reasons; they must not settle the pending snapshot or methodological decisions by default.

## Data ownership

The raw dataset remains local. No member should commit raw or processed full datasets to GitHub.
