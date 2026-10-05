# Decision Records

Forecasting protocol, configurations, producer mapping and final-refit policy are frozen; retained validation and final evaluation are complete as confirmed by the owner. [Final results](../forecasting-final-evaluation.md) owns current interpretation. Original DR dates/statuses preserve decision provenance and must not be backdated or treated as new approval.

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
- [DR-014 — Forecasting Selection and Final Refit](DR-014-forecasting-selection-and-final-refit.md) — Owner-approved scientific freeze/refit policy and Documentation Step 1; Phase 1 merged in PR #133 and explicitly accepted under Issue #131. Historical-only preflight completed successfully on 2026-10-03: `READY FOR AUTHORIZATION PREPARATION`. The original `final-20261003-01` execution failed after outcome reveal; the owner explicitly authorized corrected run `final-20261003-02` following PR #141, preserving the scientific scope.

Issue #65 has a human-approved/frozen scientific protocol. PR #90 merged Issue #89 orchestration; current storage is documented in [runner operations](../forecasting-runner.md). PR #133 implementation acceptance under Issue #131 establishes readiness only. It does not itself authorize execution. The subsequent owner instruction separately authorizes `final-20261003-02` as a defect-correction rerun. Preserve and disclose the failed first execution and its outcome exposure. Scientific-document/data/environment bindings remain enforced; source/Git identities are provenance only.

RQ2 subordinate hypotheses and interpretation are approved as comparative and descriptive under DR-013: use horizon-specific arithmetic mean WAPE, all four fold-level results and supporting metrics; discuss magnitude, direction and fold consistency. No significance procedure or universal numerical decision threshold is approved, and no cross-horizon composite/overall winner is introduced.

## Decisions still to be formalised as evidence becomes sufficient

Examples include:

- exact retained-model set/audit exceptions and archive responsibilities under the storage policy;
- verification and human-reviewed reporting for the explicitly authorized `final-20261003-02`, preserving the failed first execution and outcome-exposure history;
- separate downstream 28-day approval (forecasting baseline formulas are already approved);
- demand-regime definitions;
- uncertainty representation;
- remaining inventory input-contract details, overstock/excess-stock evaluation and numerical replenishment quantities beyond DR-012's proposed origin reorder-threshold exposure method;
- cross-component forecast-to-decision evaluation and human-review rules;
- final operationalisation of the primary group-level and secondary forecasting hypotheses.

Use one Markdown file per material decision.
