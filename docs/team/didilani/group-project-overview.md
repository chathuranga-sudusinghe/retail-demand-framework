# Didilani — COMP1884 Group Project Contribution

## Member details

**Name:** Didilani Prasadika Weerawickrama Pathinayaka  
**Student ID:** 001560460

## Role

**Inventory-Risk Analytics, Replenishment Analysis, Visual Analytics, and Business Interpretation**

## Purpose in the group system

This component receives Chathuranga's demand forecast and translates it into inventory-risk and replenishment information using the inventory variables available in the selected dataset.

Didilani does **not** forecast demand a second time.

## Component research question

**How can demand forecasts and inventory-state variables be combined to identify inventory risk and support replenishment decisions?**

## Inputs

Primary inputs include:

- Chathuranga's forecast demand;
- `Inventory_Level`;
- `Reorder_Point`;
- `Supplier_Lead_Time_Days`;
- `Order_Quantity`;
- `Stockout_Flag` where informative;
- warehouse/product identifiers;
- forecast error or uncertainty where available.

## Responsibilities

1. Define the inventory-risk and replenishment logic.
2. Compare forecast demand with relevant inventory state and policy variables.
3. Identify conditions indicating stockout/replenishment pressure.
4. Identify conditions indicating excess/overstock pressure where defensible.
5. Develop a reproducible rules-based, scoring, or other justified analytical method.
6. Define and test thresholds rather than choosing them arbitrarily.
7. Produce replenishment recommendations where a defensible method can be implemented.
8. Create visual analytics that explain the risk/replenishment outputs.
9. Translate analytical outputs into business interpretation.
10. Produce outputs usable by Dewmi's responsible decision-support component.

## Candidate outputs

```text
SKU_ID
period
forecast_demand
inventory_level
reorder_point
supplier_lead_time
current/recent replenishment quantity
risk_level
risk_reason
recommended_replenishment_quantity, if justified
supporting_explanation
```

## Important boundary

The source dataset is simulated. Therefore, inventory levels and policy fields can be used as dataset variables, but conclusions must not be presented as validated operating rules for a real retailer.

A recommended replenishment quantity is a **decision-support recommendation**, not an automatically executable purchase order.

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
