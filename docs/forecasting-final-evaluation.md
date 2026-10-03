# Forecasting Final Evaluation — Issues #130/#131

**Status — 2026-10-03 / Issue #131:** DR-014 scientific freeze/refit policy and
Phase 1 implementation are owner-approved. Historical-only preflight passed.
The real `final-20261003-01` execution accessed reserved outcomes and failed only
during final replay verification. PR #141 corrected the verified layout defect.
The owner explicitly authorized `final-20261003-02` as a defect-correction rerun
with unchanged scientific scope. Revised controls and the local authorization
are prepared for review; the corrected run has not been executed.

[DR-014](decisions/DR-014-forecasting-selection-and-final-refit.md) records the
owner-supplied human freeze, exact candidate scope, separate producer mapping and
refit-policy approval. The [frozen protocol](protocol.md) and
[feature contract](forecasting-feature-engineering.md) retain their scientific
definitions. This guide documents the merged runtime. [DR-014](decisions/DR-014-forecasting-selection-and-final-refit.md)
records both the original scientific approval and subsequent explicit
implementation-readiness acceptance.

## Separate runtime boundary

Keep the accepted validation entrypoint and `run_validation` behavior intact,
including its validated-Parquet input, four-fold evaluation, saved-model replay,
schemas, source fingerprints and completion checks. Do not route validation
through model-ready exports or modify the completed `validation-20261002-01`
artifact/model/draft bundle, authorization snapshot or manifest.

The approved final architecture has three separate responsibilities:

| Implemented module | Responsibility |
|---|---|
| `src/forecasting/final_authorization.py` | Validate human references and exact scope against frozen evidence and the reviewed policy before execution. |
| `src/forecasting/final_evaluation.py` | Load historical training only, prepare/refit, produce all approved predictions, then reveal outcomes and score. |
| `src/forecasting/final_artifacts.py` | Own final persistence, prediction sealing, model/state replay, evidence reconciliation and completion verification. |

Reuse existing feature, target, preprocessing, canonical configuration,
estimator, baseline and metric functions. Validation-specific fold preparation,
selection, descriptors and integrity checks must not be made to accept final
evidence by relabelling it as validation or a fictitious fold.

## Human review and final-run authorization

The owner approved the human freeze, refit policy and Documentation Step 1 under
Issue #130. PR #133 merged the Phase 1 runtime; the owner explicitly accepted that
implementation and its recorded test/integrity evidence under Issue #131 on
2026-10-03. That acceptance confirms implementation readiness only.

The Issue #131 historical-only preflight completed successfully on 2026-10-03
with outcome `READY FOR AUTHORIZATION PREPARATION`. Retained
`validation-20261002-01` verification passed; environment/dependencies matched;
proposed final-run storage was unused; historical eligibility, origin and baseline
checks passed. Only the approved native projection through December 2 was
decoded. The existing deterministic preparation helper calculated preprocessing
statistics in memory without estimator fitting or persistence. The frozen
28-candidate scope and DR-014 producer mapping remained unchanged. No
reserved-final outcomes were accessed.

Preflight itself supplies no execution permission. Subsequently the owner
explicitly authorized `final-20261003-01`; its real execution fitted the frozen
candidates, revealed outcomes and failed during saved-model replay verification.
Preserve its artifact/model/draft bundle exactly, including the original failed
status and diagnostics. PR #141 corrected the C/Fortran prediction-layout mismatch;
the read-only investigation found exact replay of all twenty saved learned models
when the original C-contiguous layout was reproduced.

The owner now explicitly authorizes `final-20261003-02` as a corrected rerun
following that verified implementation defect. Result-driven retries, search,
retuning, reselection, candidate substitution and methodology changes remain
prohibited. A defect-only corrected rerun requires the fix, unchanged scientific
scope, a new exact human-approved ID and unused storage. No automatic retry,
resume, overwrite or permission for further reruns is introduced.

The local final authorization must bind:

- an exact approved run ID and `evaluation_stage=final_evaluation`;
- validation run `validation-20261002-01`, its canonical artifact anchor and
  the exact completion-manifest SHA-256 recorded in DR-014;
- hashes of the reviewed DR-014 freeze/refit record and this operational guide,
  plus explicit human freeze, refit-policy, implementation-acceptance and
  specific final-run references;
- unchanged scientific protocol/feature/requirements identities, pinned
  environment and historical training-view identity;
- exactly the twelve frozen primary combinations, eight fixed supportive
  combinations and eight untuned baseline combinations in DR-014;
- training dates January 1–December 2, origin December 2, outcome dates
  December 3–30, and the approved single-worker/thread controls.

`source_hashes` in the authorization record is creation-time provenance only.
It is not compared with current source to permit or reject execution. The runner
records actual execution source hashes and Git state in runtime metadata, and
uses those actual source hashes in model provenance. Source/Git/implementation
hashes do not bind execution permission. Scientific-document/data/environment
bindings still do, and artifact hashes, provenance consistency and prediction
receipts still protect the retained evidence. Historical bundles are verified
against their recorded snapshots without rebinding them to current source.

Check the retained validation bundle with its existing completed verifier.
Check historical provenance against the retained bundle rather than refreshing
its hashes to match new source. Missing/malformed/stale records, wrong scope,
changed freeze/policy/evidence hashes or unverifiable validation evidence block
execution. Existing run storage is not reused or overwritten. Never generate
approval references, discover a "latest" run or refresh authorization hashes
automatically.

## Implemented entrypoint and completion verification

The argument-free final entrypoint reads the fixed local record
`data/processed/forecasting/final_authorization.json`. That record must bind the
exact reviewed run and the five explicit approval references: `protocol`,
`human_freeze`, `refit_policy`, `implementation_acceptance` and `specific_final_run`.
It is not generated by the runtime. After explicit authorization for the exact named run
and record validation, the repository-root execution command is:

```bash
.venv/bin/python -m src.forecasting.final_evaluation
```

This command performs the real fresh refits and protected outcome reveal; it is
not a preflight command and must not be executed under implementation acceptance.
The validation CLI's `--stage final_evaluation` remains blocked.

Completed final evidence is consumed through
`src.forecasting.final_artifacts.verify_final_completed`, passing the exact
`artifacts/forecasting/<final_run_id>/` anchor. This verifier checks retained
evidence and saved-model replay without refitting or reopening parent outcomes.
The existing validation verifier remains `src.forecasting.integrity.verify_completed`.
Final models live under `models/forecasting/<final_run_id>/final/<model>/h<horizon>/<configuration>/`.
Later reviewed interpretation belongs at `reports/forecasting/<final_run_id>.md`,
separate from the immutable generated draft.

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
A verified implementation/execution defect may support only a separately
explicitly approved corrected rerun after the fix, with a new unused ID and the
same scientific scope. Preserve and disclose the original failure and prior
outcome access. Performance-driven retries remain prohibited.

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

PR #133 records 75 focused synthetic tests and 1,061 full-suite tests passing,
along with Ruff, MyPy, dependency consistency and `git diff --check`. It also
records successful read-only verification of the completed validation bundle:
1,216 evaluations, 304,000 predictions, 304 configuration summaries and 1,184
saved-model replays. These are recorded Phase 1 checks, not checks rerun during
this documentation correction or final research results. Implementation acceptance
is established by the owner's subsequent Issue #131 instruction, not by test
results alone. Historical-only preflight subsequently completed successfully on
2026-10-03; its completion does not supply one-time final-run authorization.

Every final report must disclose that the dataset is simulated, December 3–16
had earlier validation exposure, and full-year exploratory data analysis inspected
the final interval. The interval is protected from subsequent selection but is
not historically fully unseen. Seasonal Naive's validation advantage over learned
models at 14 and 28 days must remain visible regardless of final ordering.

The first final execution already revealed reserved outcomes. Every corrected-run
report must additionally identify `final-20261003-01` as the preserved failed
execution, explain the PR #141 verifier correction and disclose that the corrected
run follows prior final-outcome access. Do not describe it as a first untouched
final evaluation, use either run for reselection or conceal the failed execution.
