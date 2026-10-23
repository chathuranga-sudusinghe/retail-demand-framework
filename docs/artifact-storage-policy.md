# Artifact and Storage Policy

This document owns storage, immutability and retention. [Shared data foundation](workflows/shared-data-foundation.md) owns representation flow; [protocol](protocol.md) and [DR-014](decisions/DR-014-forecasting-selection-and-final-refit.md) own scientific contracts; [runner operations](forecasting-runner.md) owns execution. The retained completed validation and final runs keep their original evidence identities and byte hashes. This policy grants no cleanup or experiment authorization.

## Storage responsibilities

| Location | Content / owner |
|---|---|
| data/raw/ | Original local source and acquisition receipt; immutable reproduction input |
| data/processed/validated/<data_version>/ | Typed, ordered native records, audit/schema and provenance; validated shared handoff |
| data/processed/interim/<preparation_id>/ | Isolated preparation staging/scratch; no sole authoritative evidence |
| data/processed/model-ready/<representation_id>/ | Separate feature/target tables and explicitly identified fold/horizon fitted matrices/states |
| data/processed/forecasting/ | Reviewed validation_authorization.json and final_authorization.json control records; the approved Issue #132 handoff export is listed separately below |
| data/processed/forecasting/handoffs/final-20261003-02/issue-132-forecast-export-v1.json | Local, ignored prospective derivative export for Issue #132; Chathuranga owns forecasting meaning and export, Tinosh consumes the reviewed handoff |
| artifacts/forecasting/<run_id>/ | Machine evidence, retained authorization, metadata, logs, diagnostics, sole run_manifest.json completion authority |
| models/forecasting/<run_id>/ | Native models, descriptors, fitted preprocessing and small origin replay inputs |
| reports/forecasting/<run_id>/comparison.md | Canonical trackable generated comparison for a verified completed run |
| reports/decision-support/issue-168-json/ | Limited Git-tracked review snapshot authorised by Chathuranga on 23 October 2026: the existing 20-record records.json/records.md, partial review.json and original manifest.json, copied unchanged from the local preparation. See the [evidence index](../reports/README.md#decision-support-review-evidence). |
| reports/inventory-risk/issue-164/evaluation-v1/ | Git-tracked copy authorised by Chathuranga on 23 October 2026 of the human-run constructed-origin evaluation: prospective.json, evaluation.json, report.md and manifest.json. The 1,000-row prospective view and 750-case retrospective evaluation remain separate. |
| reports/decision-support/issue-168-inventory-v1/ | Git-tracked copy authorised by Chathuranga on 23 October 2026 of the 20 inventory-linked records: records.json, records.md, blank review.json and manifest.json. Human assessment remains pending. |
| reports/forecasting/drafts/ | Local temporary/preview/failed reports and immutable historical originals where recorded by receipts |
| docs/forecasting-final-evaluation.md | Consolidated current forecasting findings, decision and limitations |
| research-materials/inventory-risk/issue-164/; research-materials/decision-support/ | Local ignored human-run preparation and evaluation: prospective.json, evaluation.json, report.md and a last-written manifest under an exclusive evaluation directory; populated JSON/Markdown decision-support records, editable JSON checklists and summaries under separate directories. Use a new directory when inputs or formats change; do not overwrite earlier evidence. Keep retrospective fields out of the prospective handoff. These are derivative evidence, not forecasting-run artifacts or executable orders. |
| reports/figures/forecasting/<run_id>/ | Optional reviewed lightweight figures |

Descriptive tables under data/processed/demand_eda/ and temporal_profile/ remain descriptive evidence, not training datasets. No automatic latest-version discovery or silent replacement is allowed. Reuse requires matching exact parents, scope, code, contract and fitted state.

Datasets, generated data tables, binaries, machine evidence and temporary reports stay local/ignored. Preserve .gitignore protections and do not embed bulk data in reports/notebooks to bypass them. Only lightweight comparison Markdown, reviewed reports/figures, documentation, code and approved small fixtures belong in Git.

**Named review-bundle exceptions:** Chathuranga authorised tracking the twelve named files in the three report directories above so members can inspect the same forecast-only records, completed constructed-scenario evaluation and prepared inventory-linked records through GitHub. Only the named outputs are covered; the full forecast export, inventory input tables, raw/processed datasets, model bundles and other bulk outputs remain local. The generators still write exclusively under ignored `research-materials/`; no generator output path or dataset protection changes. Preserve original bytes, filenames and manifests in each copied bundle so their bindings and relative links remain intact. Preparation manifests describe initial preparation, not later checklist completion, current code verification or human peer approval. Further human assessments must be clearly attributed and reviewed as changes; changed input/evidence contexts require a separate version rather than replacing an original record bundle. Publishing the retrospective evaluation does not make observations or metrics prospective inputs: consumers continue to interpret only `prospective.json` and hash its companion files without decoding their retrospective contents.

The Issue #132 derivative location was approved by Chathuranga on 2026-10-05. Its [forecast API contract](forecast-api-contract.md) owns the prospective field allowlist, frozen producers, exact source anchors and deterministic export rules. The export stays outside retained final-run evidence and MUST NOT overwrite it or contain retrospective outcomes/errors. Record the accepted derivative SHA-256 in that contract and pin it in the API configuration; do not commit generated output. Storage approval does not authorize generating the real export, training, prediction replay or metric recalculation.

The Issue #132 writer may create ignored `.forecast-export-*` staging files beside the approved export while publishing it. These are incomplete temporary material and MUST NOT be consumed as forecasts or accepted evidence. Normal completion or handled errors remove them; a process crash can leave them behind. This allowance does not authorize automatic cleanup or overwriting an existing accepted export.

## Evidence and model retention

Retain all evaluated configurations' canonical/requested/effective settings, fold/horizon/role/status, metrics, complete keyed predictions, selection/tie evidence, eligibility reasons and population fingerprints. Preserve exact source/view identity, environment, code/contract versions, model-to-preprocessor-to-origin links and authorization references. Actuals/errors are retrospective evaluation evidence and cannot enter a prospective handoff.

The implemented validation policy saves **all 1,184 successful learned fits**, including unselected configurations and ties, with exact fitted preprocessing and replay inputs. Baselines retain formula/history evidence rather than model binaries. The completed validation includes 1,216 evaluations, 304 configuration summaries and 304,000 predictions, as recorded in the retained completion evidence; this document performs no new verification.

Final evaluation retains all twenty new learned estimators, their preprocessing, sealed predictions, observations, metrics and all 28 candidate records. The four downstream producers do not narrow the retained comparison. Validation candidates remain labelled validation and are not promoted merely by a filename or producer decision.

There is **no approved selective-pruning/expiry policy**. Do not delete unselected models, introduce an artifacts/tmp/ candidate architecture, remove failed evidence or rewrite completed receipts. Any future retention reduction needs explicit human approval, a reviewed exact retention set and verification/archival design. Source history cannot replace the only available research evidence.

## Run layout and contracts

Validation machine evidence includes run_metadata.json, fold_metrics.csv, configuration_summary.csv, selected_configurations.json, predictions.csv, eligibility_counts.csv, authorization.json, run.log and run_manifest.json. Models use:

~~~text
models/forecasting/<run_id>/
  validation/<family>/h<horizon>/<configuration>/fold-<n>/
    model.ubj | model.txt | model.cbm | model.joblib
    descriptor.json
  preprocessing/<family>/h<horizon>/fold-<n>/
    state.json
    origin_features.json
~~~

The separate final bundle uses candidates.json, predictions.json and prediction_receipt.json sealed before reveal, then observations.json and metrics.json. It retains authorization.json, freeze.md and policy.md snapshots, run_metadata.json, run.log, baseline_history.json, eligibility.json and the completion manifest. Final learned bundles use models/forecasting/<run_id>/final/<family>/h<horizon>/<configuration>/, with native models, descriptors, preprocessing and origin inputs as linked from candidate records. Consult [final_artifacts.py](../src/forecasting/final_artifacts.py) for the exact separate JSON contract, not the validation CSV schema.

Validation manifest and model descriptor contracts are version 2. Final manifest is version 2, with separate schema issue-130-final-v1; final_refit model descriptors and prediction receipts are version 1. Fitted preprocessing state remains version 1. Do not conflate these version numbers or migrate historical records while editing documentation.

## Version, completion and archival discipline

The sole completion authority is **artifacts/forecasting/<run_id>/run_manifest.json**, published last after scientific reconciliation, all-model replay, log closure and final metadata. It inventories exact repository-relative artifact/model/report paths, owners and SHA-256 hashes; it does not hash itself. Metadata receipts and comparison text alone do not establish completion or human review.

Consumers verify from the exact artifact anchor using the stage-specific verifier described in [runner operations](forecasting-runner.md#persistence-and-completion-verification). For the Issue #132 prospective derivative of the already verified `final-20261003-02` run, use the read-only pinned-hash, binding and schema checks in [forecast API contract Section 2](forecast-api-contract.md#2-source-evidence); do not repeat scientific verification, model replay or metric reconciliation. Missing, extra, redirected, corrupted, cross-run or incomplete evidence blocks consumption. Final verification reads its retained freeze.md/policy.md snapshots; current documentation consolidation must not rewrite those snapshots or historical scientific/evidence hashes.

Historical completed bundles retain their original draft report and exact receipt path. A tracked canonical comparison copy does not replace that original or refresh its manifest. Do not relabel removed/unavailable earlier evidence as retained or recreate it under an original ID.

Retain failed/interrupted runs separately from completed evidence, including the first final run's prior outcome access. Archive only as a coherent reviewed set with exact identities, hashes, retrieval location, owner, code/environment requirements and review status. No archive location or automatic cleanup is inferred. A derivative archive must identify its parent and omissions without pretending to be the original bundle.

## Retention classes and remaining decisions

Retained evidence supports inspection/reproduction; regenerable representations require exact retained parents/rules/state; temporary material has no sole evidential role; archived material remains coherent historical evidence. None of these labels independently authorizes deletion.

Human agreement remains necessary for retention duration, backup/archive destination, archive owner, capacity, cleanup process and any selective model-retention set. Crash leftovers remain incomplete. Run-specific cleanup must never remove source inputs, completed evidence or unrelated work.
