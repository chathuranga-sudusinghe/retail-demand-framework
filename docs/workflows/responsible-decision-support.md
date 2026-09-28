# Responsible Decision-Support Workflow

> **Workflow revision — 2026-09-28:** The DR-011 output structure remains accepted for structure only. The revised forecasting interface is intended to include 1/7/14/28-day outputs; the 28-day forecasting revision remains under human review. Downstream 28-day interpretation, inventory use and human-review triggers remain separately pending. See the [central methodology-revision record](../forecasting-methodology-revision.md).

## Owner

Primary COMP1884 owner: **Dewmi**

## Goal

Convert forecast and inventory-risk/replenishment outputs into transparent management-facing decision-support information without presenting model recommendations as automatic managerial decisions.

## Workflow

```text
Demand forecast
  +
Inventory risk level
  +
Recommended replenishment quantity, if available
  +
Forecast uncertainty
  +
Risk / replenishment explanation
  +
Assumptions and limitations
        |
        v
Responsible decision-support logic
        |
        v
Management-facing decision-support view
        |
        v
Human review / managerial judgement
```

## Input boundary

The main analytical inputs are produced upstream:

- Chathuranga produces the demand forecast and forecast-evaluation information.
- Didilani produces the inventory-risk and replenishment outputs.
- Dewmi does not repeat those calculations; she converts them into a responsible decision-support presentation and human-review process.

## Required principles

### Transparency

The user should be able to understand:

- what demand was forecast;
- what inventory risk was identified;
- whether a replenishment quantity was recommended;
- what evidence and assumptions produced those outputs.

### Uncertainty

The framework should not hide forecast uncertainty or present a point forecast, risk level, or replenishment quantity as certain.

### Limitations

Known dataset, model, and decision-rule limitations should be visible and documented.

The source dataset is simulated, so the final interface must not imply that the recommendation has already been validated in a real operating retailer.

### Human oversight

The system supports human decisions; it does not replace managerial judgement or automatically execute replenishment orders.

### Responsible data use

Only project-relevant data should be used in the decision-support layer, with unnecessary identifiers excluded from management-facing outputs.

## Candidate output fields

```text
SKU_ID
Warehouse_ID
forecast_origin
forecast_horizon
forecast_demand
inventory_risk_level
recommended_replenishment_quantity
forecast_uncertainty
evidence
assumptions
limitations
management_consideration
human_review_flag
```

The replenishment field may be null or unavailable where Didilani's method does not produce a defensible quantity.

## Human-review direction

Candidate reasons to require explicit human review may include:

- high inventory risk;
- high forecast uncertainty;
- unusually large replenishment recommendation;
- conflict between inventory indicators;
- known data or model limitations.

Exact human-review rules must be documented before implementation.

## Evaluation direction

Before claiming that this layer "improves trust", "improves interpretability", or improves decision quality, the project must define measurable criteria for those concepts.


## Forecast identity and time alignment

The decision-support output should keep the forecasting context clear. Each forecast should be linked to its `SKU_ID`, `Warehouse_ID`, forecast origin, and forecast horizon.

Under the revised forecasting direction currently under human review, the forecast interface includes:

- 1-day next-day demand;
- 7-day cumulative demand;
- 14-day cumulative demand;
- 28-day cumulative demand (four-week / approximately monthly planning).

The 7-day, 14-day and 28-day values represent cumulative demand across their respective horizons, rather than demand for a single future day. Keeping the forecast origin and horizon visible helps avoid confusion when forecast information is combined with inventory-risk and replenishment outputs.

The overall output structure follows DR-011, while fields that depend on inventory-risk, replenishment, uncertainty, or human-review rules remain provisional until the related project decisions are approved.

## Revised forecasting interface and owner review

Under the revised forecasting direction, the forecast interface is intended to
support 1-day next-day and cumulative 7/14/28-day demand from one fixed origin.
Cumulative quantities do not imply a daily forecast path. Preserve origin and horizon in explanations; 28 days is
four weeks / approximately monthly planning, not an exact calendar month.
**28-day downstream use requires component-owner/human approval.** Do not populate
28-day inventory states, replenishment recommendations or human-review triggers
by silently extending another component's proposed method. Unavailable/unapproved
outputs need an explicit reason. No uncertainty method, threshold or decision rule
is approved by this interface update. Ownership and existing responsible-use
principles remain unchanged. Where reporting uses results from the revised final evaluation interval, disclose its prior validation exposure in accordance with DR-005.
