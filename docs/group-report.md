# A Data-Driven Decision Support Framework for Retail Demand Forecasting and Inventory Risk Analysis

**Module:** COMP1884 Group Project, MSc Data Science, University of Greenwich.
**Document status:** Shared report draft for human review, prepared 24 October 2026 (Asia/Colombo) under [Issue #187](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/187), C3 of [#179](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/179).
**Source baseline:** `c279e272942a53cc02dcd5ea4581c7c275e3438a`.

This draft assembles existing research material. The [forecasting evaluation](forecasting-final-evaluation.md), frozen contracts and retained reports remain the authorities for methods and numerical evidence. No experiment, metric, assessment or artifact verification was rerun to write this report. The section structure is provisional until checked against the applicable brief and marking sheet; no university word limit or citation style is assumed.

Chathuranga confirmed the forecasting conclusion paragraph in Section 11 in the working conversation on 24 October 2026. That approval covers the paragraph only. The assembled report, inventory and responsible-use interpretations, technical integration account and group hypothesis disposition still require their relevant human reviews. Section 13 records the remaining assembly work.

## Abstract

This project investigates how retail demand forecasts can be connected to inventory-risk analysis and transparent decision-support information. It uses the published High-Dimensional Supply Chain Inventory Dataset, whose records are simulated by the publisher. The forecasting study compares XGBoost, LightGBM and CatBoost under matched inputs and chronological evaluation, with supportive models and simple baselines retained for context. Its results show horizon-dependent ordering and limitations in the frozen producers relative to simpler methods in the final period. A separate inventory evaluation applies a documented reorder-threshold exposure method under a constructed fixed-origin, no-receipt scenario. Twenty selected decision-support records have 160 completed human-entered transparency checks. These outputs provide inspectable evidence for a bounded analytical workflow. They do not establish actual stockout accuracy, optimal replenishment, statistical significance of improved decisions or effectiveness in a real retailer. Prototype consumer and presentation acceptance remain separate from the completed component evidence. This abstract is subject to team review.

## 1. Introduction and research questions

Retail demand forecasts must be interpreted alongside inventory conditions before they can inform management decisions. Forecast error alone does not indicate whether a warehouse will reach its reorder threshold, whether a replenishment quantity is justified or whether the information presented to a manager is sufficiently transparent. This project therefore connects forecasting, inventory analysis and responsible decision support within one documented framework.

The main research question is:

> How can data-driven demand forecasting be used to identify inventory risks and support supply-chain decision-making in retail operations?

The supporting questions retain the wording in the [project overview](project-overview.md#7-supporting-research-questions):

- **RQ1:** What demand patterns can be identified from historical SKU-level sales data?
- **RQ2:** Under the same forecasting inputs, temporal validation design, evaluation metrics, and matched hyperparameter settings, how do XGBoost, LightGBM, and CatBoost compare in forecasting future retail demand?
- **RQ3:** How can forecasting outputs and inventory-state variables be combined to identify stockout, overstock, and replenishment risks?
- **RQ4:** How can uncertainty, transparency, governance, and human oversight guide the responsible use of the resulting decision-support outputs?

The contribution is an applied investigation using available evidence, rather than a claim of new forecasting theory or a production retailer deployment. The exact hypotheses and their unresolved disposition remain in [research design, Sections 2.1, 2.2, 11 and 16](research-design.md). This report introduces no replacement hypothesis or new significance-testing procedure.

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

**Assembly status:** Evidence summary for Didilani's interpretation review; this draft does not replace her component contribution or approve new analytical rules.

[DR-012](decisions/DR-012-inventory-risk-replenishment-methodology.md#group-approval-record) records group approval of the 1/7/14-day fixed-origin, fixed-reorder-point, no-receipt method on 12 October 2026, reported by Chathuranga on 23 October. For origin inventory `I`, reorder point `R` and buffer `B = I - R`, cases at or below the threshold are distinguished from cases that begin above it. In initially-above-threshold cases, forecast demand reaching or exceeding `B` indicates forecast threshold exposure within the horizon.

The [retained inventory report](../reports/inventory-risk/issue-164/evaluation-v1/report.md) uses the 2024-12-02 inventory and reorder point as hypothetical starting conditions before the target window. It compares the forecast exposure with a constructed retrospective proxy using realised demand. Each evaluated horizon has 239 paired initially-above-threshold cases and 11 separately reported scenario-at/below cases. Chathuranga is the recorded human executor; Didilani retains methodological and interpretation responsibility.

These results are conditional on no receipts, transfers, returns, losses or other adjustments. They do not reconstruct actual future inventory or establish actual stockout accuracy. Source within-day inventory timing remains unknown. `Order_Quantity` is contextual activity, not receipts. Overstock, numerical replenishment and 28-day inventory evaluation remain outside the delivered evidence. Didilani's final discussion should explain the horizon-specific proxy metrics and denominators without turning agreement into an improvement claim without a defined comparator.

## 7. Responsible decision-support evidence

**Assembly status:** Evidence summary for Dewmi's interpretation and governance review; final component wording remains hers to review.

The [completed assessment](research/responsible-decision-support-evaluation.md) covers a purposive roster of 20 records, five per horizon, with eight transparency checks per record. Chathuranga confirmed all 160 record-level outcomes and manually generated the summary. These completed assessments must not be reassigned to another assessor or repeated for unchanged records.

The [retained summary](../reports/decision-support/issue-168-inventory-v1/summary.md) records forecast visibility, assumption visibility, limitation visibility, human-review transparency and source distinction as met in all 20 records. Risk visibility is met in 15 records and not assessable in the five inventory-gated 28-day records. Recommendation traceability and uncertainty visibility are not assessable for all 20. The summary retains not-assessable cases in applicable denominators and reports no overall cross-criterion success score.

Explicit unavailable reasons communicate missing methods or inputs; they do not supply uncertainty estimates or replenishment recommendations. The records' `not_assessed` human-review state is distinct from the completed transparency checklist. Record-content review does not establish rendered usability, user trust, improved decision quality or business performance. Dewmi's reviewed contribution must also address the relevant governance and ethical/legal limitations without asserting unverified compliance, approval or exemption.

## 8. System integration and prototype

**Assembly status:** Existing implementation and demonstration account for Tinosh's technical review; actual joined-prototype and rendered acceptance remain pending in their task records.

The analytical architecture connects shared data preparation, forecasting outputs, inventory evidence and responsible decision-support records. Existing adapters preserve SKU, warehouse, origin, horizon, inclusive target interval, producer provenance and explicit unavailable reasons. Tinosh owns technical integration and visual implementation; Chathuranga shares API architecture and forecasting-facing review.

The [request-time API](forecast-inference-api.md) serves `GET /health` and `POST /forecasts`. Supplied histories are transformed with the frozen pipeline and saved producers; the API does not train models. Chathuranga's four manual synthetic examples and changed-history demonstration are recorded in [Section 6.1 of the API document](forecast-inference-api.md#61-manual-verification-evidence--24-october-2026). They establish observed serving behaviour only, not new research accuracy. The 28-day pasted response ending was truncated, and reference checksum matches remain provisional as documented there.

This live demonstration uses supplied January 2025 histories. The separate [retained export](forecast-api-contract.md) has 1,000 records at origin 2024-12-02. Its inventory and decision-support results do not recompute when a live forecast request changes. Final technical writing must distinguish these flows and use the actual accepted startup/interface behaviour from [#183](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/183); it must not describe planned joined views as completed.

## 9. Research-question synthesis and hypothesis status

RQ1 is supported by descriptive profiling at the approved warehouse-specific grain. RQ2 is answered by the completed horizon-specific comparison with the primary, supportive and baseline roles retained. RQ3 is supported for the documented threshold-exposure scenario, while actual stockout validation, overstock and numerical replenishment remain outside the supplied evaluation. RQ4 is supported by record-level transparency evidence and documented governance boundaries; rendered and managerial outcomes require separate evidence.

Together, these findings explain how an analytical workflow can connect demand forecasts to conditional inventory evidence and traceable advisory records within this simulated dataset. They do not establish statistically significant improvement in inventory-risk identification or decision support. The primary group hypothesis lacks an operationally defined improvement comparator, outcomes and statistical protocol; the temporal-condition hypothesis remains provisional without frozen condition definitions and a test procedure. No formal reject/fail-to-reject result follows, and no acceptance of H0 is asserted.

[Issue #185](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/185) records the required component/team disposition and assessed-scope discussion. The dataset boundary does not settle whether the applicable assessment requires formal testing. An unresolved mandatory evaluation remains visible; report assembly does not waive it or authorise a new experiment.

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

**Proposed group synthesis — component and team review pending:**

The project documents a reproducible connection between forecasting evidence, a conditional reorder-threshold analysis and transparent advisory records. Its contribution is bounded by the published simulated data, approved assumptions and actual retained evaluations. It supports an explanation of the analytical chain while preserving explicit unavailable information and human judgement. Actual stockout accuracy, optimal purchasing, significant improvement in decisions and real-retailer effectiveness are not established. The final group conclusion must retain the unresolved hypothesis and prototype-acceptance boundaries until the relevant human decisions and evidence are recorded.

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
| Inventory and responsible-use findings | [Inventory report](../reports/inventory-risk/issue-164/evaluation-v1/report.md), [record assessment](research/responsible-decision-support-evaluation.md), [summary](../reports/decision-support/issue-168-inventory-v1/summary.md) |
| Integration and actual serving evidence | [Readiness](integration-contract-readiness.md), [API manual record](forecast-inference-api.md#61-manual-verification-evidence--24-october-2026) |
| Claim and review boundaries | [Research-design evidence mapping](research-design.md#16-evidence-to-conclusion-mapping--draft-for-human-review), [assessment checklist](greenwich-criteria-checklist.md), [AI-use guidance](university-ai-guidance.md) |

## 13. Assembly and review actions before submission

This section is an internal drafting aid. Resolve its items and adapt/remove drafting labels before producing the human-approved submission.

| Action | Responsible member(s) | Current status |
|---|---|---|
| Confirm applicable brief/marking sheet, required structure, word limit, citation style, file format, official deadlines and AI acknowledgement rules | Team; Chathuranga coordinates | Not established by the repository's general guidance; no requirement is invented here. |
| Review the complete forecasting contribution and reconcile every numerical excerpt with its canonical source | Chathuranga | The Section 11 forecasting paragraph is confirmed; the assembled chapter/report still needs review. |
| Finalise inventory interpretation, horizon-specific proxy discussion and approved visual selections | Didilani | Existing evidence reused in Section 6; component review pending under #181. |
| Finalise responsible-use interpretation and governance discussion | Dewmi | Existing evidence reused in Section 7; component review pending under #182. |
| Supply the actual accepted implementation, integration tests and rendered views for the technical contribution | Tinosh, with relevant component reviewers | Section 8 distinguishes existing API behaviour from joined-prototype acceptance under #183. |
| Record group hypothesis disposition and approve the bounded group conclusion | Team, coordinated by Chathuranga | Pending under #185; unresolved mandatory work remains a blocker. |
| Integrate reviewed sections, verify references/figures/attribution and review the final shared document | All members; Chathuranga coordinates assembly | Working draft only; #187 remains open. |

The internal plan targets a complete shared draft by 3 November and content review/freeze by 5 November 2026. The project hard finish is midnight at the end of 8 November, **00:00 on 9 November, Asia/Colombo**. These planning dates do not establish the official university submission deadline. Individual reflective essays and presentation preparation remain each member's separate responsibilities.
