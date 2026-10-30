# Chathuranga — COMP1884 Group Project Contribution

## Member details

**Name:** Chathuranga Indrajith Sudusinghe

## Role

**Research Team Lead & Forecasting**

## Purpose in the group system

This component produces the future-demand forecast that becomes the input to Didilani's inventory-risk and replenishment analysis.

## Component research question

**How do temporal characteristics of SKU demand affect the performance and suitability of different forecasting approaches?**

## Secondary forecasting hypothesis

This component uses a secondary hypothesis under the project's primary group-level hypothesis.

### H0

Forecasting performance does not significantly differ across temporal demand conditions.

### H1

Forecasting performance significantly differs across temporal demand conditions.

This remains provisional until temporal demand conditions and the statistical testing procedure are operationally defined.

## Responsibilities

1. Implement the approved forecasting target and analytical grain defined by DR-002.
2. Build chronological training, validation, and test datasets.
3. Train appropriate forecasting models and benchmarks.
4. Compare model performance using agreed metrics.
5. Select a suitable model based on out-of-sample evidence rather than complexity alone.
6. Generate future demand forecasts for each selected SKU-warehouse series.
7. Measure forecast error, bias, and uncertainty where feasible.
8. Produce a stable forecast-output contract for Didilani's component.
9. Document assumptions and limitations.

Chathuranga also leads overall research-team coordination and cross-component research review. FastAPI/API integration is shared with Tinosh: Chathuranga guides API architecture and integration design, owns forecasting-facing input/output contracts, and reviews endpoint behaviour affecting forecasting meaning, provenance, origin and horizon. Tinosh leads endpoint, adapter, test and prototype implementation. This shared role does not make Chathuranga responsible for every prototype implementation detail.

## Downstream dependency

Didilani's component receives the selected forecast output and combines it with inventory-state and replenishment variables such as `Inventory_Level`, `Reorder_Point`, `Supplier_Lead_Time_Days`, and `Order_Quantity`.

## Scope boundary

This component is limited to the forecasting work required by the integrated COMP1884 group product. It should produce a defensible, evaluated forecast output without absorbing Didilani's inventory-risk/replenishment responsibilities or Dewmi's responsible decision-support responsibilities.


## Forecasting research completion

Preparation, training/development, validation, configuration/model freeze, final holdout evaluation and integrity verification are complete as confirmed by Chathuranga. [Final evaluation](../../forecasting-final-evaluation.md) owns results, model decision, interpretation and limitations; [DR-014](../../decisions/DR-014-forecasting-selection-and-final-refit.md) owns the unchanged frozen producer mapping and fresh-refit policy. The final results do not justify reselection.

RQ2 remains a descriptive horizon-specific matched comparison of XGBoost, LightGBM and CatBoost; Ridge/Random Forest are supportive and Naive/Seasonal Naive contextual. [Research design](../../research-design.md) preserves exact hypotheses and inference limits. The temporal-condition hypothesis above remains provisional, and no formal significance claim follows from forecasting completion.

## Canonical inputs, evaluation and outputs

[Dataset](../../dataset.md) defines source/grain; [features](../../forecasting-feature-engineering.md) defines all inputs/order/preprocessing; [protocol](../../protocol.md) defines targets, folds, settings, metrics and schemas; [forecasting workflow](../../workflows/demand-forecasting.md) links the working sequence. Retrospective validation/final actuals and errors remain separate from prospective forecasts. No uncertainty field/method is manufactured.

## Remaining handoff responsibilities

**Reconciled 30 October 2026:** [#203's request-time producer/source handoff is accepted](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/203#issuecomment-6501737406) and [#191's descriptive C1 scope is closed](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/191#issuecomment-6515040267). Continue forecasting-facing review of the retained prototype/views under #201 and final repository consistency under #179; preserve the separate retained-export acceptance and source-timing boundaries. The [team scope record](../../research-design.md#164-human-decisions-and-c1-closeout-record) retains the five deferred extensions.

Own prospective forecast/output meaning, preserve the accepted live producer/model/preprocessor/provenance handoff with Tinosh, and review its retained/prototype representation as applicable. Retain distinct SKU/warehouse, origin, horizon and target interval. [Integration readiness](../../integration-contract-readiness.md) identifies export/schema acceptance, origin inventory semantics and downstream decisions. Didilani and Dewmi retain their own methods, and carrying a 28-day forecast does not approve 28-day inventory/review use.

Forecasting research completion is separate from the integrated product's definition of done: final interchange contracts and consumable prospective outputs still require human/component review. All new experiments and Git actions require explicit authorization under [AGENTS](../../../AGENTS.md).
