# Forecasting Runner Operations

This reference describes the implemented preparation, validation and separate final runtime. Scientific methods belong in the [protocol](protocol.md), [features](forecasting-feature-engineering.md) and [DR-014](decisions/DR-014-forecasting-selection-and-final-refit.md); results belong in [final evaluation](forecasting-final-evaluation.md). Retained validation and final evaluation are complete as confirmed by the owner. Commands below are reference shapes, not permission to execute another run.

## Supported entrypoints

Run from the repository root using the reviewed Python 3.12.3 environment:

~~~bash
.venv/bin/python -m src.data.validated_handoff
.venv/bin/python -m src.forecasting.model_ready --representation-id <reviewed-id> --fold <1-4>
.venv/bin/python -m src.forecasting.experiment
.venv/bin/python -m src.forecasting.final_evaluation
~~~

The first two prepare reviewed data representations; they are not experiment commands. Real preparation requires owner authorization. Model-ready preparation supports one validation fold only and rejects final/refit stages before input access. Validation and final experiment entrypoints require their own matching specific-run authorization. Do not rerun completed evidence as a check.

## Fixed inputs and authorization

| Runtime | Fixed input / record |
|---|---|
| Forecasting dataset | data/processed/validated/supply-chain-dataset1-validated-v1/validated.parquet |
| Validation record | data/processed/forecasting/validation_authorization.json |
| Final record | data/processed/forecasting/final_authorization.json |
| Optional model-ready export | data/processed/model-ready/<representation_id>/ |

[paths.py](../src/forecasting/paths.py) resolves repository locations; [authorization.py](../src/forecasting/authorization.py) and [final_authorization.py](../src/forecasting/final_authorization.py) own the strict record contracts. Exact run ID, ordered scope, human approval references, scientific-document bindings, retained evidence, historical input identity and pinned environment must match. Missing, malformed or stale records and consumed storage fail closed. Never refresh authorization hashes, discover a latest file or infer approval from a document. Source/Git identities are provenance; they do not authorize the final runtime.

## Validation runtime

[experiment.py](../src/forecasting/experiment.py) delegates to [orchestration.py](../src/forecasting/orchestration.py). Input projection selects only native keys and Units_Sold with authorized date filters before demand decoding. Fold preparation fits features/targets/preprocessing within frozen chronological boundaries. Validation persists every successful candidate, metrics, predictions, selection records and eligibility evidence. Its entrypoint rejects final-evaluation execution, including --stage final_evaluation; final evaluation uses the separate entrypoint below.

## Separate final runtime and predict-before-reveal

[final_evaluation.py](../src/forecasting/final_evaluation.py) consumes the separate final record and frozen DR-014 scope. It verifies retained validation and historical readiness, refits the twenty learned candidates and preprocessing from eligible history, and constructs all 28 candidate predictions. **All predictions are saved, hashed and verified before any reserved outcome is revealed.** Scoring uses those immutable predictions; final results cannot trigger search, retuning, reselection, replacement or a changed producer mapping.

[final_artifacts.py](../src/forecasting/final_artifacts.py) provides separate final persistence and integrity verification. Final fold IDs are null and final rows never enter validation four-fold summaries.

## Persistence and completion verification

The [storage policy](artifact-storage-policy.md#storage-responsibilities) owns artifact/model/report locations and retention requirements, including temporary reports and historical receipt paths.

Successful lifecycle: preflight -> running -> finalizing -> verified_completed. Metadata alone never establishes completion. The sole completion authority, artifacts/forecasting/<run_id>/run_manifest.json, is published **last**, after reconciliation, model replay, closed logging and final metadata. Never overwrite a completed bundle or its report.

Validation consumers use `src.forecasting.integrity.verify_completed`; final consumers use `src.forecasting.final_artifacts.verify_final_completed`, each at the exact artifact-run anchor. They verify schemas, keys, counts, hashes, model/preprocessor/input links and saved-prediction replay without refitting. Missing, extra, redirected, cross-run, corrupted or incomplete evidence is rejected. Load only trusted locally generated native/joblib artifacts with verified provenance. Verification is an explicit operation, not something documentation edits perform automatically.

## Failure handling

Failed/interrupted runs publish no completion manifest or accepted selection. Recovery independently attempts metadata, diagnostics and partial evidence, preserving the original exception when secondary writes fail. A killed process may leave no diagnostics; absent completion still blocks consumption. Retain partial artifact/model/report directories and the failed status. There is no automatic retry, resume or cleanup.

A verified implementation defect may support only a separately approved corrected run with a new unused ID and unchanged frozen scientific scope. Preserve and disclose prior outcome access. Performance-driven retries and candidate substitution are prohibited. The earlier final execution's scientific exposure is documented in [limitations](forecasting-final-evaluation.md#9-limitations), without using its scores to change methodology.

## Lightweight implementation checks

Use targeted synthetic parser/path/authorization tests for documentation compatibility. Some broader forecasting tests include small native model fits; inspect the selected tests before running. Tests are implementation evidence, not research results. No real preparation, experiment or reserved-outcome read is part of a documentation check. CI definitions are [quality](../.github/workflows/ci-quality.yml) and [tests](../.github/workflows/ci-tests.yml).
