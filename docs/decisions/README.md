# Decision Records

> **Documentation alignment — 2026-09-29:** The project owner has approved the current forecasting design and [frozen fourteen-predictor contract](../forecasting-feature-engineering.md). Original decision dates remain provenance. [Current approval and provenance](../forecasting-methodology-revision.md) records separate protocol, baseline and downstream gates; experiments remain NOT authorised.

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
- [DR-003 — Initial Forecasting Feature-Engineering Baseline](DR-003-forecasting-feature-engineering-baseline.md) — historical baseline superseded by the [frozen feature contract](../forecasting-feature-engineering.md).
- [DR-004 — Forecast Horizons for Decision Support](DR-004-forecast-horizons.md)
- [DR-005 — Forecast Validation Design](DR-005-forecast-validation-design.md)
- [DR-006 — Forecasting Metrics and Model-Selection Policy](DR-006-forecasting-metrics-and-model-selection.md)
- [DR-007 — Forecasting Model Set](DR-007-forecasting-model-set.md) — Partially superseded by DR-013; baseline provisions retained.
- [DR-008 — Multi-Step Forecasting Strategy](DR-008-multi-step-forecasting-strategy.md)
- [DR-009 — Gradient-Boosting Model Choice](DR-009-gradient-boosting-model-choice.md) — Superseded by DR-013.
- [DR-010 — Forecasting Hyperparameter-Search Strategy](DR-010-hyperparameter-search-strategy.md) — Primary search design superseded by DR-013.
- [DR-011 — Responsible Decision-Support Output Structure](DR-011-decision-support-output-structure.md)
- [DR-012 — Inventory-Risk and Replenishment Methodology](DR-012-inventory-risk-replenishment-methodology.md) — Proposed for group approval.
- [DR-013 — Matched Gradient-Boosting RQ2 Comparison](DR-013-matched-gradient-boosting-comparison.md) — Current matched primary RQ2 comparison authority.

[Issue #65](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/65) holds its draft protocol in the owner-confirmed preserved stash. Protocol alignment and reassessment of earlier unresolved items are deferred until Issue #66 is approved; Gate 1 remains incomplete.

RQ2 subordinate hypotheses and interpretation are approved as comparative and descriptive under DR-013: use horizon-specific arithmetic mean WAPE, all four fold-level results and supporting metrics; discuss magnitude, direction and fold consistency. No significance procedure or universal numerical decision threshold is approved, and no cross-horizon composite/overall winner is introduced.

## Decisions still to be formalised as evidence becomes sufficient

Examples include:

- revised primary preprocessing/model implementation alignment after Issue #62, runtime/version controls and Issue #65 protocol approval;
- supportive Ridge/Random Forest configuration/tuning policy;
- proposed 28-day baseline formulas and separate downstream 28-day approval;
- demand-regime definitions;
- uncertainty representation;
- remaining inventory input-contract details, overstock/excess-stock evaluation and numerical replenishment quantities beyond DR-012's proposed origin reorder-threshold exposure method;
- cross-component forecast-to-decision evaluation and human-review rules;
- final operationalisation of the primary group-level and secondary forecasting hypotheses.

Use one Markdown file per material decision.
