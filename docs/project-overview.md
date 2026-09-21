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

1. Prepare and analyse historical SKU-level sales and inventory data.
2. Develop and compare suitable demand-forecasting approaches.
3. Select a suitable forecasting model using time-aware evaluation.
4. Combine forecast outputs with inventory variables to identify inventory and replenishment risks.
5. Present risk and replenishment information through clear analytical outputs.
6. Incorporate uncertainty, transparency, limitations, and human oversight into decision support.
7. Integrate the three member components into one end-to-end prototype/framework.

## 6. Main research question

**How can data-driven demand forecasting be used to identify inventory risks and support supply-chain decision-making in retail operations?**

## 7. Supporting research questions

- **RQ1:** What demand patterns can be identified from historical SKU-level sales data?
- **RQ2:** Which forecasting methods are suitable for predicting future product demand?
- **RQ3:** How can forecasting outputs and inventory-state variables be combined to identify stockout, overstock, and replenishment risks?
- **RQ4:** How can uncertainty, transparency, governance, and human oversight guide the responsible use of the resulting decision-support outputs?

## 8. Research contribution

The contribution is not simply to find the forecasting model with the lowest error. The group product will connect:

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

Owns model training, model comparison/selection, demand forecasting, forecasting evaluation, and generation of forecast outputs for downstream use.

### Didilani

Owns inventory-risk and replenishment analysis. Her component consumes Chathuranga's forecast outputs together with inventory variables such as inventory level, reorder point, supplier lead time, and replenishment quantity. She also owns visual/business interpretation of the resulting risk outputs.

### Dewmi

Owns responsible decision support, transparency, limitations, ethical/legal/governance analysis, and human oversight. Her component consumes forecast and inventory-risk/replenishment outputs and converts them into responsible management-facing decision-support information.

## 11. Integration rule

The components are not three unrelated mini-projects. They must exchange defined inputs and outputs:

```text
Chathuranga forecast
        ->
Didilani inventory-risk / replenishment analysis
        ->
Dewmi responsible decision-support layer
        ->
Final integrated framework output
```

## 12. Dataset

The selected source is the **High-Dimensional Supply Chain Inventory Dataset** on Kaggle. It is a simulated dataset designed to represent daily SKU-level supply-chain operations.

The source contains sales, inventory levels, supplier lead times, reorder points, replenishment quantities, promotions, stockout indicators, costs/prices, and a source-provided demand-forecast field.

The project will build its own forecast from historical sales. The source-provided `Demand_Forecast` must not be used in a way that causes target leakage.

See:

- `docs/dataset.md`
- `docs/decisions/DR-001-dataset-selection.md`
- `docs/references.md`

## 13. Scope

In scope:

- SKU-level historical sales analysis;
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
- full COMP1885 individual-project implementations.

## 14. Critical dataset limitation

The selected dataset is **simulated rather than observed data from a real company**. This improves coverage of the variables required by the framework, but limits claims about direct real-world operational effectiveness.

All final conclusions must distinguish:

```text
performance within the simulated dataset
!=
proven performance in a real retailer
```

## 15. Relationship to COMP1885

The group project provides a common analytical foundation. Each member's COMP1885 project can build on that foundation but must become a separate individual research project with its own question, literature review, methodology, experiments, product, results, and discussion.
