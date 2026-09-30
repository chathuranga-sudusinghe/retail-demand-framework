# Project Boundaries

## 1. Why this document exists

This document defines the boundaries of the **COMP1884 group project** so the four member contributions remain distinct while still forming one integrated product.

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

The four contributions form one integrated system.

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
Responsible management-facing records
            |
            v
Chathuranga + Tinosh
Shared API integration
            |
            v
Tinosh
Technical visualisation and prototype engineering
            |
            v
Shared integrated COMP1884 product
```

Reviewed component outputs may be integrated as they become available; the engineering work need not be strictly sequential.

## 4. Member boundaries

### Chathuranga

```text
Train forecasting models
-> compare/evaluate models
-> select a suitable model
-> forecast future demand
```

Primary boundary: Chathuranga leads research-team coordination and produces the forecasting output required by the downstream inventory component. He shares API architecture and integration design with Tinosh and reviews forecasting-facing contracts, provenance, origin and horizon handling.

### Didilani

```text
Forecast
+ inventory state / policy variables
-> inventory-risk analysis
-> replenishment recommendation where justified
-> analytical visual requirements and business interpretation
```

Primary boundary: Didilani consumes the forecast and does not retrain the forecasting models. She defines, documents and interprets inventory-risk evidence and reviews whether technical visuals represent it correctly; Tinosh implements approved visual outputs.

### Dewmi

```text
Forecast
+ inventory-risk / replenishment output
+ uncertainty / assumptions / limitations
-> responsible management-facing decision support
-> human review / managerial judgement
```

Primary boundary: Dewmi does not recalculate the primary forecast or replenishment recommendation. She owns decision-support record meaning and reviews its presentation in the prototype.

### Tinosh

```text
Reviewed component outputs
-> agreed interchange contracts and adapters
-> technical implementation of approved visuals
-> tested API and prototype delivery
```

Primary boundary: Tinosh owns system integration and prototype engineering. He shares FastAPI/API integration with Chathuranga, implementing endpoints, schemas, adapters and tests under reviewed contracts. He does not select models or create forecasting, inventory-risk, replenishment, uncertainty or human-review methodology.

## 5. Shared responsibilities

The following remain group responsibilities:

- shared data-quality and preprocessing decisions;
- integration contracts between components;
- testing and validation;
- research and methodology decisions that affect multiple components;
- repository governance and collaboration;
- meeting and decision records;
- final integration, led technically by Tinosh with component-owner review;
- group report preparation;
- presentation preparation.

## 6. Scope control

Changes that materially affect the group research question, dataset, analytical unit, forecasting target, inventory-risk meaning, replenishment logic, evaluation policy, or member ownership must be documented and reviewed before implementation.

Member ownership changes require explicit human approval. FastAPI is a read-only delivery and integration mechanism unless a later decision approves more; it is not a research method.

## 7. Simple member rule

```text
Each member owns a distinct COMP1884 component
+
all components must integrate into one shared group product.
```
