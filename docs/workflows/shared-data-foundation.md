# Shared Data Foundation Workflow

## Goal

Provide one reproducible native-grain source foundation for the COMP1884 components while preserving chronology, field meaning and provenance. Shared cleaning/validated handoff and forecasting preparation are implemented; forecasting research is complete. This does not establish downstream analytical/API acceptance.

## Data lifecycle and representation contracts

~~~text
Local immutable raw source + verified acquisition receipt
  -> typed, ordered validated native records + audit/schema/provenance
  -> authorized chronological projection/views
  -> historical features + separate horizon targets
  -> eligible-training fitted preprocessing/model-ready representations
  -> controlled experiment evidence + model bundles
  -> reviewed prospective component handoffs
~~~

| Stage / owner | Contract and persistence boundary |
|---|---|
| Source identity and meaning | [Dataset](../dataset.md); fifteen source fields and native keys |
| Shared validation/preparation | [Cleaning contract](../data-cleaning-and-validation.md), src/data/; local versioned validated Parquet with audit/schema/provenance, no observation repair |
| Chronological forecasting projection | src/forecasting/execution.py; four native key/demand columns, authorized Arrow date filters before demand decoding |
| Features/targets/preprocessing | [Feature contract](../forecasting-feature-engineering.md), [protocol](../protocol.md); grouped same-series history, separate complete labels and eligible-training vocabularies/scaling |
| Optional one-fold model-ready representation | src/forecasting/model_ready.py; separate feature/target tables, model matrices/states and model-ready.json completion record; no estimator fitting |
| Experiment evidence/models/reports | [Storage policy](../artifact-storage-policy.md) and [runner](../forecasting-runner.md); separate run-owned locations and stage-specific integrity |
| Descriptive analysis | src/analysis/; historical EDA/profile reports and local descriptive tables, not accepted training inputs |

Data/preparation/representation IDs require exact parent identity, scope, ordered schema, native-key uniqueness, population/byte hashes, code/environment versions and review status. Do not silently replace versions, infer source-quality acceptance from EDA, or load the latest matching filename. Source preparation is distinct from authorized forecasting views: carrying the full source does not permit final-outcome use for feature selection or validation.

Validation consumes its named validated projection, not optional model-ready exports. Final evaluation is a separate protected runtime. Review commands and authorization behavior in runner operations instead of duplicating them here.

## Remaining downstream decisions

Existing validators reject blocking source defects without repairing observations. A new repair, missing-period handling, identifier mapping or product exclusion requires human approval if proposed. Frozen forecasting eligibility and promotion exclusion remain unchanged.

The retained export, downstream adapters/schemas and unavailable/problematic-input handling are implemented; their scoped acceptance is recorded in the [current handoff record](../integration-contract-readiness.md#12-current-delivery-and-acceptance--9-november-2026). Source inventory within-day timing remains unknown and is disclosed under the constructed-origin scenario. Twenty-eight-day inventory use remains deferred and needs separate human approval before extension. No schema default resolves an unknown source fact or approves a future method.

## Output contracts

### Forecast-to-inventory timing

The approved shared forecast interface represents next-day and direct cumulative 7-, 14- and 28-day quantities from one fixed origin. Retain `SKU_ID`, `Warehouse_ID`, forecast origin `t` and horizon `h` separately, with the explicit target interval `t+1` through `t+h`, inclusive. A target-start date must not be mistaken for the origin date.

The [DR-012 approval record](../decisions/DR-012-inventory-risk-replenishment-methodology.md#group-approval-record) covers 1/7/14-day scenario exposure. Carrying an `h=28` forecast does not approve 28-day inventory interpretation. Source-based analysis still requires source timing evidence; the implemented constructed-origin path uses hypothetical starting balances while preserving unknown source timing. **28-day downstream use requires separate component-owner/human approval.**

Join the same SKU-warehouse's `Inventory_Level` and `Reorder_Point` available at that origin, retain the snapshot date and availability assumption, and keep the threshold fixed within the scenario. Same-date availability does not establish before/after-sales semantics; document that interpretation before integration. Do not use future inventory or silently substitute a different snapshot when origin evidence is unavailable.

The exposure scenario assumes no receipts, transfers, returns, losses or other adjustments. Origin-available lead time is context only. Order quantity is context only after its availability at the forecast origin is established; it must not be added as received inventory. Missing/invalid required evidence remains unavailable/not assessed with a reason. The retained-export mapping and problematic-forecast handling are implemented in [forecast_handoff.py](../../src/inventory_risk/forecast_handoff.py). Current scoped consumer/API acceptance is recorded separately in integration readiness; it does not establish source timing.

Keep realised cumulative `Units_Sold`, retrospective exposure states and errors in a distinguishable evaluation view. They must not enter origin-time forecast or decision inputs. Preserve DR-011's source distinction and unavailable-information semantics in the downstream handoff.

### Data views

[Dataset contract Sections 7/8](../dataset.md#7-shared-processed-dataset) own shared processed-view content and member-specific needs. [The feature contract](../forecasting-feature-engineering.md) owns model-input definitions; a raw field retained for downstream use does not automatically become a predictor. This workflow connects those representations to chronological preparation and storage without defining another field list.

The implemented cross-component contracts are documented in the retained-export contract, API guide and integration readiness record. Future contract changes need review before implementation.

Chathuranga and Tinosh share API integration design and review, with Chathuranga responsible for forecasting-facing contract meaning. Tinosh implements agreed adapters and delivery schemas after review by the relevant component owner. These technical contracts must preserve provenance, origin, horizon and unavailable-state reasons; they must not settle the pending snapshot or methodological decisions by default.

## Reproducibility and data ownership

Important preparation/analytical logic belongs in reusable src/ modules, not only notebooks. Retain local source and provenance; never commit raw/processed datasets, binaries or machine evidence. Shared field meaning stays in the dataset contract, transformations in their canonical contract, and analytical interpretation with the relevant component owner. Documentation and metadata are not experiment authorization. Contribution/review follows [CONTRIBUTING](../../CONTRIBUTING.md).
