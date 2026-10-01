# Research and Project Progress Log

**Status:** Issue #93 logging-format draft for human review. No historical events or approvals have been added.

## Purpose and boundaries

Maintain a lightweight chronological record of material research discussions, member changes, implementation milestones, Issue/Pull Request progress, experiment/validation events, blockers and next actions. Record what happened and link the evidence; do not make this a second source of research decisions or an automatically generated activity feed.

[Meeting records](meetings/README.md) own meeting details. [Decision Records](decisions/README.md) own formal decisions/rationale and approval status. [Research briefs](research/) retain component research discussion, [collaboration workflow](collaboration-workflow.md) owns contribution/review procedure, [reports](../reports/README.md) own reviewed findings, and [methodology revision](forecasting-methodology-revision.md) owns forecasting historical boundaries. Issue #92's [lifecycle](workflows/shared-data-foundation.md) and [storage policy](artifact-storage-policy.md) remain authoritative. Entries link those records rather than copying them.

## Recording rules

- Add a concise entry after a material event; the contributor closest to the work drafts it and the relevant owner checks factual/approval claims. Chathuranga coordinates completeness without replacing component ownership.
- Order entries by event date, oldest first. Use YYYY-MM-DD; include time/timezone when needed for ordering or cross-region events. Record the entry date separately when written later; mark an uncertain event date as unknown rather than inventing one.
- Record discussions/proposals as such. Distinguish implemented, validated, reviewed, approved, merged and blocked states using evidence. A planned fit budget is not an executed experiment; a passing test is not a research result or approval.
- Cite the Issue/PR URL, meeting, Decision Record, report or exact run/completion evidence supporting the entry. Human approval claims need the actual approving reference; an AI summary or this log alone cannot authorize anything.
- Record member/role changes only with explicit human approval and link the governing membership/ownership update. Do not silently alter component responsibilities.
- For experiments, record exact run ID/stage, authorization reference, completion/failure status and evidence/report links. Do not insert dataset records, credentials, full logs or model payloads. Execution remains subject to protocol gates.
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

No event entries are recorded in this draft. Populate only with verified events and explicit evidence through the normal human review workflow. Creating this format does not approve a member change, research decision, experiment or Git operation.
