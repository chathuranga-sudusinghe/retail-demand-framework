# A Data-Driven Decision Support Framework for Retail Demand Forecasting and Inventory Risk Analysis

**Module:** COMP1884 Group Project, MSc Data Science, University of Greenwich.
**Document status:** Shared report draft for human review, prepared 24 October 2026 (Asia/Colombo) under [Issue #187](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/187), C3 of [#179](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/179).
**Source baselines:** Original shared draft: `c279e272942a53cc02dcd5ea4581c7c275e3438a`; inventory integration: `766c102480afe6121e0e3d05a912ae6cfab23cba` (merged PR #188).

This draft assembles existing research material. The [forecasting evaluation](forecasting-final-evaluation.md), frozen contracts and retained reports remain the authorities for methods and numerical evidence. No experiment, metric, assessment or artifact verification was rerun to write this report. The supplied 2026/27 specifications and templates are now mapped in the [criteria checklist](greenwich-criteria-checklist.md#assessment-requirements-and-current-evidence). This repository draft remains source material: final restructuring into the required report template, word-count checking and submission exports belong to #204 after #179 closes.

The [results and interpretation summary](results.md) provides a concise reading path through the retained findings, RQ answers, hypothesis dispositions and limitations. Its draft-delivery milestone #212 is closed; remaining component review is tracked under #179. Its review does not replace this report’s assembly or prototype acceptance requirements.

Chathuranga confirmed the forecasting conclusion paragraph in Section 11 in the working conversation on 24 October 2026. On 29 October, he reported team acceptance of the bounded C1 conclusion, hypothesis dispositions and listed component limitations, recorded in [research design Section 16.4](research-design.md#164-human-decisions-and-c1-closeout-record). The assembled report, technical integration account, rendered views and applicable assessment requirements retain their separate review/verification requirements. Section 13 records the remaining assembly work.

## Abstract

This project investigates how retail demand forecasts can be connected to inventory-risk analysis and transparent decision-support information. It uses the published High-Dimensional Supply Chain Inventory Dataset, whose records are simulated by the publisher. The forecasting study compares XGBoost, LightGBM and CatBoost under matched inputs and chronological evaluation, with supportive models and simple baselines retained for context. Its results show horizon-dependent ordering and limitations in the frozen producers relative to simpler methods in the final period. A separate inventory evaluation applies a documented reorder-threshold exposure method under a constructed fixed-origin, no-receipt scenario. Twenty selected decision-support records have 160 completed human-entered transparency checks. These outputs provide inspectable evidence for a bounded analytical workflow. They do not establish actual stockout accuracy, optimal replenishment, statistical significance of improved decisions or effectiveness in a real retailer. The request-time forecast handoff is accepted; retained runtime, rendered presentation and final integrated acceptance remain separate from the completed component evidence. This abstract is subject to team review.

## 1. Introduction and research questions

Retail demand forecasts must be interpreted alongside inventory conditions before they can inform management decisions. Forecast error alone does not indicate whether a warehouse will reach its reorder threshold, whether a replenishment quantity is justified or whether the information presented to a manager is sufficiently transparent. This project therefore connects forecasting, inventory analysis and responsible decision support within one documented framework.

The main research question is:

> How can data-driven demand forecasting be used to identify inventory risks and support supply-chain decision-making in retail operations?

The supporting questions retain the wording in the [project overview](project-overview.md#7-supporting-research-questions):

- **RQ1:** What demand patterns can be identified from historical SKU-level sales data?
- **RQ2:** Under the same forecasting inputs, temporal validation design, evaluation metrics, and matched hyperparameter settings, how do XGBoost, LightGBM, and CatBoost compare in forecasting future retail demand?
- **RQ3:** How can forecasting outputs and inventory-state variables be combined to identify stockout, overstock, and replenishment risks?
- **RQ4:** How can uncertainty, transparency, governance, and human oversight guide the responsible use of the resulting decision-support outputs?

The contribution is an applied investigation using available evidence, rather than a claim of new forecasting theory or a production retailer deployment. The exact hypotheses and their recorded descriptive disposition remain in [research design, Sections 2.1, 2.2, 11 and 16](research-design.md). This report introduces no replacement hypothesis or new significance-testing procedure.

## 2. Literature and methodological rationale

The existing [literature review](literature/literature-review.md) motivates examining the forecasting-to-inventory interface. Goltsos et al. (2022) discuss the separation between forecasting and inventory-control research. Theodorou et al. (2025) explain why statistical forecast accuracy and inventory performance should not be treated as interchangeable. These sources motivate examining the downstream interpretation of forecasts; they do not validate this project's particular inventory proxy.

Temporal evaluation and clearly defined error measures are necessary for an interpretable forecasting comparison. The literature register includes Bergmeir and Benítez (2012) on time-series validation and Hyndman and Koehler (2006) on forecast-accuracy measures. The project's exact folds, features, metrics and comparison policy are its approved methodological choices, recorded in the [protocol](protocol.md), rather than settings automatically established by those publications.

The final literature discussion must connect these motivations to the observed results, including the performance of simpler baselines and the limits of the dataset. Didilani and Dewmi retain responsibility for reviewing their inventory and responsible-use arguments. Bibliographic details and the assessment's required citation style remain subject to final human verification; the working references in Section 12 are drawn from the existing register, not a new literature search.

## 3. Dataset and analytical scope

The research uses Ziya's High-Dimensional Supply Chain Inventory Dataset downloaded from Kaggle. Its records are simulated by the publisher; the team did not generate a replacement research dataset. The [dataset contract](dataset.md) and [temporal-demand profile](../reports/temporal-demand-profile.md) document 91,250 native records, 50 SKUs and five warehouses over 365 observed dates, from 2024-01-01 through 2024-12-30.

The primary analytical unit is `SKU_ID + Warehouse_ID + Date`, with `Units_Sold` as the demand source. Retaining warehouses preserves operational context: inventory levels, reorder points and supplier lead times vary across warehouses for the same SKU-day. The profiling documents complete daily histories, low median zero-demand share, variation in demand and short-lag dependence. These descriptive findings do not establish causal promotion effects or robust long-cycle seasonality.

The source `Demand_Forecast` field is excluded from ordinary forecasting targets and predictors. `Stockout_Flag` is constant zero and cannot validate actual stockout prediction. Sparse `Order_Quantity` values are not treated as received inventory or optimal-order ground truth. Raw and processed datasets and saved models remain local and Git-ignored under the [storage policy](artifact-storage-policy.md).

## 4. Forecasting methodology

### 4.1 Targets and information available at prediction time

The four direct horizons are 1, 7, 14 and 28 days. For origin `o`, the target is the sum of `Units_Sold` over `o+1` through `o+h`, inclusive. The one-day target is next-day demand; the other targets are cumulative totals. The 28-day target is four-week demand, not a calendar month, supplier-specific lead-time forecast or daily path.

The frozen [feature and preprocessing contract](forecasting-feature-engineering.md) contains fourteen conceptual predictors: SKU and warehouse identities; sine/cosine weekday coordinates for the first target day; lags 1, 7 and 14; rolling means and sample standard deviations over 7, 14 and 28 days; and a 14-day slope. Historical features use only the same series' demand through the origin. Every horizon requires a complete consecutive 28-day history.

Category vocabularies are fitted only on eligible training rows. The primary models use the same full one-hot identity representation followed by twelve unscaled numerical inputs; supportive Ridge scales the numerical inputs using training-only statistics. Unknown identities are rejected. Future operational values, target outcomes and retrospective errors do not enter the predictor matrix.

### 4.2 Model roles and chronological evaluation

XGBoost, LightGBM and CatBoost form the primary RQ2 comparison. Each has the same ordered 24-configuration external grid per horizon and fixed seed 42. Matching external settings does not make their internal algorithms or effective capacity identical. Ridge and Random Forest are fixed supportive models; Naive and Seasonal Naive are contextual baselines. These roles are preserved when interpreting results.

Four expanding historical folds begin training on 2024-01-01, with origins 2024-03-31, 2024-06-30, 2024-09-30 and 2024-11-04. Each origin has a 28-day validation interval; each horizon's target ends at its own origin plus horizon. Forecasts use one fixed-origin feature row per expected pair, without updating with outcomes inside the target window. The [protocol](protocol.md#3-temporal-boundaries) specifies the exact dates and labelled-row eligibility.

Weighted Absolute Percentage Error (WAPE) is the primary comparison metric. Mean Absolute Error (MAE), Root Mean Squared Error (RMSE) and signed Bias support interpretation. Bias is prediction minus actual. Validation summaries are arithmetic means of four fold-level metrics, separately by horizon. No pooled fold metric, cross-horizon composite or formal significance procedure is introduced.

Configurations and downstream producers were frozen before final evaluation in [DR-014](decisions/DR-014-forecasting-selection-and-final-refit.md). The retained final study fitted twenty learned candidates afresh on eligible history through 2024-12-02 and evaluated 28 candidates including the baselines. Its final origin is 2024-12-02, with target ends 2024-12-03, 2024-12-09, 2024-12-16 and 2024-12-30. The final interval was reserved from subsequent fitting and selection, but prior validation/EDA exposure means it was not historically fully unseen.

## 5. Forecasting results and discussion

The retained runs are `validation-20261002-01` and `final-20261003-02`. The following report excerpt is copied exactly from [the canonical validation/final comparison](forecasting-final-evaluation.md#6-validation-vs-final-holdout-comparison); no metrics have been recomputed. WAPE is a ratio and the other metrics use the target's demand units.

| Horizon (days) | Frozen producer | Configuration | Validation WAPE | Final/test WAPE | Final MAE | Final RMSE | Final Bias |
|---|---|---|---|---|---|---|---|
| 1 | LightGBM | GBM018 | 0.2932906923367382 | 0.30382986353577623 | 4.711793523712817 | 5.976578358817961 | -2.3923449315775596 |
| 7 | LightGBM | GBM011 | 0.13989393416032503 | 0.21742439002586517 | 24.60548337044711 | 28.08160479602628 | -23.756458303596517 |
| 14 | XGBoost | GBM022 | 0.1544216889501322 | 0.28637579706078414 | 66.6614125366211 | 70.49288687813687 | -66.65070416259766 |
| 28 | XGBoost | GBM003 | 0.22121971037471905 | 0.37086299051211 | 184.5547751464844 | 187.3698328121354 | -184.5547751464844 |

The primary models show broadly comparable validation performance, with horizon-specific ordering and differences across folds. Small aggregate differences are not evidence of statistical significance. The complete [validation comparison](../reports/forecasting/validation-20261002-01/comparison.md) retains fold-level results; it should accompany interpretation rather than an overall model ranking.

Final WAPE is higher than the validation mean for every frozen producer, and final Bias is negative for all four. Validation means and final metrics describe different origins, training histories and target populations; their difference does not identify a causal mechanism or establish an independently replicated generalisation gap.

Simpler alternatives must remain visible. Supportive Ridge has lower final WAPE than each frozen producer at all four horizons. Among all reported candidates, Ridge has the lowest final WAPE at 1 and 7 days, and Seasonal Naive at 14 and 28 days. These observations are documented in the [complete final results](forecasting-final-evaluation.md#5-final-holdouttest-results). They do not change the frozen producer mapping or make supportive/baseline models the primary RQ2 comparison. Forecast error alone does not establish inventory or managerial effectiveness.

## 6. Inventory-risk evidence

**Assembly status:** Incorporates Didilani's [analytical interpretation and visual specification](research/inventory-risk-visual-evidence.md), merged through [PR #188](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/188) and integrated into Section 6 through merged PR #190. Chathuranga's [24 October review](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/188#pullrequestreview-5636978481) approved forecasting-facing and evidence-consistency aspects and confirmed Section 6 as the shared-report insertion point; this is scoped approval, not approval of the entire report. Didilani's [Issue #181 analytical review](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/181#issuecomment-6380707367) passed with no analytical documentation change required. Her [PR #190 review](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/190#pullrequestreview-5637154678) was `COMMENTED` with `PASS WITH NON-BLOCKING NOTES`, not formal `APPROVED`. Her later D2 rendered-output review, Tinosh's technical visual review, Dewmi's responsible-presentation review, and final team/report acceptance remain pending under [#179](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/179#issuecomment-6382270737).

### 6.1 Method, origin and reporting populations

[DR-012](decisions/DR-012-inventory-risk-replenishment-methodology.md#group-approval-record) records group approval of the 1/7/14-day fixed-origin, fixed-reorder-point, no-receipt method on 12 October 2026, reported by Chathuranga on 23 October. For origin inventory `I`, reorder point `R` and buffer `B = I - R`, cases at or below the threshold are distinguished from cases that begin above it. In initially-above-threshold cases, forecast demand reaching or exceeding `B` indicates forecast threshold exposure within the horizon.

The [retained inventory report](../reports/inventory-risk/issue-164/evaluation-v1/report.md) uses the 2024-12-02 inventory and reorder point as hypothetical starting conditions before the target window. It compares the forecast exposure with a constructed retrospective proxy using realised demand. Each evaluated horizon has 239 paired initially-above-threshold cases and 11 separately reported scenario-at/below cases. Chathuranga is the recorded human executor; Didilani retains methodological and interpretation responsibility.

### 6.2 Retained counts and target windows

The following tables reproduce the values in the [reviewed interpretation](research/inventory-risk-visual-evidence.md#retained-h1h7h14-results) and retained report without recalculation. A positive event is a reorder-threshold crossing under the retrospective sales proxy, not an observed stockout. True positives (TP) are forecast and proxy crossings; true negatives (TN) are forecast and proxy noncrossings. False positives (FP) are forecast crossings without proxy crossings; false negatives (FN) are proxy crossings missed by the forecast.

| Horizon and target window | Paired N | TP | TN | FP | FN | Source-known at/below | Scenario at/below | Unavailable |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| h1 next-day; 2024-12-03 | 239 | 5 | 230 | 0 | 4 | 0 | 11 | 0 |
| h7 cumulative; 2024-12-03–2024-12-09 | 239 | 54 | 168 | 0 | 17 | 0 | 11 | 0 |
| h14 cumulative; 2024-12-03–2024-12-16 | 239 | 121 | 78 | 0 | 40 | 0 | 11 | 0 |

The 11 scenario-at/below cases are excluded from every paired comparison denominator. The source-known-at/below count of zero does not establish source snapshot availability or an absence of at/below-threshold source records. Likewise, the zero unavailable count describes this constructed-scenario run; it does not resolve unknown source inventory timing.

### 6.3 Proxy metrics, denominators and interpretation

Metric values are ratios as reported in the retained evidence. Denominators are specific to each metric; balanced accuracy retains both class populations.

| Horizon | Metric | Value | Metric denominator |
|---|---|---:|---:|
| h1 | Event prevalence | 0.0377 | 239 |
| h1 | Missed-crossing rate | 0.4444 | 9 proxy-crossing cases |
| h1 | False-alert rate | 0.0000 | 230 proxy-noncrossing cases |
| h1 | Agreement | 0.9833 | 239 |
| h1 | Precision | 1.0000 | 5 forecast-crossing cases |
| h1 | Recall | 0.5556 | 9 proxy-crossing cases |
| h1 | Balanced accuracy | 0.7778 | positive=9; negative=230 |
| h7 | Event prevalence | 0.2971 | 239 |
| h7 | Missed-crossing rate | 0.2394 | 71 proxy-crossing cases |
| h7 | False-alert rate | 0.0000 | 168 proxy-noncrossing cases |
| h7 | Agreement | 0.9289 | 239 |
| h7 | Precision | 1.0000 | 54 forecast-crossing cases |
| h7 | Recall | 0.7606 | 71 proxy-crossing cases |
| h7 | Balanced accuracy | 0.8803 | positive=71; negative=168 |
| h14 | Event prevalence | 0.6736 | 239 |
| h14 | Missed-crossing rate | 0.2484 | 161 proxy-crossing cases |
| h14 | False-alert rate | 0.0000 | 78 proxy-noncrossing cases |
| h14 | Agreement | 0.8326 | 239 |
| h14 | Precision | 1.0000 | 121 forecast-crossing cases |
| h14 | Recall | 0.7516 | 161 proxy-crossing cases |
| h14 | Balanced accuracy | 0.8758 | positive=161; negative=78 |

For h1, agreement of 0.9833 must be read alongside the low proxy-event prevalence of 0.0377 and the 230 true negatives. Four of the nine proxy crossings were missed, giving the reported recall of 0.5556 and missed-crossing rate of 0.4444. High agreement therefore does not mean that nearly all crossing cases were detected.

For h7, 54 of 71 proxy crossings were detected and 17 were missed; the reported recall is 0.7606 and the missed-crossing rate is 0.2394. For h14, 121 of 161 proxy crossings were detected and 40 were missed, with recall 0.7516 and missed-crossing rate 0.2484. The zero false-alert counts apply to 230, 168 and 78 proxy-noncrossing cases at h1, h7 and h14 respectively. They do not remove the missed-crossing limitation or establish performance outside this retained scenario.

The horizons represent different cumulative windows and event prevalences, so their rates remain separate. No pooled score or overall best inventory horizon is inferred. These descriptive results do not establish improvement over a defined operating-policy comparator, service/cost benefits or a requirement to place an order.

### 6.4 Margins, unavailable information and limitations

Where the retained case supplies margins, the inventory buffer is `Inventory_Level − Reorder_Point`, the predicted margin is `buffer − forecast demand`, and the retrospective margin is `buffer − realised Units_Sold` over the same target window. Zero is the reorder-reference boundary. A negative arithmetic margin is not verified physical negative stock. Preserve null margins rather than calculating replacements or treating them as zero; the retained at/below and unavailable states must not acquire invented margin evidence.

Realised target demand, retrospective proxy exposure, confusion cells, retrospective margins and evaluation metrics belong only to a separately labelled evaluation context. Prospective records preserve identity, forecast quantities, origin/windows, source/scenario status and original unavailable reasons. A new live API forecast does not recalculate this retained inventory scenario.

These results are conditional on no receipts, transfers, returns, losses or other adjustments. They do not reconstruct actual future inventory or establish actual stockout accuracy. Source within-day inventory timing remains unknown. `Order_Quantity` is contextual activity, not receipts. Overstock, numerical replenishment, uncertainty methods, automatic human-review triggers and 28-day inventory evaluation remain outside the delivered evidence.

The publisher-simulated data, single forecast origin, prior December 3–16 validation exposure and full-year exploratory exposure constrain interpretation. The results must not be presented as a historically fully unseen evaluation or real-retailer effectiveness. Current DR-012 approval is shown separately from immutable historical proposed-status metadata. Shared-report integration introduces no new method or additional approval.

The approved coverage, proxy-crossing, margin and availability questions are
implemented in the [compact figure delivery](research/thesis-figure-delivery.md).
Its source-index sidecars preserve case traceability; Didilani's D2 review must
assess the actual figures and the overview-plus-index presentation, separately
from the earlier analytical-documentation review.

## 7. Responsible decision-support evidence

**Assembly status — updated 29 October 2026:** Chathuranga reports team acceptance of Dewmi's W1 responsible-use interpretation/display handoff and the automatic-review-rule limitation, as recorded in [research design Section 16.4](research-design.md#164-human-decisions-and-c1-closeout-record). Her W2 review of actual rendered views remains under #182; this report does not establish that review or close her issue.

The [completed assessment](research/responsible-decision-support-evaluation.md) covers a purposive roster of 20 records, five per horizon, with eight transparency checks per record. Chathuranga confirmed all 160 record-level outcomes and manually generated the summary. These completed assessments must not be reassigned to another assessor or repeated for unchanged records.

The [retained summary](../reports/decision-support/issue-168-inventory-v1/summary.md) records forecast visibility, assumption visibility, limitation visibility, human-review transparency and source distinction as met in all 20 records. Risk visibility is met in 15 records and not assessable in the five inventory-gated 28-day records. Recommendation traceability and uncertainty visibility are not assessable for all 20. The summary retains not-assessable cases in applicable denominators and reports no overall cross-criterion success score.

Explicit unavailable reasons communicate missing methods or inputs; they do not supply uncertainty estimates or replenishment recommendations. The records' `not_assessed` human-review state is distinct from the completed transparency checklist. Record-content review does not establish rendered usability, user trust, improved decision quality or business performance. Dewmi's reviewed contribution must also address the relevant governance and ethical/legal limitations without asserting unverified compliance, approval or exemption.

## 8. System integration and prototype

**Assembly status — updated 30 October 2026:** PR #197 delivered the retained-case API and synthetic checks, closing #183. The request-time forecast handoff is [accepted under #203](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/203#issuecomment-6501737406). Retained runtime/source/component acceptance and approved views continue under [#201](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/201), assigned to Didilani with Tinosh's technical review/support. This bounded assignment does not transfer permanent component ownership or establish final prototype acceptance.

The analytical architecture connects shared data preparation, forecasting outputs, inventory evidence and responsible decision-support records. Existing adapters preserve SKU, warehouse, origin, horizon, inclusive target interval, producer provenance and explicit unavailable reasons. Tinosh owns technical integration and visual implementation; Chathuranga shares API architecture and forecasting-facing review.

The [request-time API](forecast-inference-api.md) serves `GET /health` and `POST /forecasts` using supplied history, frozen features and saved producers; it does not train models. [Section 6.1](forecast-inference-api.md#61-manual-verification-evidence--24-october-2026) preserves Chathuranga's 24 October observations, including the truncated h28 pasted response and provisional source checks at that time. [Section 6.2](forecast-inference-api.md#62-technical-consumer-verification-evidence--28-october-2026) records Tinosh's later v2 exchanges at `20265aa0ecb7f5e6436e8aa29694a076fc643286`; the 29 October producer/source acceptance separately reviewed installed-file verification at `7034d296f181564ecf575152f4ce5336ee00f6e4`. That scoped acceptance supplies the current handoff outcome without rewriting the earlier observations or establishing new forecast accuracy.

This live demonstration uses supplied January 2025 histories. The separate [retained export](forecast-api-contract.md) has 1,000 records at origin 2024-12-02. Its inventory and decision-support results do not recompute when a live forecast request changes. The merged retained interface exposes `GET /decision-support/cases` and `GET /decision-support/cases/{assessment_id}`, loading the exact 20 assessed records and validating their prospective source joins. The [API document](forecast-inference-api.md#51-retained-decision-support-cases) records existing synthetic checks and automated retained-serving outcomes, separately from human acceptance. Final technical writing must retain the implementation history in [#183 / PR #197](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/197) and the unfinished delivery/acceptance under #201; it must not describe planned rendered views as completed.

The static [figure exporter](../src/visualization/render_issue_201_views.py)
provides eight purpose-driven figures in `reports/figures/final-thesis-figures/`:
population coverage, proxy-crossing comparison, population margins, worked-case
demand and margins, evidence status, transparency checks and frozen-model
comparison. It consumes retained results without training, inference or research
recalculation. Prospective and retrospective meanings remain explicitly
separated. Chathuranga manually generated the initial and corrected candidates;
the [delivery record](research/thesis-figure-delivery.md) distinguishes those
observations from subsequent readability fixes and pending rendered acceptance.
This is an implementation account, not a claim of completed D2/W2, independent
human code approval or final prototype acceptance.

## 9. Research-question synthesis and hypothesis status

RQ1 is supported by descriptive profiling at the approved warehouse-specific grain. RQ2 is answered by the completed horizon-specific comparison with the primary, supportive and baseline roles retained. RQ3 is supported for the documented threshold-exposure scenario, while actual stockout validation, overstock and numerical replenishment remain outside the supplied evaluation. RQ4 is supported by record-level transparency evidence and documented governance boundaries; rendered and managerial outcomes require separate evidence.

Together, these findings explain how an analytical workflow can connect demand forecasts to conditional inventory evidence and traceable advisory records within this simulated dataset. WAPE-led forecasting comparisons and model/baseline evidence already exist under [DR-006](decisions/DR-006-forecasting-metrics-and-model-selection.md); they do not establish statistically significant improvement in inventory-risk identification or decision support. The primary group hypothesis lacks an operationally defined comparator/outcomes/protocol for that broader improvement claim, not for forecasting accuracy. [DR-005](decisions/DR-005-forecast-validation-design.md#current-human-approved-forecasting-design) already defines the temporal validation windows and descriptive high-demand/decline/low-demand/recovery contexts; a formal significance procedure for the temporal-condition hypothesis is not approved. [DR-013](decisions/DR-013-matched-gradient-boosting-comparison.md#rq2-interpretation-and-claim-boundaries) retains the descriptive horizon-specific RQ2 policy. No formal reject/fail-to-reject result follows, and no acceptance of H0 is asserted.

[Issue #191](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/191) closed on 30 October 2026 after PR #209 merged the reported team acceptance. The [closeout](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/191#issuecomment-6515040267) records Chathuranga's decision to complete C1 on the bounded descriptive scope using the supplied assessment materials; no explicit formal-testing requirement was found there. The marking sheet was unavailable at the time of that closeout; the supplied 2026/27 rubrics are now recorded in the [criteria checklist](greenwich-criteria-checklist.md#project-evidence-to-map-against-the-marking-sheet). The new source check records no explicit formal-testing requirement and does not change the accepted descriptive scope. Any later-evidenced mandatory requirement needs a recorded human decision and, if necessary, re-scoping; no new procedure or run is approved.

**Historical C1 proposal — 25 October 2026:** Section 16.4 proposed retaining the descriptive conclusions, recording the primary and provisional temporal significance claims as untested, and treating prospective uncertainty, numerical replenishment, overstock, automatic managerial-review rules and h28 inventory use as explicit limitations/deferred extensions. This was not approval at that date; the reported subsequent team acceptance is recorded below. Existing hypotheses, forecasting comparisons and frozen producers remain unchanged.

**Forecasting position approved by Chathuranga — 26 October 2026:** As recorded in [#191](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/191) and research design Section 16.4, Chathuranga approved retaining the existing WAPE-led comparisons and descriptive temporal synthesis, recording temporal significance as untested without accepting H0 or claiming a causal effect, and proposing prospective uncertainty estimation as a limitation/deferred extension subject to assessment requirements and team scope confirmation. This was his individual forecasting position; later team acceptance is a separate record.

**Team acceptance reported by Chathuranga — 29 October 2026:** In the #191 working conversation, he confirmed all members' acceptance of the selected C1 decisions and separately confirmed the uncertainty deferral. This accepts the bounded descriptive conclusion, primary/temporal significance claims as untested, Dewmi's W1 interpretation/display handoff and all five disclosed limitations/deferred extensions. The team considers the descriptive conclusions sufficient for its assessed scope. Attribution, source and exact boundaries are recorded once in research design Section 16.4; the individual review dates were not supplied. The supplied assessment requirements are now documented in the criteria checklist; this does not establish lecturer approval, final submission compliance, a new research run, W2 rendered review or final prototype acceptance.

## 10. Limitations

- The publisher-simulated dataset covers approximately one year. Findings do not establish real-retailer effectiveness, robust long-cycle seasonality or a connected company pipeline.
- December 3–16 had earlier validation exposure; full-year exploratory analysis inspected the final interval. The failed first final execution also accessed outcomes before integrity completion. The corrected retained run preserved the frozen scope, but prior exposure cannot be undone.
- Expanding training histories, overlapping cumulative labels and pair-level observations create dependence. Four folds and one final origin are not independent experimental replications.
- Primary ordering varies across horizons and folds. Simpler references can outperform the frozen producers. Final outcomes cannot justify retrospective reselection.
- Inventory findings use a constructed fixed-threshold, no-receipt scenario and an unverified source snapshot timing. Zero-variance stockout labels cannot validate actual stockouts.
- The 20 decision-support cases form a limited purposive roster, not a representative population sample or controlled managerial study. Not-assessable information is retained explicitly.
- Uncertainty estimation, numerical replenishment, overstock, automatic managerial-review triggers and 28-day downstream inventory use remain outside the delivered approved methods/evidence.
- Consumer acceptance, rendered presentation, applicable assessment requirements and full report review are distinct from completed research execution and record checks.

## 11. Conclusion

**Forecasting paragraph confirmed by Chathuranga on 24 October 2026; approval scope is this paragraph only:**

The matched comparison showed broadly comparable validation performance among XGBoost, LightGBM and CatBoost, with ordering varying across horizons and folds. In the final evaluation, supportive Ridge achieved the lowest reported WAPE at the 1-day and 7-day horizons, while Seasonal Naive achieved the lowest at 14 and 28 days. The producer mapping remained unchanged because it was frozen before final evaluation. These findings support a descriptive comparison within the publisher-simulated dataset; they do not establish universal model superiority or statistical significance. The documented prior outcome exposure and evaluation limitations remain applicable.

**Bounded group synthesis — team acceptance reported by Chathuranga, 29 October 2026:**

The project documents a reproducible connection between forecasting evidence, a conditional reorder-threshold analysis and transparent advisory records. Its contribution is bounded by the published simulated data, approved assumptions and actual retained evaluations. It supports an explanation of the analytical chain while preserving explicit unavailable information and human judgement. Actual stockout accuracy, optimal purchasing, significant improvement in decisions and real-retailer effectiveness are not established. The primary and provisional temporal significance claims remain explicitly untested under the reported team disposition; the institutional requirement and unfinished prototype acceptance remain separate.

C1's human decision/review record is maintained in [research design Section 16.4](research-design.md#164-human-decisions-and-c1-closeout-record) under #191. It preserves Chathuranga's 26 October forecasting position and his 29 October report of team acceptance. PR #209 is merged and the [30 October closeout](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/191#issuecomment-6515040267) completes #191 on the accepted descriptive scope; the unavailable institutional source remains a disclosed evidence limit. Dewmi's W2 and retained-view acceptance remain separately tracked in #182/#201; the accepted request-time forecast handoff is recorded in [#203](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/203#issuecomment-6501737406). This synthesis does not establish final integrated acceptance. Final submission-file preparation remains in #204 after #179 closes.

## 12. Working references and evidence sources

The entries below are drawn from the existing [reference register](references.md) and [literature review](literature/literature-review.md). Verify bibliographic details and convert to the applicable assessment style before submission. These entries do not assert a new external-source verification.

- Bergmeir, C. and Benítez, J.M. (2012) 'On the use of cross-validation for time series predictor evaluation', *Information Sciences*, 191, pp. 192–213. [Publication](https://doi.org/10.1016/j.ins.2011.12.028).
- Goltsos, T.E., Syntetos, A.A., Glock, C.H. and Ioannou, G. (2022) 'Inventory–forecasting: Mind the gap', *European Journal of Operational Research*, 299(2), pp. 397–419. [Publication](https://doi.org/10.1016/j.ejor.2021.07.040).
- Hyndman, R.J. and Koehler, A.B. (2006) 'Another look at measures of forecast accuracy', *International Journal of Forecasting*, 22(4), pp. 679–688. [Publication](https://doi.org/10.1016/j.ijforecast.2006.03.001).
- Theodorou, E., Spiliotis, E. and Assimakopoulos, V. (2025) 'Forecast accuracy and inventory performance: Insights on their relationship from the M5 competition data', *European Journal of Operational Research*, 322(2), pp. 414–426. [Publication](https://doi.org/10.1016/j.ejor.2024.12.033).
- Ziya (n.d.) *High-Dimensional Supply Chain Inventory Dataset*. Kaggle. Source details and the previously recorded access date are retained in the [dataset reference entry](references.md#selected-dataset).

| Evidence | Source to retain with the report |
|---|---|
| Source/grain and descriptive findings | [Dataset contract](dataset.md), [temporal profile](../reports/temporal-demand-profile.md), [historical EDA](../reports/demand-eda.md) |
| Frozen forecasting design | [Feature contract](forecasting-feature-engineering.md), [protocol](protocol.md), [DR-013](decisions/DR-013-matched-gradient-boosting-comparison.md), [DR-014](decisions/DR-014-forecasting-selection-and-final-refit.md) |
| Numerical results and current interpretation | [Validation snapshot](../reports/forecasting/validation-20261002-01/comparison.md), [final snapshot](../reports/forecasting/final-20261003-02/comparison.md), [canonical forecasting report](forecasting-final-evaluation.md) |
| Inventory and responsible-use findings | [Inventory interpretation](research/inventory-risk-visual-evidence.md), [inventory report](../reports/inventory-risk/issue-164/evaluation-v1/report.md), [record assessment](research/responsible-decision-support-evaluation.md), [summary](../reports/decision-support/issue-168-inventory-v1/summary.md) |
| Integration and actual serving evidence | [Readiness](integration-contract-readiness.md), [API manual record](forecast-inference-api.md#61-manual-verification-evidence--24-october-2026) |
| Claim and review boundaries | [Research-design evidence mapping](research-design.md#16-evidence-to-conclusion-mapping-and-accepted-scope), [assessment checklist](greenwich-criteria-checklist.md), [AI-use guidance](university-ai-guidance.md) |

## 13. Assembly and review actions before submission

This section is an internal drafting aid. Resolve its items and adapt/remove drafting labels before producing the human-approved submission.

| Action | Responsible member(s) | Current status |
|---|---|---|
| Apply the supplied assessment specifications and confirm remaining submission arrangements | Team; Chathuranga coordinates | The [criteria checklist](greenwich-criteria-checklist.md#assessment-requirements-and-current-evidence) now records the supplied 2026/27 report/presentation formats, word limits, rubrics and meeting-minutes/code-package requirements. Official deadlines remain unconfirmed. The [AI-use note](university-ai-guidance.md#4-applicability-to-comp1884) records Chathuranga’s Tier 2 confirmation and the supplied AIR requirement before references. Final submission-file assembly remains under #204 after #179 closes. |
| Review the complete forecasting contribution and reconcile every numerical excerpt with its canonical source | Chathuranga | The Section 11 forecasting paragraph is confirmed; the assembled chapter/report still needs review. |
| Finalise inventory interpretation, horizon-specific proxy discussion and approved visual selections | Didilani | PR #188 evidence integrated into Section 6 through PR #190. Didilani's Issue #181 analytical review passed with no analytical documentation change required; her PR #190 review was `COMMENTED` (`PASS WITH NON-BLOCKING NOTES`), not formal `APPROVED`. Chathuranga's approval is limited to forecasting-facing/evidence-consistency aspects. Didilani's later D2 rendered-output review, Tinosh's technical visual acceptance, Dewmi's responsible-presentation review, and final team/report acceptance remain pending under #179. |
| Finalise responsible-use interpretation and governance discussion | Dewmi | W1 interpretation/display handoff and automatic-review-rule limitation accepted as reported by Chathuranga on 29 October; existing evidence reused in Section 7. [Dewmi's direct confirmation on 1 November](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/182#issuecomment-6555332904) additionally records her W1 acceptance and support for automatic triggers only as a deferred extension, without approving thresholds. Actual rendered W2 review remains under #182. |
| Supply the actual accepted implementation, integration tests and rendered views for the technical contribution | Tinosh for technical integration/report review; Didilani for the bounded #201 continuation; relevant component reviewers | PR #197 delivered the retained-case API and synthetic checks, closing #183. Human-observed retained startup/route checks and eight generated figures are now recorded in the API/figure guides; source/component and rendered acceptance remain under #201/#179; request-time consumer acceptance is recorded separately in closed [#203](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/203). |
| Record group hypothesis disposition and approve the bounded group conclusion | Team, coordinated by Chathuranga | Team acceptance reported by Chathuranga on 29 October is recorded in research design Section 16.4 and Sections 9/11 here. PR #209 is merged and [#191 closed on 30 October](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/191#issuecomment-6515040267) on the accepted descriptive scope. Later-evidenced requirements need a recorded human decision; #179 retains final repository acceptance. |
| Integrate reviewed sections, verify references/figures/attribution and review the final shared document | All members; Chathuranga coordinates assembly | Working draft only; [#187](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/187) is closed as the delivered shared-report draft milestone. Continuing final report assembly and acceptance are tracked under [#179](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/179). |

The internal plan targets a complete shared draft by 3 November and content review/freeze by 5 November 2026. The project hard finish is midnight at the end of 8 November, **00:00 on 9 November, Asia/Colombo**. These planning dates do not establish the official university submission deadline. Individual reflective essays and presentation preparation remain each member's separate responsibilities.
