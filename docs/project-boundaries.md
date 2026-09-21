# Project Boundaries

## 1. Why this document exists

The programme contains both a **COMP1884 group project** and **COMP1885 individual projects**. They are related, but they are not the same assessment or the same product.

This document prevents the two levels of work from becoming mixed.

## 2. What this repository contains

```text
retail-demand-framework
= COMP1884 GROUP PROJECT REPOSITORY
```

This repository contains:

- shared group documentation;
- shared data-processing code;
- the integrated group prototype;
- member-specific COMP1884 responsibilities;
- high-level COMP1885 plans for context and future continuity.

## 3. What this repository does not contain

It does **not** contain the full implementation of any COMP1885 individual project.

The individual projects should later have separate implementation spaces/repositories.

## 4. Four-project view

Conceptually, the programme work is organised as:

```text
PROJECT 1
COMP1884 Group Project
Retail Demand Decision-Support Framework

PROJECT 2
COMP1885 — Chathuranga
Advanced Time-Series Demand Forecasting

PROJECT 3
COMP1885 — Didilani
Inventory Risk Modelling

PROJECT 4
COMP1885 — Dewmi
Trustworthy and Explainable Decision Support
```

## 5. COMP1884 integration

The group project is still **one project**, not three disconnected projects.

```text
Shared supply-chain data
            |
            v
Chathuranga
Model training, model selection, and demand forecasting
            |
            v
Forecast output
            |
            v
Didilani
Inventory-risk and replenishment analysis
            |
            v
Risk / replenishment output
            |
            v
Dewmi
Responsible decision support and human oversight
            |
            v
Shared integrated COMP1884 product
```

### Member boundaries

**Chathuranga**

```text
Train forecasting models
-> compare/evaluate models
-> select a suitable model
-> forecast future demand
```

**Didilani**

```text
Forecast
+ inventory state / policy variables
-> inventory-risk analysis
-> replenishment recommendation where justified
-> visual/business interpretation
```

**Dewmi**

```text
Forecast
+ inventory-risk / replenishment output
+ uncertainty / assumptions / limitations
-> responsible management-facing decision support
-> human review / managerial judgement
```

Dewmi does not recalculate the primary forecast or replenishment recommendation. Didilani does not retrain the demand-forecasting models.

Shared tasks such as data cleaning, testing, integration, documentation, and final reporting remain group responsibilities.

## 6. COMP1885 independence

Each COMP1885 project must have its own:

- individual research question;
- research aim/objectives;
- distinct or appropriately extended literature review;
- methodology;
- experiment design;
- product/prototype;
- results;
- critical discussion;
- conclusions.

Using the same source dataset does not make the projects identical.

## 7. Reuse rule

Allowed:

- same source dataset;
- shared understanding of the domain;
- group-developed foundations;
- appropriately cited prior group work;
- extension of a COMP1884 component.

Not acceptable:

- treating COMP1884 and COMP1885 as the same submission;
- copying the same experiment and claiming it as a separate research contribution;
- duplicating text/results without appropriate academic handling;
- allowing an individual project to depend on undocumented work that cannot be independently explained.

## 8. Simple member rule

For every member:

```text
COMP1884
= contribution to the shared group product

COMP1885
= separate, deeper individual research project
```
