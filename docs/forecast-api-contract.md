# Retained Forecast Export Contract — Fixed-Origin Handoff

**Issue:** #132 — Phase 3: Define forecast API contract and hand off forecasting outputs to Tinosh
**Owner:** Chathuranga Sudusinghe — forecasting-facing contract and output meaning
**Implementer after handoff:** Tinosh Gamage — FastAPI endpoints, schemas, adapters and API tests
**Date:** 2026-10-05 (Asia/Colombo)
**Status:** Retained-export contract; exporter and synthetic checks are implemented, and a local export exists. Acceptance of its exact hash and Tinosh's consumer acceptance remain pending. The earlier stored-forecast runtime design is superseded by Chathuranga's explicit request for request-time saved-model inference on 2026-10-05. The active API contract is [Request-time forecast API](forecast-inference-api.md); the fixed-origin export remains a separate artifact.

---

## 1. Purpose and boundaries

This document defines the retained fixed-origin forecasting export and its record meaning. Its export-specific source checks, schema and storage rules remain applicable to that artifact. Sections 8–9 describe the earlier lookup proposal and do not govern the active [request-time API](forecast-inference-api.md).

It covers:

- the exact verified source run and the read-only evidence checks required before use;
- the unchanged DR-014 producer mapping;
- forecast origin, horizon, target interval and cumulative meaning;
- record fields, provenance and model references;
- fields that must never appear in a prospective view;
- unavailable and error behaviour;
- API constraints and the handoff to Tinosh.

It does **not**:

- implement FastAPI endpoints, adapters or prototype screens (Tinosh, after handoff);
- run, refit, retune or reselect any model ([AGENTS.md](../AGENTS.md) Sections 17–19);
- reinterpret the completed research evidence ([final evaluation](forecasting-final-evaluation.md));
- define inventory-risk, replenishment, uncertainty or human-review methods (Didilani, Dewmi; [DR-011](decisions/DR-011-decision-support-output-structure.md), [DR-012](decisions/DR-012-inventory-risk-replenishment-methodology.md));
- approve 28-day downstream inventory use (blocker B8 in [integration readiness](integration-contract-readiness.md#9-blockers)).

The key words **MUST**, **MUST NOT**, **SHOULD** and **MAY** are used as described in RFC 2119 and RFC 8174 (Section 13).

## 2. Source evidence

The only source for this contract is the completed final run below. Facts are taken from its retained local metadata; this document performs no new verification.

| Item | Value |
|---|---|
| Run ID | `final-20261003-02` |
| Evaluation stage | `final_evaluation` |
| Source schema | `issue-130-final-v1` |
| Recorded run status | `verified_completed` |
| Recorded completion time (UTC) | `2026-10-03T15:34:19.963693+00:00` |
| Completion authority | `artifacts/forecasting/final-20261003-02/run_manifest.json` |
| Manifest SHA-256 | `adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43` |
| Prediction receipt SHA-256 | `853692cbf89076ac1c63791a36440a4abb433d57c8c759f0e364ce7d544ed692` |
| Series covered | 250 SKU-warehouse pairs (50 SKUs × 5 warehouses) |
| Training history | 2024-01-01 through 2024-12-02, inclusive |
| Forecast origin | 2024-12-02 |

Rules:

1. The source already completed scientific integrity verification. Before export, a consumer MUST compare the exact manifest bytes with the independently pinned manifest SHA-256 in the table above. The expected hash MUST NOT be obtained from the same mutable bundle or silently refreshed.
2. The exporter MUST perform read-only checks of run identity, source schema/version, completion status and the recorded passed integrity result; check metadata agrees with the manifest; and verify each consumed source file against its manifest SHA-256. The prediction receipt must also match the pinned receipt hash and its retained bindings. Missing, changed, redirected, malformed or incomplete required evidence blocks export; there is no fallback to another run.
3. The exporter parses only `run_manifest.json`, `run_metadata.json`, `prediction_receipt.json`, `candidates.json` and `predictions.json`. Producer model, descriptor, preprocessing and origin-input references MUST match the manifest; their files may be read as bytes for hash checks only. The exporter MUST NOT read `observations.json` or `metrics.json`, load models, generate/replay predictions, or recalculate research metrics.
4. The exporter MUST NOT call `verify_final_completed`, `verify_final_scientific` or `verify_sealed_predictions`: these perform model/baseline replay and/or scientific reconciliation beyond the export checks. Carry the recorded integrity result unchanged. Read-only binding/schema checks establish that this export uses the retained evidence; they are not a new scientific verification.
5. Nothing may be written inside `artifacts/forecasting/final-20261003-02/`, `models/forecasting/final-20261003-02/` or the run's report directory ([storage policy](artifact-storage-policy.md#version-completion-and-archival-discipline)). No "latest run" discovery is allowed.

## 3. Agreed design directions (owner discussion, 2026-10-05)

### 3.1 Active inference API; retained export remains separate

The owner explicitly requested that each presentation request supply new daily history and invoke a saved designated model. The active request, response and endpoint definitions are in [Request-time forecast API](forecast-inference-api.md). This supersedes the previous option A serving proposal, without changing the retained export or frozen producer mapping.

| Behavior | Current purpose |
|---|---|
| Serve stored fixed-origin producer records | Retained export only; not the presentation API |
| Invoke saved producers on supplied request history | Active presentation API, requested by Chathuranga on 2026-10-05; implementation subject to human review |

The retained export still represents forecasts issued at origin 2024-12-02. The active API uses the supplied request origin and history; it does not read the export as its output source.

### 3.2 Forecast producer resolved by horizon

There is one logical forecast operation. The client chooses a **horizon**; the producer model is resolved from the frozen DR-014 mapping (Section 4). Optional model/configuration assertions validate identity only and MUST NOT select or override a producer. Every returned record states which model produced it.

Reasons:

- DR-014 fixes the producer per horizon; Issue #132 forbids API model selection or changes to that mapping.
- The research comparison is horizon-specific (DR-013), and DR-014 designates exactly one producer per horizon.
- Consumers may request all four forecasting horizons for the same series. This capability does not approve 28-day inventory interpretation or human-review triggers; those remain subject to B8 and the relevant component owners.
- Model identity remains visible in every record (`model`, `configuration_id`), so the four-model design stays traceable.

## 4. Frozen producer mapping

Copied unchanged from [DR-014](decisions/DR-014-forecasting-selection-and-final-refit.md#separate-downstream-forecasting-framework-producer-decision). This contract does not change it.

| Horizon | Producer model | Configuration | Training rows (eligible) | Target interval |
|---:|---|---|---:|---|
| 1 | LightGBM | GBM018 | 77,250 | 2024-12-03 to 2024-12-03 |
| 7 | LightGBM | GBM011 | 75,750 | 2024-12-03 to 2024-12-09 |
| 14 | XGBoost | GBM022 | 74,000 | 2024-12-03 to 2024-12-16 |
| 28 | XGBoost | GBM003 | 70,500 | 2024-12-03 to 2024-12-30 |

The mapping identifies the intended downstream producer for each horizon. It does not declare a universal best model. The final evaluation records that other candidates had lower final WAPE at some horizons, and that the mapping was frozen before final evaluation and is not reselected from final results ([final evaluation](forecasting-final-evaluation.md)). The other 24 final candidates remain research evidence and MUST NOT be served as prospective forecasts.

## 5. Forecast meaning

Definitions come from the [protocol](protocol.md#2-frozen-target-predictor-information-and-ordering) and [integration readiness](integration-contract-readiness.md#4-origin-horizon-and-target-window-meaning).

| Concept | Meaning |
|---|---|
| Series | One `SKU_ID` + `Warehouse_ID` pair (DR-002 grain) |
| Forecast origin `o` | The last date whose demand history is available to the forecaster: 2024-12-02 |
| Horizon `h` | One of 1, 7, 14, 28 (DR-004). 28 days is four weeks, not a calendar month and not a lead-time estimate |
| Target interval | `o+1` through `o+h`, both inclusive. `target_start_date` = 2024-12-03 for every horizon |
| Forecast value | Predicted `Units_Sold` for the target interval: **next-day units** for `h = 1`, and **cumulative units over the whole interval** for `h = 7, 14, 28` |

Rules:

1. A 7-, 14- or 28-day value is a single cumulative total. The export MUST NOT divide it into daily values or reinterpret it as a daily forecast. No daily path is implied (direct strategy, DR-008).
2. Forecast origin and target start are different fields. `target_start_date` MUST NOT be presented as the origin.
3. Forecast values are raw model outputs: copied unchanged, not rounded, clipped or floored. Zero remains zero. Non-finite or malformed quantities make the source unusable; they MUST NOT be repaired or replaced. Inventory handling of problematic forecasts remains a separate owner decision (B5); this contract authorizes no new source run.
4. Display rounding is presentation only. It MUST NOT change the value passed to downstream components.

## 6. Prospective forecast record

Each record represents one series and one horizon. The export holds 250 series × 4 horizons = **1,000 records**.

| Field | Type | Meaning | Source |
|---|---|---|---|
| `SKU_ID` | string | Product identifier | `predictions.json` |
| `Warehouse_ID` | string | Warehouse identifier | `predictions.json` |
| `forecast_origin` | date (ISO 8601, `YYYY-MM-DD`) | Last date of demand history used | `predictions.json` |
| `horizon` | integer, one of 1/7/14/28 | Forecast horizon in days | `predictions.json` |
| `target_start_date` | date | First day of the target interval (`o+1`) | `predictions.json` |
| `target_end_date` | date | Last day of the target interval (`o+h`) | `predictions.json` |
| `forecast_type` | string: `next_day` or `cumulative_window` | Whether the value is next-day demand or a cumulative total | Derived from `horizon` (Section 5) |
| `prediction` | number | Raw forecast of `Units_Sold` for the target interval | `predictions.json` (approved D1 choice) |
| `unit` | string: `units` | Unit of `prediction` (`Units_Sold`) | Fixed |
| `model` | string | Producer model family | `predictions.json` |
| `configuration_id` | string | Frozen producer configuration | `predictions.json` |
| `producer_status` | string: `designated_producer` | Confirms the DR-014 producer for this horizon | Derived from Section 4 |
| `forecast_status` | string: `available` | Status of this record (Section 9 lists unavailable cases) | Derived |
| `uncertainty` | object | `{"status": "unavailable", "reason": "no_agreed_method"}` (approved D3 choice) | Fixed until an uncertainty method is approved (B11) |

Dates are timezone-naive calendar dates in ISO 8601 / RFC 3339 `full-date` form. JSON follows RFC 8259.

### 6.1 Export-level provenance

The export is one JSON object with a top-level `forecasts` array containing the Section 6 records. The export-level fields below are siblings of `forecasts`; `source` is a nested object and `producers` is an array. Shared provenance appears once and is not repeated in each forecast record.

| Field | Meaning |
|---|---|
| `export_schema` | Contract identifier, `issue-132-forecast-export-v1` (approved D4 choice) |
| `source.run_id`, `source.evaluation_stage`, `source.source_schema` | Source identity (Section 2) |
| `source.run_manifest_path`, `source.run_manifest_sha256` | Completion authority and its hash |
| `source.prediction_receipt_sha256` | Sealed prediction receipt hash |
| `source.integrity_result` | Existing recorded integrity result, copied unchanged from the pinned completion manifest and checked against metadata; not recalculated at export time |
| `forecast_origin`, `training_start`, `training_end` | Temporal policy of the source run |
| `producers[]` | For each horizon: `model`, `configuration_id`, `forecast_type` and a `model_reference` with repository-relative paths and SHA-256 hashes of the model, descriptor, fitted preprocessing and origin features, as recorded in `candidates.json` |
| `series_count`, `record_count` | 250 and 1,000 for the current source |
| `forecasts[]` | Section 6 prospective records, sorted by `horizon`, then `SKU_ID`, then `Warehouse_ID`; exactly `record_count` entries |

Model references let a reviewer trace each value back to the exact fitted model and preprocessing, in line with W3C PROV (entity → activity → agent), the FAIR principles and model-card practice (Section 13). The retained export exposes these references read-only and does not execute models. The active inference API loads the bound saved models at startup and invokes them on supplied request history, as specified in its separate contract.

### 6.2 Fields excluded from prospective views

These are retrospective research evidence. They MUST NOT appear in the export or in any prospective API response ([protocol](protocol.md) Section 14; [integration readiness](integration-contract-readiness.md#5-retrospective-evidence-versus-prospective-inputs)):

- `observed_target` and any `target_1_day` … `target_28_day` label;
- `wape`, `mae`, `rmse`, `bias`, `wape_denominator`, `metric_status` and any signed or absolute error;
- `fold_id`, validation selection/tie fields, and rows from non-producer candidates;
- source `Demand_Forecast` and any future inventory or operational value.

A retrospective performance view, if ever wanted, needs a separate contract that is clearly labelled as evaluation evidence.

## 7. Example records

Values below are illustrative placeholders, not numbers taken from the run.

```json
{
  "SKU_ID": "SKU_1",
  "Warehouse_ID": "WH_1",
  "forecast_origin": "2024-12-02",
  "horizon": 7,
  "target_start_date": "2024-12-03",
  "target_end_date": "2024-12-09",
  "forecast_type": "cumulative_window",
  "prediction": 0.0,
  "unit": "units",
  "model": "lightgbm",
  "configuration_id": "GBM011",
  "producer_status": "designated_producer",
  "forecast_status": "available",
  "uncertainty": {"status": "unavailable", "reason": "no_agreed_method"}
}
```

A request for all horizons of one series returns four such records, ordered by horizon 1, 7, 14, 28. Each has its own `model`, `configuration_id`, `target_end_date` and `forecast_type`.

## 8. Earlier retained-export lookup operations (superseded for runtime)

These describe behaviour, not final URLs. Tinosh chooses route names, response models and framework details, and the forecasting owner reviews them for meaning.

| Operation | Inputs | Result |
|---|---|---|
| Get forecasts for a series | `sku_id`, `warehouse_id`; optional `horizon`, `forecast_origin`, `model`, `configuration_id` | One record for the requested horizon, or four records when `horizon` is omitted; unavailable/rejected requests follow Section 9 |
| Get producer mapping and provenance | none | The Section 4 mapping and the Section 6.1 provenance block |
| Health / source status | none | Whether the configured source export is present and matches its pinned export SHA-256 (Section 11), with the Section 2 binding/schema checks recorded; reports recorded scientific verification separately and never returns forecast values |

`sku_id` and `warehouse_id` are exact source identifier strings. `forecast_origin`, when supplied, is an ISO calendar date; omission means the retained origin `2024-12-02`. Any other valid date returns `unavailable_forecast`, without generating a prediction or substituting the retained origin. A `forecast_origin` that is not a valid ISO calendar date (for example `2024-13-45` or `abc`) returns `invalid_request`. These typed logical inputs do not specify HTTP parsing or framework validation.

Optional `model` and `configuration_id` are exact source identifiers used solely as assertions. Each supplied assertion must match every requested horizon's designated producer. When `horizon` is omitted, the requested set is all four horizons; an assertion matching only some of them is rejected with `non_designated_producer`, not used to filter the response. Omitting both assertions resolves producers directly from DR-014.

These logical operations are read-only. HTTP methods, routes, status codes, error-body formats and framework response models are deferred to Tinosh's later implementation and shared architecture review. They are not selected by Issue #132.

## 9. Retained-export unavailable and lookup behaviour

The API MUST NOT substitute another value, model, horizon, run or series when a forecast is unavailable. Missing values MUST NOT be shown as zero or `false` (DR-011).

| Reason code | When | Forecast behaviour |
|---|---|---|
| `invalid_request` | A supplied `forecast_origin` is not a valid ISO calendar date | Reject the request; no substitute origin or forecast quantity |
| `unknown_sku` | The SKU is absent from the source's declared pair roster | Unavailable; no forecast quantity |
| `unknown_warehouse` | The warehouse is absent from the source's declared pair roster | Unavailable; no forecast quantity |
| `unknown_series` | Both identifiers are known, but their pair is absent from the declared roster | Unavailable; no forecast quantity |
| `unsupported_horizon` | A supplied `horizon` is not an integer (excluding booleans) in 1, 7, 14 or 28 | Reject the request; no interpolation or forecast quantity |
| `non_designated_producer` | A supplied model/configuration assertion does not match the DR-014 producer for every requested horizon | Reject the request; no substitute producer or partial response |
| `unavailable_forecast` | The requested origin has no forecast in the accepted fixed-origin export | Unavailable with a reason; no substitute origin or quantity |
| `source_unverified` | Required evidence is missing, changed, malformed, inconsistent or incomplete under Section 2 | Fail export/consumption; serve no forecasts from that source |

A missing expected producer record at the retained origin is incomplete source evidence (`source_unverified`), not an ordinary lookup miss. A failed source MUST NOT produce a partial successful export. Logical unavailable/rejected results carry the reason code and no forecast quantity; zero MUST NOT stand in for absence. Transport representation remains Tinosh's responsibility.

Reason-code precedence is deterministic. A missing or unusable source returns `source_unverified`; lookup checks use only an accepted source. For a valid source, return the first applicable code in this order:

1. `invalid_request`;
2. `unsupported_horizon`;
3. `non_designated_producer`;
4. `unknown_sku`;
5. `unknown_warehouse`;
6. `unknown_series`;
7. `unavailable_forecast`.

The current source is the complete 50-SKU × 5-warehouse grid, so `unknown_series` cannot occur when both identifiers are known. It is retained as a defensive lookup condition. An isolated lookup test may use a synthetic non-Cartesian roster with complete records for every declared pair. Such a test does not permit an incomplete real export or change the required 250-pair population.

Valid comparator rows in the full 28-candidate source are excluded during producer filtering. Their presence is expected and is not a source failure; explicitly requesting one as the designated producer is rejected.

These codes cover forecasting availability only. Mapping them to the DR-011 unavailable-state vocabulary ("no agreed method", "not applicable", "waiting on another component") is Dewmi's decision under blocker B9.

## 10. Shared forecasting API boundaries

From Issue #132 and the [system integration workflow](workflows/system-integration-and-prototype.md):

1. The API MUST NOT train, refit, tune or select models. The active [inference API](forecast-inference-api.md) invokes only the four bound saved producers on supplied request history. The retained exporter remains a read-only projection and MUST NOT execute model inference.
2. The API MUST NOT compute research metrics or expose retrospective outcomes or errors in prospective views.
3. The API MUST NOT reinterpret cumulative forecasts as daily forecasts.
4. The API MUST NOT change the producer mapping or serve non-producer candidates as forecasts.
5. Inventory-risk, replenishment and decision-support logic stay outside the forecasting contract.
6. Carrying 28-day forecasts does not approve 28-day inventory interpretation or review triggers (B8).
7. The API is advisory and presentation-oriented. Nothing it returns is a purchase order.

## 11. Export storage and reproducibility

The export is a deterministic projection of the recorded verified bundle:

1. Check the independently pinned source anchor and retained file bindings (Section 2); do not rerun scientific verification.
2. Read `predictions.json` and keep only the four producer `(model, horizon, configuration_id)` combinations, matching the frozen mapping in Section 4 and retained metadata.
3. Validate exact run/producer identity, SKU/warehouse membership, origin `2024-12-02`, integer horizons, inclusive target dates and finite stored quantities. Within the filtered producer rows, each `(run_id, SKU_ID, Warehouse_ID, forecast_origin, horizon)` must be unique. The full 28-candidate source may share that key across different models/configurations.
4. Construct records using an explicit allowlist of Section 6 fields and the listed derived fields. Construct shared provenance using the Section 6.1 allowlist; do not copy whole source records or arbitrary nested metadata. Section 6.2 fields are excluded at every level.
5. Sort by `horizon`, then `SKU_ID`, then `Warehouse_ID`; validate the exact roster and four horizons per series. The count must equal 250 × 4 = 1,000; count alone is insufficient. Missing, duplicate or invalid records stop export with `source_unverified`.
6. Serialize with fixed key ordering/formatting and no NaN/infinity or changing export-time timestamps. Copy stored quantities and the recorded integrity result unchanged.
7. Write outside retained evidence, without overwriting, and record the derivative export's SHA-256 separately.

The derivative export's SHA-256 is recorded in this contract as an accepted-export entry (path, `export_schema`, source run and hash) after owner-authorized generation, and is included in the Issue #132 handoff. Any consumer of this retained export must pin that reviewed value. Before serving retained records, that consumer MUST compare the exact export bytes with the pinned hash; a missing export, missing pin or mismatch returns `source_unverified`. The active inference API does not consume the export; it pins the saved-model source manifest and receipt instead. The expected hash MUST NOT be read from the export itself or from a file stored beside it, and MUST NOT be silently refreshed.

The same verified source always gives byte-identical output. The export stays local and ignored by Git (`.gitignore` already covers `data/processed/` and `artifacts/`). Do not commit generated output. Ignore coverage alone does not establish storage approval. The D2 location is now covered by the reviewed [storage-policy row](artifact-storage-policy.md#storage-responsibilities); generating a real export still requires the authorization below.

Generating the real derivative export requires explicit owner authorization covering the named run, pinned manifest and approved destination. An existing authorization covering that same operation remains sufficient; do not request it again. Synthetic tests use temporary synthetic evidence only and do not require real-bundle execution authorization. Neither contract review nor exporter execution authorizes training, refitting, prediction generation or metric recalculation.

## 12. Owner-approved contract choices

Owner approval: Chathuranga, 2026-10-05, by explicit instruction in the working session to adopt D1–D5, add the narrow storage-policy allowance and update the readiness reference. This approval covers the contract choices and documentation changes; it does not authorize a real export run or approve an implementation that has not yet been reviewed.

| ID | Decision | Approved choice |
|---|---|---|
| D1 | Forecast value field | Keep `prediction`, copied unchanged from the evidence; `forecast_type` and `unit` define its meaning. |
| D2 | Export location | `data/processed/forecasting/handoffs/final-20261003-02/issue-132-forecast-export-v1.json`, covered by the narrow [storage-policy row](artifact-storage-policy.md#storage-responsibilities). Generated output stays local/ignored and outside retained evidence. |
| D3 | Uncertainty in records | Explicit `unavailable` with `no_agreed_method`; no uncertainty method is introduced or B11 resolved. |
| D4 | Contract identifier | `issue-132-forecast-export-v1`. |
| D5 | Decision record | Record these choices here and reference this contract in [integration readiness](integration-contract-readiness.md). No new Decision Record. |

The logical request behaviour and reason-code precedence in Sections 8–9 are part of this approved contract. Chathuranga retains forecasting ownership; Tinosh reviews and implements the consumer. Exporter implementation and synthetic checks are complete, and the owner generated a local derivative export. Its accepted-export hash entry and consumer acceptance remain pending; existence alone does not establish acceptance. The active inference handoff has separate review and manual demonstration steps in [its contract](forecast-inference-api.md).

Posting a decision comment on Issue #132 requires the owner's instruction; this documentation approval does not authorize posting one.

## 13. Standards and references

Standards and conventions this contract follows. Bibliographic details should be checked before any of these are cited in the academic report, following the practice in [references](references.md).

| Standard / source | Used for |
|---|---|
| RFC 2119 and RFC 8174 — requirement key words | MUST / SHOULD / MAY wording |
| RFC 8259 — JSON; RFC 3339 / ISO 8601 — dates | Data and date formats |
| W3C PROV-DM / PROV-O | Provenance structure (source run → fitted model → forecast) |
| Wilkinson et al. (2016), FAIR Guiding Principles, *Scientific Data* | Traceable, reusable research outputs |
| Mitchell et al. (2019), Model Cards for Model Reporting | Stating model identity, intended use and limitations with outputs |
| Hyndman and Athanasopoulos, *Forecasting: Principles and Practice* (3rd ed.) | Forecast origin, horizon and multi-step terminology |

Project sources: [AGENTS.md](../AGENTS.md), [DR-002](decisions/DR-002-forecasting-analytical-unit.md), [DR-004](decisions/DR-004-forecast-horizons.md), [DR-008](decisions/DR-008-multi-step-forecasting-strategy.md), [DR-011](decisions/DR-011-decision-support-output-structure.md), [DR-014](decisions/DR-014-forecasting-selection-and-final-refit.md), [protocol](protocol.md), [final evaluation](forecasting-final-evaluation.md), [storage policy](artifact-storage-policy.md), [runner operations](forecasting-runner.md), [integration readiness](integration-contract-readiness.md), [system integration workflow](workflows/system-integration-and-prototype.md).

## 14. Retained-export handoff to Tinosh

For retained-export consumption only; active API responsibilities and acceptance steps are recorded in [the inference handoff](forecast-inference-api.md#7-engineering-handoff):

| Party | Responsibility |
|---|---|
| Chathuranga | Owns this contract, export and forecasting meaning; retains shared API architecture/integration design with Tinosh and reviews forecasting-facing behaviour, provenance, origin/horizon and unavailable states. |
| Tinosh | Implements the export consumer, endpoints, response schemas, error handling and API tests under this contract. Does not change the mapping, meaning or excluded fields. |
| Didilani / Dewmi | Consume the approved meaning. Their own schemas, unavailable-state vocabulary and 28-day decisions stay with them. |

Focused synthetic exporter tests for Issue #132 MUST check the following. Tinosh later adds API/integration tests preserving these invariants:

- four records per declared synthetic series; the real source separately requires exactly 250 series and 1,000 records;
- `target_start_date` = origin + 1 and `target_end_date` = origin + h;
- the DR-014 producer for each horizon;
- `forecast_type` matches the horizon;
- no field from Section 6.2 appears anywhere in a response;
- deterministic ordering/serialization and unchanged raw stored quantities;
- the independent manifest anchor, consumed-file hashes and recorded verification result;
- malformed/incomplete evidence, duplicate identities and invalid intervals;
- exact producer filtering, with comparator rows excluded rather than treated as source corruption;
- the reason codes and precedence in Section 9 wherever the tested interface implements the corresponding lookup, including unknown identifiers, unavailable origin and failed model/configuration assertions;
- the defensive `unknown_series` condition in an isolated synthetic lookup fixture, without relaxing real-export completeness;
- no outcome reads, model fitting/inference/replay or research-metric recalculation.

Tests SHOULD use synthetic fixtures. Any use of real run outputs follows the verification rule in Section 2.

## 15. Limitations

- The dataset downloaded from Kaggle is simulated by its publisher. Forecasts do not describe a real retailer ([dataset](dataset.md)).
- The retained export has one fixed origin (2024-12-02). This limitation belongs to that artifact; the active inference API computes from a supplied origin and daily history.
- The final interval was not fully unseen: December 3–16 had earlier validation exposure, and full-year exploratory analysis inspected the interval ([final evaluation](forecasting-final-evaluation.md)).
- No forecast uncertainty is available (B11).
- `Stockout_Flag` is zero-variance and plays no part in this contract.
- Forecasts are advisory decision-support inputs, not executable purchase orders.
