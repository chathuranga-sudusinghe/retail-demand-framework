# DR-003 — Initial Forecasting Feature-Engineering Baseline

**Date:** 2026-09-22  
**Status:** Accepted for the current forecasting-methodology baseline  
**Owner:** Chathuranga  
**Related issue:** #26

## Context

DR-002 fixed the primary forecasting analytical unit as:

```text
SKU_ID + Warehouse_ID + Date
```

with `Units_Sold` as the target.

The research design already identified calendar, lag, rolling, and growth/decline features as candidate feature families, but several details were not operationally defined. In particular, `week_of_year` had been listed despite the dataset containing only approximately one year of observations, and rolling statistics did not yet have explicit window lengths.

Implementation requires these points to be made explicit while avoiding unsupported feature choices.

## Decision

### 1. Exclude `week_of_year` from the primary feature set

The dataset contains only one year of observations. Each numbered week therefore occurs only once, so there is no repeated year-over-year evidence from which to learn a stable week-number effect.

Weekly behaviour may instead be represented through:

- `day_of_week`;
- lagged demand such as `lag_7`;
- 7-day rolling statistics.

### 2. Use 7-day and 14-day windows as the initial rolling-feature baseline

The initial rolling windows are:

```text
7 days
14 days
```

Candidate rolling statistics are:

- rolling mean;
- rolling median;
- rolling standard deviation.

A 30-day rolling window is not part of the initial primary baseline. It may be examined later as an alternative or sensitivity feature if evidence justifies it.

### 3. Require explicit feature definitions

Each forecasting feature should document:

- feature name;
- plain-language definition;
- calculation;
- why it is used;
- leakage rule;
- status: approved, candidate, or excluded.

### 4. Preserve leakage-safe temporal construction

For a forecast at time `t`:

- lag features must use only observations before `t`;
- rolling features must use only observations before `t`;
- the current `Units_Sold` value must not be included in its own rolling feature;
- future observations must never contribute to a feature.

### 5. Do not introduce unapproved composite forecasting features

No feature created by arbitrarily combining inventory, cost, price, or replenishment columns is approved at this stage.

Examples not currently approved include:

- `Inventory_Level - Reorder_Point`;
- `Unit_Price - Unit_Cost`;
- `Unit_Price / Unit_Cost`;
- lead-time-demand combinations.

These may be more appropriate for downstream inventory-risk analysis and require separate evidence before use in forecasting.

## Still open

This decision does **not** finalise:

- exact lag set;
- whether `month` and `quarter` improve forecasting performance;
- the exact growth/decline indicator;
- `Promotion_Flag` treatment;
- exact forecasting model set;
- train/validation/test dates;
- final metric set;
- uncertainty method;
- demand-regime definitions.

## Rationale

The decision keeps feature engineering reproducible and interpretable without overstating what can be learned from a one-year dataset. It also reduces the risk that implementation choices are silently invented before they are supported by evidence.

## Impact

- `docs/research-design.md` now defines the feature-engineering baseline in operational terms.
- `docs/workflows/demand-forecasting.md` now reflects the approved feature-engineering rules.
- Future forecasting implementation must follow this decision unless it is superseded by a later approved decision record.
