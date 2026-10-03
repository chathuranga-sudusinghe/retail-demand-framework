# Applied MLOps Workflow

Machine Learning Operations (MLOps) here provides reproducible research preparation, controlled execution, trustworthy persistence and human review. It does not add a deployment service, scheduled retraining or production monitoring. Forecasting research is complete; current evidence/interpretation is indexed in [reports](../../reports/README.md) and [final evaluation](../forecasting-final-evaluation.md).

## Authority and lifecycle

[Dataset](../dataset.md) owns source meaning; [validated preparation](../data-cleaning-and-validation.md) owns validation/persistence; [features](../forecasting-feature-engineering.md) owns inputs/preprocessing; [protocol](../protocol.md) owns science; [DR-014](../decisions/DR-014-forecasting-selection-and-final-refit.md) owns the freeze/refit decision. [Runner](../forecasting-runner.md) owns operational commands; [storage](../artifact-storage-policy.md) owns retained locations and immutability.

| Activity | Applied control / evidence |
|---|---|
| Environment | Python 3.12.3 and pinned requirements; record actual versions/builds/hardware and detect mismatch before fitting |
| Preparation | Explicit authorized scope, trustworthy source receipt, typed native keys, audit/provenance and verified readback; no silent repair |
| Feature/preprocessing | Fixed contract and prediction-time availability; separate complete labels; fit only eligible historical training rows |
| Execution | Accepted implementation plus exact stage/run/scope authorization; deterministic candidate ordering, fixed seeds, CPU/single-thread controls and requested/effective parameters |
| Final evaluation | Frozen DR-014 candidates/producers; fresh refits; all predictions persisted/verified before outcome reveal; no result-driven reselection |
| Persistence | All successful learned models with exact fitted state and replay inputs; evidence links/hashes; manifest-last completion |
| Verification | Stage-specific completed-bundle verifier; schemas, keys/counts, hashes, model-to-state links and replay; failed/incomplete evidence is rejected |
| Interpretation | Separate generated numerical evidence from human review; preserve limitations, uncertainty/unavailable status and actual approval references |
| Handoff | Component-owner acceptance of prospective contracts; no actuals/errors in prospective input and no automatic purchasing action |

Run identity is exact, not latest-file discovery. Final source/Git identities are provenance; scientific bindings, explicit approval, historical input, pinned environment and unused storage remain controls. Do not refresh stale authorization records after document edits. Historical completed bundles retain their own snapshots and hashes.

## Testing and continuous integration

Use targeted pytest checks, Ruff and project-configured MyPy for changed source. Inspect scope: forecasting suites contain synthetic/mocked tests and some small native-fit smoke tests. Passing implementation checks does not establish model performance or authorize research execution. Report failures and preserve the original error.

CI is split into [ci-quality.yml](../../.github/workflows/ci-quality.yml) and [ci-tests.yml](../../.github/workflows/ci-tests.yml), both pinned to Python 3.12.3. Pull Request checks targeting main are unconditional. Main-branch push workflows skip only listed presentation-document paths; do not infer that protocol, feature, evidence or authorization edits are automatically exempt. CI runs the configured quality/test commands and requires human review for acceptance.

## Failure, retention and review

No completion manifest means no completed research claim. Retain failed/interrupted evidence and diagnostics, never overwrite/resume automatically or replace failed candidates. A verified implementation defect needs separately approved correction with unchanged scientific scope; performance-driven retries are prohibited. The final report discloses the first failed run's prior outcome access.

Retain every successful validation fit and all final candidates under the current policy. Selective retention, backups, archives and cleanup need separate explicit human decisions. [Storage policy](../artifact-storage-policy.md) specifies those boundaries.

Before presenting or integrating results, review evidence role, stage, exact source/run identity, completion status, metric meaning, selection/freeze references and scientific limits. Forecasting completion does not approve DR-012, uncertainty, review thresholds, 28-day inventory use or shared schemas. Record material milestones in [research progress](../research-progress.md); follow [CONTRIBUTING](../../CONTRIBUTING.md) for Git/review actions.
