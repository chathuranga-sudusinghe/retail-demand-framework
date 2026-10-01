# COMP1884 Group Project Overview

Repository-wide authorities: [data lifecycle](workflows/shared-data-foundation.md), [storage and retention](artifact-storage-policy.md), [applied MLOps](workflows/applied-mlops.md), [research reporting](../reports/README.md), and [continuous progress log](research-progress.md). These connect existing scientific/component contracts without replacing them.

> **Current operational alignment — Issue #94:** Issue #89 is closed and its orchestration implementation was merged in [PR #90](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/90). See the methodology revision record for validation-run provenance and evidence availability. Merged Issues #92/#93 define the lifecycle/storage/MLOps authorities; runtime migration remains separate. No new experiment or final evaluation is authorized.

> **Current documentation alignment — Issue #94:** The current human-approved forecasting design uses 1/7/14/28-day outputs and the [frozen feature contract](forecasting-feature-engineering.md). The frozen protocol resolves the 28-day baseline formulas. [Revision and provenance](forecasting-methodology-revision.md) distinguishes the frozen/approved protocol from accepted Issue #89 implementation, run-specific authorization and separate downstream/component approvals. No experiment execution or separate supervisor approval is asserted.

## 1. Project identity

**Academic title:** A Data-Driven Decision Support Framework for Retail Demand Forecasting and Inventory Risk Analysis

**Module:** COMP1884 Group Project  
**Programme:** MSc Data Science, University of Greenwich

This is one integrated group project. Each active member owns a distinct contribution that connects to the shared final framework.

## 2. Business problem

Retail organisations need to anticipate future demand while considering available inventory, reorder thresholds, replenishment activity, supplier lead times, and operational risk. A demand forecast alone is not a complete business decision. It must be translated into inventory implications and presented with uncertainty, assumptions, and appropriate human oversight.

## 3. Research problem

Demand forecasting, inventory-risk analysis, replenishment planning, and managerial decision-making are often treated as separate stages. This project investigates how they can be connected in one practical analytical workflow.

## 4. Research aim

To investigate how data-driven demand forecasting can be integrated with inventory-state information to identify inventory risks and support retail supply-chain decision-making.

## 5. Research objectives

1. Prepare and analyse historical SKU-warehouse-level sales and inventory data at the approved daily analytical grain.
2. Develop and compare suitable demand-forecasting approaches.
3. Select a suitable forecasting model using time-aware evaluation.
4. Combine forecast outputs with inventory variables to identify inventory and replenishment risks.
5. Present risk and replenishment information through clear analytical outputs.
6. Incorporate uncertainty, transparency, limitations, and human oversight into decision support.
7. Integrate the forecasting, inventory-risk and responsible decision-support components into one end-to-end prototype/framework.

## 6. Main research question

**How can data-driven demand forecasting be used to identify inventory risks and support supply-chain decision-making in retail operations?**

## 7. Supporting research questions

- **RQ1:** What demand patterns can be identified from historical SKU-level sales data?
- **RQ2:** Under the same forecasting inputs, temporal validation design, evaluation metrics, and matched hyperparameter settings, how do XGBoost, LightGBM, and CatBoost compare in forecasting future retail demand?
- **RQ3:** How can forecasting outputs and inventory-state variables be combined to identify stockout, overstock, and replenishment risks?
- **RQ4:** How can uncertainty, transparency, governance, and human oversight guide the responsible use of the resulting decision-support outputs?

### RQ2-specific hypothesis

**H0_RQ2:** Under the matched experimental conditions, XGBoost, LightGBM, and CatBoost show comparable demand-forecasting performance across the evaluated horizons.

**H1_RQ2:** Under the matched experimental conditions, demand-forecasting performance differs among XGBoost, LightGBM, and CatBoost across the evaluated horizons.

These are comparative research hypotheses, not statistical-significance hypotheses. Interpret RQ2 descriptively and comparatively for each horizon: compare arithmetic mean WAPE across the four temporal folds, inspect all four fold-level results, and discuss magnitude, direction, fold consistency and supporting MAE, RMSE and Bias. Clearly defined relative differences may also be reported. No significance procedure or universal numerical decision threshold is approved; the folds are not independent experimental replicates. A small aggregate difference driven mainly by one fold is not strong evidence of a general performance difference. Do not mechanically accept/reject H0_RQ2 using an arbitrary threshold or create a cross-horizon composite/overall winner; report any horizon-dependent model ordering. See [DR-013](decisions/DR-013-matched-gradient-boosting-comparison.md).

## 8. Research contribution

The contribution is not simply to find the forecasting model with the lowest error. The primary forecasting grain has been fixed by DR-002 as `SKU_ID + Warehouse_ID + Date`, preserving the warehouse-specific context required by downstream inventory analysis. The group product will connect:

```text
Historical supply-chain data
    -> demand forecasting
    -> forecast error / uncertainty
    -> inventory-state and replenishment analysis
    -> inventory-risk / replenishment output
    -> responsible decision support
```

## 9. Shared product

The expected COMP1884 output is one integrated retail decision-support prototype/framework consisting of:

- a reproducible shared data foundation;
- a demand-forecasting component;
- an inventory-risk and replenishment-analysis component;
- a visual/business interpretation layer;
- a responsible decision-support layer;
- a technical integration and prototype layer;
- documented assumptions, limitations, and evaluation.

The intended end-to-end behaviour is:

```text
Forecasting output
    -> inventory-risk/replenishment output
    -> responsible management-facing output
```

A recommended replenishment quantity may be produced where the final method can be justified from the available inventory variables. It must not be presented as an unquestionable real-world order instruction.

## 10. Member contributions

### Chathuranga

As Research Team Lead & Forecasting owner, coordinates group research and owns model training, model comparison/selection, demand forecasting, forecasting evaluation, and SKU-warehouse-day forecast outputs. Shares API architecture and integration review with Tinosh, including forecasting-facing contracts and provenance.

### Didilani

Owns inventory-risk and replenishment analysis. Her component consumes Chathuranga's forecast outputs while retaining `Warehouse_ID`, then combines them with warehouse-specific inventory variables such as inventory level, reorder point, supplier lead time, and replenishment quantity. She defines the analytical requirements and meaning of inventory-risk visuals, documents and interprets the findings, and reviews their technical representation.

### Dewmi

Owns responsible decision support, transparency, limitations, ethical/legal/governance analysis, and human oversight. Her component consumes forecast and inventory-risk/replenishment outputs and converts them into responsible management-facing decision-support information.

### Tinosh

Owns system integration and prototype engineering: approved component adapters and interchange contracts, technical visual implementation, API and integration tests, reproducibility checks, and final prototype assembly. FastAPI/API integration is shared with Chathuranga. Tinosh implements the delivery layer without changing component methodology or the meaning of its outputs.

## 11. Integration rule

The components are parts of one group product. They must exchange defined inputs and outputs:

```text
Chathuranga forecast
        ->
Didilani inventory-risk / replenishment analysis
        ->
Dewmi responsible decision-support layer
        ->
Chathuranga + Tinosh shared API integration
        ->
Tinosh technical visuals and prototype assembly
        ->
Final integrated framework output
```

Integration may use each reviewed output as it becomes available; the implementation need not follow a strictly sequential schedule. FastAPI is an integration/delivery technology, not a research method.

## 12. Dataset

The selected source is the **High-Dimensional Supply Chain Inventory Dataset** on Kaggle. It is a simulated dataset designed to represent daily SKU-level supply-chain operations.

The source contains sales, inventory levels, supplier lead times, reorder points, replenishment quantities, promotions, stockout indicators, costs/prices, and a source-provided demand-forecast field.

The project will build its own forecast from historical sales using `Units_Sold` as the target at the approved `SKU_ID + Warehouse_ID + Date` grain. The source-provided `Demand_Forecast` must not be used in a way that causes target leakage. `Stockout_Flag` is zero-variance and cannot be used as a stockout target or validation label.

See:

- `docs/dataset.md`
- `docs/decisions/DR-001-dataset-selection.md`
- `docs/decisions/DR-002-forecasting-analytical-unit.md`
- `reports/temporal-demand-profile.md`
- `docs/literature/literature-review.md`
- `docs/references.md`

## 13. Scope

In scope:

- SKU-warehouse-day historical sales analysis;
- time-aware demand forecasting;
- model comparison and forecast evaluation;
- inventory-level and reorder-point analysis;
- supplier lead-time and replenishment analysis;
- inventory-risk identification;
- replenishment recommendation logic where methodologically justified;
- visual interpretation;
- uncertainty and responsible decision support.

Out of scope unless later justified:

- live retailer system integration;
- real-time production deployment;
- treating simulated data as observed data from a real operating company;
- automatic execution of purchase/replenishment orders;

## 14. Critical dataset limitation

The selected dataset is **simulated rather than observed data from a real company**. This improves coverage of the variables required by the framework, but limits claims about direct real-world operational effectiveness.

All final conclusions must distinguish:

```text
performance within the simulated dataset
!=
proven performance in a real retailer
```
