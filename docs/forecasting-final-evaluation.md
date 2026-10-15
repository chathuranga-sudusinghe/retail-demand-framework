# Forecasting Final Evaluation

This report consolidates the completed forecasting study under Issue #131. Completion and integrity verification of the retained runs are confirmed by Chathuranga; this documentation pass performs no new experiment or bundle verification. The frozen research decisions remain those in [DR-014](decisions/DR-014-forecasting-selection-and-final-refit.md). The final forecasting interpretation has been human-reviewed; this documentation pass creates no new approval.

## 1. Final evaluation scope

The study predicts future `Units_Sold` at `SKU_ID + Warehouse_ID + Date` in the High-Dimensional Supply Chain Inventory Dataset downloaded from Kaggle, whose source records are simulated by its publisher. Forecasts represent next-day demand or cumulative demand over 7, 14 or 28 days. The 28-day target is four weeks, not a calendar month or supplier-specific lead time.

The final origin is **2024-12-02**. The reserved evaluation interval is **2024-12-03 through 2024-12-30**; target ends are December 3, 9, 16 and 30 respectively. One prediction per SKU–warehouse pair and horizon is issued from that origin, without updating inside the interval.

The retained final run is `final-20261003-02`. It covers twelve frozen primary candidates, eight fixed supportive candidates and eight baseline evaluations: **20 fresh learned refits and 28 evaluations**. Every candidate is reported, independently of the four downstream producers. Forecasting completion does not establish inventory-risk, replenishment, responsible decision-support or API completion.

## 2. Training/development setup

The accepted [feature contract](forecasting-feature-engineering.md) supplies fourteen conceptual predictors: two identity inputs and twelve numerical predictors. Category vocabularies and Ridge numerical scaling are fitted only on eligible labelled training rows. All models share the same horizon-specific eligible population and fixed-origin information.

Validation uses four expanding historical windows beginning January 1, 2024, with cutoffs March 31, June 30, September 30 and November 4. Each origin is followed by a 28-day validation window. The [protocol](protocol.md) defines the exact windows, eligibility, matched grid, fixed controls, metrics and tie rules.

XGBoost, LightGBM and CatBoost are the primary controlled comparison, each with the same ordered 24-configuration grid per horizon. Ridge and Random Forest are untuned supportive benchmarks; Naive and Seasonal Naive supply contextual baselines. No cross-horizon composite ranking is used.

For the final evaluation, all twenty learned candidates and their preprocessing were fitted afresh using eligible history from **2024-01-01 through 2024-12-02**. Labels must end by December 2 and predictors require complete prior 28-day history. Fold 4 estimators were not promoted. All 28 candidates' predictions were persisted and verified before reserved outcomes were revealed, under the separate final runtime described in [runner operations](forecasting-runner.md).

### Training-error evidence

The retained tracked comparison reports and the implemented scoring/persistence contracts report out-of-sample validation and final-holdout errors. They contain no comparable recorded training-set prediction-error series. Training-set prediction error was **not used/retained as a research selection metric**, so no comparable training-error figure is reported. Training objectives and fitted parameters are not training-error evidence. No training errors have been calculated, reconstructed or invented in this pass; ignored local outcome bundles were not read.

## 3. Validation results

Source: [retained validation comparison](../reports/forecasting/validation-20261002-01/comparison.md), run `validation-20261002-01`. Values below are copied exactly from its selected-configuration and contextual summary rows. Each metric is the **arithmetic mean of four chronological fold metrics**, separately by horizon; these are not pooled prediction metrics. WAPE (Weighted Absolute Percentage Error) is a ratio. MAE (Mean Absolute Error), RMSE (Root Mean Squared Error) and Bias use target units; Bias is prediction minus actual.

| Horizon (days) | Role | Model | Configuration | Mean WAPE | Mean MAE | Mean RMSE | Mean Bias |
|---|---|---|---|---|---|---|---|
| 1 | primary | XGBoost | GBM006 | 0.29332283885069 | 4.402851698875428 | 5.559756779044709 | 0.08509869098663334 |
| 1 | primary | LightGBM | GBM018 | 0.2932906923367382 | 4.402829917488103 | 5.575164784757762 | 0.07270856809803133 |
| 1 | primary | CatBoost | GBM017 | 0.29372249803173084 | 4.41218346684394 | 5.573434797407826 | 0.09539839722238347 |
| 1 | supportive | Ridge | fixed | 0.2998747880270424 | 4.483138613755214 | 5.663814056121446 | 0.062230792548634575 |
| 1 | supportive | Random Forest | fixed | 0.2929647252889673 | 4.40847 | 5.575142243784324 | 0.12248999999999997 |
| 1 | simple_baseline | Naive | not_tuned | 0.41687702903866203 | 6.221 | 7.7992577060167 | -0.23700000000000002 |
| 1 | simple_baseline | Seasonal Naive | not_tuned | 0.41438485944093156 | 6.115 | 7.664505095551862 | 0.21700000000000003 |
| 7 | primary | XGBoost | GBM009 | 0.14067748411478126 | 15.22933073425293 | 18.631399931513645 | 2.2565893402099606 |
| 7 | primary | LightGBM | GBM011 | 0.13989393416032503 | 15.136326529979236 | 18.58592336388992 | 2.0430339478553363 |
| 7 | primary | CatBoost | GBM007 | 0.1400942513936584 | 15.168101846200331 | 18.52591871219229 | 2.184092174044906 |
| 7 | supportive | Ridge | fixed | 0.14764587174438543 | 15.704800171526177 | 19.40134870648049 | 1.346334813809718 |
| 7 | supportive | Random Forest | fixed | 0.14583521046024708 | 15.792966666666667 | 19.39741935528715 | 1.8143866666666661 |
| 7 | simple_baseline | Naive | not_tuned | 0.30579472079595166 | 32.164 | 40.279010327950786 | -0.6959999999999998 |
| 7 | simple_baseline | Seasonal Naive | not_tuned | 0.14941155577150414 | 15.84 | 19.919984236612425 | 0.594 |
| 14 | primary | XGBoost | GBM022 | 0.1544216889501322 | 34.83112683105469 | 39.480065375666065 | 9.770999359130862 |
| 14 | primary | LightGBM | GBM014 | 0.15494737674926892 | 34.88618597236386 | 39.19975464660754 | 10.174552204500902 |
| 14 | primary | CatBoost | GBM021 | 0.15712802319007085 | 35.52358694481502 | 39.68868737377666 | 11.061723589838753 |
| 14 | supportive | Ridge | fixed | 0.15820292686549917 | 33.87151202457325 | 39.795269928178456 | 5.259043667769815 |
| 14 | supportive | Random Forest | fixed | 0.1612158046629115 | 36.46435666666667 | 41.504456653913316 | 11.192590000000001 |
| 14 | simple_baseline | Naive | not_tuned | 0.2951562599922201 | 62.453 | 78.53743653940644 | -0.4470000000000003 |
| 14 | simple_baseline | Seasonal Naive | not_tuned | 0.13717195651053393 | 29.189 | 36.383787971779505 | 2.133 |
| 28 | primary | XGBoost | GBM003 | 0.22121971037471905 | 100.33282150268555 | 105.49284151385544 | 51.586875152587886 |
| 28 | primary | LightGBM | GBM022 | 0.22228836204567165 | 101.10482575084056 | 106.14097114628613 | 41.36619473218771 |
| 28 | primary | CatBoost | GBM015 | 0.22291478056982444 | 101.36117716834471 | 106.04313297606525 | 44.366650492161654 |
| 28 | supportive | Ridge | fixed | 0.2324968287973077 | 99.43330304393726 | 108.92037642295254 | 22.59316231572189 |
| 28 | supportive | Random Forest | fixed | 0.2271170122760801 | 103.14828 | 108.68883307431503 | 42.140293333333325 |
| 28 | simple_baseline | Naive | not_tuned | 0.29674079123033476 | 127.307 | 159.39396185275012 | 0.7689999999999996 |
| 28 | simple_baseline | Seasonal Naive | not_tuned | 0.14504068039350965 | 62.968999999999994 | 77.40066831588709 | 5.9289999999999985 |

Primary configurations minimize their own model/horizon's four-fold mean WAPE. The lowest primary mean WAPE is LightGBM at 1 and 7 days and XGBoost at 14 and 28 days. Differences between the primary leaders are small and are not evidence of statistical significance. No exact configuration or primary-model tie is recorded for these selected rows.

The original comparison retains all four primary fold-level WAPE values and supporting metrics. Primary ordering is not stable across every fold: at 7 days, CatBoost has lower WAPE in folds 1, 3 and 4, whereas LightGBM has the lower four-fold mean. At 28 days, LightGBM has the lowest primary WAPE in fold 2, CatBoost in folds 1 and 3, and XGBoost in fold 4. These observations limit claims based on small mean differences; no formal stability threshold is defined.

Random Forest has slightly lower mean WAPE than the primary leaders at 1 day. Seasonal Naive outperforms all learned models at 14 and 28 days. Their evidence roles remain supportive and baseline respectively; neither finding retroactively changes the approved primary comparison or producer decision.

## 4. Frozen model/configuration selection by horizon

[DR-014](decisions/DR-014-forecasting-selection-and-final-refit.md#frozen-primary-research-configurations) records the human-approved validation freeze before final evaluation:

| Horizon | XGBoost | LightGBM | CatBoost |
|---|---|---|---|
| 1 day | GBM006 | GBM018 | GBM017 |
| 7 days | GBM009 | GBM011 | GBM007 |
| 14 days | GBM022 | GBM014 | GBM021 |
| 28 days | GBM003 | GBM022 | GBM015 |

The lowest mean validation WAPE within each primary model/horizon determines its configuration, subject to the protocol's complete-evidence and exact-tie rules. The separate downstream producer decision uses LightGBM GBM018/GBM011 and XGBoost GBM022/GBM003. Canonical IDs retain their definitions in [configuration.py](../src/forecasting/configuration.py). No configuration, model, feature or parameter was selected using final outcomes.

## 5. Final holdout/test results

Source: [retained final comparison](../reports/forecasting/final-20261003-02/comparison.md), run `final-20261003-02`. All 28 reported evaluations are reproduced below, with their recorded metrics and status unchanged. Each metric measures **one reserved fixed-origin target per pair**, at its own horizon. Supportive and baseline roles remain explicit.

| Role | Model | Horizon (days) | Configuration | WAPE | MAE | RMSE | Bias | Status |
|---|---|---|---|---|---|---|---|---|
| primary | XGBoost | 1 | GBM006 | 0.3022886893169333 | 4.687892993927002 | 5.956720003479292 | -2.3674004249572755 | valid |
| primary | XGBoost | 7 | GBM009 | 0.21849152311381434 | 24.72624868774414 | 28.19651137486619 | -23.911844451904297 | valid |
| primary | XGBoost | 14 | GBM022 | 0.28637579706078414 | 66.6614125366211 | 70.49288687813687 | -66.65070416259766 | valid |
| primary | XGBoost | 28 | GBM003 | 0.37086299051211 | 184.5547751464844 | 187.3698328121354 | -184.5547751464844 | valid |
| primary | LightGBM | 1 | GBM018 | 0.30382986353577623 | 4.711793523712817 | 5.976578358817961 | -2.3923449315775596 | valid |
| primary | LightGBM | 7 | GBM011 | 0.21742439002586517 | 24.60548337044711 | 28.08160479602628 | -23.756458303596517 | valid |
| primary | LightGBM | 14 | GBM014 | 0.28685109235950523 | 66.77204987507619 | 70.53393440586665 | -66.77204987507619 | valid |
| primary | LightGBM | 28 | GBM022 | 0.39293633907826025 | 195.53926803354912 | 198.3636891470377 | -195.53926803354912 | valid |
| primary | CatBoost | 1 | GBM017 | 0.30447905308362017 | 4.721861155220782 | 5.988406610074688 | -2.3284464344212474 | valid |
| primary | CatBoost | 7 | GBM007 | 0.2175243109686565 | 24.61679122370092 | 28.211859061315142 | -23.7095352935551 | valid |
| primary | CatBoost | 14 | GBM021 | 0.27827502302528806 | 64.77574675973446 | 68.77769808617174 | -64.77574675973446 | valid |
| primary | CatBoost | 28 | GBM015 | 0.37388649474359525 | 186.05937969822375 | 189.07602486336256 | -186.05937969822375 | valid |
| supportive | Ridge | 1 | fixed | 0.2922003584097735 | 4.531443158218767 | 5.750446412396494 | -1.3424772611033802 | valid |
| supportive | Ridge | 7 | fixed | 0.1562215108697059 | 17.67927594210288 | 21.798435394771744 | -12.927662570376956 | valid |
| supportive | Ridge | 14 | fixed | 0.1517311025101034 | 35.31935911789183 | 42.352146820802346 | -30.520118164557225 | valid |
| supportive | Ridge | 28 | fixed | 0.18041612404340654 | 89.78155830446467 | 102.57361798425538 | -87.73162950566811 | valid |
| supportive | Random Forest | 1 | fixed | 0.31204883500988734 | 4.839253333333333 | 6.09423632258838 | -2.42544 | valid |
| supportive | Random Forest | 7 | fixed | 0.22055268862811633 | 24.95950666666667 | 28.728220540475913 | -24.12612 | valid |
| supportive | Random Forest | 14 | fixed | 0.2894828791055206 | 67.38466666666667 | 71.63812417855608 | -67.38466666666667 | valid |
| supportive | Random Forest | 28 | fixed | 0.4021616335366948 | 200.13010666666665 | 203.1580522881412 | -200.13010666666665 | valid |
| simple_baseline | Naive | 1 | not_tuned | 0.3941191643022956 | 6.112 | 7.611044606359892 | -0.68 | valid |
| simple_baseline | Naive | 7 | not_tuned | 0.2829421744662802 | 32.02 | 40.29049515704666 | -9.372 | valid |
| simple_baseline | Naive | 14 | not_tuned | 0.2791696738495378 | 64.984 | 80.42904947840674 | -25.184 | valid |
| simple_baseline | Naive | 28 | not_tuned | 0.2849713445168758 | 141.812 | 174.1444802455708 | -82.452 | valid |
| simple_baseline | Seasonal Naive | 1 | not_tuned | 0.3930874387412948 | 6.096 | 7.751644986710885 | -1.32 | valid |
| simple_baseline | Seasonal Naive | 7 | not_tuned | 0.15827795843347942 | 17.912 | 22.599823008156502 | -9.488 | valid |
| simple_baseline | Seasonal Naive | 14 | not_tuned | 0.14785029384472625 | 34.416 | 43.170360202342536 | -25.416 | valid |
| simple_baseline | Seasonal Naive | 28 | not_tuned | 0.17464170598590134 | 86.908 | 102.75063016838388 | -82.916 | valid |

| Metric | Preferred direction | Best possible value | Interpretation |
|---|---|---:|---|
| WAPE | Lower is better | 0 | Overall forecast error relative to total actual demand. 0 means perfect forecasts. |
| MAE | Lower is better | 0 | Average absolute forecast error in demand units. 0 means no absolute error. |
| RMSE | Lower is better | 0 | Gives greater penalty to larger forecast errors than MAE. 0 means no error. |
| Bias | Closer to zero is better | 0 | Indicates systematic forecast direction. Negative means under-forecasting; positive means over-forecasting. |

Lower WAPE, MAE and RMSE indicate better predictive accuracy; interpret Bias by its distance from zero, rather than the numerically smallest value. Compare metrics primarily within the same horizon, because target scale differs between 1-day demand and 7-, 14- and 28-day cumulative demand. This reference defines no new model-selection rule: frozen validation-based model/configuration selection remains unchanged, and final holdout/test outcomes must not trigger reselection.

Ridge has lower final WAPE than each frozen producer at all four horizons. Seasonal Naive has lower final WAPE than the frozen producer at 7, 14 and 28 days. Across the reported candidates, Ridge has the lowest final WAPE at 1 and 7 days and Seasonal Naive at 14 and 28 days. These are descriptive final observations, not new selection decisions. All reported final Bias values are negative, indicating average underprediction.

## 6. Validation vs final-holdout comparison

The table compares the **already frozen producers**, copying values from the two retained reports without recomputing metrics:

| Horizon (days) | Frozen producer | Configuration | Validation WAPE | Final/test WAPE | Final MAE | Final RMSE | Final Bias |
|---|---|---|---|---|---|---|---|
| 1 | LightGBM | GBM018 | 0.2932906923367382 | 0.30382986353577623 | 4.711793523712817 | 5.976578358817961 | -2.3923449315775596 |
| 7 | LightGBM | GBM011 | 0.13989393416032503 | 0.21742439002586517 | 24.60548337044711 | 28.08160479602628 | -23.756458303596517 |
| 14 | XGBoost | GBM022 | 0.1544216889501322 | 0.28637579706078414 | 66.6614125366211 | 70.49288687813687 | -66.65070416259766 |
| 28 | XGBoost | GBM003 | 0.22121971037471905 | 0.37086299051211 | 184.5547751464844 | 187.3698328121354 | -184.5547751464844 |

Validation averages four chronological evaluations with different training lengths, origins and demand conditions. Final/test evaluates one later origin after refitting on eligible history through December 2. They are distinct experimental quantities, not repeated estimates from identical populations or independently replicated tests.

Final WAPE is higher than the validation mean for all four producers, particularly at the longer horizons. Producer Bias changes from positive validation means to negative final values. This is evidence of different errors in the final period; it does not identify a causal mechanism, establish a formal generalization gap or justify tuning against the final interval. MAE/RMSE across horizons also refer to differently sized cumulative targets, so they must not be collapsed into an overall ranking.

## 7. Final producer mapping

| Horizon | Producer model | Configuration |
|---|---|---|
| 1 day | LightGBM | GBM018 |
| 7 days | LightGBM | GBM011 |
| 14 days | XGBoost | GBM022 |
| 28 days | XGBoost | GBM003 |

This mapping was frozen from validation evidence and human review **before final holdout evaluation**. Final primary ordering differs at 1 day (XGBoost has lower WAPE) and 14 days (CatBoost has lower WAPE), but it does not change the mapping. It identifies intended downstream/API forecast producers, not universally best models. Prospective export acceptance and downstream analytical approvals remain separate.

## 8. Interpretation

For RQ2, the matched boosting comparison shows broadly comparable validation performance with horizon-specific ordering and differences across folds. The retained evidence supports descriptive comparison under the approved conditions; no hypothesis is accepted or rejected through a formal significance test.

The final period exposes weaknesses in the frozen learned producers relative to simpler references, especially for cumulative longer horizons. Ridge and Seasonal Naive must remain visible in any presentation of the results. Negative final Bias indicates underprediction on average; it does not by itself prove stockout risk, a replenishment quantity or business effectiveness.

The completed forecasting component supplies reproducible predictions, provenance and honest error evidence for later integration. Inventory-risk effectiveness requires independently approved temporally aligned inventory inputs, rules and evaluation. Responsible decision-support transparency and human-review logic require their component owners' decisions. The [integration readiness map](integration-contract-readiness.md) records these handoff boundaries.

## 9. Limitations

- The dataset downloaded from Kaggle is simulated by its publisher and covers approximately one year; these results cannot establish effectiveness in a real retailer or robust long-cycle seasonality.
- **December 3–16 had prior validation exposure** under the earlier 1/7/14-day methodology. Full-year exploratory data analysis (EDA) also inspected the final interval. The revised December 3–30 interval is reserved from subsequent selection and fitting, but is not historically fully unseen.
- Validation folds share expanding training histories; historical horizon labels overlap. Pair-level observations and folds are not independent experimental replications. Selected-configuration validation predictions are out of sample for fitting but also participated in configuration selection.
- No formal significance test, near-tie threshold or universal fold-stability threshold was performed/defined. Small aggregate differences must not be presented as significant superiority.
- The earlier final execution, `final-20261003-01`, accessed reserved outcomes before failing integrity completion. Its evidence remains a failed historical execution. The separately authorized corrected run, `final-20261003-02`, retained exactly the frozen scientific scope, candidates and producer mapping. The first exposure cannot be undone and must remain disclosed.
- One final origin and nested cumulative horizons limit claims about year-round or future-period performance. There is no cross-horizon overall winner.
- `Stockout_Flag` is constant zero and cannot validate stockout predictions. Forecast error alone does not validate inventory-risk or replenishment effectiveness. No uncertainty method or automatic purchase action is established by this study.

## 10. Final conclusion

Forecasting preparation, development, validation, configuration/model freeze, final holdout evaluation and final integrity verification are complete, as confirmed by Chathuranga. The accepted producer mapping remains LightGBM GBM018 for 1 day, LightGBM GBM011 for 7 days, XGBoost GBM022 for 14 days and XGBoost GBM003 for 28 days.

The evidence supports a reproducible, horizon-specific forecasting comparison. It also shows that simpler supportive/baseline methods can outperform the frozen producers in the final period. The study establishes neither universal model superiority nor statistical significance nor inventory/replenishment effectiveness. Subsequent work is the reviewed prospective handoff and the separately owned downstream components, with the exposure and simulation limitations carried forward.

### Evidence and references

- [Validation numerical evidence](../reports/forecasting/validation-20261002-01/comparison.md) and [final numerical evidence](../reports/forecasting/final-20261003-02/comparison.md): immutable generated snapshots; their original generated-status wording remains historical.
- [DR-014](decisions/DR-014-forecasting-selection-and-final-refit.md): approved freeze, validation-manifest identity and fresh-refit policy.
- [Protocol](protocol.md), [feature contract](forecasting-feature-engineering.md) and [research design](research-design.md): methods, inputs and inference boundaries.
- [Report index](../reports/README.md), [storage policy](artifact-storage-policy.md) and [progress record](research-progress.md): evidence locations, retention and administrative history.
