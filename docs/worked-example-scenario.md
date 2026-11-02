# Multi-Horizon Worked Scenario

**Issue:** [#214](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/214), related to #179.
**Execution status:** Chathuranga manually completed the four-horizon historical replay on **2 November 2026**. All four API forecasts reconciled exactly with retained evidence. [Section 9](#9-recorded-human-execution--2-november-2026) records the trace, actual-sales errors and missed retrospective crossing. Component interpretation and human code peer review remain pending.

## 1. Purpose and scope

A manager considers demand for one SKU–warehouse pair over the next day, week, fortnight and four weeks. The demonstration shows:

**Pre-origin sales history → four actual API forecasts → exact retained-case reconciliation → approved scenario/advisory context → separately labelled retrospective actual-sales comparison.**

The project dataset is simulated by its publisher. This is a historical final-evaluation replay, not an operating-company decision, independent unseen-data study or new aggregate accuracy evaluation. Preserve the [prior validation/EDA/outcome exposure disclosure](forecasting-final-evaluation.md#9-limitations). The [research results](results.md) retain their existing hypotheses and conclusions.

## 2. One selected pair and four horizons

Use the horizon-neutral seed `demo-01`. The helper selects one pair reproducibly from the five available pair-selection records F02/F06/F10/F14/F18, then requires unique matching cases for that pair and origin across all four horizons. These selection records use the existing seven-day roster only to identify candidate pairs; the seed does not specify a forecast horizon. The roster is purposive, not representative of the full forecast population. The helper sorts assessment IDs and uses `random.Random(seed).choice`. Record the actual selected pair from the new run rather than assuming it matches the earlier demonstration; do not try seeds for a preferred outcome.

The [helper](../src/decision_support/worked_scenario.py) uses 337 consecutive daily sales records from **2024-01-01 through origin 2024-12-02**. The validated reader requests only `Date`, `SKU_ID`, `Warehouse_ID`, `Units_Sold` through the origin, verifies the existing provenance pin and selects the pair. It hashes the complete Parquet as opaque bytes without decoding future targets. The API receives identity, origin, horizon, `supplied_history` and daily `Date`/`Units_Sold`; no future sales, inventory or source-generated forecasts are forecast inputs. Full-span history aligns the historical replay; it is not a claim that every forecast needs 337 days.

| Horizon | Meaning | Inclusive target window | Frozen producer |
|---|---|---|---|
| 1 day | Next-day demand | 2024-12-03 | LightGBM GBM018 |
| 7 days | Cumulative demand | 2024-12-03–2024-12-09 | LightGBM GBM011 |
| 14 days | Cumulative demand | 2024-12-03–2024-12-16 | XGBoost GBM022 |
| 28 days | Cumulative demand | 2024-12-03–2024-12-30 | XGBoost GBM003 |

These windows overlap. Do not add their quantities together or infer a daily forecast path from their totals.

## 3. API execution and exact reconciliation

The helper loads the existing FastAPI application once with an in-process `TestClient`, runs its lifespan, verifies readiness for all four saved producers and calls `POST /forecasts` once per horizon. It uses real saved models in a human real-source run; no separate HTTP server is required. It does not train, refit, regenerate evidence or invoke full research-integrity replay.

Each response must match its retained forecast, prospective projection and advisory record exactly before attaching that case:

| Check | Required match |
|---|---|
| Identity and dates | SKU, warehouse, origin, integer horizon, inclusive target window and next-day/cumulative meaning |
| Producer | Model/configuration, source run, manifest path/hash, model and preprocessor paths/hashes |
| Request | Canonical digest of the actual submitted request matches API `input_sha256` |
| Quantity | Finite numeric quantity exactly equals the retained export, projection and advisory forecast; no tolerance, boolean or string substitution |
| Units and source | Retained unit is `units`; projection is bound to the same export |

The API has no unit field; units come from the documented `Units_Sold` contract and retained export. Missing, changed, duplicate or mismatched sources fail without a substituted forecast or success trace. Stage and underlying cause are reported. An existing trace is never overwritten; handled partial writes remove only the new file created by that attempt.

**Inventory and advisory evidence is retained, not recomputed.** Different request history or origin cannot silently reuse the historical exposure results. Current DR-012 approval and historical proposed labels remain separate.

## 4. Human execution

Use the project environment and development dependencies. First review the helper and source scope, then use the [checksum guide](checksums/README.md) and an independently reviewed reference for the applicable installed source profiles. Inputs include the validated dataset bundle, hash-bound saved producers/run metadata, forecast export and retained inventory/advisory sources described in the [API contract](forecast-inference-api.md). Validated provenance must match `35e9fb4218bfaf301703d6885decebaee6a3af2aa85aef55247c3a77d0ea964f`.

For the separate retrospective comparison, the local final run must also retain `artifacts/forecasting/final-20261003-02/observations.json`. The helper validates its bytes against the same pinned final completion manifest. It reads and parses the complete existing observations file only after all four API outputs have reconciled, then uses and records only the selected pair’s four target totals. No outcome regeneration or research metric replay is performed.

Record the revision and working state separately; the trace does not invoke Git:

```bash
git rev-parse HEAD
git status --short --branch
```

Chathuranga manually runs the reviewed command:

```bash
python -m src.decision_support.worked_scenario \
  --seed demo-01 \
  --output research-materials/issue-214/worked-scenario-v1.json
```

After success:

```bash
sha256sum research-materials/issue-214/worked-scenario-v1.json
```

Do not refresh source hashes, regenerate missing inputs or choose another seed to make a replay pass. Investigate a failure and preserve its cause before a separately reviewed later attempt. Subsequent attempts require a new filename; the named Git exception does not automatically extend to them.

## 5. Managerial walkthrough

Show all four forecast horizons together. For each approved inventory horizon (1, 7 and 14 days), explain forecast demand, origin inventory, fixed reorder reference, inventory buffer, predicted margin, recorded exposure state and advisory consideration using the actual new output. The [DR-012 approval](decisions/DR-012-inventory-risk-replenishment-methodology.md#group-approval-record) covers h1/h7/h14 only. **h28 forecast availability does not approve h28 inventory use**: preserve its unavailable inventory/replenishment fields and reasons.

Scenario starting balances are hypothetical, source within-day timing is unknown, the reorder point is fixed and no receipts/transfers/returns/losses or adjustments are modelled. A crossing is conditional exposure, not a verified stockout or automatic purchasing trigger. No crossing is not evidence of safety or overstock. Forecast demand is not an order quantity.

A person could check verified actual stock, expected deliveries, supplier lead time and operating policy before considering replenishment. The demo does not supply optimal orders, managerial clearance or demonstrated business benefit. Preserve the original advisory wording, unavailable numerical replenishment/uncertainty and `human_review_status=not_assessed`. Completed record-transparency checks are distinct from managerial review and rendered-view acceptance.

Didilani reviews inventory interpretation; Dewmi reviews responsible meaning and presentation; Tinosh and Chathuranga review API integration and forecast meaning. This demo does not replace #201's four-view acceptance or #182's actual-view review. Issue closure alone does not require another run; changes affecting code, inputs, models or evidence require review of whether a new trace is needed.

## 6. Separate retrospective comparison

The `retrospective_comparison` block contains the selected pair's existing final actual-sales totals and case-level arithmetic, separately from `forecast_results`. It is read after all forecasts reconcile and never sent to the API. Record all four rows, including less favourable results; do not treat the selected pair as population-level performance evidence.

- Signed error = forecast − actual sales.
- Absolute error = absolute value of signed error.
- Absolute percentage error = absolute error / actual sales × 100; unavailable when actual sales are zero.

These are explanatory retrospective errors, not prospective uncertainty intervals, a new model-ranking exercise or significance evidence. Actual sales are also different from recorded inventory. Subtracting them from hypothetical starting stock gives a scenario balance, not a verified future inventory snapshot.

## 7. Storage and human-run account

The helper writes a new JSON under `research-materials/issue-214/`, rejects symlink redirection and overwrite, and includes source/helper hashes, package versions, input count/span/digests, selection, four API responses and unchanged retained cases. Raw daily history and full request payloads are omitted. Only `worked-scenario-v1.json` has the [explicit storage exception](artifact-storage-policy.md#evidence-and-model-retention); other generated outputs, datasets and models remain ignored. Preserve generated bytes and record the actual new SHA-256.

The [recorded run account](#9-recorded-human-execution--2-november-2026) includes the actual command, supplied revision/dirty state, helper and trace identities, results and limitations. The earlier single-horizon trace was removed at Chathuranga's request and is not used as evidence for this execution. Existing checksum profiles do not cover the new trace; its SHA-256 is recorded explicitly. Human/component acceptance is separate from the successful technical run.

## 8. Implementation checks

```bash
python -m pytest tests/test_decision_support_worked_scenario.py -q
ruff check src/decision_support/worked_scenario.py tests/test_decision_support_worked_scenario.py
ruff format --check src/decision_support/worked_scenario.py tests/test_decision_support_worked_scenario.py
MYPYPATH=tests python -m mypy src/decision_support/worked_scenario.py tests/test_decision_support_worked_scenario.py --explicit-package-bases --disable-error-code import-untyped
```

Synthetic fixtures and model spies test selection, complete chronological history, all-horizon alignment, exact response/provenance reconciliation, h28 inventory gating, outcome-access ordering, hash-bound observations, zero-actual handling and failure/storage behavior. They do not establish real-model parity, actual new run outputs, rendered readability, component approval or managerial effectiveness. Human real-source execution and required reviews remain separate acceptance steps.


## 9. Recorded human execution — 2 November 2026

**Executor:** Chathuranga. Trace creation: `2026-11-02T16:47:37.799301+00:00` (22:17:37 Asia/Colombo). The human supplied terminal output records HEAD `a44131b64b4ee3655ce5e506e70940e21b132848` on `feature/h7-worked-scenario` with uncommitted implementation/documentation changes. HEAD alone does not identify those changes; the executed helper SHA-256 is `ada8738fdda2c0d3375ab361f5ea2639259e105534acb4cae4ada113200ea23f`.

The command in Section 4 was executed with seed `demo-01`, selecting F10 from F02/F06/F10/F14/F18. The pair is **SKU_10 / WH_3** at origin **2024-12-02**, with 337 daily sales records from 2024-01-01 through that origin. Matched retained cases are F09/F10/F11/F12 for horizons 1/7/14/28 respectively. Future sales were not forecast inputs. The terminal reported successful reconciliation for all four horizons, followed by the separately labelled retrospective comparison.

**Trace:** [worked-scenario-v1.json](../research-materials/issue-214/worked-scenario-v1.json). SHA-256: `c79c8a51debe0012048a341e71c76841c21f1065c0f2fdf62b81926c2dc584fb`. Preserve its exact bytes; do not overwrite it to obtain a preferred outcome.

### Forecasts and retrospective sales comparison

All quantities are units. Values below are rounded for display; the trace preserves the original numerical values. Absolute percentage error uses actual sales as the denominator and is not an accuracy percentage or population-level metric.

| Horizon | Target window | Producer | API forecast | Actual sales | Absolute error | Absolute percentage error |
|---|---|---|---:|---:|---:|---:|
| 1 day | 3 Dec 2024 | LightGBM GBM018 | 13.911102 | 20 | 6.088898 | 30.44% |
| 7 days | 3–9 Dec 2024 | LightGBM GBM011 | 91.938213 | 142 | 50.061787 | 35.25% |
| 14 days | 3–16 Dec 2024 | XGBoost GBM022 | 167.450439 | 291 | 123.549561 | 42.46% |
| 28 days | 3–30 Dec 2024 | XGBoost GBM003 | 317.719879 | 563 | 245.280121 | 43.57% |

All four forecasts underpredict the selected pair's actual sales. Exact agreement with retained forecasts demonstrates replay consistency; it does not mean those forecasts accurately match actual demand. This selected case does not establish whole-model performance or a new ranking. Keep the frozen producer choices and the canonical evaluation findings unchanged.

**Reporting and model-freeze control:** Chathuranga confirmed on 2 November 2026 that final test and demo results were not used to change the frozen training plan, retune configurations, retrain models to improve these results or reselect designated producers. The recorded `demo-01` case and all four horizon outputs are retained despite their underprediction; the case was not replaced to obtain a more favourable result. The 14-day missed proxy crossing is reported below. These controls limit result-driven changes but do not establish that all research bias is absent; the previously disclosed validation/EDA/outcome exposures remain applicable. Explaining the causal mechanism behind the underprediction is outside this worked demonstration and is not asserted from this one case.

### Prospective managerial consideration and separate retrospective check

The approved constructed scenario uses starting inventory **412**, reorder reference **218** and buffer **194** units, with no receipts or other adjustments and unknown source within-day timing.

| Horizon | Retained predicted margin | Prospective forecast state |
|---|---:|---|
| 1 day | 180.088898 | No forecast crossing |
| 7 days | 102.061787 | No forecast crossing |
| 14 days | 26.549561 | No forecast crossing |
| 28 days | Unavailable | Downstream inventory use requires separate approval |

**Prospective interpretation, pending component review:** The retained 1/7/14-day forecasts stay below the scenario's 194-unit buffer. A person can inspect these conditional margins, verify actual stock and incoming deliveries, and consider operating constraints. The smaller 14-day margin warrants attention in the walkthrough, but no numerical review threshold, new automatic trigger or purchasing rule is introduced. The advisory records remain `human_review_status=not_assessed`, with numerical replenishment and prospective uncertainty unavailable. No crossing does not establish inventory safety, excessive stock or permission to avoid replenishment.

**Retrospective evidence, unavailable when issuing the forecast:** The existing [inventory evaluation](../reports/inventory-risk/issue-164/evaluation-v1/evaluation.json) records no realised crossing at 1/7 days, with retrospective margins 174 and 52. At 14 days, actual sales are 291 against the 194-unit buffer, and the retained retrospective margin is **−97**. It records `realised_crossing` and confusion cell **FN (false negative)**: the forecast missed a crossing in the constructed proxy scenario. This illustrates why forecast consistency and positive predicted margins cannot establish safety. It is not a verified physical stockout or realised company harm, and it must not be mixed into the prospective advisory inputs. No 28-day inventory interpretation is inferred.

### Provenance, environment and remaining acceptance

The trace preserves the producer/model/preprocessor paths and hashes, horizon-specific request digests and these source identities:

| Source | SHA-256 |
|---|---|
| Forecast export | `c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863` |
| Final manifest | `adec21bf384ca898d966dd06234682d0fac0b3c014067d8ebb563bbd218feb43` |
| Validated provenance | `35e9fb4218bfaf301703d6885decebaee6a3af2aa85aef55247c3a77d0ea964f` |
| Final observations | `2ea81441dadc7e1e3d69e96bbe1f54ffd8794ff28c8bcb304c1f39608f03ba3d` |

Recorded environment: Python 3.12.3, FastAPI 0.142.2, LightGBM 4.7.0, XGBoost 3.4.1, NumPy 2.5.3 and pandas 3.0.6. The helper's internal source/hash checks and exact reconciliation succeeded. No separate independently reviewed checksum-profile command output was supplied with the human-run terminal record; this account does not claim that additional verification. The tracked inventory evaluation used for the retrospective explanation was checked against its retained manifest's evaluation-file hash; that byte match is distinct from scientific or consumer acceptance.

The technical execution is recorded. Didilani's inventory interpretation, Dewmi's responsible presentation/oversight review, Tinosh/Chathuranga's API/forecast review and another human's code approval remain pending. Independent code review and synthetic tests do not replace these controls. Current method approval remains separate from unchanged historical proposed labels. No new research experiment, uncertainty method, hypothesis decision, order recommendation or real-company benefit is asserted.
