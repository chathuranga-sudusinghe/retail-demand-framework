# Forecasting runner — Issue #89 orchestration

The frozen scientific contract remains in [protocol.md](protocol.md). Issue #89 orchestration was merged through PR #90. Merged Issues #92/#93 own [lifecycle](workflows/shared-data-foundation.md), [storage/retention](artifact-storage-policy.md), [applied MLOps](workflows/applied-mlops.md), [reporting](../reports/README.md) and [progress](research-progress.md). Issue #94 aligns operational documentation; source behavior remains unchanged. No new experiment is authorized and Gate 6 remains blocked.

## Existing entrypoint — blocked pending architecture migration

The accepted legacy entrypoint is shown for implementation identification only.
Do not execute it with unchanged code: it would recreate the removed storage
architecture. Future execution requires reviewed migration, the approved Python
3.12.3 environment and a new matching specific authorization.

```bash
python -m src.forecasting.experiment
```

Current code locations — legacy runtime description, not active execution guidance:

- Dataset: `data/processed/validated/supply-chain-dataset1-validated-v1/validated.parquet`.
- Reviewed local record: `data/processed/forecasting/validation_authorization.json`.
- Legacy output: `outputs/revised-forecasting/<exact-approved-run-id>/` (removed; migration required).

The existing ValidationAuthorization fields now live in authorization.py, with direct compatibility exports from execution.py and metadata.py. Issue #106 separates package responsibilities. Issue #108 replaces raw CSV input with the approved validation-scoped Parquet handoff and adds the Phase 4 preparation lifecycle below; experiment storage and retention remain pending migration. The reviewed record supplies the exact ID, ordered scope and human references. No approval is generated, no hashes are refreshed, and no latest-file discovery occurs. Missing/malformed/stale records, missing datasets, invalid validated handoff metadata/schema and consumed run directories fail before estimator construction. A failed directory cannot be resumed/reused; another run requires separate review. Approval references are a local workflow guard, not cryptographic identity.

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

Final/refit stages are rejected before input access. Phase 5 run-storage migration
and Phase 6 model retention are outside this change; the experiment entrypoint
above remains blocked pending those reviewed changes. No research results or run
artifacts are generated by this preparation lifecycle.

## Lifecycle

`preflight -> running -> finalizing -> verified_completed`; failures are `failed` or `interrupted`. Metadata alone never establishes completion. Persisted scientific evidence is verified; source/protocol/input and execution record are checked again; finalization logging closes; final metadata is written; `run_manifest.json` is atomically published LAST. Consumers must use `verify_completed`. Missing, partial, inconsistent or corrupt bundles are rejected. The comparison records finalizing status at rendering time; the manifest is the completion authority. Undefined WAPE remains explicit and unselectable. Selection/freeze still requires human review.

## Legacy runtime persistence — implementation evidence

Existing scientific names and CSV columns remain unchanged:

```text
run_metadata.json
fold_metrics.csv
configuration_summary.csv
selected_configurations.json
predictions.csv
eligibility_counts.csv
comparison.md
```

Additions: exact retained `authorization.json`, `run.log`, `run_manifest.json`, failure `diagnostics.json` where writable, and validation models/state. The scientific schema remains `issue-65-v2`; manifest/model/preprocessing descriptors have version 1. The final manifest hashes all finalized files, including metadata/log/model/state/authorization. It does not claim to hash itself. Full source/environment provenance remains in metadata rather than duplicated in every descriptor.

```text
models/validation/<family>/h<horizon>/<configuration>/fold-<n>/
  model.ubj | model.txt | model.cbm | model.joblib
  descriptor.json
models/preprocessing/<family>/h<horizon>/fold-<n>/
  state.json
  origin_features.json
```

Under the accepted legacy runtime contract, every successful learned validation fit is saved. Full-plan counts are 1,152 primary fits, 32 supportive fits, 32 baseline evaluations, 1,216 evaluations and 304 summaries: planned counts, not results. Native coverage yields 304,000 prediction records. Baselines have formula provenance, not binaries. Retaining 1,184 learned artifacts increases storage requirements, particularly 300-tree Random Forest models; review capacity against the approved retention plan before any future authorized run. No raw/full dataset or training matrix is copied.

Descriptors link exact run/family/horizon/configuration/fold, training/validation intervals, Git/source/protocol/feature/input provenance, requested/effective parameters, versions and hashes. Versioned state restores the original one-hot order and Ridge scaling. Reloaded models replay persisted predictions exactly using the same matrix layout and CPU/thread controls. No refitting occurs. Only trusted locally generated joblib files with verified provenance/hashes are loaded. Hashes detect alterations, not malicious replacement of an entire bundle.

## Approved architecture handoff — not yet implemented

Machine-readable evidence belongs in `artifacts/forecasting/<run_id>/`, selected
reusable model/state bundles in `models/forecasting/<run_id>/`, reviewed findings
in `reports/forecasting/<run_id>.md`, and temporary candidates in the storage
policy's run-scoped temporary location. Data handoffs retain the lifecycle's
scope/view/feature/preprocessing order; Issue #108 now implements validation-scoped
model-ready matrices separately from run-storage migration. Existing module responsibilities above describe current
code; they must be updated after accepted migration rather than inventing new APIs.

The [Issue #94 protocol amendment](protocol.md#issue-94-operational-alignment--implementation-boundary)
defines the required cross-location manifests, metadata and retained-model replay.
Complete configuration/metric/prediction evidence must survive for all evaluated
candidates. The exact selected-fold/tie/supportive/audit retention set and schema
version still require human approval; until accepted implementation, all-fit
persistence and replay remain the compatibility requirement. No pruning of current
or historical bundles is authorized. Retained models must keep exact fitted
preprocessing/order/scaling and origin replay inputs; reload never refits.

Completion must reconcile all scientific evidence, hashes and retained dependencies,
then publish the final manifest last. Retained-model/replay counts must be distinct
from evaluation counts. Completed bundles remain immutable; any approved archive
derivative must identify its parent and omissions. Missing retained dependencies,
failed/partial evidence or inconsistent candidate records block completed consumption.
Existing verification is single-bundle/all-fit and cannot verify the new layout yet.

The completed-run handoff includes a report following the reporting authority;
generated `comparison.md` remains a draft evidence summary. Human interpretation,
selection freeze and final authorization are separate. Link reviewed milestones in
the progress log; do not invent approvals or results from the existence of a report.

## Failure and interruption

Recovery independently attempts metadata, diagnostics and partial evidence; secondary failures attach notes without replacing the original exception. Failed/interrupted runs publish no completion manifest or valid selection. Filesystem failure may prevent diagnostics, but absent completion still blocks promotion. SIGKILL/power loss cannot invoke recovery: the run remains incomplete. There is no automatic retry/resume. Partial files are diagnostic only.

## Checks

```bash
python -m pytest -q
ruff check src/forecasting tests/test_forecasting_*.py
python -m mypy src/forecasting --explicit-package-bases --disable-error-code import-untyped
python -m pip check
git diff --check
```

Tests use synthetic panels/mock fits and small controlled native smoke tests. They never read the project dataset and are not research comparison evidence. The complete candidate plan uses mocks, never the real 1,152-fit workload.

The final entry, including `--stage final_evaluation`, stays blocked. Final estimator/preprocessor policy and execution need separate approval; no fold-4 reuse, all-history refit, deployment promotion or downstream rule is assumed. Disclose earlier December 3–16 validation and full-year EDA exposure.
