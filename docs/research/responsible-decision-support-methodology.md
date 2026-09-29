# Responsible Decision-Support Methodology

> **Documentation alignment — 2026-09-29:** DR-011 remains accepted for structure only. Upstream direct 1/7/14/28-day forecasting and its [feature contract](../forecasting-feature-engineering.md) are human-approved. Downstream 28-day use and substantive inventory/replenishment/uncertainty/review rules require their separate owner/human approvals. No experiment execution is authorised. See [current approval and provenance](../forecasting-methodology-revision.md).

## 1. Problem Definition

This project combines demand forecasting with inventory-risk and replenishment analysis to support retail decision-making. However, a forecast or replenishment recommendation should not be presented to a manager as an automatic or unquestionable decision. Forecasts can contain errors and uncertainty, while inventory-risk outputs also depend on the available data, assumptions, and methods used in the project.

The purpose of this component is therefore to define how these analytical outputs can be communicated to managers in a transparent and responsible way. The decision-support layer should show the forecast, inventory-risk information, replenishment recommendation where available, supporting evidence, uncertainty, assumptions, and important limitations. It should also identify situations where human review may be appropriate.

The framework is intended to support managerial judgement rather than replace it. It will not automatically approve or execute replenishment orders. This is particularly important because the project uses a simulated dataset and cannot demonstrate how the framework would perform in a real retail organisation without further validation.

### Component Research Question

**How can forecast uncertainty, inventory-risk/replenishment information, transparency, and governance considerations be incorporated into responsible retail decision support?**

## 2. Literature Evidence

Responsible decision support requires more than presenting a forecast or replenishment value. The information should be communicated in a way that helps the manager understand the evidence, assumptions, uncertainty, and limitations behind the recommendation.

Kosasih et al. (2024) identify limited explainability as a barrier to the wider use of AI-based systems in supply-chain management. This supports making the reasoning and evidence behind analytical outputs visible rather than presenting only a final recommendation.

Olan et al. (2024) examine explainable AI in supply-chain decision support and emphasise the role of explanation in supporting informed decision-making. For this project, this means that forecast and inventory-risk outputs should be accompanied by understandable supporting information.

Reis et al. (2025) provide further support for a human-centred approach. Their decision-support system considers stakeholder needs when selecting explanation methods and incorporates a human-in-the-loop. This suggests that explanations should be designed for the management decision being supported rather than added only as a technical feature.

Based on this literature, the responsible decision-support layer in this project should communicate the forecast and relevant period, inventory-risk evidence, uncertainty where available, the reasoning behind a replenishment recommendation, important assumptions and limitations, and situations requiring human review. The system should support managerial judgement rather than automatically execute replenishment decisions.

## 3. Candidate Decision-Support Fields

The decision-support view needs to give managers enough information to understand the output before acting on it. The fields below are proposed from the current project requirements and expected upstream outputs. They are not yet a final cross-component schema.

| Candidate field | Purpose |
| --- | --- |
| `SKU_ID` | Identifies the product linked to the output. |
| `Warehouse_ID` | Identifies the relevant warehouse. |
| `period` | Shows the period covered by the forecast or decision. |
| `forecast_demand` | Shows the demand forecast produced by the forecasting component. |
| `inventory_risk_level` | Shows the inventory-risk assessment received from the inventory-risk component. |
| `recommended_replenishment_quantity` | Shows a replenishment quantity where the upstream method provides a justified value. |
| `forecast_uncertainty` | Communicates available forecast-error or uncertainty information. |
| `evidence` | Summarises the main evidence supporting the risk assessment or recommendation. |
| `assumptions` | Makes relevant assumptions visible to the manager. |
| `limitations` | Shows important data, model, or methodological limitations and warnings. |
| `management_consideration` | Provides information for managerial consideration without presenting it as an automatic instruction. |
| `human_review_flag` | Indicates whether explicit human review is required under an approved review method. |

These fields remain candidates because the final outputs from the forecasting and inventory-risk components are still being developed. A field should only be included when the required information is actually available from the upstream analysis. For example, the system should not display a replenishment quantity or uncertainty value if a defensible value has not been produced.

The final field names, formats, and cross-component schema therefore remain subject to group agreement.

## 4. Candidate Human-Review Conditions

Human review should be used when the available evidence suggests that a case needs additional managerial judgement. At this stage, the project does not have enough evidence to justify fixed numerical thresholds. The conditions below are therefore candidates for later formalisation rather than final rules.

| Candidate condition | Why human review may be appropriate |
| --- | --- |
| High forecast uncertainty | A manager may need to treat the forecast with additional caution when uncertainty is high. |
| Conflicting evidence | Forecast, inventory, or replenishment indicators may not point towards the same conclusion. |
| Extreme forecast or risk value | An unusual result may need checking before it influences a replenishment decision. |
| Missing or weak supporting evidence | A recommendation should not be treated as reliable when important supporting information is unavailable. |
| Important data or model limitation | Known limitations may reduce how confidently the output can be used. |
| Unusually large replenishment recommendation | A recommendation with potentially greater operational impact may justify additional review. |

These conditions do not yet define when `human_review_flag` becomes true. In particular, terms such as "high", "extreme", and "unusually large" do not have approved numerical thresholds at this stage.

A later methodology decision should define how these conditions are measured and combined before they are implemented as decision rules. Until that decision is approved, the framework should not silently convert these candidate conditions into automatic thresholds.

Human review should also remain meaningful. A review flag should direct the manager towards the evidence, uncertainty, assumptions, or limitations that caused the case to be flagged rather than displaying a warning without explanation.

## 5. Transparency and Explainability Evaluation Criteria

Transparency and explainability should be evaluated using observable criteria rather than broad claims about trust or decision quality. The purpose of the evaluation is to check whether the management-facing output provides the information required to understand and review a recommendation.

The following criteria are proposed for the prototype:

| Evaluation criterion | How it can be checked |
| --- | --- |
| Forecast visibility | Check whether the forecast value and relevant period are clearly displayed. |
| Risk visibility | Check whether the inventory-risk level and supporting evidence are shown. |
| Recommendation traceability | Check whether a replenishment recommendation, where available, is accompanied by the evidence or reason supporting it. |
| Uncertainty visibility | Check whether available forecast uncertainty or error information is presented rather than hidden. |
| Assumption visibility | Check whether relevant assumptions are accessible to the manager. |
| Limitation visibility | Check whether important data and model limitations are clearly communicated. |
| Human-review transparency | Check whether a review flag is accompanied by the reason that triggered the review. |
| Source distinction | Check whether forecast, inventory-risk, and decision-support information can be distinguished rather than appearing as one unexplained output. |

These criteria can initially be assessed using a structured checklist against prototype outputs. The project can report how many required elements are present and whether each element is understandable and traceable to the available analytical evidence.

This evaluation would demonstrate whether the prototype meets its defined transparency requirements. It would not, by itself, prove improved user trust, better managerial decisions, or improved business performance. Claims about those outcomes would require separate evaluation with appropriate users and measurable evidence.

## 6. Assumptions

The proposed decision-support approach depends on several assumptions that should be made clear before it is used. First, the forecasting and inventory-risk outputs are assumed to have been produced using the agreed analytical unit and the methods documented elsewhere in the project. This section does not independently validate those models or redefine their calculations.

The framework also assumes that the information presented to a manager can be traced back to the available analytical evidence. A recommendation should therefore not appear on its own. Where possible, it should be shown together with the relevant forecast, inventory-risk information, uncertainty, and the reason for the recommendation.

Another assumption is that the system is intended to support rather than replace managerial judgement. The proposed human-review conditions are therefore treated as safeguards for cases where uncertainty, limited evidence, or potentially important consequences make automatic interpretation inappropriate.

Finally, the project uses simulated supply-chain data rather than observed data from a real retail organisation. The methodology can demonstrate how responsible decision support could be structured, but its effectiveness in a real operational setting would require further evaluation with appropriate users and real-world evidence.

## 7. Ethical, Legal, and Governance Considerations

The decision-support framework should be used in a way that supports responsible managerial decision-making. Forecasts, inventory-risk indicators, and replenishment recommendations may influence operational decisions, so managers should be able to understand the evidence behind an output before acting on it. The framework should therefore avoid presenting analytical outputs as automatic decisions and should preserve appropriate human oversight, particularly when uncertainty is high or the available evidence is limited.

Governance is also important because the analytical output needs to remain traceable. Where a recommendation is presented, the relevant forecast, inventory information, assumptions, and limitations should be available for review. This helps managers understand how the recommendation was reached and avoids treating the system as a black-box decision maker. Responsibility for the final operational decision should remain with the appropriate human decision maker rather than being transferred to the analytical system.

From an ethical perspective, the system should avoid giving managers a false sense of certainty. Forecasts and inventory-risk outputs are based on models and assumptions, and their limitations should remain visible when they are used for decision support. The current dataset does not contain the type of personal customer or employee information needed for a detailed assessment of privacy, discrimination, or individual rights. These issues can therefore be recognised as wider responsible-AI concerns, but the project should not claim that it has empirically tested them.

The use of project data and analytical outputs should also follow clear governance practices. Important assumptions, changes to the methodology, and any future decision thresholds should be documented so that the group can review how the framework develops. Replenishment recommendations should remain advisory rather than triggering automatic actions. This keeps responsibility with the human decision maker and allows unusual or uncertain cases to be reviewed before action is taken.

## 8. Limitations

This methodology has several limitations that should be considered when interpreting the decision-support outputs. The project is based on simulated supply-chain data rather than data collected from a real retail organisation. As a result, the framework can be used to demonstrate how forecasting and inventory-risk information could support decisions, but it cannot show how well the approach would perform under real operational conditions.

Another limitation is that the quality of the decision-support output depends on the quality of the forecasting and inventory information provided by the earlier analytical stages. If these inputs are incomplete or inaccurate, the resulting risk information and replenishment recommendation may also be affected. For this reason, the framework should present these outputs as decision-support evidence rather than as guaranteed outcomes.

A further limitation is that the project does not yet have evidence from real managers using the proposed decision-support output. The transparency criteria can be used to check whether important information is visible and traceable, but they cannot demonstrate that the framework improves trust, decision quality, or business performance. Claims about these outcomes would require separate evaluation with appropriate users and measurable evidence.

## 9. Recommended Methodology Direction

The recommended direction is to develop the decision-support component as a transparent layer between the analytical outputs and the final managerial decision. Rather than producing a replenishment recommendation alone, the framework should bring together the demand forecast, relevant inventory-risk information, available uncertainty information, and the reason behind the recommendation. This gives the manager enough context to review the evidence before deciding what action to take.

At this stage, the methodology should remain flexible rather than introducing fixed decision thresholds that have not yet been validated. Human-review conditions can be refined later using evidence from the forecasting and inventory-risk components. Any thresholds or decision rules introduced at that stage should be documented clearly and agreed by the group before they are treated as part of the final framework.

## 10. Decisions Still Requiring Group Approval

Some parts of the decision-support methodology still require agreement from the group before they can be treated as final. This is particularly important where the decision-support component depends on outputs from the forecasting and inventory-risk components. The following decisions should therefore remain open until the relevant evidence and group discussion are available.

- The final set of fields that will appear in the management-facing decision-support output.
- The method used to represent forecast uncertainty and how it should be communicated to managers.
- The conditions or thresholds that should trigger human review.
- How inventory-risk evidence should be combined with the demand forecast when producing a replenishment recommendation.
- The final wording and level of detail used to explain the reason behind each recommendation.

## 11. Current Decision Record and Provisional Contents

[DR-011](../decisions/DR-011-decision-support-output-structure.md) defines the management-facing output structure and is accepted for structure only. Fields depending on inventory-risk, replenishment, forecasting uncertainty, recommendation rules or human-review thresholds remain provisional until their related methodology decisions are approved. This structural acceptance does not approve substantive downstream logic. No thresholds should be invented; unresolved thresholds remain open.

## Revised forecasting interface and owner review

The human-approved upstream forecast interface supports 1-day next-day and cumulative 7/14/28-day demand from one fixed origin.
Cumulative quantities do not imply a daily forecast path. Preserve origin and horizon in explanations; 28 days is
four weeks / approximately monthly planning, not an exact calendar month.
**28-day downstream use requires component-owner/human approval.** Do not populate
28-day inventory states, replenishment recommendations or human-review triggers
by silently extending another component's proposed method. Unavailable/unapproved
outputs need an explicit reason. No uncertainty method, threshold or decision rule
is approved by this interface update. Ownership and existing responsible-use
principles remain unchanged. Where reporting uses results from the revised final evaluation interval, disclose its prior validation exposure in accordance with DR-005.
