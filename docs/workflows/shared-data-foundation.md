# Shared Data Foundation Workflow

> **Issue #89 operational alignment:** Gate 1 is frozen/approved and PR #76 accepted the preceding runner. Common primary encoding and validation orchestration are implemented. Issue #89 adds argument-free resolution, validation model persistence and manifest-last integrity without changing scientific methodology. These changes await human implementation review and a matching specific authorization; no experiment was run. Earlier draft/implementation-pending wording below records previous stages and does not reopen approved forecasting decisions. Downstream and Gate 6 approvals remain separate. See [runner operations](../forecasting-runner.md).

> **Documentation alignment — 2026-09-29:** The human-approved forecast interface covers 1/7/14/28 days and the [frozen feature contract](../forecasting-feature-engineering.md). Interface support does not approve downstream use. The frozen protocol resolves the 28-day baseline formulas. Downstream/component-owner approvals remain separate; experiments are NOT authorised. See [revision and provenance](../forecasting-methodology-revision.md).

## Goal

Create one reproducible, documented data foundation used by all COMP1884 components.

## Workflow

The leakage-safe forecasting sequence and representation ownership are defined below. Shared processed views also support inventory analysis and responsible decision support under the dataset contract and separately approved component handoffs.

## Issue #92 — data lifecycle and representation contracts

**Status:** Documentation proposal for human review. This workflow connects existing scientific authorities and defines representation provenance/persistence. It does not redefine their contracts or authorize implementation, data repair or experiments. The [storage policy](../artifact-storage-policy.md) owns repository-wide locations and retention classes.

### Existing authority boundaries

| Authority | Ownership retained |
|---|---|
| [Dataset contract](../dataset.md), especially Sections 7/8 | Source meaning, field roles, data quality, shared processed-layer intent and member-specific data needs |
| [Feature contract](../forecasting-feature-engineering.md) | Frozen predictors, formulas, leakage controls, preprocessing semantics and model-input definitions |
| [Protocol](../protocol.md) | Chronological windows, eligibility, metrics, selection, execution gates and experiment requirements |
| [Runner operations](../forecasting-runner.md) | Execution/orchestration mechanics and current persistence behavior |
| [Methodology revision](../forecasting-methodology-revision.md) | Current-versus-historical methodology and provenance, including prior final-period exposure |
| [Research design](../research-design.md) and [decision records](../decisions/README.md) | Research rationale and operative approved decisions; historical/superseded text does not become a new definition here |

### Leakage-safe order

~~~text
Raw source
    -> cleaned / validated representation
    -> authorized chronological scope
    -> training / validation / reserved final-evaluation views
    -> fold/origin-specific feature engineering + separate targets
    -> training-only fitted preprocessing
    -> model-ready matrices
~~~

This order does not authorize a full-year feature table followed by splitting. The current runner scopes dates before demand validation/fingerprinting and slices each fold before feature/target preparation. The cleaned/validated stage describes a representation, not permission to audit protected outcomes first: date parsing needed to isolate authorized records may precede quantity validation. Full-source historical EDA is a separate disclosed activity, not a prerequisite to each forecasting run.

Features follow the origin/cutoff availability rules in the feature contract. Targets remain separate outcome evidence under protocol eligibility rules. Preprocessing is never fitted globally or on validation/final-evaluation records. No random split or silent repair/imputation is introduced.

The reserved final-evaluation view is a protected specification at this stage, not an instruction to materialize or evaluate it. Its prior validation and full-year EDA exposure remains disclosed under the methodology revision record. Final refit/evaluation still requires the protocol's separate approval gates.

### Representation purposes, inputs/outputs and existing owners

Module names refer to existing files under src/data/ and src/forecasting/; no new API is prescribed. Scientific validation requirements remain in the linked authorities.

| Stage | Representation purpose | Inputs -> outputs | Existing owning modules/docs |
|---|---|---|---|
| Raw source | Preserve the original local reproduction input | Acquired source -> unmodified snapshot and identity receipt | Manual acquisition; demand_eda.source_receipt; dataset contract |
| Cleaned / validated representation | Provide typed, keyed, sorted observations and quality evidence without inventing repair rules | Authorized observations -> validated records and audit | demand_eda.validate_data/require_valid and profiling modules for EDA; features.prepare_demand for forecasting; dataset contract |
| Authorized chronological scope | Isolate records permitted for the named experiment before scientific preparation | Loaded records plus authorized scope -> scoped demand view | execution.load_dataset/resolve_execution; evaluation.validation_view; protocol and runner operations |
| Chronological views | Separate fitting history, origin-time inputs and retrospective outcomes; specify protected final view | Scoped demand plus protocol view definitions -> training and validation/outcome slices; reserved final specification | validation.split_fold; evaluation.prepare_fold; experiment.run_final_evaluation blocks final execution; protocol |
| Fold/origin-specific features and separate targets | Construct conceptual predictors and independently aligned observed labels | Corresponding view/history and origin -> keyed engineered features, separate targets and eligibility evidence | features.build_features/build_origin_features/feature_eligibility; targets.build_horizon_targets; evaluation.prepare_fold; feature contract and protocol |
| Training-only fitted preprocessing | Preserve learned representation state for the eligible training population | Eligible labelled training features -> fitted vocabulary/scaling state and physical order | preprocessing.fit_preprocessor/fit_primary_preprocessors; feature contract and protocol |
| Model-ready matrices | Supply numerical model inputs using the correct fitted state | View-specific features plus fitted state -> numerical matrix, with labels separately aligned where authorized | preprocessing.ForecastPreprocessor.transform; experiment candidate kernel; feature contract |

A validated dataset is not an engineered feature table. An engineered table contains conceptual predictors; a fitted matrix is its encoded/scaled numerical representation. Targets are not predictors. Replay-origin features are not a full training dataset. The shared demand and downstream view content remains defined by dataset.md Sections 7/8; this workflow does not replace that content with the forecasting loader's narrower view.

### Provenance, persistence and lifecycle status

The expectations below distinguish current behavior from proposed shared handoffs. No dataset export or matrix persistence is implemented or authorized here.

| Stage | Provenance to preserve | Current persistence | Persistence expectation and lifecycle class |
|---|---|---|---|
| Raw source | Source/snapshot identity, receipt/hash/size and acquisition provenance | Local raw CSV; EDA receipt | Retained locally or in a verified archive; never committed. Archive superseded source snapshots needed by historical evidence |
| Cleaned / validated representation | Parent identity, authorized validation scope, code/rule versions, audit and representation identity | Records in memory; EDA/profile audits persisted | Accepted shared handoff may be persisted under validated storage after review. Regenerable from exact retained parents/code; archive if required by superseded findings |
| Authorized scope | Execution authorization, protocol/source/input fingerprints and scope identity | Scoped records in memory; authorization and fingerprints persist in runner bundles | Retain scope/authorization evidence. Scoped records are regenerable; scratch copies temporary |
| Chronological views | Protocol identity, stage/fold, boundaries, origin/horizon, membership/population identity and exclusions | Views in memory; boundaries/counts/hashes persist | Retain view definitions and eligibility/membership evidence. Physical view copies are optional regenerable caches; archive supporting evidence with its run. Final view remains protected |
| Features and separate targets | Parent view, origin/cutoff, feature/protocol/code versions, key alignment, eligibility and target scope | Historical tables/labels in memory; origin features and validation outcomes persist through current runner | Accepted keyed handoffs may be persisted under model-ready data after review; targets remain separately identified and access-scoped. Regenerable tables; temporary scratch copies; archive accepted versions supporting reports |
| Fitted preprocessing | Training-population identity, family/fold/horizon, state version and exact learned representation/order | Current runner persists fitted state | Retain with every retained model; archive together. Reconstruct from exact serialized state, never refit merely to reload |
| Model-ready matrices | Parent features/targets, fitted-state identity, physical order, row alignment and matrix identity | Runtime-only matrices; no full training matrix copied | Temporary/regenerable using exact state; optional persistence needs compatibility review against current protocol. Archive only if explicitly required to preserve non-reconstructible evidence |

Regenerable material depends on retained source bytes, code, environment, definitions and applicable fitted state; hashes alone cannot reconstruct it. Removing the only evidence needed by a reviewed finding is not permitted by a regenerable label.

### Current implementation and later alignment

Current data/processed/ contains EDA/profile tables and an execution record, not a persisted shared validated snapshot or historical training feature/matrix export. artifacts/ is empty, models/ is absent and outputs/ was intentionally removed. The unchanged runner/protocol still reference that old location; do not execute the runner to recreate it.

Shared validation/profiling currently resides in src/data/; forecast-specific preparation, alignment and preprocessing reside in src/forecasting/. This records existing ownership without moving code.

The [storage policy amendment boundary](../artifact-storage-policy.md#required-protocol-amendment-before-selective-retention) identifies changes required under Issue #94 or a dedicated approved amendment task. Current all-fit persistence/replay requirements remain operative until that work is accepted. No scientific, downstream or final-evaluation decision is changed here.

## Current foundation decisions

The following foundation decisions/checks are complete:

1. downloaded schema, row count, date coverage, and key field behaviour have been verified;
2. DR-002 selects **SKU-warehouse-day** as the primary forecasting analytical unit;
3. the verified native grain is one row per `Date + SKU_ID + Warehouse_ID`;
4. `Stockout_Flag` is zero-variance and excluded from predictive/validation use as a stockout label;
5. source `Demand_Forecast` is leakage-sensitive and excluded from ordinary forecasting use;
6. warehouse-level inventory alignment has been profiled;
7. [DR-005](../decisions/DR-005-forecast-validation-design.md) and the [protocol](../protocol.md) own chronological windows and final-evaluation protection; the [methodology revision](../forecasting-methodology-revision.md) owns prior-exposure disclosure.

Pending group approval, [DR-012](../decisions/DR-012-inventory-risk-replenishment-methodology.md) proposes origin-available inventory and policy snapshots for origin reorder-threshold exposure, with fixed origin policy and a no-receipt scenario.

## Decisions still required before later modelling/integration stages

1. define handling of any invalid records discovered by the reproducible pipeline;
2. define missing-period handling if future processed views introduce gaps;
3. preserve the implemented frozen 28-complete-day predictor history and complete-target eligibility; define reviewed persistence/handoff requirements without inventing product exclusions or imputation;
4. retain `Promotion_Flag` as descriptive context, excluded from the frozen forecasting inputs; any later predictor use requires a separate contract revision;
5. document source snapshot within-day semantics and resolve availability/invalid-input handling under DR-012's origin timing contract;
6. finalise the forecasting-to-inventory output contract;
7. finalise the inventory-to-decision-support output contract.

## Reproducibility rule

All shared cleaning, validation, alignment, and aggregation logic must live in code under `src/data/` rather than only inside notebooks.

## Output contracts

### Forecast-to-inventory timing

The approved shared forecast interface represents next-day and direct cumulative 7-, 14- and 28-day quantities from one fixed origin. Retain `SKU_ID`, `Warehouse_ID`, forecast origin `t` and horizon `h` separately, with the explicit target interval `t+1` through `t+h`, inclusive. A target-start date must not be mistaken for the origin date.

DR-012 remains Proposed for group approval; its original downstream scope covers 1/7/14-day forecast inputs. Carrying an `h=28` record through the shared-data schema does not approve 28-day inventory interpretation or the longer no-receipt scenario. **28-day downstream use requires separate component-owner/human approval.** The following inventory timing and scenario requirements remain subject to DR-012 group approval.

Join the same SKU-warehouse's `Inventory_Level` and `Reorder_Point` available at that origin, retain the snapshot date and availability assumption, and keep the threshold fixed within the scenario. Same-date availability does not establish before/after-sales semantics; document that interpretation before integration. Do not use future inventory or silently substitute a different snapshot when origin evidence is unavailable.

The exposure scenario assumes no receipts, transfers, returns, losses or other adjustments. Origin-available lead time is context only. Order quantity is context only after its availability at the forecast origin is established; it must not be added as received inventory. Missing/invalid required evidence remains unavailable/not assessed with a reason. Final schemas and handling of problematic forecasts remain open.

Keep realised cumulative `Units_Sold`, retrospective exposure states and errors in a distinguishable evaluation view. They must not enter origin-time forecast or decision inputs. Preserve DR-011's source distinction and unavailable-information semantics in the downstream handoff.

### Data views

[Dataset contract Sections 7/8](../dataset.md#7-shared-processed-dataset) own shared processed-view content and member-specific needs. [The feature contract](../forecasting-feature-engineering.md) owns model-input definitions; a raw field retained for downstream use does not automatically become a predictor. This workflow connects those representations to chronological preparation and storage without defining another field list.

The final cross-component schemas must be documented before integration.

Chathuranga and Tinosh share API integration design and review, with Chathuranga responsible for forecasting-facing contract meaning. Tinosh implements agreed adapters and delivery schemas after review by the relevant component owner. These technical contracts must preserve provenance, origin, horizon and unavailable-state reasons; they must not settle the pending snapshot or methodological decisions by default.

## Data ownership

The raw dataset remains local. No member should commit raw or processed full datasets to GitHub.
