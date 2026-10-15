# Responsible Decision-Support Evaluation

**Status:** Draft for human review. Evaluation evidence is pending; this document does not complete Issue #145.

## 1. Purpose

This document prepares the responsible decision-support evaluation and presentation handoff for [Issue #145](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/145). It follows the existing measurable transparency criteria in the [approved methodology](responsible-decision-support-methodology.md#12-measurable-responsible-decision-support-and-human-review-criteria) and [DR-011](../decisions/DR-011-decision-support-output-structure.md).

The purpose is to assess whether reviewable decision-support records preserve the information needed for responsible management-facing interpretation. Each applicable transparency check is recorded as `met`, `not met`, or `not assessable`, with a short reason where required.

This evaluation does not recalculate forecasts, redefine inventory-risk methods, create replenishment quantities or thresholds, or introduce new uncertainty methods. Information that is unavailable or not yet approved remains explicitly unavailable rather than being replaced with an assumed value.

The evaluation is limited to the transparency and responsible-use characteristics that can be observed from the available records and reviewed upstream evidence. It does not provide evidence of improved user trust, managerial decision quality, business performance, inventory cost, or real-world effectiveness.

## 2. Evaluation Criteria

The check names below match [methodology §12.2](responsible-decision-support-methodology.md#122-measurable-transparency-checks). Issue #145's terms map to the same checks: inventory-risk visibility means Risk visibility; uncertainty/error visibility means Uncertainty visibility; assumptions/limitations visibility means Assumption/Limitation visibility; and source/component distinction means Source distinction. Recommendation traceability applies where a recommendation is defensibly available, as specified in Issue #145; this document introduces no new replenishment method or availability rule.

| Transparency check | What is reviewed |
|---|---|
| Forecast visibility | Whether the forecast value, forecast origin, and forecast horizon are clearly shown. |
| Risk visibility | Whether the available inventory-risk result and its supporting evidence are visible. |
| Recommendation traceability | Whether a replenishment recommendation, when defensibly available, can be traced to the evidence supporting it. |
| Uncertainty visibility | Whether available forecast-error or uncertainty information is shown rather than hidden. |
| Assumption visibility | Whether assumptions that affect interpretation are visible to the manager. |
| Limitation visibility | Whether relevant data or model limitations are explicitly presented. |
| Human-review transparency | Whether the human-review status and its reasons are visible and interpretable. |
| Source distinction | Whether forecasting, inventory-risk/replenishment, and responsible decision-support information remain distinguishable by source or provenance, using DR-011's component grouping. |

For each applicable check, the assessment outcome is recorded as `met`, `not met`, or `not assessable`. Where a check is `not met` or `not assessable`, a short reason is retained so that the evidence and limitation remain traceable.

### Proposed 20-Row Forecast Evidence Selection (Pending Scope Approval)

This is a purposive, case-based selection of 20 forecasting rows from the retained Issue #132 fixed-origin export. These rows are not yet verified as completed `DecisionSupportRecord` instances, and the selection does not claim population-wide representativeness.

| Assessment IDs | SKU_ID | Warehouse_ID | Forecast origin | Horizons (days) | Rows |
|---|---|---|---|---|---|
| F01–F04 | SKU_1 | WH_1 | 2024-12-02 | 1, 7, 14, 28 | 4 |
| F05–F08 | SKU_5 | WH_2 | 2024-12-02 | 1, 7, 14, 28 | 4 |
| F09–F12 | SKU_10 | WH_3 | 2024-12-02 | 1, 7, 14, 28 | 4 |
| F13–F16 | SKU_15 | WH_4 | 2024-12-02 | 1, 7, 14, 28 | 4 |
| F17–F20 | SKU_20 | WH_5 | 2024-12-02 | 1, 7, 14, 28 | 4 |

**Selection rule:** The five SKU–warehouse combinations were chosen using SKU numbers 1, 5, 10, 15 and 20, paired with warehouses 1–5 respectively. All four horizons are retained for each pair. The rule supports comparison across horizons and selected SKU–warehouse combinations but is not a representative sample.

**Source and version:** `issue-132-forecast-export-v1.json`; export schema `issue-132-forecast-export-v1`; handoff `final-20261003-02`; forecast origin `2024-12-02`. The retained export contract is documented in `docs/forecast-api-contract.md`. One-day predictions represent next-day demand; 7-, 14- and 28-day predictions represent cumulative-window demand. Forecast uncertainty is reported unavailable (`no_agreed_method`).

**Proposed record linkage:** Each selected forecast row will be traced by SKU_ID, Warehouse_ID, forecast origin and horizon against `src/decision_support/records.py`. Forecast predictions and provenance can inform the corresponding record fields, but no automatic record-generation or completed-record match has yet been established. The mapping between numeric export horizons and the string-valued `forecast_horizon` field requires confirmation. Test fixtures must not be treated as evaluated project records.

**Downstream evidence boundary:** Reviewed inventory-risk and replenishment outputs will be linked only where an actual matching source exists. Missing evidence will be recorded explicitly with record-specific reasons rather than replaced with assumptions or used to silently exclude reviewable cases. Pending inventory-risk decisions under Issue #164 remain dependencies. The 28-day horizon is retained for forecast-transparency assessment only; downstream inventory and replenishment interpretation remains deferred.

**Assessment status:** Selection proposed for Chathuranga's scope review. The eight transparency checks have not yet been applied to these rows. The readiness register below remains distinct from a completed record-level assessment matrix.


## 3. Evaluation Readiness and Pending Evidence

No identified decision-support record has been evaluated in this document. The table below is a readiness register, not a completed assessment matrix. Its `not assessable` entries describe evidence gaps; they must not be counted as observed record-level outcomes. Missing or unapproved upstream information is not replaced with assumed values.

| Record | Transparency check | Outcome | Evidence / reason |
|---|---|---|---|
| To be assessed | Forecast visibility | `not assessable` | Awaiting identification of the reviewable record and corresponding reviewed forecasting evidence. |
| To be assessed | Risk visibility | `not assessable` | Awaiting identification of the reviewable record and corresponding reviewed inventory-risk evidence. |
| To be assessed | Recommendation traceability | `not assessable` | A defensible replenishment recommendation and supporting evidence must be available before this check can be assessed. |
| To be assessed | Uncertainty visibility | `not assessable` | Reviewed uncertainty or forecast-error information must be available before this check can be assessed. |
| To be assessed | Assumption visibility | `not assessable` | The applicable record must be reviewed before the visibility of assumptions can be assessed. |
| To be assessed | Limitation visibility | `not assessable` | The applicable record must be reviewed before the visibility of limitations can be assessed. |
| To be assessed | Human-review transparency | `not assessable` | The applicable record must be reviewed for human-review status and explanatory reasons. |
| To be assessed | Source distinction | `not assessable` | The applicable record and its provenance information must be reviewed before source distinction can be assessed. |

Before recording an assessment, identify each reviewed record using `SKU_ID`, `Warehouse_ID`, forecast origin and horizon, together with its source artifact/version and upstream provenance. For each applicable check, retain the outcome and a record-specific evidence reference or reason. Do not treat a checklist row as a reviewed record or treat an unperformed review as an observed failure.

## 4. Current Findings and Reporting Limits

- This draft contains **0 identified evaluated records**. It reports no measured completion rate, proportion of checks met, or prototype evaluation result.
- Issues [#72](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/72) and [#73](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/73) provide the approved criteria and record implementation. Their completion does not by itself establish evaluated management-facing outputs.
- The [forecast contract](../forecast-api-contract.md) from [Issue #132](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/132) provides reviewed forecasting semantics. Actual assessment must cite the record and evidence used; it must not infer a record's completeness from contract acceptance alone.
- Inventory-dependent findings require reviewed evidence and interpretation from [Issue #85](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/85). Its pending work does not prevent preparation of the presentation requirements below.
- When results are available, report the number of reviewed records, the applicable population for each check, and counts for `met`, `not met` and `not assessable`. Identify the denominator of every reported proportion and retain unavailable cases visibly. Do not calculate a percentage from a zero denominator.
- Synthetic/test records, if reviewed, must be labelled as such and kept distinguishable from assessments using accepted project evidence. Passing implementation tests does not establish presentation quality or operational effectiveness.

## 5. Semantic/Presentation Handoff for Tinosh

The requirements below restate existing methodology and record semantics for human review. They do not introduce a new schema, adapter, uncertainty method or review rule. The current implementation is [DecisionSupportRecord](../../src/decision_support/records.py); technical integration must preserve the reviewed meaning rather than infer unavailable values.

| Information | Presentation requirement |
|---|---|
| Identity and timing | Keep `sku_id`, `warehouse_id`, `forecast_origin` and `forecast_horizon` visible and traceable. Preserve source artifact/version references where available. |
| Forecast | Show `forecast_demand` with its units and horizon meaning. One day means next-day demand; 7/14/28 days mean cumulative demand over the complete window, not a daily path. Twenty-eight days means four weeks, not an exact calendar month ([forecast contract §5](../forecast-api-contract.md#5-forecast-meaning)). |
| Provenance | Preserve `forecast_provenance`, `inventory_risk_provenance` and `component_provenance`. Distinguish forecasting, inventory-risk/replenishment and responsible decision-support sources. |
| Inventory-risk evidence | Present `inventory_risk_evidence` using Didilani's reviewed labels, assumptions and interpretation. Do not relabel threshold-exposure evidence as observed stockout prediction or derive overstock from absence of a crossing. |
| Replenishment | Show `replenishment_recommendation` only when defensibly supplied under an approved method, with its supporting evidence. Keep it advisory; do not present it as an approved purchase order. |
| Error and uncertainty | Preserve the meaning and source of `uncertainty_or_error`. Retrospective forecast error is evaluation evidence, not prospective confidence or an uncertainty interval ([forecast contract §6.2](../forecast-api-contract.md#62-fields-excluded-from-prospective-views)). The forecast contract's `unavailable` / `no_agreed_method` uncertainty information remains explicit. |
| Unavailable information | Show the field and its reason from `unavailable_fields`. Preserve the meanings of `not produced`, `not applicable`, `pending upstream output` and `not assessed` from [methodology §12.3](responsible-decision-support-methodology.md#123-missing-and-unavailable-information). Do not silently map missing information to zero, false or a recommendation. These evaluation states do not define an interchange encoding or authorize automatic mapping of upstream reason codes. |
| Assumptions and limitations | Keep `assumptions`, `limitations` and `evidence` accessible alongside the result. Preserve the publisher-simulated Kaggle-dataset limitation and the fact that zero-variance `Stockout_Flag` cannot validate stockout predictions. Retain any evidence-specific temporal or methodological limitations. |
| Management consideration | Present `management_consideration` as guidance for human consideration. Final decisions remain with a responsible person; presentation must not imply autonomous ordering. |
| Human review | Show `human_review_status` together with `human_review_reasons`. `not_assessed` means review has not been assessed; it is not clearance. `review_required` must retain its stated reason. Do not invent triggers or numerical thresholds. |
| Twenty-eight-day downstream use | Retain approved forecast identity, but do not imply approval of 28-day inventory interpretation, replenishment or human-review triggers. Show the relevant unavailability/approval reason until separately approved ([forecast contract §10](../forecast-api-contract.md#10-shared-forecasting-api-boundaries); [DR-011 component-review boundary](../decisions/DR-011-decision-support-output-structure.md#revised-forecasting-interface-and-component-review)). |

DR-011 explains why information is unavailable, while methodology §12.3 also distinguishes an unperformed assessment. Forecasting reason codes such as `no_agreed_method` remain source information; their mapping to decision-support states and concrete encoding is pending Dewmi's review with the producing owners under [integration blocker B9](../integration-contract-readiness.md#9-blockers) and [forecast contract §9](../forecast-api-contract.md#9-retained-export-unavailable-and-lookup-behaviour). The current record implementation stores reasons in `unavailable_fields`; this draft does not introduce a fixed vocabulary there.

Dewmi owns responsible-use meaning and reviews the later presentation. Tinosh implements the reviewed technical presentation; Chathuranga and Didilani retain review of their respective upstream semantics.

## 6. Deferred Checks and Completion Requirements

| Pending check | Evidence needed before completion | Owner / tracking issue |
|---|---|---|
| Forecasting evidence access and acceptance | Make the chosen forecasting evidence accessible through an agreed handoff, retaining its source/version and provenance. If the retained export is used, supply the export and its reviewed hash reference; local existence alone does not establish consumer acceptance. Generated artifacts remain outside Git under the [storage policy](../artifact-storage-policy.md). | Chathuranga supplies forecasting evidence; Tinosh reviews technical consumption; Dewmi identifies the assessment source — [#132](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/132), [#145](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/145). |
| Record-level transparency assessment | Identified, reviewable records with identity, timing, provenance and source/version references; an outcome and supporting evidence/reason for each applicable check. | Dewmi — [#145](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/145), using the criteria and implementation from #72/#73. |
| Inventory-risk and recommendation interpretation | Didilani's reviewed evidence and downstream meaning handoff, with approval boundaries and unavailable reasons retained. | Didilani supplies and reviews upstream meaning; Dewmi preserves it in the assessment — [#85](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/85), #145. |
| Unavailable-state mapping | Reviewed mapping and encoding between upstream reason codes and decision-support states; retain the original reason while the mapping remains unresolved. | Dewmi with producing owners — [B9](../integration-contract-readiness.md#9-blockers), #72/#73; presentation implications tracked in #145. |
| Visibility and readability in the prototype | Rendered screens/views from Tinosh showing labels, provenance, unavailable reasons, assumptions, limitations, advisory wording and human-review states/reasons. Record contents alone cannot establish that these are visible in the interface. | Tinosh implements the reviewed presentation; Dewmi evaluates it — [#86](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/86), #145, subject to the agreed integration scope. |
| Report-ready measured findings | A traceable assessment matrix and explicit reviewed/applicable populations and denominators. | Dewmi — #145. |
| Final presentation acceptance | Dewmi's review of Tinosh's implementation, with relevant upstream owner review and unresolved checks recorded explicitly. | Dewmi, with Chathuranga and Didilani reviewing their upstream meaning — #145; Tinosh's integration under #86. |

Issue #145 remains open until its required evidence and handoff are reviewed and its completion criteria are met. A PR containing only this preparation must describe its pending evaluation accurately and use `Related to #145` instead of `Closes #145`.


## 7. Technical Verification of Decision-Support Records

The existing responsible decision-support implementation was inspected to establish which transparency-related information is supported by the record structure. The review covered `src/decision_support/records.py` and the associated tests in `tests/test_decision_support_records.py`.

The `DecisionSupportRecord` structure includes forecast identity and horizon, forecast demand, inventory-risk evidence, replenishment recommendations, uncertainty or error information, assumptions, limitations, supporting evidence, management considerations, human-review status and reasons, and component provenance.

The implementation also requires explicit reasons when specified upstream information is unavailable. Human-review status is restricted to supported values, and explanatory reasons must be provided. These safeguards help preserve the distinction between available evidence and information that has not been assessed or supplied.

**Validation performed:** The command `python -m pytest tests/test_decision_support_records.py -q` completed successfully, with 11 tests passed.

**Interpretation:** These findings provide evidence that the record structure and its tested validation behaviour support responsible decision-support requirements. However, they do not demonstrate that populated records satisfy every transparency criterion or that the information is clearly presented to managers.

The record-level evaluation outcomes therefore remain pending until applicable decision-support records and supporting upstream evidence have been reviewed. Prototype visibility, managerial interpretation, and final presentation acceptance also require separate assessment.
