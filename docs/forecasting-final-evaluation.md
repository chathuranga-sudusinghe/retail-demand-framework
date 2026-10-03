# Forecasting Final Evaluation — Issue #130

**Status:** Documentation for owner review; final runtime implementation is
pending. No real final evaluation or reserved-outcome access is authorized.

[DR-014](decisions/DR-014-forecasting-selection-and-final-refit.md) records the
owner-supplied human freeze, exact candidate scope, separate producer mapping and
refit-policy approval. The [frozen protocol](protocol.md) and
[feature contract](forecasting-feature-engineering.md) retain their scientific
definitions. This guide specifies the intended implementation; it does not
claim that the new path already exists or is accepted.

## Separate runtime boundary

Keep the accepted validation entrypoint and `run_validation` behavior intact,
including its validated-Parquet input, four-fold evaluation, saved-model replay,
schemas, source fingerprints and completion checks. Do not route validation
through model-ready exports or modify the completed `validation-20261002-01`
artifact/model/draft bundle, authorization snapshot or manifest.

The approved final architecture has three separate responsibilities:

| Planned module | Responsibility |
|---|---|
| `src/forecasting/final_authorization.py` | Validate human references and exact scope against frozen evidence and the reviewed policy before execution. |
| `src/forecasting/final_evaluation.py` | Load historical training only, prepare/refit, produce all approved predictions, then reveal outcomes and score. |
| `src/forecasting/final_artifacts.py` | Own final persistence, prediction sealing, model/state replay, evidence reconciliation and completion verification. |

Reuse existing feature, target, preprocessing, canonical configuration,
estimator, baseline and metric functions. Validation-specific fold preparation,
selection, descriptors and integrity checks must not be made to accept final
evidence by relabelling it as validation or a fictitious fold.

## Human review and final-run authorization

The owner has supplied the human freeze and refit policy in DR-014.
The written documents still require owner review. Runtime implementation and
synthetic test results then require human acceptance. Only a separate explicit
authorization for an exact real final run permits fitting and reserved-outcome
access. No such run authorization is supplied by this documentation.

The future local final authorization must bind:

- an exact new run ID and `evaluation_stage=final_evaluation`;
- validation run `validation-20261002-01`, its canonical artifact anchor and
  the exact completion-manifest SHA-256 recorded in DR-014;
- hashes of the reviewed DR-014 freeze/refit record and this operational guide,
  plus explicit human freeze, refit-policy, implementation-acceptance and
  specific final-run references;
- the unchanged scientific protocol/feature identities, final implementation
  source identities, pinned environment and historical training-view identity;
- exactly the twelve frozen primary combinations, eight fixed supportive
  combinations and eight untuned baseline combinations in DR-014;
- training dates January 1–December 2, origin December 2, reserved evaluation
  dates December 3–30, and the approved single-worker/thread controls.

Check the retained validation bundle with its existing completed verifier.
Check historical provenance against the retained bundle rather than refreshing
its hashes to match new source. Missing/malformed/stale records, wrong scope,
changed freeze/policy/evidence hashes or unverifiable validation evidence block
execution. Existing run storage is not reused or overwritten. Never generate
approval references, discover a "latest" run or refresh authorization hashes
automatically.

## Historical preparation and fresh refit

Before outcome reveal, load only the approved native key/demand projection
for **2024-01-01 through 2024-12-02**, applying date bounds before demand
inspection. Parent file-byte integrity checks do not authorize decoding,
profiling or fingerprinting reserved outcomes.

For each horizon, construct frozen historical predictors and separately
construct complete historical labels, intersect their eligibility, and verify
one-to-one native key alignment. The horizon label must finish by December 2.
Refit vocabularies, Ridge scaling and fresh estimators on that same eligible
population under DR-014. Save population identities and exclusion counts.
No Fold 4 model/preprocessor reuse, imputation, new feature, training-matrix
export dependency or hyperparameter search is introduced.

Preserve Python **3.12.3** and the exact dependency pins in
[requirements.txt](../requirements.txt), including XGBoost **3.4.1**,
LightGBM **4.7.0**, CatBoost **1.2.10** and scikit-learn **1.9.1**.
Use the existing estimator construction/fitting checks to preserve requested
iterations and record effective parameters, CPU/seed controls and single-thread
execution. A mismatch stops the run; it does not authorize a pin or recipe change.

Construct one predictor row per historical SKU–warehouse at first target day
December 3 using only December 2 history. The same origin vector serves every
horizon. Baseline evidence is November 26–December 2, with the unchanged formulas
in [baselines.py](../src/forecasting/baselines.py). Unknown origin categories or
incomplete predictor/baseline history stop execution before outcome access.

## Predict-before-reveal ordering

The final path must enforce this ordering for the entire approved scope:

1. Validate exact authorization, evidence anchors, environment and unused storage.
2. Load and validate historical training only; prepare eligible populations and
   fit preprocessing.
3. Freshly fit all twenty learned candidates and compute all twenty-eight
   candidates' origin predictions without reserved outcomes.
4. Persist every prediction with exact run/model/horizon/configuration/native
   keys, origin, target window, role and fitted-state provenance. These records
   contain no observed targets or scores.
5. Read back the complete saved prediction set, check scope, keys, finite values
   and counts, and persist SHA-256 hashes in a prediction receipt. Verify that
   receipt and saved bytes **before** opening reserved outcomes. This receipt
   establishes prediction sealing, not successful final completion.
6. Only then load outcomes for December 3–30 through a separately controlled
   outcome-read step. Require the same historical pair roster and complete
   target coverage. Align actuals to the sealed predictions by native keys.
7. Score the immutable predictions using unchanged WAPE, MAE, RMSE and Bias.
   Persist actuals/metrics separately from the sealed prediction evidence;
   do not revise predictions, refit, reselect or update the origin.
8. Reconcile final evidence, verify hashes and replay saved learned models with
   their exact preprocessing/origin inputs without refitting. Verify unchanged
   prediction receipts and authorization bindings, close logs and publish the
   final completion manifest last.

Direct target windows end December 3, 9, 16 and 30 for 1/7/14/28 days.
Final records have no validation fold; preserve separate evidence roles.
Do not run validation selection rules on final scores or compute a cross-horizon
winner. Report all approved candidates and preserve the distinction between
research comparison and downstream producer choice.

## Storage, failure and handoff

Follow existing ownership: machine evidence under
`artifacts/forecasting/<final_run_id>/`, fresh models/fitted state under
`models/forecasting/<final_run_id>/`, and generated draft reporting under
`reports/forecasting/drafts/<final_run_id>/`. The artifact-side completion
manifest is the sole final completion authority. The separate final integrity
boundary must validate final-specific evidence without weakening the existing
validation schema or version-2 completion contract.

Retain all twenty final learned models, fitted preprocessing, replay inputs,
all twenty-eight candidates' predictions/metrics and baseline formula provenance.
Do not prune validation or final evidence, store the full dataset in run outputs,
or silently promote validation descriptors to final models.

A fit, prediction, persistence, outcome-read, scoring or integrity failure stops
execution. Preserve available diagnostics and partial evidence, with the original
failure intact. Publish no successful completion manifest; do not automatically
retry, resume, substitute candidates or use final scores for debugging/selection.
Any human response must preserve the exposure history and protected decisions;
this guide authorizes no repeat run.

A reviewed handoff identifies the exact final run, model/configuration/horizon,
origin, cumulative target meaning, eligible training population, preprocessing,
hashes and producer mapping. Completion does not itself approve API deployment,
inventory/replenishment use, uncertainty estimates or decision-support rules.

## Implementation checks and research limitations

Implementation tests use synthetic data only. Cover authorization protection,
horizon-specific eligibility, fresh estimator/preprocessor fits, Ridge scaling,
baseline/origin alignment, complete prediction sealing before the first outcome
read, tamper rejection and stop-and-record behavior. Add synthetic regression
coverage that an older completed validation bundle remains verifiable after
new source files, with its evidence unchanged. Passing synthetic tests is not
research performance evidence or final-run authorization.

The required implementation checks are Ruff, MyPy, pytest, dependency consistency
and `git diff --check`. This documentation step runs only lightweight document
checks; runtime/test implementation follows owner review of this diff.
Read-only verification of the actual completed validation bundle remains a
separate implementation check, without model refitting or validation rerun.

Every final report must disclose that the dataset is simulated, December 3–16
had earlier validation exposure, and full-year exploratory data analysis inspected
the final interval. The interval is protected from subsequent selection but is
not historically fully unseen. Seasonal Naive's validation advantage over learned
models at 14 and 28 days must remain visible regardless of final ordering.
