# Artifact and Storage Policy — Issue #92

**Status:** Merged Issue #92 storage authority; Issue #94 operational reconciliation remains subject to human review.
**Scope:** Repository-wide storage responsibilities, evidence retention and provenance. This document does not change scientific methodology, grant experiment approval, authorize cleanup or migration, or independently amend the frozen protocol. Issue #94 records operational alignment in the protocol; scientific settings remain frozen.
**Related issue:** [#92 — Define data lifecycle and artifact storage policy](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/92).

## Authority and current implementation

The [shared data workflow](workflows/shared-data-foundation.md#issue-92--data-lifecycle-and-representation-contracts) owns representation stages. The [dataset contract](dataset.md), especially Sections 7/8, owns source meaning, field roles, quality, processed-layer intent and member-specific needs. The [feature contract](forecasting-feature-engineering.md) owns predictors, formulas, leakage controls, preprocessing semantics and model inputs. The [protocol](protocol.md) owns chronological windows, eligibility, metrics, selection, execution gates and experiment requirements. [Runner operations](forecasting-runner.md) own execution/orchestration and current persistence behavior. [Methodology revision](forecasting-methodology-revision.md) owns current-versus-historical methodology and provenance. The [research design](research-design.md) and [decision records](decisions/README.md) retain their existing research authority. This policy owns storage/retention only.

The repository currently contains local raw data, processed EDA/profile tables and a local execution record. artifacts/ exists and is empty; a root models/ directory is not yet present. The former outputs/ directory was intentionally removed. No artifact archive is inferred from that removal, and previous results must not be described as available without locating their evidence. Historical methods and results keep the classification in the methodology revision record; this storage policy neither relabels them as current evidence nor rewrites their scientific history.

The locations below are the approved target architecture, not implemented paths. Do not recreate outputs/. Issue #94 aligns protocol Section 15 and runner documentation with this policy while explicitly describing legacy runtime behavior. Unchanged paths.py still targets the removed location; executing unchanged code would recreate it. Execution must wait for separately reviewed migration and new matching authorization.

## Storage responsibilities

| Location | What belongs here | Persistence and retention boundary |
|---|---|---|
| data/raw/ | Original local source snapshots | Immutable reproduction input; retain locally or archive with source identity, hash and retrieval location. Never overwrite the only source of reported evidence |
| data/processed/validated/<data_version>/ | Accepted typed/sorted native records and associated quality audits | Shared validated handoff; regenerable only from exact retained parents/rules/code. No invented repair policy |
| data/processed/interim/<preparation_id>/ | Intermediate preparation tables and diagnostic scratch data | Temporary/regenerable; no authoritative model or research result lives only here |
| data/processed/model-ready/<representation_id>/ | Accepted engineered feature tables, separate authorized target tables, view membership/specifications; optional explicitly identified fitted matrices | Versioned, keyed handoffs; distinguish conceptual features from fold/horizon-specific fitted representations. Matrix persistence remains subject to the protocol boundary below |
| models/forecasting/<run_id>/ | Retained estimator binaries, descriptors, fitted preprocessing and small replay inputs | Model-only persistence authority; retain exact state with each retained estimator. Validation candidates remain labelled validation; final models require separate Gate 6 approval |
| artifacts/forecasting/<run_id>/ | Run metadata, retained authorization, candidate configuration/metric evidence, predictions, eligibility evidence, logs, diagnostics, integrity manifest | Machine-readable experiment evidence; completed bundles are immutable. Refer to model/data locations by explicit confined references and hashes rather than copying binaries/datasets |
| artifacts/authorizations/forecasting/ | Reviewed execution control records for future runs | Approved architecture home for control information; migration pending, separate from scientific datasets. Existing data/processed/forecasting/validation_authorization.json remains untouched pending approved migration |
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

| Item | Architecture retention policy | Current implementation / approval condition |
|---|---|---|
| Source identity and reproducibility inputs | Retain source citation, exact snapshot identity/hash/size, scoped input fingerprints, code commit/source hashes, environment and contract/protocol versions; retain source bytes or verified retrievable archive | Whole-file identity and authorized-view fingerprints have different purposes. Do not inspect protected final outcomes merely to expand provenance |
| Candidate configurations and metrics | Retain every evaluated configuration's canonical/requested/effective settings, role, fold/horizon, metrics/status/reasons, counts and selection evidence, including unsuccessful candidates | Never prune comparison evidence merely because its estimator is unselected |
| Predictions | Retain complete keyed prediction evidence required to reconcile the run and report; preserve origin, interval, horizon, configuration, stage, actuals/errors and unavailable status | Current protocol requires all candidate prediction records; selected-only prediction retention is not approved here. Keep retrospective actuals separate from prospective handoffs |
| Eligibility and chronological views | Retain population hashes, boundaries, membership/exclusion evidence and reasons; view copies are regenerable when exact parents remain available | No random split, altered eligibility or new final-period access |
| Selected validation models | Retain reusable selected estimator bundles according to the later human-approved retention set, with exact fitted state and replay evidence. The amendment must settle fold-model, tie, supportive and audit coverage | Selection follows the protocol, not this policy. Administrative leaders are not human-frozen final models. Legacy compatibility requirement retains ALL successful learned fits until accepted migration |
| Fitted preprocessing and replay inputs | Retain exact vocabulary, numerical scaling, physical/conceptual order, state version, training population/fold/horizon and reference prediction inputs with each retained model; share immutable state only through verified references | Reload never refits categories/scaling or substitutes a different fold's state. Baselines need formula/history provenance, not estimator binaries |
| Unselected candidate binaries | Under an approved exact selective-retention set: temporary during fitting/selection/verification; avoid indefinite retention when complete configuration/metric/prediction evidence is sufficient. Keep only approved audit exceptions | Not currently disposable: all-fit persistence and replay remain operative until exact retention-set approval and implementation acceptance |
| Final models | Retain approved final estimator/preprocessor bundles with training population, selection-freeze and final-run authorization references | Final fitting/evaluation remains blocked under Gate 6; no reuse of a fold model as an approved final model |
| Manifests and logs | Retain authorization, run metadata, completion manifest, finalized run log and integrity outcomes; retain failure diagnostics for investigated runs with explicit failure status | Manifest-last completion, no overwrite, and failed/incomplete-run rejection remain required |
| Intermediate tables/matrices | Regenerate from exact inputs/contracts/state when needed; retain accepted shared handoffs or costly/non-reconstructible evidence explicitly | Current amendment forbids copying full raw/processed datasets or training matrices into the run bundle; new handoff/matrix persistence requires explicit compatibility review |
| Human-readable reports | Retain reviewed findings, metrics, configuration-selection rationale/status, limitations, provenance and links to supporting evidence | A generated comparison is a draft until reviewed; a validation report does not imply final evaluation |

Selective retention must preserve the replay coverage approved for retained models without retaining every grid candidate indefinitely. Metrics/configuration/prediction evidence can be retained independently of candidate binaries; dropping a binary never justifies dropping its comparison evidence. This storage policy defines no new selection rule; training grids, model roles, scoring, ranking and human freeze rules remain unchanged. Numerical reproduction by rerunning training is an experiment and still requires specific authorization; regenerability is not permission to train.

## Version, completion and archival discipline

Each run must identify its source/view, feature contract, preprocessing representation, protocol, configuration, software environment and artifact schema. Exact identifiers/hashes and authorized scope must connect retained data, models, metrics, predictions and report references. Schema/path changes must be reviewed and versioned; this document assigns no replacement protocol/schema number.

Completion must be published only after scientific evidence reconciliation and the required retained-model replay succeed. A future manifest must cover files in the evidence bundle plus explicitly linked data/model evidence, with allowed-root containment and hashes; current verification assumes a single run directory and does not yet support this layout.

Do not delete files from a completed manifest or rewrite it to hide pruning. Under a future selective policy, temporary candidates should be excluded from the final completed retention set only after approved verification and selection rules are satisfied. Historical all-fit bundles remain immutable; any approved archival conversion needs a separate derivative manifest identifying its parent and omissions, without pretending to be the original verified bundle.

Archive superseded runs supporting reports, methodology revisions or audit findings with their models/state as required by their governing protocol. Retain failed/interrupted evidence needed to explain failures separately from completed research evidence. Record archive location/access, hashes, source/code/environment requirements, review status and retrieval checks. Missing historical evidence must be recorded as unavailable, not regenerated and presented as original results.

Temporary cleanup must be run-specific, reviewed and unable to remove raw inputs, retained models/state, completed evidence or unrelated files. Crash leftovers remain incomplete; their existence never establishes completion. No cleanup operation is authorized by Issue #92.

## Required protocol amendment before selective retention

Issue #94 records [operational alignment](protocol.md#issue-94-operational-alignment--implementation-boundary)
in the protocol and distinguishes it from unchanged [runner behavior](forecasting-runner.md).
Section 15 adopts the agreed storage boundaries; the operational amendment specifies
candidate evidence retention, cross-location metadata/integrity, retained-model replay
and report handoff without changing scientific definitions.

The conflict remains at the implementation boundary: the accepted legacy Issue #89
contract and integrity.verify_scientific require every successful learned fit and
replay all saved models. All-fit persistence remains the compatibility requirement
until a precisely enumerated human-approved retention set and implementation are
accepted. Documentation reconciliation does not authorize pruning.

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
Final refit/preprocessing, Gate 6 and downstream scientific approvals remain separate.

## Remaining human decisions

The merged policy owns architecture direction. The exact retention set/audit exceptions,
persisted handoff requirements, serialization/schema versions, archival/backup ownership
and duration still require human decisions. Issue #94 reconciliation requires human
review; runtime migration, implementation acceptance and specific experiments require
separate authorization. Report review/publication and final-model promotion are not
implied by these storage responsibilities.
