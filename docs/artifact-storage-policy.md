# Artifact and Storage Policy — Issue #92

**Status:** Merged Issue #92 storage authority; Issue #111 implements Phase 5 forecasting storage. Issue #116 documents the implemented contract for human review.
**Scope:** Repository-wide storage responsibilities, evidence retention and provenance. This document records the already-implemented Phase 5 storage contract. It does not change scientific methodology, grant experiment approval, authorize cleanup or data migration, or independently amend the frozen scientific protocol. Selective retention/pruning is deferred to Phase 6.
**Related issue:** [#92 — Define data lifecycle and artifact storage policy](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/92).

## Authority and current implementation

The [shared data workflow](workflows/shared-data-foundation.md#issue-92--data-lifecycle-and-representation-contracts) owns representation stages. The [dataset contract](dataset.md), especially Sections 7/8, owns source meaning, field roles, quality, processed-layer intent and member-specific needs. The [feature contract](forecasting-feature-engineering.md) owns predictors, formulas, leakage controls, preprocessing semantics and model inputs. The [protocol](protocol.md) owns chronological windows, eligibility, metrics, selection, human approval controls and experiment requirements. [Runner operations](forecasting-runner.md) own execution/orchestration and current persistence behavior. [Methodology revision](forecasting-methodology-revision.md) owns current-versus-historical methodology and provenance. The [research design](research-design.md) and [decision records](decisions/README.md) retain their existing research authority. This policy owns storage/retention only.

Phase 5 separates forecasting evidence, model bundles and generated draft reports into the run-owned locations below. Source data, approved processed handoffs and the local execution record retain their existing ownership. The former outputs/ directory was intentionally removed. No artifact archive is inferred from that removal, and previous results must not be described as available without locating their evidence. Historical methods and results keep the classification in the methodology revision record; this storage policy neither relabels them as current evidence nor rewrites their scientific history.

The forecasting runtime now uses `artifacts/forecasting/<run_id>/`, `models/forecasting/<run_id>/` and `reports/forecasting/drafts/<run_id>/comparison.md`. The former `outputs/` layout is historical provenance only. Issue #94's earlier implementation boundary is preserved as history in the protocol; [the Phase 5 contract](protocol.md#phase-5-storage-contract) records current behavior. Execution still requires human implementation acceptance and a matching specific run authorization.

## Storage responsibilities

| Location | What belongs here | Persistence and retention boundary |
|---|---|---|
| data/raw/ | Original local source snapshots | Immutable reproduction input; retain locally or archive with source identity, hash and retrieval location. Never overwrite the only source of reported evidence |
| data/processed/validated/<data_version>/ | Accepted typed/sorted native records and associated quality audits | Shared validated handoff; regenerable only from exact retained parents/rules/code. No invented repair policy |
| data/processed/interim/<preparation_id>/ | Intermediate preparation tables and diagnostic scratch data | Temporary/regenerable; no authoritative model or research result lives only here |
| data/processed/model-ready/<representation_id>/ | Accepted engineered feature tables, separate authorized target tables, view membership/specifications; optional explicitly identified fitted matrices | Versioned, keyed handoffs; distinguish conceptual features from fold/horizon-specific fitted representations. Matrix persistence remains subject to the protocol boundary below |
| models/forecasting/<run_id>/ | Retained estimator binaries, descriptors, fitted preprocessing and small replay inputs | Phase 5 retains every successful learned validation fit with exact state and replay inputs. Completion is established only by the artifact-side manifest. Validation candidates remain labelled validation; reserved final evaluation remains blocked pending separate authorization |
| artifacts/forecasting/<run_id>/ | Run metadata, retained authorization, candidate configuration/metric evidence, predictions, eligibility evidence, logs, diagnostics, integrity manifest | Machine-readable experiment evidence and the sole completion authority, `run_manifest.json`, written last. Completed evidence is immutable; references to models and the draft report are confined and hash-verified |
| data/processed/forecasting/validation_authorization.json | Current reviewed execution control record | Location and ownership remain unchanged in Phase 5; relocation requires separate approved work |
| reports/forecasting/drafts/<run_id>/comparison.md | Generated forecasting comparison evidence | Local/ignored draft, pending human review; covered by the artifact-side completion manifest. Generation and completion confer no human acceptance |
| reports/ | Later reviewed human-readable Markdown findings and approved figures | Version-controlled research interpretation, separate from generated drafts; link exact run/evidence identities and disclose review status, limitations and provenance. No full datasets or model binaries |
| artifacts/tmp/<run_id>/ | Deferred selective-retention/scratch proposal | Not used for Phase 5 candidate retention; Phase 6 requires separate approval. Phase 5 serialization temporary files remain in their owning run directories, and no automatic cleanup is authorized |

Version identifiers above identify immutable preparation/representation records, not a new scientific definition. Reuse requires matching parents, code, contract, scope and applicable fitted state; a filename or timestamp alone is insufficient. Never silently replace a version or use ambiguous latest-file discovery.

Detailed current EDA tables remain at data/processed/demand_eda/ and data/processed/temporal_profile/. They are descriptive/audit material, not model-ready training datasets. No move or renaming is required by this documentation change.

All datasets, generated tables, binaries, run evidence and temporary files remain local/ignored. Existing .gitignore protects data/processed/, artifacts/, models/ and common dataset formats; retain these protections. The narrow `/reports/forecasting/drafts/` rule also protects generated forecasting draft reports while leaving later reviewed reports/figures eligible for version control. Only reviewed lightweight reports/figures, documentation, code and approved small fixtures belong in Git. Large records must not be embedded in reports or notebook outputs to bypass this boundary.

## Retention classes

- **Retained:** required to inspect or reproduce accepted evidence; preserve exact bytes/identity and their relationships.
- **Regenerable:** reproducible from retained source, code, environment, specifications and fitted state where applicable; removal must not break the only available evidence chain.
- **Temporary:** scratch material with no long-term evidential obligation; isolate by run and record failure/recovery status before reviewed cleanup.
- **Archived:** superseded but still evidential material, stored as a coherent version with verified hashes, archive location and retrieval instructions. Archiving is not deletion or relabelling as current evidence.

No automatic expiry period is selected here. Retention duration, backup destination, archive owner and cleanup approval process require human agreement. Keep evidence supporting research claims available through the required academic review/retention period.

## Evidence and model retention

| Item | Architecture retention policy | Current implementation / approval condition |
|---|---|---|
| Source identity and reproducibility inputs | Retain source citation, exact snapshot identity/hash/size, scoped input fingerprints, code commit/source hashes, environment and contract/protocol versions; retain source bytes or verified retrievable archive | Whole-file identity and authorized-view fingerprints have different purposes. Do not inspect protected final outcomes merely to expand provenance |
| Candidate configurations and metrics | Retain every evaluated configuration's canonical/requested/effective settings, role, fold/horizon, metrics/status/reasons, counts and selection evidence, including unsuccessful candidates | Never prune comparison evidence merely because its estimator is unselected |
| Predictions | Retain complete keyed prediction evidence required to reconcile the run and report; preserve origin, interval, horizon, configuration, stage, actuals/errors and unavailable status | Current protocol requires all candidate prediction records; selected-only prediction retention is not approved here. Keep retrospective actuals separate from prospective handoffs |
| Eligibility and chronological views | Retain population hashes, boundaries, membership/exclusion evidence and reasons; view copies are regenerable when exact parents remain available | No random split, altered eligibility or new final-period access |
| Selected validation models | Retain reusable selected estimator bundles according to the later human-approved retention set, with exact fitted state and replay evidence. The amendment must settle fold-model, tie, supportive and audit coverage | Selection follows the protocol, not this policy. Administrative leaders are not human-frozen final models. Phase 5 retains ALL successful learned fits after storage migration; selective retention/pruning is deferred to Phase 6 |
| Fitted preprocessing and replay inputs | Retain exact vocabulary, numerical scaling, physical/conceptual order, state version, training population/fold/horizon and reference prediction inputs with each retained model; share immutable state only through verified references | Reload never refits categories/scaling or substitutes a different fold's state. Baselines need formula/history provenance, not estimator binaries |
| Unselected candidate binaries | Under an approved exact selective-retention set: temporary during fitting/selection/verification; avoid indefinite retention when complete configuration/metric/prediction evidence is sufficient. Keep only approved audit exceptions | Not disposable in Phase 5: all-model persistence and replay remain operative; selective retention/pruning requires separate Phase 6 approval and implementation |
| Final models | Retain approved final estimator/preprocessor bundles with training population, selection-freeze and final-run authorization references | Reserved final evaluation and final fitting remain blocked pending separate authorization; no reuse of a fold model as an approved final model |
| Manifests and logs | Retain authorization, run metadata, completion manifest, finalized run log and integrity outcomes; retain failure diagnostics for investigated runs with explicit failure status | Manifest-last completion, no overwrite, and failed/incomplete-run rejection remain required |
| Intermediate tables/matrices | Regenerate from exact inputs/contracts/state when needed; retain accepted shared handoffs or costly/non-reconstructible evidence explicitly | Current amendment forbids copying full raw/processed datasets or training matrices into the run bundle; new handoff/matrix persistence requires explicit compatibility review |
| Human-readable reports | Retain reviewed findings, metrics, configuration-selection rationale/status, limitations, provenance and links to supporting evidence | A generated comparison is a draft until reviewed; a validation report does not imply final evaluation |

Any future Phase 6 selective-retention policy must preserve its approved replay coverage. Phase 5 continues to retain and replay every successful learned fit. Metrics/configuration/prediction evidence can be retained independently of candidate binaries; dropping a binary never justifies dropping its comparison evidence. This storage policy defines no new selection rule; training grids, model roles, scoring, ranking and human freeze rules remain unchanged. Numerical reproduction by rerunning training is an experiment and still requires specific authorization; regenerability is not permission to train.

## Version, completion and archival discipline

Each run must identify its source/view, feature contract, preprocessing representation, protocol, configuration, software environment and artifact schema. Exact identifiers/hashes and authorized scope must connect retained data, models, metrics, predictions and report references. Schema/path changes must be reviewed and versioned; this document assigns no replacement protocol/schema number.

Phase 5 manifest contract version 2 (`manifest_version: 2`) records explicit
`artifacts`, `models` and `reports` owners, repository-relative file paths and
SHA-256 hashes across the exact run-owned evidence set. The sole completion
authority is `artifacts/forecasting/<run_id>/run_manifest.json`, written last after
scientific reconciliation, all-model replay, log closure and final metadata.
It covers every persisted model/descriptor, preprocessing state, replay inputs
and `reports/forecasting/drafts/<run_id>/comparison.md` alongside machine evidence;
it does not hash itself. Missing, extra, corrupted, redirected, cross-run or
unfinished evidence blocks completion.

Model descriptor contract version 2 (`descriptor_version: 2`) uses
repository-relative references into the same `models/forecasting/<run_id>/`, with
source provenance linked back to artifact-side metadata. Candidate/fold ownership
and hashes are verified. The fitted preprocessing state format and native model
formats remain unchanged; version-1 compatibility/migration is not implemented.
Metadata receipts and generated reports do not establish completion or human
review. `data/processed/...` ownership and
`data/processed/forecasting/validation_authorization.json` remain unchanged.

Do not delete files from a completed manifest or rewrite it to hide pruning. Under a future selective policy, temporary candidates should be excluded from the final completed retention set only after approved verification and selection rules are satisfied. Historical all-fit bundles remain immutable; any approved archival conversion needs a separate derivative manifest identifying its parent and omissions, without pretending to be the original verified bundle.

Archive superseded runs supporting reports, methodology revisions or audit findings with their models/state as required by their governing protocol. Retain failed/interrupted evidence needed to explain failures separately from completed research evidence. Record archive location/access, hashes, source/code/environment requirements, review status and retrieval checks. Missing historical evidence must be recorded as unavailable, not regenerated and presented as original results.

Temporary cleanup must be run-specific, reviewed and unable to remove raw inputs, retained models/state, completed evidence or unrelated files. Crash leftovers remain incomplete; their existence never establishes completion. No cleanup operation is authorized by Issue #92.

## Selective retention deferred to Phase 6

Issue #94 records [operational alignment](protocol.md#issue-94-operational-alignment--implementation-boundary)
in the protocol. [Runner operations](forecasting-runner.md) now document the implemented Phase 5 storage contract.
Section 15 adopts the agreed storage boundaries; the operational amendment specifies
candidate evidence retention, cross-location metadata/integrity, retained-model replay
and report handoff without changing scientific definitions.

Phase 5 implements the split storage architecture and preserves every successful
learned fit and all-model replay. The exact selective-retention set remains
unresolved and deferred to Phase 6. The Issue #94 follow-up conditions below retain
the earlier retention-planning requirements; Phase 5 has now implemented the path
migration and cross-location integrity portions. Documentation does not authorize
pruning or cleanup.

Before selective retention becomes executable, the separate implementation task must:

1. Record the exact retained set/version, addressing selected configuration fold models,
   all tied IDs, supportive models and audit exceptions. Selection rules remain unchanged;
   an administrative tie representative does not silently authorize deleting other ties.
2. Review/version operational metadata and manifest schemas for retained/temporary/not-retained
   candidate status and reason, policy/selection references and model/state paths/hashes.
3. Implement cross-location integrity, all-candidate scientific reconciliation and exact
   retained-model replay, keeping fit/evaluation and retained/replayed counts distinct.
4. Resolve any requested validated/engineered/matrix handoff export against the current
   no-full-dataset/training-matrix run-copy restriction and protected outcome scopes.
5. Review path migration, failure/temporary cleanup and immutability behavior with relevant
   tests, obtain implementation acceptance and new source/protocol-bound run authorization.

No current bundle cleanup, dataset migration, manifest rewriting or experiment is
approved. Historical all-fit bundles remain immutable; missing evidence is not an archive.
Final refit/preprocessing, reserved final-evaluation authorization and downstream scientific approvals remain separate.

## Remaining human decisions

The merged policy owns architecture direction. Phase 5 implements manifest and
model descriptor contract version 2. Phase 6 selective-retention decisions, audit
exceptions, any new persisted-handoff requirements, future schema changes and
archival/backup ownership/duration still require human decisions. Implementation
acceptance and specific experiments retain their separate human authorization. Report review/publication and final-model promotion are not
implied by these storage responsibilities.
