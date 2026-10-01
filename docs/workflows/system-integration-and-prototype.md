# System Integration and Prototype Workflow

Repository-wide authorities: [data lifecycle](../workflows/shared-data-foundation.md), [storage and retention](../artifact-storage-policy.md), [applied MLOps](../workflows/applied-mlops.md), [research reporting](../../reports/README.md), and [continuous progress log](../research-progress.md). These connect existing scientific/component contracts without replacing them.

## Owner and purpose

Primary technical owner: **Tinosh Gamage — System Integration and Prototype Engineering**. FastAPI/API integration is shared with **Chathuranga — Research Team Lead & Forecasting**. This workflow delivers the existing COMP1884 research components as one reviewable prototype; it does not establish new research methodology.

## Workflow

```text
Reviewed forecast, inventory-risk and responsible decision-support outputs
        |
        v
Component-owner review of identity, timing, provenance and availability
        |
        v
Agreed interchange contracts and integration adapters
        |
        +--> Chathuranga + Tinosh: shared read-only FastAPI integration
        |
        +--> Tinosh: approved technical visual outputs
        |
        v
API, visual and cross-component integration tests
        |
        v
Tinosh: final prototype assembly and reproducibility checks
        |
        v
Component-owner review of the integrated output
        |
        v
Integrated COMP1884 framework for human consideration
```

Reviewed outputs can be integrated as they become available; this is not a requirement to complete every component in a strict sequence.

## Contracts and adapters

Keep `SKU_ID`, `Warehouse_ID`, forecast origin, horizon, target-window meaning, model/source provenance, assumptions, limitations and unavailable-state reasons traceable across handoffs. Keep retrospective outcomes and error evidence separate from prospective outputs. Final field names, types and formats require agreement before implementation. Do not resolve unknown origin-snapshot semantics, problematic forecast handling or 28-day downstream use through adapter defaults.

Chathuranga reviews forecasting-facing contract meaning and API architecture. Didilani reviews inventory-risk evidence and analytical visual specifications. Dewmi reviews responsible decision-support record semantics and management-facing presentation. Tinosh implements the agreed technical contracts and adapters.

## FastAPI and visual delivery

The initial FastAPI layer is read-only and presentation-oriented. It may expose reviewed forecasts, inventory-risk evidence, responsible decision-support records, contract/provenance metadata and health/status information. Chathuranga and Tinosh share API integration: Chathuranga leads architecture and forecasting semantics; Tinosh implements endpoints, schemas, adapters and tests.

Tinosh implements approved charts and prototype visual components. The relevant analytical owner defines what the visual means and reviews labels, horizon, evidence and limitations. Technical visual delivery does not transfer ownership of inventory-risk interpretation from Didilani or responsible presentation from Dewmi.

## Validation and boundaries

Use focused integration, API and visual tests to check identity, origin and horizon alignment, component provenance, unavailable-state reasons, and preservation of advisory-only output. Record reproducibility steps and known technical limitations. Component owners review the integrated representation before it is treated as the final prototype.

The API must not train or select models on request, silently recalculate or invent analytical rules, create replenishment actions, hide unavailable information, or use future outcome information in prospective views. It must not imply that 28-day forecast availability approves 28-day inventory interpretation. No experiment execution is authorised by this workflow; separate research, experiment and human-approval controls in `AGENTS.md` remain in force.
