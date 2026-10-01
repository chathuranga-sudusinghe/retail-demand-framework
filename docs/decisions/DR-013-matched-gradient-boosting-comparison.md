# DR-013 — Matched Gradient-Boosting RQ2 Comparison

> **Current status cross-reference — Issue #94:** [The frozen protocol](../protocol.md) resolves prior pending supportive settings, baseline and runtime decisions. Issue #89 was merged through PR #90. [Runner operations](../forecasting-runner.md) distinguish approved storage policy from unchanged runtime behavior. Original decision/development wording below remains historical provenance; this status note changes no decision or authorizes any run.

**Date:** 2026-09-29

**Status:** Owner-approved research direction; protocol/runtime details resolved in the frozen protocol. Changed implementation and each experiment require separate human approval.

**Owner:** Chathuranga

**Related issue:** [#66 — Research: revise RQ2 with a matched gradient-boosting model comparison](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/66)

**Approval provenance:** The project owner's attached Issue #66 task brief explicitly supplies the human-approved revised direction. This record documents that instruction; it does not create AI approval of implementation, runtime proposals or hypothesis operationalisation. No separate supervisor/group approval is asserted; any required review remains with the team.

## Context and reason

The earlier comparison combined Ridge, Random Forest and LightGBM with different representations and unequal search spaces. The owner requests a controlled RQ2 experiment. The principal experimental variable is the gradient-boosting implementation. XGBoost Regressor, LightGBM Regressor and CatBoost Regressor are the three implementations in the primary matched gradient-boosting comparison. The revision precedes training, tuning or scoring for this revised design; historical Issue #52 evidence remains separate provenance and supplies no justification for a preferred primary model.

## Decision

**RQ2:** Under the same forecasting inputs, temporal validation design, evaluation metrics, and matched hyperparameter settings, how do XGBoost, LightGBM, and CatBoost compare in forecasting future retail demand?

**H0_RQ2:** Under the matched experimental conditions, XGBoost, LightGBM, and CatBoost show comparable demand-forecasting performance across the evaluated horizons.

**H1_RQ2:** Under the matched experimental conditions, demand-forecasting performance differs among XGBoost, LightGBM, and CatBoost across the evaluated horizons.

The main research question, RQ1 and existing group-level H0/H1 remain unchanged. The project owner approves these subordinate RQ2 hypotheses as comparative research hypotheses, not statistical-significance hypotheses.

| Role | Models | Evidence boundary |
|---|---|---|
| Primary RQ2 comparison | XGBoost Regressor, LightGBM Regressor, CatBoost Regressor | Only these three determine the matched-comparison RQ2 answer. |
| Supportive benchmarks | Ridge Regression, Random Forest Regressor | Contextual linear/non-linear references; label separately in tables. |
| Simple forecast baselines | Naive, Seasonal Naive (period 7) | DR-007 formulas and 28-day approval boundaries unchanged; no tuning. |

Primary controls are the same dataset, Units_Sold target, SKU_ID + Warehouse_ID + Date grain, fourteen conceptual predictors/formulas/order, physical representation, eligible rows, horizons 1/7/14/28, four temporal folds, WAPE primary and MAE/RMSE/Bias supporting, Cartesian search, dimensions/values/budget and seed 42. Fixed-origin forecasting and complete 28-day history remain mandatory. No cross-horizon composite is approved.

XGBoost, LightGBM and CatBoost use the same fitted category vocabulary within each fold/horizon and the same physical feature column order: full one-hot SKU_ID, full one-hot Warehouse_ID (all fitted levels retained), followed by the same twelve frozen numerical predictors in their existing order. Each primary model has **67 physical columns under full 50-SKU / 5-warehouse training coverage: 50 + 5 + 12 = 67**. Category vocabularies are fitted only on eligible training rows and shared across the three implementations. Native LightGBM/CatBoost categorical handling is excluded. Tree inputs are unscaled; supportive Ridge alone may standardise numerical predictors. The frozen fourteen conceptual predictors, numerical formulas and order remain unchanged.

## RQ2 interpretation and claim boundaries

RQ2 evidence is interpreted descriptively and comparatively, separately for each horizon. WAPE remains the primary comparison metric: compare arithmetic mean WAPE across the four temporal folds, retain and inspect all four fold-level WAPE results, and use MAE, RMSE and Bias as supporting metrics. Report the magnitude and direction of performance differences; relative differences may also be reported when clearly defined. Examine whether observed differences are reasonably consistent across folds.

No statistical-significance procedure is approved for RQ2. The four temporal folds are not treated as independent experimental replicates. No universal numerical threshold is predeclared for a "meaningful difference". A small aggregate difference driven primarily by one fold must not be presented as strong evidence of a general performance difference. Discuss magnitude, direction, fold consistency and supporting metrics rather than mechanically accepting or rejecting H0_RQ2 using an arbitrary threshold.

Do not average or rank performance across horizons into a single composite. Model ordering may differ by horizon; report those differences rather than collapsing them into an overall winner.

## Matched canonical grid and API mapping

| Canonical dimension | Values | XGBRegressor | LGBMRegressor | CatBoostRegressor |
|---|---|---|---|---|
| learning_rate | [0.03, 0.05, 0.10] | learning_rate | learning_rate | learning_rate |
| boosting_iterations | [100, 300] | n_estimators | n_estimators | iterations |
| max_depth | [4, 8] | max_depth | max_depth | depth |
| subsample | [0.8, 1.0] | subsample | subsample | subsample |
| Fixed seed (not searched) | 42 | random_state | random_state | random_seed |

**3 × 2 × 2 × 2 = 24 configurations per primary model × horizon.** Use ordered Cartesian products with subsample varying fastest. Record both canonical identity and complete effective API settings; the same configuration identity maps to all three models. The ordering and metadata requirements below must be incorporated into the preserved [Issue #65 protocol draft](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/65) during its later continuation; they do not imply that draft is aligned or approved.

**24 × 3 × 4 × 4 = 1,152 planned primary validation fits.** This excludes supportive work, simple baseline evaluations and subsequent final refits. No fit was executed under this task.

## Canonical identities and reproducibility requirements

Enumerate the Cartesian product of learning_rate, boosting_iterations, max_depth and subsample in that order, using each listed value order; subsample varies fastest. Assign one-based identities `GBM001` through `GBM024`, independent of model, horizon and fold. `GBM001` is (0.03, 100, 4, 0.8); `GBM015` is (0.05, 300, 8, 0.8); `GBM024` is (0.10, 300, 8, 1.0). Each identity has exactly the same canonical values across all three primary models. A fit is uniquely identified by run, stage, model, horizon, canonical configuration ID and fold, so shared configuration IDs do not collide. Model order is XGBoost, LightGBM, CatBoost; horizon order is 1, 7, 14, 28; fold order is 1, 2, 3, 4. These are deterministic external iteration/record orders, not estimator fitting instructions.

For each later authorised run, record Git SHA/branch and working-tree state; Python and exact library versions/builds; operating system/hardware/device; thread counts, parallelism and determinism controls; every seed and its effective API mapping; feature-contract and DR versions; conceptual and physical feature order/count; eligible row counts/keys and exclusions by fold/horizon; training dates, fixed origin and target interval; training-only category vocabularies; the complete canonical grid/ordered ID mapping; requested and effective API parameters including fixed settings/defaults; fold metrics and their arithmetic means by horizon; selected configuration and human selection rationale; and artifact paths. The canonical seed is 42 throughout candidates/folds/horizons; any additional library seeds must be explicitly recorded consistently before execution. Fixed seed does not imply identical random samples or bit-for-bit equality across libraries.

Issue #65 must revise artifact schemas to carry `evidence_role` (primary/supportive/simple_baseline), `canonical_config_id`, canonical parameter values and library-specific effective parameters separately. Preserve fold/configuration metrics, horizon-specific selections/comparison, auditable prediction rows and run metadata. Prospective forecasts remain separate from actual-demand/error records. Supportive/simple-baseline rows must not enter primary RQ2 ranking. Exact artifact filenames/types, missing-metric representation and tie handling belong to the preserved protocol's later human review; no schema implementation occurs here.

## Fixed runtime controls and unresolved decisions

The checked official APIs support the matched dimensions; no documented incompatibility with full numeric one-hot inputs or the specified subsample/depth values was identified. This is API-documentation evidence, not installed-runtime testing.

The project owner explicitly approves the following fixed runtime/model and subsampling controls for the primary matched XGBoost / LightGBM / CatBoost comparison. This approval records these controls only; it does not authorise implementation acceptance or experiment execution.

| Primary model | Human-approved fixed controls | Fixed execution / seed |
|---|---|---|
| XGBoost | `objective="reg:squarederror"`, `booster="gbtree"`, `tree_method="hist"`, `sampling_method="uniform"`, `colsample_bytree=1.0` | CPU execution; `random_state=42` |
| LightGBM | `objective="regression"`, `boosting_type="gbdt"`, `data_sample_strategy="bagging"`, `subsample_freq=1`, `deterministic=True`, `force_col_wise=True`, `feature_fraction=1.0` | CPU execution; `random_state=42` |
| CatBoost | `loss_function="RMSE"`, `grow_policy="SymmetricTree"`, `bootstrap_type="Bernoulli"`, `sampling_unit="Object"`, `sampling_frequency="PerTree"`, `rsm=1.0`, `use_best_model=False` | `task_type="CPU"`; `random_seed=42` |

These controls are fixed runtime settings, not tuning dimensions. **`subsample` remains a matched tuning dimension with canonical values `[0.8, 1.0]`.** `subsample=0.8` must actually activate row subsampling; `subsample=1.0` retains all eligible training rows. Matched fractions do not imply identical sampled rows or identical internal sampling algorithms across libraries. CPU execution and the model-specific seed mappings above are fixed across the primary grid.

**Iteration-count fairness:** Early stopping is disabled for every primary matched configuration; do not use validation-based early-stopping settings or callbacks. CatBoost `use_best_model=False` is fixed. The canonical `boosting_iterations` value (100 or 300) must remain the requested and effective iteration/tree count for each fitted primary configuration. Record requested and effective counts; no library may silently shorten a configuration because of validation-based stopping.

**Training loss and evaluation:** The three primary models use library-specific squared-error regression formulations: XGBoost `objective="reg:squarederror"`, LightGBM `objective="regression"` and CatBoost `loss_function="RMSE"`. These formulations do not imply mathematically identical internal implementations. Training loss and evaluation/model-selection metrics are separate concepts. WAPE remains the primary model-selection metric; MAE, RMSE and Bias remain supporting evaluation metrics.

**Fairness and fixed defaults:** The controlled experiment matches externally comparable learning rate, boosting iterations, maximum depth, subsample fraction, input representation, data, folds, horizons, metrics and seed policy. Library-specific internal tree-growing algorithms remain different; the study does not attempt to force identical internal implementations. LightGBM remains internally leaf-wise despite externally matched maximum depth, so identical tree topology is not claimed. Non-matched model-specific controls are fixed rather than tuned. Column sampling is fixed at full-feature use through XGBoost `colsample_bytree=1.0`, LightGBM `feature_fraction=1.0` and CatBoost `rsm=1.0`. No additional tuning dimension may be introduced without separate human review.

- XGBoost regularisation and other tree-growth parameters remain at the pinned-library defaults unless explicitly listed in this record; capture inherited effective defaults in run metadata.
- LightGBM remaining growth/regularisation settings remain at the pinned-library defaults unless explicitly fixed in this record; capture effective values, including `num_leaves`, in run metadata. `num_leaves` is a fixed control, not a fifth search dimension. Do not enable `force_row_wise` simultaneously with the fixed `force_col_wise=True` setting.
- CatBoost remaining regularisation parameters remain at the pinned-library defaults unless explicitly fixed in this record; capture effective values in run metadata.

**Threading and reproducibility:** All primary models run on CPU with seed 42 and should use the same execution environment for the controlled comparison. LightGBM `deterministic=True` and `force_col_wise=True` are fixed. Thread counts must be explicitly fixed before experiment execution; no numeric thread count is approved in this record. Thread-count choice remains a final human implementation/protocol decision. Capture exact effective runtime parameters, inherited defaults from the pinned versions, thread counts and seed mappings in run metadata. These controls do not guarantee bit-for-bit equality across libraries.

The project owner reports the following pinned and verified library versions for the planned Issue #66 implementation. The local Python version is **3.12.3**; the four library versions match the exact pins in `requirements.txt`.

| Runtime / library | Verified version / exact pin | Scope |
|---|---|---|
| Python | `3.12.3` | Local project runtime |
| XGBoost | `xgboost==3.4.1` | Primary RQ2 comparison |
| LightGBM | `lightgbm==4.7.0` | Primary RQ2 comparison |
| CatBoost | `catboost==1.2.10` | Primary RQ2 comparison |
| scikit-learn | `scikit-learn==1.9.1` | Supportive Ridge Regression / Random Forest environment and preprocessing utilities |

The owner confirms that all four libraries imported successfully, reported versions matched the requirements pins, and `pip check` reported: "No broken requirements found." Successful import and pip dependency verification do **not** constitute model training, experimental validation, scientific evidence or execution approval.

The matched canonical grid remains unchanged. The fixed controls, objectives/losses, pinned-library default policy, CPU execution, seed mappings and iteration-retention rules above are human-approved. Numeric thread counts and remaining execution/protocol details still require human review; inherited defaults must be explicitly captured rather than silently inferred. The complete mapped recipe still requires version-specific verification before execution. The earlier LightGBM API evidence was checked against 4.6.0 and must be rechecked against the pinned 4.7.0 version.

## Supportive benchmark configuration policy

The project owner approves **one fixed, predeclared configuration for each supportive model**, with no Ridge Regression or Random Forest hyperparameter search. Historical Ridge / Random Forest 5/12 configuration grids remain superseded and are not reused. Ridge is a regularised linear benchmark; Random Forest is a non-linear bagged-tree benchmark. These configurations provide contextual comparison and are not presented as optimal.

| Supportive model | Human-approved fixed configuration |
|---|---|
| Ridge Regression | `alpha=1.0`, `fit_intercept=True`, `solver="auto"` |
| Random Forest Regressor | `n_estimators=300`, `max_depth=None`, `min_samples_split=2`, `min_samples_leaf=1`, `max_features=1.0`, `bootstrap=True`, `random_state=42` |

**Ridge preprocessing:** Use full one-hot `SKU_ID` / `Warehouse_ID` identities and the twelve frozen numerical predictors. Standardise only those twelve numerical predictors; identity indicators remain 0/1. No Ridge hyperparameter search is approved.

**Random Forest preprocessing:** Use the common full one-hot representation with 67 physical columns under full category coverage (50 SKU identities + 5 warehouse identities + 12 numerical predictors), with unscaled numerical predictors. No Random Forest hyperparameter search is approved. Thread count / `n_jobs` remains an implementation/protocol control to be fixed before execution.

**Evaluation role:** Both supportive models use the same target definitions, forecast horizons, temporal folds, eligible observations and WAPE / MAE / RMSE / Bias evaluation definitions. Report their results separately as supportive/contextual evidence. They do not enter or compete within the matched 24-configuration primary grid, contribute to the 1,152 planned primary validation fits, determine the answer to RQ2 or replace the Naive / Seasonal Naive baseline roles. Only XGBoost, LightGBM and CatBoost determine the primary RQ2 comparison. This supportive-policy approval does not authorise implementation acceptance or experiment execution.

## Human decisions still required

- Review the complete mapped runtime recipe and verify it against the pinned library versions recorded above. The specified controls and inherited-default policy are human-approved as recorded; successful imports and pip dependency verification do not approve additional runtime changes or experiment execution.
- Choose and explicitly fix numeric thread counts and remaining execution/parallelism details through final implementation/protocol review before execution. Seed aliases beyond the approved top-level mapping must be explicit. Objectives/losses, tree controls, full-feature column sampling, LightGBM determinism settings and the pinned-library default policy above are already approved and introduce no new tuning dimension.
- Resolve the pre-existing proposed 28-day Naive/Seasonal Naive formulas under their separate approval boundaries.
- After Issue #66 approval, continue Issue #65 from its preserved stash, reassess the earlier four unresolved items, revise artifact schemas/selection handling and freeze the executable protocol. Gate 1 is not completed here. Later primary implementation alignment, test acceptance and each specific validation/final-evaluation run remain separate gates.

None of these is silently declared resolved by this record. Do not run experiments, install packages, restore the stash or infer execution authority from the approved direction.

## Supersession and preserved provisions

- **DR-007:** supersedes primary learned-model roles. Preserves Naive/Seasonal Naive definitions, baseline status and proposed 28-day approval boundaries.
- **DR-009:** supersedes selection of LightGBM as the only boosting candidate and exclusion of other boosting implementations from the current scope.
- **DR-010:** supersedes primary unequal grids, representation and 41-configuration/656-fit planning. Earlier Ridge/Random Forest grids remain provenance and are not reused; the approved supportive policy uses one fixed, predeclared configuration per model with no hyperparameter search.
- **Issue #57 feature contract:** revises categorical physical representation only; the fourteen conceptual predictors, numerical formulas/order and completeness remain frozen.
- **DR-006:** metric formulas and horizon-specific selection remain unchanged; primary RQ2 evidence is restricted to the three boosting models.
- DR-002/004/005/008, final origin 2024-12-02 and interval 2024-12-03–2024-12-30 remain unchanged. Prior December 3–16 validation and full-year EDA exposure remain disclosed.

Earlier DR bodies are retained verbatim beneath explicit notices. Historical Issue #52 protocol/results, exploratory reports and source/test behaviour are preserved; no historical result is relabelled as revised-model evidence.

## Alternatives considered

- Retain the heterogeneous Ridge/Random Forest/LightGBM primary comparison: rejected by the owner's revised direction because representation/search scope would also differ.
- Use native categorical support for LightGBM/CatBoost: excluded from the primary comparison to control representation.
- Tune model-specific additional dimensions: excluded; only the four matched dimensions are searched.
- Remove simple/supportive benchmarks: rejected; contextual and baseline evidence remain useful under separate roles.

## Impact and execution boundary

The accepted Issue #62 feature/preprocessing implementation reflects the earlier contract. Features/targets/fold utilities exist, but preprocessing supports only ridge/random_forest/lightgbm and returns native categorical LightGBM inputs. After design approval, a separate alignment task must add the common primary encoding and XGBoost/CatBoost representation interfaces/tests. Model classes, metric code and a runner are not implemented here. No source/tests/dependencies change in Issue #66.

[Issue #65](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/65) must align, review and freeze its preserved `docs/protocol.md` after this revision. Gate 1 remains incomplete; subsequent implementation acceptance, validation-run authorisation, selection freeze and final-evaluation authorisation are separate human gates. The owner confirms that `docs/protocol.md` and the earlier review work are preserved in the Git stash named `issue-65 protocol draft before rq2 redesign`. Issue #66 does not inspect, restore, modify or drop that stash or reconstruct the protocol. Issue #65 remains blocked on human approval of this revision; its later continuation must align the preserved draft and reassess its previous four unresolved items. Those items cannot be declared resolved or copied speculatively in this task.

## Limitations and references

Matched external values do not equalise internal tree-growing algorithms, capacity, parameter effects or random sampling. Equal maximum depth does not remove LightGBM leaf-count controls or CatBoost symmetric-tree differences. Four dependent folds do not justify an invented significance test. The study uses one simulated year; results cannot establish real-retailer effectiveness or universal model superiority. Fixed seed 42 does not measure variability over seeds or promise bit-for-bit cross-library equality.

API evidence checked on 2026-09-29 (version-free documentation must be rechecked against selected pins):

- [XGBoost parameters](https://xgboost.readthedocs.io/en/stable/parameter.html) and [XGBRegressor API](https://xgboost.readthedocs.io/en/stable/python/python_api.html#xgboost.XGBRegressor).
- [LightGBM 4.6.0 parameters](https://lightgbm.readthedocs.io/en/v4.6.0/Parameters.html) and [LGBMRegressor API](https://lightgbm.readthedocs.io/en/v4.6.0/pythonapi/lightgbm.LGBMRegressor.html).
- [CatBoost common parameters](https://catboost.ai/docs/en/references/training-parameters/common) and [CatBoostRegressor API](https://catboost.ai/docs/en/concepts/python-reference_catboostregressor).
