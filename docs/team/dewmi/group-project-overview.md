# Dewmi — COMP1884 Group Project Contribution

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
SKU_ID / period
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
