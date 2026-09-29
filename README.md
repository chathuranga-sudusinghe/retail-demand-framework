# Retail Demand Framework

> **Documentation alignment — 2026-09-29:** The project owner has approved the 1/7/14/28-day forecasting design and frozen the [14-predictor feature contract](docs/forecasting-feature-engineering.md). Implementation acceptance, the revised executable protocol, proposed 28-day baselines and downstream methods remain separately gated. Experiment execution is NOT authorised. See [revision and provenance](docs/forecasting-methodology-revision.md).

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

## Primary group-level hypothesis

**H0:** Demand forecasting does not significantly improve inventory-risk identification and supply-chain decision support.

**H1:** Demand forecasting significantly improves inventory-risk identification and supply-chain decision support.

The detailed baseline, measurable outcomes, and statistical testing needed to operationalise this hypothesis remain part of the research methodology.

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

The project will build and evaluate its **own demand-forecasting component** using historical `Units_Sold`. DR-002 has selected the primary forecasting grain as `SKU_ID + Warehouse_ID + Date`, so forecasts must retain warehouse identity for downstream inventory analysis. The source `Demand_Forecast` field must not be used in a way that leaks future/target information into model training.

Verified profiling also shows that `Stockout_Flag` is 0 for all 91,250 rows, so it cannot be used as a stockout target or validation label.

The full dataset is intentionally **not stored in GitHub**. Raw and processed data remain local.

See [Dataset Contract](docs/dataset.md), [DR-001 — Dataset Selection](docs/decisions/DR-001-dataset-selection.md), [DR-002 — Forecasting Analytical Unit](docs/decisions/DR-002-forecasting-analytical-unit.md), [Literature Review](docs/literature/literature-review.md), [Temporal Demand Profile](reports/temporal-demand-profile.md), and [References](docs/references.md).

## Documentation map

### Collaboration and AI-agent rules

- [AI agent instructions](AGENTS.md)
- [Contributor guide](CONTRIBUTING.md)
- [Collaboration workflow](docs/collaboration-workflow.md)
- [Member onboarding guide](docs/member-onboarding.md)

### Research and implementation

- [Project overview](docs/project-overview.md)
- [Research design](docs/research-design.md)
- [Frozen forecasting feature contract](docs/forecasting-feature-engineering.md)
- [Forecasting methodology and provenance](docs/forecasting-methodology-revision.md)
- [Dataset contract](docs/dataset.md)
- [Project boundaries](docs/project-boundaries.md)
- [Literature review](docs/literature/literature-review.md)
- [References](docs/references.md)
- [Decision records](docs/decisions/README.md)
- [Temporal demand and inventory-alignment profile](reports/temporal-demand-profile.md)
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

## Usage and permissions

This repository is provided publicly for **academic and educational review**.

No open-source licence is granted for the original project materials in this repository. Unless explicit written permission is obtained from the project authors, the repository content must not be copied, modified, redistributed, commercially reused, or incorporated into another project beyond what is otherwise permitted by applicable law.

Third-party datasets, software libraries, frameworks, and other external materials referenced by this project remain subject to their own licences, terms, and conditions. The project dataset is not distributed in this repository and is not covered by this repository notice.

## Status

**Research foundation and forecasting feature contract documented.** The current learned models are Ridge Regression, Random Forest Regressor and LightGBM Regressor. Features, revised chronological folds and WAPE-led metrics are settled; feature/preprocessing implementation and its tests remain to be aligned. Proposed 28-day baseline formulas, the revised executable experiment protocol, uncertainty, DR-012 inventory methodology, replenishment quantities and human-review rules retain separate approval boundaries. No experiment execution is authorised.
