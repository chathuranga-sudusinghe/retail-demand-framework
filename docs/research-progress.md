# Research and Project Progress Log

**Current status:** Forecasting research, retained validation and corrected final evaluation are complete; integrity verification is confirmed by Chathuranga. Constructed-origin inventory results and 20 inventory-linked records with 160 record-level checks are published. DR-012 group approval and repository status alignment are recorded under [#177](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/177); Chathuranga reported the approval for 12 October. Entries below are dated history; methods/results remain in their canonical documents, including the [final evaluation](forecasting-final-evaluation.md).

## Purpose and boundaries

Maintain a lightweight chronological record of material research discussions, member changes, implementation milestones, Issue/Pull Request progress, experiment/validation events, blockers and next actions. Record what happened and link the evidence; do not make this a second source of research decisions or an automatically generated activity feed.

[Meeting records](meetings/README.md) own meeting details. [Decision Records](decisions/README.md) own formal decisions/rationale and approval status. [Research briefs](research/) retain component research discussion, [collaboration workflow](../CONTRIBUTING.md) owns contribution/review procedure, [reports](../reports/README.md) own reviewed findings, and [final results and limitations](forecasting-final-evaluation.md#9-limitations) owns forecasting historical boundaries. Issue #92's [lifecycle](workflows/shared-data-foundation.md) and [storage policy](artifact-storage-policy.md) remain authoritative. Entries link those records rather than copying them.

## Recording rules

- Add a concise entry after a material event; the contributor closest to the work drafts it and the relevant component member checks factual/approval claims. Chathuranga coordinates completeness without replacing component ownership.
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

> **Correction recorded — 2026-10-15, Issue #165:** Actor wording in the earlier entries below was clarified on 2026-10-14, replacing generic “owner” references with Chathuranga where the recorded instruction, execution or approval was his. The event dates, run identities, outcomes and approval scope are preserved; literal retained metadata remains quoted with context. These terminology edits are not new events or group/lecturer approvals. Statements such as “uncommitted” continue to describe their original event dates.

## Chronological entries

### 2026-10-02 — Retained forecasting validation completion

- Recorded retrospectively: 2026-10-03; component owner: Chathuranga.
- Type/status: validation event; retained manifest records `verified_completed` for `validation-20261002-01`, completed at `2026-10-02T17:38:14.247307+00:00`.
- Evidence: [exact completion manifest](../artifacts/forecasting/validation-20261002-01/run_manifest.json); [DR-014 evidence identity and manifest SHA-256](decisions/DR-014-forecasting-selection-and-final-refit.md#context-and-evidence-binding). PR #133 records successful verification of 1,216 evaluations, 304,000 predictions, 304 configuration summaries and 1,184 model replays. This entry performs no new verification or validation run.
- Approval reference: retained run metadata records "Owner explicit validation-run authorization, 2026-10-02" (literal metadata wording referring to Chathuranga's instruction, not a project role); permission and verified completion are separate evidence.

### 2026-10-03 — Final runtime merged and explicitly accepted

- Recorded: 2026-10-03; component owner: Chathuranga.
- Type/status: implementation milestone; [PR #133](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/133) merged Phase 1 at `2026-10-03T07:52:20Z`. Its recorded checks include 75 focused synthetic tests, 1,061 full-suite tests, Ruff, MyPy, dependency consistency and diff checks, plus completed-validation verification.
- Scientific approval: Chathuranga approved DR-014 scope/refit policy and Documentation Step 1 under Issue #130; configurations and the separate producer mapping remain unchanged.
- Implementation acceptance: Chathuranga's explicit Issue #131 instruction in the conversation between Chathuranga and the AI assistant accepts the merged runtime and its recorded evidence as conforming to DR-014. [DR-014 subsequent-review provenance](decisions/DR-014-forecasting-selection-and-final-refit.md) records that reference; this is implementation readiness only, not final-run authorization. No GitHub approval comment or additional lecturer/group approval is asserted.
- Blocker/next action: review the [Issue #131](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/131) documentation/status corrections, then separately proceed with historical-only preflight. Exact one-time final-run authorization remains pending; no real authorization record or final-run bindings are created/frozen by this update, no reserved outcomes are accessed, and final evaluation has not been executed.

### 2026-10-03 — Historical-only final-evaluation preflight completed

- Recorded: 2026-10-03; component owner: Chathuranga.
- Type/status: preflight milestone; completed successfully with outcome `READY FOR AUTHORIZATION PREPARATION`.
- Evidence: the read-only [Issue #131](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/131) preflight result in the conversation between Chathuranga and the AI assistant, subsequently confirmed by Chathuranga's explicit status-update instruction. The checkout was clean at [PR #139](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/139) merge commit `13e11d6648f56e5f5140950896f0f8c29a4d557f`.
- Checks: retained `validation-20261002-01` verification passed; environment/dependencies matched; proposed final-run storage was unused; historical eligibility, origin and baseline checks passed. The frozen 28-candidate scope and [DR-014 producer mapping](decisions/DR-014-forecasting-selection-and-final-refit.md) remained unchanged.
- Boundaries: no estimator was fitted, no reserved-final outcomes were accessed, no real `final_authorization.json` exists, no final-run bindings are frozen, and final evaluation has not been executed. This milestone is not one-time final-run authorization.
- Next action: review and merge this preflight-status update before recalculating exact final-run authorization bindings. Proposed run ID `final-20261003-01` remains unauthorized; exact one-time final-run authorization is still pending.

### 2026-10-03 — First final execution failed; replay defect corrected

- Recorded: 2026-10-03; component owner: Chathuranga.
- Type/status: final execution and implementation correction; `final-20261003-01` remains `failed`, with no completion manifest.
- Event/outcome: Chathuranga ran the frozen 28 evaluations once; reserved outcomes were accessed. Final integrity verification failed because of a verified replay implementation defect.
- Evidence: Issue #131 execution/error report supplied by Chathuranga; retained [diagnostics](../artifacts/forecasting/final-20261003-01/diagnostics.json); [PR #141](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/141). The read-only investigation found exact replay of all twenty saved learned models with matching layout and reconciliation of all 28 retained metric records.
- Boundaries: preserve the failed artifact/model/draft bundle exactly. This entry claims no completed final run, recovery promotion or newly executed experiment.

### 2026-10-03 — Defect-correction rerun explicitly authorized

- Recorded: 2026-10-03; component owner: Chathuranga.
- Type/status: execution-governance decision by Chathuranga; exact run `final-20261003-02` explicitly authorized, not yet executed.
- Approval reference: Chathuranga's Issue #131 instruction in the conversation between Chathuranga and the AI assistant beginning "Yes. Explicitly authorize the corrected final evaluation rerun", followed by approval to implement the scoped changes on `research/issue-131-corrected-final-run`. See [DR-014 approval provenance](decisions/DR-014-forecasting-selection-and-final-refit.md).
- Decision: a corrected rerun caused solely by a verified implementation/execution defect may proceed after its fix, with unchanged scientific scope, a new explicitly approved ID and unused storage. Result-driven retries, search, retuning, reselection, substitution and methodology changes remain prohibited.
- Controls: source/Git/implementation hashes record provenance only; scientific-document, data, scope, pinned-runtime, predict-before-reveal, artifact-integrity and overwrite safeguards remain enforced.
- Next action: review the revised controls, documentation and local authorization, then Chathuranga manually executes the corrected run. Preserve/disclose the first failed execution and prior outcome exposure; downstream and research-report acceptance remain separate.

### 2026-10-03 — Corrected final evaluation completed

- Recorded retrospectively: 2026-10-04; component owner: Chathuranga.
- Type/status: forecasting completion milestone; Chathuranga confirms preparation/development, validation, freeze, final evaluation and final integrity verification are complete.
- Evidence: [validation comparison](../reports/forecasting/validation-20261002-01/comparison.md), [final-20261003-02 comparison](../reports/forecasting/final-20261003-02/comparison.md), [DR-014](decisions/DR-014-forecasting-selection-and-final-refit.md).
- Authority: explicit instructions from Chathuranga supplied for Issue #131 final repository refinement; no new experiment, ignored-outcome access or bundle verification is performed by this entry.
- Boundaries: corrected final scope and producer mapping stayed frozen; first-run outcome exposure remains disclosed. Downstream and prospective handoff decisions stay separate.

### 2026-10-04 — Final documentation consolidation prepared for review

- Type/status: documentation maintenance under Issue #131; uncommitted review draft.
- Outcome: canonical methods/features/operations/results/storage and contribution ownership consolidated; redundant temporary guides retired after preserving material caveats and contributor guidance.
- Evidence: [final report](forecasting-final-evaluation.md), [protocol](protocol.md), [feature contract](forecasting-feature-engineering.md), [runner](forecasting-runner.md), [CONTRIBUTING](../CONTRIBUTING.md).
- Review/next action: review by Chathuranga of the documentation and compatibility-check handoff before any commit/push. No scientific decision, execution or Git finalization is authorized by this entry.

### 2026-10-08 — University AI-use guidance documented for review

- Type/status: documentation under [Issue #155](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/155); uncommitted human-review draft coordinated by Chathuranga.
- Evidence: [university AI-use note](university-ai-guidance.md) records the first-semester declaration, 2025/26 handbook, inspected 9 September 2026 website update, access date, file identities and verification limits. Original documents remain local/ignored; the supplied declaration was copied without changing its bytes, and the existing handbook copy matches the supplied file.
- Boundaries: COMP1884 tier, permitted activities and applicable acknowledgement format remain unconfirmed; no research methodology, component ownership, experiment permission or Git finalisation is approved by this note.
- Next action: human review of the source summary and references, followed by assessment/cohort-specific confirmation of applicable AI guidance. No commit, push or Pull Request has been performed.


### 2026-10-12 — Inventory method approved in group discussion (reported retrospectively)

- Recorded: 2026-10-23; reporting member: Chathuranga.
- Type/status: reported group methodology decision. Chathuranga confirmed that the group approved the discussed DR-012 fixed-origin/no-receipt exposure method in its Monday WhatsApp discussion.
- Evidence: his explicit working-conversation instruction recorded in [Issue #177](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/177) and the [DR-012 approval record](decisions/DR-012-inventory-risk-replenishment-methodology.md#group-approval-record). The private discussion was not independently inspected.
- Boundary: record the approval without rewriting original run labels or inferring additional 28-day inventory, replenishment, uncertainty, source-timing or research-run approval.

### 2026-10-23 — Downstream evidence published; repository status refinement prepared

- Recorded: 2026-10-23; coordinator: Chathuranga; AI-assisted implementation/documentation prepared under #177.
- Delivered evidence: [PR #174](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/174) merged the inventory mapping/runner, human-run constructed-origin results and linked records. [PR #175](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/175) merged the completed record-level assessment and closed #164/#168 as evidence milestones. Chathuranga remains the recorded executor/assessor; component responsibilities are unchanged.
- CI: [PR #176](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/176) merged documentation/report change-scope optimisation. The two main-branch CI runs at baseline `33b4492` completed successfully; these checks cover that baseline. Validation of the #177 changes must be assessed separately through their own checks and human review.
- Current changes: align stale current documentation and approval labels; retain historical proposed-status bundle consumption without changing calculations or evidence bytes. No research execution or Git finalisation occurs in this refinement.
- Next action: review the refinement and its checks, then a human opens/merges the PR. Inspect the resulting baseline before publishing the [next member-owned issue scopes](integration-contract-readiness.md#13-remaining-work-handoff-after-issue-177).


### 2026-10-29 — C1 scope decisions recorded; request-time handoff accepted

- Recorded retrospectively: 2026-11-05; reporting/forecasting member: Chathuranga.
- The [C1 scope record](research-design.md#164-human-decisions-and-c1-closeout-record) records team acceptance reported on 29 October of the bounded descriptive conclusion and five disclosed limitations/deferred extensions. B8/B10/B11/B12 are resolved for current scope through approved deferral; unavailable methods are not silently implemented.
- [#203 producer/source acceptance](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/203#issuecomment-6501737406) accepts the scoped request-time handoff; retained-export and component acceptance remain separate.

### 2026-10-30 — C1 research closure

- Recorded retrospectively: 2026-11-05; coordinated by Chathuranga.
- [#191 closed](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/191#issuecomment-6515040267) on the accepted descriptive scope. Significance remains untested; this closes neither final prototype acceptance nor #179.

### 2026-11-01 — Dewmi’s direct W1 acceptance

- Recorded retrospectively: 2026-11-05; responsible-use reviewer: Dewmi.
- [Dewmi accepted the interpretation/display baseline](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/182#issuecomment-6555332904) and supported automatic managerial-review triggers only as a possible deferred extension. Reuse that W1 decision and the completed 160 checks; W2 remains a distinct actual-interface review under #182.

### 2026-11-02 — Multi-horizon worked scenario delivered

- Recorded retrospectively: 2026-11-05; executor/forecasting member: Chathuranga.
- [PR #215](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/215) merged the #214 scenario implementation and documented human execution at `ae6905cd971f4e7a3a21d04d1b37744dc08bd83b`. The [worked example](worked-example-scenario.md#9-recorded-human-execution--2-november-2026) retains the exact trace and interpretation; no replay or metric recalculation is performed here.
- [#179’s delivery update](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/179#issuecomment-6584118919) preserves outstanding human review and component-acceptance boundaries. Delivery is not a new approval of inventory methods or evidence of managerial effectiveness.

### 2026-11-05 — Meeting evidence delivered; current-state reconciliation prepared

- [PR #216](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/216) merged the dated discussion/meeting records at `e17f6961db64ba70f80a30a65447c8b03c5b077b`. [Meeting records](meetings/README.md) distinguish original messages from Chathuranga’s later lecturer/attendance clarifications.
- Chathuranga explicitly approved documentation reconciliation of accepted deferrals, W1, current review tracking and supplied assessment requirements in the working conversation on 5 November 2026. This entry records that instruction and the resulting documentation; it does not supply a new component approval or peer-review decision.
- PNG regeneration, renderer changes and PNG-delivery status updates are explicitly excluded from this pass. Original evidence, numerical results and frozen producers are unchanged. #179 and outstanding retained/component acceptance remain separate from later submission preparation under #204.

- Assessment-source reconciliation on 5 November also incorporates all seven supplied 2026/27 COMP1884 specifications, templates and process documents. The [criteria checklist](greenwich-criteria-checklist.md), [AI-use note](university-ai-guidance.md) and [references](references.md#university--project-guidance) replace older provisional/website-only assessment mappings with the supplied sources. Report/presentation rubrics and acknowledged AI support are documented. Chathuranga subsequently confirmed continued Tier 2 application on 5 November and instructed use of the supplied student AI/AIR and GenAI referencing PDFs; the AI-use note and checklist record those sources and required AIR placement. Official deadlines remain TBA. The new research-design source check finds no explicit formal hypothesis-testing requirement and preserves the existing accepted descriptive scope. No submission files are assembled in this reconciliation.

- Following an AI-assisted repository inspection reported on 5 November 2026, Chathuranga authorised the suitable remaining corrections on this branch while explicitly ruling out model training. The CI description now matches the shared scope detector; Dewmi’s overview links her direct scoped W1 acceptance, and conceptual field labels point to the implemented record. A missing runtime package now raises a named `ExecutionBlocked` error, with synthetic regression tests. This records implementation scope, not a model/research rerun or completed peer approval. PNG/renderer work remains postponed.
