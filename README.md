# Retail Demand Forecasting and Inventory Risk Analysis

**COMP1884 · MSc Data Science · University of Greenwich**

This group project builds a data-driven decision-support framework connecting demand forecasts, inventory-risk/replenishment analysis and responsible management-facing outputs. It uses the simulated High-Dimensional Supply Chain Inventory Dataset; results do not establish effectiveness in a real retailer.

## Current project state

Chathuranga's forecasting research is complete: preparation, development, validation, configuration/model freeze, final holdout evaluation and integrity verification, as confirmed by the project owner. [Final results and limitations](docs/forecasting-final-evaluation.md) consolidate the evidence and interpretation for human review.

| Horizon | Frozen producer | Configuration |
|---|---|---|
| 1 day | LightGBM | GBM018 |
| 7 days | LightGBM | GBM011 |
| 14 days | XGBoost | GBM022 |
| 28 days | XGBoost | GBM003 |

The mapping was frozen before final evaluation and remains unchanged. Ridge and Seasonal Naive outperform frozen producers on some final horizons; see the complete report. Numerical evidence: [validation-20261002-01](reports/forecasting/validation-20261002-01/comparison.md) and [final-20261003-02](reports/forecasting/final-20261003-02/comparison.md). These generated snapshots remain immutable.

**The full group project remains in progress.** Inventory-risk and replenishment methodology/implementation, responsible decision-support content and prospective API/integration acceptance remain separate work. DR-012 group approval, origin-time inventory semantics, unavailable-input handling, uncertainty and 28-day downstream approval are not settled by forecasting completion. [Integration readiness](docs/integration-contract-readiness.md) lists the remaining handoff work.

## System architecture

~~~text
Local validated source
  -> demand forecasting
  -> temporally aligned inventory-risk / replenishment analysis
  -> responsible decision-support records
  -> shared API integration and approved visuals / prototype
~~~

[Project overview](docs/project-overview.md) explains the architecture; [boundaries](docs/project-boundaries.md) define ownership. A recommendation remains human decision support, not an automatically executable purchase order.

## Team contributions

### [Chathuranga Sudusinghe](docs/team/chathuranga/group-project-overview.md) — Research Team Lead, Forecasting & System Architecture
- Leads overall research coordination and shared system architecture.
- Owns the demand-forecasting research component, including forecasting methodology, feature design, temporal validation, model comparison, model/configuration selection, final holdout evaluation, reproducibility and forecasting evidence.
- Owns forecasting-output meaning and reviews the shared forecast/API contract.
- Coordinates cross-component integration with Tinosh.

### [Didilani Pathinayaka](docs/team/didilani/group-project-overview.md) — Inventory Risk & Replenishment Analysis
- Owns inventory-risk and replenishment methodology.
- Defines and evaluates stockout, overstock and replenishment-risk evidence using approved forecasting outputs and inventory-state variables.
- Owns analytical visuals and business interpretation for the inventory-risk component.
- Reviews the inventory semantics exposed through shared integration outputs.

### [Dewmi Haputhanthrige](docs/team/dewmi/group-project-overview.md) — Responsible Decision Support
- Owns responsible decision-support methodology and governance.
- Defines transparency, limitations, human oversight and management-facing interpretation.
- Develops and reviews responsible presentation of forecasting and inventory-risk evidence.
- Owns decision-support records and responsible-use semantics.

### [Tinosh Gamage](docs/team/tinosh/group-project-overview.md) — System Integration & Prototype Engineering
- Owns cross-component technical integration and final prototype engineering.
- Implements approved adapters, schemas, API/integration tests, technical visual outputs and prototype components.
- Works with Chathuranga on the shared forecast/API integration while preserving the research meaning defined by each component owner.

## Documentation entry points

- Research: [design and hypotheses](docs/research-design.md), [dataset](docs/dataset.md), [literature](docs/literature/literature-review.md), [references](docs/references.md).
- Forecasting contracts: [validated preparation](docs/data-cleaning-and-validation.md), [exact features/preprocessing](docs/forecasting-feature-engineering.md), [experimental protocol](docs/protocol.md), [DR-014 freeze/refit](docs/decisions/DR-014-forecasting-selection-and-final-refit.md).
- Operations/evidence: [runner](docs/forecasting-runner.md), [storage/retention](docs/artifact-storage-policy.md), [report index](reports/README.md), [historical progress](docs/research-progress.md).
- Contribution: [CONTRIBUTING](CONTRIBUTING.md), [AGENTS](AGENTS.md), [decision records](docs/decisions/README.md), [member/workflow boundaries](docs/project-boundaries.md).

## Repository layout

~~~text
retail-demand-framework/
├── src/                              # Reusable implementation by system component
│   ├── data/                         # Shared preparation and validated data handoff
│   │   ├── data_cleaning.py          # Source cleaning and validation
│   │   └── validated_handoff.py      # Controlled validated-data interface
│   ├── forecasting/                  # Demand-forecasting implementation
│   │   ├── features.py               # Forecast predictor construction
│   │   ├── models.py                 # Forecasting model definitions
│   │   ├── validation.py             # Temporal-validation support
│   │   └── final_evaluation.py       # Final holdout evaluation
│   ├── analysis/                     # Reusable research/EDA analysis logic
│   ├── inventory_risk/               # Inventory-risk and replenishment component
│   ├── decision_support/             # Responsible decision-support component
│   └── visualization/                # Approved visual implementation
├── docs/                             # Research, methodology, decisions and ownership
│   ├── decisions/                    # Research/design decision records
│   ├── research/                     # Component research methodology
│   ├── literature/                   # Literature review
│   ├── team/                         # Member responsibilities and contributions
│   ├── meetings/                     # Historical meeting records
│   └── workflows/                    # Component and integration workflows
├── reports/                          # Tracked research evidence and figures
│   ├── forecasting/                  # Validation and final forecasting evidence
│   │   ├── validation-20261002-01/   # Retained validation comparison
│   │   └── final-20261003-02/        # Retained final/test comparison
│   └── figures/                      # Research figures
├── notebooks/                        # Exploratory notebooks
│   └── eda/                          # Demand exploratory analysis
├── tests/                            # Implementation and regression tests
├── data/                             # Local ignored raw/processed data
│   ├── raw/                          # Local source data
│   └── processed/                    # Local processed data
├── artifacts/                        # Local ignored run/evidence artifacts
│   └── forecasting/                  # Forecasting run artifacts
└── models/                           # Local ignored fitted model bundles
    └── forecasting/                  # Forecasting models/preprocessing state
~~~

Code is organized by system component, not student name. Dataset formats, generated tables, artifacts and model binaries stay local; retain .gitignore protections. Setup and safe checks are in CONTRIBUTING. Real preparation and experiments require explicit authorization.

## Usage and permissions

This repository is provided publicly for **academic and educational review**.

No open-source licence is granted for the original project materials in this repository. Unless explicit written permission is obtained from the project authors, the repository content must not be copied, modified, redistributed, commercially reused, or incorporated into another project beyond what is otherwise permitted by applicable law.

Third-party datasets, software libraries, frameworks, and other external materials referenced by this project remain subject to their own licences, terms, and conditions. The project dataset is not distributed in this repository and is not covered by this repository notice.
