# COMP1884 Group Project Overview

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

Research hypotheses, rationale and inference boundaries are defined in [research design](research-design.md); exact forecasting methods are in the [protocol](protocol.md).

## 8. Integrated system architecture

~~~text
Downloaded Kaggle source -> shared validation/preparation
  -> demand forecasting at SKU–warehouse–day grain
  -> origin-aligned inventory-risk/replenishment analysis
  -> responsible decision-support record
  -> shared API delivery, approved visuals and prototype
~~~

[Shared data foundation](workflows/shared-data-foundation.md) connects component representations. [Integration readiness](integration-contract-readiness.md) distinguishes completed forecasting evidence from prospective exports and unresolved downstream contracts. Forecast error is retrospective evaluation evidence; an uncertainty method is a separate decision and cannot be inferred from it.

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

As Research Team Lead & Forecasting contributor, coordinates group research and owns model training, model comparison/selection, demand forecasting, forecasting evaluation, and SKU-warehouse-day forecast outputs. Shares API architecture and integration review with Tinosh, including forecasting-facing contracts and provenance.

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

Ziya's published High-Dimensional Supply Chain Inventory Dataset, downloaded from Kaggle, supplies historical sales and inventory context. The publisher describes its source records as simulated. [Dataset identity/schema/limitations](dataset.md) owns its field meanings and quality profile. Forecasting uses historical Units_Sold; Stockout_Flag is zero-variance and cannot validate stockout predictions. Source Demand_Forecast is excluded from normal forecasting features/targets.

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

The selected dataset is **downloaded from Kaggle**, with source records **simulated by the publisher rather than observed from a real company**. This improves coverage of the variables required by the framework, but limits claims about direct real-world operational effectiveness.

All final conclusions must distinguish:

```text
performance within the simulated dataset
!=
proven performance in a real retailer
```

## 15. Current delivery state

Forecasting preparation, training/development, validation, freeze, final evaluation and integrity verification are complete as confirmed by Chathuranga. The [final report](forecasting-final-evaluation.md) links unchanged numerical evidence and the [DR-014](decisions/DR-014-forecasting-selection-and-final-refit.md) producer mapping. Final ordering does not change that mapping.

The integrated group product remains in progress. Inventory-risk/replenishment, responsible decision-support semantics, approved uncertainty/human-review logic and prospective API/export acceptance require their component owners' work and review. This overview does not approve unresolved DR-012 or 28-day downstream use.
