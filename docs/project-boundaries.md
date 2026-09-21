# Project Boundaries

## 1. Why this document exists

This document defines the boundaries of the **COMP1884 group project** so the three member contributions remain distinct while still forming one integrated product.

## 2. Repository scope

```text
retail-demand-framework
= COMP1884 GROUP PROJECT REPOSITORY
```

This repository contains:

- shared group documentation;
- shared data-processing code;
- the integrated group prototype;
- member-specific COMP1884 responsibilities;
- meeting, decision, issue, and Pull Request evidence;
- testing, evaluation, and report-support material for the group project.

## 3. Integrated group structure

The project is one integrated system, not three disconnected mini-projects.

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

## 4. Member boundaries

### Chathuranga

```text
Train forecasting models
-> compare/evaluate models
-> select a suitable model
-> forecast future demand
```

Primary boundary: Chathuranga produces the forecasting output required by the downstream inventory component.

### Didilani

```text
Forecast
+ inventory state / policy variables
-> inventory-risk analysis
-> replenishment recommendation where justified
-> visual/business interpretation
```

Primary boundary: Didilani consumes the forecast and does not retrain the forecasting models.

### Dewmi

```text
Forecast
+ inventory-risk / replenishment output
+ uncertainty / assumptions / limitations
-> responsible management-facing decision support
-> human review / managerial judgement
```

Primary boundary: Dewmi does not recalculate the primary forecast or replenishment recommendation.

## 5. Shared responsibilities

The following remain group responsibilities:

- shared data-quality and preprocessing decisions;
- integration contracts between components;
- testing and validation;
- research and methodology decisions that affect multiple components;
- repository governance and collaboration;
- meeting and decision records;
- final integration;
- group report preparation;
- presentation preparation.

## 6. Scope control

Changes that materially affect the group research question, dataset, analytical unit, forecasting target, inventory-risk meaning, replenishment logic, evaluation policy, or member ownership must be documented and reviewed before implementation.

## 7. Simple member rule

```text
Each member owns a distinct COMP1884 component
+
all components must integrate into one shared group product.
```
