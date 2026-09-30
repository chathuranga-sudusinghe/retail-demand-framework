# Tinosh Gamage — COMP1884 Group Project Contribution

## Member details

**Name:** Tinosh Gamage

## Role

**System Integration and Prototype Engineering**

## Purpose in the group system

Tinosh makes the reviewed forecasting, inventory-risk and responsible decision-support outputs work together in the final COMP1884 prototype. His contribution is technical integration within the existing research framework, not a new research question, hypothesis or analytical method.

## Dependencies and expected inputs

- Chathuranga's reviewed forecast outputs and forecasting-facing contract, including `SKU_ID`, `Warehouse_ID`, forecast origin, horizon, target-window meaning and model provenance.
- Didilani's reviewed inventory-risk evidence, analytical visual requirements, assumptions, limitations and interpretation.
- Dewmi's reviewed responsible decision-support records, unavailable-state semantics, management-facing meaning and human-review criteria.
- Agreed cross-component interchange contracts and explicit decisions about origin snapshot availability before any dependent integration.

The final schemas remain open. A 28-day forecast can be represented without implying approval for 28-day inventory interpretation or human-review triggers.

## Responsibilities

1. Implement agreed cross-component adapters and interchange contracts without changing the producing component's calculations.
2. Build the technical implementation of approved visual outputs, reusable chart/rendering code and prototype visual components.
3. Assemble the end-to-end prototype from reviewed component outputs as they become available.
4. Implement and test the shared API delivery layer with Chathuranga.
5. Add integration and API tests for identity, origin/horizon alignment, provenance, unavailable information and advisory-only behaviour.
6. Perform reproducibility and technical validation checks for the integrated prototype, reporting failures and limitations.

## Shared FastAPI/API responsibility

Chathuranga leads API architecture and integration design, owns forecasting-facing contracts, and reviews forecasting output semantics and shared API behaviour. Tinosh implements endpoints, request/response schemas, adapters, API tests and prototype-facing delivery. The relevant component owner reviews any representation of their output. FastAPI is a delivery mechanism, not a research method; initial delivery is read-only and presentation-oriented unless a later explicit approval changes that boundary.

## Visualisation and component-owner review

Didilani defines the analytical requirements, meaning, documentation, business interpretation and conclusions for inventory-risk visuals. Tinosh implements the approved technical rendering and checks that it preserves labels, horizon, provenance, assumptions and limitations. Didilani reviews the analytical meaning. Dewmi reviews presentation of responsible decision-support records and human-review information.

## Expected outputs

- Reviewed component adapters and documented technical interchange schemas.
- Read-only API responses and prototype views that preserve component provenance and unavailable-state reasons.
- Reusable technical visual components based on approved analytical specifications.
- Integration, API and visual integration test results.
- A reproducible integrated prototype with documented technical limitations.

These are engineering deliverables, not final research evidence or approval of unresolved upstream methods.

## Boundaries

Tinosh must not independently choose forecasting models, alter forecasting methodology or validation, redefine inventory-risk or responsible decision-support rules, invent replenishment quantities, uncertainty methods or human-review thresholds, or treat the API as authority to execute orders. Prospective views must not use future outcomes. Missing or unapproved information remains explicitly unavailable rather than zero or `false`.

The simulated dataset stays local under the repository dataset rules. Current inventory-risk, replenishment, 28-day downstream and human-review approval boundaries remain in force. Tinosh's technical work requires review by Chathuranga, Didilani and Dewmi where it represents their respective components.
