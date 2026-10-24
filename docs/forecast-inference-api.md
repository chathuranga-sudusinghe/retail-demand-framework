# Request-time forecast API and presentation inputs

**Responsible member:** Chathuranga — forecasting meaning and shared API architecture.
**Integration reviewer:** Tinosh — endpoint, schema and adapter acceptance.
**Date:** 2026-10-05 (Asia/Colombo).
**Status:** Implementation and four synthetic JSON examples are merged through [PR #151](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/151); #132 is closed. Chathuranga supplied revised-example manual outcomes on 24 October 2026 under [Issue #180](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/180); see Section 6.1 for evidence and limits. Tinosh's consumer acceptance remains pending. The API is a presentation prototype, not completed group-wide integration.

## 1. Active serving behavior

The presentation flow is:

`example JSON daily history → POST /forecasts → frozen input pipeline → saved model.predict() → forecast response`

Models and their saved preprocessing are loaded once at application startup. Every accepted request builds its own feature vector and invokes the designated model. Responses are not cached. The existing [retained forecast export](forecast-api-contract.md) is a separate fixed-origin artifact: the runtime neither opens it nor reads stored predictions, observations or metric files.

This behavior requested by Chathuranga supersedes the earlier stored-forecast serving proposal. It preserves the existing feature definitions, saved preprocessing, model files and producer mapping. Chathuranga and Tinosh retain their documented ownership; this initial implementation is subject to their review.

### 1.1 Research and demonstration scope

**Scope confirmed by Chathuranga on 2026-10-05:** this API is a presentation prototype demonstrating request-time inference with the existing saved models. The main research task is to address the research questions and hypotheses through the documented analytical evidence. The API is a delivery mechanism within that project; it introduces no research method or hypothesis.

The FastAPI service demonstrates request-time inference using the saved forecasting models and synthetic historical inputs. Research conclusions are based on the documented analytical evidence in [research design](research-design.md) and the existing reports. Successful API responses demonstrate software integration only; they do not establish forecasting accuracy, generalisation, inventory-decision effectiveness, or acceptance/rejection of the research hypotheses.

The demonstration preserves the research questions, hypotheses, targets, feature definitions, producer mapping, saved models and retained numerical evidence. Synthetic requests and their responses are illustrative presentation material and must be labelled accordingly in slides and recordings. Changing an example input does not create an additional research result. The API neither establishes replenishment quantities nor approves downstream 28-day use.

**Historical preparation instruction — 5 October 2026:** Chathuranga authorised preparing the demo on its then-existing feature branch; prior Tinosh review was not required for preparation. That instruction is not standing Git authorisation. The implementation is now merged; component ownership and remaining consumer acceptance are unchanged.

## 2. Models and source bindings

Only saved producers from `final-20261003-02` are eligible:

| Horizon | Saved model | Configuration | Output meaning |
|---:|---|---|---|
| 1 | LightGBM | GBM018 | Next-day demand |
| 7 | LightGBM | GBM011 | Cumulative 7-day demand |
| 14 | XGBoost | GBM022 | Cumulative 14-day demand |
| 28 | XGBoost | GBM003 | Cumulative 28-day demand |

The independently pinned source manifest and receipt hashes are unchanged from [the retained-export contract, Section 2](forecast-api-contract.md#2-source-evidence). Startup checks their exact bytes, source identity, completion metadata, mapping and manifest/receipt bindings. Each selected model, descriptor, preprocessing state and retained origin-feature reference must match those bindings. Origin-feature files are hashed only; request features always come from supplied history.

The saved preprocessing is restored and used as-is. The native model loader receives the exact checked model bytes. No user-controlled file path, uploaded model, alternate run or producer selection is accepted. Source inspection uses existing read-only helpers in `src/forecasting/export.py`; it never invokes the exporter or scientific verifier functions. No retained artifact is modified.

## 3. Request contract

Submit one SKU–warehouse pair and one horizon per request:

| Field | Type / rule |
|---|---|
| `SKU_ID` | Exact known, unpadded saved-model identifier |
| `Warehouse_ID` | Exact known, unpadded saved-model identifier |
| `forecast_origin` | Valid `YYYY-MM-DD` calendar date, at or after the saved-model boundary `2024-12-02` |
| `horizon` | JSON integer 1, 7, 14 or 28; booleans and numeric strings rejected |
| `input_kind` | `synthetic_demo` or `supplied_history`; default `supplied_history` |
| `history` | 28–366 consecutive daily objects containing only `Date` and `Units_Sold` |
| `history[].Date` | Unique valid `YYYY-MM-DD` calendar date |
| `history[].Units_Sold` | Nonnegative JSON integer; no missing, fractional, string or boolean values |

History must end exactly at the forecast origin, with no gaps, duplicates or later dates. Input order may vary: the existing pipeline sorts by date. At least 28 days are needed by the frozen lag and rolling features. The 366-row maximum bounds this local demo request; it does not change feature definitions.

Extra fields are rejected, including model/configuration overrides, `Demand_Forecast`, `observed_target`, future labels and inventory variables. Models retain their original SKU and warehouse vocabularies; arbitrary new identifiers are not supported.

## 4. Response contract

A successful response is one `ForecastResponse`, with an explicit field allowlist in [the API source](../src/api/main.py):

- `inference_schema`: `forecast-inference-v1`; `inference_mode`: `request_time`; `input_kind`;
- `model_source_run_id`, `manifest_reference`, `manifest_sha256`;
- `SKU_ID`, `Warehouse_ID`, `forecast_origin`, `horizon`;
- `target_start_date` = origin + 1; `target_end_date` = origin + horizon, inclusive;
- `forecast_type`: `next_day` for 1, `cumulative_window` for 7/14/28;
- `forecast_quantity`: finite raw model output in `Units_Sold` units, with no clipping or rounding;
- `model`, `configuration_id`, `producer_designation`: `frozen_designated_producer`;
- `provenance`: saved model/preprocessor paths and hashes, plus `input_sha256` of canonical supplied input;
- `status`: `available`; `unavailable_reasons`: empty on success;
- `assumptions`, `limitations`.

The source run identifies the saved model, while the request origin identifies this newly computed forecast. They are separate identities. The input hash records the supplied history and request fields; no export-time timestamp changes it. There is no actual outcome or error metric in the response. Forecast uncertainty is unavailable because no agreed uncertainty method exists; this demo supplies no confidence interval. A successful `status` and empty `unavailable_reasons` indicate a finite point forecast, not an uncertainty estimate. Quantity units are units sold for the stated target interval.

A multi-day result is one cumulative quantity, not a per-day path. A finite negative model output is returned unchanged. Inventory interpretation, replenishment, responsible decision support and approval of 28-day downstream use remain outside this API.

## 5. Unavailable behavior

| Situation | HTTP status | Domain reason |
|---|---:|---|
| Malformed request, extra fields, invalid calendar date or scalar types | 422 | Standard FastAPI request-validation detail |
| Unsupported integer horizon | 422 | `unsupported_horizon` |
| Unknown SKU / warehouse | 422 | `unknown_sku` / `unknown_warehouse` |
| Origin before the saved-model boundary | 422 | `invalid_origin` |
| Duplicate, gapped or otherwise invalid history | 422 | `invalid_history` |
| History extends past origin | 422 | `future_history` |
| History does not end at origin / incomplete feature window | 422 | `incomplete_history` |
| Missing, changed or inconsistent source artifacts | 503 | `source_unverified` |
| Model failure, non-finite quantity or wrong output shape | 503 | `unavailable_forecast` |

Schema checks run first. Once parsed, an unavailable source takes precedence; otherwise domain checks follow horizon → SKU → warehouse → origin/history → model output. Errors contain no substitute forecast quantity.

`GET /health` reports `ready` only after all four producers load successfully; otherwise it reports `unavailable` with `source_unverified`. Health describes source readiness, not a new prediction. Interactive documentation remains available when local artifacts are absent.

### 5.1 Retained decision-support cases

The retained fixed-origin cases are served separately from request-time inference:

| Method and path | Result |
|---|---|
| `GET /decision-support/cases` | The existing 20-case F01–F20 decision-support roster |
| `GET /decision-support/cases/{assessment_id}` | One exact retained case, selected by its existing ID such as `F01` |

These routes do not call `POST /forecasts`, run a model, prepare or assess records, or expand the roster to the 1,000-key upstream forecast population. An unknown assessment ID returns HTTP 404 with `reason_code: unknown_case`; a missing, changed or inconsistent source returns HTTP 503 with `reason_code: source_unverified`.

Each returned case contains the original `assessment_id`, integer `horizon` and unchanged `record` object, alongside a separately identified `prospective_record` projection. The record retains the existing `DecisionSupportRecord` fields, including `not_assessed`, assumptions, limitations, unavailable-field reasons and component provenance. The projection preserves the validated source identity (`SKU_ID`, `Warehouse_ID`, `forecast_origin`, `horizon`), inclusive `target_start_date` / `target_end_date`, raw `prediction` and unit, producer/configuration, run/evaluation provenance, `evidence_role`, source hash/provenance, forecast-input and downstream-use statuses/reasons, methodology status, assumptions and limitations.

For h1, h7 and h14 only, the projection also retains the existing inventory evidence fields: `Date`, `Inventory_Level`, `Reorder_Point`, source snapshot availability/status/reason, source/scenario/analysis availability, inventory basis and snapshot assumption, exposure states, buffer and predicted margin. Null, zero, false, unknown and source reasons remain distinct. A matching date alone does not establish source snapshot availability. h1 remains next-day demand; h7/h14 remain cumulative-window quantities, not daily paths.

For h28, the forecast case remains available for forecast transparency, but `prospective_record` omits all inventory quantity, snapshot, buffer and exposure fields. The existing `downstream_use_status` and `downstream_use_reason` remain visible, including `28_day_downstream_use_requires_separate_approval`; the original record's unavailable-field reason is preserved. This route does not approve h28 inventory use.

The response excludes source `Demand_Forecast`, `Stockout_Flag`, observed/future targets, realised `Units_Sold`, retrospective margins/errors, confusion cells, TP/TN/FP/FN, evaluation metrics, and decoded contents of `evaluation.json` or `review.json`. The inventory loader retains its existing behavior of verifying the manifest-bound companion bytes without decoding retrospective results. The decision-support loader verifies the reviewed retained manifest and record hashes, source-export binding, exact 20-case roster, and wrapper/nested identity and horizon agreement before returning any case; no case is substituted when a requested source key is absent.

The service requires the retained forecast export, the decision-support `records.json` / `manifest.json`, and a byte-identical local copy of the complete inventory evaluation bundle under `research-materials/inventory-risk/issue-164/evaluation-v1/`. The copy must preserve filenames and bytes so the existing inventory loader can verify all companion hashes. It is not generated by the API. If any required source is absent or fails validation, retained-case requests remain unavailable; `POST /forecasts` and its model lifecycle remain independent.

## 6. Manual presentation

From the repository root, install the configured dependencies and start the local API:

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs`, select `POST /forecasts`, and choose a horizon example. Each example supplies invented daily demand for the known `SKU_1` / `WH_1` pair over 2025-01-01 through 2025-01-28, explicitly labelled `synthetic_demo`. These are new illustrative inputs, not measurements from a retailer or copies of stored forecast outputs.

All four examples share the same 28-day history; only the requested horizon changes. The hand-authored daily `Units_Sold` values range from 11 to 20 (mean 15.29). This is an illustrative scale close to the retained `SKU_1` / `WH_1` origin-history 28-day mean of 15.25. That recorded rolling mean supplies scale context; it is not the full historical daily-sales range or an approved accuracy threshold. The example values are invented rather than copied from retained research rows.

The 28-day history requirement comes from the existing lag and rolling features, independently of the requested 1/7/14/28-day horizon. Historical `Units_Sold` is supplied through the origin; future sales are unknown. Model responses remain raw and are not rescaled to match the example history.

| File | Origin | Target interval |
|---|---|---|
| [1-day](../examples/forecast-api/forecast-1-day.json) | 2025-01-28 | 2025-01-29 |
| [7-day](../examples/forecast-api/forecast-7-day.json) | 2025-01-28 | 2025-01-29 … 2025-02-04 |
| [14-day](../examples/forecast-api/forecast-14-day.json) | 2025-01-28 | 2025-01-29 … 2025-02-11 |
| [28-day](../examples/forecast-api/forecast-28-day.json) | 2025-01-28 | 2025-01-29 … 2025-02-25 |

If the API is already running when an example file changes, stop it with `Ctrl+C` and restart it using the command above. Swagger examples are read at application import, so restarting and refreshing `/docs` displays the revised inputs.

From a second WSL terminal, submit the files manually, one at a time:

```bash
curl --fail-with-body http://127.0.0.1:8000/forecasts -H 'Content-Type: application/json' --data-binary @examples/forecast-api/forecast-1-day.json
curl --fail-with-body http://127.0.0.1:8000/forecasts -H 'Content-Type: application/json' --data-binary @examples/forecast-api/forecast-7-day.json
curl --fail-with-body http://127.0.0.1:8000/forecasts -H 'Content-Type: application/json' --data-binary @examples/forecast-api/forecast-14-day.json
curl --fail-with-body http://127.0.0.1:8000/forecasts -H 'Content-Type: application/json' --data-binary @examples/forecast-api/forecast-28-day.json
```

Check the returned origin, target interval, producer and `inference_mode`. Modify a supplied demand value and resubmit to demonstrate that the model receives changed inputs. Tree models can return the same quantity for different inputs; an unchanged number alone does not imply a cached response.

This is a local presentation service. Start it on the loopback address above. Deployment, authentication and other components are separate integration tasks.

### 6.1 Manual verification evidence — 24 October 2026

**Task:** [#180](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/180), related to [#179](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/179).
**Human executor:** Chathuranga; commands and responses were pasted into the working conversation. Codex compared the supplied outputs with this contract. This records execution and inspection, not formal producer approval or Tinosh's technical consumer acceptance.
**Environment:** local WSL/Bash, existing repository, branch `test/forecast-prototype-handoff`, HEAD `22e12b9b1da170feab50cf3028b59917646e5b30`; API started with `.venv/bin/python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000`. Installed Python/package versions were not captured in the supplied output.

#### Source identity checks

Chathuranga manually ran:

```bash
python3 -B -m src.data.verify_checksums --profile tinosh
python3 -B -m src.data.verify_checksums --profile dewmi
```

| Check | Supplied result |
|---|---|
| `tinosh` profile | 20/20 registered inference files matched: run manifest, metadata, prediction receipt, candidates and four sets of model/descriptor/preprocessor/origin-feature files |
| `dewmi` profile | 1/1 matched: retained `issue-132-forecast-export-v1.json` under `data/processed/forecasting/handoffs/final-20261003-02/` |
| Missing or changed selected files | None reported |
| Reference | `docs/checksums/2026-10-06.json`, matching local HEAD `22e12b9b1da170feab50cf3028b59917646e5b30` |
| Reference SHA-256 | `381ed9607a9e3ec155ee3754d699d62873bfbff18f5e1f4edc31c407267ed7cc` |

Both outputs explicitly reported **provisional local matches**: tracked content and independent reference review were not checked. These checks read selected bytes only; files outside the two profiles remain unverified. No full retained-bundle scan or scientific verification was run. Complete trusted handoff verification using an independently reviewed reference commit and the [checksum guide](checksums/README.md); do not infer review from a local HEAD match.

#### Health and four existing examples

Chathuranga ran `curl -i --fail-with-body http://127.0.0.1:8000/health`. At 07:27:23 Asia/Colombo, the supplied HTTP 200 response reported `ready`, horizons `[1,7,14,28]` and no unavailable reasons.

For each POST, he used the corresponding Section 6 file command with `curl -i --fail-with-body`; `-i` additionally printed HTTP response headers. All requests used `SKU_1` / `WH_1`, origin `2025-01-28`, `input_kind: synthetic_demo` and the same invented 28-day history.

| Example | HTTP status | Producer | Inclusive target interval | Raw forecast quantity (units) | Supplied result |
|---|---|---|---|---:|---|
| `forecast-1-day.json` | 200 | LightGBM `GBM018` | 2025-01-29 | 13.83799223799719 | `next_day`, `available` |
| `forecast-7-day.json` | 200 | LightGBM `GBM011` | 2025-01-29 through 2025-02-04 | 90.0643865572258 | `cumulative_window`, `available` |
| `forecast-14-day.json` | 200 | XGBoost `GBM022` | 2025-01-29 through 2025-02-11 | 181.0713348388672 | `cumulative_window`, `available` |
| `forecast-28-day.json` | 200 | XGBoost `GBM003` | 2025-01-29 through 2025-02-25 | 349.0440673828125 | `cumulative_window`, `available`; pasted response ending truncated |

All four supplied responses showed `forecast-inference-v1`, `inference_mode: request_time`, source run `final-20261003-02`, the designated producer, model/preprocessor references and an empty `unavailable_reasons` list. The 28-day producer, quantity, dates and availability were visible, but its complete final limitations text was not captured; do not claim full response capture for that case.

#### Changed-history check

Chathuranga manually submitted this request, changing the final historical `Units_Sold` from 15 to 20 in memory. The increment of five was an illustrative input change, not a research threshold. The original example file was not rewritten.

```bash
.venv/bin/python - <<'PY' | curl --fail-with-body http://127.0.0.1:8000/forecasts -H 'Content-Type: application/json' --data-binary @-
import json
from pathlib import Path

payload = json.loads(Path("examples/forecast-api/forecast-1-day.json").read_text())
payload["history"][-1]["Units_Sold"] += 5
print(json.dumps(payload))
PY
```

| Field | Original example | Modified request |
|---|---|---|
| `forecast_quantity` | `13.83799223799719` | `13.864131443279389` |
| `provenance.input_sha256` | `0685fa833140b464a3390e226aaf187d744c706a2b8cb290268522931c16ec58` | `c52bcbd52733897b46342ccbb3ef40bcb60891b6810f3dc23bb7d5df288cc93c` |

The modified response retained LightGBM `GBM018`, origin `2025-01-28`, next-day target `2025-01-29`, saved model/preprocessor hashes, `request_time` and `available`. Changed input provenance and quantity are consistent with processing the modified request. This check complements existing synthetic call/matrix checks; different valid inputs do not always produce different tree-model predictions.

These manual requests demonstrate serving only. They did not train, tune, refit, replay research evaluation, measure accuracy or accept downstream inventory/decision-support behaviour. The live January examples must not be joined to inventory/decision-support results from the retained origin `2024-12-02` as though those results had recomputed. Existing synthetic rejection/failure coverage in `tests/test_forecast_api.py`, `tests/test_forecasting_inference.py` and `tests/test_forecasting_export.py` was inspected for reuse; these manual requests do not exercise those failure cases, and that suite was not rerun for this record.

## 7. Engineering handoff

The implementation consists of [saved-model inference](../src/forecasting/inference.py), [FastAPI schemas/routes](../src/api/main.py), four small input files, and focused synthetic API/inference checks. Native loads and predictions in automated checks use test doubles; request feature preparation uses the existing pipeline.

Chathuranga's supplied manual outcomes are recorded in Section 6.1. Formal producer approval, independently reviewed reference verification and Tinosh's consumer acceptance remain unrecorded here. Tinosh's next step under [#183](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/183) is to use the [retained-export contract](forecast-api-contract.md) for the joined fixed-origin case and this separate request-time contract for the live demonstration, checking identity, units, inclusive windows, cumulative meaning and unavailable behaviour in his actual consumer. Record the consumed version, reviewer, date and outcome separately from Chathuranga's producer review; involve Didilani/Dewmi where their input meaning is affected. Preserve 28-day downstream unavailability. Issue #180 remains open until its outstanding evidence and acceptance requirements are satisfied. API code acceptance does not settle other component blockers in [integration readiness](integration-contract-readiness.md).
