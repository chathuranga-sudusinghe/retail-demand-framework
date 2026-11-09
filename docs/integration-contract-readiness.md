# Integration Contract Readiness — Component Handoff Map

**Issue:** #87 — Docs: map component handoff contracts and integration blockers
**Tracking — reconciled 9 November 2026:** #191, #203, #201 and #182 are closed delivery/acceptance milestones. [#179](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/179) records repository completion through the documentation closeout PR; #204 covers later submission files. The [current delivery and acceptance record](#12-current-delivery-and-acceptance--9-november-2026) supersedes older open/pending summaries below.
**Responsible member:** Tinosh Gamage — System Integration and Prototype Engineering
**Reviewers:** Chathuranga (forecasting-facing accuracy), Didilani (inventory-risk interpretation), Dewmi (responsible-use meaning)
**Updated:** 9 November 2026; inspected implementation baseline `e9aba1fc09558fac0f687d8fd79f5c2e0128103f`. Earlier revision references remain historical.
**Status:** Retained-case routes, the separate request-time forecast path, four approved inventory questions and eight research figures are delivered. Scoped acceptances and the documentation closeout steps are listed below. Unknown inventory timing and accepted deferred methods remain unchanged.

---

## 1. Purpose and boundaries

This document maps the handoffs that currently exist, or are currently documented, between:

1. forecasting (Chathuranga);
2. inventory-risk / replenishment analysis (Didilani);
3. responsible decision support (Dewmi);
4. later prototype / API integration (Tinosh, with Chathuranga for API architecture).

It records what each source already says, separates what is implemented from what is only agreed or proposed, and lists remaining decisions and acceptance work for the next reviewed integration slice.

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
| **Proposed** | A genuinely unresolved proposal, or explicitly historical metadata; it is not the current DR-012 approval status. |
| **Unresolved** | Explicitly recorded as open by an existing source; no decision exists yet. |

---

### 1.2 Current delivery and acceptance — 9 November 2026

This record, including the subsequent human closeout clarification below, supersedes earlier current-facing statements that #201/#182 are open,
that views are planned, or that W2/technical review has not happened. Dated
observations below retain their original scope. This documentation correction
records existing work; it does not create a human approval. The linked completion
tracker is closed by the human-merged closeout PR, rather than by editing prose.

**Closeout clarification — Chathuranga, 9 November 2026:** In the working
conversation, Chathuranga confirmed that the old pending PNG items were addressed
by the replacement eight-figure delivery already committed to the repository,
and instructed that Didilani not be asked to confirm those same items again.
He also reaffirmed that PR #217's review was completed and requested that this
be recorded in the 9 November documentation closeout PR. Retain
his previously reported inventory/consumer acceptance; this is his clarification,
not a newly authored direct acceptance from Didilani or a fabricated GitHub review.
The subsequent independent review identified documentation-only stale-status
corrections, approved by Chathuranga; no implementation or existing review gap
was identified as a blocker. The documentation closeout PR carries `Closes #179`;
GitHub records closure when a human merges that PR into `main`. Reuse existing
component reviews and preserve their attribution.

The current delivery is the eight PNG/SVG/JSON figure sets, README and manifest
in [final-thesis-figures](../reports/figures/final-thesis-figures/README.md),
merged through PR #211 and subsequent clarifications through #218/#219.
Manifest SHA-256: `e95cbd33e5b708f3fe21458f570ecbcaafe81c1df5b9e3a1266dcb9d7f2f3ad1`.
The generation receipt's dirty HEAD is historical provenance, not the current
checkout identity. No figure regeneration is needed for these status edits.

| Scope | Recorded evidence and current disposition |
|---|---|
| Retained delivery / #201 | [Closed on 8 November](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/201#issuecomment-6719061457), including the 5 November human route walkthrough and eight-figure delivery. |
| Forecast producer/source | [Chathuranga confirmed completion](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/179#issuecomment-6719032400), including applicable source verification. |
| Inventory figures / retained consumer | Chathuranga reported Didilani's acceptance in the linked #179 confirmation and clarified on 9 November that the later old-page findings are addressed by the current eight figures. Her [last direct #179 outcome](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/179#issuecomment-6730175531) was **pending final acceptance**, citing removed output pages and reviews now recorded. Inventory acceptance for the current delivery rests on Chathuranga's report and 9 November clarification, not a later direct statement from her. No repeated confirmation is requested. |
| Responsible presentation / W2 | [Dewmi's final scoped W2 acceptance](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/182#issuecomment-6704944020) resolved all four clarification points; #182 is closed. Her [overall component confirmation](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/179#issuecomment-6724432473) records no responsible-use blockers. |
| Technical integration / worked scenario | [Tinosh accepted T1–T4 at `e9aba1f`](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/179#issuecomment-6723530741), reusing his #201/#211 and #215 reviews, 45 visualization tests and 104 synthetic worked-scenario tests. His #211/#215 reviews were recorded after merge; they are not pre-merge approvals. |
| PR #217 review record | Chathuranga confirmed in the working conversation that the human review was completed and reaffirmed this on 9 November. [PR #217](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/217) covers missing-runtime-package handling in `src/forecasting/metadata.py` and the associated synthetic tests, incorporated in baseline `e9aba1fc09558fac0f687d8fd79f5c2e0128103f`. This records his completion report; the reviewer's identity and original timing were not supplied, and no formal GitHub review submission or pre-merge timing is invented. No repeated review is requested. |
| Overall completion / final files | Implementation and existing component reviews are complete under the recorded confirmations and Chathuranga's 9 November clarification. The documentation closeout PR records completion and carries `Closes #179`, with issue closure taking effect on human merge into `main`. #204 covers later final report/presentation files. Record the actual completion time; do not backdate to the internal 00:00 on 9 November target. |

#### Reconciliation of Didilani's latest pending items

| Item in the latest comment | Disposition for the current delivery |
|---|---|
| Metadata-page readability and spacing | Addressed by the replacement eight-figure delivery already committed to the repository, as clarified by Chathuranga on 9 November. Removed pages are outside the current deliverable; no restoration, repair or repeated D2 confirmation is requested. |
| Dewmi's W2 review | Completed and accepted at the links above; reuse it for unchanged figures. |
| Tinosh's technical/component review and API handoff | Completed within the recorded scope above; the separate #203 request-time handoff is accepted. PR #217 review completion is recorded as confirmed by Chathuranga; no repeat is requested. |
| Report integration and overall acceptance | Inventory evidence is incorporated in group-report Section 6; Sections 7–8 link completed responsible-use and technical reviews. Retain the reported inventory acceptance and the 9 November clarification. Final submission-file assembly belongs to #204. |

#### Retained-export identity check — 9 November 2026

Before these documentation edits, Codex inspected the standard-library verifier
and ran the narrow `dewmi` profile against the full `e9aba1f` baseline named in
Tinosh's independent human technical review above. This was a read-only check
of tracked Git content, the checksum reference and one installed export; no
model deserialization, inference, replay, evaluation or full-bundle scan ran.

```bash
.venv/bin/python -B -m src.data.verify_checksums --profile dewmi --tracked-ref e9aba1fc09558fac0f687d8fd79f5c2e0128103f
```

```text
OK  tracked Git content matches e9aba1fc09558fac0f687d8fd79f5c2e0128103f
Reference: docs/checksums/2026-10-06.json
Reference SHA-256: 381ed9607a9e3ec155ee3754d699d62873bfbff18f5e1f4edc31c407267ed7cc
Repository HEAD: e9aba1fc09558fac0f687d8fd79f5c2e0128103f
Reference revision: e9aba1fc09558fac0f687d8fd79f5c2e0128103f
Reference status: matches the supplied reviewed commit bytes.
OK  data/processed/forecasting/handoffs/final-20261003-02/issue-132-forecast-export-v1.json
Files matched: 1/1
```

Exit status was 0, with no missing/changed selected files or warnings. Absolute
local root lines are omitted above; the command ran at the existing repository
root. Other ignored payloads were outside this profile. This new check does not
upgrade earlier provisional checks retroactively or claim another member ran it.
Tracked content matched before editing; this documentation change is outside
that earlier clean-tree observation. File identity does not establish scientific
correctness, source inventory timing or consumer acceptance.

## 2. Sources reviewed

| Source | What it supplies for this map |
|---|---|
| [AGENTS.md](../AGENTS.md) | Ownership boundaries, research-decision rule, dataset rule, experiment execution rule |
| [docs/protocol.md](protocol.md) | Frozen forecasting validation protocol (`issue-65-matched-frozen-1`), artifact schemas, human approval boundaries |
| [src/forecasting/artifacts.py](../src/forecasting/artifacts.py) | Exact implemented artifact column names and schema version |
| [src/forecasting/targets.py](../src/forecasting/targets.py) | Exact meaning of horizon targets and their row alignment |
| [src/forecasting/experiment.py](../src/forecasting/experiment.py) | How origin and target dates are written for validation records |
| [docs/forecasting-runner.md](forecasting-runner.md) | Run lifecycle, completion manifest, Issue #89 status |
| [Forecast API contract](forecast-api-contract.md), [storage policy](artifact-storage-policy.md) | Retained export contract and local/ignored derivative location; current acceptance and identity evidence are in Section 1.2 |
| [Request-time forecast API](forecast-inference-api.md), [inference source](../src/forecasting/inference.py), [API source](../src/api/main.py) | Active serving behavior requested by Chathuranga; supplied-history request contract, four presentation examples and merged implementation; consumer acceptance remains separate |
| [docs/workflows/shared-data-foundation.md](workflows/shared-data-foundation.md) | Forecast-to-inventory timing contract and open contract decisions |
| [docs/workflows/system-integration-and-prototype.md](workflows/system-integration-and-prototype.md) | Integration rules and adapter boundaries |
| [docs/team/tinosh/group-project-overview.md](team/tinosh/group-project-overview.md) | Tinosh's expected inputs and boundaries |
| [DR-011](decisions/DR-011-decision-support-output-structure.md) | Responsible decision-support output structure (accepted for structure only) |
| [DR-012](decisions/DR-012-inventory-risk-replenishment-methodology.md) | Group-approved 1/7/14-day scenario method; approval attribution is recorded in DR-012 |
| [Inventory-risk workflow](workflows/inventory-risk-analysis.md), [Didilani overview](team/didilani/group-project-overview.md) | Inventory-side inputs, candidate outputs, constraints |
| [Responsible decision-support workflow](workflows/responsible-decision-support.md), [Dewmi overview](team/dewmi/group-project-overview.md) | Decision-support inputs, candidate fields, human-review direction |
| GitHub Issues #70, #85, #72, #73, #78, #86 | Referenced as listed in Issue #87; see Section 8 note |

---

## 3. Forecasting artifacts — actual implemented field names

Retained validation run validation-20261002-01 and final evaluation run final-20261003-02 are completed evidence, with integrity verification confirmed by Chathuranga. Numerical sources are indexed in [reports](../reports/README.md); current findings are in [final evaluation](forecasting-final-evaluation.md). The removed earlier validation run remains historical and is not the current evidence source.

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
| *(none exists)* | `forecast_uncertainty`, forecast-error / uncertainty context | DR-011 supplies structure only; prospective uncertainty is deferred under [the recorded team scope](research-design.md#164-human-decisions-and-c1-closeout-record) |

Any mapping from an actual field to a downstream concept requires agreement by the relevant producing and consuming component members before implementation ([system integration workflow](workflows/system-integration-and-prototype.md)).

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
| Retrospective exposure state (`Y_t,h` against `B_t`) | Origin-available `Inventory_Level`, `Reorder_Point` (DR-012 scenario method) |
| `retrospective_margin = B_t - Y_t,h` | `predicted_margin = B_t - F_t,h` (DR-012 scenario method) |
| TP / TN / FN / FP counts and DR-012 rates | Origin-available `Supplier_Lead_Time_Days` (context only) |

Rules recorded in sources:

- `observed_target` appears only in authorised retrospective evaluation, never in predictors or prospective exports ([protocol.md §14](protocol.md)).
- The retrospective margin is evaluation evidence and must not become a prospective review input (DR-012 §7).
- The API must not use future outcome information in prospective views ([system integration workflow](workflows/system-integration-and-prototype.md)).

**Historical state — 30 October 2026; current acceptance is in Section 1.2:** The [retained-export contract](forecast-api-contract.md) applies to its fixed-origin artifact and separate retained acceptance. The merged [request-time API](forecast-inference-api.md) uses supplied history and the frozen saved producer. Section 6 of that contract preserves the 24 October manual observations and 28 October v2 capture; [Chathuranga's 29 October acceptance](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/203#issuecomment-6501737406) separately reviewed the v2 capture at `20265aa0ecb7f5e6436e8aa29694a076fc643286` with installed-file verification at `7034d296f181564ecf575152f4ce5336ee00f6e4`, closing #203 (B2 live path). PR #197 delivered retained roster/case GET routes, closing #183. Those routes validate the retained export and inventory joins to the 20 assessed records; they do not recompute a retained case from live history. Retained handoff/views continue under #201, with B14 acceptance separate. Neither prospective path exposes retrospective outcomes.

---

## 6. Inventory-risk handoff requirements (forecasting → inventory-risk → decision support)

Responsible member: Didilani. Primary source: [DR-012](decisions/DR-012-inventory-risk-replenishment-methodology.md#group-approval-record) — **group-approved 1/7/14-day scenario method**, reported by Chathuranga for the 12 October WhatsApp discussion. Method approval is distinct from source timing and consumer acceptance.

### 6.1 Inputs Didilani's component expects

| Requirement | Status | Source |
|---|---|---|
| Scenario identity: `SKU_ID`, `Warehouse_ID`, origin `t`, horizon `h` | Approved method; implemented internal mapping | DR-012 §1 |
| Project model forecast `F_t,h` with model provenance and horizon meaning retained | Implemented internal mapping; consumer acceptance separate | DR-012 §5 |
| Source `Demand_Forecast` must not substitute for the project forecast | Implemented / frozen rule | AGENTS.md §5; DR-012 §5 |
| `Inventory_Level` and `Reorder_Point` at the origin, same SKU-warehouse; snapshot date and availability assumption retained | Implemented exact-origin mapping; source timing unresolved, constructed basis explicit | DR-012 §1; shared-data foundation |
| Within-day meaning of a same-date inventory row (before / after sales) | **Unresolved** | DR-012 §1; shared-data foundation item 5 |
| `Supplier_Lead_Time_Days` as context only (shorter / equal / longer than horizon) | Approved context-only rule; availability remains independent | DR-012 §4 |
| `Order_Quantity` as context only, after origin availability is established | Approved context-only boundary; availability **unresolved** | DR-012 §5 |
| `Stockout_Flag` as dataset limitation only (zero-variance) | Implemented / frozen rule | AGENTS.md §5; dataset.md |
| Handling of negative or otherwise problematic forecasts (no clipping approved) | Implemented rejection/unavailable handling; consumer acceptance separate | DR-012 §2; inventory protocol §6.1 |
| Original inventory scope is 1 / 7 / 14 days; 28-day downstream use | 1/7/14-day method approved; h=28 **requires separate approval** | DR-012 §4 and 28-day review |

### 6.2 Outputs Didilani's component hands to Dewmi (DR-012 §8)

The internal prospective adapter implements these concepts. DR-012 does not lock the final API names, types or format:

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
| Three-state exposure rule and equality rule | Approved method; implemented internal mapping |
| Numerical replenishment quantity | **Unresolved** (provisional) |
| Overstock / excess-stock evaluation | **Unresolved** (provisional) |
| Final column names, types, interchange format | **Unresolved** |
| Implementation | Mapping, preparation, evaluation and runner implemented; retained scenario results and record bridge published |

---

## 7. Responsible decision-support handoff requirements

Responsible member: Dewmi. Primary source: [DR-011](decisions/DR-011-decision-support-output-structure.md) — **Accepted for structure only** (Issue #48).

### 7.1 Field groups (structure-only agreement)

identity / time; forecast; forecast-error / uncertainty context; inventory risk; replenishment; evidence; assumptions; limitations; management consideration; human review.

### 7.2 Requirements

| Requirement | Status | Source |
|---|---|---|
| Preserve `SKU_ID`, `Warehouse_ID`, forecast-origin date, forecast horizon; origin and horizon kept separate | Implemented in internal records; final presentation acceptance separate | DR-011 |
| Each field / group identifies its producing component (forecasting; inventory-risk / replenishment; responsible decision support) | Implemented in internal records; final presentation acceptance separate | DR-011 |
| Missing values never shown as zero; reason distinguishes: no agreed method / not applicable / waiting on another component | Internal reasons retained; final cross-component/API vocabulary **unresolved** | DR-011 |
| Human-review status with reason(s); unassessed cases shown as `not assessed`, never `false` | Implemented in internal records; final presentation acceptance separate | DR-011 |
| Advisory-only presentation; never an executable purchase order | Implemented / frozen rule | DR-011; AGENTS.md §8 |
| Standing limitations: publisher-simulated Kaggle dataset; zero-variance `Stockout_Flag` | Implemented / frozen rule | DR-011 |
| Eight transparency criteria for evaluation | Implemented in internal records; final presentation acceptance separate | DR-011 |
| Uncertainty method | **Unresolved** | DR-011 dependency table |
| Human-review rules and numerical thresholds | **Unresolved** | DR-011; responsible DS workflow |
| 28-day review triggers / 28-day downstream population | **Unresolved — approval required** | DR-011 revised interface section |
| Final column names, types, file / interchange format | **Unresolved** | DR-011 open decisions |

Candidate field names in the [responsible decision-support workflow](workflows/responsible-decision-support.md) (`forecast_origin`, `forecast_horizon`, `forecast_demand`, `inventory_risk_level`, `recommended_replenishment_quantity`, `forecast_uncertainty`, `evidence`, `assumptions`, `limitations`, `management_consideration`, `human_review_flag`) are **candidates, not final fields**.

---

## 8. Readiness summary by handoff

**Status reconciliation — 9 November 2026:** The planning rows below preserve their earlier scope. [Section 1.2](#12-current-delivery-and-acceptance--9-november-2026) supersedes open/pending assignments resolved by #201/#182/#203 and records the documentation closeout steps. Do not repeat completed reviews from these historical rows.

**Static figure implementation — 5 November 2026:** The four approved inventory
questions now have a compact eight-figure delivery, including Chathuranga's
explicitly approved forecasting/transparency additions. The
[delivery guide](research/thesis-figure-delivery.md) records sources, synthetic
checks, actual human generation, current readability corrections and recovery.
The stable output is `reports/figures/final-thesis-figures/`; static figures are
separate from the prospective retained routes and live inference. Didilani's D2,
Dewmi's W2, forecasting/technical interpretation and human code peer approval
remain separate. B14 exact-export acceptance is not inferred from PNGs or checksums. The separate
[human retained-route record](forecast-inference-api.md#human-observed-retained-route-walkthrough--5-november-2026)
now supplies startup/HTTP observations and separately attributed read-only parity checks.

| Handoff | Available / frozen | Remaining acceptance or decision |
|---|---|---|
| Retrospective forecasting research | Completed validation/final evidence; approved configurations, fresh-refit policy and producer mapping | Preserve the reviewed final interpretation and retained evidence |
| Prospective forecasting input/API | Retained exporter, request-time API, frozen DR-014 producers and synthetic examples are merged; v2 serving evidence and the separate 29 October producer/source decision complete the scoped #203 live handoff | Retained-export/source/component acceptance remains under #201/B14; live acceptance does not establish rendered or integrated acceptance |
| Forecasting → inventory-risk | Group-approved DR-012 method, implemented retained mapping and human-run scenario evidence | Source timing stays unknown; exact retained-export/consumer and representation acceptance continue under #201/B14. Additional h28 inventory use is deferred, not an automatically required extension |
| Inventory-risk → responsible decision support | Prospective bridge, populated records, completed record assessments and W1 interpretation/display acceptance as reported by Chathuranga | Retained component/representation acceptance and W2 rendered review remain under #201/#182. Numerical uncertainty, replenishment and automatic review rules remain deferred/unavailable |
| Components → prototype/API | PR #197 delivered retained roster/case response schemas, source-bound adapters and synthetic API/integration checks; #183 is closed | #201 now has recorded human-observed retained startup/route checks and an eight-figure delivery; source/component and rendered acceptance remain with the relevant reviewers, and final prototype acceptance remains under #179 |

Completed retrospective evidence resolves the former absence-of-validation-evidence blocker. It does not resolve prospective contract acceptance or other members' methodologies. Closed issue references below identify historical requirements or delivered milestones; #179 is the current umbrella, with #201/#182 tracking the relevant continuations.

## 9. Blockers

**Status reconciliation — 9 November 2026:** The planning rows below preserve their earlier scope. [Section 1.2](#12-current-delivery-and-acceptance--9-november-2026) supersedes open/pending assignments resolved by #201/#182/#203 and records the documentation closeout steps. Do not repeat completed reviews from these historical rows.

B1 (retained forecasting evidence availability) is resolved by the completed validation/final evidence. Remaining blockers retain their existing owners and approval boundaries.

**Checksum evidence (reported):** The latest successful Didilani-profile verification against reviewed reference `fd4debcac0719fca306c99d32dacfbe391230ec4` matched 5/5 files, including `data/processed/validated/supply-chain-dataset1-validated-v1/validated.parquet`. This is file identity/integrity evidence only; it does not establish producer acceptance, consumer acceptance, inventory-timing evidence, methodology approval, or evaluation authorization.

**Human-run evidence update — 23 October 2026:** Chathuranga completed the constructed-origin inventory evaluation and prepared its inventory-linked decision-support records. Shared review copies are indexed under [inventory evidence](../reports/README.md#inventory-risk-evaluation-evidence) and [inventory-linked records](../reports/README.md#inventory-linked-records). The evaluation has 239 paired comparisons plus 11 scenario-at/below-threshold cases per 1/7/14-day horizon. Fifteen selected records contain inventory evidence; five h=28 records remain gated. Chathuranga subsequently confirmed all 160 record-level assessment outcomes; Codex transcribed them with his assessor name and date `2026-10-23`. Chathuranga manually generated the [assessment summary](../reports/decision-support/issue-168-inventory-v1/summary.md), which retains all 20 applicable cases per criterion and their unavailable outcomes. This individual assessment does not establish group methodology approval, component acceptance or prototype presentation quality.

The decision rows below reconcile the historical Issue #164 milestone with current acceptance work; detailed method and protocol definitions remain in [DR-012](decisions/DR-012-inventory-risk-replenishment-methodology.md) and the [inventory-risk evaluation protocol](research/inventory-risk-evaluation-protocol.md). Existing issue references are tracking pointers, not a claim about their current live status. A separate issue may be considered only for substantial work after checking live GitHub for overlap; no issue is created or assigned here.

| ID | Decision | Evidence and approval status | Required reviewers | Remaining action | Existing tracking issue / document | Separate issue? |
|---|---|---|---|---|---|---|
| B2 | **Forecasting API review and consumer handoff — live path accepted** | Request-time implementation and v2 serving evidence are delivered; [Chathuranga's separate 29 October producer/source acceptance](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/203#issuecomment-6501737406) reviewed the capture at `20265aa0ecb7f5e6436e8aa29694a076fc643286` together with reported 20/20 installed-file verification at `7034d296f181564ecf575152f4ce5336ee00f6e4`. #203 is closed. | Chathuranga and Tinosh for the live handoff; #201 executor/reviewers for retained delivery | Reuse accepted live evidence for unchanged behaviour. Continue retained runtime/component acceptance under #201/B14; it is not established by the live decision. | #203 acceptance; #193/#195 producer corrections; #180/#184 manual evidence; #183/#197 retained API; #201 continuation | No duplicate live acceptance task; retain #201/#179 for unfinished delivery. |
| B14 | **Forecast export acceptance and provenance** | Run `final-20261003-02`; Chathuranga confirmed producer/source acceptance and reported Didilani's consumer acceptance. The 9 November reviewed-baseline export check matched 1/1; Section 1.2 records scope/output and his clarification resolving the old pending figure items. | Chathuranga (producer); Didilani (consumer); Tinosh (technical representation) | Reuse completed source verification and reported acceptance; no repeated component confirmation is requested. The documentation closeout PR records this correction; #179 closure takes effect on human merge into `main`. | [Current acceptance record](#12-current-delivery-and-acceptance--9-november-2026); #179; #201 closeout; [checksum reference](checksums/2026-10-06.json) | No replacement implementation or issue required. |
| B3, B13 | **Origin inventory snapshot timing and availability** | Source timing remains unknown. The runner provides an explicit constructed-origin scenario with separate assumption, analysis-availability and scenario-state fields; it never changes unknown source timing to verified availability. `Order_Quantity` is not treated as receipts. | Didilani; relevant dataset/source owner if identifiable; Chathuranga for forecast-time alignment | Select and disclose the specific run's snapshot policy using [protocol §12.2](research/inventory-risk-evaluation-protocol.md#122-run-the-implemented-inventory-evaluation); retain unknown source timing and distinguish conditional scenario evidence from source-confirmed evidence. | #164; #162; #51; #70 / #85; [dataset](dataset.md); [protocol](research/inventory-risk-evaluation-protocol.md) | Existing implementation; source semantics remain distinct. |
| B6 | **Forecast-to-inventory field mapping** | The exact retained-export mapping is implemented in `src/inventory_risk/forecast_handoff.py`: validated identity/timing, explicit status and source-forecast eligibility, source-bound primary role and provenance propagation. Snapshot availability remains an independent input. | Chathuranga, Didilani, and Tinosh jointly | Inspect the completed human-run evidence in [protocol §12.3](research/inventory-risk-evaluation-protocol.md#123-retained-human-run-evidence); record actual consumer acceptance and retain unknown snapshot timing rather than inferring it. | #164; #162; #70 / #85; shared-data foundation item 6; [protocol §4.1](research/inventory-risk-evaluation-protocol.md#41-implemented-forecast-to-inventory-mapping) | Existing implementation; no replacement issue created. |
| B5 | **Problematic forecast handling** | Implemented validation rejects invalid source exports and retains finite negative values as unavailable inventory inputs; no rounding, clipping, substitution or row deletion. | Chathuranga and Didilani; Tinosh for technical error handling | Review the implemented distinctions between whole-input failure and retained-row unavailability in [protocol §6.1](research/inventory-risk-evaluation-protocol.md#61-implemented-validation-and-error-behaviour). | #164; #162; #70 / #85 | Existing implementation; no replacement issue created. |
| B4 | **DR-012 group approval — recorded** | The group approved the 1/7/14-day fixed-origin/no-receipt exposure method on 12 October, as reported by Chathuranga on 23 October under #177. Historical run labels remain unchanged. | COMP1884 group; reporting attribution: Chathuranga | Use the [approval record](decisions/DR-012-inventory-risk-replenishment-methodology.md#group-approval-record); do not obtain the same approval again. | #177; historical #164/#51 | Resolved approval-record gap. |
| B8, B12 | **Additional horizon/replenishment scope — deferred** | Team acceptance reported by Chathuranga on 29 October retains h28 inventory use, numerical replenishment and overstock as disclosed limitations/deferred extensions; DR-012 remains h1/h7/h14 only. | Didilani and relevant human/team reviewers | Keep these outputs unavailable. Any future method or extension needs a separately justified human decision; deferral is not implementation approval. | [C1 scope/closeout record](research-design.md#164-human-decisions-and-c1-closeout-record); DR-012 | Deferred scope, not a current delivery blocker or automatic implementation task. |
| B15 | **Retrospective evaluation eligibility** | The implemented runner requires exact complete daily `Units_Sold` windows for 1/7/14-day targets and reports the existing DR-012 metrics separately by horizon. Invalid/missing targets remain unavailable; duplicate daily keys fail. The completed human-run constructed-scenario results are distinct from implementation tests. | Didilani; Chathuranga for forecast/temporal evidence; group review of methodology | Review the retained run in [protocol §12.3](research/inventory-risk-evaluation-protocol.md#123-retained-human-run-evidence); retain Dec 3–16 prior validation exposure and full-year exploratory-exposure disclosures. | #164; #162; [evaluation protocol](research/inventory-risk-evaluation-protocol.md); [DR-005](decisions/DR-005-forecast-validation-design.md) | Existing runner implemented at Chathuranga's explicit request; no issue created. |
| B7, B9 | **Inventory-risk-to-decision-support handoff** | A concrete internal prospective-only adapter is implemented: manifest/hash/source-bound 1,000-key evidence feeds the 20 decision-support records. Snapshot assumptions, source status, method limitations and unavailable reasons are preserved; retrospective fields and h=28 inventory interpretation are rejected/gated. This does not establish final API or presentation acceptance. | Didilani and Dewmi; Tinosh for technical representation | Inspect the completed inventory-backed [record preparation](research/responsible-decision-support-evaluation.md#22-prepare-records-and-record-the-human-assessment) and complete the remaining component/presentation acceptance; the 160 record-level checks are already delivered. No human-review threshold or new uncertainty method is introduced. | #164 (inventory-side decisions); #168 (record mapping, transparency assessment and presentation handoff); #153 (historical context); #85; #72 / #73; [DR-011](decisions/DR-011-decision-support-output-structure.md) | Existing internal adapter implemented; final shared API/presentation remains separate. |
| B10 | **Automatic human-review rules — deferred** | Team deferral and Dewmi's W1 interpretation/display acceptance reported by Chathuranga on 29 October. [Dewmi's direct confirmation on 1 November](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/182#issuecomment-6555332904) additionally accepts W1 and supports automatic triggers only as a deferred extension. No trigger or threshold method is approved. | Dewmi and relevant producing members | Render `not_assessed` with its reason and preserve advisory wording. Complete actual W2 presentation review under #182; do not invent automatic rules. | [C1 scope record](research-design.md#164-human-decisions-and-c1-closeout-record); #182/#201 | Method deferred; rendered review remains in existing tasks. |
| B11 | **Prospective forecast uncertainty — deferred** | Team deferral explicitly reported by Chathuranga on 29 October; uncertainty remains unavailable with `no_agreed_method`. | Chathuranga; relevant team scope reviewers | Preserve the existing unavailable field/reason. A future numerical method needs separate approval; retrospective error is not substituted for uncertainty. | [C1 scope record](research-design.md#164-human-decisions-and-c1-closeout-record) | Deferred extension, not an unresolved requirement to select a method now. |

---

## 10. Continuing integration work — available work and dependencies

**Historical scoping guidance:** Current delivery is complete at the scope in Section 1.2. The rows below are retained for their original dependency logic and future-extension boundaries, not as unfinished #179 assignments.

### 10.1 Scope each continuation

PR #197 delivered the retained API slice; #201 subsequently completed its bounded continuation. The following original scoping guidance applies to separately approved future extensions. Existing scoped acceptance is recorded in Section 1.2; these rows are not current implementation assignments.

- Narrow the next integration task to **one** reviewed handoff and a concrete, testable interface, using the reviewed readiness requirements.
- Draft that narrowed interface as a proposal for the relevant owner's review (draft only; not a final schema).
- Prepare test-case descriptions from requirements that are already frozen: identity preservation, separate origin and horizon, `target_start_date` = origin + 1, `target_end_date` = origin + h, no `observed_target` in prospective views, advisory-only output, `not assessed` instead of `false`.
- Any technical reading of the existing frozen forecasting artifact schema (`issue-65-v2`) using synthetic fixtures only, labelled as retrospective validation evidence — **only if Chathuranga confirms this is in scope for the narrowed integration task.**

### 10.2 Must wait

The current delivery and scoped reviews are complete as recorded in Section 1.2. The dependency rows below preserve the original planning boundaries; they do not reopen completed acceptance. Deferred method extensions require separate approval and are not required additions to #179.

| Work in the next integration task | Waits for |
|---|---|
| Accept/extend the retained-export mapping or connect live inference to downstream analysis | B3, B5, B6, B14; the existing mapping and accepted #203 serving path do not establish retained/downstream acceptance |
| Accept/extend the implemented record bridge for final delivery | B7, B9; B12 only if numerical replenishment is added |
| Extend the accepted request-time forecast API beyond its current contract | A separately reviewed scope/contract change; #203's existing live handoff is accepted (B2) |
| 28-day inventory calculation or review trigger | B8; forecast identity and explicit unavailability can already be shown |
| New automatic human-review triggers | B10; existing not_assessed status and reasons can be rendered under reviewed record semantics |
| Numerical uncertainty values | B11; an unavailable field with its existing reason can already be rendered |
| Inventory-risk visual components | #201 implementation/runtime evidence using Didilani's existing approved specification; no repeat specification decision is needed |
| Decision-support record presentation | Implement the W1 handoff accepted as reported by Chathuranga; actual rendered W2 review was a dependency at this planning checkpoint and is now accepted under closed #182 (B7, B9) |
| Any use of real run outputs | Stage-specific verified run_manifest.json and human acceptance of the exact handoff |

### 10.3 Start checklist for the next integration task

- [ ] This document is reviewed by Chathuranga, Didilani and Dewmi.
- [ ] The next integration task is narrowed to one handoff with a named producer, consumer and reviewer.
- [ ] The producing component's output for that handoff is human-reviewed and available (not only planned).
- [ ] Field names, types and format for that handoff are agreed by the producing owner.
- [ ] Origin, horizon and target-interval meaning for that handoff match Section 4.
- [ ] Retrospective fields are excluded from any prospective part of the interface.
- [ ] Unavailable-state reasons for that handoff are agreed (no zero or `false` substitutes).
- [ ] Any 28-day content is either approved or explicitly marked unavailable.
- [ ] No pending decision in Section 9 is settled through an adapter default.
- [ ] Concrete, testable acceptance criteria are written into the narrowed integration task.

---

## 11. Standing limitations

- The dataset downloaded from Kaggle is simulated by its publisher; outputs are not validated for a real retailer ([dataset.md](dataset.md); DR-011).
- `Stockout_Flag` is zero-variance and cannot be stockout ground truth.
- The final evaluation interval (2024-12-03 to 2024-12-30) is reserved but not historically fully unseen; December 3–16 had earlier validation exposure and full-year EDA inspected it ([protocol.md §3, §12](protocol.md)).
- All framework outputs are advisory decision support, not executable purchase orders.

## 12. Integration acceptance scenarios (Issue #101)

**Issue:** #101 — Docs: specify integration acceptance scenarios from frozen handoff requirements

**Builds on:** Issue #87 (Sections 1–11 of this document). Issue #101 lists #98, #70 and #73 as completed inputs. This section uses their requirements only as they are already reflected in Sections 3–9 and in the merged component tests named below.

**Status:** #101 delivered the scenario specification. Existing component coverage and the subsequently merged synthetic API/integration coverage are distinguished in Section 12.3. Completed human-observed runtime and scoped rendered reviews are linked in Section 1.2; the original scenario specification and automated results alone do not establish those outcomes.

### 12.1 Rules for this section

- **Synthetic data only.** Every value below is invented for illustration (`SKU_SYN_A`, `WH_SYN_1`, `syn-run-01`, small demand numbers). None comes from the project dataset or a real run.
- **Real names only where they already exist.** Back-ticked forecasting names (`SKU_ID`, `Warehouse_ID`, `forecast_origin`, `horizon`, `target_start_date`, `target_end_date`, `prediction`, `observed_target`, `run_id`, `evaluation_stage`, `evidence_role`, `model`, `configuration_id`, `canonical_config_id`) are the implemented `predictions.csv` columns in [artifacts.py](../src/forecasting/artifacts.py). Downstream content in these original scenarios is described in plain words. The merged retained response schemas are documented in the [API contract](forecast-inference-api.md#51-retained-decision-support-cases); their existence does not settle every final consumer/encoding decision (B6, B7, B9).
- **No new defaults.** Where a value is missing or unapproved, a scenario only requires that this is visible with a reason. It does not choose a fallback, clipping rule, uncertainty method or review threshold.
- **Three kinds of evidence.** *Component unit coverage* checks behaviour inside one component. *Synthetic API/integration coverage* checks the implemented HTTP/adaptor path with disposable fixtures or model doubles. *Human runtime/rendered acceptance* records actual consumption and presentation review. Section 12.3 identifies existing automated coverage without marking an entire scenario or human acceptance complete.
- **Issue references.** #132, #164, #168, #85, #145 and #153 are closed historical requirement/evidence references. #101/#157 delivered these scenarios; #177 records the earlier refined baseline. #193/#195 and #183/#197 delivered later implementation work; #201 and #182 are completed milestones; #179 records repository closeout through the documentation PR. Closure does not replace missing acceptance evidence.
- **Positive** examples show acceptable behaviour. **Negative** examples show behaviour a later integration must reject or never produce.

### 12.2 Acceptance matrix

| ID | Requirement | Authoritative reference | Synthetic scenario | Expected invariant / observable behaviour | Remaining dependency | Responsible reviewer |
|---|---|---|---|---|---|---|
| AS-01 | Identity preservation | AGENTS.md §5 (DR-002 grain); [protocol.md §6, §14](protocol.md); §3.2 | One forecast for `SKU_SYN_A` / `WH_SYN_1` passes through a handoff | The same `SKU_ID` + `Warehouse_ID` pair arrives unchanged; no merging, swapping or new identity; an unknown identity fails explicitly | #164; #132; #168 | Chathuranga; Didilani |
| AS-02 | Forecast origin is not the target start | [protocol.md §2, §5](protocol.md); §4; shared-data foundation | Origin 2024-03-31, h = 28 | Origin shown as 2024-03-31; target start shown as 2024-04-01; never equal or swapped | #132; #164 | Chathuranga; Didilani |
| AS-03 | Inclusive target window | [protocol.md §2, §3](protocol.md); §4 | Origin 2024-11-04, h = 7 | Window is 2024-11-05 to 2024-11-11, both days included, exactly 7 days | #132 | Chathuranga |
| AS-04 | Horizon preservation | DR-004; DR-008; [protocol.md §2](protocol.md); §4 | Same pair and origin with h = 1, 7, 14, 28 | Four separate records, each keeps its horizon; 7/14/28 stay cumulative totals; no daily path or cross-horizon total | #132; #164; B8 for 28-day downstream use | Chathuranga; Didilani; Dewmi |
| AS-05 | Provenance preservation | [protocol.md §7.3, §11, §14](protocol.md); DR-011 source distinction; §3.4 | A primary and a supportive record from `syn-run-01` | Each record keeps `run_id`, `evaluation_stage`, `evidence_role`, `model`, `configuration_id`; supportive `canonical_config_id` stays empty; the producing component stays identifiable | #132; #164; #168 | Chathuranga; Dewmi |
| AS-06 | Retrospective outcomes kept out of prospective presentation | [protocol.md §14](protocol.md); DR-012 §7; §5; system integration workflow | One record with `prediction` 14.0 and `observed_target` 15 | A retrospective view may show both, clearly labelled; a prospective view shows no `observed_target`, error or metric | #132; #168 | Chathuranga; Dewmi |
| AS-07 | Unavailable information stays visible with a reason | DR-011 missing-value semantics; DR-012 §2; §7.2 | Origin inventory snapshot missing; upstream evidence missing | Shown as unavailable with a reason; never zero, never silently dropped, never scored | #164; #168; B9 | Didilani; Dewmi |
| AS-08 | Advisory-only presentation | DR-011; AGENTS.md §8; system integration workflow | Exposure evidence shown to a manager | Presented as guidance for human consideration; no automatic or executable order | #168; B7; B10 | Dewmi; Didilani |
| AS-09 | "Not assessed" with a reason, never `false` | DR-011 human review; DR-012 §8; §7.2 | A record before any review method is approved | Review status reads as not assessed, with a reason; never `false`, "no" or blank | #168; B9; B10 | Dewmi |
| AS-10 | Undefined metric stays unavailable | [protocol.md §8](protocol.md) | Retrospective group whose actual total is 0 | WAPE is unavailable (`undefined_zero_actual_total`), not 0 or infinity; supporting metrics are kept | None (retrospective only) | Chathuranga |

### 12.3 Existing coverage and pending checks

| ID | Component unit coverage (existing tests) | Remaining acceptance scope (synthetic coverage below) |
|---|---|---|
| AS-01 | `tests/test_forecasting_features.py` (invalid and duplicate keys rejected); `tests/test_forecasting_evaluation.py` (row index is not an identity key); `tests/test_inventory_risk_preparation.py::test_preparation_preserves_identity_timing_provenance_and_source_fields` | Identity carried unchanged from forecast → inventory-risk → decision-support record → API/prototype view |
| AS-02 | `tests/test_forecasting_features.py` (origin features use the first target day, not the origin); `tests/test_inventory_risk_preparation.py::test_preparation_preserves_identity_timing_provenance_and_source_fields` | Origin and target start displayed separately in the API response and prototype |
| AS-03 | `tests/test_forecasting_features.py` (inclusive fold boundaries; targets fit inside windows) | Inclusive window shown correctly in the API response and prototype |
| AS-04 | `tests/test_forecasting_evaluation.py` (direct cumulative, not recursive); `tests/test_forecasting_configuration.py` (unapproved horizons rejected); `tests/test_inventory_risk_preparation.py::test_preparation_preserves_identity_timing_provenance_and_source_fields` | Four horizons kept separate across the handoff; no daily path drawn; 28-day downstream content stays gated (B8) |
| AS-05 | `tests/test_forecasting_orchestration.py::test_exact_csv_column_order_is_checked_against_the_frozen_protocol`; `tests/test_forecasting_orchestration.py::test_artifacts_are_exclusive_safe_and_reject_schema_drift`; `tests/test_inventory_risk_preparation.py::test_preparation_preserves_identity_timing_provenance_and_source_fields` | Provenance and producing component visible in the decision-support record and prototype |
| AS-06 | `tests/test_forecasting_features.py` (post-origin actuals masked); `tests/test_forecasting_evaluation.py` (outcomes change only targets) | No observed outcome, error or metric in any prospective API response or view |
| AS-07 | `tests/test_inventory_risk_evaluation.py::test_unavailable_snapshot_is_retained_and_not_scored`; `tests/test_decision_support_records.py::test_missing_upstream_evidence_requires_explicit_reason` | Unavailable state and reason carried across handoffs and shown in the prototype; final encoding still open (B9) |
| AS-08 | No dedicated component test identified for advisory wording | Advisory-only wording and absence of order actions checked in the prototype |
| AS-09 | `tests/test_decision_support_records.py::test_default_human_review_status_is_not_assessed`; `tests/test_decision_support_records.py::test_not_assessed_must_have_reason` | Not-assessed status and reason shown in the prototype; automatic review rules deferred (B10); preserve the accepted W1 semantics |
| AS-10 | `tests/test_forecasting_models_metrics_baselines.py::test_zero_wape_denominator_keeps_supporting_metrics_and_json_null` | Unavailable WAPE shown as unavailable in any retrospective view |

**Delivered synthetic API/integration coverage — source baseline `b6f196a`, updated 25 October 2026:**

| Scope | Existing test and what it verifies | What it does not establish |
|---|---|---|
| AS-01/02/04/05/06, selected retained API assertions | `tests/test_decision_support_retained_cases.py::test_existing_validators_join_synthetic_twenty_case_roster_and_gate_h28` checks the 20-case roster, selected identity/origin/target-start/provenance fields, cumulative wording, h28 inventory gating and exclusion of listed retrospective fields in HTTP responses | Exhaustive acceptance of every field/window, actual installed inputs or rendered visibility/readability |
| Identity/origin/horizon mismatch rejection | `tests/test_decision_support_retained_cases.py::test_wrapper_nested_identity_origin_and_horizon_mismatches_fail` rejects mutated wrapper/nested identities and an incomplete roster | A completed human consumer review |
| AS-07/09, selected availability/review assertions | `tests/test_decision_support_retained_cases.py::test_null_zero_false_unknown_and_reasons_are_preserved` checks distinct zero/null/false values, unknown snapshot timing with its reason and the retained `not_assessed` status | Final display wording, managerial review or an approved review-trigger method |
| Retained-source failures and read-only serving | The same file's `test_changed_records_bytes_fail_the_pinned_and_manifest_hashes`, `test_manifest_cannot_be_rebound_to_another_forecast_export`, `test_missing_or_tampered_retained_files_make_routes_unavailable` and `test_lifespan_and_requests_never_prepare_or_assess_records` check source binding, API unavailability on missing/tampered files, unchanged returned records and no preparation/assessment/evaluation calls or fixture writes during serving | Independently reviewed installed-file provenance, scientific validity or human acceptance |
| Separate request-time execution | `tests/test_forecast_api.py::test_four_example_requests_compute_new_outputs` and `test_api_passes_changed_history_to_model_on_every_request` check four-horizon HTTP responses and per-request invocation with synthetic model spies | Saved-model accuracy; Tinosh's saved-model consumer verification is recorded separately below |
| #203 evidence helper | `tests/test_capture_consumer_evidence.py` checks, with an in-memory synthetic API, that `capture_consumer_evidence.py` derives AS-01 to AS-06 and the request-time contract, changed-history and rejection outcomes from recorded exchanges (passing and failing cases), refuses to overwrite existing evidence and re-verifies stored outcomes | Saved-model behaviour, producer approval or independently reviewed source verification |

The [recorded checks](forecast-inference-api.md#scoped-checks-and-observed-automated-outcomes--25-october-2026) report 128 targeted synthetic tests plus scoped Ruff/MyPy passing for the PR #197 correction. [CI Tests](https://github.com/chathuranga-sudusinghe/retail-demand-framework/actions/runs/40180999250) and [CI Quality](https://github.com/chathuranga-sudusinghe/retail-demand-framework/actions/runs/40180999258) passed at `c540f0384b3a3fe04f56124a90d5e7ac32951f5c`. These are reused results, not new executions for this documentation update. Advisory wording, actual rendered views, retrospective metric presentation and final component acceptance still require their applicable reviews; no complete AS-01–AS-10 pass is asserted.

**Additional #201 implementation checks — 5 November 2026:** The approved
readability/recovery follow-up passed 75 synthetic tests across the four
visualization test files and `tests/test_decision_support_retained_cases.py`.
This adds marker/value retention, explicit evaluation-only/negative-margin
caveats, hatch-label backgrounds, tick-label spacing and interrupted-publication
recovery checks to the existing retained-route coverage. Scoped Ruff/MyPy and
format checks passed; 186 local link targets in the changed delivery/API/report
documents existed. The installed API inventory bundle matched the four tracked
review-copy files byte for byte, and the records hash matched its preparation
manifest. These local checks do not upgrade reference provenance or replace
human runtime observations, B14 producer/consumer acceptance, D2 or W2.

### Consumer Verification Results — related to #203

Request-time API path only. Outcomes are derived by `capture_consumer_evidence.py` from the recorded exchanges in the evidence file and re-derived by its `--verify` mode; check details are in [the inference contract, Section 6.2](forecast-inference-api.md).

| Requirement | Request-time check basis | Derived outcome |
|:---|:---|:---|
| AS-01 | Identity echoed unchanged for h1/h7/h14/h28; unknown SKU and warehouse rejected with HTTP 422 reason codes | **PASSED** |
| AS-02 | Origin echoed; `target_start_date` = origin + 1 | **PASSED** |
| AS-03 | `target_end_date` = origin + h; inclusive window of exactly h days | **PASSED** |
| AS-04 | Horizon and `forecast_type` preserved; cumulative and 28-day limitation wording; four separate records; unsupported horizon rejected | **PASSED** |
| AS-05 | Designated producer and configuration; source run/manifest; `model_hash`, `preprocessor_hash`, `input_sha256` digests; repeat and changed-history input hashes | **PASSED** |
| AS-06 | Exact response allowlist; no retrospective, inventory or metric keys; such request fields rejected | **PASSED** |
| `RT-CONTRACT` | Health ready; HTTP 200, available, finite quantity; example files unchanged | **PASSED** |
| `RT-CHANGED-HISTORY` | Final-day `Units_Sold` +5 in memory yields a new `input_sha256` with the same producer | **PASSED** |
| `RT-REJECTIONS` | Ten negative requests return HTTP 422 without a substitute quantity | **PASSED** |

* **Reviewer:** Tinosh (technical request-time consumer).
* **Capture:** `2026-10-28T15:35:48+00:00` (28 October 2026, Asia/Colombo); tested source revision `20265aa0ecb7f5e6436e8aa29694a076fc643286`.
* **Evidence:** `research-materials/issue-203/consumer-evidence-v2.json` (SHA-256 `ee048a7412f5727cb5bebfe606ecf3784fecba2352e06c25d43a415817af9abf`).
* **Superseded:** `research-materials/issue-203/consumer-evidence.json` is preserved unchanged; it captured h7 only and its outcomes were constants. The previously cited SHA-256 `503a3d03…` and 25 October date are withdrawn.
* **Scope:** these rows cover the live request-time path only. They do not complete AS-01 to AS-06 across the retained, inventory or prototype handoffs in the table above, and AS-07 to AS-10 are outside this check.
* **Status:** [#203 closed on 29 October](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/203#issuecomment-6501737406) after Chathuranga's separate producer/source acceptance. He reviewed the v2 serving capture and reported 20/20 installed-file verification at `7034d296f181564ecf575152f4ce5336ee00f6e4`; the capture remains at its stated `20265aa` revision. Historical pending labels in the evidence are unchanged. This does not accept retained inputs/views or complete the full AS-01–AS-10 integration suite.

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

These describe **behaviour only**. The implemented records/API retain `human_review_status=not_assessed` and source-specific unavailable reasons. Dewmi’s [accepted W1 interpretation/display baseline](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/182#issuecomment-6555332904) supplies the semantic handoff; a new universal vocabulary or another W1 decision is not required. At that checkpoint, B9 concerned actual component/presentation acceptance under #182/#201; both later completed scopes are linked in Section 1.2. Human-readable labels may explain existing codes without changing retained values. This reconciliation records the current state on 5 November 2026.

#### Unavailable information (AS-07)

DR-011 separates three reasons: **no agreed method**, **does not apply**, and **waiting for another component's decision or output**.

| Synthetic situation | Acceptable behaviour | Must never happen |
|---|---|---|
| Uncertainty for any forecast (no method, B11) | Shown as unavailable; reason: no agreed method | Shown as 0, ±0 or an invented range |
| 28-day inventory exposure (approved deferral, B8) | Shown as unavailable with its original source reason and current deferred-scope context | Calculated by extending DR-012 on its own, or described as an unresolved current-delivery decision |
| Replenishment quantity (approved deferral, B12) | Shown as unavailable; preserve the source reason and disclosed limitation | Shown as 0 units or as a suggested order |
| Origin inventory snapshot missing for `SKU_SYN_A` / `WH_SYN_1` | Record retained, exposure unavailable with a reason and not scored; the forecast itself can still be shown (DR-012 §2) | Record silently dropped, scored, or filled from a later snapshot |
| Upstream evidence missing for a decision-support record | Explicit reason recorded | Field left blank or shown as complete |
| Observed demand of 0 on a real day | Shown as 0 — a real zero | Treated as unavailable |

#### Advisory-only presentation (AS-08)

| Acceptable | Must never happen |
|---|---|
| "Illustrative threshold-crossing evidence — advisory information. Human-review status remains not assessed; no automatic review trigger is implied." | "Order 120 units now" |
| Evidence, assumptions and limitations shown next to the result | A button or action that creates a purchase order |
| The final decision is clearly left with a responsible person | Wording that implies the system approved the action |

#### "Not assessed" with a reason (AS-09)

| Acceptable | Must never happen |
|---|---|
| Review status: not assessed; reason: no approved review method yet | Review status shown as `false` |
| Exposure assessed but review still not assessed (independent, DR-012 §8) | "No review needed" when no rule exists |
| More than one reason kept when more than one applies | Not-assessed status with no reason |

### 12.6 Ready to specify now versus waiting on dependencies

**Status reconciliation — 9 November 2026:** The planning rows below preserve their earlier scope. [Section 1.2](#12-current-delivery-and-acceptance--9-november-2026) supersedes open/pending assignments resolved by #201/#182/#203 and records the documentation closeout steps. Do not repeat completed reviews from these historical rows.

**Specified requirements with existing component coverage** (frozen sources and component tests exist; no pending decision is needed to write the expected behaviour):

- AS-01 to AS-06 inside the forecasting component, using the implemented `predictions.csv` fields and synthetic records;
- AS-01, AS-02, AS-04, AS-05 and the unavailable-snapshot case of AS-07 inside the inventory-risk preparation and evaluation components;
- the not-assessed default, reason requirement and missing-evidence reason inside decision-support records (AS-07, AS-09);
- AS-10;
- the **behaviour** described in 12.5, but not its final interchange encoding.

**Resolved live dependency:** #203's AS-01–AS-06 request-time handoff is accepted through the separate 29 October producer/source decision; reuse Section 12.3's evidence for unchanged behaviour. B14 concerns retained-export acceptance, not this resolved live handoff.

**Waiting on a dependency** (cross-component or rendered acceptance remains):

| Depends on | Scenarios affected | What must exist first | Related blockers |
|---|---|---|---|
| #201/#179; historical #164 and #183/#197 delivery | AS-01, AS-02, AS-04, AS-05 and AS-07 across forecasting → inventory | Mapping and retained HTTP delivery exist; accept the exact retained input/consumer contract and human-observed flow; source timing stays unknown or explicitly constructed | B3, B5, B6, B13, B14 |
| #182 and #201/#179; historical #168 | AS-05 to AS-09 in the prototype | Record mapping, 160 record checks and retained API delivery exist; W1 interpretation/display acceptance is reported; actual W2 rendered acceptance remains | B7, B9, B10 |
| Separate future approval only if the accepted scope is reopened | Numerical uncertainty or h28 inventory content | These methods are deferred under the 29 October team record. Current views may render their existing unavailable states/reasons without adding a method | B8, B11 |

**Historical references:**

- **#85** supplied the analytical visual specification. #164 delivered the mapping/evaluation milestone. #181/#188/#190 delivered inventory interpretation and report insertion/reviews; #192/#194 aligned that documentation. Remaining approved views and rendered review continue under #201/#179.
- **#145** is closed; its preparation work was merged through #152.
- **#153** is historical. #168 subsequently delivered populated records and completed record-level assessment; rendered presentation acceptance is separate.

The historical closures of #164/#168 do not imply other acceptance. B4 approval is recorded under #177; B2 live acceptance is recorded under #203. Source timing (B3/B13), exact retained handoff acceptance (B5/B6/B14) and retained/rendered representation (B7/B9) remain separate. B8/B10/B11/B12 now reference the team-accepted deferrals; they do not require those methods to be implemented for current delivery.

### 12.7 What this section does not do

- It does not add runtime code, adapters, FastAPI endpoints, charts or automated tests.
- It does not define final shared or interchange schemas, field names, encodings or defaults.
- It does not choose an uncertainty method, review threshold, clipping rule or replenishment quantity.
- It does not change any research methodology or authorise any experiment.


## 13. Remaining-work handoff after Issue #177

**Status reconciliation — 9 November 2026:** The planning rows below preserve their earlier scope. [Section 1.2](#12-current-delivery-and-acceptance--9-november-2026) supersedes open/pending assignments resolved by #201/#182/#203 and records the documentation closeout steps. Do not repeat completed reviews from these historical rows.

The following handoff is reconciled on 30 October 2026 at `a3f6368bbbec6cc7a2bfc67bd46e29202bef8b63`, with the subsequent #191 closeout and #203 acceptance referenced above. The #201 retained implementation and #182 rendered-review scopes remain open. Reuse existing evidence and tasks; this table creates no new issue, assignment, ownership transfer or research approval.

| Responsible member | Delivered starting point | Next focused scope and dependencies |
|---|---|---|
| Chathuranga | Completed forecasting study, frozen producers, accepted #203 live handoff and closed #191 descriptive C1 scope | Review forecasting/API representation in #201 and reconcile repository documentation under #179. Preserve the recorded team deferrals and source-timing limitations. Do not rerun completed forecasting or add an RQ2 significance test. |
| Didilani | Group-approved DR-012 method, mapping/evaluator, human-run scenario results, reviewed interpretation/report insertion and visual specification; recorded contributions to the retained API | Execute the bounded #201 continuation: remaining retained runtime/source/component handoff and approved inventory views. Record inventory interpretation; another human reviews code, while Chathuranga and Dewmi review their respective semantics. No repeat DR-012 approval or research run. |
| Dewmi | Populated records, 160 checks assessed by Chathuranga and W1 interpretation/display acceptance as reported by Chathuranga | Review actual #201 views under #182 W2 when a revision is reviewable. Reuse the accepted W1 interpretation and unchanged record assessments; preserve attribution. |
| Tinosh | Accepted #203 live handoff; original PR #197 authorship; retained adapters, synthetic checks and AS-01–AS-10 specifications | Provide technical review/support for #201's implementation, affected CI and single integrated setup/report account. Reuse accepted live evidence. The bounded implementation assignment to Didilani preserves his permanent technical role and earlier contributions; keep live/retained paths distinct. |

All members retain their component/repository reviews under #179. Final submission-file preparation, presentation preparation and individual reflections are outside #179. Following #179 repository closeout, #204 covers Chathuranga's preparation of the final report/presentation and his own reflective file if required; each member remains responsible for their own reflection. Official deadlines, formats and assessment-specific permissions still require actual source confirmation; C1's descriptive scope is closed under the recorded human decision. The five deferred extensions remain unavailable unless separately approved. Method approval and completed C1 do not establish significant managerial benefit or final prototype acceptance.
