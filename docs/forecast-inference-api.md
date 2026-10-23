# Request-time forecast API and presentation inputs

**Responsible member:** Chathuranga — forecasting meaning and shared API architecture.
**Integration reviewer:** Tinosh — endpoint, schema and adapter acceptance.
**Date:** 2026-10-05 (Asia/Colombo).
**Status:** Implementation and four synthetic JSON examples are merged through [PR #151](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/151); #132 is closed. Chathuranga reported that the initial manual demonstration worked. Revised-example demonstration and Tinosh's consumer acceptance are not established by that closure. The API is a presentation prototype, not completed group-wide integration.

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

## 7. Engineering handoff

The implementation consists of [saved-model inference](../src/forecasting/inference.py), [FastAPI schemas/routes](../src/api/main.py), four small input files, and focused synthetic API/inference checks. Native loads and predictions in automated checks use test doubles; request feature preparation uses the existing pipeline.

Chathuranga runs the four revised manual examples against the retained local models and checks their identity and timing. Tinosh can subsequently review endpoints, schemas, unavailable behavior and integration suitability through the PR process. API code acceptance does not settle other component blockers in [integration readiness](integration-contract-readiness.md).
