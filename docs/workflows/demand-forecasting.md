# Demand Forecasting Workflow

## Responsible member

Chathuranga — Research Team Lead & Forecasting. Owns methodology, model comparison, forecast/output meaning and evaluation; shares API architecture/integration review with Tinosh.

## Goal and current state

Produce reproducible next-day and cumulative planning-horizon forecasts from historical Units_Sold at SKU_ID + Warehouse_ID + Date. Preparation, development, validation, freeze, final evaluation and integrity verification are complete as confirmed by Chathuranga. [Final evaluation](../forecasting-final-evaluation.md) owns the full results, decision and scientific limitations; downstream work remains separate.

## Canonical working sequence

~~~text
Validated source -> authorized chronological demand projection
  -> frozen features and separate complete horizon labels
  -> eligible-training preprocessing -> controlled validation
  -> human-reviewed configuration/producer freeze
  -> separately authorized fresh final refits
  -> persist/verify all predictions -> reveal outcomes -> final scoring/verification
  -> reviewed prospective handoff and integration
~~~

| Contract | Canonical home |
|---|---|
| Dataset meaning/profile/limitations | [Dataset](../dataset.md) |
| Source cleaning and validated handoff | [Preparation contract](../data-cleaning-and-validation.md) |
| Exact predictor/preprocessing behavior | [Feature contract](../forecasting-feature-engineering.md) |
| Targets, horizons, dates, grid, baselines, metrics, aggregation/ties | [Protocol](../protocol.md) |
| Frozen configurations, producer mapping and fresh final-refit decision | [DR-014](../decisions/DR-014-forecasting-selection-and-final-refit.md) |
| Commands, authorization, persistence, verification and failures | [Runner](../forecasting-runner.md) |
| Storage/retention | [Storage policy](../artifact-storage-policy.md) |
| Numerical evidence and current interpretation | [Report index](../../reports/README.md), [final results](../forecasting-final-evaluation.md) |

## Evidence roles and leakage control

XGBoost/LightGBM/CatBoost are the matched primary RQ2 comparison; Ridge/Random Forest are fixed supportive references; Naive/Seasonal Naive remain contextual baselines. Comparison is horizon-specific. No universal winner, formal significance claim, cross-horizon composite or final-result-driven reselection is approved.

Keep features and retrospective labels separate. Every historical row uses its own origin; preprocessing fits only eligible labelled training rows. Prediction vectors do not update inside a validation/final target window. Source Demand_Forecast is excluded from normal features/targets; future inventory states and actuals/errors do not enter prospective inputs.

The December 3–30 final interval had earlier December 3–16 validation and full-year EDA exposure. The first failed final execution also revealed outcomes; the corrected run retained the frozen scope. Disclose all of these in presentations and carry them into later handoffs.

## Downstream handoff

Use the unchanged DR-014 producer mapping. Forecast origin, target start/end, horizon, SKU/warehouse, model/configuration and provenance must remain distinguishable. Retrospective actuals/errors are evaluation evidence, not prospective decision inputs. No uncertainty method is currently supplied by this comparison.

[Integration readiness](../integration-contract-readiness.md) records completed prospective export/schema acceptance, reported consumer acceptance and the continuing unknown source inventory timing limitation. Didilani owns inventory-risk/replenishment interpretation; Dewmi owns responsible review/semantics; Tinosh implements approved contracts. Carrying 28-day records does not approve downstream 28-day use.

## Execution and review boundary

The completed study does not authorize another run. For forecasting, Chathuranga manually runs any specifically approved preparation/experiment. Synthetic checks support implementation review but are not research evidence. Follow [CONTRIBUTING](../../CONTRIBUTING.md), [applied MLOps](applied-mlops.md) and [AGENTS](../../AGENTS.md). The earlier experiment's different design remains historical, not the revised study's official baseline.
