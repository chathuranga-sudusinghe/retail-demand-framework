# Artifact and Storage Policy — Issue #92

**Status:** Proposed for human review before architecture implementation or retraining.
**Scope:** Repository-wide storage responsibilities, evidence retention and provenance. This document does not change scientific methodology, grant experiment approval, authorize cleanup or migration, or amend the frozen protocol.
**Related issue:** [#92 — Define data lifecycle and artifact storage policy](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/92).

## Authority and current implementation

The [shared data workflow](workflows/shared-data-foundation.md#issue-92--data-lifecycle-and-representation-contracts) owns representation stages. The [dataset contract](dataset.md), especially Sections 7/8, owns source meaning, field roles, quality, processed-layer intent and member-specific needs. The [feature contract](forecasting-feature-engineering.md) owns predictors, formulas, leakage controls, preprocessing semantics and model inputs. The [protocol](protocol.md) owns chronological windows, eligibility, metrics, selection, execution gates and experiment requirements. [Runner operations](forecasting-runner.md) own execution/orchestration and current persistence behavior. [Methodology revision](forecasting-methodology-revision.md) owns current-versus-historical methodology and provenance. The [research design](research-design.md) and [decision records](decisions/README.md) retain their existing research authority. This policy owns storage/retention only.

The repository currently contains local raw data, processed EDA/profile tables and a local execution record. artifacts/ exists and is empty; a root models/ directory is not yet present. The former outputs/ directory was intentionally removed. No artifact archive is inferred from that removal, and previous results must not be described as available without locating their evidence. Historical methods and results keep the classification in the methodology revision record; this storage policy neither relabels them as current evidence nor rewrites their scientific history.

The locations below are the proposed target architecture, not implemented paths. Do not recreate outputs/. Current paths.py, protocol Section 15 and runner documentation still target it; an owner-run command using unchanged code would recreate it. Execution must wait for separately reviewed path migration and matching authorization. This documentation does not perform that migration.

## Storage responsibilities

| Location | What belongs here | Persistence and retention boundary |
|---|---|---|
| data/raw/ | Original local source snapshots | Immutable reproduction input; retain locally or archive with source identity, hash and retrieval location. Never overwrite the only source of reported evidence |
| data/processed/validated/<data_version>/ | Accepted typed/sorted native records and associated quality audits | Shared validated handoff; regenerable only from exact retained parents/rules/code. No invented repair policy |
| data/processed/interim/<preparation_id>/ | Intermediate preparation tables and diagnostic scratch data | Temporary/regenerable; no authoritative model or research result lives only here |
| data/processed/model-ready/<representation_id>/ | Accepted engineered feature tables, separate authorized target tables, view membership/specifications; optional explicitly identified fitted matrices | Versioned, keyed handoffs; distinguish conceptual features from fold/horizon-specific fitted representations. Matrix persistence remains subject to the protocol boundary below |
| models/forecasting/<run_id>/ | Retained estimator binaries, descriptors, fitted preprocessing and small replay inputs | Model-only persistence authority; retain exact state with each retained estimator. Validation candidates remain labelled validation; final models require separate Gate 6 approval |
| artifacts/forecasting/<run_id>/ | Run metadata, retained authorization, candidate configuration/metric evidence, predictions, eligibility evidence, logs, diagnostics, integrity manifest | Machine-readable experiment evidence; completed bundles are immutable. Refer to model/data locations by explicit confined references and hashes rather than copying binaries/datasets |
| artifacts/authorizations/forecasting/ | Reviewed execution control records for future runs | Proposed home for control information, separate from scientific datasets. Existing data/processed/forecasting/validation_authorization.json remains untouched pending approved migration |
| reports/ | Reviewed human-readable Markdown findings and approved figures | Version-controlled research interpretation; link exact run/evidence identities and disclose review status, limitations and provenance. No full datasets or model binaries |
| artifacts/tmp/<run_id>/ | Unselected candidate binaries awaiting retention decisions, temporary serialization and runtime scratch files | Temporary, run-owned storage; cleanup only after approved verification/retention conditions. Not completed evidence; no destructive cleanup authorized here |

Version identifiers above identify immutable preparation/representation records, not a new scientific definition. Reuse requires matching parents, code, contract, scope and applicable fitted state; a filename or timestamp alone is insufficient. Never silently replace a version or use ambiguous latest-file discovery.

Detailed current EDA tables remain at data/processed/demand_eda/ and data/processed/temporal_profile/. They are descriptive/audit material, not model-ready training datasets. No move or renaming is required by this documentation change.

All datasets, generated tables, binaries, run evidence and temporary files remain local/ignored. Existing .gitignore protects data/processed/, artifacts/, models/ and common dataset formats; retain these protections. Only reviewed lightweight reports/figures, documentation, code and approved small fixtures belong in Git. Large records must not be embedded in reports or notebook outputs to bypass this boundary.

## Retention classes

- **Retained:** required to inspect or reproduce accepted evidence; preserve exact bytes/identity and their relationships.
- **Regenerable:** reproducible from retained source, code, environment, specifications and fitted state where applicable; removal must not break the only available evidence chain.
- **Temporary:** scratch material with no long-term evidential obligation; isolate by run and record failure/recovery status before reviewed cleanup.
- **Archived:** superseded but still evidential material, stored as a coherent version with verified hashes, archive location and retrieval instructions. Archiving is not deletion or relabelling as current evidence.

No automatic expiry period is selected here. Retention duration, backup destination, archive owner and cleanup approval process require human agreement. Keep evidence supporting research claims available through the required academic review/retention period.

## Evidence and model retention

| Item | Proposed long-term policy | Current-protocol exception / condition |
|---|---|---|
| Source identity and reproducibility inputs | Retain source citation, exact snapshot identity/hash/size, scoped input fingerprints, code commit/source hashes, environment and contract/protocol versions; retain source bytes or verified retrievable archive | Whole-file identity and authorized-view fingerprints have different purposes. Do not inspect protected final outcomes merely to expand provenance |
| Candidate configurations and metrics | Retain every evaluated configuration's canonical/requested/effective settings, role, fold/horizon, metrics/status/reasons, counts and selection evidence, including unsuccessful candidates | Never prune comparison evidence merely because its estimator is unselected |
| Predictions | Retain complete keyed prediction evidence required to reconcile the run and report; preserve origin, interval, horizon, configuration, stage, actuals/errors and unavailable status | Current protocol requires all candidate prediction records; selected-only prediction retention is not approved here. Keep retrospective actuals separate from prospective handoffs |
| Eligibility and chronological views | Retain population hashes, boundaries, membership/exclusion evidence and reasons; view copies are regenerable when exact parents remain available | No random split, altered eligibility or new final-period access |
| Selected validation models | Retain reusable selected estimator bundles according to the later human-approved retention set, with exact fitted state and replay evidence. The amendment must settle fold-model, tie, supportive and audit coverage | Selection follows the protocol, not this policy. Administrative leaders are not human-frozen final models. Current amendment still requires ALL successful learned fits |
| Fitted preprocessing and replay inputs | Retain exact vocabulary, numerical scaling, physical/conceptual order, state version, training population/fold/horizon and reference prediction inputs with each retained model; share immutable state only through verified references | Reload never refits categories/scaling or substitutes a different fold's state. Baselines need formula/history provenance, not estimator binaries |
| Unselected candidate binaries | Proposed: temporary during fitting/selection/verification; avoid indefinite retention when complete configuration/metric/prediction evidence is sufficient. Keep only approved audit exceptions | Not currently disposable: all-fit persistence and replay remain operative until amendment and implementation acceptance |
| Final models | Retain approved final estimator/preprocessor bundles with training population, selection-freeze and final-run authorization references | Final fitting/evaluation remains blocked under Gate 6; no reuse of a fold model as an approved final model |
| Manifests and logs | Retain authorization, run metadata, completion manifest, finalized run log and integrity outcomes; retain failure diagnostics for investigated runs with explicit failure status | Manifest-last completion, no overwrite, and failed/incomplete-run rejection remain required |
| Intermediate tables/matrices | Regenerate from exact inputs/contracts/state when needed; retain accepted shared handoffs or costly/non-reconstructible evidence explicitly | Current amendment forbids copying full raw/processed datasets or training matrices into the run bundle; new handoff/matrix persistence requires explicit compatibility review |
| Human-readable reports | Retain reviewed findings, metrics, configuration-selection rationale/status, limitations, provenance and links to supporting evidence | A generated comparison is a draft until reviewed; a validation report does not imply final evaluation |

Selective retention must preserve the replay coverage approved for retained models without retaining every grid candidate indefinitely. Metrics/configuration/prediction evidence can be retained independently of candidate binaries; dropping a binary never justifies dropping its comparison evidence. This storage proposal defines no new selection rule; training grids, model roles, scoring, ranking and human freeze rules remain unchanged. Numerical reproduction by rerunning training is an experiment and still requires specific authorization; regenerability is not permission to train.

## Version, completion and archival discipline

Each run must identify its source/view, feature contract, preprocessing representation, protocol, configuration, software environment and artifact schema. Exact identifiers/hashes and authorized scope must connect retained data, models, metrics, predictions and report references. Schema/path changes must be reviewed and versioned; this document assigns no replacement protocol/schema number.

Completion must be published only after scientific evidence reconciliation and the required retained-model replay succeed. A future manifest must cover files in the evidence bundle plus explicitly linked data/model evidence, with allowed-root containment and hashes; current verification assumes a single run directory and does not yet support this layout.

Do not delete files from a completed manifest or rewrite it to hide pruning. Under a future selective policy, temporary candidates should be excluded from the final completed retention set only after approved verification and selection rules are satisfied. Historical all-fit bundles remain immutable; any approved archival conversion needs a separate derivative manifest identifying its parent and omissions, without pretending to be the original verified bundle.

Archive superseded runs supporting reports, methodology revisions or audit findings with their models/state as required by their governing protocol. Retain failed/interrupted evidence needed to explain failures separately from completed research evidence. Record archive location/access, hashes, source/code/environment requirements, review status and retrieval checks. Missing historical evidence must be recorded as unavailable, not regenerated and presented as original results.

Temporary cleanup must be run-specific, reviewed and unable to remove raw inputs, retained models/state, completed evidence or unrelated files. Crash leftovers remain incomplete; their existence never establishes completion. No cleanup operation is authorized by Issue #92.

## Required protocol amendment before selective retention

The conflict is explicit: the protocol's **Issue #89 operational/artifact amendment** states, “All successful learned validation fits are retained”; runner operations likewise say every successful learned validation fit is saved. integrity.verify_scientific currently requires one model record per successful learned candidate and replays all saved models. This issue does not override any of those requirements.

Current requirements remain operative until **Issue #94 or a dedicated human-approved amendment task** changes them. A later amendment to docs/protocol.md must explicitly:

1. Amend **Section 15 — Stable output artifacts** to replace the removed run location with the agreed artifacts/data/models boundaries and evidence references; retain the required scientific tables unless a separately reviewed schema change is approved.
2. Amend the **Issue #89 operational/artifact amendment** to replace all-fit long-term persistence with a precisely enumerated human-approved retention set, explicitly addressing selected configuration fold models, tied configurations, supportive models and audit exceptions; define handling of unselected candidates before completion.
3. Amend **Section 13 — Machine-readable reproducibility metadata** and the operational amendment to declare retained versus temporary/not-retained model status, selection basis, reasons, model/state paths/hashes, cross-root manifest coverage and the retention-policy version.
4. Replace the all-candidate saved-model replay requirement with retained-model replay plus complete candidate metric/configuration/prediction reconciliation. Distinguish fit/evaluation counts from retained-model counts; neither missing retained models nor discarded scientific evidence may pass completion.
5. Explicitly resolve the current no-full-dataset/training-matrix-copy restriction if new validated/engineered handoffs or fitted matrices are to be persisted. Specify the allowed locations and protected outcome scopes rather than silently broadening run exports.
6. Record the approval and version/fingerprint changes; align runner/path/persistence/integrity documentation, implementation and tests in a separate task. Obtain implementation acceptance and a new matching specific-run authorization before any experiment.

The same task must amend docs/forecasting-runner.md without inventing scientific definitions:

- **Normal owner command:** document reviewed artifact/model/data and authorization paths after migration; remove active instructions that recreate outputs/.
- **Responsibilities:** align the path, persistence and integrity module mappings with the accepted implementation.
- **Lifecycle / Outputs:** replace “Every successful learned validation fit is saved” only after protocol approval; distinguish evaluated candidates from retained bundles, identify exact preprocessing/replay dependencies and explain the completion manifest's evidence references.
- **Failure and interruption / Checks:** document temporary-candidate handling, immutable completion, failure evidence and the accepted verification checks for the new layout/retention policy.

Issue #92 leaves both protocol.md and forecasting-runner.md unchanged. Merely drafting this policy does not amend their operative all-fit requirements, refresh approvals or make the proposed storage layout executable.

Until then, selective retention is a proposal only. Do not delete unselected models from any surviving governed bundle, alter existing completion manifests, move data, or run the unchanged removed-path runner. Gate 6, forecasting definitions and downstream approval boundaries remain unchanged.

## Later document alignment and human decisions

After review, README, dataset processed-view guidance, feature representation mapping, forecasting workflow, protocol and runner documentation need links/current-state alignment. The methodology revision record should distinguish missing historical evidence from archived evidence. No source/test edits or other document edits are included in this task.

Human approval is still required for this policy, the exact retention set/audit exceptions, new persisted handoff requirements and serialization/version conventions, archival/backup responsibilities and duration, the protocol amendment, implementation acceptance and any specific experiment. References to models or reports here grant no final-model, publication or execution approval.
