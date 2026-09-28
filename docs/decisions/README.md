# Decision Records

This directory records important project decisions that affect multiple members or components.

Each decision record should include:

- date;
- status;
- decision;
- reason;
- alternatives considered;
- impact;
- owner(s);
- whether supervisor confirmation is required.

## Current decision records

- [DR-001 — Dataset Selection](DR-001-dataset-selection.md)
- [DR-002 — Forecasting Analytical Unit](DR-002-forecasting-analytical-unit.md)
- [DR-003 — Initial Forecasting Feature-Engineering Baseline](DR-003-forecasting-feature-engineering-baseline.md)
- [DR-004 — Forecast Horizons for Decision Support](DR-004-forecast-horizons.md)
- [DR-005 — Forecast Validation Design](DR-005-forecast-validation-design.md)
- [DR-006 — Forecasting Metrics and Model-Selection Policy](DR-006-forecasting-metrics-and-model-selection.md)
- [DR-007 — Forecasting Model Set](DR-007-forecasting-model-set.md)
- [DR-008 — Multi-Step Forecasting Strategy](DR-008-multi-step-forecasting-strategy.md)
- [DR-009 — Gradient-Boosting Model Choice](DR-009-gradient-boosting-model-choice.md)
- [DR-010 — Forecasting Hyperparameter-Search Strategy](DR-010-hyperparameter-search-strategy.md)
- [DR-011 — Responsible Decision-Support Output Structure](DR-011-decision-support-output-structure.md)
- [DR-012 — Inventory-Risk and Replenishment Methodology](DR-012-inventory-risk-replenishment-methodology.md) — Proposed for group approval.

## Decisions still to be formalised as evidence becomes sufficient

Examples include:

- final lag set;
- `Promotion_Flag` treatment;
- growth/decline feature definition;
- demand-regime definitions;
- uncertainty representation;
- remaining inventory input-contract details, overstock/excess-stock evaluation and numerical replenishment quantities beyond DR-012's proposed origin reorder-threshold exposure method;
- cross-component forecast-to-decision evaluation and human-review rules;
- final operationalisation of the primary group-level and secondary forecasting hypotheses.

Use one Markdown file per material decision.
