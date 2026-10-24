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

**Task:** [Issue #185](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/185), C1 under [#179](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/179).
**Prepared:** 24 October 2026, Asia/Colombo; source baseline `faedfa492a1d7e3da52de9c6a1c09f08aba347dd`.
**Status:** Draft synthesis of existing evidence. No C1 team hypothesis disposition or approval of this conclusion text is recorded here. Sections 2.1, 2.2 and 11 retain their exact hypothesis wording; no methodology or assessed-scope decision is changed.

This mapping uses the tracked reports and current interpretation documents below. It does not read ignored research bundles, regenerate results, rerun scientific verification or establish new artifact acceptance. Historical generated wording remains in its original source; current DR-012 approval is governed by its [group approval record](decisions/DR-012-inventory-risk-replenishment-methodology.md#group-approval-record).

### 16.1 Research questions, evidence and claim boundaries

The supporting research-question wording is retained from the [project overview](project-overview.md#7-supporting-research-questions). The interpretations below are proposed report wording for component review.

| Question | Existing evidence | Supported descriptive interpretation for review | Limit or remaining gap |
|---|---|---|---|
| **Main:** How can data-driven demand forecasting be used to identify inventory risks and support supply-chain decision-making in retail operations? | [Forecasting findings](forecasting-final-evaluation.md), [constructed inventory evaluation](../reports/inventory-risk/issue-164/evaluation-v1/report.md) and [record assessment](research/responsible-decision-support-evaluation.md) | The implemented methods and populated records document an analytical linkage from demand forecasts to conditional inventory exposure and traceable advisory information. | A completed analytical linkage is not proof of significant improvement, actual stockout prediction, managerial benefit or an accepted end-to-end prototype. Consumer and rendered-presentation acceptance remain separate. |
| **RQ1:** What demand patterns can be identified from historical SKU-level sales data? | [Temporal-demand profile](../reports/temporal-demand-profile.md#3-candidate-analytical-unit-comparison), including its historical EDA notice and limitations; approved SKU-warehouse-day grain in DR-002 | Retained profiling documents complete daily histories for 250 SKU-warehouse series, low median zero-demand share, demand variability and short-lag dependence. Warehouse-level detail preserves operational context lost through SKU-day aggregation. | These are descriptive observations within approximately one simulated year. They do not establish long-cycle seasonality, causal promotion effects or frozen demand-condition groups for hypothesis testing. Historical EDA does not redefine the current frozen features or protocol. |
| **RQ2:** Under the same forecasting inputs, temporal validation design, evaluation metrics, and matched hyperparameter settings, how do XGBoost, LightGBM, and CatBoost compare in forecasting future retail demand? | [DR-013](decisions/DR-013-matched-gradient-boosting-comparison.md#rq2-interpretation-and-claim-boundaries), [validation comparison](../reports/forecasting/validation-20261002-01/comparison.md), [final comparison](../reports/forecasting/final-20261003-02/comparison.md) and [current interpretation](forecasting-final-evaluation.md#8-interpretation) | The primary boosting models show broadly comparable validation performance with horizon-specific ordering and differences across folds. In the final period, supportive Ridge has the lowest reported WAPE at 1/7 days and contextual Seasonal Naive at 14/28 days. | This is the approved descriptive comparison, without a significance claim or universal winner. Supporting models/baselines retain their roles. Final outcomes do not change the DR-014 producer mapping; small means and dependent folds cannot justify a new significance rule. |
| **RQ3:** How can forecasting outputs and inventory-state variables be combined to identify stockout, overstock, and replenishment risks? | [DR-012](decisions/DR-012-inventory-risk-replenishment-methodology.md), [retained inventory report](../reports/inventory-risk/issue-164/evaluation-v1/report.md) and [evaluation protocol](research/inventory-risk-evaluation-protocol.md) | The approved 1/7/14-day method combines cumulative/next-day demand with origin inventory and a fixed reorder point. The retained constructed-origin evaluation reports 239 paired initially-above-threshold cases and 11 separate scenario-at/below cases per evaluated horizon. | This answers the supported threshold-exposure part of RQ3. The no-receipt scenario and realised-demand proxy do not establish actual stockouts or an optimal ordering policy. Source inventory timing remains unknown; overstock, numerical replenishment and 28-day downstream use remain outside the delivered evaluation. |
| **RQ4:** How can uncertainty, transparency, governance, and human oversight guide the responsible use of the resulting decision-support outputs? | [Responsible decision-support evaluation](research/responsible-decision-support-evaluation.md) and [completed assessment summary](../reports/decision-support/issue-168-inventory-v1/summary.md) | The 20 purposively selected records and 160 human-entered checks provide record-level evidence about forecast visibility, assumptions, limitations, human-review transparency and source distinction. Risk visibility is met for 15 records and not assessable for five; uncertainty and recommendation traceability are not assessable for all 20. | Record-content findings do not establish rendered usability, improved trust/decision quality, legal compliance or business effectiveness. Explicit unavailable reasons disclose gaps; they do not supply uncertainty estimates or replenishment recommendations. A transparent `not_assessed` human-review state is not a completed managerial review. |

Chathuranga is the recorded executor of the retained inventory evaluation and assessor of the 160 decision-support checks. Didilani retains inventory-method and interpretation responsibility; Dewmi retains responsible decision-support meaning and review responsibility. This draft does not reassign completed work or request repetition of unchanged assessments.

### 16.2 Hypothesis evidence and unresolved disposition

| Hypothesis authority | Current evidence status | Decision still required |
|---|---|---|
| **Primary group H0/H1 — Section 2.1** | Statistical significance of improved inventory-risk identification and decision support is not established. The current design lacks an operationally defined improvement comparator, outcome measures and testing protocol. Neither the inventory proxy results nor the transparency checklist supplies that controlled comparison. No formal reject/fail-to-reject result is recorded; this is not acceptance of H0. | The team must confirm the assessed requirement and determine whether formal testing is required or whether bounded descriptive conclusions with an explicit untested claim are acceptable. Neither option is approved by this draft. An unresolved mandatory evaluation remains a blocker. |
| **Comparative H0_RQ2/H1_RQ2 — Section 2.2** | The approved horizon-specific descriptive interpretation is already available. No statistical-significance procedure, universal meaningful-difference threshold or mechanical hypothesis decision rule was approved. | Chathuranga reviews that the report accurately carries the existing interpretation and evidence roles. This is not a request to reopen the frozen comparison, producer selection or completed evaluation. |
| **Provisional secondary temporal-condition H0/H1 — Section 11** | Temporal-condition definitions and a statistical procedure are not operationally frozen. Descriptive fold differences do not resolve this hypothesis or establish that temporal conditions caused performance changes. | Chathuranga coordinates the final assessed-scope disposition with the team. Preserve its provisional/untested status until the actual decision is recorded; do not invent regimes or choose a test after inspecting results. |

### 16.3 Proposed bounded group conclusion

**Draft for component and team review; not an approved final hypothesis disposition.**

Within the publisher-simulated dataset, the framework provides a reproducible way to connect SKU-warehouse demand forecasts with a documented reorder-threshold exposure scenario and traceable decision-support records. The forecasting study supports a horizon-specific descriptive comparison of the primary boosting models. Simpler supportive/baseline methods outperform the frozen producers on final WAPE, so the results do not support universal boosting superiority or final-result-driven reselection.

The inventory evidence describes conditional threshold exposure under a fixed-origin, fixed-reorder-point, no-receipt assumption. The decision-support assessment describes the contents of a limited purposive record roster, including explicitly unavailable information. These results support a bounded explanation of the analytical workflow; they do not establish actual stockout accuracy, optimal replenishment, significant improvement in decision quality or real-retailer effectiveness. Statistical significance for the primary and provisional secondary hypotheses remains unestablished, and the assessed-scope disposition still requires human decisions.

Interpretation must retain the one-year simulated-data limitation, prior December 3–16 validation and full-year exploratory exposure, the failed first final execution after outcome access, dependent histories/overlapping labels and the single final origin. Source inventory timing and prototype consumer/rendered-presentation acceptance remain separate limitations or unfinished work, as documented by their respective components.

### 16.4 Human decisions and review record still needed

| Required decision/review | Responsibility | Status for this C1 draft |
|---|---|---|
| Confirm whether the applicable COMP1884 brief/marking criteria require formal hypothesis testing; obtain teaching clarification if needed | Team; Chathuranga coordinates the applicable evidence in the [criteria checklist](greenwich-criteria-checklist.md#open-points-and-maintenance) | Unconfirmed here; existing general guidance does not settle this requirement. |
| Record primary and secondary hypothesis disposition and whether the bounded submission satisfies the assessed scope | Team, with Chathuranga coordinating forecasting and the group conclusion | Pending; this draft does not waive a required evaluation or rewrite hypotheses. |
| Review the proposed forecasting, inventory and responsible-use interpretations above | Chathuranga: forecasting; Didilani: inventory; Dewmi: responsible decision support | C1-specific review outcomes not yet recorded. Existing DR-012 approval and completed assessments remain valid within their recorded scope. |
| Approve the final group conclusion with the remaining limitations and required work visible | Team | Pending; keep #185 open until its acceptance criteria are satisfied. |

For each actual review, record the reviewer, date, exact scope, decision and supporting evidence or issue/PR reference. Do not populate an approval from an AI assessment or from permission to draft this section. If formal testing is mandatory, prepare a separately reviewed protocol covering the estimand, comparator, outcomes, experimental unit, dependence, statistical procedure and reporting/decision rule before any specifically authorised human-run analysis. No additional test or run is selected or authorised here.

This evidence mapping can progress independently of Tinosh's consumer implementation. It does not establish acceptance for [#180](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/180) or [#183](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/183), and those tasks do not have to close before the component interpretations and assessed-scope discussion above can proceed.
