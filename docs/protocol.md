# Revised forecasting experiment protocol — Issue #65

**Status:** GATE 1 SCIENTIFIC PROTOCOL HUMAN-APPROVED / FROZEN — NO NEW EXECUTION AUTHORIZATION

**Operational alignment:** Issue #94 documentation reconciliation for human review; approved Issues #92/#93 supply architecture authorities. Runtime migration remains unimplemented.

**Prepared:** 2026-09-29

**Owner:** Chathuranga

**Protocol version:** `issue-65-matched-frozen-1`

**Human decisions recorded:** 2026-09-29, on the project owner's explicit Issue #65
instruction: exact-tie handling, single-thread runtime, 28-day simple baselines
and deferral of final refit/preprocessing to Gate 6. These decisions remain
unchanged.

**Gate 1 approval/freeze:** 2026-09-29, explicitly approved by the project owner
after reviewing the complete protocol. Approval reference: the project owner's
Issue #65 instruction, "I have reviewed and approved `docs/protocol.md` for
Issue #65. Record Gate 1 as human-approved/frozen." This approves the validation
protocol only; experiment execution remains **NOT AUTHORISED**.

**Issue:** [#65 — Research: define and freeze revised forecasting experiment protocol](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/65)

## 1. Authority, scope and current implementation

`docs/protocol.md` is the consolidated, human-approved and frozen forecasting
validation experiment protocol. Gate 1 is complete on the explicit project-owner
approval recorded above. Accepted runner implementation and specific run
authorisation remain required; protocol approval does not grant execution approval.

The current research authority is
[DR-013](decisions/DR-013-matched-gradient-boosting-comparison.md): XGBoost,
LightGBM and CatBoost are the primary controlled RQ2 comparison; Ridge and
Random Forest are fixed supportive benchmarks only. DR-013 supersedes the
learned-model roles in DR-007, the single-boosting choice in DR-009 and the
primary grids/representation/fit counts in DR-010. Their historical bodies do
not supply current execution instructions. DR-007's retained 1/7/14-day
simple-baseline formulas remain unchanged. The project owner's decisions recorded
in this protocol resolve the previously pending 28-day formulas and numeric
thread policy; no other decision record or source file is changed here.

[DR-004](decisions/DR-004-forecast-horizons.md),
[DR-005](decisions/DR-005-forecast-validation-design.md),
[DR-006](decisions/DR-006-forecasting-metrics-and-model-selection.md),
[DR-008](decisions/DR-008-multi-step-forecasting-strategy.md) and the
[frozen feature contract](forecasting-feature-engineering.md) continue to govern
horizons, dates, metrics, direct targets and predictor formulas. The only new
resolutions are the explicit human decisions recorded above and in Section 18.
The older Issue #65 body and companion-document implementation notes describe
the pre-#66/pre-#68 state;
current DR-013 decisions and the merged interfaces below take precedence.

Issue #68 implementation alignment is complete and merged into the inspected
main-aligned checkout through PR #69. The existing reusable interfaces are:

| Existing interface | Protocol use |
|---|---|
| [features.py](../src/forecasting/features.py): `build_features`, `feature_eligibility` | Historical predictors and complete-vector eligibility |
| [features.py](../src/forecasting/features.py): `build_origin_features` | One fixed-origin evidence row per historical pair |
| [preprocessing.py](../src/forecasting/preprocessing.py): `fit_primary_preprocessors` | Fit one eligible-training vocabulary and share immutable unscaled primary representations |
| [preprocessing.py](../src/forecasting/preprocessing.py): `fit_preprocessor`, `ForecastPreprocessor.transform` | Training-only supportive scaling/encoding and prediction transformation without refitting |
| [configuration.py](../src/forecasting/configuration.py): `PRIMARY_GRID`, `primary_configuration_grid`, `primary_model_parameters` | Canonical `GBM001`–`GBM024` grid and primary API mappings/fixed controls |
| [configuration.py](../src/forecasting/configuration.py): `supportive_model_parameters` | One predeclared configuration per supportive model; no search |
| [targets.py](../src/forecasting/targets.py): `build_horizon_targets` | Complete observed cumulative labels, separate from predictors |
| [validation.py](../src/forecasting/validation.py): `split_fold`, `VALIDATION_FOLDS`, `FINAL_HOLDOUT` | Exact fold slicing and final interval boundaries |

`FINAL_HOLDOUT` remains a legacy identifier for the revised final evaluation
interval, not a claim that it is historically unseen. The current
[feature tests](../tests/test_forecasting_features.py),
[preprocessing tests](../tests/test_forecasting_preprocessing.py) and
[configuration tests](../tests/test_forecasting_configuration.py) cover the
frozen calculations, targets/boundaries, identical primary matrices, training-only
vocabularies, supportive scaling, grid identities and parameter declarations.
They are inspected as implementation evidence; this documentation task does not
execute them or infer scientific performance from them.

The configuration layer declares parameters without constructing estimators.
Estimator orchestration, metrics, baselines and the runner are now implemented;
Issue #89 was merged through PR #90. The owner confirms validation has occurred;
[methodology provenance](forecasting-methodology-revision.md) records the evidence
availability boundary. The unchanged runner does not implement the approved
storage layout. No new command is authorized by this reconciliation. The deferred
Gate 6 policy in Section 18 and
[AGENTS.md](../AGENTS.md), Sections 17–19, remain binding.

## 2. Frozen target, predictor information and ordering

The dataset is simulated. The target is `Units_Sold` at
`SKU_ID + Warehouse_ID + Date`; [dataset.md](dataset.md) records its limitations.
For origin o and horizon h in `1, 7, 14, 28`, the direct observed target is:

$$
Y_{o,h}=\sum_{j=1}^{h}y_{o+j}.
$$

For h=1 this is next-day demand; h=7/14/28 are cumulative totals. No daily path,
recursive prediction or within-window updating is implied. All learned models
receive the same ordered fourteen conceptual predictors:

```text
SKU_ID
Warehouse_ID
dow_sin
dow_cos
lag_1
lag_7
lag_14
rolling_mean_7
rolling_std_7
rolling_mean_14
rolling_std_14
rolling_mean_28
rolling_std_28
rolling_slope_14
```

The last twelve are the numerical feature order. Calendar phase refers to the
first target day t=o+1, Monday=0 through Sunday=6. Lags are y_o, y_(o-6) and
y_(o-13). Rolling mean/sample std (`ddof=1`) and oldest-to-newest fourteen-day
slope end at o, exactly as defined in the feature contract.

`Date` is alignment/calendar construction only; raw `Units_Sold` supplies history
and separate labels. The eleven other raw fields remain excluded forecasting
predictors: `Supplier_ID`, `Region`, `Inventory_Level`, `Supplier_Lead_Time_Days`,
`Reorder_Point`, `Order_Quantity`, `Unit_Cost`, `Unit_Price`, `Promotion_Flag`,
`Stockout_Flag`, `Demand_Forecast`. No raw weekday, month/quarter, lag_28, median,
interaction or other additional predictor is permitted. No source forecast,
future operational value, label or retrospective error enters a predictor matrix.

## 3. Temporal boundaries

All dates are inclusive and timezone-naive calendar days. Training begins on
2024-01-01 in each fold. The validation interval supplies outcomes only; each
horizon's target ends at origin+h, not automatically at the interval's last day.

| Fold | Training start | Training end / origin | Training days | Validation start | Validation end |
|---|---|---|---:|---|---|
| 1 | 2024-01-01 | 2024-03-31 | 91 | 2024-04-01 | 2024-04-28 |
| 2 | 2024-01-01 | 2024-06-30 | 182 | 2024-07-01 | 2024-07-28 |
| 3 | 2024-01-01 | 2024-09-30 | 274 | 2024-10-01 | 2024-10-28 |
| 4 | 2024-01-01 | 2024-11-04 | 309 | 2024-11-05 | 2024-12-02 |

Final evaluation has origin **2024-12-02** and interval
**2024-12-03 to 2024-12-30**, after its separate approvals. It is reserved from
subsequent fitting/selection, but **not historically fully unseen**:
December 3–16 had earlier validation exposure, and full-year exploratory data
analysis (EDA) inspected the interval. Both disclosures must accompany results.
No December 31 observation is invented. Earlier validation dates may become
historical training data in later folds once available at the later cutoff.

## 4. Historical labelled-row eligibility

For a historical row Date=t, its own origin is t-1. For fitting cutoff c and
horizon h, include the row only when all of the following hold:

1. The same SKU–warehouse pair has 28 complete consecutive daily demand values
   on t-28 through t-1, all available at that row's origin.
2. Both categorical identities and all twelve finite numerical predictors are
   available, in the exact conceptual order above.
3. Every demand observation on t through t+h-1 is present and nonmissing,
   with t+h-1 no later than c, inside the assigned training interval.
4. No imputation, partial/shortened rolling window, future fill, shortened label
   or replacement observation is used.

Use only raw keys/demand inside the training interval to build historical
features. Build labels separately with `build_horizon_targets(training,
window_start=training_start, window_end=training_end)`. Match feature and target
rows one-to-one by `SKU_ID`, `Warehouse_ID`, `Date`; validate uniqueness and
alignment. Intersect `feature_eligibility` with availability of `target_h_day`
and the complete outcome-end boundary. Pass ONLY those accepted predictor rows
and the aligned label vector to later preprocessing/model fitting. The label
never joins the model input columns.

`fit_preprocessor` additionally checks dates, predictor completeness and the
horizon-end cutoff. It does **not** verify observed label completeness, so the
runner must perform the target-availability intersection first. Invalid keys,
invalid observed quantities or strict target/fold date-coverage failures produce
explicit diagnostics; do not repair the data or infer a new cleaning policy.

For N consecutive observed dates, feasibility before other exclusions is
N - 28 - h + 1; an interval shorter than 28+h supplies no eligible rows.

| Horizon | Feasible rows per series in the 91-day first training fold |
|---|---:|
| 1 | 63 |
| 7 | 57 |
| 14 | 50 |
| 28 | 36 |

These are feasibility counts, not independent-sample counts or guaranteed actual
eligibility. Cumulative labels overlap and folds share histories. Record raw,
feature-eligible, label-eligible and intersected fitting counts per fold/horizon,
including per-pair counts and explicit, potentially overlapping exclusion reasons.
Use identical fitting rows across learned candidates within each fold/horizon.

## 5. Fixed-origin validation procedure

For each fold, use the many eligible historical labelled rows for fitting one
pooled learned estimator per model × horizon × configuration. Every history
operation remains grouped by BOTH SKU and warehouse. Validation is different:
it uses one fixed-origin evidence row per pair, not every day as a new origin.

1. Isolate the named fold's raw training and outcome windows using `split_fold`;
   exclude dates outside the fold before feature construction or fitting.
2. Construct training rows/labels under Section 4. Keep validation outcomes
   outside all training matrices and preprocessing statistics.
3. Call `build_origin_features(training, origin=training_end)`, or select the
   equivalent masked row Date=origin+1. This calendar-only target-start row
   needs no future realised demand. Validate exactly one row per training pair.
4. Check all origin predictors are feature-eligible. Reuse the SAME underlying
   fourteen-predictor row across all four horizons. Apply each horizon's fitted
   preprocessing: identical representations across the three primary models,
   and numerical scaling for supportive Ridge. Never select later
   validation-date feature rows or update with realised validation demand.
5. Independently build observed labels from the validation outcome interval and
   select Date=origin+1 for each horizon. Labels cover origin+1 through origin+h.
6. Evaluate each authorised candidate on the same keyed pair population and
   complete targets for that horizon. Record pair coverage and ordered-key
   fingerprints; no candidate-dependent exclusion is allowed.

The runner must fail preflight if a required pair lacks an accepted origin
vector, complete target or approved baseline history, or a category is unseen.
It must retain diagnostics rather than silently dropping pairs or manufacturing
completeness. The expected pair roster comes from training data, checked against
the native dataset coverage; future categories cannot define the training roster.
No result from an incomplete/failed fold becomes a valid four-fold comparison.

## 6. Exact preprocessing interface and representations

For each fold/horizon, first complete the labelled-row eligibility intersection
in Section 4. Call `fit_primary_preprocessors(eligible_training_features,
training_end=training_end, horizon=h)` once. Its `xgboost`, `lightgbm` and
`catboost` states share the same fitted vocabulary, training population, physical
column order and unscaled numerical values. Transform the same eligible training
rows and same keyed origin rows with those states; require identical primary
matrices within that fold/horizon.

For supportive models, call `fit_preprocessor` on the SAME eligible training
features with `model="ridge"` or `model="random_forest"`, the same cutoff and
horizon. The single-model interface also accepts all three primary model keys,
but independently fitted states must never imply different primary populations,
vocabularies or matrix order. Reuse fitted state across configurations only
within the same fold/horizon and fitting population. Transform never refits.
Do not reuse learned state between folds or horizons with different fitting rows.

| Evidence role / model | Categorical treatment | Numerical treatment | Full-coverage width |
|---|---|---|---:|
| Primary XGBoost | Full one-hot SKU_ID + Warehouse_ID, all levels retained | Twelve frozen predictors, unscaled | 67 |
| Primary LightGBM | Identical full one-hot vocabulary and column order | Identical unscaled values | 67 |
| Primary CatBoost | Identical full one-hot vocabulary and column order | Identical unscaled values | 67 |
| Supportive Ridge | Full one-hot identities, indicators remain 0/1 | Standardise only twelve numerical predictors | 67 |
| Supportive Random Forest | Same full one-hot identities | Unscaled numerical values | 67 |

Fit categories only from eligible labelled training rows, never from validation
or final-evaluation identities. Lexically sorted SKU columns come first, then
lexically sorted warehouse columns, then the twelve frozen numerical predictors
in Section 2 order. Native categorical LightGBM/CatBoost is excluded from the
primary path. No categorical dtype, ordinal ID or new predictor is substituted.

Full coverage means 50 + 5 + 12 = 67 physical columns representing fourteen
conceptual predictors. Smaller training coverage yields training_SKU_count +
training_warehouse_count + 12, equally for the primary models; never pad with
future categories. Unknown prediction identities fail explicitly: no all-zero
fallback, category extension, imputation or silent population exclusion.

Ridge uses (x-training_mean)/training_scale with population standard deviation
(`ddof=0`) and unit scale for a constant training column. Identity indicators
remain 0/1. This does not change demand-window sample standard deviations
(`ddof=1`). The primary models and Random Forest do not scale numerical inputs.

Record `conceptual_feature_names`, `numerical_feature_names`,
`categorical_feature_names`, `physical_feature_names`, `physical_feature_count`,
`category_vocabularies`, `category_mappings`, `training_row_count` and Ridge
means/scales. Link fitted states by fold/horizon/stage and training population.
Feature-only preprocessing does not verify labels; the runner must first enforce
complete observed outcomes and the same eligible population for all candidates.

## 7. Matched primary grid, fixed controls and deterministic ordering

### 7.1 Primary configuration space

Use DR-013 and the merged `PRIMARY_GRID` unchanged. For every primary model and
horizon, `primary_configuration_grid(model, horizon=h)` returns the SAME ordered
24 canonical declarations:

| Canonical dimension | Ordered values | XGBoost API | LightGBM API | CatBoost API |
|---|---|---|---|---|
| `learning_rate` | [0.03, 0.05, 0.10] | `learning_rate` | `learning_rate` | `learning_rate` |
| `boosting_iterations` | [100, 300] | `n_estimators` | `n_estimators` | `iterations` |
| `max_depth` | [4, 8] | `max_depth` | `max_depth` | `depth` |
| `subsample` | [0.8, 1.0] | `subsample` | `subsample` | `subsample` |

Enumerate the Cartesian product in this field order and each listed value order;
subsample varies fastest. IDs `GBM001`–`GBM024` are shared across models,
horizons and folds for the same canonical combination. `GBM001` is
(0.03, 100, 4, 0.8), `GBM015` is (0.05, 300, 8, 0.8), and `GBM024` is
(0.10, 300, 8, 1.0). Use `primary_model_parameters(model, configuration)` to map
those declarations. Record `canonical_config_id`, canonical values, requested
API parameters and complete effective API parameters separately.

Primary model order is `xgboost`, `lightgbm`, `catboost`; horizon order is
`1, 7, 14, 28`; configuration order is `GBM001`–`GBM024`; fold order is
`1, 2, 3, 4`. These are external iteration/record orders. Section 9 uses the
lowest canonical ID only as an administrative representative of an exact
within-model/horizon tie; order never implies scientific superiority.
Scheduling must not change identities or artifact ordering.

Evaluate EVERY approved primary configuration across all four temporal folds:
**24 × 3 primary models × 4 horizons × 4 folds = 1,152 planned primary validation
fits**. This excludes supportive fits, simple-baseline calculations and later
final refits. There is no random K-fold, adaptive search, grid expansion,
additional tuning dimension, seed search or performance-driven retry policy.

### 7.2 Approved primary runtime controls

| Model | Fixed settings, in addition to the mapped grid values |
|---|---|
| XGBoost | `objective="reg:squarederror"`, `booster="gbtree"`, `tree_method="hist"`, `sampling_method="uniform"`, `colsample_bytree=1.0`, `random_state=42`, `device="cpu"`, `n_jobs=1` |
| LightGBM | `objective="regression"`, `boosting_type="gbdt"`, `data_sample_strategy="bagging"`, `subsample_freq=1`, `deterministic=True`, `force_col_wise=True`, `force_row_wise=False`, `feature_fraction=1.0`, `random_state=42`, `device_type="cpu"`, `n_jobs=1` |
| CatBoost | `loss_function="RMSE"`, `bootstrap_type="Bernoulli"`, `sampling_unit="Object"`, `sampling_frequency="PerTree"`, `task_type="CPU"`, `grow_policy="SymmetricTree"`, `rsm=1.0`, `use_best_model=False`, `random_seed=42`, `thread_count=1` |

`subsample=0.8` must activate row subsampling; `subsample=1.0` retains all eligible
training rows. Fixed enabling controls are not additional tuning dimensions.
Matched fractions do not imply identical sampled rows or internal algorithms.
Column sampling is fixed at full-feature use. LightGBM remains internally
leaf-wise; matched depth does not imply identical tree topology.

No primary early stopping, validation-based stopping callback or CatBoost
best-model truncation is permitted. Requested and effective iteration/tree counts
must match the canonical 100 or 300 value. Record both counts and report/fail an
unexpected mismatch instead of silently shortening the budget or fabricating
extra trees. The parameter layer alone is not a fit-time stopping guard; the
future runner must enforce these restrictions.

Training uses library-specific squared-error regression formulations. These are
not identical internal implementations, and their losses do not replace WAPE
as the primary evaluation/selection metric. Unlisted growth/regularisation
settings inherit pinned-library defaults as approved in DR-013; record their
effective values, including LightGBM `num_leaves`. Do not silently override them.

### 7.3 Fixed supportive configurations

Use the fixed configuration declared by `supportive_model_parameters`, plus
the approved Random Forest thread control in Section 7.4, with one configuration
per model and NO hyperparameter search:

| Supportive model | Fixed parameters | Evidence purpose |
|---|---|---|
| Ridge | `alpha=1.0`, `fit_intercept=True`, `solver="auto"` | Regularised linear contextual benchmark |
| Random Forest | `n_estimators=300`, `max_depth=None`, `min_samples_split=2`, `min_samples_leaf=1`, `max_features=1.0`, `bootstrap=True`, `random_state=42`, `n_jobs=1` | Non-linear bagged-tree contextual benchmark |

The historical 5/12 grids are not reused. These are predeclared benchmarks, not
claimed optimal configurations. They use the same targets, horizons, folds,
eligible rows and metric definitions as the primary models. Report them
separately; they cannot enter the primary grid/ranking, determine RQ2 or replace
Naive/Seasonal Naive. If all four horizons/folds are authorised, this is
2 × 4 × 4 = 32 supportive fits, separate from the 1,152 primary fits.

Record order after the primary block is `ridge`, `random_forest`, then
`naive`, `seasonal_naive` in their separately approved baseline scope. Supportive
records use `configuration_id="fixed"` and `canonical_config_id=null`; simple
baselines use `configuration_id="not_tuned"` and `canonical_config_id=null`.
Primary `configuration_id` equals its `canonical_config_id`. Model/stage/run/
horizon/fold remain part of every composite key, so shared IDs do not collide.

### 7.4 Versions, CPU and frozen single-thread runtime controls

DR-013 records Python **3.12.3** and the pinned, import/dependency-verified
versions `xgboost==3.4.1`, `lightgbm==4.7.0`, `catboost==1.2.10` and
`scikit-learn==1.9.1`. scikit-learn supplies supportive Ridge/Random Forest and
preprocessing utilities. Verify and record the actual versions/builds for a
later authorised run; a mismatch requires review, not silent pin changes.
Import success and `pip check` are not training, experimental validation,
scientific evidence or execution approval.

CPU execution, seed 42 and all existing primary/supportive model controls are
preserved. The project owner has approved the following fixed execution controls:

| Component | Fixed runtime control |
|---|---|
| XGBoost | `n_jobs=1` |
| LightGBM | `n_jobs=1` |
| CatBoost | `thread_count=1` |
| Random Forest | `n_jobs=1` |
| Experiment orchestration | `worker_count=1`; execute fits sequentially |

These are runtime controls, not tuning dimensions. No new Ridge hyperparameter
or solver choice is introduced. The current parameter declarations omit these
thread settings; the later accepted runner must add the exact controls above,
preserve the existing settings and verify effective single-thread execution.
This document records the policy without modifying source code or claiming that
thread enforcement is already implemented. Do not rely on automatic library
thread counts or infer execution authority from this approval.

Before an authorised run, record the frozen thread mappings/counts, worker count,
seed mappings and shared execution environment/hardware. Verify the complete
effective recipe against the pinned libraries, then capture requested/effective
parameters, defaults, devices and determinism controls in run metadata. DR-013
specifically requires rechecking the earlier LightGBM API evidence (4.6.0) against
the pinned 4.7.0 version before execution. Capturing defaults and verifying runtime
behaviour remain preflight requirements; they do not reopen the approved numeric
thread policy. Fixed seeds do not guarantee cross-library bitwise equality.

## 8. Metric formulas and aggregation

For one model × horizon × configuration × fold, n is the number of accepted
pair-level validation predictions, y_i the observed direct target, and p_i the
raw prediction. Compute:

$$
\mathrm{WAPE}=\frac{\sum_{i=1}^{n}|p_i-y_i|}{\sum_{i=1}^{n}|y_i|},
\qquad
\mathrm{MAE}=\frac{1}{n}\sum_{i=1}^{n}|p_i-y_i|,
$$

$$
\mathrm{RMSE}=\sqrt{\frac{1}{n}\sum_{i=1}^{n}(p_i-y_i)^2},
\qquad
\mathrm{Bias}=\frac{1}{n}\sum_{i=1}^{n}(p_i-y_i).
$$

WAPE is primary, stored as a ratio; a labelled percentage display is 100 × WAPE.
MAE/RMSE/Bias support selection. Positive Bias is overforecasting; negative Bias
is underforecasting. Do not clip/round predictions or add an epsilon denominator.
No prediction-processing rule is approved by this protocol.

Zero WAPE denominator produces unavailable WAPE with explicit status
`undefined_zero_actual_total`, not zero, infinity or silent division. Empty
populations, nonfinite predictions and failed fits are diagnostic failures;
retain their status, never turn them into valid scores. Undefined WAPE prevents
automatic configuration ranking.

For each model/horizon/configuration, calculate the arithmetic mean of EACH
metric across exactly four folds: (m_1+m_2+m_3+m_4)/4. Do not use sample-size
weights, pooled predictions as a replacement statistic, or a mean over available
folds. If any required fold/metric is unavailable, mark its four-fold summary
unavailable with a reason. No weighted averaging or cross-horizon composite
score/leaderboard is approved. Full precision governs comparison; rounding is
for display only.

## 9. Primary selection and descriptive RQ2 interpretation

For EACH primary model and horizon, compare arithmetic mean WAPE across exactly
four folds for all 24 configurations. Retain every fold's WAPE/MAE/RMSE/Bias and
all supporting means. The lowest mean-WAPE configuration is the validation
leader, subject to human fold-stability and supporting-metric review under
DR-006. It is not automatically frozen or independent final-performance evidence.
Supporting review cannot expand the grid or consult final outcomes.

**Human-approved deterministic exact-tie handling:** Within one primary model
and horizon, preserve ALL canonical configuration IDs tied for the lowest
four-fold arithmetic mean WAPE at full precision. Use the lowest canonical
`GBM` ID only as a deterministic administrative representative; retain the full
tied set in `tied_configuration_ids` and identify the representative explicitly.
**Canonical order does not imply scientific superiority.** The representative
remains subject to the same human review/freeze as any other validation leader;
its administrative designation does not make the other tied configurations worse.

Exact ties between primary model leaders remain reported as ties for that
horizon, with all tied model names retained. Do not break model ties by model
order or force a single overall winner. Preserve horizon-specific interpretation
and supporting-metric/fold review. No near-tie tolerance is approved; do not
silently use MAE, complexity or runtime to break an exact WAPE tie.

Ridge and Random Forest have one fixed configuration, so there is no supportive
configuration search/selection. Their evidence is contextual and cannot determine
RQ2. Simple baselines also remain untuned. A downstream deployment-selection
policy is not approved by the primary comparison.

The RQ2 and subordinate hypotheses remain exactly those in DR-013. For each
horizon independently, compare the three primary implementations descriptively
and comparatively using their human-reviewed validation configurations:

- Use arithmetic mean WAPE over the four folds as the primary comparison metric;
  retain and inspect ALL four fold-level WAPE results.
- Use MAE, RMSE and Bias as supporting metrics; report magnitude and direction
  of differences. Clearly defined relative differences may also be reported.
- Examine reasonable fold consistency. A small aggregate difference driven
  primarily by one fold is not strong evidence of a general performance difference.
- Treat the temporal folds as dependent, not independent experimental replicates.
  No statistical-significance procedure or universal numerical threshold for
  a meaningful difference is approved. Do not mechanically accept/reject
  H0_RQ2 using an arbitrary threshold.
- Report model ordering by horizon, including any changes in ordering. Do not
  average/rank across horizons into a composite score or collapse them into an
  overall winner.

Record each primary model/horizon's frozen configuration and review rationale,
exact ties and any descriptive near-equivalence discussion. No observed result
silently authorises a new setting, metric, threshold or experiment.

## 10. Approved contextual simple baselines

Naive and weekly Seasonal Naive are fixed, untuned, contextual baselines.
DR-007's 1/7/14-day formulas remain unchanged. The project owner explicitly
approves both 28-day extensions in this protocol. For origin o, y_o is the latest
observed daily demand, and S_o is the latest complete seven-day sum within the
same SKU–warehouse pair, ending at o:

$$
S_o=\sum_{j=0}^{6}y_{o-j}.
$$

| Horizon | Approved Naive | Approved Seasonal Naive |
|---|---|---|
| 1 | y_o | y_(o-6), matching the first target day's weekday |
| 7 | 7y_o | S_o |
| 14 | 14y_o | 2S_o |
| 28 | 28 * y_o | 4 * S_o |

The 28-day Naive holds the last observed daily level constant for 28 days.
The 28-day Seasonal Naive repeats the latest complete observed seven-day pattern
four times. Neither uses future observations or a partially observed week.
Baselines use origin-available history, the same eligible validation population,
all four folds and the same metrics; they have no learned preprocessing, tuning
or configuration-selection search.

Both baselines are approved for all horizons 1/7/14/28 and remain contextual
only: they do not enter the matched primary grid or determine RQ2. Their previous
28-day approval-pending/excluded status is resolved by the project owner's
explicit decision recorded here. Formula approval does not authorise execution;
Gate 4 still requires a specific run and scope manifest, and no baseline may be
silently omitted or executed outside that scope. Improvement over a baseline
may be claimed only using actually executed, authorised comparable evidence.

Two baselines × four approved horizons × four folds means **32 planned baseline
evaluations**, separate from the 1,152 primary fits and 32 supportive fits.
No prediction or score is fabricated for any unexecuted or failed baseline.

## 11. Candidate comparison and evidence stages

Produce separate primary-comparison, supportive-context and simple-baseline
sections/tables for EACH horizon. Do not mix their rows into a primary ranking.
Required comparison columns are `model`, `evidence_role`, `configuration_id`,
`canonical_config_id`, `selection_status`, `fold_count`, `n_predictions`,
`mean_wape`, `mean_mae`, `mean_rmse`, `mean_bias`, `metric_status`,
`review_status` and `artifact_paths`.

`evidence_role` is exactly `primary`, `supportive` or `simple_baseline`, separate
from `evaluation_stage` (`validation` or `final_evaluation`). Primary summaries
identify the reviewed canonical configuration and retain the full 24-configuration
evidence behind it. Primary selection statuses are `candidate`,
`validation_leader`, `tied_administrative_representative`, `tied_configuration`
and `human_frozen`. Within-model configuration ties retain all tied IDs; only
the lowest ID is marked as the administrative representative. Human-frozen
records retain their tie provenance. Exact primary-model ties retain all tied
models in the horizon comparison and are labelled as ties, with no forced model
winner. Supportive records use `fixed_supportive`; untuned baselines use
`not_applicable`. Neither role participates in primary RQ2 selection.

Final evidence has its own stage/run reference and never enters validation
ranking. Do not label validation leaders final model performance, claim
improvement over unexecuted baselines or invent an overall winner. Record human
review/freeze references separately. Paired series, overlapping labels, dependent
folds and a simulated year limit interpretation; no significance test, uncertainty,
demand-regime or downstream inventory method is introduced here.

## 12. Final-evaluation protection and refit policy

Validation-stage input is restricted to 2024-01-01 through 2024-12-02 before
feature construction, demand validation, eligibility analysis or input-view
fingerprinting. Fold operations additionally restrict to their own intervals.
Final-period demand must not enter validation fitting, preprocessing, debugging
based on forecast performance, feature/model/configuration selection, search-space
changes or protocol revision in response to scores. Do not profile or
fingerprint final outcomes as part of validation metadata. Reading dates to isolate
permitted rows is not authorisation to evaluate outcomes outside that scope.

Before final evaluation, freeze human-reviewed validation configurations and
model choices by horizon, any approved baseline policy, this protocol and the
accepted implementation. Gate 6 requires a separately authorised final run
manifest naming the models/horizons, selected configurations and approved
fitting policy. Synthetic/static implementation diagnostics may precede that
gate; actual final-window performance cannot be used to debug or redesign it.

**Final estimator refit and preprocessing policy are explicitly deferred to
Gate 6. This does not block validation-protocol approval/freeze at Gate 1 or
separately authorised validation.** The
current decisions define folds, complete-label eligibility and the December 2
final origin, but do not approve a final fitting population or reuse/refit rule.
The merged configuration/preprocessing modules and their tests do not supply
that approval. No historical Issue #52 policy, fold-4 fitted estimator or implicit
all-history refit may be assumed authoritative.

Before Gate 6, human approval must explicitly specify the final training dates
and eligible labelled population separately by horizon; whether the frozen
configuration is newly fitted or an identified accepted estimator is reused;
and whether category vocabularies/Ridge scaling state are newly fitted or which
identified fitted states are reused. The chosen policy must comply with Section 4,
use no outcome after December 2, and preserve common primary representation,
unknown-ID rejection and exact requested iterations without a new search.
Do not choose a final refit/preprocessing policy without separate Gate 6 approval.

Only after that decision and separate final-run authorisation may the runner
construct the common December 2-origin vector (first target day December 3),
apply the approved fitted preprocessing and predict the authorised frozen
candidates. Direct targets end December 3/9/16/30 for horizons 1/7/14/28.
Final estimator and preprocessing fitting remain blocked until this policy is
approved, even if validation has already completed.

All final reporting must repeat the earlier Dec 3–16 validation exposure and
full-year EDA exposure. Reserved from subsequent selection is not historically
fully unseen. Final evidence must not feed back into accepted decisions.

## 13. Machine-readable reproducibility metadata

`run_metadata.json` uses the Gate 1-approved schema version `issue-65-v2`.
Preserve a manifest before computation and record completion/failure without
overwriting another run. The following keys/groups are required:

| Group | Required machine-readable keys |
|---|---|
| Run identity | `run_id`, `created_at_utc`, `evaluation_stage`, `run_status`, `schema_version`, `protocol_version`, `protocol_path`, `protocol_hash` |
| Source/environment | `git_commit_sha`, `git_branch`, `git_dirty`, `source_hashes`, `python_version`, `library_versions`, `library_builds`, `requirements_hash`, `operating_system`, `hardware`, `execution_environment` |
| Human authority | `approval_references` for protocol/full implementation/specific run/tie/numeric runtime/final refit; `run_scope` with ordered primary/supportive models, horizons and explicit baseline exclusions/approvals |
| Canonical grid | Ordered `canonical_grid` entries with `canonical_config_id` and `canonical_parameters`; exactly the shared 24 declarations, separate from API settings |
| Candidate records | `model`, `evidence_role`, `horizon`, `configuration_id`, `canonical_config_id`, `canonical_parameters`, `requested_api_parameters`, `effective_api_parameters`, `random_seeds`, `device`, `thread_count`, `worker_count`, `requested_iterations`, `effective_iterations` |
| Temporal candidate evidence | `fold_id` (null for final), `training_start`, `training_end`, `forecast_origin`, `target_start_date`, `target_end_date`, `outcome_window_start`, `outcome_window_end` |
| Feature contract | `feature_contract_path`, `feature_contract_hash`, `decision_record_references`, ordered conceptual/numerical/categorical feature names |
| Representation records | `representation_id`, model/role/horizon/fold-or-stage keys, `physical_feature_names`, `physical_feature_count`, `category_vocabularies`, `category_mappings`, `training_row_count`, `training_population_hash`, `numerical_means`, `numerical_scales` (Ridge only) |
| Eligibility records | Candidate/fold/pair keys, `raw_row_count`, `feature_eligible_count`, `label_eligible_count`, `training_row_count`, `expected_origin_count`, `scored_origin_count`, `exclusion_counts`, `overlapping_reasons`, `pair_key_hash`, `input_view_hash` |
| Metrics/selection | Candidate/fold keys, all four metric values/means, `metric_status`, `failure_reason`, `selected_configuration`, `selection_status`, `review_status`, `human_review_reference`, `selection_rationale`, `tied_configuration_ids`, `administrative_representative_id`, `tied_primary_models` |
| Artifact manifest | `artifact_path`, `artifact_hash`, `artifact_status`, `diagnostic_paths` |

Repeated records use ordered arrays `candidate_records`, `representation_records`,
`eligibility_records`, `metric_records`, `selection_records` and `artifact_manifest`.
Stage/role/model/horizon/configuration/fold identify a candidate; representation
IDs additionally bind the exact training population. Preserve the shared primary
vocabulary/order linkage and supportive Ridge means/scales. Primary records must
carry identical canonical values for the same ID but their own requested/effective
API settings. Supportive/baseline canonical fields are null, not invented GBM IDs.

Use ISO dates, UTC timestamps, JSON booleans and JSON null with explicit status/
reason for unavailable numbers. No JSON NaN/infinity is permitted. Preserve
feature arrays, lexical fitted categories and Section 7 record order. Store full
pinned-library defaults and requested/effective runtime mappings; successful
import verification is not a substitute. Unknown approvals stay pending/null.
Input fingerprints cover only the authorised stage's rows, not the complete raw
file or future-period outcomes. No raw dataset or credentials belong in metadata.

## 14. Prediction-level records

`predictions.csv` retains pair-level validation predictions for every successfully
authorised primary configuration, fixed supportive benchmark and approved simple
baseline. Final rows cover only separately authorised frozen candidates. Required
columns, in order:

```text
run_id, evaluation_stage, evidence_role, fold_id, model, horizon,
configuration_id, canonical_config_id, SKU_ID, Warehouse_ID,
training_start, training_end, forecast_origin, target_start_date, target_end_date,
prediction, observed_target, prediction_status, target_status, eligibility_status,
selected_configuration, selection_status, representation_id
```

Role/stage and ID conventions are in Sections 7 and 11. `fold_id` is 1–4 for
validation and empty for final. `canonical_config_id` is populated only for
primary models; supportive/baseline values are empty. The composite key is
run/stage/role/model/horizon/configuration/fold/SKU/warehouse. Each accepted key
has exactly one fixed-origin record; primary IDs cannot collide across models.

Predictions remain raw. `observed_target` appears only in separately authorised
retrospective evaluation, never in predictors/prospective exports. Status fields
explain unavailability; they do not manufacture outcomes or scores. Optional
signed/absolute errors are retrospective only. Supportive/simple-baseline rows
have an empty `selected_configuration` field and never enter the RQ2 ranking.
Baselines have no learned `representation_id`; their formula/history reference
is held in the manifest. Approved 28-day baselines follow the same authorised
prediction-record rules as the 1/7/14-day baselines; unexecuted baselines have no
fabricated prediction rows.

CSV unavailable numbers and null identifiers are empty with explicit status/
reason in metadata; an observed zero remains zero. Sort by stage order
`validation`, `final_evaluation`, then role/model/horizon/configuration/fold order
from Section 7 and lexical SKU/warehouse. A final null fold follows validation
folds. Prospective exports exclude observed targets and retrospective errors;
no full source row or future operational predictor is included.

## 15. Stable output artifacts

Use a new local ignored `artifacts/forecasting/<run_id>/` evidence directory
under the approved [storage policy](artifact-storage-policy.md). Retained reusable
model/preprocessor bundles belong in `models/forecasting/<run_id>/`; reviewed
findings belong in `reports/forecasting/<run_id>.md` under the
[reporting contract](../reports/README.md). Completed evidence is immutable and
must reference its model/state dependencies across these locations. Never
overwrite another run or relabel historical evidence.

These are the active architecture requirements for the next accepted implementation,
not the unchanged runner's executable layout. Scientific table schemas below remain
unchanged. No full raw/processed dataset or training matrix is copied into the run
bundle. Separately approved validated/engineered handoffs follow the lifecycle and
storage authorities; this amendment does not authorize new exports or protected
outcome access. See the Issue #94 implementation boundary below.

| Artifact | Required purpose |
|---|---|
| `run_metadata.json` | Section 13 manifest, canonical grid, API settings, fitted-state/eligibility records and approval references |
| `fold_metrics.csv` | Four-fold primary/supportive/baseline metrics with separate role and stage; column order below |
| `configuration_summary.csv` | Arithmetic four-fold means for every primary canonical configuration and each fixed supportive/approved baseline entry |
| `selected_configurations.json` | Primary selections/ties and human freeze references, fixed supportive declarations, and explicit baseline policies/exclusions |
| `predictions.csv` | Section 14 keyed pair-level audit records |
| `eligibility_counts.csv` | Per-pair history/label/intersection and exclusion diagnostics |
| `comparison.md` | Generated evidence summary/draft: separate horizon/role tables, magnitude/direction/fold-consistency discussion, approval gaps and final-exposure disclosure; not a reviewed report |

`fold_metrics.csv` required column order:

```text
run_id, evaluation_stage, evidence_role, model, horizon,
configuration_id, canonical_config_id, fold_id, training_start, training_end,
forecast_origin, target_start_date, target_end_date, n_predictions,
wape, mae, rmse, bias, wape_denominator, metric_status, failure_reason
```

`configuration_summary.csv` required column order:

```text
run_id, evaluation_stage, evidence_role, model, horizon,
configuration_id, canonical_config_id, expected_fold_count, valid_fold_count,
n_predictions, mean_wape, mean_mae, mean_rmse, mean_bias, metric_status,
failure_reason, selected_configuration, selection_status, review_status
```

`n_predictions` counts predictions across validation folds and never supplies
weights for arithmetic metric means. Only primary summaries participate in RQ2
configuration/model comparison. Canonical/API parameter values resolve separately
against the manifest, not against supportive historical grids.

`eligibility_counts.csv` required column order:

```text
run_id, evaluation_stage, evidence_role, model, horizon, fold_id,
SKU_ID, Warehouse_ID, raw_row_count, feature_eligible_count, label_eligible_count,
training_row_count, expected_origin_count, scored_origin_count,
exclusion_reason, reason_count, overlapping_reasons
```

For multiple reasons, repeat the keyed population counts with one reason per
row, disclose overlaps, and do not sum repeated population counts or assume
reason counts are disjoint. JSON metadata retains unique intersected counts.
CSV flags are `true`/`false`; unavailable numbers/null IDs are empty; counts,
horizons and folds are integers; finite predictions/metrics are numbers.
`overlapping_reasons` is a JSON array cell. Dates follow Section 13.

`selected_configurations.json` contains `run_id`, `schema_version`, ordered
`selections`, `supportive_configurations` and `baseline_policies`. Each PRIMARY
selection contains `model`, `evidence_role`, `horizon`, `configuration_id`,
`canonical_config_id`, `canonical_parameters`, `requested_api_parameters`,
`effective_api_parameters`, `selection_status`, `tied_configuration_ids`,
`administrative_representative_id`, `metric_references`, `human_review_reference`,
`selection_rationale` and `freeze_reference`. For an exact configuration tie,
retain every tied ID and set the administrative representative to the lowest
canonical ID; `configuration_id`/`canonical_config_id` identify that representative
without a superiority claim. For untied selections, the representative field is
null. Preserve horizon-level `tied_primary_models` in comparison/selection records
when model leaders tie; no model representative or overall winner is forced.
Unreviewed freeze references remain null. Supportive declarations
identify their fixed settings with `fixed_supportive`, never a tuning winner.
Baseline policies record exact formula references, horizons, exclusions and
approval status/references; both 28-day formulas are approved as in Section 10.

Required CSV fields are ordered as listed; optional schema changes require a
recorded version amendment before execution. Final metrics have null fold IDs
and never enter four-fold validation summaries. Baselines outside an authorised
run scope are explicitly identified as not executed, never as formula-approval
pending. No prediction/score is fabricated. Failures retain diagnostics, not
replacement results. Machine evidence remains local and separate from reusable
models and reviewed interpretation. A completed experiment must hand off a report
under the reporting contract; its review status, evidence links and outstanding
decisions remain explicit. Generated comparison text alone does not meet human
review requirements or authorize publication. Record the reviewed handoff in the
[progress log](research-progress.md), linking actual review evidence.

## 16. Experiment-stage gates

| Gate | Required explicit human control | Authority granted |
|---|---|---|
| 1 | **Complete:** project owner reviewed and explicitly approved/froze the full validation protocol on 2026-09-29; approval reference is recorded above | Validation-protocol freeze only; experiment execution NOT AUTHORISED; final refit deferred to Gate 6 |
| 2 | Separately authorize applicable estimator/metrics/baseline/runner implementation or architecture revision against this protocol | Implementation work; no fitting/tuning/scoring |
| 3 | Review relevant test evidence and accept the complete runner/pipeline | Full implementation acceptance; no experiment execution |
| 4 | Specifically authorise the validation run and primary/supportive/baseline scope manifest; verify the frozen single-thread policy and complete runtime recipe | Only that validation run; no final evaluation |
| 5 | Review validation evidence and freeze primary configurations/model choices by horizon and baseline policy | Selection freeze; no final evaluation |
| 6 | Approve final estimator/preprocessing refit policy and specifically authorise final evaluation | Only the named final run/frozen scope |

Issue #68 alignment and the subsequent runner are implemented; PR #90 merged
Issue #89 orchestration. The owner confirms a validation run occurred. Its retained
authorization record and unavailable machine bundle are distinguished in the
[methodology revision](forecasting-methodology-revision.md). No Gate 5 selection
freeze or Gate 6 approval is inferred from execution, generated selections or merge.

The gates above remain controls for each applicable revision/run. The completed
Gate 1 freeze does not authorize future execution. Storage/retention migration
requires implementation acceptance and a new source/protocol-bound specific
record; past authorization does not transfer. Final refit/preprocessing remains
deferred to Gate 6. See runner operations for the legacy runtime boundary.

## 17. Issue #52 relationship and historical provenance

[The original Issue #52 protocol](issue-52-forecasting-protocol.md), its outputs
and earlier runtime/tie rules remain unchanged historical provenance only. Its
thirteen numerical columns, 1/7/14-day scope, fourteen-day windows, old dates,
approval and results do not control or constitute evidence for the future matched
experiment. Neither archived first-grid tie handling nor single-thread/SVD Ridge
choices transfer into this protocol. Current supportive Ridge uses the approved
`solver="auto"` configuration in DR-013.

Future experiment work is controlled by this human-approved/frozen protocol,
DR-013, the explicit human decisions recorded here and separate implementation/run
gates, regardless of which GitHub issue
tracks that work. The historical reproduction command references absent source;
compiled caches are not a runnable source archive. Do not recreate its results
or relabel them as the revised study.

The [methodology revision record](forecasting-methodology-revision.md) preserves
that history and prior final-period exposure. Historical output references remain
provenance; local availability must be verified rather than inferred. No old score selects the current features, grid or protocol.
Issue #94 reconciles active documentation, not GitHub issue text or original
historical records, and authorizes no experiment.

## 18. Human decision record and validation-protocol finalisation

The project owner explicitly approved the following decisions on 2026-09-29 in
the earlier Issue #65 decision instruction. This record resolves the corresponding
pending items in the reviewed repository; older pending wording in DR-007/DR-013 does not
override these newer explicit human decisions. Those files remain unchanged.

| Decision | Approved policy | Protocol section / status |
|---|---|---|
| Exact configuration ties within a primary model/horizon | Preserve all tied canonical IDs; use the lowest GBM ID solely as the deterministic administrative representative. Canonical order implies no scientific superiority. | Section 9; resolved |
| Exact ties between primary model leaders | Report all tied models as ties by horizon; no forced single overall winner. | Sections 9, 11 and 15; resolved |
| Single-thread execution | XGBoost `n_jobs=1`; LightGBM `n_jobs=1`; CatBoost `thread_count=1`; Random Forest `n_jobs=1`; experiment `worker_count=1`. Preserve CPU, seeds and all existing runtime controls. | Section 7; resolved |
| 28-day simple baselines | Naive = `28 * y_o`; Seasonal Naive = `4 * S_o`, using the latest complete seven-day sum. Untuned and contextual only. | Section 10; resolved |
| Final estimator refit/preprocessing timing | Explicitly defer the final fitting population and estimator/category/scaler reuse-versus-refit decision to Gate 6. It does not block validation-protocol freeze. | Section 12; deferral approved, final policy undecided |

**Gate 1 validation-protocol review, approval and freeze are complete.** The
project owner's explicit full-protocol approval is recorded at the start of this
document. The sole deferred policy is final estimator refit/preprocessing:
human approval must specify final training dates/eligible populations by horizon
and estimator/category/scaler reuse versus refit, using no outcome after
December 2. This blocks only Gate 6 final fitting/evaluation.

The approved primary/supportive roles, canonical grid, 1,152 planned primary
fits, common primary representation, versions, existing model controls and new
single-thread settings remain fixed. Capturing inherited defaults, enforcing the
thread controls in each accepted runner revision and verifying the complete pinned-version
recipe are implementation/preflight requirements, not unresolved Gate 1 research
choices or permission to execute experiments.

The substantive Issue #65 protocol requirements are now documented: exact
training-row eligibility, fixed origins, current preprocessing, matched search,
metric formulas/aggregation, horizon-specific selection and approved exact-tie
handling, all baseline formulas, reproducibility and artifact schemas, final
protection, execution gates and historical provenance. **The validation protocol
is human-approved/frozen at Gate 1.** The project owner's explicit review and
approval satisfy Issue #65's human-reviewed/frozen protocol acceptance criterion.
Recording this approval changes no substantive research decision and does not
approve downstream implementation, model selection or experiment execution.

Final refit/preprocessing remains explicitly deferred to Gate 6 and does not
affect the completed Gate 1 freeze. Experiment execution remains
**NOT AUTHORISED** despite protocol approval; validation and final evaluation
retain their separate specific-run gates.

The runner implementation was merged through PR #90; future architecture changes
still require test acceptance and new specific-run authorization. Selection freeze
and final-run authorization remain separate gates. Downstream inventory-risk, replenishment, uncertainty and human-
review methodology stay outside this forecasting-protocol task. No tests, model
fits, scores or experiments are executed by this document update.

## Issue #89 operational/artifact amendment — historical accepted runtime contract

This amendment records the all-fit/single-bundle contract implemented in PR #90.
Its original operational requirements below are preserved as provenance and
unchanged runtime behavior. Issue #94 supersedes its storage direction for future
implementation; it does not authorize pruning historical bundles or executing the
legacy layout.

This amendment implements the project owner's Issue #89 operational instructions. It changes no grain, features, labels, horizons, folds, grid, model settings, baseline/metric formulas, tie semantics or final-stage research policy. Scientific schema remains issue-65-v2 and protocol version remains issue-65-matched-frozen-1; the full protocol byte hash binds this amendment.

Normal execution is `python -m src.forecasting.experiment` from the repository root. Fixed pathlib locations resolve dataset and reviewed execution record; the exact approved run ID is resolved, not generated. No approvals or hashes are manufactured/refreshed. Existing directories are consumed and cannot be overwritten/resumed. See [runner operations](forecasting-runner.md).

Completion requires readback schema/count/key/provenance checks, reconciliation using existing scientific functions, hashes and saved-model replay. All successful learned validation fits are retained in native XGBoost/LightGBM/CatBoost formats or trusted version-bound joblib, with fitted preprocessing and derived origin predictors. They are validation candidates, not final/deployment models. Baselines retain formula provenance. No raw/full dataset or training matrix is copied. This explicitly extends the earlier seven-artifact/no-model-binary operational policy; scientific columns and selection meaning remain unchanged. Storage capacity must be reviewed before execution.

Authorization/model/state files and finalized logs are hashed by run_manifest.json (version 1). Lifecycle is preflight, running, finalizing, verified_completed; failures are failed/interrupted. The manifest is published LAST after verification, log closure and final metadata. Metadata alone is not completion evidence. Failed, partial, missing or corrupt bundles are rejected by completed-evidence consumers. Recovery preserves the original exception.

Source/tests, direct joblib/threadpoolctl pins and this amendment change approval-bound hashes. Earlier authorization cannot authorize changed code without renewed human review and a matching reviewed record. Writing this amendment neither executes nor approves an experiment. Gate 6 remains blocked.

## Issue #94 operational alignment — implementation boundary

This operational amendment connects merged Issues #92/#93 without changing
Sections 2–12 scientific definitions, horizons, folds, metrics, model roles,
selection/tie rules or final-evaluation protection. The scientific protocol version
remains `issue-65-matched-frozen-1`; that identifier alone is insufficient to
identify this operational revision. Record Issue #94 review/acceptance, the full
protocol byte hash and applicable storage/retention/schema versions. No approval
reference or new operational schema number is invented here. Existing authorization
hashes are historical and must not be refreshed automatically.

- **Lifecycle/storage:** Follow [shared data foundation](workflows/shared-data-foundation.md)
  for chronological scope before fold/origin-specific features, separate targets,
  training-only preprocessing and model-ready matrices. Section 15 and the
  [storage policy](artifact-storage-policy.md) own distinct evidence/model/report
  locations. No random split, global preprocessing fit or silent repair is permitted.
- **Candidate retention:** Retain complete configuration, metric, prediction,
  eligibility, provenance and selection/tie evidence for every evaluated candidate.
  Reusable selected bundles include the exact fitted preprocessing and replay inputs;
  retained validation fits are not final/deployment models. Unselected binaries may
  be temporary only after an exact human-approved retention set identifies selected
  fold models, ties, supportive models and audit exceptions. The set and version
  are still unresolved: all-fit persistence/replay remains the compatibility
  requirement until that approval and accepted implementation. No current binary
  pruning is authorized. Historical completed bundles remain immutable.
- **Metadata/integrity:** Extend Section 13 operational records, through a reviewed
  schema amendment, with candidate retention status/reason, policy version,
  selection basis and model/state paths/hashes. A cross-location completion manifest
  must cover all retained evidence and model/preprocessor dependencies with confined,
  unambiguous references. Distinguish fit/evaluation counts from retained-model and
  replay counts. Verify all candidate tables/metrics/configurations/predictions;
  replay every retained model with exact saved state and origin inputs without
  refitting. Missing retained dependencies or discarded scientific evidence fail
  completion. Explicitly record not-retained candidates; absence must not masquerade
  as failed fitting. Until accepted migration, verification still expects every
  successful learned fit as in the legacy implementation.
- **Completion/failure:** Retain authorization, finalized logs and manifest-last
  verification. Temporary candidates must be accounted for before final completion
  under the approved retention set. Never rewrite a completed manifest to conceal
  pruning; archival derivatives identify parent evidence and omissions. Failed or
  interrupted evidence is diagnostic only, never a valid selection/comparison.
- **Reporting/review:** A generated comparison is machine evidence. Human-readable
  findings follow [reports/README.md](../reports/README.md), linking exact completed
  evidence, dataset/view/code/protocol/environment identities, fold/aggregate
  comparisons, selection status, limitations and prior-exposure disclosure. Human
  review, configuration freeze and final authorization remain separate. Record
  material milestones in [research-progress.md](research-progress.md) without
  duplicating meeting minutes or Decision Records.

The runner still writes the removed legacy location and retains/replays all fits.
Do not execute it to recreate that architecture. A separate implementation task
must update paths, metadata/model persistence, cross-location integrity and tests,
resolve the exact retention set/schema and persisted-handoff permissions, obtain
human acceptance and issue new matching specific authorization. Documentation
acceptance alone does not complete that work, approve experiments or unblock Gate 6.
