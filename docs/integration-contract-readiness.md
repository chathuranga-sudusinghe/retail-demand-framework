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
| Standing limitations: publisher-simulated Kaggle dataset; zero-variance `Stockout_Flag` | Implemented / frozen rule | DR-011 |
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

- The dataset downloaded from Kaggle is simulated by its publisher; outputs are not validated for a real retailer ([dataset.md](dataset.md); DR-011).
- `Stockout_Flag` is zero-variance and cannot be stockout ground truth.
- The final evaluation interval (2024-12-03 to 2024-12-30) is reserved but not historically fully unseen; December 3–16 had earlier validation exposure and full-year EDA inspected it ([protocol.md §3, §12](protocol.md)).
- All framework outputs are advisory decision support, not executable purchase orders.

## 12. Integration acceptance scenarios (Issue #101)

**Issue:** #101 — Docs: specify integration acceptance scenarios from frozen handoff requirements

**Builds on:** Issue #87 (Sections 1–11 of this document). Issue #101 lists #98, #70 and #73 as completed inputs. This section uses their requirements only as they are already reflected in Sections 3–9 and in the merged component tests named below.

**Status:** Documentation only. These scenarios describe what a later integration must show. They are not new tests, adapters, API code, charts or final schemas.

### 12.1 Rules for this section

- **Synthetic data only.** Every value below is invented for illustration (`SKU_SYN_A`, `WH_SYN_1`, `syn-run-01`, small demand numbers). None comes from the project dataset or a real run.
- **Real names only where they already exist.** Back-ticked forecasting names (`SKU_ID`, `Warehouse_ID`, `forecast_origin`, `horizon`, `target_start_date`, `target_end_date`, `prediction`, `observed_target`, `run_id`, `evaluation_stage`, `evidence_role`, `model`, `configuration_id`, `canonical_config_id`) are the implemented `predictions.csv` columns in [artifacts.py](../src/forecasting/artifacts.py). Downstream content is described in plain words, because final interchange names, types and encodings are not agreed (B6, B7, B9).
- **No new defaults.** Where a value is missing or unapproved, a scenario only requires that this is visible with a reason. It does not choose a fallback, clipping rule, uncertainty method or review threshold.
- **Two kinds of coverage.** *Component unit coverage* means an existing test checks the behaviour inside one component. *Integration / presentation check* means the behaviour still has to be shown across a handoff or in the prototype. The second kind is pending for every scenario.
- **Positive** examples show acceptable behaviour. **Negative** examples show behaviour a later integration must reject or never produce.

### 12.2 Acceptance matrix

| ID | Requirement | Authoritative reference | Synthetic scenario | Expected invariant / observable behaviour | Remaining dependency | Responsible reviewer |
|---|---|---|---|---|---|---|
| AS-01 | Identity preservation | AGENTS.md §5 (DR-002 grain); [protocol.md §6, §14](protocol.md); §3.2 | One forecast for `SKU_SYN_A` / `WH_SYN_1` passes through a handoff | The same `SKU_ID` + `Warehouse_ID` pair arrives unchanged; no merging, swapping or new identity; an unknown identity fails explicitly | #85; #132; #153 | Chathuranga; Didilani |
| AS-02 | Forecast origin is not the target start | [protocol.md §2, §5](protocol.md); §4; shared-data foundation | Origin 2024-03-31, h = 28 | Origin shown as 2024-03-31; target start shown as 2024-04-01; never equal or swapped | #132; #85 | Chathuranga; Didilani |
| AS-03 | Inclusive target window | [protocol.md §2, §3](protocol.md); §4 | Origin 2024-11-04, h = 7 | Window is 2024-11-05 to 2024-11-11, both days included, exactly 7 days | #132 | Chathuranga |
| AS-04 | Horizon preservation | DR-004; DR-008; [protocol.md §2](protocol.md); §4 | Same pair and origin with h = 1, 7, 14, 28 | Four separate records, each keeps its horizon; 7/14/28 stay cumulative totals; no daily path or cross-horizon total | #132; #85; B8 for 28-day downstream use | Chathuranga; Didilani; Dewmi |
| AS-05 | Provenance preservation | [protocol.md §7.3, §11, §14](protocol.md); DR-011 source distinction; §3.4 | A primary and a supportive record from `syn-run-01` | Each record keeps `run_id`, `evaluation_stage`, `evidence_role`, `model`, `configuration_id`; supportive `canonical_config_id` stays empty; the producing component stays identifiable | #132; #85; #153 | Chathuranga; Dewmi |
| AS-06 | Retrospective outcomes kept out of prospective presentation | [protocol.md §14](protocol.md); DR-012 §7; §5; system integration workflow | One record with `prediction` 14.0 and `observed_target` 15 | A retrospective view may show both, clearly labelled; a prospective view shows no `observed_target`, error or metric | #132; #153 | Chathuranga; Dewmi |
| AS-07 | Unavailable information stays visible with a reason | DR-011 missing-value semantics; DR-012 §2; §7.2 | Origin inventory snapshot missing; upstream evidence missing | Shown as unavailable with a reason; never zero, never silently dropped, never scored | #85; #153; B9 | Didilani; Dewmi |
| AS-08 | Advisory-only presentation | DR-011; AGENTS.md §8; system integration workflow | Exposure evidence shown to a manager | Presented as guidance for human consideration; no automatic or executable order | #153; B7; B10 | Dewmi; Didilani |
| AS-09 | "Not assessed" with a reason, never `false` | DR-011 human review; DR-012 §8; §7.2 | A record before any review method is approved | Review status reads as not assessed, with a reason; never `false`, "no" or blank | #153; B9; B10 | Dewmi |
| AS-10 | Undefined metric stays unavailable | [protocol.md §8](protocol.md) | Retrospective group whose actual total is 0 | WAPE is unavailable (`undefined_zero_actual_total`), not 0 or infinity; supporting metrics are kept | None (retrospective only) | Chathuranga |

### 12.3 Existing coverage and pending checks

| ID | Component unit coverage (existing tests) | Pending integration / presentation check |
|---|---|---|
| AS-01 | `tests/test_forecasting_features.py` (invalid and duplicate keys rejected); `tests/test_forecasting_evaluation.py` (row index is not an identity key); `tests/test_inventory_risk_preparation.py::test_preparation_preserves_identity_timing_provenance_and_source_fields` | Identity carried unchanged from forecast → inventory-risk → decision-support record → API/prototype view |
| AS-02 | `tests/test_forecasting_features.py` (origin features use the first target day, not the origin); `tests/test_inventory_risk_preparation.py::test_preparation_preserves_identity_timing_provenance_and_source_fields` | Origin and target start displayed separately in the API response and prototype |
| AS-03 | `tests/test_forecasting_features.py` (inclusive fold boundaries; targets fit inside windows) | Inclusive window shown correctly in the API response and prototype |
| AS-04 | `tests/test_forecasting_evaluation.py` (direct cumulative, not recursive); `tests/test_forecasting_configuration.py` (unapproved horizons rejected); `tests/test_inventory_risk_preparation.py::test_preparation_preserves_identity_timing_provenance_and_source_fields` | Four horizons kept separate across the handoff; no daily path drawn; 28-day downstream content stays gated (B8) |
| AS-05 | `tests/test_forecasting_orchestration.py::test_exact_csv_column_order_is_checked_against_the_frozen_protocol`; `tests/test_forecasting_orchestration.py::test_artifacts_are_exclusive_safe_and_reject_schema_drift`; `tests/test_inventory_risk_preparation.py::test_preparation_preserves_identity_timing_provenance_and_source_fields` | Provenance and producing component visible in the decision-support record and prototype |
| AS-06 | `tests/test_forecasting_features.py` (post-origin actuals masked); `tests/test_forecasting_evaluation.py` (outcomes change only targets) | No observed outcome, error or metric in any prospective API response or view |
| AS-07 | `tests/test_inventory_risk_evaluation.py::test_unavailable_snapshot_is_retained_and_not_scored`; `tests/test_decision_support_records.py::test_missing_upstream_evidence_requires_explicit_reason` | Unavailable state and reason carried across handoffs and shown in the prototype; final encoding still open (B9) |
| AS-08 | No dedicated component test identified for advisory wording | Advisory-only wording and absence of order actions checked in the prototype |
| AS-09 | `tests/test_decision_support_records.py::test_default_human_review_status_is_not_assessed`; `tests/test_decision_support_records.py::test_not_assessed_must_have_reason` | Not-assessed status and reason shown in the prototype; review rules still open (B10) |
| AS-10 | `tests/test_forecasting_models_metrics_baselines.py::test_zero_wape_denominator_keeps_supporting_metrics_and_json_null` | Unavailable WAPE shown as unavailable in any retrospective view |

> **Note:** component unit tests prove behaviour inside one component only. No cross-component integration, adapter or API acceptance test is claimed by this section.

### 12.4 Positive and negative examples

#### A. Identity preservation (AS-01)

**Positive** — the pair arrives unchanged:

```text
forecasting record:      SKU_ID=SKU_SYN_A  Warehouse_ID=WH_SYN_1  horizon=7  prediction=14.0
after handoff (concept): same SKU_SYN_A / WH_SYN_1, same horizon, same forecast value
```

**Negative** — must be rejected:

| Case | Why it fails |
|---|---|
| Output shows `WH_SYN_2` for a `WH_SYN_1` input | Warehouse swapped |
| `SKU_SYN_A` at `WH_SYN_1` and `WH_SYN_2` added into one SKU total | Breaks the SKU-warehouse grain |
| `SKU_SYN_Z` (never seen in training) gets an all-zero or default forecast | Unknown identities must fail explicitly ([protocol.md §6](protocol.md)) |

#### B. Forecast origin versus target start (AS-02)

**Positive:**

```text
forecast_origin=2024-03-31  target_start_date=2024-04-01  horizon=28  target_end_date=2024-04-28
```

**Negative:**

| Case | Why it fails |
|---|---|
| Display says "forecast made on 2024-04-01" | Target start shown as the origin |
| `forecast_origin` = `target_start_date` = 2024-04-01 | Origin must be the day before target start |
| A `target_7_day` label joined to the row dated 2024-03-31 | Labels sit on the row dated origin + 1, not the origin (§4) |

#### C. Inclusive target window (AS-03)

**Positive** — origin 2024-11-04, h = 7, synthetic daily demand:

| Date | 11-05 | 11-06 | 11-07 | 11-08 | 11-09 | 11-10 | 11-11 |
|---|---|---|---|---|---|---|---|
| Units | 3 | 0 | 2 | 5 | 1 | 4 | 0 |

```text
forecast_origin=2024-11-04  horizon=7  target_start_date=2024-11-05  target_end_date=2024-11-11
retrospective cumulative total = 3+0+2+5+1+4+0 = 15
```

For h = 1, start and end are the same day (2024-11-05).

**Negative:**

| Case | Why it fails |
|---|---|
| Window ends 2024-11-12 (8 days) | One day too many |
| Window starts 2024-11-04 | Includes the origin day |
| Window treated as 2024-11-05 to 2024-11-10 (6 days) | The end day must be included |

#### D. Horizon preservation (AS-04)

**Positive** — one pair, one origin, four separate records:

```text
horizon=1   prediction=2.0    (next day)
horizon=7   prediction=14.0   (7-day cumulative total)
horizon=14  prediction=27.5   (14-day cumulative total)
horizon=28  prediction=55.0   (28-day cumulative total; four weeks, not a calendar month)
```

**Negative:**

| Case | Why it fails |
|---|---|
| 28-day value divided by 28 and drawn as a daily line | No daily path is implied (DR-008) |
| The four values summed or averaged into one score | Horizons must not be combined |
| h = 28 labelled "next month" or "lead time" | 28 days is four weeks, not a calendar month or a lead-time estimate (DR-004) |
| A 28-day inventory exposure state shown as approved | 28-day downstream use is not approved (B8) |

#### E. Provenance preservation (AS-05)

**Positive:**

```text
run_id=syn-run-01  evaluation_stage=final_evaluation  evidence_role=primary     model=lightgbm  configuration_id=GBM015  canonical_config_id=GBM015
run_id=syn-run-01  evaluation_stage=final_evaluation  evidence_role=supportive  model=ridge     configuration_id=fixed   canonical_config_id=(empty)
```

**Negative:**

| Case | Why it fails |
|---|---|
| `model` or `run_id` dropped before display | Source can no longer be traced |
| Ridge record shown with `canonical_config_id=GBM001` | Supportive records have no canonical ID ([protocol.md §7.3](protocol.md)) |
| A `validation` record presented as final performance | Stages must stay separate ([protocol.md §11](protocol.md)) |
| Inventory or review content shown without saying which component produced it | Breaks DR-011 source distinction |

#### F. Retrospective outcomes versus prospective presentation (AS-06)

**Positive** — retrospective (evaluation) view, clearly labelled as looking back:

```text
evaluation_stage=final_evaluation  horizon=7  prediction=14.0  observed_target=15
```

**Positive** — prospective view (concept only):

```text
shows: identity, forecast origin, horizon, target window, forecast value, provenance
does not show: observed demand, errors, metrics
```

**Negative:**

| Case | Why it fails |
|---|---|
| Prospective view shows `observed_target` = 15 next to the forecast | A future outcome shown as if known at the origin |
| Prospective view shows WAPE or error beside a live forecast as if it applied to that forecast | Errors are retrospective only |
| Retrospective margin (`B_t - Y_t,h`) used to trigger review | Must not become a prospective review input (DR-012 §7) |

### 12.5 Conceptual scenarios — unavailable information, advisory-only, not assessed

These describe **behaviour only**. They do not set final interchange field names, codes or encodings (B9 remains open). DR-011 writes the review state as "not assessed"; Issue #101 writes it `not_assessed`. The final interchange spelling is not decided here.

#### Unavailable information (AS-07)

DR-011 separates three reasons: **no agreed method**, **does not apply**, and **waiting for another component's decision or output**.

| Synthetic situation | Acceptable behaviour | Must never happen |
|---|---|---|
| Uncertainty for any forecast (no method, B11) | Shown as unavailable; reason: no agreed method | Shown as 0, ±0 or an invented range |
| 28-day inventory exposure (not approved, B8) | Shown as unavailable; reason: waiting for a decision | Calculated by extending DR-012 on its own |
| Replenishment quantity (provisional, B12) | Shown as unavailable; reason: no agreed method | Shown as 0 units or as a suggested order |
| Origin inventory snapshot missing for `SKU_SYN_A` / `WH_SYN_1` | Record retained, exposure unavailable with a reason and not scored; the forecast itself can still be shown (DR-012 §2) | Record silently dropped, scored, or filled from a later snapshot |
| Upstream evidence missing for a decision-support record | Explicit reason recorded | Field left blank or shown as complete |
| Observed demand of 0 on a real day | Shown as 0 — a real zero | Treated as unavailable |

#### Advisory-only presentation (AS-08)

| Acceptable | Must never happen |
|---|---|
| "Forecast threshold crossing within 7 days — for manager review" | "Order 120 units now" |
| Evidence, assumptions and limitations shown next to the result | A button or action that creates a purchase order |
| The final decision is clearly left with a responsible person | Wording that implies the system approved the action |

#### "Not assessed" with a reason (AS-09)

| Acceptable | Must never happen |
|---|---|
| Review status: not assessed; reason: no approved review method yet | Review status shown as `false` |
| Exposure assessed but review still not assessed (independent, DR-012 §8) | "No review needed" when no rule exists |
| More than one reason kept when more than one applies | Not-assessed status with no reason |

### 12.6 Ready to specify now versus waiting on dependencies

**Ready to specify now** (frozen sources and component tests exist; no pending decision is needed to write the expected behaviour):

- AS-01 to AS-06 inside the forecasting component, using the implemented `predictions.csv` fields and synthetic records;
- AS-01, AS-02, AS-04, AS-05 and the unavailable-snapshot case of AS-07 inside the inventory-risk preparation and evaluation components;
- the not-assessed default, reason requirement and missing-evidence reason inside decision-support records (AS-07, AS-09);
- AS-10;
- the **behaviour** described in 12.5, but not its final interchange encoding.

**Waiting on a dependency** (the behaviour is written, but the cross-component or presentation check cannot be completed yet):

| Depends on | Scenarios affected | What must exist first | Related blockers |
|---|---|---|---|
| #132 | AS-01 to AS-06 as shown by the request-time forecast API | Reviewed API, four-horizon demonstration and Tinosh's consumer acceptance | B2 |
| #85 | AS-01, AS-02, AS-04, AS-05 and AS-07 carried across the forecasting → inventory-risk handoff | Agreed forecasting → inventory-risk contract; origin snapshot meaning; problematic-forecast handling | B3, B4, B5, B6, B13 |
| #153 | AS-05 to AS-09 at decision-support record level and in presentation | Record-level assessment and presentation requirements | B7, B9, B10 |
| No Issue yet / separate approval | Uncertainty display; any 28-day downstream content | Uncertainty decision; 28-day downstream approval | B8, B11 |

**Note on #145:** #145 is closed, and its preparation work was merged through #152. The remaining decision-support dependency is tracked by #153. Merging #152 does not resolve B7 (final inventory-risk → decision-support schema), B9 (final unavailable-state encoding) or B10 (human-review rules and thresholds). These stay open.

### 12.7 What this section does not do

- It does not add runtime code, adapters, FastAPI endpoints, charts or automated tests.
- It does not define final shared or interchange schemas, field names, encodings or defaults.
- It does not choose an uncertainty method, review threshold, clipping rule or replenishment quantity.
- It does not change any research methodology or authorise any experiment.