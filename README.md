# Retail Demand Framework

> **Issue #66 revision — 2026-09-29:** [DR-013](docs/decisions/DR-013-matched-gradient-boosting-comparison.md) records the revised primary XGBoost/LightGBM/CatBoost comparison; Ridge/Random Forest are supportive. Issue #62 remains the provenance for the earlier preprocessing contract. The revised protocol under Issue #65 is frozen/approved (Gate 1), implementation is complete (Gate 2), and PR #76 is human-reviewed/accepted and merged (Gate 3). See the current gate status below.

> **Documentation alignment — 2026-09-29:** The project owner has approved the 1/7/14/28-day forecasting design and frozen the [14-predictor feature contract](docs/forecasting-feature-engineering.md). The [frozen validation protocol](docs/protocol.md) records the approved supportive configurations and 28-day simple baselines. [Issue #78](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/78) authorises only the specific Gate 4 validation run `comp1884-validation-20260929-full-01`, which has not yet been executed. Downstream methods retain their separate approval requirements. See [revision and provenance](docs/forecasting-methodology-revision.md) for historical context and the current gate status below.

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
- **RQ2:** Under the same forecasting inputs, temporal validation design, evaluation metrics, and matched hyperparameter settings, how do XGBoost, LightGBM, and CatBoost compare in forecasting future retail demand?
- **RQ3:** How can forecasting outputs and inventory-state variables be combined to identify stockout, overstock, and replenishment risks?
- **RQ4:** How can uncertainty, transparency, governance, and human oversight guide the responsible use of the resulting decision-support outputs?

## RQ2-specific hypothesis

**H0_RQ2:** Under the matched experimental conditions, XGBoost, LightGBM, and CatBoost show comparable demand-forecasting performance across the evaluated horizons.

**H1_RQ2:** Under the matched experimental conditions, demand-forecasting performance differs among XGBoost, LightGBM, and CatBoost across the evaluated horizons.

These are comparative research hypotheses, not statistical-significance hypotheses. Interpret RQ2 descriptively and comparatively for each horizon: compare arithmetic mean WAPE across the four temporal folds, inspect all four fold-level results, and discuss magnitude, direction, fold consistency and supporting MAE, RMSE and Bias. Clearly defined relative differences may also be reported. No significance procedure or universal numerical decision threshold is approved; the folds are not independent experimental replicates. A small aggregate difference driven mainly by one fold is not strong evidence of a general performance difference. Do not mechanically accept/reject H0_RQ2 using an arbitrary threshold or create a cross-horizon composite/overall winner; report any horizon-dependent model ordering. See [DR-013](docs/decisions/DR-013-matched-gradient-boosting-comparison.md).

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
Responsible management-facing records
            |
            v
Shared API integration
Chathuranga + Tinosh
            |
            v
Technical visuals and prototype assembly
Tinosh
            |
            v
Integrated COMP1884 decision-support framework
```

The integration layer may assemble reviewed component outputs as they become available; FastAPI is a delivery technology, not a research method.

## Multi-Model Forecasting Design

The forecasting component uses a multi-model design with three primary gradient-boosting models, two supportive machine-learning benchmarks, and two simple forecasting baselines.

```text
Primary controlled RQ2 comparison
├── XGBoost
├── LightGBM
└── CatBoost

Supportive benchmarks
├── Ridge Regression
└── Random Forest

Simple baselines
├── Naive
└── Seasonal Naive
```

**Primary controlled comparison:** XGBoost, LightGBM and CatBoost share forecasting inputs, physical representation, eligible rows, horizons, temporal folds, evaluation metrics, matched hyperparameter dimensions/values, configuration count, search procedure and seed policy. Within each fold/horizon, they share fitted SKU and warehouse vocabularies and physical column order: full one-hot identities followed by the same twelve unscaled numerical engineered predictors, giving 67 columns under full 50-SKU / 5-warehouse training coverage.

The design retains fourteen conceptual predictors, fixed-origin 1/7/14/28-day forecasts and four expanding-window folds. Each primary model has 24 configurations per horizon, with seed 42: **1,152 planned primary validation fits**, not executed results. [DR-013](docs/decisions/DR-013-matched-gradient-boosting-comparison.md) records the controlled comparison and hyperparameter search; the [feature contract](docs/forecasting-feature-engineering.md) and [research design](docs/research-design.md) document feature engineering, temporal validation and reproducibility controls for future experimentation.

**Supportive benchmarks:** Ridge Regression and Random Forest provide contextual evidence only and do not determine RQ2. Their fixed configuration policy is approved in the [frozen validation protocol](docs/protocol.md). **Simple baselines:** Naive and Seasonal Naive retain their approved 1/7/14-day formulas; the 28-day extensions are also approved in that protocol. WAPE remains the primary forecasting evaluation metric; MAE, RMSE and Bias are supporting metrics. Protocol approval, implementation acceptance and experiment execution remain separately gated.

## Team Contributions

This is one integrated group research project. Each member is responsible for a defined component while contributing to the shared end-to-end decision-support framework.

### Chathuranga Sudusinghe — Research Team Lead & Forecasting

- Leads overall research-team coordination and the forecasting workstream.
- Responsible for forecasting methodology, model comparison and selection, temporal validation, reproducibility, evaluation, and forecast-output generation.
- Coordinates cross-component research integration and shares API integration with Tinosh.

### Didilani Pathinayaka — Inventory Risk & Replenishment Analysis

- Responsible for inventory-risk and replenishment analysis.
- Defines and evaluates inventory-risk evidence using approved forecasting outputs and inventory information.
- Owns documentation and business interpretation of inventory-risk findings and reviews the analytical meaning of related visual outputs.

### Dewmi Haputhanthrige — Responsible Decision Support

- Responsible for responsible decision-support and governance.
- Develops transparency, limitations, human oversight, and management-facing interpretation.
- Defines and reviews the responsible presentation of forecasting and inventory-risk evidence.

### Tinosh Gamage — System Integration and Prototype Engineering

- Responsible for cross-component technical integration and final prototype engineering.
- Implements approved visual outputs, integration adapters, API/integration tests, and prototype components.
- Shares FastAPI/API integration with Chathuranga while preserving the research meaning defined by each component owner.

See [Chathuranga's](docs/team/chathuranga/group-project-overview.md), [Didilani's](docs/team/didilani/group-project-overview.md), [Dewmi's](docs/team/dewmi/group-project-overview.md) and [Tinosh's](docs/team/tinosh/group-project-overview.md) contribution documents for component boundaries and collaboration responsibilities.

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
- [Issue #65 — protocol frozen / approved](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/65)
- [DR-013 — Matched Gradient-Boosting Comparison](docs/decisions/DR-013-matched-gradient-boosting-comparison.md)
- [Dataset contract](docs/dataset.md)
- [Project boundaries](docs/project-boundaries.md)
- [Literature review](docs/literature/literature-review.md)
- [References](docs/references.md)
- [Decision records](docs/decisions/README.md)
- [Temporal demand and inventory-alignment profile](reports/temporal-demand-profile.md)
- [Chathuranga — COMP1884](docs/team/chathuranga/group-project-overview.md)
- [Didilani — COMP1884](docs/team/didilani/group-project-overview.md)
- [Dewmi — COMP1884](docs/team/dewmi/group-project-overview.md)
- [Tinosh — COMP1884](docs/team/tinosh/group-project-overview.md)
- [Shared data workflow](docs/workflows/shared-data-foundation.md)
- [Forecasting workflow](docs/workflows/demand-forecasting.md)
- [Inventory-risk workflow](docs/workflows/inventory-risk-analysis.md)
- [Responsible decision-support workflow](docs/workflows/responsible-decision-support.md)
- [System integration and prototype workflow](docs/workflows/system-integration-and-prototype.md)

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

Research design was revised and approved under Issue #66. XGBoost, LightGBM and CatBoost are the primary controlled RQ2 models; Ridge and Random Forest are supportive benchmarks. The fourteen conceptual predictors, four horizons, temporal folds and WAPE-led evaluation policy remain unchanged. The primary models use a common full one-hot representation and a matched 24-configuration grid.

Gate 1 is complete: the revised forecasting experiment protocol under Issue #65 is frozen/approved. Gate 2 is complete: the forecasting runner implementation is complete. Gate 3 is complete: PR #76 has been human-reviewed/accepted and merged. [Issue #78](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/78) authorises Gate 4 only for the specific validation run `comp1884-validation-20260929-full-01`; that run has not yet been executed. Gate 5 is pending validation evidence review, and Gate 6 is blocked. Final model/configuration freeze, final refit, and final evaluation are not authorised.
