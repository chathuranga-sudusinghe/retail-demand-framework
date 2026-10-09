# Inventory-Risk Evaluation Protocol

> **Status: Proposed for human review; not approved for execution.**
>
> This document prepares the input-contract and evaluation decisions requested by [Issue #162](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/162). It records current evidence and proposes a reproducible protocol for later review. It does not approve DR-012, a final interchange schema, or any dataset-backed analysis.

## 1. Purpose and status

The purpose is to make the proposed forecast-to-inventory input mapping and any later retrospective evaluation reviewable before execution. The source of method definitions is [DR-012](../decisions/DR-012-inventory-risk-replenishment-methodology.md), which remains **Proposed for group approval**. The Issue #70 preparation and evaluation utilities implement that proposal as structured evidence; they do not turn it into an approved method or establish results from the supplied data.

This is a protocol proposal only. No inventory-risk evaluation, result table, metric, or chart is produced here. A later dataset-backed run needs separate, specific authorization after the relevant method, mapping, protocol, and execution-critical dependencies have been reviewed.

## 2. Source artifacts and provenance

| Evidence | Current record | Status and interpretation |
|---|---|---|
| Retained forecast export | `data/processed/forecasting/handoffs/final-20261003-02/issue-132-forecast-export-v1.json`; export schema `issue-132-forecast-export-v1`; SHA-256 `c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863` | The local file hash matches the hash in the received handoff manifest. The owner-reviewed hash entry and consumer acceptance remain pending in the forecast contract. This is prospective forecast evidence, not an inventory-risk result. |
| Forecast source | `source.run_id=final-20261003-02`; `source.evaluation_stage=final_evaluation`; `source.source_schema=issue-130-final-v1`; manifest SHA-256 `adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43`; prediction-receipt SHA-256 `853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692` | These are source-level provenance references. The derivative handoff does not include the full parent run archive, so package checksum verification must not be represented as an independent re-verification of the parent run. |
| Received handoff package | `research-materials/received/final-20261003-02/`; manifest records source repository commit `d9714bbffa3d52730991336b49e07b527e396cc7`, source run `final-20261003-02`, and package role “member-specific derivative subset” | The package says it is prepared for recipient review, not consumer acceptance. Its repository commit is the package/source context, not the current repository baseline. |
| Current reviewed repository baseline | `origin/main` at `12e30fc65fde367b320ea4f4b474a976ca09a3e8` when this proposal was prepared | Keep this separate from the package source commit above. The checked-in protocol and relevant documentation should be reviewed against the current main baseline. |
| Validated dataset bundle | `data/processed/validated/supply-chain-dataset1-validated-v1/` (`validated.parquet`, `schema.json`, `validation-audit.json`, `provenance.json`) | The handoff manifest records payload hashes; the accompanying schema/audit materials report passed shared validation/readback. The provenance record remains `pending_human_review`. Validation and matching hashes do not establish inventory snapshot timing, consumer acceptance, or completed inventory-risk analysis. |

The export contains 1,000 forecast rows at origin `2024-12-02`, with 250 SKU-warehouse rows for each horizon 1, 7, 14, and 28. Local checksum matching establishes byte identity against the received package manifest only. It does not accept the forecast handoff, approve DR-012, or establish an inventory-risk result. The source `Demand_Forecast` dataset column is not the project forecast in this export.

Generated analysis artifacts and full data remain outside Git under the [artifact storage policy](../artifact-storage-policy.md). The final inventory-risk run identifier and storage location are not established by this protocol and must be agreed before any authorized run; do not invent a path or write generated evidence into this document.

## 3. Forecast record selection

### Proposed candidate population

For later review, the candidate prospective population is the complete designated-producer roster in the retained export at its single fixed origin, `2024-12-02`:

| Horizon | Export records | Forecast meaning | Proposed downstream protocol status |
|---:|---:|---|---|
| 1 | 250 | Next-day demand for the inclusive target date `2024-12-03` | Candidate population, subject to the input and method reviews below. |
| 7 | 250 | Cumulative demand for `2024-12-03` through `2024-12-09`, inclusive | Candidate population, subject to the input and method reviews below. |
| 14 | 250 | Cumulative demand for `2024-12-03` through `2024-12-16`, inclusive | Candidate population, subject to the input and method reviews below. |
| 28 | 250 | Cumulative demand for `2024-12-03` through `2024-12-30`, inclusive | Retain forecast identity and provenance only. Downstream exposure and retrospective evaluation remain approval-gated and are not in the proposed evaluation population. |

This is a **candidate selection proposal**, not an approved selection or an evaluable-case count. It avoids selecting records based on observed crossings or results. The export itself is the record roster; preserve each row's `SKU_ID`, `Warehouse_ID`, `forecast_origin`, `horizon`, `target_start_date`, `target_end_date`, `model`, and `configuration_id`, together with export-level source provenance. The resulting inventory-eligible and paired-evaluable counts are unknown until reviewed input mapping, origin evidence, and later authorization are in place.

Do not pool horizons or relabel cumulative 7-, 14-, or 28-day totals as daily paths. Do not use h=28 for downstream inventory interpretation merely because its upstream forecast exists.

## 4. Forecast-to-inventory input contract proposal

The Issue #70 input format is an internal preparation format, not a final shared interchange contract. The table distinguishes source evidence from proposed mapping. “Unresolved” means no mapping or value may be fabricated to satisfy the internal function.

| Field | Current source/evidence | Proposed mapping status and handling | Review owner |
|---|---|---|---|
| `SKU_ID` | Present on each export forecast row and in the validated dataset. | Available directly; preserve exact string identity. | Chathuranga confirms forecast-side meaning; Didilani preserves the identity. |
| `Warehouse_ID` | Present on each export forecast row and in the validated dataset. | Available directly; preserve exact string identity. | Chathuranga confirms forecast-side meaning; Didilani preserves the identity. |
| `forecast_origin` | Present in each export row and at export level; value is `2024-12-02`. | Available for the forecast. It does not establish inventory snapshot availability. | Chathuranga. |
| `horizon` | Row-level integer 1, 7, 14, or 28. | Available upstream. Keep each horizon distinct; downstream h=28 is approval-gated. | Chathuranga for semantics; Didilani and human approval for downstream use. |
| `target_start_date` | Present per row; contract defines origin + 1. | Available; preserve and validate against the origin/horizon contract. | Chathuranga. |
| `target_end_date` | Present per row; contract defines origin + horizon. | Available; preserve and validate the inclusive window. | Chathuranga. |
| `prediction` | Project-generated `Units_Sold` forecast; row includes unit and `forecast_status`. | Available in the retained export, but exact-hash owner/consumer acceptance is pending. Preserve raw values and provenance. | Chathuranga; Tinosh for technical consumption. |
| `model` | Present per row. | Available; preserve the designated producer rather than changing selection. | Chathuranga. |
| `configuration_id` | Present per row. | Available; preserve the designated configuration. | Chathuranga. |
| `producer_status` | Present per row as `designated_producer`. | Available as producer status; it is not an `evidence_role` or eligibility mapping. | Chathuranga. |
| `forecast_status` | Present per row as `available` in the supplied export. | Available as the export's status. Mapping it to the internal `prediction_status` is unresolved and must not be assumed. | Chathuranga and Didilani. |
| `source.run_id` | Present at export level as `final-20261003-02`, not flattened to each row. | Source provenance is available; row-level propagation into internal records is unresolved and must be reviewed, not fabricated. | Chathuranga and Didilani. |
| `source.evaluation_stage` | Present at export level as `final_evaluation`, not flattened to each row. | Source provenance is available; row-level propagation is unresolved and must be reviewed, not fabricated. | Chathuranga and Didilani. |
| Source/schema/version/hash references | Export schema and source schema are present; source manifest/receipt hashes are in `source`; package manifest records the export hash and package source commit. | Preserve each reference at its actual scope. Which references are copied into each inventory record remains unresolved. Package verification is not consumer acceptance. | Chathuranga; Tinosh reviews technical representation. |
| `evidence_role` | Not present in the export. Forecasting artifacts document `primary`, `supportive`, and `simple_baseline` roles, but no reviewed mapping for these exported rows is supplied. | **Unresolved and absent. Do not invent a value or infer `primary` from `designated_producer`.** | Chathuranga. |
| `prediction_status` | The export has `forecast_status`, not this Issue #70 input field. | **Unresolved mapping. Do not silently equate it with `forecast_status`.** | Chathuranga and Didilani. |
| `eligibility_status` | Not present in the export. | **Unresolved and absent. Do not infer it from `forecast_status`, `producer_status`, or the source stage.** | Chathuranga and Didilani. |
| `Inventory_Level` | Present in the validated dataset at its native daily SKU-warehouse grain. | Field exists; use as an origin input only if availability at forecast issuance is evidenced. That evidence is unresolved. | Didilani; Chathuranga reviews forecast timing. |
| `Reorder_Point` | Present in the validated dataset at its native daily SKU-warehouse grain. | Field exists; use as the proposed fixed policy reference only if origin availability is evidenced. Timing and operational interpretation remain unresolved. | Didilani; group review for DR-012. |
| Inventory `Date` | Present as the dataset's daily record date. | Candidate snapshot date only. A date match does not prove origin-time availability or same-day ordering. | Didilani; Chathuranga reviews alignment. |
| `origin_snapshot_available` | Not supplied by the export or evidenced by a date match. Issue #70 requires explicit caller evidence and defaults a missing marker to unknown. | **Unresolved. Do not infer `true`; record unknown until an approved evidential basis exists.** | Didilani with source-owner review. |
| `Supplier_Lead_Time_Days` | Present in the dataset; DR-012 allows contextual use only when available at origin. | Origin availability unresolved. If later evidenced, use as context only; do not add a lead-time demand calculation. | Didilani. |
| `Order_Quantity` | Present in the dataset, but origin-time availability and order-event timing are not established. | **Unresolved availability. Context only if evidenced at origin; never treat as receipts, open orders, or optimal-order ground truth.** | Didilani. |
| Retrospective `Units_Sold` | Available in the validated source dataset after the forecast origin; not in the prospective export. | Retrospective target only for the exact complete target window. Pairing and completeness status must be explicit. | Didilani. |
| `target_status` | Not supplied by the prospective export. | **Unresolved until a reviewed retrospective completeness check supplies it. Do not fabricate `complete`.** | Didilani; Dewmi reviews downstream unavailable meaning. |
| Source `Demand_Forecast` | Dataset reference field; not the export's project `prediction`. | Do not map as a project forecast or substitute for missing project predictions. | All owners preserve this distinction. |
| `Stockout_Flag` | Dataset limitation; documented zero-variance. | Do not map as a target, label, or validation outcome. | All owners preserve this boundary. |

Any final field names, types, nesting, row-level provenance propagation, or status translation require owner review. This table is a proposal, not the final forecast-to-inventory schema.

## 5. Origin inventory snapshot gate

`Inventory_Level` and `Reorder_Point` are present in the validated daily dataset, but the available source documentation does not establish that their values were available at the moment the forecast was issued. The export's forecast origin is `2024-12-02`; a dataset row with the same `Date` is not proof of origin-time availability.

- Before-sales versus after-sales semantics for same-day inventory values are not established.
- Future `Inventory_Level` values cannot be treated as origin-known inputs.
- `origin_snapshot_available` must not be inferred as `true` from matching dates, row existence, or a file hash.
- If source timing cannot be established, retain the limitation and make dependent exposure/evaluation unavailable or not assessed with a reason.
- Any constructed scenario assumption about the snapshot is a separate proposal requiring human approval; it must not be reported as verified source timing.

The Issue #70 implementation follows this boundary: it does not join snapshots itself and requires explicit caller evidence before inventory values support exposure.

## 6. Problematic forecast handling proposal

The forecast contract preserves raw predictions without rounding, clipping, or flooring and regards malformed or non-finite source quantities as unusable. Inventory-layer handling remains open under B5. The following is a **proposal for review**, not an approved method:

| Input condition | Proposed record treatment for review |
|---|---|
| Negative finite prediction | Preserve the original prediction and provenance; do not reinterpret it as zero demand or silently repair it. Keep forecast-dependent inventory output unavailable with an explicit reason unless and until an owner-approved handling rule says otherwise. The current Issue #70 code uses `negative_forecast_handling_not_approved`; this is existing provisional behavior, not approval. |
| Missing prediction | Retain the forecast record identity and source context; mark the forecast-dependent output unavailable with a reason. Do not substitute source `Demand_Forecast`. |
| Malformed prediction | Do not coerce or rewrite the source value to make it usable. Record the validation failure and reason; do not silently delete the affected record. |
| Non-finite prediction | Treat the source quantity as unusable under the forecast contract; preserve provenance and the failure reason. Do not replace it with a finite value. |
| Invalid identity, horizon, dates, status, or duplicate forecast key | Treat as a schema/contract failure according to the relevant source and preparation checks. Do not silently repair, round, or drop rows. Retain the source artifact and report the failure explicitly. |

Chathuranga must review forecast meaning and source validity; Didilani must review the downstream disposition. No row/value repair rule is approved by this proposal.

## 7. Retrospective evaluation protocol

The following sequence is proposed for a later, separately authorized execution only:

1. **Freeze and cite inputs.** Identify the exact retained export and hash, dataset version and provenance, source run/stage, producer/configuration, code and protocol versions, and fixed forecast origin. Confirm owner/consumer acceptance before treating the export as an accepted handoff.
2. **Preserve case identity.** Keep `SKU_ID`, `Warehouse_ID`, `forecast_origin`, `horizon`, inclusive target dates, producer/configuration, and source provenance. Do not join on date alone or collapse horizons.
3. **Establish origin evidence.** Require reviewed evidence that the same SKU-warehouse `Inventory_Level` and `Reorder_Point` were available at forecast issuance. If availability or same-day semantics remain unknown, retain the case and reason as unknown/not assessed; do not score it as a crossing or no crossing.
4. **Separate origin-known states.** Under the proposed DR-012 method, report cases already at/below the origin reorder point separately from cases initially above it. The former are not evidence of forecast skill.
5. **Define the paired comparison population.** For each proposed eligible horizon, the primary comparison population is initially-above-threshold cases with the required origin snapshot, usable forecast, and complete retrospective target. Keep origin-known-at/below cases, forecast/target-unavailable cases, and other ineligible or gated cases visible with reasons and counts.
6. **Build retrospective targets only.** For each case, use realized `Units_Sold` for the exact inclusive interval `forecast_origin + 1` through `forecast_origin + horizon`. Require the complete interval for `target_status=complete`. Missing days, invalid values, or incomplete coverage make the target unavailable; they are not zero demand or no crossing.
7. **Keep evidence temporally separate.** Forecast predictions and origin snapshot evidence are prospective inputs. Realized `Units_Sold`, retrospective crossings, confusion cells, and metrics are evaluation-only; they must not enter prospective views or human-review triggers.
8. **Report traceably.** Retain the selected record identities, source/version references, per-horizon population counts, origin-known and unavailable counts, denominators, assumptions, limitations, method status, and reasons. Do not claim actual stockout accuracy, operational performance, optimal ordering, or causal benefit.

The proposed record roster is the complete export roster described in Section 3, not a result-selected sample. Its count is not an evaluable denominator. The number of records with verified origin snapshots and complete paired targets is currently unknown. No record-level evaluation is performed in this document.

For clarity, the proposed DR-012 method defines `I_t` as origin `Inventory_Level`, `R_t` as origin `Reorder_Point`, and `B_t = I_t - R_t`. `B_t <= 0` is already at/below the origin threshold; `B_t > 0` is initially above it. For initially-above cases, forecast crossing is `F_t,h >= B_t`; retrospective proxy crossing is `Y_t,h >= B_t`, with equality counted as crossing. This is the existing proposed fixed-origin, no-receipt scenario, not an approved operational inventory method or stockout label. It is usable only if origin snapshot availability is established and downstream method use is reviewed.

## 8. DR-012 metrics

Use only the existing definitions in DR-012 §6. They describe agreement with a retrospective threshold-crossing proxy, not actual stockout evidence. For initially-above-threshold cases with paired forecast and complete retrospective evidence:

| Quantity | Existing meaning or definition |
|---|---|
| TP | Forecast crossing and retrospective proxy crossing. |
| TN | No forecast crossing and no retrospective proxy crossing. |
| FN | No forecast crossing but retrospective proxy crossing (missed crossing). |
| FP | Forecast crossing but no retrospective proxy crossing (false alert). |
| `N` | `TP + TN + FN + FP` for the evaluable paired cases in the reported group. |
| Event prevalence | `(TP + FN) / N`. |
| Missed-crossing rate | `FN / (TP + FN)`. |
| False-alert rate | `FP / (FP + TN)`. |
| Agreement | `(TP + TN) / N`. |
| Precision | `TP / (TP + FP)`. |
| Recall | `TP / (TP + FN)`. |
| Balanced accuracy | `0.5 * [TP / (TP + FN) + TN / (TN + FP)]`. |

Report counts and denominators explicitly, plus separately reported origin-known and unavailable cases. If a metric denominator is zero, report the metric as unavailable, not zero. Balanced accuracy is unavailable if either class-specific rate is undefined. Do not artificially rebalance the historical population or add a pooled score, new subgroup method, statistical test, sensitivity threshold, or metric.

## 9. Horizon rules

- Keep h=1 next-day demand, h=7 cumulative demand, and h=14 cumulative demand separate.
- The 7- and 14-day predictions are single cumulative quantities over their complete target windows, not daily paths.
- Retain h=28 forecast identity and its cumulative meaning as upstream evidence only. **Do not calculate or report h=28 downstream exposure, retrospective crossing, margin, or evaluation unless separate component-owner/human approval is documented.**
- Do not interpret 28 days as supplier lead time, round lead time to a horizon, interpolate a daily path, or combine horizons into a score.

## 10. Unknown, unavailable, approval-gated, and not-assessed states

These terms are not interchangeable:

| State | Meaning in this proposal |
|---|---|
| Unknown | Evidence does not establish whether the source value was available or valid at the relevant time; for example, origin snapshot timing without an availability marker. |
| Unavailable | A required value or output cannot be supplied, with the reason retained. |
| Approval-gated / not approved for downstream use | Evidence may exist, but a downstream interpretation is not authorized; h=28 is the current example. |
| Not assessed | The assessment has not been performed. It is not clearance, no-crossing, or a negative result. |

DR-011 identifies the reason concepts “no agreed method,” “not applicable,” and “waiting on another component.” B9 states that a concrete mapping from producer statuses/reasons to those concepts is unresolved. The internal Issue #70 reasons do not establish a final shared or Dewmi-facing encoding. Preserve source reasons; do not convert missing evidence into zero, `false`, no crossing, or a negative finding. Do not silently exclude a selected, reviewable downstream record merely because inventory or replenishment evidence is unavailable.

## 11. Handoff requirements

### Chathuranga — forecasting meaning and inputs

Review the exact export and source references; forecast origin, horizon and inclusive target dates; producer/model/configuration fields; source-level `run_id` and `evaluation_stage` propagation; the missing `evidence_role` definition; meanings of `forecast_status`, `prediction_status`, and `eligibility_status`; problematic forecast handling; and the owner/consumer acceptance status. No model selection or forecast recomputation is in scope.

### Dewmi — downstream meaning and unavailable information

Review how inventory evidence, method status, provenance, assumptions, limitations and unavailable reasons should travel into responsible decision support, including the mapping to DR-011’s reason concepts. This document does not select Issue #153’s decision-support records or perform Dewmi’s transparency assessment. It defines no human-review trigger.

### Tinosh — technical clarity and implementability

Review whether the proposed identities, source scopes, horizon distinctions, statuses, provenance and unavailable behavior are technically clear. This handoff does not establish the final interchange schema and does not authorize adapters, runtime integration, charts, or prototype rendering.

## 12. Decision and dependency register

The statuses below describe the current documented evidence and proposed owner actions. A document merge alone does not resolve a blocker.

| Blocker | Proposal/status | Evidence | Required reviewer/owner | Remaining action |
|---|---|---|---|---|
| B3 — origin snapshot timing | Unresolved; no verified availability or before/after-sales semantics. | Dataset has daily `Date`, `Inventory_Level`, and `Reorder_Point`; matching dates are not an availability proof. | Didilani; Chathuranga reviews forecast timing; relevant source owner if identifiable. | Obtain evidential source timing or retain unknown/unavailable status. Do not infer `origin_snapshot_available=true`. |
| B4 — DR-012 approval | DR-012 remains Proposed for group approval. | Current decision record states Proposed; no later approval is recorded here. | Didilani presents; group review. | Record actual approval, requested revisions, or unresolved status. Do not change the status based on this protocol. |
| B5 — problematic forecast handling | Unresolved; no clipping or repair is approved. The Issue #70 negative-forecast state is provisional behavior. | Forecast contract preserves raw predictions; source malformed/non-finite quantities are unusable; inventory handling is separate. | Chathuranga and Didilani. | Review an explicit retained-value/unavailable proposal and document the agreed disposition before mapping. |
| B6 — forecast-to-inventory schema | Unresolved; Issue #70 format is internal. | Export field scopes/statuses do not directly match every Issue #70 input; `evidence_role` is missing. | Chathuranga and Didilani; Tinosh reviews technical clarity. | Agree reviewed names, types, source scopes, provenance propagation, and status mapping. |
| B7 — inventory-to-decision-support schema | Unresolved; DR-011 is structure-only and DR-012 does not lock fields/types. | Readiness map and DR-012 retain final handoff schema as open. | Didilani and Dewmi; Tinosh reviews technical clarity. | Agree the reviewed handoff meaning and encoding; keep unsupported values explicitly unavailable. |
| B12 — replenishment quantity / overstock | Provisional/unavailable absent a separately justified approved method. | DR-012 does not approve a numeric replenishment quantity or overstock rule. | Didilani and group/human review where required. | Keep unavailable unless a separate method is researched and approved. |
| B13 — `Order_Quantity` availability | Unresolved at forecast origin. | Dataset records a quantity but does not establish timing as available, received, or outstanding stock. | Didilani. | Establish origin availability before using as context; never infer receipts or optimal orders. |
| B8 — 28-day downstream use | Not approved; approval-gated. | Upstream h=28 exists, but DR-012 and DR-011 require separate downstream approval. | Didilani and Dewmi, with human approval. | Retain identity only until explicit downstream approval; no h=28 exposure/evaluation meanwhile. |
| B9 — unavailable-state mapping | Unresolved. | Forecast contract reason codes are not mapped to DR-011’s three reason concepts; readiness assigns semantic ownership to Dewmi with producing owners. | Dewmi with each producing owner. | Agree meaning and encoding while preserving original source reason; do not invent a mapping. |
| B10 — human-review rules | Unresolved and owned by responsible decision support. | DR-011 approves structure only; no triggers or thresholds. | Dewmi. | Keep `not_assessed` where unassessed; do not add rules here. |
| B11 — uncertainty method | Unresolved; current export states unavailable with `no_agreed_method`. | Forecast contract and readiness map do not approve an uncertainty estimate. | Chathuranga; Dewmi reviews downstream presentation. | Preserve unavailable status/reason unless a separate method is approved. |

When reviews occur, update the relevant readiness entries with the proposal, evidence, reviewer, actual review status, and remaining owner action. Do not mark a blocker resolved merely because this protocol or another document is merged. Any change to DR-012 must reflect actual human-reviewed decisions only.

**Referenced-issue status-text discrepancy:** Issue #101's background describes #85 and #145 as active. The current issue records show #85 closed through PR #160 and #145 closed; Issue #153 says #145 is closed and tracks the remaining decision-support assessment. Issue #101 itself remains open for its acceptance-scenario scope. This protocol uses those current statuses for dependency context and does not alter or reinterpret Issue #101's acceptance requirements.

## 13. Execution gate

This protocol does **not** authorize:

- dataset-backed preparation or inventory-risk evaluation;
- model training, tuning, inference, experiments, or final-holdout execution;
- generating inventory-risk results, metrics, or charts;
- final schema approval or forecast consumer acceptance;
- runtime adapters, FastAPI, or prototype implementation;
- replenishment formulas or quantities, overstock rules, or risk thresholds;
- an uncertainty method or human-review trigger;
- 28-day downstream inventory use.

The project owner runs approved research commands manually under AGENTS.md. Any later execution needs specific authorization after the methodology, field mapping, protocol, and execution-critical approvals are reviewed. Forecasts in the retained export must not be retrained, re-inferred, or recomputed for this work.

## 14. Review checklist

### Chathuranga

- [ ] Confirm forecast origin, horizon and inclusive target-window interpretation.
- [ ] Confirm the accepted export hash and consumer handoff status; distinguish checksum integrity from acceptance.
- [ ] Review row-level versus export-level provenance mapping.
- [ ] Define or explicitly leave unresolved `evidence_role`; do not infer it from `producer_status`.
- [ ] Review meanings and mapping of forecast, prediction, eligibility, and target statuses.
- [ ] Review the proposed handling of negative, missing, malformed, non-finite, and invalid forecast records.

### Dewmi

- [ ] Review inventory-to-decision-support meaning and the proposed unavailable-state distinctions/mapping.
- [ ] Confirm missing inventory/replenishment evidence remains explicit and does not automatically exclude a selected record.
- [ ] Confirm this protocol does not perform Issue #153's record selection or transparency assessment and does not introduce human-review triggers.

### Tinosh

- [ ] Review the technical clarity of identities, source scopes, horizon fields, provenance and status mapping.
- [ ] Confirm unavailable/unknown/approval-gated cases are distinguishable for later integration without treating this as a final schema.
- [ ] Confirm adapters, charts and prototype rendering remain outside Issue #162.

### Group / project review

- [ ] Record DR-012 approval, requested revisions, or unresolved status accurately.
- [ ] Keep any h=28 downstream decision separate from upstream forecast availability.
- [ ] Confirm the protocol remains a proposal and that execution has not been authorized by its review alone.

## References

- [Issue #162 — Research: resolve inventory-risk input contracts and prepare the evaluation protocol](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/162)
- [Issue #153 — decision-support transparency assessment](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/153); coordination only, with Dewmi retaining its assessment.
- [Issue #101 — integration acceptance scenarios](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/101); Tinosh owns technical scenario work.
- [DR-012 — Inventory-Risk and Replenishment Methodology](../decisions/DR-012-inventory-risk-replenishment-methodology.md)
- [Inventory-Risk Visual Evidence Specification](inventory-risk-visual-evidence.md)
- [Forecast API Contract](../forecast-api-contract.md)
- [Integration Contract Readiness](../integration-contract-readiness.md)
- [Inventory-Risk Analysis Workflow](../workflows/inventory-risk-analysis.md)
- [Dataset documentation](../dataset.md)
- [Artifact and Storage Policy](../artifact-storage-policy.md)
