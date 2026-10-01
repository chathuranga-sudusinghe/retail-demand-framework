# Chathuranga — COMP1884 Group Project Contribution

Repository-wide authorities: [data lifecycle](../../workflows/shared-data-foundation.md), [storage and retention](../../artifact-storage-policy.md), [applied MLOps](../../workflows/applied-mlops.md), [research reporting](../../../reports/README.md), and [continuous progress log](../../research-progress.md). These connect existing scientific/component contracts without replacing them.

> **Current operational alignment — Issue #94:** Issue #89 is closed and its orchestration implementation was merged in [PR #90](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/90). See the methodology revision record for validation-run provenance and evidence availability. Merged Issues #92/#93 define the lifecycle/storage/MLOps authorities; runtime migration remains separate. No new experiment or final evaluation is authorized.

> **Current documentation alignment — Issue #94:** The human-approved component uses direct 1/7/14/28-day targets and the [frozen fourteen-predictor contract](../../forecasting-feature-engineering.md). The revised executable protocol is frozen/approved under Issue #65, including the resolved 28-day baseline formulas. Issue #89 orchestration was accepted and merged through PR #90. Specific authorization remains run-bound; the methodology revision record distinguishes the recorded validation event from currently unavailable completion evidence. Storage migration, selection freeze and final evaluation remain separately reviewed. No experiment is authorised; see [approval and provenance](../../forecasting-methodology-revision.md).

## Member details

**Name:** Chathuranga Indrajith Sudusinghe

## Role

**Research Team Lead & Forecasting**

## Purpose in the group system

This component produces the future-demand forecast that becomes the input to Didilani's inventory-risk and replenishment analysis.

## Component research question

**How do temporal characteristics of SKU demand affect the performance and suitability of different forecasting approaches?**

## Primary controlled RQ2 responsibility

**Under the same forecasting inputs, temporal validation design, evaluation metrics, and matched hyperparameter settings, how do XGBoost, LightGBM, and CatBoost compare in forecasting future retail demand?**

**H0_RQ2:** Under the matched experimental conditions, XGBoost, LightGBM, and CatBoost show comparable demand-forecasting performance across the evaluated horizons.

**H1_RQ2:** Under the matched experimental conditions, demand-forecasting performance differs among XGBoost, LightGBM, and CatBoost across the evaluated horizons.

[DR-013](../../decisions/DR-013-matched-gradient-boosting-comparison.md) records the owner-approved direction. Only XGBoost/LightGBM/CatBoost determine RQ2; Ridge/Random Forest provide contextual evidence, and Naive/Seasonal Naive retain their separate baseline rules. These are comparative research hypotheses, not statistical-significance hypotheses. Interpret RQ2 descriptively and comparatively for each horizon: compare arithmetic mean WAPE across the four temporal folds, inspect all four fold-level results, and discuss magnitude, direction, fold consistency and supporting MAE, RMSE and Bias. Clearly defined relative differences may also be reported. No significance procedure or universal numerical decision threshold is approved; the folds are not independent experimental replicates. A small aggregate difference driven mainly by one fold is not strong evidence of a general performance difference. Do not mechanically accept/reject H0_RQ2 using an arbitrary threshold or create a cross-horizon composite/overall winner; report any horizon-dependent model ordering. The existing temporal-condition hypothesis below remains provisional and separate.

## Secondary forecasting hypothesis

This component uses a secondary hypothesis under the project's primary group-level hypothesis.

### H0

Forecasting performance does not significantly differ across temporal demand conditions.

### H1

Forecasting performance significantly differs across temporal demand conditions.

This remains provisional until temporal demand conditions and the statistical testing procedure are operationally defined.

## Inputs

Primary inputs:

- `Date`;
- `SKU_ID`;
- `Warehouse_ID`;
- `Units_Sold`;
- the twelve numerical engineered features defined in the frozen contract, constructed from the fields above.

DR-002 has fixed the primary forecasting analytical unit as `SKU_ID + Warehouse_ID + Date`. The target at this grain is `Units_Sold`.

The frozen contract contains **two categorical context + twelve numerical engineered = fourteen conceptual predictors** in the same order for all learned models/horizons, with 28 complete consecutive history days. Primary XGBoost, LightGBM and CatBoost share 67 full one-hot/numerical columns under full eligible-training category coverage, with unscaled numerical inputs. Ridge/Random Forest are supportive benchmarks only; Ridge scales numerical predictors. The primary comparison also shares origins, eligible rows, targets, folds, metrics and the matched 24-configuration grid.

`Date` and `Units_Sold` are construction/alignment/target sources; the eleven other raw fields, including source `Demand_Forecast`, promotion and inventory, are excluded predictors. They may remain useful to other components.

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

Chathuranga also leads overall research-team coordination and cross-component research review. FastAPI/API integration is shared with Tinosh: Chathuranga guides API architecture and integration design, owns forecasting-facing input/output contracts, and reviews endpoint behaviour affecting forecasting meaning, provenance, origin and horizon. Tinosh leads endpoint, adapter, test and prototype implementation. This shared role does not make Chathuranga the owner of every prototype implementation detail.

## Candidate outputs

```text
SKU_ID
Warehouse_ID
forecast_origin
target_start_date
target_end_date
forecast_horizon (1/7/14/28 days; 7/14/28 cumulative)
actual_demand
forecast_demand
forecast_error
absolute_error
model_id
forecast uncertainty / interval fields, if available
```

## Evaluation

**WAPE is primary** under DR-006; MAE, RMSE and Bias are supporting. Bias = forecast − actual. Calculate the arithmetic mean over four folds separately by horizon; no cross-horizon composite is approved. Review fold-level stability and supporting errors before selection. MAPE is not part of the primary policy.

## Downstream dependency

Didilani's component receives the selected forecast output and combines it with inventory-state and replenishment variables such as `Inventory_Level`, `Reorder_Point`, `Supplier_Lead_Time_Days`, and `Order_Quantity`.

## Definition of done

This component is complete for COMP1884 when:

- the approved target and SKU-warehouse-day analytical grain are preserved;
- at least one benchmark and justified forecasting alternatives are evaluated;
- validation is time-aware;
- a suitable model is selected using reproducible evidence;
- future demand forecasts are generated;
- forecast outputs follow an agreed schema;
- error/bias analysis is available;
- outputs can be consumed by the inventory-risk component;
- limitations are documented.

## Scope boundary

This component is limited to the forecasting work required by the integrated COMP1884 group product. It should produce a defensible, evaluated forecast output without absorbing Didilani's inventory-risk/replenishment responsibilities or Dewmi's responsible decision-support responsibilities.

## Revised forecasting responsibility

The human-approved design uses direct 1/7/14/28-day targets and four expanding 28-day validation windows.

Issue #62 accepted the earlier frozen feature/preprocessing implementation and tests and remains historical provenance. Common primary representation and XGBoost/LightGBM/CatBoost interfaces and tests now exist. Issue #65 is frozen/approved, including the resolved 28-day baseline formulas; Gate 1 is complete. PR #76 accepted the preceding runner. Issue #89 operational implementation, including validation model persistence, was merged through PR #90. A validation run has occurred; see the methodology revision record for evidence availability. Specific execution authorization remains separate from protocol freeze and implementation acceptance. Final model/configuration freeze, final refit and final evaluation require their separate approvals. Final evaluation covers December 3–30 at origin December 2, reserved from subsequent selection/fitting but not fully unseen historically: December 3–16 had prior validation exposure and full-year EDA inspected the interval. Didilani and Dewmi retain independent downstream decisions. No 28-day inventory or human-review rule, or experiment execution, is approved here.
