# Research and Project Progress Log

**Current status:** Forecasting research, retained validation and corrected final evaluation are complete; integrity verification is confirmed by the owner. Entries below are dated administrative history, not current execution instructions or a second methods/results authority. Current interpretation is in [final evaluation](forecasting-final-evaluation.md).

## Purpose and boundaries

Maintain a lightweight chronological record of material research discussions, member changes, implementation milestones, Issue/Pull Request progress, experiment/validation events, blockers and next actions. Record what happened and link the evidence; do not make this a second source of research decisions or an automatically generated activity feed.

[Meeting records](meetings/README.md) own meeting details. [Decision Records](decisions/README.md) own formal decisions/rationale and approval status. [Research briefs](research/) retain component research discussion, [collaboration workflow](../CONTRIBUTING.md) owns contribution/review procedure, [reports](../reports/README.md) own reviewed findings, and [final results and limitations](forecasting-final-evaluation.md#9-limitations) owns forecasting historical boundaries. Issue #92's [lifecycle](workflows/shared-data-foundation.md) and [storage policy](artifact-storage-policy.md) remain authoritative. Entries link those records rather than copying them.

## Recording rules

- Add a concise entry after a material event; the contributor closest to the work drafts it and the relevant owner checks factual/approval claims. Chathuranga coordinates completeness without replacing component ownership.
- Order entries by event date, oldest first. Use YYYY-MM-DD; include time/timezone when needed for ordering or cross-region events. Record the entry date separately when written later; mark an uncertain event date as unknown rather than inventing one.
- Record discussions/proposals as such. Distinguish implemented, validated, reviewed, approved, merged and blocked states using evidence. A planned fit budget is not an executed experiment; a passing test is not a research result or approval.
- Cite the Issue/PR URL, meeting, Decision Record, report or exact run/completion evidence supporting the entry. Human approval claims need the actual approving reference; an AI summary or this log alone cannot authorize anything.
- Record member/role changes only with explicit human approval and link the governing membership/ownership update. Do not silently alter component responsibilities.
- For experiments, record exact run ID/stage, authorization reference, completion/failure status and evidence/report links. Do not insert dataset records, credentials, full logs or model payloads. Execution remains subject to the protocol’s specific run authorization requirements.
- Backfill history only from explicit evidence. Distinguish retrospective recording from a contemporaneous entry; identify gaps without reconstructing undocumented discussions. Do not backdate later decisions into earlier meetings.
- Correct factual mistakes with a dated correction linked to the affected entry; keep the earlier record traceable. Later status changes receive a new dated update rather than silently rewriting history.

A milestone entry should be a few lines. Detailed discussion belongs in the linked authoritative record; routine commits/checks need entries only when they establish a material milestone, blocker or decision dependency.

## Entry format

The following is a template, not an event:

~~~markdown
### <event-date> — <short event title>

- Recorded: <entry-date>; contributor/component owner: <name or pending>.
- Type/status: <discussion/member change/milestone/Issue-PR/experiment/blocker>; <evidence-supported status>.
- Event/outcome: <brief factual account; distinguish proposal from approval>.
- Evidence: <links to actual Issue/PR/meeting/Decision Record/report/run records>.
- Approval/review: <actual human reference, pending, or not applicable>.
- Blocker/next action: <action and owner; due date only if agreed>.
~~~

## Chronological entries

### 2026-10-02 — Retained forecasting validation completion

- Recorded retrospectively: 2026-10-03; component owner: Chathuranga.
- Type/status: validation event; retained manifest records `verified_completed` for `validation-20261002-01`, completed at `2026-10-02T17:38:14.247307+00:00`.
- Evidence: [exact completion manifest](../artifacts/forecasting/validation-20261002-01/run_manifest.json); [DR-014 evidence identity and manifest SHA-256](decisions/DR-014-forecasting-selection-and-final-refit.md#context-and-evidence-binding). PR #133 records successful verification of 1,216 evaluations, 304,000 predictions, 304 configuration summaries and 1,184 model replays. This entry performs no new verification or validation run.
- Approval reference: retained run metadata records "Owner explicit validation-run authorization, 2026-10-02"; permission and verified completion are separate evidence.

### 2026-10-03 — Final runtime merged and explicitly accepted

- Recorded: 2026-10-03; component owner: Chathuranga.
- Type/status: implementation milestone; [PR #133](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/133) merged Phase 1 at `2026-10-03T07:52:20Z`. Its recorded checks include 75 focused synthetic tests, 1,061 full-suite tests, Ruff, MyPy, dependency consistency and diff checks, plus completed-validation verification.
- Scientific approval: the owner approved DR-014 scope/refit policy and Documentation Step 1 under Issue #130; configurations and the separate producer mapping remain unchanged.
- Implementation acceptance: the owner's explicit Issue #131 instruction in the owner-agent conversation accepts the merged runtime and its recorded evidence as conforming to DR-014. [DR-014 subsequent-review provenance](decisions/DR-014-forecasting-selection-and-final-refit.md) records that reference; this is implementation readiness only, not final-run authorization. No GitHub approval comment or additional supervisor/group approval is asserted.
- Blocker/next action: review the [Issue #131](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/131) documentation/status corrections, then separately proceed with historical-only preflight. Exact one-time final-run authorization remains pending; no real authorization record or final-run bindings are created/frozen by this update, no reserved outcomes are accessed, and final evaluation has not been executed.

### 2026-10-03 — Historical-only final-evaluation preflight completed

- Recorded: 2026-10-03; component owner: Chathuranga.
- Type/status: preflight milestone; completed successfully with outcome `READY FOR AUTHORIZATION PREPARATION`.
- Evidence: the read-only [Issue #131](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/131) preflight result in the owner-agent conversation, subsequently confirmed by the owner's explicit status-update instruction. The checkout was clean at [PR #139](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/139) merge commit `13e11d6648f56e5f5140950896f0f8c29a4d557f`.
- Checks: retained `validation-20261002-01` verification passed; environment/dependencies matched; proposed final-run storage was unused; historical eligibility, origin and baseline checks passed. The frozen 28-candidate scope and [DR-014 producer mapping](decisions/DR-014-forecasting-selection-and-final-refit.md) remained unchanged.
- Boundaries: no estimator was fitted, no reserved-final outcomes were accessed, no real `final_authorization.json` exists, no final-run bindings are frozen, and final evaluation has not been executed. This milestone is not one-time final-run authorization.
- Next action: review and merge this preflight-status update before recalculating exact final-run authorization bindings. Proposed run ID `final-20261003-01` remains unauthorized; exact one-time final-run authorization is still pending.

### 2026-10-03 — First final execution failed; replay defect corrected

- Recorded: 2026-10-03; component owner: Chathuranga.
- Type/status: final execution and implementation correction; `final-20261003-01` remains `failed`, with no completion manifest.
- Event/outcome: the owner ran the frozen 28 evaluations once; reserved outcomes were accessed. Final integrity verification failed because of a verified replay implementation defect.
- Evidence: owner-supplied Issue #131 execution/error report; retained [diagnostics](../artifacts/forecasting/final-20261003-01/diagnostics.json); [PR #141](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/141). The read-only investigation found exact replay of all twenty saved learned models with matching layout and reconciliation of all 28 retained metric records.
- Boundaries: preserve the failed artifact/model/draft bundle exactly. This entry claims no completed final run, recovery promotion or newly executed experiment.

### 2026-10-03 — Defect-correction rerun explicitly authorized

- Recorded: 2026-10-03; component owner: Chathuranga.
- Type/status: owner execution-governance decision; exact run `final-20261003-02` explicitly authorized, not yet executed.
- Approval reference: the owner's Issue #131 instruction in the owner-agent conversation beginning "Yes. Explicitly authorize the corrected final evaluation rerun", followed by approval to implement the scoped changes on `research/issue-131-corrected-final-run`. See [DR-014 approval provenance](decisions/DR-014-forecasting-selection-and-final-refit.md).
- Decision: a corrected rerun caused solely by a verified implementation/execution defect may proceed after its fix, with unchanged scientific scope, a new explicitly approved ID and unused storage. Result-driven retries, search, retuning, reselection, substitution and methodology changes remain prohibited.
- Controls: source/Git/implementation hashes record provenance only; scientific-document, data, scope, pinned-runtime, predict-before-reveal, artifact-integrity and overwrite safeguards remain enforced.
- Next action: review the revised controls, documentation and local authorization, then the owner manually executes the corrected run. Preserve/disclose the first failed execution and prior outcome exposure; downstream and research-report acceptance remain separate.

### 2026-10-03 — Corrected final evaluation completed

- Recorded retrospectively: 2026-10-04; component owner: Chathuranga.
- Type/status: forecasting completion milestone; the owner confirms preparation/development, validation, freeze, final evaluation and final integrity verification are complete.
- Evidence: [validation comparison](../reports/forecasting/validation-20261002-01/comparison.md), [final-20261003-02 comparison](../reports/forecasting/final-20261003-02/comparison.md), [DR-014](decisions/DR-014-forecasting-selection-and-final-refit.md).
- Authority: explicit owner instructions supplied for Issue #131 final repository refinement; no new experiment, ignored-outcome access or bundle verification is performed by this entry.
- Boundaries: corrected final scope and producer mapping stayed frozen; first-run outcome exposure remains disclosed. Downstream and prospective handoff decisions stay separate.

### 2026-10-04 — Final documentation consolidation prepared for review

- Type/status: documentation maintenance under Issue #131; uncommitted review draft.
- Outcome: canonical methods/features/operations/results/storage and contribution ownership consolidated; redundant temporary guides retired after preserving material caveats and contributor guidance.
- Evidence: [final report](forecasting-final-evaluation.md), [protocol](protocol.md), [feature contract](forecasting-feature-engineering.md), [runner](forecasting-runner.md), [CONTRIBUTING](../CONTRIBUTING.md).
- Review/next action: owner review of the documentation and compatibility-check handoff before any commit/push. No scientific decision, execution or Git finalization is authorized by this entry.

### 2026-10-08 — University AI-use guidance documented for review

- Type/status: documentation under [Issue #155](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/155); uncommitted human-review draft coordinated by Chathuranga.
- Evidence: [university AI-use note](university-ai-guidance.md) records the first-semester declaration, 2025/26 handbook, inspected 9 September 2026 website update, access date, file identities and verification limits. Original documents remain local/ignored; the supplied declaration was copied without changing its bytes, and the existing handbook copy matches the supplied file.
- Boundaries: COMP1884 tier, permitted activities and applicable acknowledgement format remain unconfirmed; no research methodology, component ownership, experiment permission or Git finalisation is approved by this note.
- Next action: human review of the source summary and references, followed by assessment/cohort-specific confirmation of applicable AI guidance. No commit, push or Pull Request has been performed.
