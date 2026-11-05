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
- coordinated presentation preparation, while each student retains the individual presentation, recording and reflective-essay submission required by the supplied COMP1884 specification.

## 6. Scope control

Changes that materially affect the group research question, dataset, analytical unit, forecasting target, inventory-risk meaning, replenishment logic, evaluation policy, or member ownership must be documented and reviewed before implementation.

Member ownership changes require explicit human approval. FastAPI is a read-only delivery and integration mechanism unless a later decision approves more; it is not a research method.

## 7. Simple member rule

```text
Each member owns a distinct COMP1884 component
+
all components must integrate into one shared group product.
```

## 8. Team, teaching and approval terminology

This is a collaborative group project; “project owner” is not a defined team role. Chathuranga coordinates research as Research Team Lead & Forecasting, while all members retain their documented component responsibilities. “Component owner” describes responsibility for a component only.

Name the person who gave an instruction, reviewed work or authorised execution, and preserve the date, source and exact scope. An individual approval must not be described as group approval. Team decisions and component review remain subject to the existing human review controls.

**Human research workflow — clarified by Chathuranga on 15 October 2026, Issue #165:** The relevant human member reviews and authorises the particular run within the approved component scope and manually executes the reviewed command in their own terminal. Shared-data or cross-component work requires review by the relevant members and a named human executor; decisions requiring group agreement must be discussed and approved by the team. AI assistants may prepare code and explain the exact command, but research execution remains with the human members under [AGENTS §17](../AGENTS.md#17-experiment-execution-responsibility). Read-only inspection and lightweight synthetic implementation checks remain supporting activities, not research decisions or results.

**Human peer review before merge — clarified by Chathuranga on 15 October 2026, Issue #165:** Before code reaches `main`, at least one other human team member must review and approve the author's changes, with the review recorded on the PR. Human reviewers may use AI tools to assist their review, but must assess the changes and make the approval decision themselves. Self-review and AI review alone do not replace this requirement. Substantive later code changes require renewed review. Once approval, resolution of review blockers and required checks are complete, either the human task/PR author or the human reviewer may merge within repository permissions and protections. See [the PR rule](../AGENTS.md#3-pull-request-rule) and [contribution workflow](../CONTRIBUTING.md#6-commit-push-and-pull-request).

**AI Git/GitHub boundaries — clarified by Chathuranga on 15 October 2026, Issue #165:** AI assistants must not create Git branches or open/merge Pull Requests. They provide branch commands and draft PR content/instructions for humans to perform those actions. They may draft or propose a GitHub Issue, but must obtain explicit user permission for that specific Issue before creating it; identifying a need does not grant permission. Other permitted Git operations retain their existing explicit-authorization controls.

Use “COMP1884 lecturer” for the teaching role clarified by Chathuranga, and “module leader” only where that distinct role is evidenced. Teaching guidance does not establish a supervisor appointment or lecturer approval of project methodology. Record any specific confirmation required by the applicable module instructions separately.

The [criteria checklist](greenwich-criteria-checklist.md) maps assessment evidence and unresolved requirements. It does not certify university compliance or grant experiment/Git permission.


## 9. Supplied COMP1884 assessment documents

The supplied 2026/27 coursework specifications and templates now provide the assessment-specific requirements; the [criteria checklist](greenwich-criteria-checklist.md#assessment-requirements-and-current-evidence) and [source register](references.md#university--project-guidance) own their mapping and provenance. The general COMP1884/COMP1885 guidance expects each group member to contribute code to one cohesive product. Preserve actual contribution attribution; this does not transfer existing component responsibilities or assert that any member’s assessment requirements have been met.

Use the COMP1884-specific report/presentation specifications for exact deliverables. Generic references to supervisors in the supplied guidance describe the university’s teaching/advisory process; they do not by themselves identify this group’s appointed contact or change the recorded lecturer terminology. COMP1885 rules and example timelines are not imported as this project’s requirements or deadlines. Final submission-file preparation remains separate from repository completion under #179 → #204.
