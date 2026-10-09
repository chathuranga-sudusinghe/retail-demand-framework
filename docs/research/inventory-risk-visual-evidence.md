# Inventory-Risk Visual Evidence Specification and Interpretation

**Issue:** [#85 — Analysis: specify and interpret inventory-risk visual evidence](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/85)

**Owner:** Didilani Pathinayaka — inventory-risk analysis and interpretation

**Status:** Analytical specification and evidence inventory; no inventory-risk result is reported here.

**Method status:** [DR-012](../decisions/DR-012-inventory-risk-replenishment-methodology.md) remains **Proposed for group approval**.

## 1. Purpose and scope

This document specifies the analytical meaning of inventory-risk visual evidence and records what the current project evidence can support. It prepares a report-ready interpretation and handoffs for Tinosh's later technical visualization work and Dewmi's responsible decision-support work.

The specification follows the current [Issue #85](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/85), the merged [Issue #70 preparation and evaluation utilities](../../src/inventory_risk/input_preparation.py) and [evaluation utilities](../../src/inventory_risk/evaluation.py), and the proposed method in [DR-012](../decisions/DR-012-inventory-risk-replenishment-methodology.md). The Issue #70 tests establish behavior on synthetic fixtures; they are not inventory-risk findings from the supplied dataset.

This is an analysis and documentation deliverable. It does not add code, render charts, execute the evaluator, create new inventory-risk calculations, or settle a shared schema. A visual may communicate only evidence that is actually available and appropriately approved. A display must not silently turn an unresolved input or proposed method into a result.

## 2. Evidence register

| Evidence item | Source identity and contents | Population / time identity | Integrity and review status | Inventory-risk use status |
|---|---|---|---|---|
| Handoff package | `research-materials/received/final-20261003-02/`; source run `final-20261003-02`; source repository commit `d9714bbffa3d52730991336b49e07b527e396cc7` | Member-specific derivative package, not a complete research archive | Package manifest says “prepared for recipient review; not consumer acceptance.” Package transfer checksums do not approve the research method or accept the forecast handoff. | Context and evidence identity only. |
| Source-run anchors | Package manifest records source-manifest SHA-256 `adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43` and prediction-receipt SHA-256 `853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692` | Refer to the retained source run; source artifacts themselves are not included in the received derivative package | Recorded references only; this package does not independently verify the source run artifacts. | Preserve as provenance references; do not treat the hashes as completed inventory-risk evidence. |
| Current repository context | Branch `analysis/inventory-risk-evidence-interpretation`; `HEAD` and `origin/main` are `8f9979eb1842e29b156cce96cfcc6e08a05c9eff` at document preparation | Current main contains merged Issue #70 code/tests and current DR-012 / integration boundaries | The package source commit differs from current main. Current main documentation governs current requirements; the package remains traceable to its source commit. | Use current main contracts; do not infer approval from the older package. |
| Forecast export | `data/processed/forecasting/handoffs/final-20261003-02/issue-132-forecast-export-v1.json`; schema `issue-132-forecast-export-v1`; SHA-256 `c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863` | Source stage context is the final run `final-20261003-02`; the export has no per-row `evaluation_stage` field. It contains 1,000 records: 250 SKU-warehouse records at each horizon 1, 7, 14 and 28; forecast origin `2024-12-02`. | Local file hash matched the received package manifest. The package states the owner-reviewed export hash and consumer acceptance are pending. Forecast uncertainty status is unavailable. | Prospective forecast evidence only. It is not a completed inventory-risk evaluation. Do not retrain, re-infer, or recompute these forecasts. |
| Designated forecast producers in export | Export records retain `model`, `configuration_id`, and `producer_status`; producer/configuration varies by horizon | `h=1`: LightGBM / GBM018; `h=7`: LightGBM / GBM011; `h=14`: XGBoost / GBM022; `h=28`: XGBoost / GBM003 | Record-level producer context is present. Forecast rows do not contain flattened `run_id` or `evaluation_stage` columns, but those values are available as `source.run_id` and `source.evaluation_stage` in export-level metadata. `evidence_role` is not supplied. Mapping these values into the Issue #70 internal preparation format remains subject to review. | Preserve actual source context. Do not fabricate missing provenance fields or use this note to change model selection. |
| Validated dataset bundle | `data/processed/validated/supply-chain-dataset1-validated-v1/`; `validated.parquet`, `schema.json`, `validation-audit.json`, and `provenance.json` | 91,250 native-grain rows; 50 SKUs, five warehouses; 2024-01-01 through 2024-12-30; key is Date + SKU_ID + Warehouse_ID | All four payload hashes matched the package manifest. Schema/audit report passed shared validation and readback. The provenance record says `pending_human_review`; this is not consumer acceptance. | Provides source inventory fields and observed `Units_Sold`. It does not establish origin-time availability or contain computed inventory-risk outcomes. |
| Handoff metadata checksums | `HANDOFF/manifest.json`, `HANDOFF/README.md`, and `HANDOFF/SHA256SUMS` | Package metadata | README and manifest hashes matched `HANDOFF/SHA256SUMS`; payload hashes matched the manifest. These are integrity checks only. | Does not change pending human review, consumer acceptance, or methodology approval. |
| Origin inventory snapshot | Same-SKU/warehouse inventory record would need to correspond to the forecast origin | Origin `2024-12-02` in the export | Availability at forecast issuance and same-day before/after-sales semantics are not established. Date equality alone is insufficient. The Issue #70 preparation API requires an explicit `origin_snapshot_available` marker from its caller. | Exposure, margins, and comparisons remain unavailable/not assessed until an approved availability basis exists. Do not infer the marker from the date. |
| Forecast-to-inventory mapping | Issue #70 preparation consumes paired records with its documented required fields; the final shared interchange schema remains open in [integration readiness](../integration-contract-readiness.md) | Must retain SKU_ID, Warehouse_ID, forecast origin, horizon, target dates, and provenance | No final field mapping or consumer acceptance is documented. | Do not silently fill required fields from package labels or treat a local export as an accepted interface. |
| Method and approval | [DR-012](../decisions/DR-012-inventory-risk-replenishment-methodology.md) and the inventory workflow | Proposed origin reorder-threshold exposure; original downstream scope is 1/7/14 days | DR-012 remains **Proposed for group approval**. Substantive method approval, same-day snapshot contract, and 28-day downstream approval remain separate. | State evidence only as proposed-method evidence if/when permitted; 28-day downstream exposure is unavailable. |

The local SHA-256 comparisons above verify the received bytes against the supplied package manifest. They do not independently verify the original forecasting run, make the export consumer-accepted, or replace the source run's retained evidence.

## 3. Evidence availability and limitations

### Supplied evidence versus inventory-risk results

The supplied export is prospective forecast evidence at one fixed origin. The validated dataset is source data, including inventory variables and observations after that origin. Neither file is a completed inventory-risk output. No real-data state counts, paired crossings, confusion counts, rates, margins, or visual results are currently available in the repository.

The Issue #70 evaluator accepts an `observed_target` for retrospective comparison, but the supplied forecast export does not contain one. Any retrospective target would have to be derived only from the corresponding later `Units_Sold` observations over the export's exact target window, kept separate from prospective information. No such join, target construction, or evaluation is performed by this document.

### Evidence classes

- **Descriptive source observations:** [Temporal Demand and Inventory-Alignment Profiling](../../reports/temporal-demand-profile.md) reports historical dataset characteristics and inventory context. It is historical descriptive evidence, not forecast-to-inventory evaluation; no results were regenerated for this document.
- **Synthetic/test evidence:** [Issue #70 tests](../../tests/test_inventory_risk_preparation.py) and [evaluation tests](../../tests/test_inventory_risk_evaluation.py) use controlled test records to check implementation behavior. Passing tests support code behavior only; they do not establish actual inventory effectiveness.
- **Prospective forecast evidence:** The received export contains project-generated forecast values and producer context. It is not the source `Demand_Forecast` field and is not yet recorded as consumer-accepted.
- **Retrospective proxy evidence:** None has been produced from the supplied data. If later permitted and validly paired, realized cumulative `Units_Sold` crossing the fixed origin threshold would be a retrospective proxy, not observed stockout ground truth or reconstructed inventory evolution.

### Known limits and unavailable evidence

- The dataset is simulated by its publisher. It does not establish real-retailer effectiveness.
- `Stockout_Flag` is zero-variance and cannot validate stockout predictions.
- The export has one origin, so it cannot establish temporal consistency across forecast origins.
- Forecast horizons 7, 14, and 28 are cumulative totals, not daily paths. A direct 28-day forecast exists upstream, but downstream inventory use is not approved.
- The no-receipt, fixed-reorder-point scenario is the proposed DR-012 method, not an approved operational inventory model. Future inventory is not known at forecast time.
- `Order_Quantity` is sparse recorded activity; its timing and receipt meaning are not established.
- Forecast uncertainty has no agreed method and is marked unavailable in the export.
- Same-day inventory timing, final forecast-to-inventory mapping, problematic-forecast handling, and downstream unavailable-state mappings remain unresolved in the [integration readiness map](../integration-contract-readiness.md).
- No cost, service-level, optimal-order, or replenishment-quantity evidence is supplied by these files.

## 4. Visual evidence specification

The fields named below refer to the existing internal Issue #70 case/summary outputs and source fields; they are not a new cross-component schema. The evaluator keeps model/configuration, origin, horizon, and available provenance groupings separate. Every case-level mark or row must retain `SKU_ID`, `Warehouse_ID`, `forecast_origin`, and `horizon` so that different warehouses or horizons are not blended.

### A. Exposure-state and population coverage

- **Analytical question:** For each forecast horizon, what portion of the relevant population is origin-known at/below the threshold, initially above it, paired for retrospective comparison, or unavailable?
- **Required evidence fields:** Case identity; `origin_exposure_state`, `forecast_exposure_state`, `retrospective_exposure_state`, `comparison_case`, `methodology_status`; snapshot, forecast, and retrospective status/reason fields; summary counts including `origin_known_at_or_below_count`, `initially_above_threshold_count`, `evaluable_paired_case_count`, `unavailable_case_count`, and forecast/retrospective unavailable counts; source model/configuration and forecast provenance where available.
- **Case identity:** Preserve `SKU_ID`, `Warehouse_ID`, forecast origin, and horizon at record level. Counts must identify their population and denominator.
- **Grouping dimensions:** Horizon and existing evaluator provenance groups; case-level rows remain traceable to the SKU-warehouse pair. Do not invent additional subgroup aggregation rules.
- **Horizon handling:** Keep h=1 next-day, h=7 cumulative, and h=14 cumulative separate. The h=28 record may be shown as retained forecast identity with downstream use not approved; no h=28 exposure or evaluation result is shown.
- **What it can support:** Coverage, input availability, and the distribution of proposed exposure states if required inputs are valid and permitted.
- **What it cannot support:** A stockout label, actual future inventory state, universally meaningful risk category, cross-origin score, or approved action.
- **Assumptions:** The proposed DR-012 origin snapshot and no-receipt scenario apply only if their required evidence and permissions are explicit; no future `Inventory_Level` is used.
- **Limitations:** Current snapshot availability and export consumer acceptance are unresolved; no real-data case-state counts have been generated.
- **Unavailable/not-assessed behavior:** Keep affected cases with explicit status and reason. Unknown snapshot availability must not be recoded as unavailable with an invented cause, zero, false, or no crossing. Distinguish unknown from confirmed unavailable using the existing evidence reason/status.

### B. Forecast versus retrospective proxy-crossing comparison

- **Analytical question:** Among initially above-threshold cases with paired usable inputs, how do forecast threshold crossings compare with retrospective demand-proxy crossings?
- **Required evidence fields:** Case identity; forecast and retrospective exposure states; `comparison_case`, `confusion_cell`; TP, TN, FP, FN and `N`; `event_prevalence`, `missed_crossing_rate`, `false_alert_rate`, `agreement`, `precision`, `recall`, and `balanced_accuracy` with their status fields; provenance, unavailable reasons, and the reporting population/denominators.
- **Case identity:** Keep each SKU, warehouse, origin, and horizon visible at case level; summaries retain the evaluator's existing source and configuration context.
- **Grouping dimensions:** Existing evaluator-defined origin/horizon/provenance groups only. Do not pool across origins, horizons, configurations, or invent SKU/warehouse subgroup metrics.
- **Horizon handling:** Separate h=1, h=7, and h=14; label h=7 and h=14 as cumulative. Do not calculate downstream h=28 crossing or rates.
- **What it can support:** Agreement with a retrospective threshold-crossing proxy, plus missed-crossing and false-alert behavior in the stated eligible population.
- **What it cannot support:** Actual stockout prediction accuracy, real-world service or cost improvement, causal benefit, or operational policy performance. A retrospective crossing is not an observed stockout.
- **Assumptions:** Forecast and realized demand refer to the same exact target interval; an origin snapshot is explicitly established; the proposed DR-012 fixed-threshold/no-receipt scenario is clearly disclosed. Realized `Units_Sold` is used only retrospectively.
- **Limitations:** There is one supplied forecast origin, and no paired real-data evaluation exists. `Stockout_Flag` is not a label. Results remain conditional on a proposed method and simulated data.
- **Unavailable/not-assessed behavior:** Exclude unavailable cases from paired confusion counts while retaining their reason and reporting unavailable counts. Undefined denominators remain unavailable, never zero. No forecast, target, or snapshot may be silently imputed.

### C. Margin comparison around reorder reference

- **Analytical question:** For valid cases, how do forecast and retrospective cumulative demand compare with the proposed origin buffer, and how close are margins to the zero reference?
- **Required evidence fields:** `predicted_margin`, `retrospective_margin`; `inventory_buffer` if available; case identity; forecast/retrospective status and reasons; exposure state, source model/configuration, and methodology status.
- **Case identity:** Retain SKU, warehouse, origin, and horizon on each point/row.
- **Grouping dimensions:** Separate panels or facets by the existing horizon/provenance grouping. No cross-origin pooling or new segment summaries.
- **Horizon handling:** Show only eligible proposed-method horizons 1, 7, and 14, separately. h=28 downstream margin is not assessed. Preserve next-day versus cumulative meanings.
- **What it can support:** Descriptive proximity to the reorder reference under the proposed scenario for valid cases.
- **What it cannot support:** A future physical inventory trajectory, actual stockout, approved risk band, boundary classification, or order quantity.
- **Assumptions:** Origin inventory and reorder point are available at the forecast origin; reorder point is held fixed; the documented no-receipt scenario is explicit. The zero line is the reference; no near-boundary tolerance is introduced.
- **Limitations:** Origin snapshot timing is unresolved; no margins have been computed from the supplied files. Negative arithmetic balances, if ever shown from approved evidence, are not verified physical negative inventory.
- **Unavailable/not-assessed behavior:** Do not plot missing margins as zero or place them on either side of the reference. Retain the case and reason in accompanying availability evidence.

### D. Availability and provenance matrix

- **Analytical question:** Which evidence is present, accepted, unavailable, unknown, or gated for each forecast record, and why?
- **Required evidence fields:** Case identity; export schema/source run; forecast origin, horizon, target dates, prediction status/value, model, configuration, producer status; dataset version and provenance; origin snapshot status/reason; forecast and retrospective input status/reasons; downstream-use status/reason; methodology status, assumptions, and limitations.
- **Case identity:** Preserve SKU, warehouse, origin, and horizon per record. Keep package/source identifiers alongside records without pretending absent row fields exist.
- **Grouping dimensions:** Horizon, SKU-warehouse identity, and recorded producer/configuration. Do not combine records across horizons or invent missing provenance fields.
- **Horizon handling:** Show h=1/7/14/28 distinctly. For h=28, show forecast evidence as present but downstream exposure/evaluation as gated/unavailable pending separate approval.
- **What it can support:** Traceability, evidence completeness, approval-state visibility, and the explanation of why an output is not assessed.
- **What it cannot support:** Acceptance of the forecast handoff, a finalized interchange schema, an uncertainty method, or an inventory-risk conclusion.
- **Assumptions:** Package hashes identify the checked local copies only. Human review, consumer acceptance, and method approval are separate statuses.
- **Limitations:** Forecast rows are not in the internal preparation format: run/stage provenance is available at export level, while `evidence_role` is not supplied. No cross-component mapping is approved. The received package is a derivative, not the full forecasting archive.
- **Unavailable/not-assessed behavior:** Display status and reason separately from numeric values; do not replace missing evidence with zero/false or silently drop records. Keep “unknown” distinct from “unavailable” and from “not approved for downstream use.”

## 5. Report-ready interpretation

### Supported findings

- The received handoff identifies a project-generated forecast export at origin `2024-12-02`, with separate records for horizons 1, 7, 14, and 28 and producer/configuration context. These are supplied forecast records, not an inventory-risk result.
- The validated dataset bundle passed its recorded shared-data validation/readback checks, and local payload hashes match the package manifest. Its provenance record remains `pending_human_review`; the export consumer acceptance remains pending.
- The current Issue #70 implementation produces structured evidence and preserves unavailable reasons when called with appropriately mapped inputs. Its tests establish synthetic implementation behavior only.
- The source is publisher-simulated. Existing descriptive dataset observations are available in the historical [temporal profile](../../reports/temporal-demand-profile.md), with its stated historical scope and limitations.

### Descriptive observations

The temporal profile reports source-level inventory, reorder-point, supplier lead-time, and order-quantity characteristics. Those values describe the dataset; they do not show forecast threshold crossings, inventory-risk effectiveness, or current-origin stock availability. This document does not regenerate or extend that analysis.

### Synthetic/test evidence

Issue #70 tests cover preparation, provenance/identity retention, status handling, proposed exposure behavior, retrospective proxy metrics, and unavailable cases using synthetic records. They do not establish that the supplied real dataset has any particular exposure-state distribution or metric value.

### Retrospective proxy evidence

No real-data retrospective proxy evaluation is currently available. Although later `Units_Sold` observations are present in the validated source bundle, they have not been paired with the export in an Issue #70 evidence result here. Any future realized crossing is a proxy comparison under the stated scenario, not actual stockout ground truth or reconstructed inventory evolution.

### Unsupported claims

The current evidence does not support actual stockout accuracy, real-retailer effectiveness, cost reduction, service-level improvement, optimal replenishment, causal effect, or the claim that a forecast crossing requires an order or human review.

### Unresolved questions

- Has Chathuranga accepted the exact export hash and consumer handoff?
- What approved evidence establishes that the same-date inventory snapshot was available at forecast origin, and what are its within-day semantics?
- What owner-approved field mapping supplies the Issue #70 input contract without inventing run/stage/role provenance or availability markers?
- Is DR-012 approved for group use, and what permitted analytical execution follows from that status?
- How should problematic forecasts be represented without clipping or substitution?
- Does any separate approval authorize h=28 downstream inventory interpretation? Until then, it remains unavailable.

## 6. Technical handoff to Tinosh

The later visualization implementation should preserve this specification's analytical meaning and use only reviewed evidence made available through the relevant component handoff.

| Handoff requirement | Required behavior |
|---|---|
| Visual questions | Implement the four questions in Section 4: population/state coverage; forecast versus retrospective proxy crossings; margins around the reorder reference; and availability/provenance. |
| Evidence fields | Consume the existing Issue #70 case/summary outputs and their source/provenance fields. Do not interpret the concepts in this document as a final shared schema. |
| Identity and grouping | Keep `SKU_ID`, `Warehouse_ID`, `forecast_origin`, and `horizon` traceable per case. Use only existing evaluator groupings for summaries; state the population and denominators. |
| Labels | Label DR-012 exposure evidence as proposed; distinguish origin-known cases from forecast crossings and retrospective proxy crossings. Label 7/14 as cumulative, h=1 as next-day, and retrospective views as retrospective. |
| Provenance | Retain source run/package, export schema, origin, horizon, model/configuration/producer context where supplied, dataset version, and approval/acceptance status. Do not fabricate fields absent from the export. |
| Horizon handling | Keep horizons separate. Do not show downstream h=28 exposure, retrospective crossing, or margin results before separate approval. |
| Denominators | Show the stated eligible population and `N` with count/rate summaries; retain metric status for undefined denominators. Do not hide unavailable cases from coverage reporting. |
| Unavailable/not assessed | Display the existing status and reason; do not use zero, false, blank, or silent row deletion as a substitute. Keep unknown, unavailable, and approval-gated distinct. |
| Assumptions/limitations | Keep snapshot timing, no-receipt scenario, simulated-data limitation, proxy status, and unresolved approvals visible near the evidence. |

Visual implementation must not create a new exposure rule, subgroup aggregation rule, or final interchange schema. It must not introduce a risk score, replenishment rule, order execution, or human-review trigger.

## 7. Downstream-meaning handoff to Dewmi

- **What the evidence can support:** If the relevant inputs and permissions are established, it can describe origin-known reorder-threshold states and compare forecast demand crossings with retrospective cumulative-sales proxy crossings under DR-012's proposed scenario. It can show population coverage, denominators, margins, provenance, and unavailable reasons.
- **What remains unavailable:** Real-data crossing metrics have not been produced; origin snapshot availability and same-day semantics are unresolved; the forecast-to-inventory field mapping and export acceptance are pending; h=28 downstream exposure is not approved; uncertainty, replenishment quantity, overstock, and review rules remain unresolved.
- **Retrospective meaning:** A realized threshold crossing is retrospective proxy evidence based on `Units_Sold`, not an observed stockout or actual inventory path. Keep outcomes/errors out of prospective views.
- **Human-review status:** Do not infer a review trigger from exposure state. Human-review status remains not assessed unless Dewmi's approved method defines it; this document does not define that method.
- **Transparency to preserve:** Carry assumptions, limitations, source/model provenance, horizon meaning, methodology/approval status, and each unavailable/not-assessed reason. Do not translate missing information into a negative decision.

## 8. Explicit boundaries

- DR-012 remains **Proposed for group approval**; this specification does not approve it.
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

1. Obtain/record owner acceptance of the exact forecast export and consumer handoff; retain the existing source hashes rather than regenerating the export.
2. Resolve the origin inventory snapshot availability and within-day semantics with the responsible owners. Do not set `origin_snapshot_available=True` from a date match alone.
3. Agree a forecast-to-inventory input mapping that preserves identity, target interval, producer provenance, statuses, assumptions, and unavailable reasons. Preserve the available `source.run_id` and `source.evaluation_stage` as export-level provenance; propagating them into inventory-risk records requires a reviewed mapping. `evidence_role` is not supplied and remains unresolved. Do not invent missing provenance values.
4. Confirm the permitted use/execution status of the DR-012 proposal before producing any real-data crossing or margin results. Keep 28-day downstream use separately gated.
5. If and when those dependencies are resolved and analytical execution is separately authorized, create traceable evidence from the existing forecast values and retrospective `Units_Sold` only; do not rerun forecasting. Report the exact population, origin, horizon, denominators, unavailable cases, assumptions, and limitations.
6. Give the reviewed analytical specification to Tinosh for technical implementation and to Dewmi for downstream meaning review. Their work must preserve the boundaries in this document and their own component approvals.

Until the relevant dependencies are resolved, the report-ready conclusion is limited to the supplied-file provenance, existing descriptive dataset context, synthetic/test implementation evidence, and explicit non-availability of real-data inventory-risk results.
