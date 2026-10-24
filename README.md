# A Data-Driven Decision Support Framework for Retail Demand Forecasting and Inventory Risk Analysis: A Comparative Study of Gradient-Boosted Decision Trees

**University:** University of Greenwich<br>
**Programme:** MSc Data Science and Its Applications<br>
**Module:** COMP1884 Group Project<br>
**Research type:** Group research project

## Research overview

This group project builds a data-driven decision-support framework connecting demand forecasts, inventory-risk/replenishment analysis and responsible management-facing outputs. Its forecasting component compares gradient-boosted decision-tree models—XGBoost, LightGBM and CatBoost—under matched inputs and chronological evaluation. It uses the published [High-Dimensional Supply Chain Inventory Dataset](https://www.kaggle.com/datasets/ziya07/high-dimensional-supply-chain-inventory-dataset) from Kaggle, selected for its linked daily sales and inventory variables supporting analysis at SKU-warehouse level. The publisher-simulated records support evaluation within this dataset; results do not establish effectiveness in a real retailer.

## Dataset source

**Original dataset:** [High-Dimensional Supply Chain Inventory Dataset — Kaggle](https://www.kaggle.com/datasets/ziya07/high-dimensional-supply-chain-inventory-dataset)

**Publisher:** Ziya on Kaggle.

The research uses the dataset downloaded from this published source. The project team did not generate a replacement research dataset. The [dataset contract](docs/dataset.md#11-suitability-for-the-project-research-purpose) documents the selection rationale, verified profiling evidence, source context and limitations.

## Current project state

**Status checked:** 24 October 2026. The [overall delivery tracker, Issue #179](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/179), records current tasks, review outcomes and outstanding approvals for all members. Closed task issues identify delivered milestones; remaining acceptance is tracked there.

Chathuranga's forecasting research is complete: preparation, development, validation, configuration/model freeze, final holdout evaluation and integrity verification, as confirmed by Chathuranga. [Final results and limitations](docs/forecasting-final-evaluation.md) consolidate the evidence and interpretation for human review.

| Horizon | Frozen producer | Configuration |
|---|---|---|
| 1 day | LightGBM | GBM018 |
| 7 days | LightGBM | GBM011 |
| 14 days | XGBoost | GBM022 |
| 28 days | XGBoost | GBM003 |

The mapping was frozen before final evaluation and remains unchanged. Ridge and Seasonal Naive outperform frozen producers on some final horizons; see the complete report. Numerical evidence: [validation-20261002-01](reports/forecasting/validation-20261002-01/comparison.md) and [final-20261003-02](reports/forecasting/final-20261003-02/comparison.md). These generated snapshots remain immutable.

**The full group project remains in progress.** Delivered component evidence and remaining integration work are distinct:

| Area | Delivered | Remaining work / acceptance |
|---|---|---|
| Forecast serving | [Request-time API](docs/forecast-inference-api.md), four synthetic JSON examples and recorded manual outcomes; validation-error and input-provenance fixes merged through [PR #195](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/195) | Producer approval, independently reviewed source verification and Tinosh's technical consumer acceptance remain tracked in #179. |
| Inventory scenario | Forecast-to-inventory mapping, runner and [retained 1/7/14-day constructed-origin evaluation](reports/inventory-risk/issue-164/evaluation-v1/report.md); [canonical interpretation review](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/181#issuecomment-6380707367) and [shared-report Section 6 review](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/190#pullrequestreview-5637154678) recorded | Technical consumption, rendered visuals, Didilani's D2 review and responsible-presentation acceptance remain separate. Documentation alignment is tracked under [#192](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/192). |
| Responsible decision support | [20 prepared records and 160 completed human-entered checks](reports/decision-support/issue-168-inventory-v1/summary.md): 15 inventory-linked cases and five h28 cases with downstream inventory gated | Dewmi's final interpretation/display mappings under [#182](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/182), actual rendered readability and consumer acceptance remain pending. |
| Integrated prototype | Existing forecast API, retained-export mapping, prospective record bridge and [AS-01–AS-10 requirements](docs/integration-contract-readiness.md#12-integration-acceptance-scenarios-issue-101) | Tinosh's [#183 retained-case slice](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/183), approved visual implementation and cross-component acceptance remain in progress. |
| Research synthesis and shared report | [Evidence-to-conclusion draft](docs/research-design.md#16-evidence-to-conclusion-mapping--draft-for-human-review) and [shared report draft](docs/group-report.md), including reviewed inventory material | Group hypothesis/scope decisions, remaining member contributions, verified assessment requirements and final team/report review remain unresolved under #179. |

[DR-012 group approval](docs/decisions/DR-012-inventory-risk-replenishment-methodology.md#group-approval-record) covers the documented 1/7/14-day fixed-origin, fixed-reorder-point, no-receipt scenario. It was reported by Chathuranga on 23 October for the 12 October WhatsApp discussion. Source inventory timing remains unknown. Uncertainty estimates, numerical replenishment, overstock rules, automatic managerial-review triggers and 28-day inventory use are outside the delivered approved methods.

Chathuranga is the recorded executor of the retained inventory evaluation and assessor of the 160 record-level checks. Didilani retains inventory methodology/interpretation responsibility; Dewmi retains responsible decision-support semantics and review responsibility. Completed records and checklists do not establish actual stockout accuracy, managerial benefit or final prototype acceptance.

## System architecture

Green indicates completed data preparation/forecasting research; amber indicates implemented component functionality or reviewed evidence with remaining handoff/acceptance work; blue indicates the remaining integrated prototype and human-facing delivery. Dashed arrows indicate conditional or not-yet-accepted handoffs.

~~~mermaid
flowchart TB
    DATA[("Kaggle dataset<br/>SKU_ID + Warehouse_ID + Date")]
    PREP["Shared data preparation<br/>Cleaning, validation and provenance"]
    HISTORY["Supplied daily history<br/>Four synthetic request examples included"]

    DATA --> PREP

    subgraph CH["Chathuranga — Research Lead and Forecasting"]
        FEATURES["Frozen feature pipeline<br/>Identity, weekday, lags, rolling statistics and trend"]
        RESEARCH["Model comparison and temporal validation<br/>Human-approved freeze and final evaluation"]
        MODELS["Saved designated producers<br/>1 day: LightGBM GBM018<br/>7 days: LightGBM GBM011<br/>14 days: XGBoost GBM022<br/>28 days: XGBoost GBM003"]
        EVIDENCE["Retained research evidence<br/>Validation/final predictions and reports"]
        FORECAST["Retained forecast export implemented<br/>Fixed origin 2024-12-02; acceptance separate"]

        FEATURES --> RESEARCH
        RESEARCH --> MODELS
        RESEARCH --> EVIDENCE
        EVIDENCE --> FORECAST
    end

    PREP --> FEATURES

    subgraph DI["Didilani — Inventory Risk and Replenishment"]
        SNAPSHOT["Constructed origin inventory snapshot<br/>Source timing unknown; assumption disclosed"]
        INVENTORY["Mapping and scenario evaluation implemented<br/>Method approved; source timing unknown"]
        INTERPRET["Inventory interpretation/report wording reviewed<br/>Technical rendering and D2 review remain"]

        SNAPSHOT -.-> INVENTORY
        INVENTORY --> INTERPRET
    end

    PREP -.-> SNAPSHOT
    FORECAST -.->|"Retained-export mapping implemented; acceptance pending"| INVENTORY

    subgraph DE["Dewmi — Responsible Decision Support"]
        RECORD["20 decision-support records<br/>15 inventory-linked; five h28 inventory-gated"]
        ASSESS["20 records; 160 record-level checks completed<br/>Rendered presentation acceptance pending"]

        RECORD --> ASSESS
    end

    FORECAST -.-> RECORD
    INVENTORY -->|"Implemented prospective evidence bridge"| RECORD

    subgraph TI["Tinosh — Integration and Prototype Engineering"]
        API["Request-time forecast API implemented<br/>Supplied history and frozen saved models"]
        ACCEPT["AS-01 to AS-10 specified<br/>Integrated acceptance remains under Issue 179"]
        PROTOTYPE["Joined retained-case flow and approved visuals<br/>Implementation/acceptance under Issue 183"]

        ACCEPT -.-> PROTOTYPE
    end

    HISTORY --> API
    MODELS --> API
    API -.->|"Separate live-inference view"| PROTOTYPE
    ASSESS -.-> PROTOTYPE
    INTERPRET -.->|"Approved analytical visual requirements"| PROTOTYPE

    PROTOTYPE -.-> HUMAN["Human review and managerial judgement<br/>Advisory decision support"]

    classDef complete fill:#dcfce7,stroke:#15803d,color:#14532d;
    classDef pending fill:#fef3c7,stroke:#b45309,color:#78350f;
    classDef planned fill:#dbeafe,stroke:#2563eb,color:#1e3a8a;

    class DATA,PREP,FEATURES,RESEARCH,MODELS,EVIDENCE complete;
    class HISTORY,FORECAST,SNAPSHOT,INVENTORY,INTERPRET,RECORD,ASSESS,API,ACCEPT pending;
    class PROTOTYPE,HUMAN planned;
~~~

[Project overview](docs/project-overview.md) explains the architecture; [boundaries](docs/project-boundaries.md) define ownership. The live API computes a new forecast from supplied history; it does not recompute the retained inventory/decision-support case. Multi-day quantities remain cumulative totals, and a 28-day forecast does not approve 28-day inventory use. A recommendation remains human decision support, not an automatically executable purchase order.

## Team contributions

### [Chathuranga Sudusinghe](docs/team/chathuranga/group-project-overview.md) — Research Team Lead, Forecasting & System Architecture
- Leads overall research coordination and shared system architecture.
- Owns the demand-forecasting research component, including forecasting methodology, feature design, temporal validation, model comparison, model/configuration selection, final holdout evaluation, reproducibility and forecasting evidence.
- Owns forecasting-output meaning and reviews the shared forecast/API contract.
- Coordinates cross-component integration with Tinosh.

### [Didilani Pathinayaka](docs/team/didilani/group-project-overview.md) — Inventory Risk & Replenishment Analysis
- Owns inventory-risk and replenishment methodology.
- Owns the approved reorder-threshold exposure interpretation, its assumptions, limitations and analytical visual requirements.
- Owns analytical visuals and business interpretation for the inventory-risk component.
- Delivered the inventory interpretation and reviewed its shared-report insertion; reviews inventory meaning in actual rendered outputs when available. Overstock rules and numerical replenishment remain separate methodological work.

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

- Current delivery and approvals: [Issue #179](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/179), the single umbrella for all members' milestones, pending reviews and subsequent decisions.
- Shared writing: [group report draft](docs/group-report.md), assembled through the closed #187 milestone; remaining assembly and component/team acceptance are tracked in #179.
- Research: [design and hypotheses](docs/research-design.md), [dataset](docs/dataset.md), [literature](docs/literature/literature-review.md), [references](docs/references.md).
- Forecasting contracts: [validated preparation](docs/data-cleaning-and-validation.md), [exact features/preprocessing](docs/forecasting-feature-engineering.md), [experimental protocol](docs/protocol.md), [DR-014 freeze/refit](docs/decisions/DR-014-forecasting-selection-and-final-refit.md).
- Serving and handoffs: [request-time API](docs/forecast-inference-api.md), [retained-export contract](docs/forecast-api-contract.md), [integration readiness](docs/integration-contract-readiness.md), [inventory visual/interpretation source](docs/research/inventory-risk-visual-evidence.md), [responsible decision-support assessment](docs/research/responsible-decision-support-evaluation.md).
- Operations/evidence: [runner](docs/forecasting-runner.md), [storage/retention](docs/artifact-storage-policy.md), [report index](reports/README.md), [historical progress](docs/research-progress.md).
- Contribution: [CONTRIBUTING](CONTRIBUTING.md), [AGENTS](AGENTS.md), [decision records](docs/decisions/README.md), [member/workflow boundaries](docs/project-boundaries.md).
- Assessment requirements: [COMP1884 criteria checklist](docs/greenwich-criteria-checklist.md), including programme evidence, submission requirements, team/lecturer roles and remaining verification gaps.
- Academic AI assistance: [university guidance and source evidence](docs/university-ai-guidance.md), including dated references and assessment permissions still requiring confirmation.

## Repository layout

~~~text
retail-demand-framework/
├── src/                              # Reusable implementation by system component
│   ├── data/                         # Shared preparation and validated data handoff
│   │   ├── data_cleaning.py          # Source cleaning and validation
│   │   └── validated_handoff.py      # Controlled validated-data interface
│   ├── api/
│   │   └── main.py                   # Existing health and request-time forecast routes
│   ├── forecasting/                  # Demand-forecasting implementation
│   │   ├── features.py               # Forecast predictor construction
│   │   ├── inference.py              # Saved-model inference from supplied history
│   │   ├── export.py                 # Deterministic retained prospective export
│   │   ├── models.py                 # Forecasting model definitions
│   │   ├── validation.py             # Temporal-validation support
│   │   └── final_evaluation.py       # Final holdout evaluation
│   ├── analysis/                     # Reusable research/EDA analysis logic
│   ├── inventory_risk/               # Inventory-risk and replenishment component
│   ├── decision_support/             # Records, prospective evidence bridge and assessment
│   └── visualization/                # Approved visual rendering (pending)
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
│   ├── raw/                          # Source data downloaded from Kaggle
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
