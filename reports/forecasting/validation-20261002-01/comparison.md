# Validation comparison — pending human review

## Run summary

- Run ID: validation-20261002-01
- Protocol version: issue-65-matched-frozen-1
- Git commit SHA: fdabd83e67e436df2d918ba5d9a616fbf9744cb0
- Evaluation stage: validation
- Run status at rendering: finalizing
- Completion authority: [run manifest](../../../artifacts/forecasting/validation-20261002-01/run_manifest.json); metadata alone does not establish completion.
- Validation folds: 1, 2, 3, 4 (frozen protocol plan).
- Recorded fold IDs: 1, 2, 3, 4
- Authorised horizons (days): 1, 7, 14, 28
- Primary model roles: XGBoost, LightGBM, CatBoost
- Supportive model roles: Ridge, Random Forest
- Baseline model roles: Naive, Seasonal Naive
- Final-evaluation status: blocked_gate_6; blocked/not executed until separate Gate 6 authorisation.

WAPE (Weighted Absolute Percentage Error) values are stored ratios. All displayed metrics are copied
from the result artifacts; no metric, tie or selection is recalculated here.
[Run metadata](../../../artifacts/forecasting/validation-20261002-01/run_metadata.json) · [Configuration summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv) ·
[Selected configurations](../../../artifacts/forecasting/validation-20261002-01/selected_configurations.json) · [Fold metrics](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv) ·
[Predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) · [Eligibility counts](../../../artifacts/forecasting/validation-20261002-01/eligibility_counts.csv)

## Selected-configuration matrix

| Horizon | XGBoost | LightGBM | CatBoost |
| --- | --- | --- | --- |
| 1-day | GBM006 | GBM018 | GBM017 |
| 7-day | GBM009 | GBM011 | GBM007 |
| 14-day | GBM022 | GBM014 | GBM021 |
| 28-day | GBM003 | GBM022 | GBM015 |

## Primary WAPE comparison matrix

| Horizon | XGBoost WAPE | LightGBM WAPE | CatBoost WAPE |
| --- | --- | --- | --- |
| 1-day | 0.29332283885069 | 0.2932906923367382 | 0.29372249803173084 |
| 7-day | 0.14067748411478126 | 0.13989393416032503 | 0.1400942513936584 |
| 14-day | 0.1544216889501322 | 0.15494737674926892 | 0.15712802319007085 |
| 28-day | 0.22121971037471905 | 0.22228836204567165 | 0.22291478056982444 |

Matrices use the recorded selected configuration (administrative representative where tied).
No cross-horizon overall winner is calculated. Canonical ordering implies no scientific superiority.

## 1-day

### Primary model comparison

- Selected configuration — XGBoost: GBM006.
- Selected configuration — LightGBM: GBM018.
- Selected configuration — CatBoost: GBM017.

| model | evidence_role | configuration_id | canonical_config_id | selection_status | fold_count | n_predictions | mean_wape | mean_mae | mean_rmse | mean_bias | metric_status | review_status | artifact_paths |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| xgboost | primary | GBM006 | GBM006 | validation_leader | 4 | 1000 | 0.29332283885069 | 4.402851698875428 | 5.559756779044709 | 0.08509869098663334 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |
| lightgbm | primary | GBM018 | GBM018 | validation_leader | 4 | 1000 | 0.2932906923367382 | 4.402829917488103 | 5.575164784757762 | 0.07270856809803133 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |
| catboost | primary | GBM017 | GBM017 | validation_leader | 4 | 1000 | 0.29372249803173084 | 4.41218346684394 | 5.573434797407826 | 0.09539839722238347 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |

### Fold-level primary WAPE comparison

| Fold | XGBoost WAPE | LightGBM WAPE | CatBoost WAPE |
| --- | --- | --- | --- |
| 1 | 0.14711052345552264 | 0.14773671612588626 | 0.14751947750761818 |
| 2 | 0.23620623087573 | 0.2350846218051868 | 0.23739381422282063 |
| 3 | 0.41061834237534783 | 0.41081512200454356 | 0.41045893629057556 |
| 4 | 0.3793562586961594 | 0.3795263094113362 | 0.37951776410590904 |

All four stored fold metrics for every displayed configuration (including ties):

| Model | Configuration | Fold | WAPE | MAE | RMSE | Bias | Metric status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| xgboost | GBM006 | 1 | 0.14711052345552264 | 4.515704627990723 | 5.871850431849849 | -0.6592198715209961 | valid |
| xgboost | GBM006 | 2 | 0.23620623087573 | 4.868682830810547 | 6.064557752575375 | 1.3565261383056642 | valid |
| xgboost | GBM006 | 3 | 0.41061834237534783 | 3.940293613433838 | 4.782240374587105 | 0.5087601051330567 | valid |
| xgboost | GBM006 | 4 | 0.3793562586961594 | 4.286725723266602 | 5.520378557166508 | -0.8656716079711914 | valid |
| lightgbm | GBM018 | 1 | 0.14773671612588626 | 4.534926238200204 | 5.926955100340376 | -0.6688526987203982 | valid |
| lightgbm | GBM018 | 2 | 0.2350846218051868 | 4.84556422464851 | 6.065587529243142 | 1.3108444654294378 | valid |
| lightgbm | GBM018 | 3 | 0.41081512200454356 | 3.9421819107556 | 4.773067321752668 | 0.5042203967069014 | valid |
| lightgbm | GBM018 | 4 | 0.3795263094113362 | 4.288647296348099 | 5.535049187694863 | -0.8553778910238157 | valid |
| catboost | GBM017 | 1 | 0.14751947750761818 | 4.528257881573848 | 5.900120304157661 | -0.7135438990348181 | valid |
| catboost | GBM017 | 2 | 0.23739381422282063 | 4.893161298760779 | 6.066366609386459 | 1.3638193685007278 | valid |
| catboost | GBM017 | 3 | 0.41045893629057556 | 3.938763952644363 | 4.800946871176616 | 0.5714071937338745 | valid |
| catboost | GBM017 | 4 | 0.37951776410590904 | 4.288550734396772 | 5.526305404910569 | -0.8400890743102504 | valid |

### Supportive comparison — Ridge and Random Forest

| model | evidence_role | configuration_id | canonical_config_id | selection_status | fold_count | n_predictions | mean_wape | mean_mae | mean_rmse | mean_bias | metric_status | review_status | artifact_paths |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ridge | supportive | fixed | unavailable | fixed_supportive | 4 | 1000 | 0.2998747880270424 | 4.483138613755214 | 5.663814056121446 | 0.062230792548634575 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |
| random_forest | supportive | fixed | unavailable | fixed_supportive | 4 | 1000 | 0.2929647252889673 | 4.40847 | 5.575142243784324 | 0.12248999999999997 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |

### Baseline comparison — Naive and Seasonal Naive

| model | evidence_role | configuration_id | canonical_config_id | selection_status | fold_count | n_predictions | mean_wape | mean_mae | mean_rmse | mean_bias | metric_status | review_status | artifact_paths |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| naive | simple_baseline | not_tuned | unavailable | not_applicable | 4 | 1000 | 0.41687702903866203 | 6.221 | 7.7992577060167 | -0.23700000000000002 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |
| seasonal_naive | simple_baseline | not_tuned | unavailable | not_applicable | 4 | 1000 | 0.41438485944093156 | 6.115 | 7.664505095551862 | 0.21700000000000003 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |

### Tie information

Primary model tie: none recorded.

- XGBoost configuration ties: none recorded.
- LightGBM configuration ties: none recorded.
- CatBoost configuration ties: none recorded.

### Limitations and status

Human selection/freeze remains pending; supportive and baseline evidence cannot establish a primary-model winner.
Human review should compare recorded error magnitudes, signed Bias and the direction/consistency of fold WAPE values.
Unavailable cells denote absent, unselected or undefined evidence; inspect CSV status/reason fields.
Selection unavailable unless all 24 complete four-fold configurations meet the existing selection rules.
Final evaluation remains blocked/not executed until separately authorised.

## 7-day

### Primary model comparison

- Selected configuration — XGBoost: GBM009.
- Selected configuration — LightGBM: GBM011.
- Selected configuration — CatBoost: GBM007.

| model | evidence_role | configuration_id | canonical_config_id | selection_status | fold_count | n_predictions | mean_wape | mean_mae | mean_rmse | mean_bias | metric_status | review_status | artifact_paths |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| xgboost | primary | GBM009 | GBM009 | validation_leader | 4 | 1000 | 0.14067748411478126 | 15.22933073425293 | 18.631399931513645 | 2.2565893402099606 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |
| lightgbm | primary | GBM011 | GBM011 | validation_leader | 4 | 1000 | 0.13989393416032503 | 15.136326529979236 | 18.58592336388992 | 2.0430339478553363 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |
| catboost | primary | GBM007 | GBM007 | validation_leader | 4 | 1000 | 0.1400942513936584 | 15.168101846200331 | 18.52591871219229 | 2.184092174044906 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |

### Fold-level primary WAPE comparison

| Fold | XGBoost WAPE | LightGBM WAPE | CatBoost WAPE |
| --- | --- | --- | --- |
| 1 | 0.060853267030262226 | 0.06195941643698593 | 0.06021554944635345 |
| 2 | 0.15969356034306917 | 0.15505036008997175 | 0.15980842790826108 |
| 3 | 0.1683314623578518 | 0.16861309939594557 | 0.16671340065578588 |
| 4 | 0.17383164672794188 | 0.17395286071839688 | 0.17363962756423318 |

All four stored fold metrics for every displayed configuration (including ties):

| Model | Configuration | Fold | WAPE | MAE | RMSE | Bias | Metric status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| xgboost | GBM009 | 1 | 0.060853267030262226 | 12.908438415527344 | 16.32354202778506 | -2.2647838745117186 | valid |
| xgboost | GBM009 | 2 | 0.15969356034306917 | 21.872268798828124 | 26.63733820923294 | 19.99582287597656 | valid |
| xgboost | GBM009 | 3 | 0.1683314623578518 | 11.342847259521484 | 13.815633676981433 | 3.855113983154297 | valid |
| xgboost | GBM009 | 4 | 0.17383164672794188 | 14.793768463134766 | 17.749085812055142 | -12.559795623779296 | valid |
| lightgbm | GBM011 | 1 | 0.06195941643698593 | 13.143079252279204 | 16.666134619403195 | -2.3213633874181285 | valid |
| lightgbm | GBM011 | 2 | 0.15505036008997175 | 21.236317519362892 | 26.081144431230562 | 19.125187655271187 | valid |
| lightgbm | GBM011 | 3 | 0.16861309939594557 | 11.361825089696396 | 13.8318305260446 | 3.9179985621569715 | valid |
| lightgbm | GBM011 | 4 | 0.17395286071839688 | 14.804084258578449 | 17.76458387888132 | -12.549687038588685 | valid |
| catboost | GBM007 | 1 | 0.06021554944635345 | 12.773163210758279 | 16.19215363284748 | -2.343445705104624 | valid |
| catboost | GBM007 | 2 | 0.15980842790826108 | 21.88800152002707 | 26.50738691019813 | 20.155427415065205 | valid |
| catboost | GBM007 | 3 | 0.16671340065578588 | 11.233815789789476 | 13.678089902566805 | 3.504546301578551 | valid |
| catboost | GBM007 | 4 | 0.17363962756423318 | 14.7774268642265 | 17.726044403156745 | -12.580159315359507 | valid |

### Supportive comparison — Ridge and Random Forest

| model | evidence_role | configuration_id | canonical_config_id | selection_status | fold_count | n_predictions | mean_wape | mean_mae | mean_rmse | mean_bias | metric_status | review_status | artifact_paths |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ridge | supportive | fixed | unavailable | fixed_supportive | 4 | 1000 | 0.14764587174438543 | 15.704800171526177 | 19.40134870648049 | 1.346334813809718 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |
| random_forest | supportive | fixed | unavailable | fixed_supportive | 4 | 1000 | 0.14583521046024708 | 15.792966666666667 | 19.39741935528715 | 1.8143866666666661 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |

### Baseline comparison — Naive and Seasonal Naive

| model | evidence_role | configuration_id | canonical_config_id | selection_status | fold_count | n_predictions | mean_wape | mean_mae | mean_rmse | mean_bias | metric_status | review_status | artifact_paths |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| naive | simple_baseline | not_tuned | unavailable | not_applicable | 4 | 1000 | 0.30579472079595166 | 32.164 | 40.279010327950786 | -0.6959999999999998 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |
| seasonal_naive | simple_baseline | not_tuned | unavailable | not_applicable | 4 | 1000 | 0.14941155577150414 | 15.84 | 19.919984236612425 | 0.594 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |

### Tie information

Primary model tie: none recorded.

- XGBoost configuration ties: none recorded.
- LightGBM configuration ties: none recorded.
- CatBoost configuration ties: none recorded.

### Limitations and status

Human selection/freeze remains pending; supportive and baseline evidence cannot establish a primary-model winner.
Human review should compare recorded error magnitudes, signed Bias and the direction/consistency of fold WAPE values.
Unavailable cells denote absent, unselected or undefined evidence; inspect CSV status/reason fields.
Selection unavailable unless all 24 complete four-fold configurations meet the existing selection rules.
Final evaluation remains blocked/not executed until separately authorised.

## 14-day

### Primary model comparison

- Selected configuration — XGBoost: GBM022.
- Selected configuration — LightGBM: GBM014.
- Selected configuration — CatBoost: GBM021.

| model | evidence_role | configuration_id | canonical_config_id | selection_status | fold_count | n_predictions | mean_wape | mean_mae | mean_rmse | mean_bias | metric_status | review_status | artifact_paths |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| xgboost | primary | GBM022 | GBM022 | validation_leader | 4 | 1000 | 0.1544216889501322 | 34.83112683105469 | 39.480065375666065 | 9.770999359130862 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |
| lightgbm | primary | GBM014 | GBM014 | validation_leader | 4 | 1000 | 0.15494737674926892 | 34.88618597236386 | 39.19975464660754 | 10.174552204500902 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |
| catboost | primary | GBM021 | GBM021 | validation_leader | 4 | 1000 | 0.15712802319007085 | 35.52358694481502 | 39.68868737377666 | 11.061723589838753 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |

### Fold-level primary WAPE comparison

| Fold | XGBoost WAPE | LightGBM WAPE | CatBoost WAPE |
| --- | --- | --- | --- |
| 1 | 0.046342085148426776 | 0.04394047548824847 | 0.04419694741625291 |
| 2 | 0.26940026865635885 | 0.2746890916099378 | 0.28532101076036964 |
| 3 | 0.1131131369530121 | 0.11381972291970893 | 0.11352281271695441 |
| 4 | 0.18883126504273107 | 0.18734021697918046 | 0.18547132186670648 |

All four stored fold metrics for every displayed configuration (including ties):

| Model | Configuration | Fold | WAPE | MAE | RMSE | Bias | Metric status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| xgboost | GBM022 | 1 | 0.046342085148426776 | 19.575823608398437 | 24.93492711300226 | -3.5664888916015625 | valid |
| xgboost | GBM022 | 2 | 0.26940026865635885 | 71.15938696289062 | 76.14978936597588 | 71.10993994140625 | valid |
| xgboost | GBM022 | 3 | 0.1131131369530121 | 15.654858154296875 | 19.17434751843826 | 3.559569091796875 | valid |
| xgboost | GBM022 | 4 | 0.18883126504273107 | 32.93443859863281 | 37.66119750524786 | -32.01902270507812 | valid |
| lightgbm | GBM014 | 1 | 0.04394047548824847 | 18.561335655745918 | 23.184478635946125 | -3.851057561772152 | valid |
| lightgbm | GBM014 | 2 | 0.2746890916099378 | 72.55637665784897 | 77.05271609044179 | 72.55637665784897 | valid |
| lightgbm | GBM014 | 3 | 0.11381972291970893 | 15.752649652087715 | 19.326130224055536 | 3.8000294375895556 | valid |
| lightgbm | GBM014 | 4 | 0.18734021697918046 | 32.67438192377283 | 37.2356936359867 | -31.80713971566277 | valid |
| catboost | GBM021 | 1 | 0.04419694741625291 | 18.66967452757355 | 23.392507113099274 | -3.6310128969993354 | valid |
| catboost | GBM021 | 2 | 0.28532101076036964 | 75.36469178224405 | 79.35601057276227 | 75.33524840078742 | valid |
| catboost | GBM021 | 3 | 0.11352281271695441 | 15.71155728002649 | 19.172752405857594 | 3.896205075992408 | valid |
| catboost | GBM021 | 4 | 0.18547132186670648 | 32.34842418941601 | 36.83347940338751 | -31.353546220425482 | valid |

### Supportive comparison — Ridge and Random Forest

| model | evidence_role | configuration_id | canonical_config_id | selection_status | fold_count | n_predictions | mean_wape | mean_mae | mean_rmse | mean_bias | metric_status | review_status | artifact_paths |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ridge | supportive | fixed | unavailable | fixed_supportive | 4 | 1000 | 0.15820292686549917 | 33.87151202457325 | 39.795269928178456 | 5.259043667769815 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |
| random_forest | supportive | fixed | unavailable | fixed_supportive | 4 | 1000 | 0.1612158046629115 | 36.46435666666667 | 41.504456653913316 | 11.192590000000001 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |

### Baseline comparison — Naive and Seasonal Naive

| model | evidence_role | configuration_id | canonical_config_id | selection_status | fold_count | n_predictions | mean_wape | mean_mae | mean_rmse | mean_bias | metric_status | review_status | artifact_paths |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| naive | simple_baseline | not_tuned | unavailable | not_applicable | 4 | 1000 | 0.2951562599922201 | 62.453 | 78.53743653940644 | -0.4470000000000003 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |
| seasonal_naive | simple_baseline | not_tuned | unavailable | not_applicable | 4 | 1000 | 0.13717195651053393 | 29.189 | 36.383787971779505 | 2.133 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |

### Tie information

Primary model tie: none recorded.

- XGBoost configuration ties: none recorded.
- LightGBM configuration ties: none recorded.
- CatBoost configuration ties: none recorded.

### Limitations and status

Human selection/freeze remains pending; supportive and baseline evidence cannot establish a primary-model winner.
Human review should compare recorded error magnitudes, signed Bias and the direction/consistency of fold WAPE values.
Unavailable cells denote absent, unselected or undefined evidence; inspect CSV status/reason fields.
Selection unavailable unless all 24 complete four-fold configurations meet the existing selection rules.
Final evaluation remains blocked/not executed until separately authorised.

## 28-day

### Primary model comparison

- Selected configuration — XGBoost: GBM003.
- Selected configuration — LightGBM: GBM022.
- Selected configuration — CatBoost: GBM015.

| model | evidence_role | configuration_id | canonical_config_id | selection_status | fold_count | n_predictions | mean_wape | mean_mae | mean_rmse | mean_bias | metric_status | review_status | artifact_paths |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| xgboost | primary | GBM003 | GBM003 | validation_leader | 4 | 1000 | 0.22121971037471905 | 100.33282150268555 | 105.49284151385544 | 51.586875152587886 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |
| lightgbm | primary | GBM022 | GBM022 | validation_leader | 4 | 1000 | 0.22228836204567165 | 101.10482575084056 | 106.14097114628613 | 41.36619473218771 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |
| catboost | primary | GBM015 | GBM015 | validation_leader | 4 | 1000 | 0.22291478056982444 | 101.36117716834471 | 106.04313297606525 | 44.366650492161654 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |

### Fold-level primary WAPE comparison

| Fold | XGBoost WAPE | LightGBM WAPE | CatBoost WAPE |
| --- | --- | --- | --- |
| 1 | 0.031108142060737864 | 0.03407701798792307 | 0.03084487618411814 |
| 2 | 0.5397882450513437 | 0.5237250468389942 | 0.5358692366829972 |
| 3 | 0.10555097710790447 | 0.08370445514925137 | 0.08220364598215188 |
| 4 | 0.20843147727889014 | 0.24764692820651796 | 0.24274136343003053 |

All four stored fold metrics for every displayed configuration (including ties):

| Model | Configuration | Fold | WAPE | MAE | RMSE | Bias | Metric status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| xgboost | GBM003 | 1 | 0.031108142060737864 | 26.041372314453124 | 31.768896348600162 | -7.118696533203125 | valid |
| xgboost | GBM003 | 2 | 0.5397882450513437 | 266.8518759765625 | 268.4143400338119 | 266.8518759765625 | valid |
| xgboost | GBM003 | 3 | 0.10555097710790447 | 30.011942626953125 | 37.61749198599055 | 25.00572021484375 | valid |
| xgboost | GBM003 | 4 | 0.20843147727889014 | 78.42609509277344 | 84.1706376870191 | -78.39139904785156 | valid |
| lightgbm | GBM022 | 1 | 0.03407701798792307 | 28.526689606122112 | 35.47455688338353 | -9.776297165578045 | valid |
| lightgbm | GBM022 | 2 | 0.5237250468389942 | 258.9108090555125 | 260.9773080774304 | 258.9108090555125 | valid |
| lightgbm | GBM022 | 3 | 0.08370445514925137 | 23.800189959317535 | 29.77940010195416 | 9.511881421226475 | valid |
| lightgbm | GBM022 | 4 | 0.24764692820651796 | 93.1816143824101 | 98.33261952237645 | -93.1816143824101 | valid |
| catboost | GBM015 | 1 | 0.03084487618411814 | 25.820986130753713 | 32.09354106171641 | -5.191661864657093 | valid |
| catboost | GBM015 | 2 | 0.5358692366829972 | 264.9144593235533 | 266.60066910326844 | 264.9144593235533 | valid |
| catboost | GBM015 | 3 | 0.08220364598215188 | 23.373455883981137 | 29.234337786832675 | 9.079611844841152 | valid |
| catboost | GBM015 | 4 | 0.24274136343003053 | 91.33580733509072 | 96.24398395244346 | -91.33580733509072 | valid |

### Supportive comparison — Ridge and Random Forest

| model | evidence_role | configuration_id | canonical_config_id | selection_status | fold_count | n_predictions | mean_wape | mean_mae | mean_rmse | mean_bias | metric_status | review_status | artifact_paths |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ridge | supportive | fixed | unavailable | fixed_supportive | 4 | 1000 | 0.2324968287973077 | 99.43330304393726 | 108.92037642295254 | 22.59316231572189 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |
| random_forest | supportive | fixed | unavailable | fixed_supportive | 4 | 1000 | 0.2271170122760801 | 103.14828 | 108.68883307431503 | 42.140293333333325 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |

### Baseline comparison — Naive and Seasonal Naive

| model | evidence_role | configuration_id | canonical_config_id | selection_status | fold_count | n_predictions | mean_wape | mean_mae | mean_rmse | mean_bias | metric_status | review_status | artifact_paths |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| naive | simple_baseline | not_tuned | unavailable | not_applicable | 4 | 1000 | 0.29674079123033476 | 127.307 | 159.39396185275012 | 0.7689999999999996 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |
| seasonal_naive | simple_baseline | not_tuned | unavailable | not_applicable | 4 | 1000 | 0.14504068039350965 | 62.968999999999994 | 77.40066831588709 | 5.9289999999999985 | valid | pending_human_review | [summary](../../../artifacts/forecasting/validation-20261002-01/configuration_summary.csv); [folds](../../../artifacts/forecasting/validation-20261002-01/fold_metrics.csv); [predictions](../../../artifacts/forecasting/validation-20261002-01/predictions.csv) |

### Tie information

Primary model tie: none recorded.

- XGBoost configuration ties: none recorded.
- LightGBM configuration ties: none recorded.
- CatBoost configuration ties: none recorded.

### Limitations and status

Human selection/freeze remains pending; supportive and baseline evidence cannot establish a primary-model winner.
Human review should compare recorded error magnitudes, signed Bias and the direction/consistency of fold WAPE values.
Unavailable cells denote absent, unselected or undefined evidence; inspect CSV status/reason fields.
Selection unavailable unless all 24 complete four-fold configurations meet the existing selection rules.
Final evaluation remains blocked/not executed until separately authorised.

## Shared limitations

The dataset is simulated. Validation leaders are not frozen scientific conclusions.
Supporting metrics and fold stability require human review; no significance test is produced.
Overlapping training labels and shared training histories make folds dependent.
December 3–16 had prior validation exposure; full-year EDA also inspected the final interval.
Human selection/freeze and Gate 4/6 approval references must be reviewed in run_metadata.json.
