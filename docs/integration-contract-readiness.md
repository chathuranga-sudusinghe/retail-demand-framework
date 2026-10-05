# Integration Contract Readiness — Component Handoff Map

**Issue:** #87 — Docs: map component handoff contracts and integration blockers
**Prepares:** Issue #86 (later integration implementation; remains open)
**Owner:** Tinosh Gamage — System Integration and Prototype Engineering
**Reviewers:** Chathuranga (forecasting-facing accuracy), Didilani (inventory-risk / replenishment references), Dewmi (responsible decision-support references)
**Updated:** 2026-10-05 for the owner-requested saved-model inference API and presentation inputs.
**Status:** The retained exporter is implemented and a local derivative exists. Chathuranga has requested a saved-model request-time API in place of stored-forecast serving; its implementation and four synthetic input examples are prepared on the feature branch for review. Manual demonstration and Tinosh's consumer acceptance remain pending (B2). Other component decisions and review requirements are unchanged.

---

## 1. Purpose and boundaries

This document maps the handoffs that currently exist, or are currently documented, between:

1. forecasting (Chathuranga);
2. inventory-risk / replenishment analysis (Didilani);
3. responsible decision support (Dewmi);
4. later prototype / API integration (Tinosh, with Chathuranga for API architecture).

It records what each source already says, separates what is implemented from what is only agreed or proposed, and lists the blockers that must be resolved before Issue #86 can be implemented.

This document does **not**:

- define final shared schemas, field names, types or interchange formats;
- resolve any approval-pending decision;
- propose solutions for blockers;
- describe any unfinished output as available;
- change any research methodology or authorise any experiment.

Governing rules: [AGENTS.md](../AGENTS.md) Sections 4, 9, 17 and 19; [System integration workflow](workflows/system-integration-and-prototype.md).

### 1.1 Status vocabulary used in this document

| Label | Meaning |
|---|---|
| **Implemented / frozen** | Exists in merged source code or in a human-approved, frozen record. |
| **Structure-only agreement** | Accepted as a structure (field groups, concepts), with contents, names and types still open. |
| **Proposed** | Written down as a method, but group / owner approval is still pending. |
| **Unresolved** | Explicitly recorded as open by an existing source; no decision exists yet. |

---

## 2. Sources reviewed

| Source | What it supplies for this map |
|---|---|
| [AGENTS.md](../AGENTS.md) | Ownership boundaries, research-decision rule, dataset rule, experiment execution rule |
| [docs/protocol.md](protocol.md) | Frozen forecasting validation protocol (`issue-65-matched-frozen-1`), artifact schemas, human approval boundaries |
| [src/forecasting/artifacts.py](../src/forecasting/artifacts.py) | Exact implemented artifact column names and schema version |
| [src/forecasting/targets.py](../src/forecasting/targets.py) | Exact meaning of horizon targets and their row alignment |
| [src/forecasting/experiment.py](../src/forecasting/experiment.py) | How origin and target dates are written for validation records |
| [docs/forecasting-runner.md](forecasting-runner.md) | Run lifecycle, completion manifest, Issue #89 status |
| [Forecast API contract](forecast-api-contract.md), [storage policy](artifact-storage-policy.md) | Retained export contract and local/ignored derivative location; exporter exists, acceptance remains pending |
| [Request-time forecast API](forecast-inference-api.md), [inference source](../src/forecasting/inference.py), [API source](../src/api/main.py) | Owner-requested active serving behavior; supplied-history request contract, four presentation examples and implementation pending review |
| [docs/workflows/shared-data-foundation.md](workflows/shared-data-foundation.md) | Forecast-to-inventory timing contract and open contract decisions |
| [docs/workflows/system-integration-and-prototype.md](workflows/system-integration-and-prototype.md) | Integration rules and adapter boundaries |
| [docs/team/tinosh/group-project-overview.md](team/tinosh/group-project-overview.md) | Tinosh's expected inputs and boundaries |
| [DR-011](decisions/DR-011-decision-support-output-structure.md) | Responsible decision-support output structure (accepted for structure only) |
| [DR-012](decisions/DR-012-inventory-risk-replenishment-methodology.md) | Inventory-risk / replenishment method (proposed for group approval) |
| [Inventory-risk workflow](workflows/inventory-risk-analysis.md), [Didilani overview](team/didilani/group-project-overview.md) | Inventory-side inputs, candidate outputs, constraints |
| [Responsible decision-support workflow](workflows/responsible-decision-support.md), [Dewmi overview](team/dewmi/group-project-overview.md) | Decision-support inputs, candidate fields, human-review direction |
| GitHub Issues #70, #85, #72, #73, #78, #86 | Referenced as listed in Issue #87; see Section 8 note |

---

## 3. Forecasting artifacts — actual implemented field names

Retained validation run validation-20261002-01 and final evaluation run final-20261003-02 are completed evidence, with integrity verification confirmed by the owner. Numerical sources are indexed in [reports](../reports/README.md); current findings are in [final evaluation](forecasting-final-evaluation.md). The removed earlier validation run remains historical and is not the current evidence source.

### 3.1 Run output files and storage

Machine-readable evidence and sole completion manifest are in artifacts/forecasting/<run_id>/; models/preprocessing/replay inputs are in models/forecasting/<run_id>/; tracked comparison snapshots are reports/forecasting/<run_id>/comparison.md. [Storage policy](artifact-storage-policy.md) owns exact layouts, versions and historical receipt compatibility; [runner operations](forecasting-runner.md) owns stage-specific verification. No output is independently opened or verified by this documentation update.

### 3.2 `predictions.csv` columns, grouped by purpose

| Purpose | Exact field names | Status |
|---|---|---|
| **Identity** | `SKU_ID`, `Warehouse_ID` | Implemented / frozen |
| **Origin** | `forecast_origin` | Implemented / frozen |
| **Horizon** | `horizon` (integer: `1`, `7`, `14`, `28`) | Implemented / frozen |
| **Target interval** | `target_start_date`, `target_end_date` | Implemented / frozen |
| **Training window** | `training_start`, `training_end`, `fold_id` | Implemented / frozen |
| **Forecast value** | `prediction` (raw; not clipped or rounded) | Implemented / frozen |
| **Provenance** | `run_id`, `evaluation_stage`, `evidence_role`, `model`, `configuration_id`, `canonical_config_id`, `representation_id`, `selected_configuration`, `selection_status` | Implemented / frozen |
| **Status** | `prediction_status`, `target_status`, `eligibility_status` | Implemented / frozen |
| **Retrospective outcome** | `observed_target` | Implemented / frozen — retrospective only |

### 3.3 Other artifacts and separate final schema

[Protocol §13–15](protocol.md#13-machine-readable-reproducibility-metadata) is the canonical validation metadata/CSV schema. Validation field names above refer to predictions.csv, not a universal downstream/API record.

The separate final runtime uses candidates.json, sealed predictions.json/prediction_receipt.json, observations.json and metrics.json under schema issue-130-final-v1. [Final persistence source](../src/forecasting/final_artifacts.py) owns the exact JSON contract. All twenty fresh learned models, preprocessing and replay inputs are retained. The DR-014 producer mapping identifies the intended four prospective producers; it does not make retrospective observations/errors prospective inputs.

### 3.4 Allowed provenance values (from protocol and source)

| Field | Values |
|---|---|
| `evaluation_stage` | `validation`, `final_evaluation` (separate completed stages; no final-result-driven reselection) |
| `evidence_role` | `primary`, `supportive`, `simple_baseline` |
| `model` | `xgboost`, `lightgbm`, `catboost` (primary); `ridge`, `random_forest` (supportive); `naive`, `seasonal_naive` (simple baselines) |
| `configuration_id` | `GBM001`–`GBM024` (primary); `fixed` (supportive); `not_tuned` (baselines) |
| `selection_status` | `candidate`, `validation_leader`, `tied_administrative_representative`, `tied_configuration`, `human_frozen`, `fixed_supportive`, `not_applicable` |

### 3.5 Actual fields versus conceptual downstream field groups

The forecasting names above are **real column names**. The names used by inventory-risk and decision-support documents are **concepts only**; none of them exists as a final column:

| Actual forecasting field | Conceptual downstream name (not a final field) | Source of conceptual name |
|---|---|---|
| `SKU_ID`, `Warehouse_ID` | identity / time group | DR-011 |
| `forecast_origin` | "forecast origin `t`", `forecast_origin` (candidate) | DR-012 §1; responsible DS workflow |
| `horizon` | "horizon `h`", `forecast_horizon` (candidate) | DR-012 §1; responsible DS workflow |
| `prediction` | `F_t,h`, `forecast_demand` (candidate) | DR-012 §1; Didilani / Dewmi overviews |
| `observed_target` | `Y_t,h` (retrospective only) | DR-012 §1, §6 |
| `model`, `run_id`, `configuration_id`, … | "model / source provenance" | DR-011; DR-012 §8 |
| *(none exists)* | `forecast_uncertainty`, forecast-error / uncertainty context | DR-011 (pending) |

Any mapping from an actual field to a downstream concept requires owner agreement before implementation ([system integration workflow](workflows/system-integration-and-prototype.md)).

---

## 4. Origin, horizon and target-window meaning

| Concept | Recorded meaning | Source |
|---|---|---|
| Origin `o` (or `t`) | The last date whose demand history is available to the forecaster. In validation records, `forecast_origin` = `training_end`. | DR-012 §1; [experiment.py](../src/forecasting/experiment.py) |
| Horizon `h` | One of `1`, `7`, `14`, `28`. `1` = next-day demand; `7` / `14` / `28` = **cumulative** demand totals. 28 days = four weeks / approximately monthly planning, not a calendar month and not a lead-time estimate. | DR-004; [protocol.md §2](protocol.md) |
| Target interval | `o+1` through `o+h`, both inclusive. `target_start_date` = `o+1`; `target_end_date` = `o+h`. | [protocol.md §2, §5](protocol.md); shared-data foundation |
| Direct target | `Y(o,h) = sum of Units_Sold over o+1 … o+h`. No daily path, recursive prediction or within-window update is implied. | [protocol.md §2](protocol.md); DR-008 |
| Label row alignment | In [targets.py](../src/forecasting/targets.py), `target_1_day`, `target_7_day`, `target_14_day`, `target_28_day` are stored on the row where `Date` = `o+1` (the **first forecast date**), not the origin date. | `build_horizon_targets` docstring |

**Integration warning (already stated in sources):** a target-start date must not be mistaken for the origin date ([shared-data foundation](workflows/shared-data-foundation.md)). Origin and horizon must be kept as separate fields; a single ambiguous `period` field must not be the only time descriptor (DR-011).

Worked examples from the frozen dates ([protocol.md §3, §12](protocol.md)):

| Case | `forecast_origin` | `h` | `target_start_date` | `target_end_date` |
|---|---|---|---|---|
| Validation fold 1 | 2024-03-31 | 28 | 2024-04-01 | 2024-04-28 |
| Validation fold 4 | 2024-11-04 | 7 | 2024-11-05 | 2024-11-11 |
| Final evaluation (completed) | 2024-12-02 | 1 / 7 / 14 / 28 | 2024-12-03 | 2024-12-03 / 09 / 16 / 30 |

---

## 5. Retrospective evidence versus prospective inputs

Sources require these two kinds of information to stay separate at every handoff ([protocol.md §14](protocol.md); DR-012 §6–8; shared-data foundation; system integration workflow).

| Retrospective (evaluation only) | May appear in a prospective / origin-time view |
|---|---|
| `observed_target` | `SKU_ID`, `Warehouse_ID` |
| `target_1_day` … `target_28_day` labels | `forecast_origin`, `horizon`, `target_start_date`, `target_end_date` |
| `wape`, `mae`, `rmse`, `bias`, `wape_denominator`, `mean_*` | `prediction` |
| Signed / absolute errors | Model / run provenance fields |
| Retrospective exposure state (`Y_t,h` against `B_t`) | Origin-available `Inventory_Level`, `Reorder_Point` (DR-012, proposed) |
| `retrospective_margin = B_t - Y_t,h` | `predicted_margin = B_t - F_t,h` (DR-012, proposed) |
| TP / TN / FN / FP counts and DR-012 rates | Origin-available `Supplier_Lead_Time_Days` (context only) |

Rules recorded in sources:

- `observed_target` appears only in authorised retrospective evaluation, never in predictors or prospective exports ([protocol.md §14](protocol.md)).
- The retrospective margin is evaluation evidence and must not become a prospective review input (DR-012 §7).
- The API must not use future outcome information in prospective views ([system integration workflow](workflows/system-integration-and-prototype.md)).

**Current state:** the [retained-export contract](forecast-api-contract.md) remains applicable to its fixed-origin artifact; exporter code and a local derivative exist. The active [forecast inference API](forecast-inference-api.md) builds fresh request features and invokes the frozen saved producer. Its code and four synthetic JSON inputs are prepared for review; manual demonstration and Tinosh's acceptance remain pending (B2). No retrospective outcome is used by this runtime.

---

## 6. Inventory-risk handoff requirements (forecasting → inventory-risk → decision support)

Owner: Didilani. Primary source: [DR-012](decisions/DR-012-inventory-risk-replenishment-methodology.md) — **Proposed for group approval** (Issue #51).

### 6.1 Inputs Didilani's component expects

| Requirement | Status | Source |
|---|---|---|
| Scenario identity: `SKU_ID`, `Warehouse_ID`, origin `t`, horizon `h` | Proposed (DR-012) | DR-012 §1 |
| Project model forecast `F_t,h` with model provenance and horizon meaning retained | Proposed | DR-012 §5 |
| Source `Demand_Forecast` must not substitute for the project forecast | Implemented / frozen rule | AGENTS.md §5; DR-012 §5 |
| `Inventory_Level` and `Reorder_Point` at the origin, same SKU-warehouse; snapshot date and availability assumption retained | Proposed | DR-012 §1; shared-data foundation |
| Within-day meaning of a same-date inventory row (before / after sales) | **Unresolved** | DR-012 §1; shared-data foundation item 5 |
| `Supplier_Lead_Time_Days` as context only (shorter / equal / longer than horizon) | Proposed | DR-012 §4 |
| `Order_Quantity` as context only, after origin availability is established | Proposed; availability **unresolved** | DR-012 §5 |
| `Stockout_Flag` as dataset limitation only (zero-variance) | Implemented / frozen rule | AGENTS.md §5; dataset.md |
| Handling of negative or otherwise problematic forecasts (no clipping approved) | **Unresolved** | DR-012 §2; protocol.md §8 |
| Original inventory scope is 1 / 7 / 14 days; 28-day downstream use | **Unresolved — owner/human approval required** | DR-012 §4 and 28-day review |

### 6.2 Outputs Didilani's component hands to Dewmi (DR-012 §8)

Concepts only — DR-012 does not lock names, types or format:

- identity, forecast origin and horizon, model/source provenance;
- origin inventory and policy evidence, buffer `B_t = I_t - R_t`;
- exposure state and reason (three states: already at/below threshold; forecast crossing; no forecast crossing);
- conceptual `predicted_margin` where available;
- contextual lead time;
- assumptions, limitations and availability reasons;
- replenishment quantity and uncertainty marked provisional / unavailable where no approved method exists;
- human-review status `not assessed` until a review method is approved.

| Item | Status |
|---|---|
| Three-state exposure rule and equality rule | Proposed (DR-012) |
| Numerical replenishment quantity | **Unresolved** (provisional) |
| Overstock / excess-stock evaluation | **Unresolved** (provisional) |
| Final column names, types, interchange format | **Unresolved** |
| Implementation | Not started (`src/inventory_risk/` contains only `.gitkeep`) |

---

## 7. Responsible decision-support handoff requirements

Owner: Dewmi. Primary source: [DR-011](decisions/DR-011-decision-support-output-structure.md) — **Accepted for structure only** (Issue #48).

### 7.1 Field groups (structure-only agreement)

identity / time; forecast; forecast-error / uncertainty context; inventory risk; replenishment; evidence; assumptions; limitations; management consideration; human review.

### 7.2 Requirements

| Requirement | Status | Source |
|---|---|---|
| Preserve `SKU_ID`, `Warehouse_ID`, forecast-origin date, forecast horizon; origin and horizon kept separate | Structure-only agreement | DR-011 |
| Each field / group identifies its producing component (forecasting; inventory-risk / replenishment; responsible decision support) | Structure-only agreement | DR-011 |
| Missing values never shown as zero; reason distinguishes: no agreed method / not applicable / waiting on another component | Structure-only agreement; concrete encoding **unresolved** | DR-011 |
| Human-review status with reason(s); unassessed cases shown as `not assessed`, never `false` | Structure-only agreement | DR-011 |
| Advisory-only presentation; never an executable purchase order | Implemented / frozen rule | DR-011; AGENTS.md §8 |
| Standing limitations: simulated dataset; zero-variance `Stockout_Flag` | Implemented / frozen rule | DR-011 |
| Eight transparency criteria for evaluation | Structure-only agreement | DR-011 |
| Uncertainty method | **Unresolved** | DR-011 dependency table |
| Human-review rules and numerical thresholds | **Unresolved** | DR-011; responsible DS workflow |
| 28-day review triggers / 28-day downstream population | **Unresolved — approval required** | DR-011 revised interface section |
| Final column names, types, file / interchange format | **Unresolved** | DR-011 open decisions |

Candidate field names in the [responsible decision-support workflow](workflows/responsible-decision-support.md) (`forecast_origin`, `forecast_horizon`, `forecast_demand`, `inventory_risk_level`, `recommended_replenishment_quantity`, `forecast_uncertainty`, `evidence`, `assumptions`, `limitations`, `management_consideration`, `human_review_flag`) are **candidates, not final fields**.

---

## 8. Readiness summary by handoff

| Handoff | Available / frozen | Remaining acceptance or decision |
|---|---|---|
| Retrospective forecasting research | Completed validation/final evidence; approved configurations, fresh-refit policy and producer mapping | Preserve the reviewed final interpretation and retained evidence |
| Prospective forecasting input/API | Retained exporter exists; owner-requested [inference API](forecast-inference-api.md), frozen DR-014 saved models and four synthetic request examples are prepared for review | Human code/schema review, manual four-horizon demonstration and Tinosh's consumer acceptance; retained-export hash acceptance is separate |
| Forecasting → inventory-risk | Grain/target meaning and documented dataset limits | Proposed DR-012 approval; origin snapshot semantics, problematic forecasts, schema, 28-day use and Order_Quantity availability |
| Inventory-risk → responsible decision support | Advisory-only boundary and DR-011 structure-only field groups | Final schema, unavailable-state encoding, replenishment quantity, uncertainty and review rules |
| Components → prototype/API | Ownership split and presentation-oriented boundary | Approved interchange/response schemas, adapters, tests and technical visual requirements |

Completed retrospective evidence resolves the former absence-of-validation-evidence blocker. It does not resolve prospective contract acceptance or other members' methodologies. Issue references below are existing task pointers, not freshly checked GitHub status.

## 9. Blockers

B1 (retained forecasting evidence availability) is resolved by the completed validation/final evidence. Remaining blockers retain their existing owners and approval boundaries.

| ID | Blocker | Component owner | Related Issue | Required decision or deliverable |
|---|---|---|---|---|
| B2 | The active request-time forecasting API is prepared for review; consumer handoff remains pending. | Chathuranga, with Tinosh for delivery | #132; #86 | Review the [inference API](forecast-inference-api.md), run the four manual input examples against saved models, and obtain Tinosh's consumer acceptance. Accept the separate retained-export hash only if that artifact is consumed. |
| B3 | Origin inventory snapshot availability and within-day (before/after sales) semantics are undocumented. | Didilani | #51 (DR-012); #70 / #85 | Documented snapshot semantics and handling of unavailable origin snapshots |
| B4 | DR-012 is still Proposed. | Didilani (group decision) | #51; #70 / #85 | Group approval or revision of DR-012 |
| B5 | Handling of negative / problematic forecasts at the inventory input is open; no clipping is approved. | Didilani, with Chathuranga for forecast meaning | #70 / #85 | Explicit input-contract decision |
| B6 | Final forecasting → inventory-risk schema (names, types, format) not agreed. | Chathuranga + Didilani | #70 / #85; shared-data foundation item 6 | Agreed, reviewed interchange contract |
| B7 | Final inventory-risk → decision-support schema not agreed. | Didilani + Dewmi | #85; #72 / #73; shared-data foundation item 7 | Agreed, reviewed interchange contract |
| B8 | 28-day downstream use is not approved (inventory interpretation and review triggers). | Didilani (inventory); Dewmi (review triggers); human approval | #70 / #85; #72 / #73 | Component-owner / human approval decision |
| B9 | Concrete encoding of missing / unavailable information (three DR-011 reasons) is not defined; current forecasting status fields only record `available` / `complete` / `eligible` for accepted rows. | Dewmi (semantics), with each producing owner | #72 / #73 | Agreed unavailable-state vocabulary per handoff |
| B10 | Human-review rules, thresholds and combination of reasons not approved. | Dewmi | #72 / #73 | Approved review method |
| B11 | Forecast uncertainty method not defined. | Chathuranga | Not yet assigned to an Issue (DR-011 dependency table) | Forecasting uncertainty decision, or explicit "unavailable" agreement |
| B12 | Numerical replenishment quantity and overstock evaluation remain provisional. | Didilani | #51; #70 / #85 | Separately approved method, or confirmed "unavailable" status |
| B13 | `Order_Quantity` availability at the forecast origin not established. | Didilani | #51; #70 / #85 | Documented availability decision |

---

## 10. Issue #86 — what can begin and what must wait

### 10.1 Can begin after this document is reviewed

- Narrow Issue #86 to **one** reviewed handoff and a concrete, testable interface, as Issue #87 requires.
- Draft that narrowed interface as a proposal for the relevant owner's review (draft only; not a final schema).
- Prepare test-case descriptions from requirements that are already frozen: identity preservation, separate origin and horizon, `target_start_date` = origin + 1, `target_end_date` = origin + h, no `observed_target` in prospective views, advisory-only output, `not assessed` instead of `false`.
- Any technical reading of the existing frozen forecasting artifact schema (`issue-65-v2`) using synthetic fixtures only, labelled as retrospective validation evidence — **only if Chathuranga confirms this is in scope for the narrowed #86.**

### 10.2 Must wait

| Work in #86 | Waits for |
|---|---|
| Forecast → inventory-risk adapter | B2, B3, B4, B5, B6 |
| Inventory-risk → decision-support adapter | B4, B7, B9, B12 |
| Accept or extend prospective forecast API endpoints | B2 (initial inference implementation is prepared for review) |
| Any 28-day downstream view or review trigger | B8 |
| Human-review flags or reasons in the prototype | B10 |
| Uncertainty display | B11 |
| Inventory-risk visual components | Didilani's approved analytical visual specification |
| Decision-support record presentation | Dewmi's reviewed record semantics (B7, B9, B10) |
| Any use of real run outputs | Stage-specific verified run_manifest.json and human acceptance of the exact handoff |

### 10.3 Start checklist for Issue #86

- [ ] This document is reviewed by Chathuranga, Didilani and Dewmi.
- [ ] Issue #86 is narrowed to one handoff with a named producer, consumer and reviewer.
- [ ] The producing component's output for that handoff is human-reviewed and available (not only planned).
- [ ] Field names, types and format for that handoff are agreed by the producing owner.
- [ ] Origin, horizon and target-interval meaning for that handoff match Section 4.
- [ ] Retrospective fields are excluded from any prospective part of the interface.
- [ ] Unavailable-state reasons for that handoff are agreed (no zero or `false` substitutes).
- [ ] Any 28-day content is either approved or explicitly marked unavailable.
- [ ] No pending decision in Section 9 is settled through an adapter default.
- [ ] Concrete, testable acceptance criteria are written into the narrowed #86.

---

## 11. Standing limitations

- The dataset is simulated; outputs are not validated for a real retailer ([dataset.md](dataset.md); DR-011).
- `Stockout_Flag` is zero-variance and cannot be stockout ground truth.
- The final evaluation interval (2024-12-03 to 2024-12-30) is reserved but not historically fully unseen; December 3–16 had earlier validation exposure and full-year EDA inspected it ([protocol.md §3, §12](protocol.md)).
- All framework outputs are advisory decision support, not executable purchase orders.