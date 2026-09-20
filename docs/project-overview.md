# COMP1884 Group Project Overview

## 1. Project identity

**Academic title:** A Data-Driven Decision Support Framework for Retail Demand Forecasting and Inventory Risk Analysis

**Module:** COMP1884 Group Project  
**Programme:** MSc Data Science, University of Greenwich

This is one integrated group project. Each active member owns a distinct data-science contribution that connects to the shared final framework.

## 2. Business problem

Retail demand changes over time. Underestimating demand can increase stockout pressure and lost-sales risk, while overestimating demand can contribute to excess stock, storage cost, and slow-moving inventory. Retail managers therefore need more than a forecast: they need a transparent interpretation of what the forecast means for operational decisions.

## 3. Research problem

Demand forecasting, inventory-risk analysis, and decision-making are often treated as separate stages. This project investigates how they can be connected in one practical analytical workflow.

## 4. Research aim

To investigate how historical online retail transaction data can be used to forecast product demand and translate forecasting outputs into inventory-risk insights that support retail supply-chain decision-making.

## 5. Research objectives

1. Analyse historical demand patterns and temporal behaviour.
2. Develop and compare suitable forecasting approaches.
3. Translate forecast outputs and demand behaviour into defensible inventory-risk proxies.
4. Present risk information through clear analytical and visual outputs.
5. Incorporate uncertainty, transparency, limitations, and human oversight into decision support.
6. Integrate the member components into one group prototype/framework.

## 6. Main research question

**How can data-driven demand forecasting be used to identify inventory risks and support supply-chain decision-making in retail operations?**

## 7. Supporting research questions

- **RQ1:** What demand patterns can be identified from historical online retail transaction data?
- **RQ2:** Which forecasting methods are suitable for predicting product-level or category-level retail demand?
- **RQ3:** How can forecasting outputs be translated into inventory-risk categories such as stockout, overstocking, and slow-moving product risks?
- **RQ4:** How can ethical, legal, governance, transparency, and human-decision considerations guide responsible use of retail demand-forecasting outputs?

## 8. Research contribution

The contribution is not simply to find the forecasting model with the lowest error. The group product will connect:

```text
Historical transactions
    -> demand behaviour
    -> demand forecasts
    -> forecast error / bias / uncertainty
    -> inventory-risk interpretation
    -> responsible decision support
```

## 9. Shared product

The expected COMP1884 output is one integrated retail decision-support prototype/framework consisting of:

- a reproducible shared data foundation;
- a demand-forecasting component;
- an inventory-risk analytics component;
- a visual/business interpretation layer;
- a responsible decision-support layer;
- documented assumptions, limitations, and evaluation.

## 10. Member contributions

### Chathuranga
Owns time-series demand forecasting, temporal feature engineering, forecasting evaluation, and generation of forecast outputs for downstream use.

### Didilani
Owns inventory-risk analytics, visual analytics, and business interpretation. Her component consumes historical demand behaviour and forecasting outputs.

### Dewmi
Owns responsible decision support, transparency, limitations, ethical/legal/governance analysis, and human decision-support considerations.

## 11. Integration rule

The components are not three unrelated mini-projects. They must exchange defined inputs and outputs and jointly answer the overarching group research question.

## 12. Scope

In scope:

- historical retail transaction analysis;
- time-based demand aggregation;
- trend, seasonality, autocorrelation, volatility, and intermittency analysis;
- baseline, statistical, regression-based, and/or machine-learning forecasting where justified;
- time-aware evaluation;
- inventory-risk proxy design;
- visual interpretation;
- uncertainty and responsible decision support.

Out of scope unless later justified:

- live retailer inventory integration;
- real-time production deployment;
- claims of observed stockouts or true on-hand inventory where the dataset does not contain inventory-level data;
- full COMP1885 individual-project implementations.

## 13. Critical dataset limitation

The UCI Online Retail dataset records transactions, not complete inventory state. It does not directly provide variables such as on-hand stock, reorder points, safety stock, supplier lead time, or replenishment orders.

Therefore, stockout, overstock, and similar outputs must be described as **inventory-risk proxies or decision-support indicators** unless additional defensible data or assumptions are introduced.

## 14. Relationship to COMP1885

The group project provides a common analytical foundation. Each member's COMP1885 project can build on that foundation but must become a separate individual research project with its own question, literature review, methodology, experiments, product, results, and discussion.
