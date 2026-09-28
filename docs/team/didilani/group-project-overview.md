# Didilani — COMP1884 Group Project Contribution

> **Component revision — 2026-09-28:** DR-012 remains Proposed for group approval. The original downstream scope covers 1/7/14-day inputs; the revised forecasting methodology under human review introduces a proposed 28-day cumulative input. Downstream 28-day inventory/replenishment interpretation still requires separate component-owner/human approval. See the [central methodology-revision record](../../forecasting-methodology-revision.md).

## Member details

**Name:** Didilani Prasadika Weerawickrama Pathinayaka  
**Student ID:** 001560460

## Role

**Inventory-Risk Analytics, Replenishment Analysis, Visual Analytics, and Business Interpretation**

## Purpose in the group system

This component receives Chathuranga's demand forecast and translates it into inventory-risk and replenishment information using the inventory variables available in the selected dataset.

[DR-012](../../decisions/DR-012-inventory-risk-replenishment-methodology.md) proposes the initial method as **origin reorder-threshold exposure** under a fixed-origin, no-receipt scenario. Group approval is pending; implementation remains separate work.

Didilani does **not** forecast demand a second time.

## Component research question

**How can demand forecasts and inventory-state variables be combined to identify inventory risk and support replenishment decisions?**

## Inputs

Primary inputs include:

- Chathuranga's forecast demand;
- origin-available `Inventory_Level`;
- origin-available `Reorder_Point`, held fixed within the scenario;
- origin-available `Supplier_Lead_Time_Days` as context only;
- `Order_Quantity` as contextual activity only after its availability at the forecast origin is established, not receipts or optimal-policy ground truth;
- `SKU_ID` and `Warehouse_ID` so forecasts can be aligned with warehouse-specific inventory state;
- forecast error or uncertainty where available.

## Verified dataset constraints

- `Stockout_Flag` is 0 for all 91,250 records, so it cannot be used as a stockout target or validation label.
- `Order_Quantity` is non-zero in 5,027 records and zero in 86,223 records, so replenishment events are sparse and require profiling before modelling.
- DR-002 fixes the upstream forecasting grain at SKU-warehouse-day. Inventory-risk logic must preserve `Warehouse_ID` so each forecast is aligned with the correct warehouse-specific inventory state.
- The exposure calculation uses project forecast demand, origin inventory and the origin reorder point. Lead time and order quantity remain contextual; future inventory and source `Demand_Forecast` are not substituted as origin inputs.

## Responsibilities

1. Following group approval, implement and evaluate DR-012's documented origin reorder-threshold exposure method in separately authorised work.
2. Compare forecast demand with relevant inventory state and policy variables.
3. Distinguish already-at/below-threshold states from forecast threshold crossings and no forecast crossings.
4. Keep excess/overstock evaluation provisional until a defensible method is separately approved.
5. Preserve origin timing, horizon meaning and the no-receipt assumptions in reusable logic.
6. Evaluate retrospective crossings and boundary margins without inventing a numeric near-boundary tolerance.
7. Keep numerical replenishment quantity provisional until a defensible method is separately approved.
8. Create visual analytics that explain the risk/replenishment outputs.
9. Translate analytical outputs into business interpretation.
10. Produce outputs usable by Dewmi's responsible decision-support component.

## Candidate outputs

```text
SKU_ID
Warehouse_ID
forecast origin
forecast input horizon (1-day / 7-day cumulative / 14-day cumulative / 28-day cumulative)
28-day inventory interpretation: component-owner/human approval pending
forecast_demand
origin inventory level
origin reorder point
origin buffer B_t = I_t - R_t
origin reorder-threshold exposure state and reason
predicted margin B_t - forecast_demand
origin supplier lead time (context only)
order quantity (context only, after availability at the forecast origin is established)
assumptions, limitations and unavailable-information reasons
forecast provenance / available uncertainty context
supporting_explanation
```

These are output concepts, not a final schema. Follow DR-011's structure. Numerical replenishment quantity remains provisional. Retrospective state and `B_t - realised_demand` belong to separately identified evaluation evidence.

## Evaluation direction

For `B_t = I_t - R_t`, report `B_t <= 0` cases separately. On `B_t > 0` cases, compare forecast cumulative demand `>= B_t` with realised cumulative `Units_Sold >= B_t` over the same horizon. Equality counts as reaching the threshold. Report DR-012's counts and denominator-defined proxy metrics separately by horizon, with undefined metrics unavailable and event prevalence visible.

Missing/invalid required evidence must not become a negative result. Not reaching the threshold is not evidence of overstock. The method supplies the downstream interpretation for the primary forecast-to-decision study; the final cross-component protocol, uncertainty method and human-review rules remain separate decisions. Chathuranga's DR-006 WAPE-based selection is unchanged.

## Important boundary

The source dataset is simulated. The no-receipt scenario assumes no transfers, returns, losses or other adjustments and does not reconstruct actual inventory evolution. Negative projected balances are arithmetic scenario values, not verified physical negative inventory. Conclusions must not be presented as actual stockout prediction, actual shortage ground truth or validated operating rules for a real retailer.

If a numerical replenishment method is later justified and approved, any quantity it recommends would be a **decision-support recommendation**, not an automatically executable purchase order.

## Definition of done

- risk/replenishment rules or model are documented;
- required inventory variables are reproducibly derived;
- mapping/calculation logic is implemented;
- thresholds are justified and sensitivity is considered;
- replenishment recommendation logic is evaluated where used;
- visual outputs are understandable;
- limitations are reported;
- outputs can be consumed by the responsible decision-support layer.

## Scope boundary

This is not a dashboard-only contribution. The visual layer communicates a substantive inventory-risk and replenishment-analysis method.

## 28-day compatibility review — downstream approval pending

The revised forecasting direction under human review introduces a proposed
direct cumulative 28-day quantity. Algebraically, the
proposed comparison F(o,h) against the fixed origin buffer I(o) − R(o) accepts
h=28 when the same origin and complete outcome interval are retained. This does
not validate the longer no-receipt scenario or approve its use. The extended
scenario may be more sensitive to omitted receipts and other adjustments.
**28-day downstream use requires component-owner/human approval.** DR-012 remains
proposed for group approval. Origin snapshot semantics, reorder-threshold meaning,
lead-time context, formulas and metric denominators remain unchanged. Lead times
are 2–14 days; do not reinterpret 28 days as lead time, interpolate daily paths,
or invent replenishment quantities or review thresholds. If/when the relevant
28-day downstream retrospective evaluation is approved and executed, disclose the
revised final-evaluation interval's prior validation exposure in accordance with DR-005.
