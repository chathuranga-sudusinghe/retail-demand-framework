# Forecasting runner — Issue #89 orchestration

The frozen scientific contract remains in [protocol.md](protocol.md). Issue #89 orchestration was merged through PR #90. Merged Issues #92/#93 own [lifecycle](workflows/shared-data-foundation.md), [storage/retention](artifact-storage-policy.md), [applied MLOps](workflows/applied-mlops.md), [reporting](../reports/README.md) and [progress](research-progress.md). Issue #111 implements Phase 5 run storage; Issue #116 documents that contract. Phase 1 final runtime is merged in [PR #133](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/133) and explicitly accepted by the owner under Issue #131. Historical-only preflight completed successfully on 2026-10-03: `READY FOR AUTHORIZATION PREPARATION`. The real `final-20261003-01` execution revealed reserved outcomes and failed during final replay verification. PR #141 fixed the verified implementation defect. The owner explicitly authorized `final-20261003-02` as a defect-correction rerun with the same frozen 28 evaluations and producer mapping; it has not been executed. The original failed bundle remains preserved. Source/Git hashes are provenance only; scientific bindings, explicit specific-run approval and overwrite protection remain enforced. Result-driven retries, search, retuning, reselection and candidate substitution remain prohibited. Selective retention/pruning is deferred to Phase 6.

## Existing entrypoint — explicit run authorization required

The entrypoint uses the implemented Phase 5 storage contract below. Execution
requires human implementation acceptance, the approved Python 3.12.3 environment
and a matching specific run authorization. This documentation does not authorize a run.

```bash
python -m src.forecasting.experiment
```

Current locations:

- Dataset: `data/processed/validated/supply-chain-dataset1-validated-v1/validated.parquet`.
- Reviewed local record: `data/processed/forecasting/validation_authorization.json` (unchanged).
- Artifact-run anchor: `artifacts/forecasting/<run_id>/`.
- All persisted model/state bundles: `models/forecasting/<run_id>/`.
- Generated draft comparison: `reports/forecasting/drafts/<run_id>/comparison.md`.

Historical provenance only: the former `outputs/revised-forecasting/<exact-approved-run-id>/`
single bundle is no longer a runtime destination. Its removal does not establish
that an archive exists or that historical results are available.

The existing ValidationAuthorization fields live in authorization.py, with direct
compatibility exports from execution.py and metadata.py. Issue #106 separates
package responsibilities; Issue #108 supplies the validation-scoped Parquet
handoff and Phase 4 preparation lifecycle below. Phase 5 leaves all
`data/processed/...` ownership and the authorization-record location unchanged.

The reviewed record supplies the exact ID, ordered scope and human references.
No approval is generated, no hashes are refreshed, and no latest-file discovery
occurs. Missing/malformed/stale records, missing datasets, invalid validated
handoffs, redirected or non-directory storage ancestors, and consumed run
directories fail before dataset loading or execution as applicable. Existing
artifact, model or draft run directories cannot be reused or resumed; another run
requires separate review. Approval references are a local workflow guard, not
cryptographic identity.

`RepositoryLayout` resolves all storage locations. `ArtifactWriter.directory`
remains the canonical artifact-run anchor; model and report locations resolve
from that anchor, with the same exact run ID.

## Responsibilities

| Module | Responsibility |
|---|---|
| paths.py | Fixed repository-relative locations; no import-time writes. |
| authorization.py | Strict record/scope loading, human approval checks and execution-context resolution. |
| execution.py | Scoped validated Parquet input and strict four-column forecasting projection; direct legacy authorization exports. |
| model_ready.py | One-fold preparation, separate features/targets, fitted preprocessing, model-ready Parquet publication and verified readback. |
| experiment.py | Thin CLI/runtime entrypoint: arguments, authorization resolution, input loading and orchestration dispatch. |
| orchestration.py | Candidate planning, preparation/execution coordination, validation lifecycle, independent recovery and final-evaluation blocking. |
| persistence.py | Authorization snapshots, checkpoints, model-index coordination, result-set persistence and manifest-last finalization; delegates low-level artifact/model I/O. |
| features/targets/validation/configuration/models/baselines/metrics | Unchanged scientific definitions and runtime controls. |
| preprocessing.py | Unchanged transformations plus versioned fitted-state reconstruction. |
| evaluation/selection | Existing populations, alignment and selection semantics. |
| model_artifacts.py | Native candidate persistence, provenance descriptors and replay. |
| artifacts.py | Existing schemas, exclusive directories, atomic writes and streaming hashes. |
| metadata.py | Git/source/protocol/input/feature/runtime/build/environment provenance. |
| reporting/progress | Read-only reporting, verified completed consumption, UTC phase events. |
| integrity.py | Readback schemas/counts/keys/metrics/selection/model links, hashes and completion verification. |

## Phase 4 model-ready preparation — Issue #108

The preparation lifecycle is:

```text
validated.parquet -> scoped forecasting projection -> existing fold/origin features
  -> separate horizon targets -> existing training-only fitted preprocessing
  -> model-ready Parquet datasets + preparation metadata
```

`execution.load_projection` selects only `SKU_ID`, `Warehouse_ID`, `Date` and
`Units_Sold`, using Arrow date filters before decoding demand. A selected fold
loads January 1 through its frozen validation end; the reserved December 3–30
period is excluded. Existing `prepare_fold` owns all feature, cumulative 1/7/14/28-day
target, eligibility and preprocessing semantics. No estimator is constructed or
trained. `Date` in features/targets is the first target day, one day after the
forecast origin. Historical labels must finish by the training cutoff.

`model_ready.prepare_model_ready` accepts one validation fold and an explicit
representation ID. It writes an exclusive local version under
`data/processed/model-ready/<representation_id>/`:

```text
projection.parquet
origin-features.parquet
h<1|7|14|28>/
  training-features.parquet
  training-targets.parquet
  validation-targets.parquet
  <existing-model-family>/
    preprocessing.json
    training-matrix.parquet
    origin-matrix.parquet
model-ready.json
```

Each fold has 54 Parquet files, 20 fitted-state JSON files and one preparation
metadata file. Features and encoded matrices contain no targets or `Units_Sold`;
target tables contain only native keys and one horizon target. Matrix keys are
identity columns, excluded from the physical predictor list. Preprocessing
state is fitted only on eligible historical training features, independently
per horizon; the unchanged primary/shared and supportive transformations are reused.

Metadata records versions, scope/origin/cutoffs, eligibility/population fingerprints,
ordered schemas, physical predictor names, file sizes/hashes, implementation and
protocol hashes, and parent validated provenance/source receipts. The complete
parent Parquet SHA-256 is recomputed from actual file bytes and compared with
the published receipt before Arrow consumption. Byte hashing does not decode or
evaluate reserved outcomes; date filters restrict decoded data. Parent metadata
hashes, Parquet footer schema/population, file size and scoped logical data are
checked again before publication. Protocol, feature-contract, Git state and source
hashes come from the repository layout supplied to preparation.

Files and restored transformations are read back exactly. `model-ready.json` is
written last; incomplete versions are rejected and existing IDs cannot be reused.
`read_model_ready` verifies hashes, schemas, key alignment, frozen chronology and
restored matrix values without fitting or reopening parent outcomes. Its optional
external metadata hash anchors the preparation record. Human review remains pending;
preparation metadata grants no experiment or final-evaluation authorization.

After implementation review and explicit authorization for real preparation, the
project owner can use this command shape (not executed for Issue #108):

```bash
python -m src.forecasting.model_ready --representation-id <reviewed-id> --fold <1-4>
```

Final/refit stages are rejected before input access. This Phase 4 preparation
lifecycle remains separate from the implemented Phase 5 run storage below.
Selective model retention/pruning remains deferred to Phase 6. No research results
or run artifacts are generated by this preparation lifecycle.

## Lifecycle

`preflight -> running -> finalizing -> verified_completed`; failures are `failed` or `interrupted`. Metadata alone never establishes completion. Persisted scientific evidence is verified; source/protocol/input and execution record are checked again; finalization logging closes; final metadata is written; artifact-side `artifacts/forecasting/<run_id>/run_manifest.json` is atomically published LAST as the sole completion authority. Consumers must use `verify_completed`. Missing, partial, inconsistent or corrupt bundles are rejected. The comparison records finalizing status at rendering time; the manifest is the completion authority. Undefined WAPE remains explicit and unselectable. Selection/freeze still requires human review.

## Phase 5 storage contract

Scientific names and CSV columns remain unchanged. The current run layout is:

```text
artifacts/forecasting/<run_id>/
  run_metadata.json
  fold_metrics.csv
  configuration_summary.csv
  selected_configurations.json
  predictions.csv
  eligibility_counts.csv
  authorization.json
  run.log
  run_manifest.json
  diagnostics.json                 # failure diagnostics where writable

models/forecasting/<run_id>/
  validation/<family>/h<horizon>/<configuration>/fold-<n>/
    model.ubj | model.txt | model.cbm | model.joblib
    descriptor.json
  preprocessing/<family>/h<horizon>/fold-<n>/
    state.json
    origin_features.json

reports/forecasting/drafts/<run_id>/
  comparison.md
```

Manifest contract version 2 (`manifest_version: 2`) records repository-relative
file paths, explicit owners (`artifacts`, `models`, `reports`) and SHA-256 hashes.
It covers finalized machine evidence, metadata, authorization, logs, every
persisted model/descriptor, preprocessing state, replay inputs and the draft
comparison. It excludes the completion manifest itself. Metadata's
`artifact_manifest` contains receipts, not completion authority.

The sole completion authority is
`artifacts/forecasting/<run_id>/run_manifest.json`, written last after scientific
reconciliation, all-model replay, log closure and final metadata persistence.
Model writes and draft writes are protected by that artifact-side manifest;
no model-side or report-side completion manifest is used. `verify_completed`
accepts the artifact-run anchor and verifies the exact run-owned file set across
all three locations. Missing, extra, corrupted, redirected, cross-run or unfinished
evidence blocks completed consumption.

Model descriptor contract version 2 (`descriptor_version: 2`) and model-index
receipts use repository-relative `model_path`, `descriptor_path`,
`preprocessor_path` and `origin_features_path` references under the same
`models/forecasting/<run_id>/`.
The descriptor's source-hash reference points back to the artifact-side run
metadata. Candidate/family/horizon/configuration/fold ownership, hashes and
provenance are verified before replay. Historical version-1 compatibility or
migration is not implemented.

The scientific schema remains `issue-65-v2` and the protocol version remains
`issue-65-matched-frozen-1`. Fitted preprocessing state remains version 1;
native serialization formats, preprocessing behavior and scientific checks are
unchanged.

Phase 5 saves and replays every successful learned validation fit, including
unselected candidates and all tied configurations. Full-plan counts remain
1,152 primary fits, 32 supportive fits, 32 baseline evaluations, 1,216 evaluations
and 304 summaries: planned counts, not results. Native coverage would yield
304,000 prediction records. Baselines have formula provenance, not binaries.
Retaining all 1,184 learned artifacts increases storage requirements, particularly
300-tree Random Forest models; review capacity for all-model persistence before
any authorized run. No raw/full dataset or training matrix is copied into run storage.

Descriptors link exact run/family/horizon/configuration/fold, training/validation
intervals, Git/source/protocol/feature/input provenance, requested/effective
parameters, versions and hashes. Saved state restores the original one-hot order
and Ridge scaling. Every saved model replays persisted predictions exactly using
the same matrix layout and CPU/thread controls, without refitting. Only trusted
locally generated joblib files with verified provenance/hashes are loaded. Hashes
detect alterations, not malicious replacement of an entire bundle.

## Retention and reporting boundary

Selective model retention/pruning is deferred to Phase 6 and requires a separate
human-approved retention set and implementation. Phase 5 introduces no candidate
deletion, temporary-candidate retention policy, cleanup or historical conversion.
Complete configuration, metric, prediction, eligibility and selection evidence
remains retained for all evaluated candidates.

`comparison.md` is generated draft evidence, labelled pending human review.
Its links resolve from `reports/forecasting/drafts/<run_id>/` to machine-readable
evidence at the artifact anchor, including the sole completion manifest. Report
creation and verified completion do not establish human review, interpretation
acceptance, configuration freeze or final-run authorization.

Later human-reviewed findings and approved figures follow
[reports/README.md](../reports/README.md), at `reports/forecasting/<run_id>.md` and
`reports/figures/forecasting/<run_id>/`. Keep those reviewed outputs separate from
the ignored generated draft. Completed draft evidence stays immutable alongside
its artifact/model dependencies. Data handoffs and the Phase 4 preparation
lifecycle retain their existing ownership.

## Failure and interruption

Recovery independently attempts metadata, diagnostics and partial evidence; secondary failures attach notes without replacing the original exception. Failed/interrupted runs publish no completion manifest or valid selection. Filesystem failure may prevent diagnostics, but absent completion still blocks promotion. SIGKILL/power loss cannot invoke recovery: the run remains incomplete. There is no automatic retry/resume or cleanup. Partial artifact, model and draft directories, including unfinished serialization files in their owning directory, are retained as diagnostic evidence; they cannot be consumed as completed.

## Checks

```bash
python -m pytest -q
ruff check src/forecasting tests/test_forecasting_*.py
python -m mypy src/forecasting --explicit-package-bases --disable-error-code import-untyped
python -m pip check
git diff --check
```

Tests use synthetic panels/mock fits and small controlled native smoke tests. They never read the project dataset and are not research comparison evidence. The complete candidate plan uses mocks, never the real 1,152-fit workload.

## Separate final-evaluation runtime — Issues #130/#131

The validation entrypoint, including `--stage final_evaluation`, stays blocked.
[DR-014](decisions/DR-014-forecasting-selection-and-final-refit.md) records the
owner-approved scientific freeze, 28-candidate scope, separate producer mapping
and fresh estimator/preprocessing refit policy. PR #133 merged the separate final
runtime; the owner explicitly accepted implementation readiness under Issue #131
on 2026-10-03. Historical-only preflight completed successfully on 2026-10-03:
`READY FOR AUTHORIZATION PREPARATION`. Subsequently `final-20261003-01` ran once,
accessed reserved outcomes and failed during replay verification; retain its
artifact/model/draft bundle and failed status unchanged. PR #141 fixed the
verified C/Fortran replay-layout defect. The owner explicitly authorized
`final-20261003-02` as a defect-correction rerun with unchanged scientific scope.

The argument-free command `python -m src.forecasting.final_evaluation` reads
`data/processed/forecasting/final_authorization.json`. It performs real refits and
outcome reveal and must be run manually by the owner after review. Source/Git
hashes record provenance and do not bind permission; scientific-document, data,
scope, pinned environment and unused-storage checks remain enforced. A defect
rerun requires a new explicit approval and unused ID. Performance-driven retries,
search, retuning, reselection, substitutions, automatic retries and resumption
remain prohibited. The corrected run has not been executed.

The [final-evaluation guide](forecasting-final-evaluation.md) documents ordering,
record requirements and storage. Consume completed final evidence with
`src.forecasting.final_artifacts.verify_final_completed` at its artifact anchor;
validation continues to use its existing `verify_completed` and fold schemas.
No final run, deployment promotion or downstream methodology is authorized.
Disclose earlier December 3–16 validation and full-year EDA exposure.
