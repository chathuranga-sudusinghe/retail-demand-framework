# Applied MLOps Workflow

**Status:** Merged Issue #93 applied-MLOps authority; no experiment or implementation authorization.
**Related issue:** [#93 — Define applied MLOps, research reporting, and progress logging](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/93).

## Purpose and authority

Machine Learning Operations (MLOps) here means reproducible research preparation, controlled experiments, trustworthy persistence and reviewable evidence. It does not introduce deployment, a model registry service, scheduled retraining or production monitoring.

Merged Issue #92 supplies the [data lifecycle](shared-data-foundation.md) and [artifact/storage policy](../artifact-storage-policy.md). Issue #94 aligns operational protocol requirements; storage migration and the exact selective-retention set remain separate reviewed work. Acceptance of documentation does not make those paths executable. This workflow references those authorities instead of redefining their architecture.

The [dataset contract](../dataset.md) owns source meaning/quality and shared/member data needs. The [feature contract](../forecasting-feature-engineering.md) owns predictors, availability and preprocessing semantics. The [protocol](../protocol.md) owns scientific settings, eligibility, evaluation, selection and gates. [Runner operations](../forecasting-runner.md) own exact commands, execution mechanics, persistence and recovery. [Methodology revision](../forecasting-methodology-revision.md), [research design](../research-design.md) and [decision records](../decisions/README.md) govern research provenance and interpretation.

## Practical controls across the research workflow

| Activity | Repository-specific control | Evidence and existing owner |
|---|---|---|
| Environment preparation | Use the repository's pinned dependencies and reviewed runtime; record actual package/build/platform information. Detect mismatches before fitting | requirements files; metadata.py; protocol and runner documentation |
| Data preparation | Follow Issue #92's authorized chronological scope and view sequence; retain source/view identity and quality evidence. No silent repair, imputation or random split | src/data/ audit/profiling modules; execution.py, features.prepare_demand and evaluation.py; dataset contract |
| Feature generation | Use the frozen contract within each fold/origin; keep observed targets separate and fit preprocessing on eligible training rows only | features.py, targets.py, preprocessing.py and evaluation.py; feature contract/protocol |
| Training | Apply the approved deterministic ordering, seeds, device/thread controls and requested/effective parameter checks; do not tune controls outside the protocol | configuration.py, models.py and experiment.py; protocol |
| Run identity | Bind one exact authorized run to its stage/scope, protocol, source implementation and input fingerprints; do not refresh stale authorization or reuse consumed run directories | execution.py, metadata.py and paths.py; runner operations |
| Persistence | Preserve model-to-preprocessor-to-input links and replay evidence. Retention follows the governing protocol and Issue #92 amendment boundary | model_artifacts.py, preprocessing.py and artifacts.py; storage policy/runner |
| Integrity and completion | Reconcile scientific tables, candidate populations, model/state references and hashes; require the completion authority before consuming evidence | integrity.py and experiment.py; runner operations |
| Research handoff | Produce a report grounded in verified evidence, then obtain human interpretation/selection review; record the event with evidence links | [Reporting contract](../../reports/README.md); [progress log](../research-progress.md) |

Exact scientific values and terminal commands remain in their existing authorities. Deterministic controls support repeatability in the recorded environment; they do not establish identical results across arbitrary hardware/library builds or research validity.

## Identity and provenance chain

Keep distinguishable identities for source snapshot, authorized demand view, engineered representation, fitted preprocessing state, configuration, candidate/fold/horizon, run and artifact schema. Use the versions and fingerprints defined by the protocol/storage policy; this workflow assigns no new schema or naming convention.

The evidence chain should connect source and scoped input fingerprints to code/commit state, feature/protocol versions, eligible populations, fitted representations, requested/effective estimator settings, predictions, metrics and retained artifacts. Preserve authorization references and environment/build details. Missing provenance remains explicitly unavailable, never fabricated.

A dataset filename alone is not a version. A code commit alone does not account for uncommitted source changes. A hash alone cannot reconstruct missing data. Reproduction requires the retained inputs, matching code/environment/contracts and exact fitted state where applicable; rerunning training is an experiment requiring specific human authorization.

## CI and testing already applied

[Current CI](../../.github/workflows/ci.yml) runs for Pull Requests targeting main and pushes to main. It installs pinned development dependencies, checks imports/dependency consistency, lints forecasting source/tests, type-checks forecasting source and runs pytest. This document changes no triggers, checks or coverage.

Scientific tests use synthetic panels to check temporal availability, target boundaries, feature/label eligibility, representations, baselines, metrics and selection. Operational tests use mocks and small controlled native smoke tests to check authorization, paths, persistence/replay, reporting, failure recovery and integrity. They do not read the project dataset or constitute research model-comparison evidence.

For each implementation review, record relevant test/static-check commands, environment, results and failures against the reviewed revision. Use the project's configured checks listed in runner operations. Forecasting lint/type-check coverage does not imply equivalent coverage of every component; dependency pins do not constitute a full transitive lock. A passing CI run does not approve methodology, selection or an experiment.

## Persistence, integrity and failure boundaries

The current runner persists every successful learned validation fit and its required state, then reconciles and replays the saved evidence. All-fit persistence remains the compatibility requirement until the exact retention set is human-approved and migrated implementation accepted under the Issue #94 protocol boundary. Do not infer permission to prune candidate binaries from the approved architecture direction with an unresolved exact selective-retention set.

Follow Issue #92 for machine evidence, reusable bundles and reviewed-report responsibilities. Keep completed evidence immutable and traceable. Current verification assumes the existing bundle layout; cross-location references need the separately reviewed migration. The removed outputs/ architecture must not be recreated by running unchanged code.

Runner operations define preflight, running, finalizing and verified completion, plus failed/interrupted behavior. Metadata or a generated comparison alone does not establish completion; the verified final manifest is the authority. Partial evidence can support diagnosis but cannot establish a completed comparison or approved selection. No automatic retry/resume, manifest rewrite or cleanup is authorized by this workflow. Hashes detect changes but do not authenticate human identity or prevent malicious replacement of an entire bundle.

## Human-review gates and ownership

Use the protocol's existing gates: methodology/protocol freeze, implementation acceptance, specific validation authorization, evidence review/selection freeze and separately authorized final refit/evaluation. Do not treat implementation, passing checks, generated leaders or a merged workflow document as approval of the next gate.

Chathuranga owns forecasting methodology/output meaning and research coordination. Didilani retains inventory-risk interpretation, Dewmi responsible decision-support semantics, and Tinosh technical integration/prototype engineering under [project boundaries](../project-boundaries.md). This workflow transfers no analytical ownership. Final-period protection and prior-exposure disclosure remain governed by the protocol/methodology revision; downstream decisions remain separately gated.

Before a run is treated as reviewed research evidence, verify its completion/provenance, inspect its report, record explicit human review and preserve unresolved decisions. Exact review references belong in the governing records; the progress log links them without granting authority.
