# DR-011 — Responsible Decision-Support Output Structure

## Status

Accepted for structure only; upstream-dependent field contents remain provisional.

## Context

The project requires a management-facing decision-support output that brings together forecasting, inventory-risk, replenishment, uncertainty, evidence, assumptions, limitations, management consideration, and human-review information.

This Decision Record defines the structure of that output without prematurely fixing upstream-dependent methods, thresholds, formulas, or final column names.


## Decision

The responsible decision-support output will be organised into the following field groups:

- identity / time;
- forecast;
- forecast-error / uncertainty context;
- inventory risk;
- replenishment;
- evidence;
- assumptions;
- limitations;
- management consideration;
- human review.

These groups define the required structure without locking final column names, data types, formulas, thresholds, or implementation technology.


## Identity and Time Alignment

The output structure will preserve the following identity and time concepts:

- `SKU_ID`;
- `Warehouse_ID`;
- forecast-origin date;
- forecast horizon.

The approved forecasting horizons are:

- 1-day next-day demand;
- 7-day cumulative demand;
- 14-day cumulative demand.

Forecast origin and forecast horizon should be represented separately. An ambiguous single `period` field should not be used as the only temporal descriptor.


## Provenance and Source Distinction

Each field or field group should clearly identify the component that produced or owns the information.

The source components are:

- forecasting;
- inventory-risk / replenishment;
- responsible decision support.

Keeping these sources distinguishable supports traceability and helps managers understand where each part of the decision-support output comes from.


## Missing-Value Semantics

Some information may not be available when the decision-support output is produced. A missing value should not be shown as zero, because this could give managers the wrong impression.

The output should make it clear whether the information:

- cannot currently be produced because there is no agreed or defensible method;
- does not apply to that particular case; or
- is waiting for a decision or output from another part of the project.

Missing information should not simply be hidden. The reason it is unavailable should be clear to the person using the decision-support output.


## Human Review

The decision-support output should include a review status together with the reason, or reasons, why additional human review may be needed. A review flag on its own would not give enough information to the manager.

At this stage, specific human-review rules and thresholds have not been approved. Because of this, cases that have not yet been assessed should be shown as `not assessed` rather than `false`. Using `false` could wrongly suggest that the case has already been checked and is safe.

All outputs from the framework are advisory. The final decision remains with the responsible person. In the future, some cases may also be flagged for additional review once suitable rules have been agreed by the group.


## Advisory-Only Presentation

The framework is intended to support managers when making decisions, rather than making decisions for them. Any replenishment information or recommendation shown in the output should therefore be presented as guidance for consideration.

The output must not be treated as an automatic instruction, an automatically approved replenishment action, or an executable purchase order. A responsible person should remain involved in the final decision.


## Standing Limitations

There are some important limitations that should remain visible in the decision-support output.

The dataset used in this project is simulated, so the framework should not be presented as if it has already been tested as an operating policy in a real retail business.

The verified dataset also shows no variation in `Stockout_Flag`. For this reason, this field cannot be treated as observed evidence of actual stockout events or used to validate stockout predictions.

These limitations should remain clear when the framework and its outputs are presented to managers.


## Transparency and Explainability Evaluation

The prototype decision-support output will be checked using the transparency criteria identified in the responsible decision-support methodology. These criteria help us check whether a manager can understand what the output is showing and where the information comes from.

The eight criteria are:

- forecast visibility;
- risk visibility;
- recommendation traceability;
- uncertainty visibility;
- assumption visibility;
- limitation visibility;
- human-review transparency;
- source distinction.

These criteria are used to evaluate how clearly the prototype communicates its decision-support information. They do not, by themselves, prove that the framework improves trust or business performance.


## Dependency Status

Some parts of the output structure are already supported by approved project decisions, while others still depend on work being completed elsewhere in the project.

| Field group | Source / owner | Current status |
|---|---|---|
| Identity and forecast horizon | Forecasting | Approved |
| Forecast output | Forecasting | Approved in principle, subject to implementation |
| Forecast-error / uncertainty context | Forecasting | Pending further forecasting decision |
| Inventory-risk information | Inventory-risk / replenishment | Pending Issue #51 / DR-012 |
| Replenishment information | Inventory-risk / replenishment | Pending Issue #51 / DR-012 |
| Evidence and explanation | Responsible decision support | Structure approved; content remains provisional |
| Assumptions and limitations | Responsible decision support | Approved for inclusion |
| Management consideration | Responsible decision support | Structure approved; wording remains provisional |
| Human-review information | Responsible decision support | Structure approved; thresholds and rules remain pending |

This distinction allows the structure to be agreed without making decisions that belong to the forecasting or inventory-risk and replenishment parts of the project.


## Open Decisions and Out of Scope

This Decision Record does not finalise every detail of the decision-support output. The following areas remain open for later project decisions:

- final column names and data types;
- final file or interchange format;
- forecast uncertainty method;
- inventory-risk formulas, thresholds, levels, or labels;
- replenishment formulas and whether a replenishment quantity can always be produced;
- numerical human-review thresholds;
- definitions of terms such as high, extreme, or unusually large;
- rules for combining multiple human-review conditions;
- final explanation and management-consideration wording;
- segment or bias analysis design;
- dashboard or interface technology;
- final operationalisation of the group-level hypothesis.

Keeping these areas open avoids making decisions before the related forecasting, inventory-risk, and replenishment work has been completed and reviewed.


## Consequences

This decision gives the group a common structure that can later be used when the forecasting, inventory-risk, and replenishment components are brought together.

It also keeps the output transparent by showing where information comes from, what is still uncertain, and when human judgement is required. At the same time, some parts of the output cannot be finalised yet because they depend on decisions and results from other parts of the project.

Future implementation should follow this structure, but the provisional areas identified in this Decision Record may be updated when the relevant upstream decisions are approved.