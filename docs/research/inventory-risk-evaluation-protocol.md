# Inventory-Risk Evaluation Protocol

> **Status — 23 October 2026, Issue #177:** Mapping, evaluation utilities and human-run constructed-scenario evidence are available. Chathuranga executed the 1/7/14-day evaluation; Section 12.3 retains its provenance. DR-012 group approval is now recorded separately; source timing, consumer acceptance and final prototype acceptance remain distinct.
>
> This document records the implemented protocol, retained run and remaining consumer/input decisions. It does not itself grant a new research execution or settle the final interchange schema.

The original decision work was tracked under [Issue #164](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/164). Sections [4.1](#41-implemented-forecast-to-inventory-mapping) and [6.1](#61-implemented-validation-and-error-behaviour) document the executable forecasting-side B5/B6 mapping and error handling. Section 12.1 gives the human-run preparation command; Section 12.2 gives the evaluation command implemented at Chathuranga's request in the working conversation on 23 October 2026.

**Issue closeout scope — 23 October 2026:** PR #175 merged and closed #164/#168 for the delivered implementation/evidence milestone. Closure did not approve the methodology or finish prototype acceptance. The group approval reported by Chathuranga for the 12 October WhatsApp discussion is now recorded in [DR-012](../decisions/DR-012-inventory-risk-replenishment-methodology.md#group-approval-record) under #177. Historical run metadata stays unchanged. Remaining member work is scoped from the refined readiness baseline.

**Delivery acceptance reconciliation — 9 November 2026:** The retained source/consumer and presentation decisions are recorded in the [current handoff record](../integration-contract-readiness.md#12-current-delivery-and-acceptance--9-november-2026). Earlier package/provenance statements below retain their original scope and are not current pending tasks. No evidence bytes, evaluation method or execution permission are changed.

## Current scope reconciliation — 5 November 2026

The team-accepted [C1 scope/closeout record](../research-design.md#164-human-decisions-and-c1-closeout-record) resolves B8/B10/B11/B12 for current delivery through approved deferral: h28 inventory use, automatic human-review rules, prospective uncertainty, numerical replenishment and overstock remain disclosed limitations/deferred extensions. They are not unresolved requirements to implement before repository completion. Their outputs remain unavailable under the existing source reasons and gates. Source timing, exact retained-export acceptance and actual component/interface reviews remain separate; no new method, approval or research run is created by this reconciliation.

## 1. Purpose and status

This protocol documents the implemented forecast-to-inventory mapping and constructed-scenario evaluation under [DR-012](../decisions/DR-012-inventory-risk-replenishment-methodology.md#group-approval-record). The method has the reported group approval for 1/7/14-day analysis. Synthetic tests verify software behaviour; the retained human-run results in Section 12.3 supply the separate scenario evidence. Neither establishes actual stockout accuracy or final consumer acceptance.

The runner implements the existing DR-012 calculations and exact-window completeness rules, with an explicit snapshot-policy choice. Synthetic tests exercise the code; they are not project research results. A dataset-backed run remains a human action under AGENTS §17, and its selected snapshot basis must be reported accurately.

## 2. Source artifacts and provenance

| Evidence | Current record | Status and interpretation |
|---|---|---|
| Retained forecast export | `data/processed/forecasting/handoffs/final-20261003-02/issue-132-forecast-export-v1.json`; export schema `issue-132-forecast-export-v1`; SHA-256 `c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863` | The local file hash matches the hash in the received handoff manifest. That received-package checkpoint recorded export-hash review and consumer acceptance as pending; subsequent producer/source and reported consumer acceptance are linked in the 9 November handoff record above. This is prospective forecast evidence, not an inventory-risk result. |
| Forecast source | `source.run_id=final-20261003-02`; `source.evaluation_stage=final_evaluation`; `source.source_schema=issue-130-final-v1`; manifest SHA-256 `adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43`; prediction-receipt SHA-256 `853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692` | These are source-level provenance references. The derivative handoff does not include the full parent run archive, so package checksum verification must not be represented as an independent re-verification of the parent run. |
| Received handoff package | `research-materials/received/final-20261003-02/`; manifest records source repository commit `d9714bbffa3d52730991336b49e07b527e396cc7`, source run `final-20261003-02`, and package role “member-specific derivative subset” | The package says it is prepared for recipient review, not consumer acceptance. Its repository commit is the package/source context, not the current repository baseline. |
| Historical repository baseline at proposal preparation | `origin/main` at `12e30fc65fde367b320ea4f4b474a976ca09a3e8` when this proposal was prepared | Keep this separate from the package source commit above. The checked-in protocol and relevant documentation should be reviewed against the current main baseline. |
| Validated dataset bundle | `data/processed/validated/supply-chain-dataset1-validated-v1/` (`validated.parquet`, `schema.json`, `validation-audit.json`, `provenance.json`) | The handoff manifest records payload hashes; the accompanying schema/audit materials report passed shared validation/readback. The provenance record remains `pending_human_review`. Validation and matching hashes do not establish inventory snapshot timing, consumer acceptance, or completed inventory-risk analysis. |

The export contains 1,000 forecast rows at origin `2024-12-02`, with 250 SKU-warehouse rows for each horizon 1, 7, 14, and 28. Local checksum matching establishes byte identity against the received package manifest only. It does not accept the forecast handoff, approve DR-012, or establish an inventory-risk result. The source `Demand_Forecast` dataset column is not the project forecast in this export.

Generated analysis artifacts and full data remain local under the [storage policy](../artifact-storage-policy.md). The named unchanged review bundles are published under reports/. Section 12.2 defines exclusive output paths for any separately authorised human run; Section 12.3 identifies the run already performed.

## 3. Forecast record selection

### Retained forecast population

The retained prospective population is the complete designated-producer roster in the exact export at its single fixed origin, `2024-12-02`:

| Horizon | Export records | Forecast meaning | Downstream scope |
|---:|---:|---|---|
| 1 | 250 | Next-day demand for the inclusive target date `2024-12-03` | Included in the retained constructed-origin evaluation; consumer acceptance remains separate. |
| 7 | 250 | Cumulative demand for `2024-12-03` through `2024-12-09`, inclusive | Included in the retained constructed-origin evaluation; consumer acceptance remains separate. |
| 14 | 250 | Cumulative demand for `2024-12-03` through `2024-12-16`, inclusive | Included in the retained constructed-origin evaluation; consumer acceptance remains separate. |
| 28 | 250 | Cumulative demand for `2024-12-03` through `2024-12-30`, inclusive | Retain forecast identity and provenance only. Downstream exposure and retrospective evaluation remain approval-gated and are not in the retained inventory evaluation population. |

The export is the complete roster, selected without using observed crossings. Preserve its exact keys, target intervals, producer/configuration and source provenance. The retained run evaluated 750 h=1/7/14 candidates, with 239 paired and 11 separate scenario-at/below cases per horizon. These are conditional constructed-scenario counts, not proof of verified source snapshots; h=28 remains outside inventory evaluation.

Do not pool horizons or relabel cumulative 7-, 14-, or 28-day totals as daily paths. Do not use h=28 for downstream inventory interpretation merely because its upstream forecast exists.

## 4. Forecast-to-inventory input contract

The Issue #70 input format is an internal preparation format. Section 4.1 implements the retained-export mapping into that format; the table keeps source availability, snapshot timing and retrospective inputs distinct. Unknown source information is not fabricated to satisfy a function.

| Field | Current source/evidence | Proposed mapping status and handling | Review owner |
|---|---|---|---|
| `SKU_ID` | Present on each export forecast row and in the validated dataset. | Available directly; preserve exact string identity. | Chathuranga confirms forecast-side meaning; Didilani preserves the identity. |
| `Warehouse_ID` | Present on each export forecast row and in the validated dataset. | Available directly; preserve exact string identity. | Chathuranga confirms forecast-side meaning; Didilani preserves the identity. |
| `forecast_origin` | Present in each export row and at export level; value is `2024-12-02`. | Available for the forecast. It does not establish inventory snapshot availability. | Chathuranga. |
| `horizon` | Row-level integer 1, 7, 14, or 28. | Available upstream. Keep each horizon distinct; downstream h=28 is approval-gated. | Chathuranga for semantics; Didilani and human approval for downstream use. |
| `target_start_date` | Present per row; contract defines origin + 1. | Available; preserve and validate against the origin/horizon contract. | Chathuranga. |
| `target_end_date` | Present per row; contract defines origin + horizon. | Available; preserve and validate the inclusive window. | Chathuranga. |
| `prediction` | Project-generated `Units_Sold` forecast; row includes unit and `forecast_status`. | Available in the retained export, but exact-hash Chathuranga/consumer acceptance is pending. Preserve raw values and provenance. | Chathuranga; Tinosh for technical consumption. |
| `model` | Present per row. | Available; preserve the designated producer rather than changing selection. | Chathuranga. |
| `configuration_id` | Present per row. | Available; preserve the designated configuration. | Chathuranga. |
| `producer_status` | Present per row as `designated_producer`. | Available as producer status; it is not an `evidence_role` or eligibility mapping. | Chathuranga. |
| `forecast_status` | Present per row as `available` in the supplied export. | Mapped explicitly to internal `prediction_status`; see Section 4.1. | Chathuranga and Didilani. |
| `source.run_id` | Present at export level as `final-20261003-02`, not flattened to each row. | Copied from the containing export into internal rows, with its original source scope retained; see Section 4.1. | Chathuranga and Didilani. |
| `source.evaluation_stage` | Present at export level as `final_evaluation`, not flattened to each row. | Copied from the containing export into internal rows, retaining the original export-level scope; see Section 4.1. | Chathuranga and Didilani. |
| Source/schema/version/hash references | Export schema and source schema are present; source manifest/receipt hashes are in `source`; package manifest records the export hash and package source commit. | Retain source references in `source_provenance` and explicit export hash/schema columns. Package verification remains distinct from consumer acceptance. | Chathuranga; Tinosh reviews technical representation. |
| `evidence_role` | Not present in the export. The exporter checks primary role on the exact designated parent candidates and prediction rows before omitting the role from exported records. | Derived as `primary` for the exact hash-bound source only, using the exporter's parent-role checks; see Section 4.1. | Chathuranga. |
| `prediction_status` | The export has `forecast_status`, not this Issue #70 input field. | Explicit translation of a validated source `forecast_status=available`; see Section 4.1. | Chathuranga and Didilani. |
| `eligibility_status` | Not present in the export. | Internal source-forecast usability flag defined in Section 4.1, independent of inventory availability and retrospective targets. | Chathuranga and Didilani. |
| `Inventory_Level` | Present in the validated dataset at its native daily SKU-warehouse grain. | Field exists; use as an origin input only if availability at forecast issuance is evidenced. That evidence is unresolved. | Didilani; Chathuranga reviews forecast timing. |
| `Reorder_Point` | Present in the validated dataset at its native daily SKU-warehouse grain. | Field exists; use as the proposed fixed policy reference only if origin availability is evidenced. Timing and operational interpretation remain unresolved. | Didilani; source timing and consumer review remain separate from the recorded method approval. |
| Inventory `Date` | Present as the dataset's daily record date. | Candidate snapshot date only. A date match does not prove origin-time availability or same-day ordering. | Didilani; Chathuranga reviews alignment. |
| `origin_snapshot_available` | Not supplied by the export or evidenced by a date match. Issue #70 requires explicit caller evidence and defaults a missing marker to unknown. | **Unresolved. Do not infer `true`; record unknown until an approved evidential basis exists.** | Didilani with source-owner review. |
| `Supplier_Lead_Time_Days` | Present in the dataset; DR-012 allows contextual use only when available at origin. | Origin availability unresolved. If later evidenced, use as context only; do not add a lead-time demand calculation. | Didilani. |
| `Order_Quantity` | Present in the dataset, but origin-time availability and order-event timing are not established. | **Unresolved availability. Context only if evidenced at origin; never treat as receipts, open orders, or optimal-order ground truth.** | Didilani. |
| Retrospective `Units_Sold` | Available in the validated source dataset after the forecast origin; not in the prospective export. | Retrospective target only for the exact complete target window. Pairing and completeness status must be explicit. | Didilani. |
| `target_status` | Not supplied by the prospective export. | **Unresolved until a reviewed retrospective completeness check supplies it. Do not fabricate `complete`.** | Didilani; Dewmi reviews downstream unavailable meaning. |
| Source `Demand_Forecast` | Dataset reference field; not the export's project `prediction`. | Do not map as a project forecast or substitute for missing project predictions. | All owners preserve this distinction. |
| `Stockout_Flag` | Dataset limitation; documented zero-variance. | Do not map as a target, label, or validation outcome. | All owners preserve this boundary. |

Any final field names, types, nesting, row-level provenance propagation, or status translation require review by the relevant producing and consuming component members. This table is a proposal, not the final forecast-to-inventory schema.

### 4.1 Implemented forecast-to-inventory mapping

The implementation is [forecast_handoff.py](../../src/inventory_risk/forecast_handoff.py), contract version `issue-164-168-v1`. It validates the exact hash-bound retained export before producing internal preparation inputs. It does not read model binaries, calculate forecasts or decode future sales.

| Source | Internal mapping / validation |
|---|---|
| Forecast identity, origin, horizon, target dates, prediction, unit and producer/configuration | Preserve source values; require the frozen producer mapping, complete 250-series grid across all four horizons, exact inclusive windows and finite JSON numbers. Reject booleans, numeric strings, duplicates, partial populations and retrospective fields. |
| `forecast_status=available` | Copy to `prediction_status=available` and retain the original status. This means forecast availability, not known inventory or permission for downstream interpretation. |
| Export-level `source.run_id` / `source.evaluation_stage` | Copy exact values into internal rows. Retain `source_provenance` as the original source object encoded as JSON text, plus `source_export_sha256` and `source_export_schema`. |
| Missing `evidence_role` | Set `primary` only within this hash-bound export contract: its producer code checks primary role on both parent candidates and designated prediction rows before export. This is not a general inference from `designated_producer`. |
| Missing `eligibility_status` | Define this internal flag as source-forecast usability: `eligible` for a validated finite nonnegative forecast, `ineligible` for a finite negative forecast. It does not establish snapshot availability, retrospective completeness or downstream horizon/method approval. |
| Origin inventory fields | Join on exact SKU, warehouse and origin date, with a many-to-one snapshot check. Required fields missing after a join remain unavailable. A date match does not set an availability marker. |
| `origin_snapshot_available` | Preserve an explicitly supplied marker. Default to unknown; never borrow future inventory or assume timing from matching dates. The human-run CLI can record a confirmed availability assertion only with a nonblank, nondefault source-timing basis. |
| Retrospective targets | Never read or generate `observed_target` or `target_status` in this preparation. They remain separately scoped retrospective inputs. |

The function reuses `prepare_inventory_risk_inputs`, including its existing method and 28-day gates and unavailable reasons. It does not redefine those calculations. The executable mapping and synthetic tests replace the earlier field-translation placeholders; no new approval log is required to run the software's synthetic tests.

## 5. Origin inventory snapshot gate

`Inventory_Level` and `Reorder_Point` are present in the validated daily dataset, but the available source documentation does not establish that their values were available at the moment the forecast was issued. The export's forecast origin is `2024-12-02`; a dataset row with the same `Date` is not proof of origin-time availability.

- Before-sales versus after-sales semantics for same-day inventory values are not established.
- Future `Inventory_Level` values cannot be treated as origin-known inputs.
- `origin_snapshot_available` must not be inferred as `true` from matching dates, row existence, or a file hash.
- If source timing cannot be established, retain the limitation and make **source-based** exposure/evaluation unavailable with a reason. A separately selected constructed scenario may evaluate hypothetical starting balances while preserving the unknown/unavailable source status.
- A constructed scenario assumption must be explicitly reviewed/selected for the particular human run; a documented option or passing test does not itself approve a research decision. It must not be reported as verified source timing.

The Issue #70 `input_preparation.py` validates already paired rows and does not join snapshots. `forecast_handoff.py` supplies the exact-origin join; missing origin rows are explicitly unavailable with reason `origin_inventory_record_missing`. A matched row with unconfirmed timing remains unknown. The evaluation function's default source-based path requires an available source snapshot; its explicit constructed path uses conditional scenario availability instead.

## 6. Problematic forecast handling and review

The forecast contract preserves raw predictions without rounding, clipping, or flooring and regards malformed or non-finite source quantities as unusable. The implementation follows the dispositions below and the exact validation behaviour in Section 6.1. Implementation availability does not itself resolve the relevant human review of B5 or approve a row/value repair rule.

| Input condition | Contract disposition / review boundary |
|---|---|
| Negative finite prediction | Preserve the original prediction and provenance; do not reinterpret it as zero demand or silently repair it. Keep forecast-dependent inventory output unavailable with an explicit reason unless and until a handling rule approved by Didilani, after Chathuranga's review of forecast meaning, says otherwise. The current Issue #70 code uses `negative_forecast_handling_not_approved`; this is existing provisional behavior, not approval. |
| Missing prediction | Retain the forecast record identity and source context; mark the forecast-dependent output unavailable with a reason. Do not substitute source `Demand_Forecast`. |
| Malformed prediction | Do not coerce or rewrite the source value to make it usable. Record the validation failure and reason; do not silently delete the affected record. |
| Non-finite prediction | Treat the source quantity as unusable under the forecast contract; preserve provenance and the failure reason. Do not replace it with a finite value. |
| Invalid identity, horizon, dates, status, or duplicate forecast key | Treat as a schema/contract failure according to the relevant source and preparation checks. Do not silently repair, round, or drop rows. Retain the source artifact and report the failure explicitly. |

Chathuranga must review forecast meaning and source validity; Didilani must review the downstream disposition. No row/value repair rule is approved by this proposal.

### 6.1 Implemented validation and error behaviour

- A hash, source identity, schema, producer, interval, quantity or population mismatch raises a validation error before preparation; no partial export is accepted.
- Missing required preparation columns, invalid identity/provenance and duplicate snapshot keys fail explicitly.
- Finite negative forecasts retain their raw value and provenance, are ineligible for inventory exposure, and carry the existing unavailable reason. Zero remains valid zero demand.
- Missing inventory and unknown snapshot timing retain all forecast rows with explicit unavailable reasons. Lead time and order quantity remain context-only and unknown unless their own availability is explicitly established.
- The source artifact is never repaired, overwritten, re-inferred or silently filtered. Generated JSON uses normal numeric serialization so raw forecast precision is retained.

## 7. Retrospective evaluation protocol

The implemented sequence below also governs any later, separately authorised human execution. The completed run is recorded in Section 12.3:

1. **Freeze and cite inputs.** Identify the exact retained export and hash, dataset version and provenance, source run/stage, producer/configuration, code and protocol versions, and fixed forecast origin. Confirm Chathuranga/consumer acceptance before treating the export as an accepted handoff.
2. **Preserve case identity.** Keep `SKU_ID`, `Warehouse_ID`, `forecast_origin`, `horizon`, inclusive target dates, producer/configuration, and source provenance. Do not join on date alone or collapse horizons.
3. **Establish the snapshot basis.** For source-based evaluation, require reviewed evidence that the same SKU-warehouse `Inventory_Level` and `Reorder_Point` were available at issuance. Unknown timing blocks that source-based result. An explicitly selected constructed-origin run instead uses the stated hypothetical starting-balance assumption, preserves source unavailability and labels its separate scenario states/counts. Neither path borrows future inventory.
4. **Separate origin-known/scenario states.** Under the DR-012 method, report cases already at/below the origin reorder point separately from cases initially above it. Preserve the distinction between source-known and hypothetical scenario origin states; neither at/below group establishes forecast skill.
5. **Define the paired comparison population.** For each proposed eligible horizon, the primary comparison population is initially-above-threshold cases with the required origin snapshot, usable forecast, and complete retrospective target. Keep origin-known-at/below cases, forecast/target-unavailable cases, and other ineligible or gated cases visible with reasons and counts.
6. **Build retrospective targets only.** For each case, use realized `Units_Sold` for the exact inclusive interval `forecast_origin + 1` through `forecast_origin + horizon`. Require the complete interval for `target_status=complete`. Missing days, invalid values, or incomplete coverage make the target unavailable; they are not zero demand or no crossing.
7. **Keep evidence temporally separate.** Forecast predictions and origin snapshot evidence are prospective inputs. Realized `Units_Sold`, retrospective crossings, confusion cells, and metrics are evaluation-only; they must not enter prospective views or human-review triggers.
8. **Report traceably.** Retain the selected record identities, source/version references, per-horizon population counts, origin-known and unavailable counts, denominators, assumptions, limitations, method status, and reasons. Disclose that December 3–16 had prior validation exposure and that full-year exploratory analysis inspected the final interval. Results must not be described as evaluation on a historically fully unseen period. Do not claim actual stockout accuracy, operational performance, optimal ordering, or causal benefit.

The roster is the complete export described in Section 3, not a result-selected sample. Its count is not an evaluable denominator. The retained constructed scenario supplies the per-horizon denominators in Section 12.3; verified source origin availability remains unresolved.

For clarity, the DR-012 method defines `I_t` as origin `Inventory_Level`, `R_t` as origin `Reorder_Point`, and `B_t = I_t - R_t`. `B_t <= 0` is already at/below the origin threshold; `B_t > 0` is initially above it. For initially-above cases, forecast crossing is `F_t,h >= B_t`; retrospective proxy crossing is `Y_t,h >= B_t`, with equality counted as crossing. This is the group-approved fixed-origin/no-receipt scenario method, not a verified operational inventory model or stockout label. Source-based use requires timing evidence; constructed-origin use retains explicitly hypothetical balances and unknown source availability.

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

Review the exact export and source references; forecast origin, horizon and inclusive target dates; producer/model/configuration fields; source-level `run_id` and `evaluation_stage` propagation; the missing `evidence_role` definition; meanings of `forecast_status`, `prediction_status`, and `eligibility_status`; problematic forecast handling; and Chathuranga's and the consumer's acceptance status. No model selection or forecast recomputation is in scope.

### Dewmi — downstream meaning and unavailable information

Review how inventory evidence, method status, provenance, assumptions, limitations and unavailable reasons should travel into responsible decision support, including the mapping to DR-011’s reason concepts. This document does not select Issue #153’s decision-support records or perform Dewmi’s transparency assessment. It defines no human-review trigger.

### Tinosh — technical clarity and implementability

Review whether the proposed identities, source scopes, horizon distinctions, statuses, provenance and unavailable behavior are technically clear. This handoff does not establish the final interchange schema and does not authorize adapters, runtime integration, charts, or prototype rendering.

## 12. Decision and dependency register

The statuses below describe the current documented evidence and proposed actions by the responsible members. A document merge alone does not resolve a blocker.

| Blocker | Proposal/status | Evidence | Required reviewer/owner | Remaining action |
|---|---|---|---|---|
| B3 — origin snapshot timing | Unresolved; no verified availability or before/after-sales semantics. | Dataset has daily `Date`, `Inventory_Level`, and `Reorder_Point`; matching dates are not an availability proof. | Didilani; Chathuranga reviews forecast timing; relevant source owner if identifiable. | Obtain evidential source timing or retain unknown/unavailable status. Do not infer `origin_snapshot_available=true`. |
| B4 — DR-012 approval | Recorded group approval for the 1/7/14-day fixed-origin/no-receipt method. | Chathuranga reported the 12 October WhatsApp group decision on 23 October under #177; see the DR-012 approval record. | Group decision; reporting attribution: Chathuranga. | No repeat approval request for the same scope. Source timing, final consumer acceptance and additional methods remain separate. |
| B5 — problematic forecast handling | Implemented: invalid exports fail explicitly; finite negatives retain their value and are unavailable for inventory exposure. | Sections 4.1/6.1 and synthetic boundary tests. | Chathuranga and Didilani; Tinosh for representation. | Review the implementation and retain original diagnostics; no clipping or repair occurs. |
| B6 — forecast-to-inventory mapping | Implemented for the exact retained export and existing internal preparation format. | Section 4.1 defines status, role, eligibility, provenance and exact-origin alignment; the CLI writes an exclusive derivative. | Chathuranga and Didilani; Tinosh reviews technical clarity. | Inspect the retained preparation and actual source/consumer evidence; software mapping does not establish snapshot timing or close other scientific gates. |
| B7 — inventory-to-decision-support schema | Concrete internal prospective handoff and record adapter implemented; final API/presentation acceptance remains separate. | Section 12.2 and the decision-support preparation define hash-bound identity, exposure, source availability, scenario assumptions and original reasons. Retrospective fields are excluded. | Didilani and Dewmi; Tinosh reviews technical clarity. | Inspect the actual human-run prospective bundle and linked records; keep unsupported values explicitly unavailable. |
| B12 — replenishment quantity / overstock | Resolved for current scope through approved deferral; outputs unavailable. | Team acceptance reported on 29 October in the C1 scope/closeout record; DR-012 supplies neither method. | Didilani and relevant team reviewers. | Preserve unavailable reasons and disclose the deferral. Any future implementation needs a separately approved method. |
| B13 — `Order_Quantity` availability | Unresolved at forecast origin. | Dataset records a quantity but does not establish timing as available, received, or outstanding stock. | Didilani. | Establish origin availability before using as context; never infer receipts or optimal orders. |
| B8 — 28-day downstream use | Resolved for current scope through approved deferral; inventory use remains gated. | C1 scope/closeout retains h28 inventory as a disclosed limitation; upstream forecasting remains available. | Didilani and Dewmi with relevant team reviewers. | Retain forecast identity and the existing downstream reason; do not calculate h28 exposure/evaluation. Future extension needs separate approval. |
| B9 — unavailable-state mapping | Internal adapter retains explicit source status/reason fields and field-specific unavailability; no universal shared reason vocabulary is invented. | The prospective handoff distinguishes unknown source timing, conditional scenario availability, gated h=28 outputs and unavailable quantities. Decision-support records preserve those reasons and their source hashes. | Dewmi with each producing owner. | Review the concrete record representation for presentation; retain original reasons and separate future API acceptance. |
| B10 — human-review rules | Resolved for current scope through approved deferral. | C1 scope/closeout and Dewmi’s direct W1 acceptance on 1 November retain automatic triggers as a deferred extension. | Dewmi. | Preserve advisory wording and `not_assessed` with its reason; no automatic trigger is implemented or required for current delivery. |
| B11 — uncertainty method | Resolved for current scope through approved deferral; estimates unavailable. | C1 scope/closeout records team acceptance of the uncertainty limitation. | Chathuranga; Dewmi reviews downstream presentation. | Preserve `unavailable` / `no_agreed_method`; retrospective error is not prospective uncertainty. A future method needs separate approval. |

When reviews occur, update the relevant readiness entries with the proposal, evidence, reviewer, actual review status, and remaining action by the responsible member. Do not mark a blocker resolved merely because this protocol or another document is merged. Any change to DR-012 must reflect actual human-reviewed decisions only.

**Tracking history:** #85/#145/#153 are earlier references; #164/#168 are closed implementation/evidence milestones. #101/#157 supplied the acceptance scenarios in [readiness §12](../integration-contract-readiness.md#12-integration-acceptance-scenarios-issue-101). Current refinement is #177; subsequent member issues are scoped from its reviewed baseline. Specification alone does not establish completed integration.

### 12.1 Run the implemented preparation

Run from the repository root using the existing project environment. This is a human-run data-preparation command, not an inventory evaluation. It verifies the pinned forecast export and validated-bundle provenance, and decodes only inventory columns at `2024-12-02`.

```bash
.venv/bin/python -m src.inventory_risk.forecast_handoff \
  --operator Chathuranga \
  --snapshot-availability unknown \
  --output research-materials/inventory-risk/issue-164/inputs.json
```

The output contains all 1,000 mapped forecasts, source/version hashes, the operator's snapshot basis and preparation status/reasons. The example preserves unknown source timing; it will not create usable inventory exposure from unknown timing. Where actual origin availability is established, use `--snapshot-availability confirmed --snapshot-basis "<actual source-timing basis>"`; a constructed assumption must not be described as verified source timing.

Output is restricted to ignored `research-materials/` and published exclusively: an existing output file is not overwritten. Choose a new output filename for a new run. Keep source data, prepared rows and model artifacts outside Git. Snapshot semantics, the method disposition and actual producer/consumer acceptance remain human-owned factual inputs; software validation does not supply them.

### 12.2 Run the implemented inventory evaluation

[runner.py](../../src/inventory_risk/runner.py) connects the retained export to [evaluation.py](../../src/inventory_risk/evaluation.py). It reads origin inventory only at `2024-12-02`, then separately reads daily `Units_Sold` for `2024-12-03` through `2024-12-16`. Each 1/7/14-day target requires every daily record for its exact inclusive window, valid nonnegative integer sales and unique daily keys. Missing or invalid targets remain unavailable; duplicates fail explicitly. No forecast is trained, re-inferred, clipped or replaced.

The snapshot policy is a required command argument:

| Policy | Meaning |
|---|---|
| `unknown` | Retain unknown source timing and unavailable exposure. Date equality alone never enables a result. |
| `source-confirmed` | The human supplies the actual origin-availability basis using `--snapshot-basis`; this is a source assertion, not a date-match inference. |
| `constructed-origin` | Explicitly select a hypothetical no-receipt scenario using the recorded 2 December inventory/reorder values as starting balances before the 3 December target window. This does not establish actual source timing. |

For a matched constructed-scenario snapshot with unconfirmed source timing, `origin_snapshot_available` stays null, `origin_snapshot_status` stays `unknown` and `inventory_state_available` stays false. Separate `scenario_inventory_state_available` and `analysis_inventory_state_available` fields indicate whether valid same-origin quantities support the conditional calculation. `inventory_basis`, `snapshot_assumption`, scenario-prefixed origin states and separate scenario-at/below counts preserve that distinction. A missing/mismatched origin row remains unavailable in every mode. The explicit option is an execution setting for human review, not a claim that source timing or a new group decision has been verified.

A missing origin row is an explicit input absence: its marker is false, status is unavailable and reason is `origin_inventory_record_missing`, including in constructed mode. The library counterfactual path may use valid same-origin quantities even when their source marker explicitly says unavailable; it preserves that negative source assertion and does not turn the result into origin-known evidence. H=28 rows carry the same constructed assumption/limitation disclosures but never gain analysis availability or exposure values. In source-confirmed mode a valid h=28 source snapshot may be available while its downstream analysis remains gated; those fields describe different facts.

The human executor can run the following command after reviewing that constructed assumption:

```bash
.venv/bin/python -m src.inventory_risk.runner \
  --operator Chathuranga \
  --snapshot-policy constructed-origin \
  --output research-materials/inventory-risk/issue-164/evaluation-v1
```

This evaluates 750 candidate rows across horizons 1/7/14 separately. It decodes at most 250 origin rows and 3,500 daily target rows from the validated bundle; existing receipt checks also hash its retained bytes. All 250 h=28 rows remain in the prospective roster with gated inventory fields; no h=28 retrospective target is read or scored. No horizon-pooled score is generated.

The exclusive output bundle contains:

- `prospective.json`: 1,000 forecast identities with origin/forecast exposure evidence and explicit snapshot assumptions. It excludes realised demand, retrospective margins, confusion cells and metrics.
- `evaluation.json`: the 750 retained candidate cases and horizon-specific DR-012 counts/metrics, including unavailable and already-at/below-threshold cases.
- `report.md`: human-readable counts, metric denominators, unavailable rates and standing limitations.
- `manifest.json`: published last, binding the output hashes, exact export, dataset provenance, snapshot policy, operator, timestamp and implementation hashes.

Only `prospective.json` is interpreted by the optional inventory bridge in the [decision-support preparation](responsible-decision-support-evaluation.md#22-prepare-records-and-record-the-human-assessment). All three output-file hashes are checked; the retrospective JSON and Markdown report are hashed as opaque bytes, not decoded as prospective inputs. Consistency checks do not authenticate a mutable manifest or establish scientific correctness. Existing output directories are never overwritten. These files are conditional scenario evidence, not actual stockout ground truth, numerical replenishment instructions or proof of real-retailer effectiveness.

### 12.3 Retained human-run evidence

Chathuranga manually ran the command in Section 12.2 with `--snapshot-policy constructed-origin`. The manifest records `2026-10-23T06:08:29.741586+00:00` and operator `Chathuranga`. It used the implementation committed in `d977c4747f9d2914e393bacc8b8a9eb2f787f032`; all four recorded source-file hashes matched that local HEAD at publication. This attribution records the actual run; it does not supply missing consumer/peer review. The group approval is recorded separately under #177, without altering the original run status metadata.

The original local bundle remains under `research-materials/inventory-risk/issue-164/evaluation-v1/`. Chathuranga authorised unchanged GitHub review copies: [report.md](../../reports/inventory-risk/issue-164/evaluation-v1/report.md), [prospective.json](../../reports/inventory-risk/issue-164/evaluation-v1/prospective.json), [evaluation.json](../../reports/inventory-risk/issue-164/evaluation-v1/evaluation.json) and [manifest.json](../../reports/inventory-risk/issue-164/evaluation-v1/manifest.json). The prospective SHA-256 is `5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4`; the original manifest SHA-256 is `5d9ea6206c277f4853dc39fc5fdffdcd93f1df629c67fc5a8f2b524038c0fda9`.

The run retained 750 retrospective candidate cases: each 1/7/14-day horizon has 239 paired comparisons, 11 scenario-at/below-threshold cases excluded from forecast-skill comparisons and zero unavailable cases. The prospective roster retains all 1,000 keys, including 250 gated h=28 rows. Counts, metric denominators, prior-validation/exploratory exposure and conditional-scenario limitations remain in the original report; no scores are recomputed or pooled by this documentation update.

Read-only publication checks matched all three manifest-bound output hashes and all four source hashes against local HEAD, accepted all 1,000 prospective rows through the existing decision-support consumer, and matched all four copied files byte for byte. These are local consistency/identity checks; no independently reviewed reference commit was supplied for this run, and the manifest is not authenticated. Publication leaves the original bundle unchanged and does not establish scientific correctness, source timing or peer approval.

The command `.venv/bin/python -m src.data.verify_checksums --profile dewmi` also matched the selected forecast export, 1/1 files with none missing or changed, against `docs/checksums/2026-10-06.json` (reference SHA-256 `381ed9607a9e3ec155ee3754d699d62873bfbff18f5e1f4edc31c407267ed7cc`). The reference revision and repository HEAD were both `d977c4747f9d2914e393bacc8b8a9eb2f787f032`. This was a provisional local check without `--tracked-ref`; the Dewmi profile does not cover the validated dataset, original model bundles or this new evaluation bundle.

## 13. Execution gate

The command examples and implementation status do **not themselves authorise** any of the following. A particular reviewed human run remains a separate action under AGENTS §17:

- dataset-backed preparation or inventory-risk evaluation;
- model training, tuning, inference, experiments, or final-holdout execution;
- generating inventory-risk results, metrics, or charts;
- final schema approval or forecast consumer acceptance;
- runtime adapters, FastAPI, or prototype implementation;
- replenishment formulas or quantities, overstock rules, or risk thresholds;
- an uncertainty method or human-review trigger;
- 28-day downstream inventory use.

Didilani retains responsibility for inventory-risk methodology and evaluation and may manually execute her specifically authorised component research commands in her own terminal under [AGENTS §17](../../AGENTS.md#17-experiment-execution-responsibility). She reviews and explicitly authorises the particular run within the approved component scope; DR-012 method approval is recorded; review of additional cross-component decisions and specific-run authorisation remain separate prerequisites. Any later execution requires the methodology, field mapping, protocol and execution-critical approvals to be reviewed first. AI assistants may prepare code and explain the exact command, then hand it to the human member; they do not execute the research run. Forecasts in the retained export must not be retrained, re-inferred, or recomputed for this work.

## 14. Review checklist

### Chathuranga

- [ ] Confirm forecast origin, horizon and inclusive target-window interpretation.
- [ ] Confirm the accepted export hash and consumer handoff status; distinguish checksum integrity from acceptance.
- [ ] Review row-level versus export-level provenance mapping.
- [ ] Define or explicitly leave unresolved `evidence_role`; do not infer it from `producer_status`.
- [ ] Review meanings and mapping of forecast, prediction, eligibility, and target statuses.
- [ ] Review the proposed handling of negative, missing, malformed, non-finite, and invalid forecast records.
- [ ] Review the implemented mappings and error handling in Sections 4.1 and 6.1 and the actual preparation output; keep snapshot/source limitations and separate method decisions explicit.

### Dewmi

- [ ] Review inventory-to-decision-support meaning and the proposed unavailable-state distinctions/mapping.
- [ ] Confirm missing inventory/replenishment evidence remains explicit and does not automatically exclude a selected record.
- [ ] Confirm this protocol does not perform Issue #153's record selection or transparency assessment and does not introduce human-review triggers.

### Tinosh

- [ ] Review the technical clarity of identities, source scopes, horizon fields, provenance and status mapping.
- [ ] Confirm unavailable/unknown/approval-gated cases are distinguishable for later integration without treating this as a final schema.
- [ ] Confirm adapters, charts and prototype rendering remain outside Issue #162.

### Group / project review

- [x] Record Chathuranga's report of DR-012 group approval for the documented 1/7/14-day method; preserve the original output labels and other open decisions.
- [x] Record the accepted h28 inventory deferral separately from available upstream forecasts; preserve its downstream gate.
- [ ] Confirm the retained execution, method approval and final consumer acceptance are distinct; any later research run requires its own specific human authorisation.

## References

- [Issue #164 — inventory-risk scenario assumptions and forecast input mapping](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/164); closed implementation/evidence milestone; current refinement is #177 and later member tasks are scoped from its reviewed baseline.
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
