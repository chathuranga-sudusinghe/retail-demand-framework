# Retail Demand Framework

**Academic title:** A Data-Driven Decision Support Framework for Retail Demand Forecasting and Inventory Risk Analysis

**Programme:** MSc Data Science, University of Greenwich  
**Module:** COMP1884 Group Project  
**Repository purpose:** Shared implementation and documentation for the COMP1884 group project.

> **Repository scope:** This repository is dedicated to the COMP1884 group project and its shared research, implementation, collaboration, and evidence.

## Project overview

Retail businesses must decide how much stock to hold, when to replenish, and how to respond when demand changes over time. This project uses simulated daily supply-chain inventory data to build an integrated decision-support framework that connects:

1. demand forecasting;
2. inventory-risk and replenishment analysis;
3. visual and business interpretation; and
4. responsible, transparent decision support.

The project therefore does not stop at a forecasting score. Forecast outputs are passed into inventory analysis and then into a responsible management-facing decision-support layer.

## Research aim

To investigate how data-driven demand forecasting can be integrated with inventory-state information to identify inventory risks and support retail supply-chain decision-making.

## Main research question

**How can data-driven demand forecasting be used to identify inventory risks and support supply-chain decision-making in retail operations?**

## Supporting research questions

- **RQ1:** What demand patterns can be identified from historical SKU-level sales data?
- **RQ2:** Which forecasting methods are suitable for predicting future product demand?
- **RQ3:** How can forecasting outputs and inventory-state variables be combined to identify stockout, overstock, and replenishment risks?
- **RQ4:** How can uncertainty, transparency, governance, and human oversight guide the responsible use of the resulting decision-support outputs?

## Group architecture

```text
High-Dimensional Supply Chain Inventory Dataset
            |
            v
Shared data foundation
            |
            v
Demand forecasting
Chathuranga
            |
            v
Inventory-risk and replenishment analysis
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

| Member | COMP1884 focus |
|---|---|
| Chathuranga Indrajith Sudusinghe | Model training, model selection, demand forecasting and evaluation |
| Didilani Prasadika Weerawickrama Pathinayaka | Inventory-risk analytics, replenishment analysis, visual analytics and business interpretation |
| Haputhanthrige Dewmi Pramodya | Responsible decision support, ethical/legal/governance analysis |

See the group contribution files under `docs/team/`.

## Dataset

The selected dataset is the **High-Dimensional Supply Chain Inventory Dataset** published on Kaggle.

It contains simulated daily SKU-level supply-chain data, including fields such as:

- `Date`
- `SKU_ID`
- `Warehouse_ID`
- `Supplier_ID`
- `Region`
- `Units_Sold`
- `Inventory_Level`
- `Supplier_Lead_Time_Days`
- `Reorder_Point`
- `Order_Quantity`
- `Unit_Cost`
- `Unit_Price`
- `Promotion_Flag`
- `Stockout_Flag`
- `Demand_Forecast`

The project will build and evaluate its **own demand-forecasting component** using historical `Units_Sold`. The source `Demand_Forecast` field must not be used in a way that leaks future/target information into model training.

The full dataset is intentionally **not stored in GitHub**. Raw and processed data remain local.

See [Dataset Contract](docs/dataset.md), [Decision Record DR-001](docs/decisions/DR-001-dataset-selection.md), and [References](docs/references.md).

## Documentation map

### Collaboration and AI-agent rules

- [AI agent instructions](AGENTS.md)
- [Contributor guide](CONTRIBUTING.md)
- [Collaboration workflow](docs/collaboration-workflow.md)
- [Member onboarding guide](docs/member-onboarding.md)

### Research and implementation

- [Project overview](docs/project-overview.md)
- [Research design](docs/research-design.md)
- [Dataset contract](docs/dataset.md)
- [Project boundaries](docs/project-boundaries.md)
- [References](docs/references.md)
- [Decision records](docs/decisions/README.md)
- [Chathuranga — COMP1884](docs/team/chathuranga/group-project-overview.md)
- [Didilani — COMP1884](docs/team/didilani/group-project-overview.md)
- [Dewmi — COMP1884](docs/team/dewmi/group-project-overview.md)
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

**Foundation stage.** The dataset selection and integrated component boundaries are being formalised before implementation begins.
