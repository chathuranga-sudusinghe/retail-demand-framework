# Retail Demand Framework

**Academic title:** A Data-Driven Decision Support Framework for Retail Demand Forecasting and Inventory Risk Analysis

**Programme:** MSc Data Science, University of Greenwich  
**Module:** COMP1884 Group Project  
**Repository purpose:** Shared implementation and documentation for the COMP1884 group project.

> **Important boundary:** This repository contains the COMP1884 group project. It also documents the planned COMP1885 individual-project directions for each member so the relationship is clear, but the full COMP1885 implementations will be developed separately.

## Project overview

Retail businesses must decide how much stock to hold, when to replenish, and how to respond when demand changes over time. This project uses historical online retail transaction data to build a decision-support framework that connects:

1. retail demand analysis;
2. time-series demand forecasting;
3. inventory-risk interpretation;
4. visual and business interpretation; and
5. responsible, transparent decision support.

The project therefore does not stop at a forecasting score. Its purpose is to translate forecasting outputs into practical inventory-risk insights and decision-support information.

## Research aim

To investigate how historical online retail transaction data can be used to forecast product demand and translate forecasting outputs into inventory-risk insights that support retail supply-chain decision-making.

## Main research question

**How can data-driven demand forecasting be used to identify inventory risks and support supply-chain decision-making in retail operations?**

## Supporting research questions

- **RQ1:** What demand patterns can be identified from historical online retail transaction data?
- **RQ2:** Which forecasting methods are suitable for predicting product-level or category-level retail demand?
- **RQ3:** How can forecasting outputs be translated into inventory-risk categories such as stockout, overstocking, and slow-moving product risks?
- **RQ4:** How can ethical, legal, governance, transparency, and human-decision considerations guide the responsible use of retail demand-forecasting outputs?

## Group architecture

```text
UCI Online Retail transactions
            |
            v
Shared data foundation
            |
            v
Time-series demand forecasting
Chathuranga
            |
            v
Inventory-risk analytics and visual interpretation
Didilani
            |
            v
Responsible decision support and governance
Dewmi
            |
            v
Integrated COMP1884 decision-support framework
```

## Team

| Member | COMP1884 focus | Planned COMP1885 direction |
|---|---|---|
| Chathuranga Indrajith Sudusinghe | Time-series demand forecasting and model evaluation | Advanced time-series demand forecasting for heterogeneous retail demand |
| Didilani Prasadika Weerawickrama Pathinayaka | Inventory-risk analytics, visual analytics, and business interpretation | Inventory-risk modelling using demand dynamics and forecast uncertainty |
| Haputhanthrige Dewmi Pramodya | Responsible decision support, ethical/legal/governance analysis | Trustworthy and explainable retail decision support |

See the separate group and individual overview files under `docs/team/`.

## Dataset

The project uses the **UCI Machine Learning Repository – Online Retail** dataset.

Core source fields:

- `InvoiceNo`
- `StockCode`
- `Description`
- `Quantity`
- `InvoiceDate`
- `UnitPrice`
- `CustomerID`
- `Country`

The raw forecasting target is `Quantity`, but forecasting will use **time-aggregated demand**, for example product-level daily or weekly quantity.

The dataset itself is intentionally **not stored in GitHub**. Raw and processed data remain local.

## Documentation map

- [Project overview](docs/project-overview.md)
- [Research design](docs/research-design.md)
- [Dataset contract](docs/dataset.md)
- [Project boundaries](docs/project-boundaries.md)
- [Chathuranga — COMP1884](docs/team/chathuranga/group-project-overview.md)
- [Chathuranga — COMP1885 overview](docs/team/chathuranga/individual-project-overview.md)
- [Didilani — COMP1884](docs/team/didilani/group-project-overview.md)
- [Didilani — COMP1885 overview](docs/team/didilani/individual-project-overview.md)
- [Dewmi — COMP1884](docs/team/dewmi/group-project-overview.md)
- [Dewmi — COMP1885 overview](docs/team/dewmi/individual-project-overview.md)
- [Shared data workflow](docs/workflows/shared-data-foundation.md)
- [Forecasting workflow](docs/workflows/demand-forecasting.md)
- [Inventory-risk workflow](docs/workflows/inventory-risk-analysis.md)
- [Responsible decision-support workflow](docs/workflows/responsible-decision-support.md)

## Repository structure

```text
docs/               Research, scope, member and workflow documentation
data/raw/            Local raw data location; dataset files are ignored
data/processed/      Local processed data location; generated data are ignored
notebooks/           Exploratory notebooks
src/data/            Shared data pipeline
src/forecasting/     Forecasting implementation
src/inventory_risk/  Inventory-risk implementation
src/visualization/   Shared analytical visualisation code
src/decision_support/Decision-support implementation
tests/              Automated tests
reports/            Project/report support material
```

## Development principle

Code is organised by **system component**, not by student name. Member ownership is documented in `docs/team/`, while the implementation remains an integrated group product.

## Status

**Foundation stage.** Research design, dataset rules, project boundaries, and member responsibilities are being formalised before implementation begins.
