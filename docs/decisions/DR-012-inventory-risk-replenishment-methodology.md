# DR-012 — Inventory-Risk and Replenishment Methodology

> **Current status — 23 October 2026, Issue #177:** The COMP1884 group approved the documented fixed-origin, fixed-reorder-point, no-receipt exposure method for 1/7/14-day analysis on 12 October 2026, as reported by Chathuranga on 23 October. See the approval record below. Source timing, consumer acceptance and additional downstream methods remain separate.
>
> **Historical documentation alignment — 2026-09-29:** DR-012 remains Proposed for group approval. Upstream direct 1/7/14/28-day forecasting and its [feature contract](../forecasting-feature-engineering.md) are human-approved. Downstream 28-day use and substantive inventory/replenishment/uncertainty/review rules require their separate component-member/human approvals. No experiment execution is authorised. See [final results and limitations](../forecasting-final-evaluation.md#9-limitations).

**Date:** 2026-09-28
**Status:** Approved by the COMP1884 group for the documented 1/7/14-day fixed-origin/no-receipt method; calculation utilities and a human-run evaluation are implemented. Method approval does not establish source snapshot timing or operational effectiveness.
**Responsible member:** Didilani
**Decision owners:** COMP1884 group
**Related issue:** [#51 — Formalise inventory-risk and replenishment methodology](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/51)
**University requirements:** This record asserts no separate lecturer approval. Any confirmation required by the applicable COMP1884 instructions remains subject to the team's review process; teaching guidance does not establish approval of this methodology.

## Group approval record

- **Approval date:** 12 October 2026 (Monday).
- **Communication source:** WhatsApp group discussion.
- **Reported by:** Chathuranga, in the working conversation on 23 October 2026; recorded under [Issue #177](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/177).
- **Scope:** The documented origin reorder-threshold exposure method and fixed-origin, fixed-reorder-point, no-receipt scenario for horizons 1/7/14. The original decision date above is preserved; this is a later repository record of the reported group decision.
- **Boundary:** The private discussion was not independently inspected. This record does not infer approval of source-confirmed timing, 28-day inventory use, numerical replenishment, overstock, uncertainty estimation, automatic review rules or a new research execution.

The 23 October retained evaluation and assessment bundles still contain their original `proposed_for_group_approval` status. Preserve their bytes and preparation metadata: those labels record what the generator emitted, not the current approval record. New outputs use `group_approved`; the prospective consumer accepts both historical and current statuses without relabelling evidence. For 1/7/14-day rows, `approved_method` with an empty downstream reason denotes method scope only, not inventory availability or consumer acceptance. Historical rows retain `proposed_method_not_group_approved` and their original reason. H=28 remains gated under either status.

## Context

The [inventory methodology research brief](../research/inventory-risk-methodology.md) identified candidate methods and unresolved timing and evaluation questions. This record defines the group-approved initial method: **origin reorder-threshold exposure**. It supplies a common downstream interpretation of Chathuranga's forecasts while preserving Didilani's inventory-analysis ownership and Dewmi's responsible decision-support ownership.

The [dataset contract](../dataset.md) documents publisher-simulated SKU-warehouse records downloaded from Kaggle, one observed year, a zero-variance `Stockout_Flag`, and sparse `Order_Quantity`. These data cannot validate actual stockout prediction or establish an optimal ordering policy. The method below produces constructed scenario evidence, not actual shortage ground truth or a reconstruction of realised inventory evolution.

## Reason / rationale

The source `Reorder_Point` provides a documented policy reference. Comparing origin inventory with forecast demand relative to that reference makes the interpretation reproducible without inventing an additional numerical risk threshold. The source threshold is not established as economically optimal.

Separating cases already at/below the threshold from new forecast crossings makes the information supplied by the forecast visible. Otherwise, states known at the origin could inflate retrospective agreement. A no-receipt scenario avoids silently treating recorded orders as received stock when their timing and operational meaning remain unresolved.

The repository's [literature review](../literature/literature-review.md) motivates evaluating the forecasting-to-inventory relationship. It does not validate this particular proxy. The [retained constructed-origin evaluation](../../reports/inventory-risk/issue-164/evaluation-v1/report.md) remains conditional on the simulated data and the assumptions below.

## Alternatives considered

| Alternative | Decision and reason |
|---|---|
| Origin inventory versus reorder point alone | Retain as the already-at/below-threshold state; it does not identify additional forecast crossings. |
| One binary pressure label for all origin states | Do not use as the primary forecast comparison because origin-known positive states could inflate agreement. |
| Actual stockout classification | Unsupported: `Stockout_Flag` has no positive examples. |
| Treat `Order_Quantity` as receipts or optimal orders | Unsupported without a separate timing and policy decision. |
| Add low/medium/high cut points, overstock rules, or a numerical replenishment formula | Keep provisional; the available evidence does not approve these additional rules. |
| Reconstruct actual future inventory | Outside this method; receipts and other stock adjustments are not modelled. |

## Impact

The implemented inventory utilities use a common three-state interpretation and preserve origin, horizon, and warehouse identity. Retrospective forecast comparison will focus on initially above-threshold cases. This record aligns the research design, inventory workflow, member overview, and shared timing contract.

DR-002's grain, DR-004's horizons, DR-005's validation boundaries, DR-006's WAPE-based forecasting selection, and DR-008's direct cumulative targets remain unchanged. Recording approval changes no implementation formulas, experiment results, uncertainty method or human-review rule.

## Decision

### 1. Identity, origin and input availability

One scenario is identified by `SKU_ID`, `Warehouse_ID`, forecast origin `t`, and horizon `h`. The origin is the last date whose demand history is available to the forecaster. The horizon covers `t + 1` through `t + h`, inclusive.

Use `Inventory_Level` and `Reorder_Point` for the same SKU-warehouse at the origin, available when that forecast is issued. Preserve the snapshot date and availability assumption. A same-date row does not establish whether a field is recorded before or after sales; the within-day interpretation must be documented before integration. Do not silently substitute a future snapshot or invent a fallback for an unavailable origin snapshot.

For one origin, define:

```text
I_t = Inventory_Level_at_origin
R_t = Reorder_Point_at_origin
B_t = I_t - R_t
F_t,h = project model forecast of cumulative Units_Sold over t+1 through t+h
Y_t,h = subsequently realised cumulative Units_Sold over t+1 through t+h
```

When `B_t > 0`, it is the amount of demand that can occur before the origin reorder threshold is reached. `B_t <= 0` means the threshold has already been reached or passed at the origin.

### 2. Three exposure states

Apply the following interpretation to valid, available inputs:

| Condition | Forecast-based state |
|---|---|
| `B_t <= 0` | Already at/below the origin reorder threshold |
| `B_t > 0` and `F_t,h >= B_t` | Forecast threshold crossing within the horizon |
| `B_t > 0` and `F_t,h < B_t` | No forecast threshold crossing within the horizon |

Equality counts as reaching the threshold. The first state is known from origin inventory and policy evidence; it does not establish forecasting skill. For initially above-threshold cases, the crossing comparison is equivalent to `I_t - F_t,h <= R_t`.

Missing or invalid information required for an output makes that output unavailable/not assessed, with the reason retained; it must not become `FALSE` or zero. Availability is output-specific: the origin state can be known even when a forecast or later outcome is unavailable. This record does not approve clipping, rounding, or another repair of negative or otherwise problematic forecasts. Their handling remains an explicit input-contract decision before implementation.

### 3. Scenario assumptions and interpretation

- `I_t` and `R_t` are origin-available values; future `Inventory_Level` must not enter the origin-time calculation.
- `R_t` remains fixed throughout the evaluated scenario, even if later source records contain other thresholds.
- No receipts, transfers, returns, losses, or other inventory adjustments are assumed during the horizon unless a later approved method explicitly models them.
- `Units_Sold` is the approved demand proxy. Realised future sales are used only retrospectively, never as forecast-time inputs.
- Arithmetic projected balances such as `I_t - F_t,h` or `I_t - Y_t,h` are scenario quantities. Negative values are not verified physical negative inventory.
- Reaching this policy reference does not establish an actual stockout, actual shortage, an optimal order, or a requirement to execute a purchase.

### 4. Horizons and supplier lead time

The approved inventory scope covers 1-day next-day demand, 7-day cumulative demand, and 14-day cumulative demand. Current forecasting DR-004 / DR-008 includes an approved upstream 28-day cumulative input; that inventory extension is not approved by this record. Do not combine horizons into one score or treat the cumulative totals as daily forecast paths.

Retain origin-available `Supplier_Lead_Time_Days` as contextual evidence only. Describe each horizon as shorter than, equal to, or longer than that lead time. Do not round lead time to a horizon, interpolate a daily path, or claim an exact lead-time-demand forecast. Unavailable lead-time context must be marked explicitly; it is not a term in the exposure formula.

Different exposure states across different horizons are not automatically conflicting evidence: a longer horizon includes more demand. This record does not define horizon-disagreement review triggers.

### 5. Roles of source variables and replenishment scope

| Input | Role / boundary |
|---|---|
| Project model forecast | Demand input from Chathuranga's component, with model provenance and horizon meaning retained. |
| `Inventory_Level`, `Reorder_Point` | Origin snapshot and fixed policy reference for the scenario. |
| `Supplier_Lead_Time_Days` | Origin-available context only; no horizon mapping or additional lead-time calculation. |
| `Order_Quantity` | Contextual recorded activity only after its availability at the forecast origin is established; neither receipts nor optimal-policy ground truth. |
| Realised `Units_Sold` | Retrospective outcome over the exact target window. |
| `Stockout_Flag` | Dataset limitation only; unusable as stockout ground truth because it is zero-variance. |
| Source `Demand_Forecast` | Not the project model forecast and not substituted as the downstream forecast input. |
| Forecast-error / uncertainty context | Supplied by forecasting where available under an approved method; no uncertainty method is defined here. |

The initial output describes origin reorder-threshold exposure as replenishment-related evidence. Final numerical replenishment quantity remains provisional until a defensible method is separately approved. Overstock/excess-stock evaluation also remains provisional: not reaching the reorder threshold is not evidence of overstock.

### 6. Retrospective comparison and metric definitions

Replace `F_t,h` with `Y_t,h` in the same state rule, keeping `I_t`, `R_t`, identity and the horizon fixed. Require complete realised outcomes over the exact target window; unavailable outcomes are not zero demand.

The primary downstream forecast comparison uses `B_t > 0` cases with the required paired forecast and retrospective evidence. Report already-at/below-threshold cases separately, along with unavailable cases and reasons. When comparing candidates, use the same SKU, warehouse, origin, horizon, inventory snapshot and exposure method; disclose any differences in evaluable coverage.

For the initially above-threshold comparison, define:

| Count | Meaning |
|---|---|
| TP | Forecast crossing and retrospective proxy crossing |
| TN | No forecast crossing and no retrospective proxy crossing |
| FN | No forecast crossing but retrospective proxy crossing: missed crossing |
| FP | Forecast crossing but no retrospective proxy crossing: false alert |

Let `N = TP + TN + FN + FP` be the number of evaluable paired cases in the reported group. The evaluation direction uses the following explicitly defined summaries:

| Measure | Definition |
|---|---|
| Counts | `N`, `TP`, `TN`, `FN`, `FP`, plus separately reported origin-known and unavailable cases |
| Event prevalence | `(TP + FN) / N` |
| Missed-crossing rate | `FN / (TP + FN)` |
| False-alert rate | `FP / (FP + TN)` |
| Agreement | `(TP + TN) / N` |
| Precision | `TP / (TP + FP)` |
| Recall | `TP / (TP + FN)` |
| Balanced accuracy | `0.5 * [TP / (TP + FN) + TN / (TN + FP)]` |

Report a metric as unavailable when its denominator is zero; balanced accuracy is unavailable when either class-specific rate is undefined. State the reporting population and denominators explicitly. Check prevalence and counts before strong interpretation, and do not artificially rebalance the historical population. No single rate establishes a universally best downstream model or a justified cost trade-off.

These definitions establish the proxy-evaluation direction. The final cross-component experiment protocol, aggregation across origins/folds, inference procedure and uncertainty/robustness design remain separate decisions. DR-005's temporal boundaries and protection of the revised final evaluation interval continue to apply; its prior-exposure disclosure applies if/when the relevant 28-day downstream evaluation is approved and executed. DR-006's forecasting scores and selection are unchanged.

### 7. Boundary behaviour

Retain the conceptual margins:

```text
predicted_margin = B_t - F_t,h
retrospective_margin = B_t - Y_t,h
```

Near-zero margins indicate sensitivity to small demand changes. No numerical near-boundary tolerance is approved here. The retrospective margin is evaluation evidence and must not become a prospective review input.

### 8. Downstream handoff

The handoff to Dewmi should preserve identity, forecast origin and horizon, model/source provenance, origin inventory and policy evidence, buffer, exposure state and reason, conceptual margin where available, contextual lead time, assumptions, limitations and availability reasons. Replenishment quantity and uncertainty information remain explicitly provisional/unavailable where no approved method produces them.

Keep retrospective labels and errors distinguishable from information available when the forecast was issued. Follow DR-011's field groups and missing-information semantics; this record does not lock final column names, types or interchange formats. Human-review status remains `not assessed` until a review method is approved, independently of whether exposure itself can be assessed.

## Implementation interface

[The inventory runner](../../src/inventory_risk/runner.py) implements the formulas above with exact-window daily-target completeness and separate horizon summaries. Its required snapshot policy distinguishes unknown availability, an explicit source-confirmed assertion, and an explicitly selected constructed-origin scenario. The latter uses recorded same-origin quantities as hypothetical starting balances; it preserves unknown source timing and labels scenario states/counts separately. It does not retrospectively establish inventory availability or change this decision's approval status. See [protocol §12.2](../research/inventory-risk-evaluation-protocol.md#122-run-the-implemented-inventory-evaluation) for the exact settings, output contract and human-run command.

Prospective evidence excludes realised targets, retrospective margins, confusion cells and metrics. Numerical replenishment, uncertainty and h=28 inventory evaluation are not introduced by this implementation.

## Dependencies

- [DR-002](DR-002-forecasting-analytical-unit.md), [DR-004](DR-004-forecast-horizons.md) and [DR-008](DR-008-multi-step-forecasting-strategy.md): native grain, horizon meanings and direct forecasts.
- [DR-005](DR-005-forecast-validation-design.md) and [DR-006](DR-006-forecasting-metrics-and-model-selection.md): temporal evaluation and forecasting-selection boundaries.
- [Issue #52](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/52): historical forecasting protocol/artifacts only, not current implementation or final evidence. Downstream integration requires separately reviewed predictions from the revised frozen-contract pipeline/protocol; this DR does not authorise forecasting or inventory experiments.
- [Shared data workflow](../workflows/shared-data-foundation.md): snapshot availability, within-day interpretation and final input/output contracts before integration.
- [DR-011](DR-011-decision-support-output-structure.md) and [Issue #54](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/54): responsible output structure and evaluation-design work; neither supplies an approved uncertainty method or review threshold.
- Later cross-component decisions: the primary forecast-to-decision study (A), limited robustness analysis (C), and responsible human-review analysis (D).

## Open decisions / out of scope

- Source snapshot within-day semantics and final schemas, including explicit handling of problematic forecasts; no negative-forecast clipping is approved here.
- Final cross-component A/C/D evaluation protocol, boundary bands, statistical inference and final operationalisation of the research hypotheses.
- Forecast uncertainty estimation, calibration and propagation.
- Human-review conditions, thresholds and how multiple reasons are combined.
- Overstock/excess-stock definitions, numerical replenishment quantities, receipts and other inventory-flow modelling, and inventory-cost optimisation.
- Implementation code, model training, dashboard technology and autonomous ordering.

No new low/medium/high categories, lead-time interpolation, model-selection objective or research-question wording is introduced by this record.

## Consequences

This record provides the group with a common, explicit inventory-pressure interpretation used by the implemented utilities and retained constructed-scenario evaluation. The primary comparison separates forecast-added crossing evidence from states already known at the origin. The fixed-reference, no-receipt assumptions make the calculation inspectable but restrict its operational meaning, particularly over longer horizons where real receipts or policy changes could matter.

Results may describe agreement with the constructed retrospective proxy, missed crossings, false alerts and boundary behaviour within the simulated dataset. They cannot establish actual stockout accuracy, optimal purchasing, reduced cost, improved service level or improved managerial decisions. Event rarity, the one-year history and dependent time-series observations limit stronger inference. The existing implementation and human-run evidence remain separate from acceptance of a final consumer interface. Further research execution requires its own specific human authorisation; this approval record is not new empirical evidence.

## 28-day compatibility review — downstream approval pending

**Current disposition — reconciled 5 November 2026:** The heading and compatibility discussion below preserve the earlier extension proposal. The team subsequently accepted h28 inventory use as a disclosed limitation/deferred extension in the [C1 scope/closeout record](../research-design.md#164-human-decisions-and-c1-closeout-record), reported on 29 October. B8 is resolved for current delivery through that approved deferral; it is not awaiting another decision to complete the current project scope. Upstream h28 forecasting remains available; downstream exposure/evaluation remains gated. Any future extension needs separate methodological approval.

The approved upstream forecasting design supplies a direct cumulative 28-day quantity. Algebraically, the
proposed comparison F(o,h) against the fixed origin buffer I(o) − R(o) accepts
h=28 when the same origin and complete outcome interval are retained. This does
not validate the longer no-receipt scenario or approve its use. The extended
scenario may be more sensitive to omitted receipts and other adjustments.
**28-day downstream use requires component-owner/human approval.** The 1/7/14-day method has group approval; this does not approve h=28. Origin snapshot semantics, reorder-threshold meaning,
lead-time context, formulas and metric denominators remain unchanged. Lead times
are 2–14 days; do not reinterpret 28 days as lead time, interpolate daily paths,
or invent replenishment quantities or review thresholds. Cross-component
retrospective evaluation must disclose the revised final window's prior exposure
if/when the relevant 28-day downstream evaluation is approved and executed.
