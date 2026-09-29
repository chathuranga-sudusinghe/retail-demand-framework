# Dewmi — COMP1884 Group Project Contribution

> **Documentation alignment — 2026-09-29:** DR-011 remains accepted for structure only. Upstream direct 1/7/14/28-day forecasting and its [feature contract](../../forecasting-feature-engineering.md) are human-approved. Downstream 28-day use and substantive inventory/replenishment/uncertainty/review rules require their separate owner/human approvals. No experiment execution is authorised. See [current approval and provenance](../../forecasting-methodology-revision.md).

## Member details

**Name:** Haputhanthrige Dewmi Pramodya  
**Student ID:** 001560683

## Role

**Responsible Decision Support, Ethical/Legal/Governance Analysis, and Human Oversight**

## Purpose in the group system

This component receives the demand forecast and Didilani's inventory-risk/replenishment outputs and converts them into transparent, responsible management-facing decision-support information.

It ensures that forecasts, risk levels, and replenishment recommendations are not presented as unquestionable automated decisions. The layer should communicate uncertainty, evidence, assumptions, limitations, and appropriate human oversight.

## Component research question

**How can forecast uncertainty, inventory-risk/replenishment information, transparency, and governance considerations be incorporated into responsible retail decision support?**

## Hypothesis status

A separate statistical H0/H1 is **not required for this component under the current research design**.

The full project is guided by the primary group-level hypothesis, while this component is evaluated through its research question and explicit criteria for transparency, governance, robustness, and human oversight. A separate component hypothesis should only be introduced later if a justified measurable statistical relationship is formally defined.

## Inputs

- Chathuranga's demand forecasts;
- model-error information;
- forecast uncertainty where available;
- Didilani's inventory-risk level/output;
- recommended replenishment quantity where available and justified;
- risk/replenishment explanation or evidence;
- explanatory metadata;
- assumptions and limitations.

## Responsibilities

1. Define how the system communicates forecast and inventory-risk uncertainty.
2. Present replenishment recommendations with their evidence, assumptions, and limitations.
3. Document data and model limitations, including the simulated nature of the source dataset.
4. Analyse transparency and explainability requirements.
5. Examine potential bias or uneven behaviour across relevant segments where methodologically justified.
6. Define appropriate human-in-the-loop decision points.
7. Develop responsible decision-support rules and presentation logic.
8. Address ethical, legal, and governance considerations.
9. Ensure the framework supports rather than replaces managerial judgement.
10. Contribute to robustness/sensitivity evaluation where feasible.

## Candidate decision-support output

```text
SKU_ID
Warehouse_ID
Forecast origin
Forecast horizon: 1-day next-day demand, 7-day cumulative demand, 14-day cumulative demand, and 28-day cumulative demand
Forecast demand
Inventory risk level
Recommended replenishment quantity, if available
Forecast uncertainty / confidence information
Evidence / main drivers
Assumptions
Limitations / warnings
Suggested management consideration
Human review required
```

"Suggested management consideration" and any replenishment recommendation must not be presented as an automatically authoritative business decision or executable purchase order.

## Definition of done

- responsible-use principles are operationalised in the prototype;
- forecast, risk, and replenishment outputs are presented transparently;
- uncertainty and limitations are visible to the user;
- risk/replenishment outputs are explainable at an appropriate level;
- human oversight points are defined;
- ethical/legal/governance issues are documented;
- evaluation criteria for transparency/robustness are reported.

## Scope boundary

Dewmi does not calculate the primary demand forecast or the inventory replenishment recommendation.

Her component consumes the outputs of Chathuranga and Didilani and implements the responsible-use and decision-support layer of the integrated data-science product. This contribution is therefore not an ethics essay attached after modelling.


## Decision-support output alignment

The responsible decision-support layer will keep the forecasting identity and timing information visible when it combines outputs from the different project components. This includes `SKU_ID`, `Warehouse_ID`, the forecast origin, and the forecast horizon.

The approved upstream forecast-interface horizons are:

- 1-day next-day demand;
- 7-day cumulative demand;
- 14-day cumulative demand;
- 28-day cumulative demand (four-week / approximately monthly planning).

The 7-day, 14-day and 28-day forecasts represent cumulative demand over those periods; 28 days is four-week / approximately monthly planning, not an exact calendar month. This information should remain clear when forecasts are combined with inventory-risk and replenishment information.

DR-011 defines the overall structure for this management-facing output. Details that depend on forecasting uncertainty, inventory-risk methods, replenishment rules, or human-review thresholds will remain provisional until the relevant group decisions are approved.

## Revised forecasting interface and owner review

The human-approved upstream forecast interface supports 1-day next-day and cumulative 7/14/28-day demand from one fixed origin.
Cumulative 7/14/28-day quantities do not imply a daily forecast path. Preserve origin and horizon in explanations; 28 days is
four weeks / approximately monthly planning, not an exact calendar month.
**28-day downstream use requires component-owner/human approval.** Do not populate
28-day inventory states, replenishment recommendations or human-review triggers
by silently extending another component's proposed method. Unavailable/unapproved
outputs need an explicit reason. No uncertainty method, threshold or decision rule
is approved by this interface update. Ownership and existing responsible-use
principles remain unchanged. Where reporting uses results from the revised final evaluation interval, disclose its prior validation exposure in accordance with DR-005.
