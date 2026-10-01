# Research Reports

**Status:** Merged Issue #93 reporting-contract authority. No report results or approvals are created here.

## Purpose, locations and ownership

reports/ holds human-readable research findings and approved figures under the [Issue #92 storage policy](../docs/artifact-storage-policy.md). Machine-readable run evidence and model bundles retain the responsibilities defined there; this guide does not redefine storage or change runner outputs.

For a completed forecasting experiment, use:

~~~text
reports/forecasting/<run_id>.md
reports/figures/forecasting/<run_id>/
~~~

Use the exact evidence run ID; identify validation versus final evaluation in the report. These are future report locations, not directories or reports created by this issue. Existing [demand EDA](demand-eda.md) and [temporal profile](temporal-demand-profile.md) keep their historical scope and names.

Chathuranga owns forecasting interpretation and coordinates review under the [collaboration workflow](../docs/collaboration-workflow.md). Component owners review any statements about their analytical area; report authors and technical renderers do not acquire another member's ownership. Publication/commits follow existing human approval rules.

## Generated evidence versus reviewed interpretation

Generated metrics, predictions, metadata, selection records and comparisons are evidence, not human acceptance of findings. Consume completed bundles through the verification requirements in [runner operations](../docs/forecasting-runner.md); missing/failed/incomplete evidence cannot support a completed-experiment claim.

A generated narrative is a draft. Label report review status explicitly as draft/pending human review, reviewed or superseded, with author, revision date and actual reviewer/date/reference when available. This is a report label, not a replacement for machine schema/status fields. Leave unreceived approval explicitly pending. Report review, configuration freeze and final-run authorization are separate statuses.

Do not modify immutable machine evidence to match prose. Correct the report transparently, or reference a separately reviewed corrected evidence version. Superseded findings retain their original run/protocol identity and correction history.

## Required forecasting-report sections

| Section | Required content |
|---|---|
| Run identity and review status | Exact run ID, purpose, stage, author/reviewer, report revision and completion/review references; distinguish planned workload from executed evidence |
| Data, features and protocol | Dataset/source-view version or recorded fingerprint; feature-contract and protocol versions/hashes; code revision; temporal boundaries/origins and eligible populations copied/referenced from the governing run records |
| Model and baseline comparison | Separate primary, supportive and baseline evidence by horizon; identify scope/exclusions and comparison populations. Use the roles defined by the protocol |
| Fold and aggregate metrics | Show every required fold and approved aggregate metric, units/ratio-versus-percent presentation, counts and explicit undefined/missing status. Cite source table/keys; use protocol aggregation without inventing formulas |
| Selected configurations | Recorded identifiers and parameter references, ties and administrative representatives, selection rationale, human freeze status/reference; keep fixed benchmarks distinct from tuned selections |
| Interpretation | Explain magnitude, direction and fold consistency in relation to baselines and the research question. Separate observed evidence from proposed explanations |
| Limitations | Simulated-data scope, temporal/selection exposure, comparison limitations, unavailable information and unresolved downstream claims; disclose prior final-period exposure using the methodology revision record |
| Provenance and reproduction | Link source/view identity, feature/protocol/code/environment records, authorization, integrity/completion evidence and retained model/state references. Link runner reproduction prerequisites rather than duplicating commands |
| Supporting evidence and figures | Link exact run-relative evidence files and relevant candidate/fold/horizon keys; label charts with stage, horizon, units and evidence source |
| Outstanding decisions and next step | Pending interpretation/freeze/downstream decisions, blockers, owner and best next research action; no implied experiment authorization |

[Protocol](../docs/protocol.md) owns metrics, aggregation and selection. [Research design](../docs/research-design.md) and [operative decisions](../docs/decisions/README.md) own interpretation boundaries. [Feature specification](../docs/forecasting-feature-engineering.md) and [dataset contract](../docs/dataset.md) retain scientific definitions. Reference them rather than copying feature formulas, model grids or establishing new thresholds/tests.

For RQ2, keep comparisons descriptive by horizon under the existing rules; do not create an overall cross-horizon winner or treat dependent folds as independent replicates. Selected validation performance is not independent final-evaluation evidence. The [methodology revision record](../docs/forecasting-methodology-revision.md) governs historical-versus-current evidence and prior exposure; storage changes do not erase that history.

## Evidence links and review checklist

Link the actual metadata, completion manifest, fold metrics, configuration summaries, selection records, prediction and eligibility evidence from which the report was derived. Include exact identities/hashes or archive references needed to locate supporting evidence. Local ignored files may be unavailable to a GitHub reader: state that limitation and how an authorized reviewer can retrieve them. Do not add fake links to absent archives or recreate removed outputs/ paths. If evidence cannot be located/verified, mark availability explicitly and do not claim verification.

Before human acceptance, check that tables/figures reconcile with evidence; roles, dates, units, horizons and counts are correct; ties/unavailable results are visible; review/freeze status is supported; limitations and reproduction references are present. Any derived reporting calculation must state its calculation and source values and remain within approved methods. New scientific analysis requires separate review.

Only reviewed lightweight findings/figures are eligible for version control under the storage policy; drafting does not authorize publication. Keep full generated datasets, prediction tables and binaries local. Record the report-review milestone in the [research progress log](../docs/research-progress.md) with its supporting human reference.
