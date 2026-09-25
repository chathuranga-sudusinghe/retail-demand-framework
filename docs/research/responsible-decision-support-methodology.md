# Responsible Decision-Support Methodology

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