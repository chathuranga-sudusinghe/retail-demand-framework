# Research Design

This document owns the research questions, hypotheses, rationale and inference boundaries. Exact forecasting methods belong in the [protocol](protocol.md); completed numerical interpretation belongs in [final evaluation](forecasting-final-evaluation.md). The forecasting study is complete as confirmed by Chathuranga; the integrated group hypothesis and downstream components are not declared complete.

## 1. Purpose

This document defines the current research-design baseline for the COMP1884 group project. Hypotheses are treated as testable statements and will only be finalised when their variables and evaluation methods are operationally defined.

## 2. Main research question

**How can data-driven demand forecasting be used to identify inventory risks and support supply-chain decision-making in retail operations?**

## 2.1 Primary group-level hypothesis

### H0

Demand forecasting does not significantly improve inventory-risk identification and supply-chain decision support.

### H1

Demand forecasting significantly improves inventory-risk identification and supply-chain decision support.

This is the primary hypothesis for the integrated group research. Its baseline, measurable inventory-risk outcome(s), decision-support outcome(s), and statistical testing must be operationally defined before final hypothesis testing.

## 2.2 RQ2 — matched gradient-boosting comparison

**Under the same forecasting inputs, temporal validation design, evaluation metrics, and matched hyperparameter settings, how do XGBoost, LightGBM, and CatBoost compare in forecasting future retail demand?**

### H0_RQ2

Under the matched experimental conditions, XGBoost, LightGBM, and CatBoost show comparable demand-forecasting performance across the evaluated horizons.

### H1_RQ2

Under the matched experimental conditions, demand-forecasting performance differs among XGBoost, LightGBM, and CatBoost across the evaluated horizons.

These are comparative research hypotheses, not statistical-significance hypotheses, and remain subordinate to the unchanged primary group-level H0/H1.

RQ2 evidence is interpreted descriptively and comparatively, separately for each horizon. WAPE remains the primary comparison metric: compare arithmetic mean WAPE across the four temporal folds, retain and inspect all four fold-level WAPE results, and use MAE, RMSE and Bias as supporting metrics. Report the magnitude and direction of performance differences; relative differences may also be reported when clearly defined. Examine whether observed differences are reasonably consistent across folds.

No statistical-significance procedure is approved for RQ2. The four temporal folds are not treated as independent experimental replicates. No universal numerical threshold is predeclared for a "meaningful difference". A small aggregate difference driven primarily by one fold must not be presented as strong evidence of a general performance difference. Discuss magnitude, direction, fold consistency and supporting metrics rather than mechanically accepting or rejecting H0_RQ2 using an arbitrary threshold.

Do not average or rank performance across horizons into a single composite. Model ordering may differ by horizon; report those differences rather than collapsing them into an overall winner.

[DR-013](decisions/DR-013-matched-gradient-boosting-comparison.md) records Chathuranga's approved revised direction. The protocol and DR-014 selection/refit decision are frozen; further implementation or experiment execution requires separate human approval.

## 3. Source and analytical unit

The selected source is the **High-Dimensional Supply Chain Inventory Dataset**, published by Ziya and downloaded from Kaggle. Its daily SKU-level supply-chain records are simulated by the publisher; the project team did not generate a replacement research dataset.

The primary forecasting unit is a regular **SKU-warehouse-day** demand time series derived from `Units_Sold`.

This decision is recorded in `docs/decisions/DR-002-forecasting-analytical-unit.md` and is supported by the temporal and inventory-alignment profiling in `reports/temporal-demand-profile.md`.

The selected grain is:

```text
SKU_ID + Warehouse_ID + Date
```

Profiling showed that each SKU-warehouse series has 365 observations with complete temporal coverage and very low median zero-demand frequency. It also showed that `Inventory_Level`, `Reorder_Point`, and `Supplier_Lead_Time_Days` vary across warehouses for every SKU-day, so aggregating demand across warehouses would discard operational context needed by the downstream inventory-risk component.

SKU-day and SKU-week may still be used for descriptive comparison, visualisation, or sensitivity analysis, but they are not the primary modelling grain.

## 4. Forecasting target

Primary source variable:

```text
Units_Sold
```

Primary target at the selected analytical unit:

```text
Demand(SKU_ID, Warehouse_ID, Date) = Units_Sold
```

Because the verified native source grain is one unique row per `Date + SKU_ID + Warehouse_ID`, no additional demand aggregation is required for the primary forecasting view.

The project will build its own forecasting models. The dataset's source-provided `Demand_Forecast` field is **not the project's target** and must not be used as an ordinary predictor if doing so would leak target/future information. It may only be used later as a clearly separated external/source benchmark if methodologically justified.

## 5. Temporal characteristics to investigate

The forecasting component may examine:

- trend;
- seasonality;
- autocorrelation / lag dependence;
- volatility;
- changes in demand level;
- SKU-to-SKU heterogeneity;
- promotion-related effects where leakage-safe.

## 6. Forecasting feature engineering

The [final feature/preprocessing contract](forecasting-feature-engineering.md) is the sole definition of the fourteen predictors, exact order/formulas, origin-time availability, complete 28-day history, common one-hot representation and training-only fitting. Identities supply pooled series context; cyclic weekday, lags, local level/dispersion and slope encode known calendar and past demand. Excluded calendars, promotion plans, inventory states and source forecasts are not reopened by final results.

## 7. Forecast horizon

Approved direct targets cover 1/7/14/28 days from one origin. The 28-day quantity is four-week planning, not an exact month or supplier-specific lead time. [DR-004](decisions/DR-004-forecast-horizons.md) gives rationale; the [protocol](protocol.md#2-frozen-target-predictor-information-and-ordering) defines target meaning. Downstream h=28 use remains separately subject to component-owner/human approval.

## 8. Forecasting approach

RQ2 compares XGBoost, LightGBM and CatBoost under shared inputs, chronological populations and a matched external grid. Matching settings does not make internal tree algorithms, capacity or sampled rows identical. Ridge/Random Forest are fixed supportive references; Naive/Seasonal Naive are contextual baselines. [DR-013](decisions/DR-013-matched-gradient-boosting-comparison.md) records the approved roles/rationale; [protocol](protocol.md#7-matched-primary-grid-fixed-controls-and-deterministic-ordering) owns exact settings.

## 9. Validation design

Use expanding historical training and four fixed-origin 28-day windows, preserving chronological order. April high demand, July decline, October low demand and November–early December recovery provide broader observed temporal coverage than three folds. Four is a project-specific choice, not a statistically optimal or independent replication count. Increasing folds increases workload/selection exposure; it does not permit fitting on their future outcomes.

The [protocol](protocol.md#3-temporal-boundaries) owns exact dates, target completeness, eligibility and fixed-origin behavior. Configurations/model choices were frozen before the final December 2-origin evaluation in [DR-014](decisions/DR-014-forecasting-selection-and-final-refit.md). No final-result-driven reselection is allowed.

Selected validation predictions are out of sample for fitting but participated in configuration selection. The December 3–30 final interval is reserved from subsequent decisions, not historically fully unseen: December 3–16 had prior validation exposure and full-year EDA inspected it. The first final execution also revealed outcomes before failing integrity completion; the corrected run kept the frozen scope. [Final results](forecasting-final-evaluation.md#9-limitations) carries these disclosures.

## 10. Approved forecasting metrics and model-selection policy

WAPE is the primary horizon-specific comparison/selection metric; MAE, RMSE and signed Bias support interpretation. WAPE expresses aggregate absolute error relative to aggregate actual demand and avoids per-observation percentage division, but a zero aggregate denominator remains undefined and low totals affect its interpretation. MAPE is not a primary metric because zero/low demand makes it unstable.

[Protocol](protocol.md#8-metric-formulas-and-aggregation) owns formulas, zero-denominator status and arithmetic four-fold means. Do not pool/weight fold metrics or build a cross-horizon composite. Within-model exact ties retain all IDs with a deterministic administrative representative; primary-model ties stay ties. No significance procedure, near-tie tolerance or universal stability threshold is defined.

The approved [DR-014 freeze](decisions/DR-014-forecasting-selection-and-final-refit.md) and [final report](forecasting-final-evaluation.md) supply the completed model decision and performance progression. Forecasting errors do not establish inventory-risk or replenishment effectiveness.

## 11. Secondary forecasting hypothesis

This secondary hypothesis applies to Chathuranga's forecasting / machine-learning component and supports the primary group-level hypothesis.

### H0

Forecasting performance does not significantly differ across temporal demand conditions.

### H1

Forecasting performance significantly differs across temporal demand conditions.

This remains provisional until temporal demand conditions and the statistical testing procedure are operationally defined.

## 12. Inventory-risk and replenishment interpretation

Didilani's component uses [DR-012 — Inventory-Risk and Replenishment Methodology](decisions/DR-012-inventory-risk-replenishment-methodology.md) to connect project forecasts with inventory evidence under an explicit snapshot basis. The group-approved method is **origin reorder-threshold exposure**; its [approval record](decisions/DR-012-inventory-risk-replenishment-methodology.md#group-approval-record) distinguishes the 12 October decision reported by Chathuranga from source timing and later component acceptance.

For the same SKU-warehouse at forecast origin `t`, define `I_t = Inventory_Level_at_origin`, `R_t = Reorder_Point_at_origin`, and `B_t = I_t - R_t`. For forecast cumulative demand `F_t,h`:

| Condition | Interpretation |
|---|---|
| `B_t <= 0` | Already at/below the origin reorder threshold |
| `B_t > 0` and `F_t,h >= B_t` | Forecast threshold crossing within the horizon |
| `B_t > 0` and `F_t,h < B_t` | No forecast threshold crossing within the horizon |

Use origin-available snapshots, keep the origin threshold fixed, and assume no receipts, transfers, returns, losses or other adjustments during the scenario. The approved downstream method scope applies separately to next-day, 7-day cumulative and 14-day cumulative demand over `t+1` through `t+h`. The new 28-day forecast is mathematically compatible with the generic formula, but **28-day downstream use requires component-owner/human approval**; the longer no-receipt interpretation is not approved here. Equality counts as reaching the threshold. Missing/invalid required evidence produces unavailable/not assessed, not `FALSE`. Within-day snapshot semantics and handling of problematic forecasts remain explicit input-contract decisions; no forecast clipping is introduced here.

The primary retrospective comparison replaces `F_t,h` with realised cumulative `Units_Sold` over the exact same horizon and uses `B_t > 0` cases. Report origin-known already-at/below-threshold cases separately to avoid inflating agreement. DR-012 defines event prevalence, counts, missed-crossing rate, false-alert rate, agreement, precision, recall and balanced accuracy, with explicit denominators and unavailable results for undefined metrics. Check prevalence and do not artificially rebalance the historical population. The conceptual margins are `B_t - F_t,h` and `B_t - realised_demand`; no numeric near-boundary band is approved.

Relevant evidence includes:

- `Inventory_Level`;
- `Reorder_Point`;
- `Supplier_Lead_Time_Days` as context only: horizon shorter than, equal to, or longer than lead time, without rounding or interpolation;
- `Order_Quantity` as contextual activity, not receipts or optimal-policy ground truth;
- forecast error / uncertainty;
- product and warehouse identifiers.

The goal is to transform the forecast into inventory-risk and replenishment information rather than forecast demand a second time.

Verified profiling shows that `Stockout_Flag` is 0 for every row, so it cannot be used as a stockout classification target or validation label. `Order_Quantity` is also sparse: only 5,027 of 91,250 rows contain a non-zero order quantity. These findings must shape the downstream method.

The output is constructed threshold-exposure evidence, not actual stockout prediction or actual shortage ground truth. Negative arithmetic projected balances do not establish physical negative inventory. Source `Demand_Forecast` is not the project model forecast, and future inventory values cannot be origin-time inputs.

Overstock/excess-stock evaluation and final numerical replenishment quantities remain provisional. Not reaching the threshold is not evidence of overstock. The common method supports the primary forecast-to-decision study, while the cross-component evaluation protocol, uncertainty method, human-review thresholds and final hypothesis operationalisation remain later decisions. DR-006 WAPE-based forecasting selection is unchanged.

## 13. Responsible decision support

Dewmi's component will consume forecast and inventory-risk/replenishment outputs and should communicate:

- what the model predicts;
- inventory/risk interpretation;
- forecast uncertainty;
- evidence used by the rule/model;
- assumptions and limitations;
- management considerations;
- whether human review is required.

The framework supports decisions; it does not automatically execute replenishment actions.

## 14. End-to-end framework

```text
Historical sales and supply-chain data
        ->
Forecasting model
        ->
Forecast output
        ->
Inventory-risk / replenishment analysis
        ->
Responsible decision-support logic
        ->
Management-facing output
```


The management-facing output follows the structure defined in DR-011. It keeps `SKU_ID`, `Warehouse_ID`, forecast origin, and forecast horizon visible so that each output can be traced back to its forecasting context. Under the revised direction, the 7-day, 14-day and 28-day forecasts represent cumulative demand over their respective horizons, without implying a daily forecast path. Representing a 28-day cumulative forecasting output does not itself approve downstream 28-day inventory/replenishment use; that remains subject to component-owner/human approval. DR-012 defines the group-approved exposure method; mapping, evaluation utilities and human-run constructed-scenario evidence are available. Final interchange/consumer and prototype acceptance remain pending. Uncertainty, overstock, numerical replenishment and human-review rules remain provisional until their related decisions are approved.

Tinosh's fourth-member contribution is technical integration and prototype engineering within this existing research design. He may implement reviewed component adapters, approved visual outputs and prototype delivery, while Chathuranga shares API architecture and forecasting-contract review. Didilani retains inventory-risk method and interpretation; Dewmi retains responsible decision-support semantics and human-review methodology. FastAPI is a delivery technology, not a research method, and does not alter the research questions, analytical rules or evaluation protocol.

## 15. Threats to validity

Important threats include:

- the dataset downloaded from Kaggle is simulated by its publisher, not observed from a real operating retailer;
- approximately one year of data limits long-cycle seasonal inference;
- source-generated variables may embed assumptions from the simulation;
- `Demand_Forecast` may create leakage if incorrectly used;
- product/warehouse aggregation choices may affect conclusions;
- `Stockout_Flag` is zero-variance in the downloaded dataset and cannot validate stockout predictions;
- non-zero `Order_Quantity` events are sparse and may limit direct replenishment-target modelling;
- model and inventory thresholds may be sensitive to the chosen evaluation period;
- performance on the simulated dataset does not establish production effectiveness in a real company.

Additional forecasting-specific threats include prior final-period validation/EDA exposure, the failed first final execution after outcome access, dependent histories/overlapping labels, selection-conditioned validation evidence and the single final origin. No formal significance test was performed. These limitations remain explicit in [final evaluation](forecasting-final-evaluation.md#9-limitations).

## 16. Evidence-to-conclusion mapping — draft for human review

**Original draft milestone:** [Issue #185](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/185), delivered through PR #186 and closed. Active C1 closure is tracked under [#191](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/191), within the repository-completion parent [#179](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/179). The Section 16.5 descriptive synthesis was delivered through closed [#199](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/199) / merged PR #200; it does not complete the remaining C1 decisions.
**Prepared:** 24 October 2026, Asia/Colombo; source baseline `faedfa492a1d7e3da52de9c6a1c09f08aba347dd`.
**Status — updated 29 October 2026:** Chathuranga reports team acceptance of the bounded descriptive conclusion, primary/temporal hypothesis dispositions and the component limitations recorded in Section 16.4. Applicable assessment requirements remain independently unverified. Sections 2.1, 2.2 and 11 retain their exact hypothesis wording; no new method, result or research run is introduced.

This mapping uses the tracked reports and current interpretation documents below. It does not read ignored research bundles, regenerate results, rerun scientific verification or establish new artifact acceptance. Historical generated wording remains in its original source; current DR-012 approval is governed by its [group approval record](decisions/DR-012-inventory-risk-replenishment-methodology.md#group-approval-record).

### 16.1 Research questions, evidence and claim boundaries

The supporting research-question wording is retained from the [project overview](project-overview.md#7-supporting-research-questions). Chathuranga's reported team acceptance of the bounded interpretation is recorded in Section 16.4; prototype acceptance and assessment-source confirmation remain separate.

| Question | Existing evidence | Supported descriptive interpretation | Limit or remaining gap |
|---|---|---|---|
| **Main:** How can data-driven demand forecasting be used to identify inventory risks and support supply-chain decision-making in retail operations? | [Forecasting findings](forecasting-final-evaluation.md), [constructed inventory evaluation](../reports/inventory-risk/issue-164/evaluation-v1/report.md) and [record assessment](research/responsible-decision-support-evaluation.md) | The implemented methods and populated records document an analytical linkage from demand forecasts to conditional inventory exposure and traceable advisory information. | A completed analytical linkage is not proof of significant improvement, actual stockout prediction, managerial benefit or an accepted end-to-end prototype. Consumer and rendered-presentation acceptance remain separate. |
| **RQ1:** What demand patterns can be identified from historical SKU-level sales data? | [Temporal-demand profile](../reports/temporal-demand-profile.md#3-candidate-analytical-unit-comparison), including its historical EDA notice and limitations; approved SKU-warehouse-day grain in DR-002 | Retained profiling documents complete daily histories for 250 SKU-warehouse series, low median zero-demand share, demand variability and short-lag dependence. Warehouse-level detail preserves operational context lost through SKU-day aggregation. | These are descriptive observations within approximately one simulated year. They do not establish long-cycle seasonality, causal promotion effects or frozen demand-condition groups for hypothesis testing. Historical EDA does not redefine the current frozen features or protocol. |
| **RQ2:** Under the same forecasting inputs, temporal validation design, evaluation metrics, and matched hyperparameter settings, how do XGBoost, LightGBM, and CatBoost compare in forecasting future retail demand? | [DR-013](decisions/DR-013-matched-gradient-boosting-comparison.md#rq2-interpretation-and-claim-boundaries), [validation comparison](../reports/forecasting/validation-20261002-01/comparison.md), [final comparison](../reports/forecasting/final-20261003-02/comparison.md) and [current interpretation](forecasting-final-evaluation.md#8-interpretation) | The primary boosting models show broadly comparable validation performance with horizon-specific ordering and differences across folds. In the final period, supportive Ridge has the lowest reported WAPE at 1/7 days and contextual Seasonal Naive at 14/28 days. | This is the approved descriptive comparison, without a significance claim or universal winner. Supporting models/baselines retain their roles. Final outcomes do not change the DR-014 producer mapping; small means and dependent folds cannot justify a new significance rule. |
| **RQ3:** How can forecasting outputs and inventory-state variables be combined to identify stockout, overstock, and replenishment risks? | [DR-012](decisions/DR-012-inventory-risk-replenishment-methodology.md), [retained inventory report](../reports/inventory-risk/issue-164/evaluation-v1/report.md) and [evaluation protocol](research/inventory-risk-evaluation-protocol.md) | The approved 1/7/14-day method combines cumulative/next-day demand with origin inventory and a fixed reorder point. The retained constructed-origin evaluation reports 239 paired initially-above-threshold cases and 11 separate scenario-at/below cases per evaluated horizon. | This answers the supported threshold-exposure part of RQ3. The no-receipt scenario and realised-demand proxy do not establish actual stockouts or an optimal ordering policy. Source inventory timing remains unknown; overstock, numerical replenishment and 28-day downstream use remain outside the delivered evaluation. |
| **RQ4:** How can uncertainty, transparency, governance, and human oversight guide the responsible use of the resulting decision-support outputs? | [Responsible decision-support evaluation](research/responsible-decision-support-evaluation.md) and [completed assessment summary](../reports/decision-support/issue-168-inventory-v1/summary.md) | The 20 purposively selected records and 160 human-entered checks provide record-level evidence about forecast visibility, assumptions, limitations, human-review transparency and source distinction. Risk visibility is met for 15 records and not assessable for five; uncertainty and recommendation traceability are not assessable for all 20. | Record-content findings do not establish rendered usability, improved trust/decision quality, legal compliance or business effectiveness. Explicit unavailable reasons disclose gaps; they do not supply uncertainty estimates or replenishment recommendations. A transparent `not_assessed` human-review state is not a completed managerial review. |

Chathuranga is the recorded executor of the retained inventory evaluation and assessor of the 160 decision-support checks. Didilani retains inventory-method and interpretation responsibility; Dewmi retains responsible decision-support meaning and review responsibility. This draft does not reassign completed work or request repetition of unchanged assessments.

### 16.2 Hypothesis evidence and unresolved disposition

**Established forecasting evidence:** [DR-006](decisions/DR-006-forecasting-metrics-and-model-selection.md) defines WAPE as the primary forecasting comparison metric, with MAE, RMSE and Bias supporting it. The primary XGBoost/LightGBM/CatBoost comparison, supportive Ridge/Random Forest models and Naive/Seasonal Naive baselines already provide forecasting comparators. These are completed parts of the study, not missing C1 definitions.

[DR-005](decisions/DR-005-forecast-validation-design.md#current-human-approved-forecasting-design) and the frozen protocol define the four dated validation periods. Their documented demand contexts are April high demand, July decline, October low demand and November–early December recovery. These descriptive contexts and windows already exist; they are distinct from a separately approved statistical procedure or formal demand-regime classification. The dispositions below concern the claims that can be made from this evidence; Section 16.4 records the reported team acceptance and the remaining assessment-requirement gap.

| Hypothesis authority | Current evidence status | Recorded disposition and remaining requirement |
|---|---|---|
| **Primary group H0/H1 — Section 2.1** | WAPE/model/baseline comparisons establish forecasting-error evidence. This broader hypothesis concerns significant improvement in inventory-risk identification and decision support; its improvement comparator, outcome measures and testing protocol are not operationally defined. Inventory proxy agreement and record-transparency checks do not supply that comparison. No formal reject/fail-to-reject result is recorded; this is not acceptance of H0. | **Team acceptance reported by Chathuranga — 29 October:** retain the bounded descriptive conclusion and record the significance/improvement claim as untested. The team considers that conclusion sufficient for its assessed scope. The applicable institutional requirement remains unverified; any mandatory evaluation still blocks closure. |
| **Comparative H0_RQ2/H1_RQ2 — Section 2.2** | WAPE-led horizon-specific model comparisons, supporting metrics, fold-level evidence and the approved descriptive interpretation are already available. [DR-013](decisions/DR-013-matched-gradient-boosting-comparison.md#rq2-interpretation-and-claim-boundaries) defines these as comparative research hypotheses, not statistical-significance hypotheses; no formal test or universal numerical decision threshold was approved. | Chathuranga reviews that the report accurately carries the existing interpretation and evidence roles. This is not a request to add a significance test, reopen the frozen comparison or reselect producers from final results. |
| **Provisional secondary temporal-condition H0/H1 — Section 11** | Dated periods and descriptive demand-context labels are defined under DR-005; Section 16.5 reports their existing fold results. A formal significance procedure for this hypothesis and a formal demand-regime classification are not approved. Shared histories, changing training length and repeated pairs limit inference; descriptive fold differences do not establish a causal condition effect or settle the significance hypothesis. | **Team acceptance reported by Chathuranga — 29 October:** retain the existing descriptive synthesis and provisional hypothesis wording, with formal significance untested and no causal condition-effect claim or acceptance of H0. Assessment-requirement confirmation remains separate. |

### 16.3 Proposed bounded group conclusion

**Team acceptance reported by Chathuranga — 29 October 2026:** The existing bounded conclusion and its untested hypothesis claims are accepted within the scope recorded in Section 16.4. This is separate from institutional requirement verification and prototype acceptance.

Within the publisher-simulated dataset, the framework provides a reproducible way to connect SKU-warehouse demand forecasts with a documented reorder-threshold exposure scenario and traceable decision-support records. The forecasting study supports a horizon-specific descriptive comparison of the primary boosting models. Simpler supportive/baseline methods outperform the frozen producers on final WAPE, so the results do not support universal boosting superiority or final-result-driven reselection.

The inventory evidence describes conditional threshold exposure under a fixed-origin, fixed-reorder-point, no-receipt assumption. The decision-support assessment describes the contents of a limited purposive record roster, including explicitly unavailable information. These results support a bounded explanation of the analytical workflow; they do not establish actual stockout accuracy, optimal replenishment, significant improvement in decision quality or real-retailer effectiveness. Under the reported team disposition, statistical significance for the primary and provisional secondary hypotheses is explicitly untested; applicable assessment requirements remain unverified.

Interpretation must retain the one-year simulated-data limitation, prior December 3–16 validation and full-year exploratory exposure, the failed first final execution after outcome access, dependent histories/overlapping labels and the single final origin. Source inventory timing and prototype consumer/rendered-presentation acceptance remain separate limitations or unfinished work, as documented by their respective components.

### 16.4 Human decisions and review record still needed

**Requirement check — 25 October 2026:** Chathuranga confirmed in the working conversation that the formal hypothesis-testing requirement has **not yet been confirmed**, and asked to consider testing if it is justified for research quality. This is not confirmation that testing is mandatory or unnecessary, approval of a statistical procedure, a team hypothesis disposition or authorisation of a run. The local G2 instructions identified in the [criteria checklist](greenwich-criteria-checklist.md#sources) refer to a separate marking sheet, which was not present among the reviewed local materials. The general student handbook and historical group-work escalation procedure also did not establish a COMP1884-specific formal-testing requirement. These findings do not establish an exemption or current-cohort applicability. G2 matched its previously registered local SHA-256 provisionally; the other two documents had no independently reviewed identity reference established by this check.

**Local source inspection — 29 October 2026, under #191:** At Chathuranga's request, Codex searched document filenames throughout `docs/` and `research-materials/`, inspected the three university Word documents (including their embedded-file inventories), extracted the group-work PDF text and inspected the programme screenshot. The relevant criteria, reference and lecturer-guidance records were also checked. Source baseline: `7034d296f181564ecf575152f4ce5336ee00f6e4`; working branch: `docs/c1-research-closure`.

| Local source | What it establishes for this requirement check |
|---|---|
| `COMP1884_Group Project_Instructions.docx` | Describes the group report, individual reflection and presentation. It refers to a separately attached marking sheet; no marking sheet is embedded in the document. It does not state a formal hypothesis-testing requirement or exemption. |
| `student-handbook-2025-26.docx` | Supplies general assessment guidance and directs students to module handbooks/Moodle for assessment details. It does not establish the COMP1884 research-testing requirement or current-cohort applicability. |
| `COMP1884_Group_work_escalation_procedure_2024-25.pdf` | Addresses group-work escalation and conditional changes to deliverables; it does not define a research-testing requirement. |
| `declaration-of-ai-use.docx` | Provides an AI-use acknowledgement form; it does not define research-evaluation requirements. |
| `programme-specification-2026-27.png` | Shows programme/module identity, including COMP1884 Group Project; it does not show a marking rubric or research-testing rule. |

No separate current marking sheet, module rubric or dated lecturer confirmation about formal hypothesis testing was found in the inspected local sources. G1/G2 SHA-256 values matched the two existing [checklist references](greenwich-criteria-checklist.md#sources) at the source baseline (2/2 matches, no missing or changed files in that selected pair). These remain provisional local matches; the other three university documents have no independently reviewed identity reference established by this inspection and are outside the registered checksum profiles. No research bundles were opened or research runs performed. **The requirement remains unconfirmed.** Absence of a rule in these files does not approve an exemption. Section 2.1's significance claim requires an explicit team disposition separately from assessment-requirement confirmation; the subsequent reported team decision is recorded below. This source inspection did not itself approve the proposals or complete #191.

The forecasting metrics, model/baseline comparators, temporal windows and descriptive contexts are already established, as distinguished in Section 16.2. The remaining primary-hypothesis gap concerns a defined inventory/decision-support improvement comparison; the secondary hypothesis lacks an approved significance procedure despite its existing dated-period evidence. Section 16.5 documents the dependence, selection and single-final-origin limits. Adding a test to retained fold metrics would not by itself establish the broader improvement claim or isolate a temporal-condition effect. The remaining assessment-requirement check must establish whether additional evaluation is mandatory despite the team's accepted descriptive scope; any required method would need its own approved claim, comparator, outcomes and protocol. No statistical procedure is selected here. The approved descriptive RQ2 interpretation remains unchanged.

**Historical C1 proposal — 25 October 2026:** Retain the completed descriptive evidence, report the primary and provisional temporal significance claims as untested, and propose the five unapproved methods below as explicit limitations/deferred extensions. This was a proposal for review, not approval at that date. PR #205 delivered the preceding evidence-boundary clarification. The later reported team acceptance below records the subsequent decision without backdating it or establishing an assessment exemption.

**Forecasting position approved by Chathuranga — 26 October 2026:** In the working conversation, Chathuranga explicitly approved the following three-point forecasting position on the proposals delivered through PR #206 (`c7900738acc3dc6bad16462150c6173987c54935`). The dated approval is recorded in [Issue #191](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/191):

1. Retain the existing approved WAPE-led comparisons and descriptive temporal synthesis, with model/baseline roles and frozen producers unchanged.
2. Record temporal statistical significance as **untested**, without accepting H0 or claiming a causal temporal-condition effect; preserve the original hypothesis wording.
3. Propose prospective uncertainty estimation as a disclosed limitation/deferred extension, **subject to assessment requirements and team scope confirmation**.

This was Chathuranga's individual forecasting position on 26 October; it did not itself approve the primary group-hypothesis disposition, another component's scope or the final group conclusion. The subsequent reported team acceptance is recorded below. No statistical procedure or research run is approved by either record, and #191 remains open for its outstanding acceptance requirements.

**Team acceptance reported by Chathuranga — 29 October 2026 (Asia/Colombo):** In the current #191 working conversation, Chathuranga annotated the four-row decision table and confirmed that all members accepted: (1) the sufficiency of the existing descriptive conclusions for the assessment, (2) retaining numerical replenishment, overstock and h28 inventory as disclosed limitations, (3) Dewmi's W1 responsible-use interpretation and automatic-review-rule scope, and (4) the final hypothesis dispositions and bounded group conclusion. In a follow-up answer, he explicitly confirmed that the team also accepted keeping prospective uncertainty estimation unavailable as a disclosed limitation/deferred extension, subject to applicable assessment requirements.

**Attribution and scope:** This records the team's acceptance as reported by Chathuranga, covering the existing Section 16 proposals and report synthesis; individual members' original review dates and separate review records were not supplied. The report date is not an invented date for each member's review. Original research evidence, executor/assessor attribution, hypothesis wording, frozen producers and numerical results are preserved. The team's judgement that the descriptive conclusions are sufficient does not supply the missing marking sheet or establish lecturer/university approval. The external requirement check remains unresolved. W2 rendered review, #201 implementation/acceptance and final repository/report acceptance under #179 remain separate.

| Required decision/review | Responsibility | Recorded disposition and remaining requirement |
|---|---|---|
| Confirm whether the applicable COMP1884 brief/marking criteria require formal hypothesis testing; obtain teaching clarification if needed | Team; Chathuranga coordinates the actual source and confirmation | **Team sufficiency judgement reported — 29 October:** the members accept the existing descriptive conclusions. **Source verification still pending:** the applicable marking sheet/rule or dated teaching clarification has not been supplied; the local sources inspected above do not establish a requirement or exemption. |
| Record the primary group hypothesis disposition and whether the bounded conclusion satisfies the required research scope | Team, coordinated by Chathuranga, with Didilani/Dewmi reviewing the affected outcomes | **Team acceptance reported — 29 October:** preserve the hypothesis wording, record the significance/improvement claim as untested and use Section 16.3's bounded analytical conclusion. Untested does not mean accepting H0. The institutional requirement remains unverified, as recorded above. |
| Record the provisional temporal-condition hypothesis disposition | Chathuranga coordinates the relevant team decision | **Individual forecasting position approved — 26 October; team acceptance reported — 29 October:** retain DR-005's defined dates/contexts and Section 16.5's descriptive synthesis, with formal significance untested and no causal condition-effect claim. Preserve the provisional hypothesis wording; do not introduce a new regime classification or test. Applicable assessment requirements remain unverified. |
| Decide whether forecast uncertainty estimation is required or an explicit limitation/deferred extension | Chathuranga for forecasting methodology; relevant team scope review | **Individual proposal approved — 26 October; team deferral explicitly reported — 29 October:** retain unavailable prospective uncertainty as a disclosed limitation/deferred extension, subject to applicable assessment requirements. Point forecasts and retrospective errors are not uncertainty estimates; no estimation method or run is approved. |
| Decide whether numerical replenishment is required or an explicit limitation/deferred extension | Didilani for inventory/replenishment methodology; relevant team scope review | **Component/team acceptance reported — 29 October:** retain the approved [DR-012 threshold-exposure method](decisions/DR-012-inventory-risk-replenishment-methodology.md), disclose unavailable order quantities and retain numerical replenishment as a limitation/deferred extension. Exposure is replenishment-related evidence, not an order calculation. Applicable assessment requirements remain unverified. |
| Decide whether overstock evaluation is required or an explicit limitation/deferred extension | Didilani; relevant team scope review | **Component/team acceptance reported — 29 October:** disclose that overstock was not evaluated and retain its definition/evaluation as a limitation/deferred extension. A noncrossing threshold state is not overstock evidence; DR-012 does not approve an overstock rule. Applicable assessment requirements remain unverified. |
| Decide whether automatic human-review rules are required or an explicit limitation/deferred extension | Dewmi for responsible-use methodology, with relevant producing members and team scope review | **Component/team acceptance reported — 29 October:** retain automatic triggers as a limitation/deferred extension, preserve advisory output and human judgement, and expose `not_assessed` with its reason. This state is not clearance, a trigger or completed managerial review; [DR-011](decisions/DR-011-decision-support-output-structure.md) supplies structure only. Applicable assessment requirements remain unverified. |
| Decide whether h28 inventory use is required or an explicit limitation/deferred extension | Didilani and relevant component/team reviewers | **Component/team acceptance reported — 29 October:** retain the available h28 forecast while keeping h28 inventory use gated as a limitation/deferred extension; preserve the approved h1/h7/h14 inventory scope. This accepts deferral, not h28 inventory use or evaluation. Applicable assessment requirements remain unverified. |
| Confirm the component interpretations used in the group synthesis | Chathuranga: forecasting; Didilani: inventory; Dewmi: responsible decision support | **Reuse:** Chathuranga's 24 October forecasting-paragraph confirmation in [report Section 11](group-report.md#11-conclusion), his 26 October forecasting position and [Didilani's scoped analytical PASS](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/181#issuecomment-6380707367). **Component/team acceptance reported — 29 October:** the bounded component interpretation and Dewmi's W1 responsible-use/display handoff are accepted. W2 rendered review remains under #182; no record assessments are repeated or reassigned. |
| Approve the final group research conclusion with remaining limitations and required work visible | Team | **Team acceptance reported — 29 October:** use Section 16.3 and the repository report's bounded group synthesis with the recorded dispositions and limitations. This accepts the conclusion, not unperformed research or prototype acceptance. Institutional requirement verification and human review/merge of the documentation remain outstanding for #191; #179 aggregates repository completion. |

For each actual review, record the reviewer, date, exact scope, decision and supporting evidence or issue/PR reference. Do not populate an approval from an AI assessment or from permission to draft this section. If formal testing is mandatory, prepare a separately reviewed protocol covering the estimand, comparator, outcomes, experimental unit, dependence, statistical procedure and reporting/decision rule before any specifically authorised human-run analysis. No additional test or run is selected or authorised here.

This C1 work can progress independently of closing [#201](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/201) (retained prototype/views) or [#203](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/203) (request-time consumer acceptance). Reuse the relevant reviewed [#182](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/182) W1 interpretation before its W2 rendered review where appropriate. Evidence genuinely required for a research claim still gates that claim; no engineering or rendered acceptance is inferred. Final submission-file preparation is outside C1 and waits under [#204](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/204) until #179 closes. Documentation delivery alone does not satisfy #191's required human decisions and reviews.

### 16.5 Descriptive comparison of dated validation periods — C1 follow-up

**Delivered synthesis milestone:** [Issue #199](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/199), closed through PR #200; remaining C1 closure is tracked in #191. **Prepared:** 25 October 2026, Asia/Colombo; source baseline `462956f42abcedce6e7c2db8ea0805920bc0a568`.
**Approval scope:** Chathuranga explicitly approved the documentation-only protocol in the working conversation on 25 October: reuse existing reviewed fold metrics and frozen configurations, compare dated periods separately by horizon, keep final results separate and disclose dependence, selection and prior exposure. This approves preparation of this synthesis, not its final interpretation, a statistical method/run, hypothesis disposition or a team/lecturer decision. The text remains for human review.

#### Evidence and comparison protocol

Use the [retained validation report](../reports/forecasting/validation-20261002-01/comparison.md) for stored metrics, [protocol Section 3](protocol.md#3-temporal-boundaries) for dates and [DR-014](decisions/DR-014-forecasting-selection-and-final-refit.md#frozen-primary-research-configurations) for the twelve frozen primary configurations. No prediction errors or metrics are recalculated. The four-fold means below are copied from existing arithmetic-mean summaries, not pooled or newly averaged. Each model retains the same configuration across all four folds; there is no per-fold reselection. The primary comparison remains XGBoost/LightGBM/CatBoost; Ridge/Random Forest remain supportive and Naive/Seasonal Naive remain contextual baselines.

The period labels identify calendar windows, not newly defined demand regimes. Each horizon's target starts the day after its origin and ends at origin plus horizon; the 28-day window does not make each fold a sequence of daily forecast origins.

| Fold / period | Training start | Training end / origin | Training days | Target start | Target end for h1 / h7 / h14 / h28 |
|---|---|---|---|---|---|
| 1 / April | 2024-01-01 | 2024-03-31 | 91 | 2024-04-01 | 2024-04-01 / 2024-04-07 / 2024-04-14 / 2024-04-28 |
| 2 / July | 2024-01-01 | 2024-06-30 | 182 | 2024-07-01 | 2024-07-01 / 2024-07-07 / 2024-07-14 / 2024-07-28 |
| 3 / October | 2024-01-01 | 2024-09-30 | 274 | 2024-10-01 | 2024-10-01 / 2024-10-07 / 2024-10-14 / 2024-10-28 |
| 4 / November–December | 2024-01-01 | 2024-11-04 | 309 | 2024-11-05 | 2024-11-05 / 2024-11-11 / 2024-11-18 / 2024-12-02 |

The [read-only inspection milestone](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/179#issuecomment-6388160846) records provisional identity matches for three selected local files. The performed structural checks found 304,000 prediction rows across 1,216 complete candidate groups, each covering the same 250 SKU-warehouse pairs, with 4,000 distinct fold/horizon/pair actual-target keys and no duplicate candidate keys, conflicting actuals or date-boundary mismatches. These counts describe repeated evidence coverage, not independent sample sizes. The reference was not independently established from a reviewed commit; the checks did not verify the remaining bundle, source/input fingerprints, model replay or scientific correctness. This documentation step reuses that inspection without another bundle scan.

#### Stored primary fold results

WAPE (Weighted Absolute Percentage Error) is shown as its stored ratio; lower is better. Columns F1–F4 refer to the dated periods above. Values and configuration IDs are copied exactly from the retained report. Its horizon-specific detail tables also retain all four fold-level MAE (Mean Absolute Error), RMSE (Root Mean Squared Error) and signed Bias values; use those supporting results alongside WAPE rather than substituting a new metric or stability threshold.

| Horizon (days) | Primary model | Frozen configuration | F1 WAPE | F2 WAPE | F3 WAPE | F4 WAPE | Stored mean WAPE |
|---|---|---|---|---|---|---|---|
| 1 | XGBoost | GBM006 | 0.14711052345552264 | 0.23620623087573 | 0.41061834237534783 | 0.3793562586961594 | 0.29332283885069 |
| 1 | LightGBM | GBM018 | 0.14773671612588626 | 0.2350846218051868 | 0.41081512200454356 | 0.3795263094113362 | 0.2932906923367382 |
| 1 | CatBoost | GBM017 | 0.14751947750761818 | 0.23739381422282063 | 0.41045893629057556 | 0.37951776410590904 | 0.29372249803173084 |
| 7 | XGBoost | GBM009 | 0.060853267030262226 | 0.15969356034306917 | 0.1683314623578518 | 0.17383164672794188 | 0.14067748411478126 |
| 7 | LightGBM | GBM011 | 0.06195941643698593 | 0.15505036008997175 | 0.16861309939594557 | 0.17395286071839688 | 0.13989393416032503 |
| 7 | CatBoost | GBM007 | 0.06021554944635345 | 0.15980842790826108 | 0.16671340065578588 | 0.17363962756423318 | 0.1400942513936584 |
| 14 | XGBoost | GBM022 | 0.046342085148426776 | 0.26940026865635885 | 0.1131131369530121 | 0.18883126504273107 | 0.1544216889501322 |
| 14 | LightGBM | GBM014 | 0.04394047548824847 | 0.2746890916099378 | 0.11381972291970893 | 0.18734021697918046 | 0.15494737674926892 |
| 14 | CatBoost | GBM021 | 0.04419694741625291 | 0.28532101076036964 | 0.11352281271695441 | 0.18547132186670648 | 0.15712802319007085 |
| 28 | XGBoost | GBM003 | 0.031108142060737864 | 0.5397882450513437 | 0.10555097710790447 | 0.20843147727889014 | 0.22121971037471905 |
| 28 | LightGBM | GBM022 | 0.03407701798792307 | 0.5237250468389942 | 0.08370445514925137 | 0.24764692820651796 | 0.22228836204567165 |
| 28 | CatBoost | GBM015 | 0.03084487618411814 | 0.5358692366829972 | 0.08220364598215188 | 0.24274136343003053 | 0.22291478056982444 |

For these frozen primary configurations, the April fold has the lowest stored WAPE at every horizon. The largest stored WAPE occurs in October at h1, November–December at h7 and July at h14/h28 for all three primary models. At h1, October WAPE exceeds July WAPE while their stored MAE values move in the opposite direction; WAPE depends on the actual-demand denominator as well as absolute error. Thus the metrics describe different aspects of performance, and neither calendar labels nor WAPE differences establish a causal demand-condition effect.

Primary model ordering also changes across folds: at h7, CatBoost has the lowest primary WAPE in F1/F3/F4 while LightGBM has the lower four-fold mean; at h28, the fold leaders are CatBoost, LightGBM, CatBoost and XGBoost respectively. These already documented observations do not identify a universal winner. [Validation interpretation](forecasting-final-evaluation.md#3-validation-results) retains the contextual findings: Random Forest has slightly lower mean h1 WAPE than the primary leaders, and Seasonal Naive outperforms all learned models at h14/h28. Those roles and the frozen producer decision remain unchanged.

#### Final-origin evidence remains separate

The [final comparison](forecasting-final-evaluation.md#6-validation-vs-final-holdout-comparison) evaluates one origin, 2024-12-02, after fresh refitting through that date. The following values are copied from its frozen-producer comparison; they are not extra validation folds or an estimate of an independently replicated generalisation gap.

| Horizon (days) | Frozen producer | Configuration | Stored validation mean WAPE | Stored final WAPE |
|---|---|---|---|---|
| 1 | LightGBM | GBM018 | 0.2932906923367382 | 0.30382986353577623 |
| 7 | LightGBM | GBM011 | 0.13989393416032503 | 0.21742439002586517 |
| 14 | XGBoost | GBM022 | 0.1544216889501322 | 0.28637579706078414 |
| 28 | XGBoost | GBM003 | 0.22121971037471905 | 0.37086299051211 |

Final WAPE is higher than the validation mean for each frozen producer. Across the full final comparison, supportive Ridge has the lowest WAPE at h1/h7 and contextual Seasonal Naive at h14/h28. These final observations do not authorize reselection or establish inventory/decision-support improvement.

#### Feasibility and hypothesis limits

The four validation outcome windows are separate, but cumulative horizons within an origin share outcomes; historical training labels overlap, folds share expanding histories and the same pairs recur. Configuration selection used these validation outcomes. Each dated period supplies one origin, while training-history length and fitted estimators change with period. The retained design therefore does not isolate a temporal-demand-condition effect. The row count does not justify treating observations as independent, and a test treating the four folds as independent would not resolve those design limits. No new condition definition, significance procedure, confidence interval or p-value is introduced.

Any additional analysis of these previously inspected outcomes would be retrospective/exploratory rather than an originally preregistered confirmatory test. Preserve prior December 3–16 validation exposure, full-year exploratory exposure and the failed first final execution after outcome access. One publisher-simulated year and one final origin limit generalisation to other periods or real retailers.

The primary group hypothesis still lacks an operational improvement comparator, outcomes and approved testing protocol. Forecast-error differences do not establish inventory-risk improvement; the constructed threshold-exposure evaluation and purposive record-content checks do not provide a controlled decision-quality comparison. Under the team acceptance reported in Section 16.4, both primary and provisional temporal significance claims are explicitly untested, without acceptance of H0 or a waiver of any assessed requirement. Chathuranga retains forecasting review; Didilani and Dewmi retain their component interpretations; the applicable institutional requirement remains unverified. Any new scientific method needs explicit human approval, and any approved research run must be separately authorized and manually started by its responsible human under [AGENTS Sections 17–19](../AGENTS.md#17-experiment-execution-responsibility).
