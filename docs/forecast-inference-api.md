# Request-time forecast API and presentation inputs

**Responsible member:** Chathuranga — forecasting meaning and shared API architecture.
**Integration reviewer:** Tinosh — endpoint, schema and adapter acceptance.
**Date:** 2026-10-05 (Asia/Colombo).
**Status — updated 30 October 2026:** Request-time inference and four synthetic examples are merged through PR #151; producer corrections were delivered through #193 / PR #195. [#203 closed on 29 October](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/203#issuecomment-6501737406) after Tinosh's technical consumer verification and Chathuranga's separate producer/source acceptance. Section 6 preserves the distinct 24/28 October observations and the later acceptance. PR #197 delivered the separate retained-case routes, closing #183. Retained runtime/source/component acceptance and approved views continue under [#201](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/201), assigned to Didilani; W2 rendered review remains under #182 and final repository acceptance under #179.

## 1. Active serving behavior

The presentation flow is:

`example JSON daily history → POST /forecasts → frozen input pipeline → saved model.predict() → forecast response`

Models and their saved preprocessing are loaded once at application startup. Every accepted request builds its own feature vector and invokes the designated model. Responses are not cached. The request-time forecast path neither opens the separate fixed-origin [retained forecast export](forecast-api-contract.md) nor reads stored predictions, observations or metric files. The retained-case GET routes in Section 5.1 separately consume that export and its linked prospective evidence.

This behavior requested by Chathuranga supersedes the earlier stored-forecast serving proposal. It preserves the existing feature definitions, saved preprocessing, model files and producer mapping. Chathuranga and Tinosh retain their documented ownership; the scoped request-time handoff was accepted under #203 on 29 October 2026.

### 1.1 Research and demonstration scope

**Scope confirmed by Chathuranga on 2026-10-05:** this API is a presentation prototype demonstrating request-time inference with the existing saved models. The main research task is to address the research questions and hypotheses through the documented analytical evidence. The API is a delivery mechanism within that project; it introduces no research method or hypothesis.

The FastAPI service demonstrates request-time inference using the saved forecasting models and synthetic historical inputs. Research conclusions are based on the documented analytical evidence in [research design](research-design.md) and the existing reports. Successful API responses demonstrate software integration only; they do not establish forecasting accuracy, generalisation, inventory-decision effectiveness, or acceptance/rejection of the research hypotheses.

The demonstration preserves the research questions, hypotheses, targets, feature definitions, producer mapping, saved models and retained numerical evidence. Synthetic requests and their responses are illustrative presentation material and must be labelled accordingly in slides and recordings. Changing an example input does not create an additional research result. The API neither establishes replenishment quantities nor approves downstream 28-day use.

**Historical preparation instruction — 5 October 2026:** Chathuranga authorised preparing the demo on its then-existing feature branch; prior Tinosh review was not required for preparation. That instruction is not standing Git authorisation. The implementation is now merged; the later scoped request-time acceptance is recorded in Section 6.2. Component ownership and separate retained acceptance remain unchanged.

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

#### Retained-route inputs and local access

Paths are fixed relative to the repository root:

| Input | Required repository-relative path |
|---|---|
| Forecast export | `data/processed/forecasting/handoffs/final-20261003-02/issue-132-forecast-export-v1.json` |
| Decision-support records and manifest | `reports/decision-support/issue-168-inventory-v1/records.json` and adjacent `manifest.json` |
| Inventory bundle | `research-materials/inventory-risk/issue-164/evaluation-v1/`, containing `prospective.json`, `evaluation.json`, `report.md` and `manifest.json` |

Obtain the existing byte-identical local inventory bundle through the reviewed handoff and use the [checksum guide](checksums/README.md). Preserve existing files and bindings; do not generate replacement research evidence or commit protected inputs to make the service start. The tracked record bundle and local forecast/inventory inputs must belong to the same retained source context.

From the repository root, start the server in one WSL terminal using the configured environment:

```bash
.venv/bin/python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

In a second WSL terminal:

```bash
curl -i http://127.0.0.1:8000/decision-support/cases
curl -i http://127.0.0.1:8000/decision-support/cases/F01
curl -i http://127.0.0.1:8000/decision-support/cases/F04
curl -i http://127.0.0.1:8000/decision-support/cases/F99
```

For a native Windows checkout, use its own configured Windows virtual environment. In PowerShell, start the server with:

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

In a second PowerShell terminal, use `curl.exe` to avoid the PowerShell alias:

```powershell
curl.exe -i http://127.0.0.1:8000/decision-support/cases
curl.exe -i http://127.0.0.1:8000/decision-support/cases/F01
curl.exe -i http://127.0.0.1:8000/decision-support/cases/F04
curl.exe -i http://127.0.0.1:8000/decision-support/cases/F99
```

The WSL and Windows virtual environments are platform-specific. A missing/broken interpreter must be repaired in the applicable environment before recording a manual demo result. The serving commands above are a human-run walkthrough, not evidence that a hosted demo or Windows execution has occurred.

#### Scoped checks and observed automated outcomes — 25 October 2026

The retained-case tests use disposable synthetic inputs. Reproduce the focused checks from the repository root in WSL:

```bash
.venv/bin/python -m pytest tests/test_decision_support_retained_cases.py tests/test_forecast_api.py tests/test_decision_support_assessment.py tests/test_decision_support_records.py tests/test_inventory_risk_forecast_handoff.py -q
.venv/bin/python -m ruff check src/api/main.py src/decision_support/retained_cases.py tests/test_decision_support_retained_cases.py
MYPYPATH=tests .venv/bin/python -m mypy src/api/main.py src/decision_support/retained_cases.py tests/test_decision_support_retained_cases.py --explicit-package-bases --disable-error-code import-untyped
```

These commands passed locally on the PR working tree based on `b3b69e2`, including this correction: **128 synthetic tests passed**, Ruff passed and MyPy reported no issues in the three target files. The [CI Quality workflow](../.github/workflows/ci-quality.yml) now includes the scoped Ruff/MyPy checks, retaining its documentation-only skip behavior. The startup/request regression patches preparation, assessment and inventory-evaluation entry points to fail, checks the original records are returned unchanged, and verifies that serving writes no fixture files. Missing/tampered record and manifest cases return 503 rather than substituting a case.

A separate automated `TestClient` smoke check consumed the seven existing retained input files listed above. Model loading was deliberately disabled through the existing injected loader, and preparation/evaluation/export entry points were patched to fail. It observed:

| Request | Observed result |
|---|---|
| `GET /decision-support/cases` | HTTP 200; exactly 20 records |
| `GET /decision-support/cases/F01` | HTTP 200; retained h1 case |
| `GET /decision-support/cases/F04` | HTTP 200; h28 inventory gate preserved, without inventory quantities in its projection |
| `GET /decision-support/cases/F99` | HTTP 404; `unknown_case` |

Forecast-model health remained unavailable in that injected test while retained routes remained usable. No saved model, forecast calculation, research evaluator, record generator or human assessment was executed. This is automated retained-serving evidence, not a human-observed demo, rendered-visual acceptance or scientific evaluation.

The separate read-only `.venv/bin/python -B -m src.data.verify_checksums --profile dewmi` check matched the forecast export **1/1**, with no missing/changed selected file. Reference `docs/checksums/2026-10-06.json` had SHA-256 `381ed9607a9e3ec155ee3754d699d62873bfbff18f5e1f4edc31c407267ed7cc`; reference-byte comparison revision and repository HEAD were `b3b69e2a2de89a1993e9b2f9c9781aaf977c9150`. Independent reference review and tracked-source comparison were not checked, so this remains a provisional local identity match. The API's additional source-binding checks do not establish scientific correctness or final consumer acceptance.

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

Both outputs explicitly reported **provisional local matches**: tracked content and independent reference review were not checked. These checks read selected bytes only; files outside the two profiles remain unverified. No full retained-bundle scan or scientific verification was run. The later request-time handoff verification and acceptance are recorded in Section 6.2. These earlier outputs remain provisional at their original scope; they are not retroactively upgraded by the later review. Retained-export acceptance remains separate under #201.

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
### 6.2 Technical consumer verification evidence — 28 October 2026

**Task:** [#203](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/203), closed on 29 October 2026 for the scoped request-time forecast handoff; the 28 October evidence below retains its capture-time context.
**Executor / technical consumer reviewer:** Tinosh.
**Capture outcome — 28 October:** every requirement outcome derived from the exchanges is `PASSED` (AS-01 to AS-06, `RT-CONTRACT`, `RT-CHANGED-HISTORY`, `RT-REJECTIONS`). This is Tinosh's technical consumer verification. Chathuranga's subsequent producer/source decision is a separate human acceptance, recorded below.
**Evidence:** `research-materials/issue-203/consumer-evidence-v2.json`, SHA-256 `ee048a7412f5727cb5bebfe606ecf3784fecba2352e06c25d43a415817af9abf` (committed LF bytes), capture timestamp `2026-10-28T15:35:48+00:00`.
**Tested source:** revision `20265aa0ecb7f5e6436e8aa29694a076fc643286` with a clean tracked working tree; Python 3.13.4; Windows-11-10.0.22631-SP0.
**Subsequent acceptance — 29 October 2026:** [Chathuranga accepted the scoped producer/source handoff](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/203#issuecomment-6501737406) after reviewing the v2 exchanges and Tinosh's reported `tinosh` profile verification at `7034d296f181564ecf575152f4ce5336ee00f6e4`: 20/20 files matched, no missing/changed files or reported warnings/failures, exit status 0. The independently reviewed reference revision and tested verification HEAD were that full commit; reference SHA-256 was `381ed9607a9e3ec155ee3754d699d62873bfbff18f5e1f4edc31c407267ed7cc`. The reported command was `.\.venv\Scripts\python.exe -B -m src.data.verify_checksums --profile tinosh --tracked-ref 7034d296f181564ecf575152f4ce5336ee00f6e4`. The serving capture remains bound to `20265aa0ecb7f5e6436e8aa29694a076fc643286`; the acceptance explicitly reviewed that evidence together with installed-file/source verification at `7034d29`. These are distinct revisions and scopes, not a claim of a new capture at the later commit. Existing CI was reused; no new research evaluation was performed. Historical `pending_under` labels in the immutable capture retain their original meaning. Retained inputs/routes, rendered views and group acceptance remain under #201/#182/#179.

**Execution:** in-process `fastapi.testclient.TestClient(src.api.main.app)` with the application lifespan, so the four saved producers were loaded from the local artifacts and verified at startup exactly as in the served application. This is not a separately started uvicorn server or a hosted demo.

From the repository root:

```bash
.venv/bin/python capture_consumer_evidence.py --output research-materials/issue-203/consumer-evidence-v2.json
.venv/bin/python capture_consumer_evidence.py --verify research-materials/issue-203/consumer-evidence-v2.json
```

The helper records every request and response first, then derives each outcome from assertions on those recorded exchanges; no outcome is written as a constant. It creates the evidence file exclusively and never overwrites an existing file. `--verify` recomputes all checks from the stored exchanges and fails if any stored check or outcome differs, any outcome is not `PASSED`, or the file has CRLF line endings.

| Requirement | Derived from |
|---|---|
| AS-01 | `SKU_ID` / `Warehouse_ID` echoed for all four horizons; unknown SKU and unknown warehouse return HTTP 422 `unknown_sku` / `unknown_warehouse` |
| AS-02 | `forecast_origin` echoed; `target_start_date` = origin + 1 for all four horizons |
| AS-03 | `target_end_date` = origin + h and the inclusive window is exactly h days, for h = 1, 7, 14, 28 |
| AS-04 | `horizon` echoed as the same JSON integer; `forecast_type` `next_day` / `cumulative_window`; cumulative (not daily-path) limitation for h7/h14/h28; h28 limitation that 28-day availability does not approve downstream inventory use; four separate records; horizon 3 returns HTTP 422 `unsupported_horizon` |
| AS-05 | `producer_designation: frozen_designated_producer`; Section 2 model/configuration per horizon; source run and run-manifest reference; one manifest hash across horizons; `provenance` keys exactly `model_path`, `model_hash`, `preprocessor_path`, `preprocessor_hash`, `input_sha256`, each hash a SHA-256 digest and each path under that horizon's producer directory; distinct model and input hashes per horizon; an identical repeat request reproduces `input_sha256`; changed history produces a new `input_sha256` |
| AS-06 | response keys exactly match the 22-field `ForecastResponse` allowlist; no retrospective, inventory or metric key at any depth (for example `observed_target`, `Demand_Forecast`, `Inventory_Level`, `Reorder_Point`, `retrospective_margin`, WAPE/MAE/RMSE); `inference_mode: request_time`; `observed_target`, `Demand_Forecast` and `Inventory_Level` request fields are rejected with HTTP 422 `extra_forbidden` |
| `RT-CONTRACT` | `GET /health` ready for `[1, 7, 14, 28]`; HTTP 200, `available`, empty `unavailable_reasons`, `forecast-inference-v1`, echoed `input_kind` and a finite `forecast_quantity`; the four example files are byte-identical before and after capture |
| `RT-CHANGED-HISTORY` | the 1-day example with final-day `Units_Sold` increased by 5 in memory returns a new `input_sha256` (against the identical-request control) with unchanged identity, window, producer and saved model/preprocessor provenance |
| `RT-REJECTIONS` | all ten negative requests return HTTP 422 without a substitute `forecast_quantity`: the five above plus `invalid_origin` (origin 2024-12-01), `future_history`, `incomplete_history` and `invalid_history` (one missing day) |

Forecast quantities and hashes are kept in the evidence file rather than restated here. As in Section 6, the changed-history quantity difference is recorded as an informational observation: tree models can return the same quantity for different inputs, so the pass/fail signal is the changed `input_sha256`.

**Superseded capture:** `research-materials/issue-203/consumer-evidence.json` (capture timestamp `2026-10-27T18:06:44.383554+00:00`) is preserved unchanged but superseded. It captured h7 only, and its AS-01 to AS-06 values were written as constants rather than derived from checks. The SHA-256 `503a3d03…` and 25 October date previously cited in this section identified neither that file nor the current evidence and are withdrawn. Chathuranga's 24 October outcomes in Section 6.1 remain his separate record.

These requests used the synthetic examples only. They did not train, tune, refit, replay research evaluation, measure accuracy or accept inventory/decision-support behaviour; the retained-case routes remain under #201.

## 7. Engineering handoff

For a dataset-backed 1/7/14/28-day historical replay, see the [multi-horizon worked scenario](worked-example-scenario.md). It calls the existing API with the same pre-origin history and requires exact identity/provenance/quantity reconciliation for each horizon before linking retained cases. Actual sales and errors are read only afterwards and labelled retrospective. It does not recompute inventory/advisory outputs, approve h28 inventory use or establish a new aggregate accuracy result; real-source execution is a separately recorded human action.

The implementation consists of [saved-model inference](../src/forecasting/inference.py), [FastAPI schemas/routes](../src/api/main.py), four small input files, and focused synthetic API/inference checks. Native loads and predictions in automated checks use test doubles; request feature preparation uses the existing pipeline.

Chathuranga's supplied 24 October outcomes remain in Section 6.1, with #180 closed for that evidence milestone. Producer corrections were delivered through #193 / PR #195. Section 6.2 records Tinosh's v2 serving evidence and the separate [29 October producer/source acceptance](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/203#issuecomment-6501737406), which closed #203. Continue with #201's retained handoff/views, #182's W2 rendered review and #179's final integrated acceptance; do not repeat completed live checks for unchanged behaviour.

[PR #197](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/197) merged as `b6f196ad73d3a31017582f81dbc7f5183ef573df`, closing #183. Chathuranga's [approval at corrected source commit `c540f03`](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/197#pullrequestreview-5642602452) covers the retained-case API scope. Both [CI Tests](https://github.com/chathuranga-sudusinghe/retail-demand-framework/actions/runs/40180999250) and [CI Quality](https://github.com/chathuranga-sudusinghe/retail-demand-framework/actions/runs/40180999258) passed for that corrected commit. These are existing implementation checks and scoped code approval; they do not establish a human-observed demo, final producer/source/consumer acceptance or rendered-visual acceptance.

[Issue #201](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/201), assigned to Didilani, continues the retained runtime handoff and approved inventory views from that merged implementation. Preserve Tinosh's original PR authorship and Didilani's recorded contributions. Chathuranga reviews forecast/API meaning, Didilani reviews inventory interpretation and Dewmi reviews responsible presentation. Tinosh retains his documented technical integration role and the separate request-time consumer review. Use the [retained-export contract](forecast-api-contract.md) for the fixed-origin case and this request-time contract for the live demonstration; record the consumed version, reviewer, date, outcome and remaining dependency for each. Preserve 28-day downstream unavailability and track subsequent acceptance in #179.
