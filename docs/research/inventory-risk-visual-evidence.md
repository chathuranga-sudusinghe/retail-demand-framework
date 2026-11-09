# Inventory-Risk Visual Evidence Specification and Interpretation

**Current figure delivery — reconciled 9 November 2026:** Chathuranga approved the compact eight-figure selection on 5 November, including the two forecasting/transparency additions. The eight PNG/SVG/JSON sets are delivered in `reports/figures/final-thesis-figures/`. The [figure delivery guide](thesis-figure-delivery.md) records source identities, generation and checks; the [current acceptance record](../integration-contract-readiness.md#12-current-delivery-and-acceptance--9-november-2026) links completed technical/W2 reviews and Chathuranga's reported inventory acceptance and clarification. No analytical requirement, retained value or method is changed.

**Historical specification issue:** [#85](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/85), closed. Current delivery/acceptance is recorded under completed #201/#182 and [#179](../integration-contract-readiness.md#12-current-delivery-and-acceptance--9-november-2026); #177 remains the historical readiness baseline.

**Responsible member:** Didilani Pathinayaka — inventory-risk analysis and interpretation

**Status:** Analytical specification and interpretation linked to the published constructed-origin evaluation and the delivered eight figures. Completed scoped reviews are linked above; this update runs no analysis or renderer.

**Method status:** [DR-012](../decisions/DR-012-inventory-risk-replenishment-methodology.md#group-approval-record) records approval of the 1/7/14-day method in the 12 October WhatsApp discussion, reported by Chathuranga on 23 October. Historical evidence retains its recorded proposed-status labels; source timing and h=28 inventory approval are separate.

## 1. Purpose and scope

This document specifies the analytical meaning of inventory-risk visual evidence and records what the current project evidence can support. It prepares a report-ready interpretation and handoffs for Tinosh's technical visualization contribution and Dewmi's responsible decision-support work.

The specification follows the historical [Issue #85](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/85), the merged [Issue #70 preparation and evaluation utilities](../../src/inventory_risk/input_preparation.py) and [evaluation utilities](../../src/inventory_risk/evaluation.py), and the method in [DR-012](../decisions/DR-012-inventory-risk-replenishment-methodology.md). The Issue #70 tests establish behavior on synthetic fixtures; they are not inventory-risk findings from the supplied dataset.

This is an analysis and documentation deliverable. It does not add code, render charts, execute the evaluator, create new inventory-risk calculations, or settle a shared schema. A visual may communicate only evidence that is actually available and appropriately approved. A display must not silently turn an unresolved input or a method approval into proof of operational effectiveness.

## 2. Evidence register

**Historical package inspection:** The received-package statuses and local byte checks below retain their original scope. They are not current acceptance status. The current producer/source, reported consumer and rendered acceptance is linked above; original package/provenance labels are unchanged.

| Evidence item | Source identity and contents | Population / time identity | Integrity and review status | Inventory-risk use status |
|---|---|---|---|---|
| Handoff package | `research-materials/received/final-20261003-02/`; source run `final-20261003-02`; source repository commit `d9714bbffa3d52730991336b49e07b527e396cc7` | Member-specific derivative package, not a complete research archive | Package manifest says “prepared for recipient review; not consumer acceptance.” Package transfer checksums do not approve the research method or accept the forecast handoff. | Context and evidence identity only. |
| Source-run anchors | Package manifest records source-manifest SHA-256 `adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43` and prediction-receipt SHA-256 `853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692` | Refer to the retained source run; source artifacts themselves are not included in the received derivative package | Recorded references only; this package does not independently verify the source run artifacts. | Preserve as provenance references; do not treat the hashes as completed inventory-risk evidence. |
| Historical repository context at specification preparation | Branch `analysis/inventory-risk-evidence-interpretation`; `HEAD` and `origin/main` are `8f9979eb1842e29b156cce96cfcc6e08a05c9eff` at document preparation | Current main contains merged Issue #70 code/tests and current DR-012 / integration boundaries | The package source commit differs from current main. Current main documentation governs current requirements; the package remains traceable to its source commit. | Use current main contracts; do not infer approval from the older package. |
| Forecast export | `data/processed/forecasting/handoffs/final-20261003-02/issue-132-forecast-export-v1.json`; schema `issue-132-forecast-export-v1`; SHA-256 `c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863` | Source stage context is the final run `final-20261003-02`; the export has no per-row `evaluation_stage` field. It contains 1,000 records: 250 SKU-warehouse records at each horizon 1, 7, 14 and 28; forecast origin `2024-12-02`. | Local file hash matched the received package manifest. The package states the export hash reviewed by Chathuranga and consumer acceptance are pending. Forecast uncertainty status is unavailable. | Prospective forecast evidence only. It is not a completed inventory-risk evaluation. Do not retrain, re-infer, or recompute these forecasts. |
| Designated forecast producers in export | Export records retain `model`, `configuration_id`, and `producer_status`; producer/configuration varies by horizon | `h=1`: LightGBM / GBM018; `h=7`: LightGBM / GBM011; `h=14`: XGBoost / GBM022; `h=28`: XGBoost / GBM003 | Record-level producer context is present. Forecast rows do not contain flattened `run_id` or `evaluation_stage` columns, but those values are available as `source.run_id` and `source.evaluation_stage` in export-level metadata. `evidence_role` is not supplied. The [implemented mapping](../../src/inventory_risk/forecast_handoff.py) preserves source scopes, propagates provenance and derives primary role only for the pinned export; consumer acceptance remains separate. | Preserve actual source context. Do not fabricate missing provenance fields or use this note to change model selection. |
| Validated dataset bundle | `data/processed/validated/supply-chain-dataset1-validated-v1/`; `validated.parquet`, `schema.json`, `validation-audit.json`, and `provenance.json` | 91,250 native-grain rows; 50 SKUs, five warehouses; 2024-01-01 through 2024-12-30; key is Date + SKU_ID + Warehouse_ID | All four payload hashes matched the package manifest. Schema/audit report passed shared validation and readback. The provenance record says `pending_human_review`; this is not consumer acceptance. | Provides source inventory fields and observed `Units_Sold`. It does not establish origin-time availability or contain computed inventory-risk outcomes. |
| Handoff metadata checksums | `HANDOFF/manifest.json`, `HANDOFF/README.md`, and `HANDOFF/SHA256SUMS` | Package metadata | README and manifest hashes matched `HANDOFF/SHA256SUMS`; payload hashes matched the manifest. These are integrity checks only. | Does not change pending human review, consumer acceptance, or methodology approval. |
| Origin inventory snapshot | Same-SKU/warehouse inventory record would need to correspond to the forecast origin | Origin `2024-12-02` in the export | Availability at forecast issuance and same-day before/after-sales semantics are not established. Date equality alone is insufficient. The Issue #70 preparation API requires an explicit `origin_snapshot_available` marker from its caller. | Source-based exposure stays unavailable without timing evidence. The retained constructed-origin scenario uses hypothetical starting balances and preserves unknown source timing; do not infer the source marker from the date. |
| Forecast-to-inventory mapping | [forecast_handoff.py](../../src/inventory_risk/forecast_handoff.py), mapping `issue-164-168-v1`; final API contract remains separate | Exact 1,000-key retained export with identity, origin, horizon, intervals and provenance | Internal mapping and problem-value validation are implemented; consumer acceptance remains separate. | Use the implemented mapping; no invented provenance or snapshot availability. |
| Method and approval | [DR-012 approval record](../decisions/DR-012-inventory-risk-replenishment-methodology.md#group-approval-record) | Fixed-origin/no-receipt scenario, h=1/7/14 | Group approval reported by Chathuranga; source timing and final consumer acceptance are separate. | Do not extend to h=28, actual stockout claims or order quantities. |

The historical local SHA-256 comparisons above identified the received bytes against the supplied package manifest. They do not independently verify the original forecasting run, make the export consumer-accepted, or replace the source run's retained evidence.

## 3. Evidence availability and limitations

### Supplied evidence versus inventory-risk results

The supplied export is prospective forecast evidence at one fixed origin. The validated dataset is source data, including inventory variables and observations after that origin. Neither file alone is a completed inventory-risk output. The [published evaluation](../../reports/inventory-risk/issue-164/evaluation-v1/report.md) now supplies constructed-scenario cases, counts, rates and margins. The eight-figure rendering is delivered; completed scoped reviews are linked in the current acceptance record above.

The Issue #70 evaluator accepts an `observed_target` for retrospective comparison, but the supplied forecast export does not contain one. Any retrospective target would have to be derived only from the corresponding later `Units_Sold` observations over the export's exact target window, kept separate from prospective information. No such join, target construction, or evaluation is performed by this document.

### Evidence classes

- **Descriptive source observations:** [Temporal Demand and Inventory-Alignment Profiling](../../reports/temporal-demand-profile.md) reports historical dataset characteristics and inventory context. It is historical descriptive evidence, not forecast-to-inventory evaluation; no results were regenerated for this document.
- **Synthetic/test evidence:** [Issue #70 tests](../../tests/test_inventory_risk_preparation.py) and [evaluation tests](../../tests/test_inventory_risk_evaluation.py) use controlled test records to check implementation behavior. Passing tests support code behavior only; they do not establish actual inventory effectiveness.
- **Prospective forecast evidence:** The received export contains project-generated forecast values and producer context. It is not the source `Demand_Forecast` field. Current producer/source and reported consumer acceptance are recorded in the linked closeout record; the original package labels remain historical.
- **Retrospective proxy evidence:** Chathuranga manually executed the constructed-origin evaluation on 23 October. The [report](../../reports/inventory-risk/issue-164/evaluation-v1/report.md) and [evaluation.json](../../reports/inventory-risk/issue-164/evaluation-v1/evaluation.json) retain 239 paired cases plus 11 separate scenario-at/below cases per 1/7/14-day horizon. These are simulated-data, hypothetical no-receipt proxy results, not stockout ground truth.

### Known limits and unavailable evidence

- The dataset is simulated by its publisher. It does not establish real-retailer effectiveness.
- `Stockout_Flag` is zero-variance and cannot validate stockout predictions.
- The export has one origin, so it cannot establish temporal consistency across forecast origins.
- Forecast horizons 7, 14, and 28 are cumulative totals, not daily paths. A direct 28-day forecast exists upstream, but downstream inventory use is not approved.
- The no-receipt, fixed-reorder-point scenario is the group-approved DR-012 scenario method, not an approved operational inventory model. Future inventory is not known at forecast time.
- `Order_Quantity` is sparse recorded activity; its timing and receipt meaning are not established.
- Forecast uncertainty has no agreed method and is marked unavailable in the export.
- Same-day inventory timing and final consumer/API acceptance remain unresolved; internal mapping, problematic-forecast handling and the record bridge are implemented in the [integration readiness map](../integration-contract-readiness.md).
- No cost, service-level, optimal-order, or replenishment-quantity evidence is supplied by these files.

## 4. Visual evidence specification

The fields named below refer to the existing internal Issue #70 case/summary outputs and source fields; they are not a new cross-component schema. The evaluator keeps model/configuration, origin, horizon, and available provenance groupings separate. Every case-level mark or row must retain `SKU_ID`, `Warehouse_ID`, `forecast_origin`, and `horizon` so that different warehouses or horizons are not blended.

### A. Exposure-state and population coverage

- **Analytical question:** For each forecast horizon, what portion of the relevant population is origin-known at/below the threshold, initially above it, paired for retrospective comparison, or unavailable?
- **Evidence source:** The retained [prospective records](../../reports/inventory-risk/issue-164/evaluation-v1/prospective.json), [evaluation records and summaries](../../reports/inventory-risk/issue-164/evaluation-v1/evaluation.json), and [manifest](../../reports/inventory-risk/issue-164/evaluation-v1/manifest.json). The source dataset and validated handoff provide source context, not proof of origin-time availability.
- **Required evidence fields:** Case identity; `origin_exposure_state`, `forecast_exposure_state`, `retrospective_exposure_state`, `comparison_case`, `methodology_status`; snapshot, forecast, and retrospective status/reason fields; summary counts including `origin_known_at_or_below_count`, `initially_above_threshold_count`, `evaluable_paired_case_count`, `unavailable_case_count`, and forecast/retrospective unavailable counts; source model/configuration and forecast provenance where available.
- **Population and labels:** Report origin-known-at/below, initially-above, paired-evaluable, constructed-scenario-at/below, and unavailable counts as distinct populations. Label the states `origin status`, `forecast scenario exposure`, `retrospective proxy exposure` (evaluation view only), and `unavailable/not assessed`; name each displayed denominator.
- **Case identity:** Preserve `SKU_ID`, `Warehouse_ID`, forecast origin, and horizon at record level. Counts must identify their population and denominator.
- **Grouping dimensions:** Horizon and existing evaluator provenance groups; case-level rows remain traceable to the SKU-warehouse pair. Do not invent additional subgroup aggregation rules.
- **Horizon handling:** Keep h=1 next-day, h=7 cumulative, and h=14 cumulative separate. The h=28 record may be shown as retained forecast identity with downstream use not approved; no h=28 exposure or evaluation result is shown.
- **What it can support:** Coverage, input availability, and the distribution of scenario exposure states under the stated input basis.
- **What it cannot support:** A stockout label, actual future inventory state, universally meaningful risk category, cross-origin score, or approved action.
- **Assumptions:** The source-available or constructed snapshot basis and no-receipt assumptions must be explicit; no future `Inventory_Level` is used.
- **Limitations:** Current snapshot availability and export consumer acceptance are unresolved; constructed-scenario case counts are published; they do not verify source timing.
- **Unavailable/not-assessed behavior:** Keep affected cases with explicit status and reason. Unknown snapshot availability must not be recoded as unavailable with an invented cause, zero, false, or no crossing. Distinguish unknown from confirmed unavailable using the existing evidence reason/status.

### B. Forecast versus retrospective proxy-crossing comparison

- **Analytical question:** Among initially above-threshold cases with paired usable inputs, how do forecast threshold crossings compare with retrospective demand-proxy crossings?
- **Evidence source:** The retained `evaluation.json` case rows and horizon summaries, with `report.md` as the published summary. Forecast values and producer provenance originate in the retained export; realised `Units_Sold` is retrospective evidence only.
- **Required evidence fields:** Case identity; forecast and retrospective exposure states; `comparison_case`, `confusion_cell`; TP, TN, FP, FN and `N`; `event_prevalence`, `missed_crossing_rate`, `false_alert_rate`, `agreement`, `precision`, `recall`, and `balanced_accuracy` with their status fields; provenance, unavailable reasons, and the reporting population/denominators.
- **Population and labels:** Include only the initially-above-threshold cases with paired usable forecast and complete target-window evidence in confusion counts (`N`). Label the outcome `retrospective threshold-crossing proxy based on Units_Sold—not observed stockout`; show the TP/TN/FP/FN meanings and each metric denominator.
- **Case identity:** Keep each SKU, warehouse, origin, and horizon visible at case level; summaries retain the evaluator's existing source and configuration context.
- **Grouping dimensions:** Existing evaluator-defined origin/horizon/provenance groups only. Do not pool across origins, horizons, configurations, or invent SKU/warehouse subgroup metrics.
- **Horizon handling:** Separate h=1, h=7, and h=14; label h=7 and h=14 as cumulative. Do not calculate downstream h=28 crossing or rates.
- **What it can support:** Agreement with a retrospective threshold-crossing proxy, plus missed-crossing and false-alert behavior in the stated eligible population.
- **What it cannot support:** Actual stockout prediction accuracy, real-world service or cost improvement, causal benefit, or operational policy performance. A retrospective crossing is not an observed stockout.
- **Assumptions:** Forecast and realized demand refer to the same exact target interval; the snapshot is source-confirmed or explicitly hypothetical; the DR-012 fixed-threshold/no-receipt scenario is clearly disclosed. Realized `Units_Sold` is used only retrospectively.
- **Limitations:** There is one supplied forecast origin and a published constructed-scenario paired evaluation. `Stockout_Flag` is not a label. Results remain conditional on the group-approved scenario method and simulated data; source inventory timing is not confirmed.
- **Unavailable/not-assessed behavior:** Exclude unavailable cases from paired confusion counts while retaining their reason and reporting unavailable counts. Undefined denominators remain unavailable, never zero. No forecast, target, or snapshot may be silently imputed.

### C. Margin comparison around reorder reference

- **Analytical question:** For valid cases, how do forecast and retrospective cumulative demand compare with the origin buffer, and how close are margins to the zero reference?
- **Evidence source:** Case-level `inventory_buffer`, `predicted_margin`, and `retrospective_margin` in the retained `evaluation.json`; use `prospective.json` for prospective-only margins and source/assumption context.
- **Required evidence fields:** `predicted_margin`, `retrospective_margin`; `inventory_buffer` if available; case identity; forecast/retrospective status and reasons; exposure state, source model/configuration, and methodology status.
- **Population and labels:** Retain each valid case by SKU, warehouse, origin, and horizon. Label `predicted margin (buffer − forecast demand)` and `retrospective margin (buffer − realised Units_Sold; evaluation only)`, with zero identified as the reorder-reference boundary. Do not merge these into one margin or one population.
- **Case identity:** Retain SKU, warehouse, origin, and horizon on each point/row.
- **Grouping dimensions:** Separate panels or facets by the existing horizon/provenance grouping. No cross-origin pooling or new segment summaries.
- **Horizon handling:** Show only eligible method horizons 1, 7, and 14, separately. h=28 downstream margin is not assessed. Preserve next-day versus cumulative meanings.
- **What it can support:** Descriptive proximity to the reorder reference under the stated scenario for valid cases.
- **What it cannot support:** A future physical inventory trajectory, actual stockout, approved risk band, boundary classification, or order quantity.
- **Assumptions:** Origin quantities are source-available or explicitly hypothetical; reorder point is held fixed; the documented no-receipt scenario is explicit. The zero line is the reference; no near-boundary tolerance is introduced.
- **Limitations:** Origin snapshot timing is unresolved; scenario margins are retained in the evaluation bundle. Negative arithmetic balances, if ever shown from approved evidence, are not verified physical negative inventory.
- **Unavailable/not-assessed behavior:** Do not plot missing margins as zero or place them on either side of the reference. Retain the case and reason in accompanying availability evidence.

### D. Availability and provenance matrix

- **Analytical question:** Which evidence is present, accepted, unavailable, unknown, or gated for each forecast record, and why?
- **Evidence source:** Retained prospective records and manifest, the forecast-export provenance, validated-dataset provenance, and the readiness register. Use each source only for the fields and status scope it actually records.
- **Required evidence fields:** Case identity; export schema/source run; forecast origin, horizon, target dates, prediction status/value, model, configuration, producer status; dataset version and provenance; origin snapshot status/reason; forecast and retrospective input status/reasons; downstream-use status/reason; methodology status, assumptions, and limitations.
- **Population and labels:** Keep one row/mark per existing forecast identity and distinguish `unknown`, `unavailable`, `not assessed`, `approval gated`, and `accepted` only where the source actually establishes that status. Do not collapse these states or infer acceptance from file presence or checksums.
- **Case identity:** Preserve SKU, warehouse, origin, and horizon per record. Keep package/source identifiers alongside records without pretending absent row fields exist.
- **Grouping dimensions:** Horizon, SKU-warehouse identity, and recorded producer/configuration. Do not combine records across horizons or invent missing provenance fields.
- **Horizon handling:** Show h=1/7/14/28 distinctly. For h=28, show forecast evidence as present but downstream exposure/evaluation as gated/unavailable pending separate approval.
- **What it can support:** Traceability, evidence completeness, approval-state visibility, and the explanation of why an output is not assessed.
- **What it cannot support:** Acceptance of the forecast handoff, a finalized interchange schema, an uncertainty method, or an inventory-risk conclusion.
- **Assumptions:** Package hashes identify the checked local copies only. Human review, consumer acceptance, and method approval are separate statuses.
- **Limitations:** Forecast rows are not in the internal preparation format: run/stage provenance is available at export level, while `evidence_role` is not supplied. The internal mapping is implemented; final consumer/API acceptance is separate. The received package is a derivative, not the full forecasting archive.
- **Unavailable/not-assessed behavior:** Display status and reason separately from numeric values; do not replace missing evidence with zero/false or silently drop records. Keep “unknown” distinct from “unavailable” and from “not approved for downstream use.”

## 5. Report-ready interpretation

### Supported findings

- The received handoff identifies a project-generated forecast export at origin `2024-12-02`, with separate records for horizons 1, 7, 14, and 28 and producer/configuration context. These are supplied forecast records, not an inventory-risk result.
- The validated dataset bundle passed its recorded shared-data validation/readback checks, and local payload hashes match the package manifest. Its provenance record retains the historical `pending_human_review` label; later producer/source and reported export consumer acceptance are recorded separately in the linked current record.
- The current Issue #70 implementation produces structured evidence and preserves unavailable reasons when called with appropriately mapped inputs. Its tests establish synthetic implementation behavior only.
- The source is publisher-simulated. Existing descriptive dataset observations are available in the historical [temporal profile](../../reports/temporal-demand-profile.md), with its stated historical scope and limitations.

### Descriptive observations

The temporal profile reports source-level inventory, reorder-point, supplier lead-time, and order-quantity characteristics. Those values describe the dataset; they do not show forecast threshold crossings, inventory-risk effectiveness, or current-origin stock availability. This document does not regenerate or extend that analysis.

### Synthetic/test evidence

Issue #70 tests cover preparation, provenance/identity retention, status handling, proposed exposure behavior, retrospective proxy metrics, and unavailable cases using synthetic records. They do not establish that the supplied real dataset has any particular exposure-state distribution or metric value.

### Retrospective proxy evidence

The [retained evaluation](../../reports/inventory-risk/issue-164/evaluation-v1/report.md) provides the completed dataset-backed constructed-origin comparison for 1/7/14 days. It retains confusion counts, metric denominators and scenario margins. Source timing remains unknown; the results are not observed stockout accuracy, a reconstructed inventory path or proof of managerial benefit. Historical metadata remains unchanged.

#### Retained h1/h7/h14 results

The following values are transcribed from the retained report; no results were recalculated for this document. Each horizon uses the same forecast origin (`2024-12-02`) and a constructed-origin, fixed-reorder-point, no-receipt scenario. The paired population contains initially-above-threshold cases with paired usable evidence. Scenario-at/below cases are reported separately and are not included in the paired comparison denominators.

| Horizon and target window | Paired N | TP | TN | FP | FN | Source-known at/below | Scenario at/below | Unavailable |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| h1 next-day; 2024-12-03 | 239 | 5 | 230 | 0 | 4 | 0 | 11 | 0 |
| h7 cumulative; 2024-12-03–2024-12-09 | 239 | 54 | 168 | 0 | 17 | 0 | 11 | 0 |
| h14 cumulative; 2024-12-03–2024-12-16 | 239 | 121 | 78 | 0 | 40 | 0 | 11 | 0 |

`Source-known at/below = 0` does not establish that the source snapshot was available or that no source records were at/below the threshold. The 11 at/below cases are from the constructed-origin scenario. The reported `unavailable = 0` is the retained evaluator count under that constructed-scenario run, not a resolution of source timing.

| Horizon | Metric | Value | Metric denominator |
|---|---|---:|---:|
| h1 | Event prevalence | 0.0377 | 239 |
| h1 | Missed-crossing rate | 0.4444 | 9 proxy-crossing cases |
| h1 | False-alert rate | 0.0000 | 230 proxy-noncrossing cases |
| h1 | Agreement | 0.9833 | 239 |
| h1 | Precision | 1.0000 | 5 forecast-crossing cases |
| h1 | Recall | 0.5556 | 9 proxy-crossing cases |
| h1 | Balanced accuracy | 0.7778 | positive=9; negative=230 |
| h7 | Event prevalence | 0.2971 | 239 |
| h7 | Missed-crossing rate | 0.2394 | 71 proxy-crossing cases |
| h7 | False-alert rate | 0.0000 | 168 proxy-noncrossing cases |
| h7 | Agreement | 0.9289 | 239 |
| h7 | Precision | 1.0000 | 54 forecast-crossing cases |
| h7 | Recall | 0.7606 | 71 proxy-crossing cases |
| h7 | Balanced accuracy | 0.8803 | positive=71; negative=168 |
| h14 | Event prevalence | 0.6736 | 239 |
| h14 | Missed-crossing rate | 0.2484 | 161 proxy-crossing cases |
| h14 | False-alert rate | 0.0000 | 78 proxy-noncrossing cases |
| h14 | Agreement | 0.8326 | 239 |
| h14 | Precision | 1.0000 | 121 forecast-crossing cases |
| h14 | Recall | 0.7516 | 161 proxy-crossing cases |
| h14 | Balanced accuracy | 0.8758 | positive=161; negative=78 |

These are horizon-specific descriptive comparisons against the retrospective sales proxy. The longer horizons are cumulative windows, so results must remain separate and must not be reduced to a single score. The rates do not establish actual stockout prediction accuracy, real-retailer performance, service/cost improvement, or a need to place an order.

For an individual case, `inventory_buffer = Inventory_Level − Reorder_Point`; `predicted_margin = inventory_buffer − forecast demand`; and `retrospective_margin = inventory_buffer − realised Units_Sold` over the same target window. These margins describe the retained scenario relative to the reorder reference: zero is the reference boundary, and a negative arithmetic margin is not verified physical negative stock. The retrospective margin belongs only in the evaluation view. Preserve unavailable/null margins as null; do not substitute zero or place them on either side of the reference.

The retained report states that December 3–16 had prior validation exposure and that full-year exploratory analysis inspected the final interval. These results must not be described as evaluation on a historically fully unseen period. The source dataset is publisher-simulated, the constructed starting inventory is hypothetical, source snapshot timing remains unknown, and no real-world inventory trajectory is established.

### Unsupported claims

The current evidence does not support actual stockout accuracy, real-retailer effectiveness, cost reduction, service-level improvement, optimal replenishment, causal effect, or the claim that a forecast crossing requires an order or human review.

### Unresolved questions

- Has Chathuranga accepted the exact export hash and consumer handoff?
- What approved evidence establishes that the same-date inventory snapshot was available at forecast origin, and what are its within-day semantics?
- Have the producing and consuming members accepted the implemented internal mapping and the exact evidence version for final delivery?
- Which additional consumer, interpretation and rendered-presentation reviews remain? DR-012 group approval is recorded; further research still needs specific human authorisation.
- Have consumers reviewed the implemented malformed-export rejection and finite-negative/unavailable behaviour?
- Does any separate approval authorize h=28 downstream inventory interpretation? Until then, it remains unavailable.

## 6. Technical handoff to Tinosh

The later visualization implementation should preserve this specification's analytical meaning and use only reviewed evidence made available through the relevant component handoff.

| Handoff requirement | Required behavior |
|---|---|
| Visual questions | Implement the four questions in Section 4: population/state coverage; forecast versus retrospective proxy crossings; margins around the reorder reference; and availability/provenance. |
| Evidence fields | Consume the existing Issue #70 case/summary outputs and their source/provenance fields. Do not interpret the concepts in this document as a final shared schema. |
| Identity and grouping | Keep `SKU_ID`, `Warehouse_ID`, `forecast_origin`, and `horizon` traceable per case. Use only existing evaluator groupings for summaries; state the population and denominators. |
| Labels | Preserve the evidence's recorded method status and show the current DR-012 approval reference separately; distinguish origin-known cases from forecast crossings and retrospective proxy crossings. Label 7/14 as cumulative, h=1 as next-day, and retrospective views as retrospective. |
| Provenance | Retain source run/package, export schema, origin, horizon, model/configuration/producer context where supplied, dataset version, and approval/acceptance status. Do not fabricate fields absent from the export. |
| Horizon handling | Keep horizons separate. Do not show downstream h=28 exposure, retrospective crossing, or margin results before separate approval. |
| Denominators | Show the stated eligible population and `N` with count/rate summaries; retain metric status for undefined denominators. Do not hide unavailable cases from coverage reporting. |
| Unavailable/not assessed | Display the existing status and reason; do not use zero, false, blank, or silent row deletion as a substitute. Keep unknown, unavailable, and approval-gated distinct. |
| Assumptions/limitations | Keep snapshot timing, no-receipt scenario, simulated-data limitation, proxy status, and unresolved approvals visible near the evidence. |

### T1 — minimum joined-prospective-record handoff

Use the existing prospective-record evidence as the source; this description does not define a new interchange schema. A joined prospective record must preserve `SKU_ID`, `Warehouse_ID`, `forecast_origin`, `horizon`, and the existing target start/end dates. It must carry the forecast prediction/unit and available producer/configuration/run/evaluation provenance, plus the applicable inventory buffer and exposure state only with the recorded inventory basis, method status, assumptions, limitations, and original unavailable reasons. Keep source snapshot status (`unknown` in this evaluation) distinct from scenario inventory availability. The approved DR-012 exposure scope is h1/h7/h14; h28 remains downstream-gated. Do not synthesize missing values or rewrite the retained rows' historical `proposed_for_group_approval` metadata.

The T1 prospective view must not contain realised target values, retrospective exposure states, confusion cells, retrospective margins, or evaluation metrics. Those belong in a separately labelled evaluation view.

### W1 — inventory display handoff

The inventory display must label the retained basis as a **constructed-origin, fixed-reorder-point, no-receipt scenario** and show that source origin-snapshot availability and within-day timing remain **unknown**. Do not display the scenario as source-confirmed inventory availability, infer availability from date equality, or imply that the displayed state is an observed stockout or future physical inventory. Keep the source-availability status/reason, scenario state, and method approval status visible as distinct information. Display h1 next-day, h7 cumulative, and h14 cumulative separately; show h28 forecast identity only as downstream-gated, without inventory exposure. Preserve null margins and unavailable reasons. Retrospective realised targets, retrospective exposure states, confusion cells and proxy metrics must be restricted to a separately labelled evaluation view and must not appear as prospective inventory inputs.

Visual implementation must not create a new exposure rule, subgroup aggregation rule, or final interchange schema. It must not introduce a risk score, replenishment rule, order execution, or human-review trigger.

## 7. Downstream-meaning handoff to Dewmi

- **What the evidence can support:** If the relevant inputs and permissions are established, it can describe origin-known reorder-threshold states and compare forecast demand crossings with retrospective cumulative-sales proxy crossings under DR-012's stated scenario. It can show population coverage, denominators, margins, provenance, and unavailable reasons.
- **What remains unavailable:** Verified source snapshot timing, final consumer/API acceptance and rendered views; h=28 inventory, uncertainty, numerical replenishment, overstock and automatic review rules. Existing 1/7/14-day scenario metrics and internal mappings are available.
- **Retrospective meaning:** A realized threshold crossing is retrospective proxy evidence based on `Units_Sold`, not an observed stockout or actual inventory path. Keep outcomes/errors out of prospective views.
- **Human-review status:** Do not infer a review trigger from exposure state. Human-review status remains not assessed unless Dewmi's approved method defines it; this document does not define that method.
- **Transparency to preserve:** Carry assumptions, limitations, source/model provenance, horizon meaning, methodology/approval status, and each unavailable/not-assessed reason. Do not translate missing information into a negative decision.

## 8. Explicit boundaries

- DR-012 approval is recorded separately from this specification. Preserve historical proposed-status evidence and distinguish it from current method approval.
- No new numerical threshold, tolerance, or risk category is introduced.
- No replenishment formula or quantity is introduced.
- `Stockout_Flag` is not ground truth and is not an evaluation label.
- No actual or real-world stockout-accuracy claim is supported.
- No cost-reduction or service-level-improvement claim is supported.
- No automatic review trigger or human-review rule is introduced.
- No 28-day downstream exposure, crossing, margin, or evaluation result is produced.
- Supplied forecasts are not retrained, re-inferred, or recomputed by this work.
- Source `Demand_Forecast` is not the project forecast and must not replace it.
- Future `Inventory_Level` is not assumed known at forecast time; same-date equality alone does not establish availability.
- `Order_Quantity` is not interpreted as confirmed receipts or an optimal-order target.
- The supplied dataset remains publisher-simulated; findings cannot be generalized as real-retailer performance.

## 9. Next analytical steps and unresolved dependencies

**Status reconciliation — 9 November 2026:** The original handoff checklist below records the review dependencies at preparation. Existing source/consumer and technical/presentation decisions are now recorded in the current acceptance record above. Future methods still require separate approval; this is not a request to repeat completed reviews.

1. Review/record exact-export producer and consumer acceptance without regenerating the forecasts or expected hashes.
2. Review the completed constructed-origin evidence and its unknown source timing. Do not turn the hypothetical starting-balance assumption into verified source availability.
3. Review the implemented mapping, exposure results and downstream record bridge, preserving identities, intervals, provenance and unavailable reasons.
4. **Review status:** Didilani's [Issue #181 analytical review](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/181#issuecomment-6380707367) passed and required no analytical documentation change. Her [PR #190 review](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/190#pullrequestreview-5637154678) was `COMMENTED` with `PASS WITH NON-BLOCKING NOTES`, not formal `APPROVED`. Tinosh's technical acceptance and Dewmi's W2 acceptance are recorded; Chathuranga's reported inventory/consumer acceptance and 9 November clarification resolve the old-page findings. The [current #179 record](../integration-contract-readiness.md#12-current-delivery-and-acceptance--9-november-2026) preserves exact attribution and review scopes. Keep h=28 inventory gated.
5. **Report integration:** The inventory interpretation was integrated into Section 6 of the existing group report through merged PR #190. The retained [evaluation report](../../reports/inventory-risk/issue-164/evaluation-v1/report.md) and immutable evaluation bundle remain unchanged; do not create a second report path or alter the bundle.
6. Scope any additional robustness or evaluation separately before a human executes it. Do not repeat completed forecasting or scenario evaluation merely to align documentation.

The existing report supports conditional scenario interpretation. Technical visuals, final owner/consumer acceptance and managerial effectiveness remain separate. The earlier [Issue #177 handoff](../integration-contract-readiness.md#13-remaining-work-handoff-after-issue-177) is historical planning; the [current acceptance record](../integration-contract-readiness.md#12-current-delivery-and-acceptance--9-november-2026) governs the delivered scope.
