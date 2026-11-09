# A Data-Driven Decision Support Framework for Retail Demand Forecasting and Inventory Risk Analysis: A Comparative Study of Gradient-Boosted Decision Trees

**University:** University of Greenwich<br>
**Programme:** MSc Data Science and Its Applications<br>
**Module:** COMP1884 Group Project<br>
**Research type:** Group research project

## Research problem and aim

This project investigates how demand forecasts can be connected to inventory-state information and transparent advisory outputs. It asks:

> How can data-driven demand forecasting be used to identify inventory risks and support supply-chain decision-making in retail operations?

The framework combines forecasting, conditional inventory exposure and responsible decision support at SKU-warehouse level. The [project overview](docs/project-overview.md#7-supporting-research-questions) defines the supporting questions; [research design](docs/research-design.md) defines the hypotheses and claim boundaries.

## Contribution and key findings

- **Forecasting:** a matched, chronologically evaluated comparison of XGBoost, LightGBM and CatBoost for next-day and cumulative 7-, 14- and 28-day demand. In the final evaluation, supportive Ridge achieved the lowest WAPE at 1/7 days and contextual Seasonal Naive at 14/28 days; no universal boosting superiority is claimed.
- **Inventory exposure:** the group-approved [DR-012 method](docs/decisions/DR-012-inventory-risk-replenishment-methodology.md#group-approval-record) links forecasts to a fixed-origin, fixed-reorder-point, no-receipt scenario for 1/7/14 days. Its retrospective comparison uses a realised-demand proxy, rather than actual stockout labels.
- **Responsible decision support:** 20 traceable advisory records with 160 human-entered transparency checks preserve assumptions, limitations, unavailable information and the distinction between transparency assessment and managerial review.
- **Technical delivery:** a local FastAPI service provides request-time forecasts from supplied history and read-only access to retained decision-support cases. Eight research figures with PNG/SVG outputs and evidence sidecars are delivered in [final-thesis-figures](reports/figures/final-thesis-figures/README.md).

The designated producers were frozen before final evaluation and remain unchanged:

| Horizon | Frozen producer | Configuration |
|---|---|---|
| 1 day | LightGBM | GBM018 |
| 7 days | LightGBM | GBM011 |
| 14 days | XGBoost | GBM022 |
| 28 days | XGBoost | GBM003 |

[Final results and limitations](docs/forecasting-final-evaluation.md) explain the comparison, evidence roles and prior outcome exposure. The retained [validation](reports/forecasting/validation-20261002-01/comparison.md) and [final comparison](reports/forecasting/final-20261003-02/comparison.md) snapshots remain immutable.

## Dataset

The project uses Ziya's published [High-Dimensional Supply Chain Inventory Dataset](https://www.kaggle.com/datasets/ziya07/high-dimensional-supply-chain-inventory-dataset), downloaded from Kaggle. Its 91,250 records cover 50 SKUs across five warehouses over 365 dates in 2024. **The records are simulated by the publisher; the team did not generate a replacement dataset.**

Forecasts are built from historical `Units_Sold` at `SKU_ID + Warehouse_ID + Date` grain. The [dataset contract](docs/dataset.md) documents the fields, selection rationale and limitations. Data and model bundles remain local and are not distributed with this repository.

## Methods and system architecture

The architecture separates the retained research case from request-time forecast serving:

~~~mermaid
flowchart TB
    DATA[("Published Kaggle dataset")]
    PREP["Shared validation and preparation"]
    RESEARCH["Frozen features and chronological model comparison"]
    MODELS["Saved designated forecasting models"]
    EXPORT["Retained prospective forecasts<br/>Origin: 2024-12-02"]
    CONTEXT["Constructed origin inventory context<br/>Source timing unknown"]
    INVENTORY["DR-012 threshold-exposure evidence<br/>1/7/14-day scope"]
    RECORDS["Responsible decision-support records"]
    RETAINED["Read-only retained-case GET routes"]
    VIEWS["Retained-case presentation and approved views"]
    HISTORY["Supplied daily history"]
    LIVE["Request-time POST /forecasts"]
    HUMAN["Human review and judgement"]

    DATA --> PREP --> RESEARCH
    RESEARCH --> MODELS
    RESEARCH --> EXPORT
    PREP --> CONTEXT
    EXPORT --> INVENTORY
    CONTEXT --> INVENTORY
    EXPORT --> RECORDS
    INVENTORY --> RECORDS --> RETAINED --> VIEWS --> HUMAN
    MODELS --> LIVE
    HISTORY --> LIVE --> HUMAN
~~~

Both serving paths use the shared FastAPI application. Changing supplied history creates a new forecast; it does not recompute retained inventory or decision-support evidence. Multi-day forecasts are cumulative totals, not daily paths. Retrospective outcomes and metrics belong in separately labelled evaluation views and are excluded from prospective inputs.

## Scope and limitations

- Conclusions describe a publisher-simulated dataset covering approximately one year; real-retailer effectiveness is not established.
- Temporal evaluation preserves chronology. Prior final-period validation/EDA exposure, the failed first final execution and dependent histories remain disclosed in the research documentation.
- Inventory findings depend on the constructed no-receipt scenario. Source inventory timing is unknown, and zero-variance `Stockout_Flag` cannot validate actual stockouts.
- Primary and provisional temporal significance claims are **untested** under the team-accepted descriptive scope. Forecast-error comparisons and transparency checks do not establish improved managerial decisions.
- Prospective uncertainty estimation, numerical replenishment, overstock, automatic managerial-review rules and 28-day inventory use are disclosed limitations/deferred extensions. A 28-day forecast does not approve downstream 28-day inventory use.
- Outputs are advisory and do not create executable purchase orders. Missing or unapproved information remains explicitly unavailable.

## Getting started

1. Follow [CONTRIBUTING: one-time setup](CONTRIBUTING.md#1-one-time-setup) for the project environment and dependencies.
2. Read [AGENTS.md](AGENTS.md), the relevant component workflow and [local file verification](docs/checksums/README.md) before using shared artifacts.
3. Use the [forecast API instructions](docs/forecast-inference-api.md#6-manual-presentation) for local startup and request examples, and [Section 5.1](docs/forecast-inference-api.md#51-retained-decision-support-cases) for the separate retained routes. Required data/models stay local; missing sources produce explicit unavailable responses.

Research preparation, training and evaluation remain specifically authorised human-run activities. Setup instructions are not standing experiment or Git permission.

## Documentation map

- **Research:** [results and interpretation](docs/results.md), [design and decisions](docs/research-design.md), [literature review](docs/literature/literature-review.md), [references](docs/references.md), [shared report](docs/group-report.md).
- **Data and forecasting:** [dataset](docs/dataset.md), [validated preparation](docs/data-cleaning-and-validation.md), [features](docs/forecasting-feature-engineering.md), [protocol](docs/protocol.md), [DR-014 producer freeze](docs/decisions/DR-014-forecasting-selection-and-final-refit.md), [results](docs/forecasting-final-evaluation.md).
- **Inventory and responsible use:** [inventory interpretation and visual specification](docs/research/inventory-risk-visual-evidence.md), [responsible decision-support evaluation](docs/research/responsible-decision-support-evaluation.md).
- **Contracts and integration:** [request-time API](docs/forecast-inference-api.md), [retained-export contract](docs/forecast-api-contract.md), [integration readiness](docs/integration-contract-readiness.md), [integration workflow](docs/workflows/system-integration-and-prototype.md).
- **Evidence and operations:** [report index](reports/README.md), [runner](docs/forecasting-runner.md), [storage policy](docs/artifact-storage-policy.md), [progress history](docs/research-progress.md).
- **Assessment and collaboration:** [COMP1884 criteria checklist](docs/greenwich-criteria-checklist.md), [AI-use guidance](docs/university-ai-guidance.md), [project boundaries](docs/project-boundaries.md), [contribution workflow](CONTRIBUTING.md).

## Team contributions

- **[Chathuranga Sudusinghe](docs/team/chathuranga/group-project-overview.md):** research-team coordination, forecasting methodology, model comparison/evaluation, output meaning and shared API architecture/review.
- **[Didilani Pathinayaka](docs/team/didilani/group-project-overview.md):** inventory-risk/replenishment methodology, analytical visual requirements and business interpretation. Her implementation contributions include the retained-case interface and inventory views.
- **[Dewmi Haputhanthrige](docs/team/dewmi/group-project-overview.md):** responsible decision-support semantics, transparency, governance, human oversight and presentation review.
- **[Tinosh Gamage](docs/team/tinosh/group-project-overview.md):** technical integration, adapters, API/integration checks and prototype engineering.

Chathuranga is the recorded executor of the retained inventory evaluation and assessor of the 160 record-level checks. That attribution does not transfer Didilani's inventory or Dewmi's responsible-use responsibilities. [Project boundaries](docs/project-boundaries.md) define the permanent roles.

## Repository layout

~~~text
retail-demand-framework/
├── src/
│   ├── data/                  # Shared validation and data handoff
│   ├── analysis/              # Reusable descriptive analysis
│   ├── forecasting/           # Features, experiments, artifacts and inference
│   ├── inventory_risk/        # Scenario preparation, mapping and evaluation
│   ├── decision_support/      # Advisory records, assessment and retained cases
│   ├── api/                   # Shared FastAPI delivery
│   └── visualization/         # Inventory views and eight-figure rendering
├── examples/forecast-api/     # Synthetic request-time input examples
├── capture_consumer_evidence.py # Existing request-time evidence helper
├── tests/                    # Implementation and regression checks
├── notebooks/                # Historical exploration
├── docs/                     # Research, contracts, decisions and workflows
├── reports/
│   ├── forecasting/           # Retained comparison snapshots
│   ├── inventory-risk/        # Constructed-scenario evidence
│   ├── decision-support/      # Record and assessment evidence
│   └── figures/               # Reviewed research figures
├── research-materials/       # Local materials; named #203 evidence exception
├── data/                     # Local ignored raw and processed data
├── artifacts/                # Local ignored run evidence
└── models/                   # Local ignored fitted model bundles
~~~

Code is organised by component. The [storage policy](docs/artifact-storage-policy.md) identifies the exact trackable exceptions, including two synthetic request-time evidence files under `research-materials/issue-203/`; other local materials and dataset/model protections remain in force.

## Usage and permissions

This repository contains academic project materials for educational review.

No open-source licence is granted for the original project materials in this repository. Unless explicit written permission is obtained from the project authors, the repository content must not be copied, modified, redistributed, commercially reused, or incorporated into another project beyond what is otherwise permitted by applicable law.

Third-party datasets, software libraries, frameworks, and other external materials referenced by this project remain subject to their own licences, terms, and conditions. The project dataset is not distributed in this repository and is not covered by this repository notice.
