# Inventory-Risk and Replenishment Analysis Workflow

Repository-wide authorities: [data lifecycle](../workflows/shared-data-foundation.md), [storage and retention](../artifact-storage-policy.md), [applied MLOps](../workflows/applied-mlops.md), [research reporting](../../reports/README.md), and [continuous progress log](../research-progress.md). These connect existing scientific/component contracts without replacing them.

> **Current alignment — 23 October 2026, Issue #177:** [DR-012](../decisions/DR-012-inventory-risk-replenishment-methodology.md#group-approval-record) records group approval of the 1/7/14-day fixed-origin/no-receipt method, reported by Chathuranga for the 12 October WhatsApp discussion. Implementation and constructed-scenario evidence exist. Unknown source timing, consumer acceptance and additional 28-day/replenishment/uncertainty/review methods remain separate; this update authorises no research execution.

## Owner

Primary COMP1884 owner: **Didilani**

## Goal

Translate Chathuranga's demand forecast into **origin reorder-threshold exposure** under the group-approved [DR-012](../decisions/DR-012-inventory-risk-replenishment-methodology.md), with transparent evidence, assumptions and limitations.

## Workflow

```text
Project forecast at a defined origin and horizon
        +
Origin inventory level and reorder point
        |
        v
Origin buffer B_t = I_t - R_t
        |
        v
Three exposure states under the no-receipt scenario
        |
        v
Exposure evidence + margins + assumptions / limitations
        |
        v
Visual interpretation and responsible decision-support handoff
```

Didilani defines and reviews the analytical content of inventory-risk visuals and the business interpretation. Tinosh may implement approved chart/rendering code and prototype delivery. The inventory-risk evidence and assumptions passed onward remain Didilani's responsibility; technical integration must not create a new exposure or replenishment rule.

## Approved scenario interpretation

For the same SKU-warehouse, `I_t` and `R_t` are inventory and reorder-point values available at origin `t`; `B_t = I_t - R_t`. Forecast demand covers `t+1` through `t+h`, inclusive.

| Condition | State |
|---|---|
| `B_t <= 0` | Already at/below the origin reorder threshold |
| `B_t > 0` and forecast cumulative demand `>= B_t` | Forecast threshold crossing within the horizon |
| `B_t > 0` and forecast cumulative demand `< B_t` | No forecast threshold crossing within the horizon |

The approved inventory method scope applies separately to 1-day, 7-day cumulative and 14-day cumulative forecasts; the approved upstream 28-day forecasting input has not yet been approved for this downstream rule. Equality counts as reaching the threshold. Keep the origin threshold fixed and assume no receipts, transfers, returns, losses or other adjustments. Future inventory values must not be joined as origin inputs. Document snapshot availability and within-day interpretation before integration.

Missing/invalid required evidence produces unavailable/not assessed with a reason, not `FALSE`. The implemented mapping rejects malformed exports and retains finite negative forecasts as unavailable inventory inputs; no clipping is approved. Consumer acceptance remains separate. Negative arithmetic projected balances are not verified physical negative inventory.

## Context and output boundary

- Retain `SKU_ID`, `Warehouse_ID`, forecast origin, horizon and model provenance.
- Retain origin inventory, reorder point, buffer, exposure state/reason and the conceptual predicted margin `B_t - forecast_demand`.
- Retain origin-available supplier lead time as context only: horizon shorter than, equal to or longer than lead time. Do not round lead time, interpolate a daily path or claim an exact lead-time-demand forecast.
- Retain `Order_Quantity` as contextual recorded activity only after its availability at the forecast origin is established; it is neither receipts nor optimal-policy ground truth.
- Include available approved forecast-error/uncertainty context and the scenario assumptions and limitations.
- Follow DR-011 field groups and unavailable-information semantics; final names, types and interchange format remain open.

## Replenishment and overstock scope

Origin reorder-threshold exposure supplies replenishment-related evidence. Final numerical replenishment quantity and overstock/excess-stock evaluation remain provisional until separately justified and approved. Not reaching the threshold is not evidence of overstock. No low/medium/high risk scale or autonomous order instruction is defined.

## Verified dataset constraints

- `Stockout_Flag = 0` for all 91,250 rows. It must not be used to train or validate a stockout classifier.
- `Order_Quantity > 0` occurs in 5,027 rows, while 86,223 rows have zero order quantity. Replenishment modelling must account for this sparsity.
- Source `Demand_Forecast` is not Chathuranga's project model output.
- The exposure output is a constructed scenario proxy, not actual stockout prediction or actual shortage ground truth.

## Critical limitation

The dataset downloaded from Kaggle is simulated by its publisher. Its inventory fields provide a useful controlled environment for testing the framework, but the resulting rules/recommendations are not automatically validated for a real company.

## Evaluation

Replace forecast demand with realised cumulative `Units_Sold` over the exact same horizon, retaining the origin inventory and threshold. Use `B_t > 0` cases for the primary forecast comparison; report already-at/below-threshold cases separately, together with unavailable evidence and reasons.

Use DR-012's explicitly defined counts, event prevalence, missed-crossing rate, false-alert rate, agreement, precision, recall and balanced accuracy. Report denominators and undefined metrics as unavailable; inspect prevalence before interpretation and do not artificially rebalance the population. Compare the same cases and method across candidates, separately by horizon. No single rate establishes a universally best downstream model.

The retrospective margin is `B_t - realised_demand`. Near-zero predicted or retrospective margins indicate sensitivity, but no numeric tolerance is approved. Retrospective evidence must not enter forecast-time inputs or review triggers.

The [retained human-run evaluation](../../reports/inventory-risk/issue-164/evaluation-v1/report.md) reports the constructed-origin scenario separately for 1/7/14 days. The A/C/D cross-component protocol, further robustness work, uncertainty and human-review rules remain separate. The group approval does not settle those decisions. DR-006 forecasting selection remains WAPE-based.

## 28-day compatibility review — downstream use deferred

**Scope reconciled 30 October 2026:** The [C1 decision/closeout record](../research-design.md#164-human-decisions-and-c1-closeout-record) retains h28 inventory use, numerical replenishment and overstock as team-accepted disclosed limitations/deferred extensions, reported by Chathuranga on 29 October. They are not current requirements to add methods. Retained input/runtime acceptance and approved h1/h7/h14 views remain under #201, with Didilani as the bounded implementation executor and Tinosh providing technical review/support.

The approved upstream forecasting design supplies a direct cumulative 28-day quantity. Algebraically, the
proposed comparison F(o,h) against the fixed origin buffer I(o) − R(o) accepts
h=28 when the same origin and complete outcome interval are retained. This does
not validate the longer no-receipt scenario or approve its use. The extended
scenario may be more sensitive to omitted receipts and other adjustments.
**28-day downstream use requires component-owner/human approval.** DR-012 approval covers 1/7/14-day scenario exposure; it does not extend to h=28. Origin snapshot semantics, reorder-threshold meaning,
lead-time context, formulas and metric denominators remain unchanged. Lead times
are 2–14 days; do not reinterpret 28 days as lead time, interpolate daily paths,
or invent replenishment quantities or review thresholds. If/when the relevant
28-day downstream retrospective evaluation is approved and executed, disclose the
revised final-evaluation interval's prior validation exposure in accordance with DR-005.
