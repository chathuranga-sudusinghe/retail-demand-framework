# DR-001 — Dataset Selection

**Date:** 2026-09-21  
**Status:** Accepted for project planning; supervisor awareness/confirmation recommended because the source dataset differs from the COMP1889 proposal.  
**Owners:** COMP1884 group

## Decision

Use the **High-Dimensional Supply Chain Inventory Dataset** as the primary COMP1884 implementation dataset instead of the UCI Online Retail dataset.

Selected source:

https://www.kaggle.com/datasets/ziya07/high-dimensional-supply-chain-inventory-dataset

## Original position

The COMP1889 proposal and initial COMP1884 repository design used the UCI Online Retail dataset.

That dataset is useful for historical transaction and demand analysis, but it does not directly provide the inventory-state variables needed by the integrated framework, such as:

- inventory level;
- reorder point;
- supplier lead time;
- replenishment/order quantity;
- stockout indicator.

Using UCI alone would therefore require the group to invent a substantial hypothetical inventory environment for the inventory-risk component.

## Reason for change

The selected High-Dimensional Supply Chain Inventory Dataset better matches the end-to-end framework:

```text
Historical sales
    ->
Demand forecasting
    ->
Inventory-risk / replenishment analysis
    ->
Responsible decision support
```

It provides connected sales and inventory variables in one source, allowing:

- Chathuranga to train and evaluate the project's own demand-forecasting models using `Units_Sold`;
- Didilani to combine forecast outputs with inventory level, reorder point, supplier lead time, and replenishment information;
- Dewmi to consume forecast and risk/replenishment outputs and create the responsible decision-support layer.

## Key trade-off

The new dataset is **simulated**.

Therefore:

```text
better framework-variable coverage
vs.
lower real-world observational validity
```

The project must not describe the data as records from a real operating company.

## Alternatives considered

### 1. Retain UCI Online Retail

Advantages:

- real transaction data;
- established academic source.

Disadvantages:

- no direct inventory level;
- no reorder point;
- no supplier lead time;
- no replenishment quantity;
- inventory-risk/replenishment logic would depend heavily on hypothetical assumptions.

### 2. Use a richer simulated supply-chain dataset

Advantages:

- directly supports the three connected framework components;
- reduces the need to invent core inventory variables;
- supports end-to-end implementation and testing.

Disadvantages:

- simulated rather than observed company data.

## Implementation consequences

The project documentation and code must now treat:

```text
Units_Sold
```

as the primary historical demand source.

The project must build its own forecasting model. The source `Demand_Forecast` field must be excluded from normal model training unless a later, explicitly documented use proves leakage-safe.

Didilani's component should use inventory-state variables directly rather than create a complete fictional company inventory policy from scratch.

Dewmi's component remains the responsible decision-support layer.

## Research continuity

This decision changes the **data source and implementation detail**, not the core research direction.

The following remain:

- retail/supply-chain demand forecasting;
- inventory-risk analysis;
- decision support;
- the three-member integrated framework;
- the overarching COMP1884 research question.

## Supervisor note

Because the primary dataset differs from the earlier COMP1889 proposal, the group should keep this record and raise the change with the supervisor/module leader where required by module guidance.
