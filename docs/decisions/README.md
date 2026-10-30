# Decision Records

Forecasting protocol, configurations, producer mapping and final-refit policy are frozen; retained validation and final evaluation are complete as confirmed by Chathuranga. [Final results](../forecasting-final-evaluation.md) owns current interpretation. Original DR dates/statuses preserve decision provenance and must not be backdated or treated as new approval.

> **Header correction recorded — 15 October 2026, Issue #165:** The 14 October terminology edits replaced earlier “Supervisor confirmation: Not required” assertions in current decision-record headers with explicit university-requirement verification boundaries. The earlier wording remains traceable in Git history and, where retained, verbatim historical blocks. It is not evidence that the applicable confirmation requirements were verified. No lecturer or group approval is added by this correction.

This directory records important project decisions that affect multiple members or components.

Each decision record should include:

- date;
- status;
- decision;
- reason;
- alternatives considered;
- impact;
- responsible member(s) and actual reviewer(s);
- any confirmation required by the applicable COMP1884 instructions, with its evidence or unresolved status.

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
- [DR-012 — Inventory-Risk and Replenishment Methodology](DR-012-inventory-risk-replenishment-methodology.md) — Group-approved fixed-origin/no-receipt method for 1/7/14 days; approval reported by Chathuranga on 23 October for the 12 October WhatsApp discussion. Historical outputs retain their original status.
- [DR-013 — Matched Gradient-Boosting RQ2 Comparison](DR-013-matched-gradient-boosting-comparison.md) — Current matched primary RQ2 comparison authority.
- [DR-014 — Forecasting Selection and Final Refit](DR-014-forecasting-selection-and-final-refit.md) — Scientific freeze/refit policy and Documentation Step 1 approved by Chathuranga; Phase 1 merged in PR #133 and explicitly accepted under Issue #131. Historical-only preflight completed successfully on 2026-10-03: `READY FOR AUTHORIZATION PREPARATION`. The original `final-20261003-01` execution failed after outcome reveal; Chathuranga explicitly authorized corrected run `final-20261003-02` following PR #141, preserving the scientific scope.

Issue #65 has a human-approved/frozen scientific protocol. PR #90 merged Issue #89 orchestration; current storage is documented in [runner operations](../forecasting-runner.md). PR #133 implementation acceptance under Issue #131 establishes readiness only. It does not itself authorize execution. The subsequent instruction from Chathuranga separately authorizes `final-20261003-02` as a defect-correction rerun. Preserve and disclose the failed first execution and its outcome exposure. Scientific-document/data/environment bindings remain enforced; source/Git identities are provenance only.

RQ2 subordinate hypotheses and interpretation are approved as comparative and descriptive under DR-013: use horizon-specific arithmetic mean WAPE, all four fold-level results and supporting metrics; discuss magnitude, direction and fold consistency. No significance procedure or universal numerical decision threshold is approved, and no cross-horizon composite/overall winner is introduced.

## Remaining decisions and deferred extensions

**Reconciled 30 October 2026:** [The C1 decision/closeout record](../research-design.md#164-human-decisions-and-c1-closeout-record) records team acceptance, reported by Chathuranga on 29 October, of prospective uncertainty estimation, numerical replenishment, overstock, automatic human-review rules and h28 inventory use as disclosed limitations/deferred extensions. [#191 closed](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/191#issuecomment-6515040267) on the bounded descriptive scope; primary and provisional temporal significance claims remain untested. These are not pending requirements to invent methods or run tests for current delivery.

Remaining or future decisions include:

- retained-model audit/retention exceptions, archival responsibilities and backup policy;
- remaining retained input-contract/source-timing and component-acceptance details under #201;
- any future demand-regime definition, controlled forecast-to-decision evaluation or extension of a deferred method, if explicitly proposed and approved.

A future material methodology change needs the relevant human/component review and a decision recorded in the appropriate existing or new Decision Record. Preserve historical DR text, approval attribution and immutable evidence; the current scope record does not approve the deferred methods.
