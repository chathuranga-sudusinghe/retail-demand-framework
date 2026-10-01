# Responsible Decision-Support Methodology

Repository-wide authorities: [data lifecycle](../workflows/shared-data-foundation.md), [storage and retention](../artifact-storage-policy.md), [applied MLOps](../workflows/applied-mlops.md), [research reporting](../../reports/README.md), and [continuous progress log](../research-progress.md). These connect existing scientific/component contracts without replacing them.

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


## 12. Measurable Responsible Decision-Support and Human-Review Criteria

### 12.1 Evaluation Unit

For this evaluation, each management-facing decision-support record will be treated as one evaluation unit. The record should be linked clearly to the relevant `SKU_ID`, `Warehouse_ID`, forecast origin and forecast horizon so that the information can be traced back to the correct forecasting and inventory context.

The main purpose of the evaluation is to check whether a manager can understand the information provided before using it to support a decision. This includes checking what evidence is available, where the information has come from, what information is still missing or has not been assessed, and which parts still require human judgement.

Where reviewed forecasting and inventory-risk outputs are available, they will be used as the supporting evidence. This part of the research will not recalculate forecasts, change the agreed inventory-risk method, or create new replenishment quantities. Those outputs remain the responsibility of their respective project components.

### 12.2 Measurable Transparency Checks

The transparency checks focus on information that can be observed directly in the decision-support record. Each check can be recorded as `met`, `not met`, or `not assessable`, with a short reason where needed.

| Check | What will be reviewed |
| --- | --- |
| Forecast visibility | Whether the forecast value, forecast origin and horizon are clearly shown. |
| Risk visibility | Whether the available inventory-risk result and its supporting evidence are visible. |
| Recommendation traceability | Whether a replenishment recommendation, when available, can be traced to the evidence supporting it. |
| Uncertainty visibility | Whether available forecast-error or uncertainty information is shown rather than hidden. |
| Assumption visibility | Whether assumptions that affect interpretation are visible to the manager. |
| Limitation visibility | Whether relevant data or model limitations are clearly stated. |
| Human-review transparency | Whether a human-review state is accompanied by a reason explaining why it is present. |
| Source distinction | Whether forecasting, inventory-risk and responsible decision-support information can be distinguished from each other. |

A check should not be marked as failed simply because an upstream component has not produced the required information. In that situation, the result should be recorded as `not assessable`, together with the reason the evidence is unavailable. This avoids treating missing information as if it were a valid zero or false value.

### 12.3 Missing and Unavailable Information

Missing information needs to be shown clearly because it can affect how a manager interprets the decision-support record. A blank value should not automatically be treated as zero, and unavailable information should not be hidden.

Where information is missing, the record should distinguish between the following situations:

- `not produced` – the information cannot currently be produced because there is no approved or defensible method;
- `not applicable` – the information does not apply to the particular record;
- `pending upstream output` – the information depends on another project component and is not yet available;
- `not assessed` – the relevant evaluation or human-review check has not yet been completed.

A short reason should be recorded with the status where it is needed to understand why the information is unavailable.

These states are intended to make missing information visible rather than fill the gap with an assumed value. They do not introduce a new forecasting, inventory-risk or replenishment rule.

### 12.4 Human-Review Protocol

Human review should be represented as a clear state rather than a simple true or false value. This is important because a false value could be misunderstood as meaning that no review is needed, even when the review criteria have not yet been assessed.

For evaluation purposes, the decision-support record should show whether human review has been assessed and, where additional review is required, explain the reason. If the review has not yet been assessed, this should be shown explicitly as `not assessed`.

A review reason should point back to the information that caused the concern, such as conflicting evidence, missing supporting information, an important limitation, or another condition defined by an approved downstream rule. This allows a manager to understand why the record needs additional attention instead of seeing an unexplained warning.

This protocol does not define numerical thresholds for triggering human review. Those thresholds and decision rules should only be applied after they have been agreed by the relevant component owners. Regardless of the review state, the output remains advisory and the final decision stays with the human reviewer.

### 12.5 Evaluation Recording

The results of the responsible decision-support evaluation should be recorded in a simple and consistent way. For each decision-support record, the applicable transparency checks should be reviewed and their outcome recorded as `met`, `not met`, or `not assessable`.

Where a check is marked as `not met` or `not assessable`, a short reason should also be included. This provides evidence for the evaluation and makes it possible to identify which parts of the decision-support output need further improvement.

The evaluation can then report the number or proportion of records meeting each transparency check. These results describe how consistently the prototype presents the required information. They should not be interpreted as evidence that the system improves managerial trust, business performance or decision quality, as those outcomes would require a separate form of evaluation.

### 12.6 Interpretation of the Evaluation

The evaluation results will be used to show how consistently the prototype meets the responsible decision-support criteria defined in this methodology. They can also help identify areas where information is unclear, missing or difficult to trace back to its source.

A high number of `met` results would indicate that the required information is being presented consistently. However, this should not be taken as proof that managers trust the system more or make better decisions because of it. Those outcomes are outside the scope of this evaluation unless they are tested separately with suitable evidence.

Any `not met` or `not assessable` results should be reported rather than removed from the evaluation. This is particularly important where the result depends on an upstream method or decision that has not yet been approved.

The findings should therefore be interpreted as evidence about the transparency and reviewability of the prototype, rather than evidence of improved business performance or automatic decision-making.

### 12.7 Supported and Unsupported Claims

The evaluation should separate conclusions that are supported by the available evidence from claims that have not been tested in this project.

The evaluation can support statements about whether the required decision-support information is present, whether its source can be identified, whether missing information is made explicit, and whether human-review reasons are visible and traceable to the available evidence.

It cannot, on its own, support claims that the decision-support approach improves manager trust, leads to better decisions, reduces inventory costs, improves business performance or performs effectively in a real retail environment. These outcomes have not been evaluated through this methodology.

Any conclusion reported from this evaluation should therefore remain within the evidence actually produced by the project. Unsupported claims should be identified as outside the current evaluation rather than presented as project findings.

### 12.8 Upstream Dependencies

The responsible decision-support evaluation depends on reviewed outputs from other parts of the project. Forecast information should come from Chathuranga's reviewed forecasting outputs and the agreed forecasting-facing contract. Inventory-risk evidence and its interpretation should come from Didilani's reviewed inventory-risk work.

These dependencies should remain visible when the decision-support record is evaluated. If an expected upstream output is unavailable or has not yet been approved, it should be shown as unavailable rather than treated as complete or replaced with an assumed value.

This methodology does not recalculate forecasting outputs or redefine the inventory-risk method. It uses reviewed upstream evidence where it is available and keeps any remaining gaps explicit.

### 12.9 Handoff and Implementation Boundary

This research note defines the responsible decision-support meaning, evaluation criteria and human-review requirements. The next stage is Issue #73, where responsible decision-support records can be created and tested against these requirements.

The implementation should preserve the transparency checks, missing-information states, human-review reasons, assumptions, limitations and source distinctions defined here. Any information that depends on an upstream component should remain identifiable rather than being replaced with an assumed value.

Tinosh may later support the technical presentation or integration of reviewed decision-support records. This does not transfer ownership of the responsible-use methodology or human-review logic. Changes to these criteria should remain under Dewmi's responsible decision-support component and follow the project's review process.

The resulting output remains advisory. It should support management review and should not be treated as an automatic approval or replenishment instruction.

