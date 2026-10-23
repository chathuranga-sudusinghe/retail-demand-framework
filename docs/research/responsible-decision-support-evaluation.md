# Responsible Decision-Support Evaluation

**Status:** Draft for human review. Evaluation evidence is pending; this document does not complete Issue #168.

## 1. Purpose

This document prepares the responsible decision-support evaluation and presentation handoff for [Issue #168](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/168). It follows the existing measurable transparency criteria in the [approved methodology](responsible-decision-support-methodology.md#12-measurable-responsible-decision-support-and-human-review-criteria) and [DR-011](../decisions/DR-011-decision-support-output-structure.md).

The purpose is to assess whether reviewable decision-support records preserve the information needed for responsible management-facing interpretation. Each applicable transparency check is recorded as `met`, `not met`, or `not assessable`, with a short reason where required.

This evaluation does not recalculate forecasts, redefine inventory-risk methods, create replenishment quantities or thresholds, or introduce new uncertainty methods. Information that is unavailable or not yet approved remains explicitly unavailable rather than being replaced with an assumed value.

The evaluation is limited to the transparency and responsible-use characteristics that can be observed from the available records and reviewed upstream evidence. It does not provide evidence of improved user trust, managerial decision quality, business performance, inventory cost, or real-world effectiveness.

## 2. Evaluation Criteria

The check names below match [methodology §12.2](responsible-decision-support-methodology.md#122-measurable-transparency-checks). Issue #145's terms map to the same checks: inventory-risk visibility means Risk visibility; uncertainty/error visibility means Uncertainty visibility; assumptions/limitations visibility means Assumption/Limitation visibility; and source/component distinction means Source distinction. Recommendation traceability applies where a recommendation is defensibly available, as specified in Issue #145; this document introduces no new replenishment method or availability rule.

| Transparency check | What is reviewed |
|---|---|
| Forecast visibility | Whether the forecast value, forecast origin, and forecast horizon are clearly shown. |
| Risk visibility | Whether the available inventory-risk result and its supporting evidence are visible. |
| Recommendation traceability | Whether a replenishment recommendation, when defensibly available, can be traced to the evidence supporting it. |
| Uncertainty visibility | Whether available forecast-error or uncertainty information is shown rather than hidden. |
| Assumption visibility | Whether assumptions that affect interpretation are visible to the manager. |
| Limitation visibility | Whether relevant data or model limitations are explicitly presented. |
| Human-review transparency | Whether the human-review status and its reasons are visible and interpretable. |
| Source distinction | Whether forecasting, inventory-risk/replenishment, and responsible decision-support information remain distinguishable by source or provenance, using DR-011's component grouping. |

For each applicable check, the assessment outcome is recorded as `met`, `not met`, or `not assessable`. Where a check is `not met` or `not assessable`, a short reason is retained so that the evidence and limitation remain traceable.

### 20-Row Forecast Evidence Selection

This is a purposive, case-based selection of 20 forecasting rows from the retained Issue #132 fixed-origin export. Chathuranga's human-run preparation on 23 October 2026 populated all 20 `DecisionSupportRecord` instances. Chathuranga has since confirmed all eight record-level transparency outcomes for each of F01–F03; F04–F20 remain unassessed. The selection does not claim population-wide representativeness.

| Assessment IDs | SKU_ID | Warehouse_ID | Forecast origin | Horizons (days) | Rows |
|---|---|---|---|---|---|
| F01–F04 | SKU_1 | WH_1 | 2024-12-02 | 1, 7, 14, 28 | 4 |
| F05–F08 | SKU_5 | WH_2 | 2024-12-02 | 1, 7, 14, 28 | 4 |
| F09–F12 | SKU_10 | WH_3 | 2024-12-02 | 1, 7, 14, 28 | 4 |
| F13–F16 | SKU_15 | WH_4 | 2024-12-02 | 1, 7, 14, 28 | 4 |
| F17–F20 | SKU_20 | WH_5 | 2024-12-02 | 1, 7, 14, 28 | 4 |

**Selection rule:** The five SKU–warehouse combinations were chosen using SKU numbers 1, 5, 10, 15 and 20, paired with warehouses 1–5 respectively. All four horizons are retained for each pair. The rule supports comparison across horizons and selected SKU–warehouse combinations but is not a representative sample.

**Source and version:** `issue-132-forecast-export-v1.json`; export schema `issue-132-forecast-export-v1`; handoff `final-20261003-02`; forecast origin `2024-12-02`. The retained export contract is documented in `docs/forecast-api-contract.md`. One-day predictions represent next-day demand; 7-, 14- and 28-day predictions represent cumulative-window demand. Forecast uncertainty is reported unavailable (`no_agreed_method`).

**Versioned checksum reference:** The selected forecasting evidence is
`issue-132-forecast-export-v1.json` (566,670 bytes), from source run
`final-20261003-02`. Its registered SHA-256 is
`c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863`,
recorded in the [versioned checksum reference](../checksums/2026-10-06.json) under
`profiles.dewmi.files`. This reference establishes the expected file
identity; downstream acceptance remains a separate human-reviewed
requirement and is not claimed here.

**Prepared record linkage:** Each selected forecast row is traced by SKU_ID, Warehouse_ID, forecast origin and horizon to a populated instance of [DecisionSupportRecord](../../src/decision_support/records.py), using the implemented mapping in Section 2.1. Chathuranga ran the command in Section 2.2 with output directory `research-materials/decision-support/issue-168-json/`. Its local working files remain ignored. On 23 October 2026, Chathuranga authorised unchanged copies of the four files under `reports/decision-support/issue-168-json/` for shared GitHub review: [readable records](../../reports/decision-support/issue-168-json/records.md), [JSON records](../../reports/decision-support/issue-168-json/records.json), [partial checklist](../../reports/decision-support/issue-168-json/review.json) and [original preparation manifest](../../reports/decision-support/issue-168-json/manifest.json). The JSON record-bundle SHA-256 is `34c3e0d64a891a00c468aac5b65f95ced565eca1be8487d7df0266ec530864a3`. The manifest records operator `Chathuranga` and preparation time `2026-10-23T03:48:14.025886+00:00`. Verification at preparation matched the generated content hashes, then-current code hashes and registered export binding. The recorded `assessment.py` generator SHA-256 is `bbba5ecd713668b3e1beeb26cc262cdbdce0b9a706a6df1a13493abdf4f01b05`; it differs from today's implementation, and no committed generator revision was recorded. The manifest is a historical generation receipt, not verification of current source or independent scientific review. Subsequent F01–F03 assessments changed only the editable checklist.

The tracked checklist snapshot SHA-256 is `99a7e8659fc0b5e33b360bd35421f79c64071ecafc1eaa7bd10e36b03e29864f`. The original manifest's assessment-status text and initial-template hash describe the blank preparation, not this later partial review. The [evidence index](../../reports/README.md#decision-support-review-evidence) explains each file and its current scope. Files are copied without regenerating records, changing outcomes or updating historical generator hashes; the [storage policy](../artifact-storage-policy.md) permits only this limited snapshot, while bulk research outputs remain local.

**Snapshot identity check — 23 October 2026:** All four copied files matched the local originals byte for byte; record/Markdown hashes and the original blank-template binding matched the preparation manifest. The read-only command `.venv/bin/python -m src.data.verify_checksums --profile dewmi` matched the selected forecast export, 1/1 files, with none missing or changed. It used `docs/checksums/2026-10-06.json`, SHA-256 `381ed9607a9e3ec155ee3754d699d62873bfbff18f5e1f4edc31c407267ed7cc`; reference revision and repository HEAD were both `1a15b810622e0e19944769f06dec8e29b4708afc`. No independently reviewed commit was supplied, so these are provisional local identity matches, not a completed trusted handoff or scientific validation. The Dewmi profile covers the forecast export only; it does not verify the historical generator or other research artifacts.


**Forecast-key roster linked to prepared records:**

The historical roster verification found all 20 selected forecast keys in the 1,000-row export. The human-run preparation now links each key to the zero-based `records` array index shown below in the retained `records.json`; assessment IDs are also present in both JSON and Markdown outputs. There are five records per horizon; preparation initially created 160 unique, unassessed record/criterion checks.

| Assessment ID | SKU_ID | Warehouse_ID | Forecast origin | Horizon (days) | Record linkage |
|---|---|---|---|---|---|
| F01 | SKU_1 | WH_1 | 2024-12-02 | 1 | `records[0]` |
| F02 | SKU_1 | WH_1 | 2024-12-02 | 7 | `records[1]` |
| F03 | SKU_1 | WH_1 | 2024-12-02 | 14 | `records[2]` |
| F04 | SKU_1 | WH_1 | 2024-12-02 | 28 | `records[3]` |
| F05 | SKU_5 | WH_2 | 2024-12-02 | 1 | `records[4]` |
| F06 | SKU_5 | WH_2 | 2024-12-02 | 7 | `records[5]` |
| F07 | SKU_5 | WH_2 | 2024-12-02 | 14 | `records[6]` |
| F08 | SKU_5 | WH_2 | 2024-12-02 | 28 | `records[7]` |
| F09 | SKU_10 | WH_3 | 2024-12-02 | 1 | `records[8]` |
| F10 | SKU_10 | WH_3 | 2024-12-02 | 7 | `records[9]` |
| F11 | SKU_10 | WH_3 | 2024-12-02 | 14 | `records[10]` |
| F12 | SKU_10 | WH_3 | 2024-12-02 | 28 | `records[11]` |
| F13 | SKU_15 | WH_4 | 2024-12-02 | 1 | `records[12]` |
| F14 | SKU_15 | WH_4 | 2024-12-02 | 7 | `records[13]` |
| F15 | SKU_15 | WH_4 | 2024-12-02 | 14 | `records[14]` |
| F16 | SKU_15 | WH_4 | 2024-12-02 | 28 | `records[15]` |
| F17 | SKU_20 | WH_5 | 2024-12-02 | 1 | `records[16]` |
| F18 | SKU_20 | WH_5 | 2024-12-02 | 7 | `records[17]` |
| F19 | SKU_20 | WH_5 | 2024-12-02 | 14 | `records[18]` |
| F20 | SKU_20 | WH_5 | 2024-12-02 | 28 | `records[19]` |

**Record linkage status:** All selected forecasting keys now have populated decision-support records. Numeric forecast horizons map to explicit string labels through Section 2.1, with target meaning retained in evidence. Inventory-risk and replenishment evidence remains unavailable where no matching source was supplied. The 28-day horizon remains restricted to forecast-transparency scope. Confirmed outcomes are currently limited to F01–F03, as recorded in Section 3.


**Downstream evidence boundary:** Reviewed inventory-risk and replenishment outputs will be linked only where an actual matching source exists. Missing evidence will be recorded explicitly with record-specific reasons rather than replaced with assumptions or used to silently exclude reviewable cases. Pending inventory-risk decisions under Issue #164 remain dependencies. The 28-day horizon is retained for forecast-transparency assessment only; downstream inventory and replenishment interpretation remains deferred.

**Assessment status:** Chathuranga's [forecasting-side roster support and origin/horizon clarification](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/168#issuecomment-6283379812) support retaining F01–F20 as a limited purposive roster. That historical comment did not itself approve every mapping or execute an assessment. In the working conversation on 23 October 2026, Chathuranga explicitly confirmed F01's forecast-visibility outcome, its risk-visibility outcome and then the remaining six outcomes shown in Section 3. He subsequently confirmed all eight proposed outcomes for F02 and then F03 after reviewing their respective evidence summaries. Codex transcribed those human-confirmed decisions into `review.json` with assessor `Chathuranga`; it did not extend them to other records.

### 2.1 Implemented source-to-record mapping

[assessment.py](../../src/decision_support/assessment.py) maps the F01–F20 roster to the existing [DecisionSupportRecord](../../src/decision_support/records.py) class, using contract version `issue-164-168-v1`. The forecast-only path reads the pinned forecast export through `forecast_handoff.py`. The optional inventory path also reads `prospective.json`, verifies all three manifest-bound file hashes as bytes, and validates the prospective producer contract. It does not decode retrospective observations or metrics, generate inventory outcomes, run forecasting models or assign transparency outcomes. Cross-field checks reject inconsistent supplied evidence rather than repairing it.

| Record field | Implemented mapping |
|---|---|
| Identity and origin | Copy exact SKU/warehouse strings and ISO forecast origin; retain assessment ID and the complete source key in evidence. |
| `forecast_horizon` | Map numeric 1/7/14/28 to `1-day` / `7-day` / `14-day` / `28-day`. Retain numeric horizon, forecast type, units and inclusive target dates in evidence; cumulative totals are not daily paths. |
| `forecast_demand` | Preserve the raw numeric prediction, including zero and finite negatives. Add an inventory-use limitation for negative forecasts; never clip or substitute values. |
| `forecast_provenance` | JSON text containing exact export hash/schema, export-level source provenance, case identity, producer/configuration and original statuses. |
| Inventory evidence / provenance | Forecast-only preparation uses `None` with field-specific pending-upstream reasons. With `--inventory-evidence`, matching available 1/7/14-day exposure and its manifest/source provenance populate these fields; unavailable cases keep their original reason. Twenty-eight-day inventory fields remain gated. No case is dropped for missing inventory evidence. |
| Replenishment and uncertainty | `None` with explicit reasons. Preserve `no_agreed_method`; do not manufacture orders, intervals or retrospective errors. |
| Assumptions, limitations and evidence | Retain target meaning, units, source references, assessment ID, publisher-simulated data, limited selection, zero-variance stockout label and applicable prior-exposure disclosures. |
| Component provenance | Identify forecasting and responsible decision-support contributions. Identify the inventory component only when its hash-bound evidence handoff is supplied; do not invent a producer in forecast-only mode. |
| Management consideration | Advisory wording with final decisions left to a responsible person. |
| Human review | Existing `not_assessed` state and reason. This is independent of the eight transparency-check outcomes. |

Forecast-only records retain explicit upstream gaps. Inventory-linked records additionally expose conditional inventory evidence with its source/scenario distinction. Neither preparation is a completed assessment or rendered prototype acceptance. Source and snapshot/method limitations remain visible. The historical forecast-only preparation manifest and source identity are recorded above.

### 2.2 Prepare records and record the human assessment

The human executor runs:

```bash
.venv/bin/python -m src.decision_support.assessment prepare \
  --operator Chathuranga \
  --output research-materials/decision-support/issue-168-json
```

Use the actual executor's name for `--operator`; this records preparation attribution, not the assessor or component ownership. This writes `records.json` (20 populated records), `records.md` (the same records for reading), `review.json` (160 blank checklist entries: 20 records × eight criteria), and `manifest.json` (source, record and code hashes, operator and preparation time). All generated files are JSON or Markdown. It never overwrites an existing preparation directory. The `issue-168-json` directory keeps earlier CSV preparations intact; use a fresh directory for any subsequent preparation. Generation still writes to ignored `research-materials/`. The limited tracked review copy in Section 2 lets members inspect the existing evidence through GitHub without running this command; it is not a new output destination for the CLI.

Dewmi reads `records.md` and records the assessment in the `checks` array in `review.json`: applicability (`yes`/`no`), the existing outcomes (`met`, `not met`, `not assessable`), evidence/reasons, assessor and ISO assessment date. A non-applicable check needs a reason and an empty outcome (`""`). A met check needs an evidence reference; not-met/not-assessable checks need reasons. Preserve the supplied identities, numeric horizons and source/version fields. Missing upstream evidence does not automatically assign any outcome. Assess actual record contents separately from visibility in a rendered prototype.

After the human checklist is complete, run:

```bash
.venv/bin/python -m src.decision_support.assessment summarize \
  --directory research-materials/decision-support/issue-168-json \
  --report research-materials/decision-support/issue-168-json/summary.json
```

The summarizer verifies the JSON and Markdown record-file hashes, source/version fields, unchanged case identities and exact 160-key coverage. Review schema `issue-168-review-v2` also binds the checklist to the exact populated-record hash, so assessments from a different inventory-evidence context cannot be silently reused. It rejects blank, duplicated, missing or invalid review entries; it does not perform the assessment. It writes both `summary.json` and `summary.md`, reporting per-criterion counts and the met proportion using all applicable cases, including not-assessable cases, with non-applicable cases excluded. A zero denominator remains JSON `null` and is labelled unavailable in Markdown. The reports bind the human-edited `review.json` by SHA-256 and do not overwrite either existing report.

The original `issue-168-review-v1` forecast-only bundles remain supported without migration. `summarize_files` first verifies their original record hash, Markdown hash, source binding, blank-template hash and schema agreement with the preparation manifest. It then applies the same identity/coverage/outcome checks. Legacy input files are never rewritten, and legacy assessments cannot be reused for inventory-linked records. Summary metadata preserves the original preparation timestamp and generator code hashes as historical receipts; those hashes need not match current source. The existing F01–F03 checklist still requires its remaining human assessments before it can produce a complete summary.

After the human-run [inventory evaluation](inventory-risk-evaluation-protocol.md#122-run-the-implemented-inventory-evaluation), prepare a separate bundle that includes its prospective inventory evidence:

```bash
.venv/bin/python -m src.decision_support.assessment prepare \
  --operator Chathuranga \
  --inventory-evidence research-materials/inventory-risk/issue-164/evaluation-v1/prospective.json \
  --output research-materials/decision-support/issue-168-inventory-v1
```

The bridge verifies the adjacent manifest, all three output-file hashes, registered dataset provenance, forecast-source binding and all 1,000 exact forecast keys. Evaluation/report files are hashed as opaque bytes; only prospective records are interpreted. All three snapshot policies are checked for consistent markers, statuses, basis, valid/null balances, exposure states and existing DR-012 margins. It rejects retrospective fields, mismatched values, duplicate keys and any claim that a constructed scenario established source timing. These consistency checks do not authenticate a mutable manifest or prove scientific correctness. It links only matching 1/7/14-day inventory evidence into `inventory_risk_evidence` and `inventory_risk_provenance`, preserving the snapshot assumption, source availability, method status, limitations and original reasons. H=28 remains inventory-gated; numerical replenishment and uncertainty stay unavailable.

This creates the same JSON/Markdown outputs with a fresh blank checklist. The historical forecast-only F01–F03 assessments below remain attached to their original record bundle and are not transferred to changed records. The bridge does not automatically assign human-review states or transparency outcomes.

**Inventory-linked preparation completed — 23 October 2026:** Chathuranga manually ran the inventory-backed command above. Its manifest records preparation time `2026-10-23T06:09:37.526263+00:00`, operator `Chathuranga` and review schema `issue-168-review-v2`. The original local directory is `research-materials/decision-support/issue-168-inventory-v1/`; unchanged shared copies are available as [records.md](../../reports/decision-support/issue-168-inventory-v1/records.md), [records.json](../../reports/decision-support/issue-168-inventory-v1/records.json), [review.json](../../reports/decision-support/issue-168-inventory-v1/review.json) and [manifest.json](../../reports/decision-support/issue-168-inventory-v1/manifest.json). Fifteen selected 1/7/14-day records contain matching constructed-scenario inventory evidence; the five h=28 records retain gated inventory fields. All 160 checklist outcomes are blank. No inventory-linked assessment or complete summary is claimed.

The new record-bundle SHA-256 is `dc029ba66c07009202f17643a3565f550e7ac2aa7c23ac411ea15f964c91937a`. Its source binds prospective SHA-256 `5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4` and inventory-manifest SHA-256 `5d9ea6206c277f4853dc39fc5fdffdcd93f1df629c67fc5a8f2b524038c0fda9`; the review's v2 record hash binds this new context. Publication checks matched the JSON/Markdown/template hashes and all four copied files without assigning outcomes or changing the historical F01–F03 checklist. These are local identity checks, not independent peer review. The [evidence index](../../reports/README.md#inventory-linked-records) distinguishes both assessment contexts.

The completed human preparation establishes record links and execution attribution above. F01–F03's human-confirmed findings are recorded below; the complete 20-record summary remains pending until the remaining checklist entries are completed. Keep selected, prepared and reviewed populations separate. No outcome is claimed from synthetic tests or a blank template. Prototype-dependent visibility and final presentation acceptance remain separate from record-content assessment.

## 3. Evaluation Readiness and Pending Evidence

F01–F03 (`SKU_1`, `WH_1`, origin `2024-12-02`, horizons `1-day`, `7-day` and `14-day` respectively) each have eight human-confirmed record-level assessments dated 23 October 2026, with assessor Chathuranga. The matrix below transcribes those outcomes; all checks are recorded as applicable. Detailed field references and reasons are available in the tracked [review.json](../../reports/decision-support/issue-168-json/review.json), linked by assessment ID and criterion to [records.json](../../reports/decision-support/issue-168-json/records.json) entries `records[0]`, `records[1]` and `records[2]` respectively. The ignored local originals remain unchanged. The source record-bundle hash is documented in Section 2. F04–F20's 136 checks remain blank and are excluded from this partial matrix.

| Record | Transparency check | Outcome | Evidence / reason |
|---|---|---|---|
| F01 | Forecast visibility | `met` | `forecast_demand`, `forecast_origin` and `forecast_horizon` explicitly show the forecast value and timing. |
| F01 | Risk visibility | `not assessable` | `inventory_risk_evidence` and `inventory_risk_provenance` are null; `unavailable_fields` retains the pending-upstream reasons. |
| F01 | Recommendation traceability | `not assessable` | `replenishment_recommendation` is null with an explicit unavailable reason; no recommendation or supporting evidence was supplied. |
| F01 | Uncertainty visibility | `not assessable` | `uncertainty_or_error` is null with the source reason `no_agreed_method`; retrospective errors are excluded. |
| F01 | Assumption visibility | `met` | `assumptions` explicitly states the inclusive target interval and next-day/cumulative-window meaning. |
| F01 | Limitation visibility | `met` | `limitations` states the simulated-data, stockout-label, selection, missing-evidence, prior-exposure and prototype-visibility limitations. |
| F01 | Human-review transparency | `met` | `human_review_status` is `not_assessed`, accompanied by the explanation in `human_review_reasons`. This evaluates visibility of the state, not completion of managerial review. |
| F01 | Source distinction | `met` | `forecast_provenance` and `component_provenance` identify the forecast and responsible decision-support sources; missing inventory provenance has an explicit reason. |
| F02 | Forecast visibility | `met` | `forecast_demand` is 89.08327726179623 units; origin `2024-12-02` and horizon `7-day` are explicit. Evidence identifies cumulative demand for 3–9 December. |
| F02 | Risk visibility | `not assessable` | Inventory-risk evidence and provenance are null, with explicit pending-upstream reasons. |
| F02 | Recommendation traceability | `not assessable` | No replenishment recommendation or supporting evidence was supplied; the unavailable reason is retained. |
| F02 | Uncertainty visibility | `not assessable` | Uncertainty/error information is unavailable with reason `no_agreed_method`; retrospective errors are excluded. |
| F02 | Assumption visibility | `met` | `assumptions` explicitly states the inclusive 3–9 December target interval and cumulative-window meaning. |
| F02 | Limitation visibility | `met` | Simulated-data, stockout-label, selection, missing-evidence, prior-exposure and prototype-visibility limitations are explicit. |
| F02 | Human-review transparency | `met` | `not_assessed` is accompanied by its explanatory human-review reason; visibility does not establish completed managerial review. |
| F02 | Source distinction | `met` | Forecast provenance, component ownership and reasons for missing inventory provenance remain distinguishable. |
| F03 | Forecast visibility | `met` | `forecast_demand` is 170.942626953125 units; origin `2024-12-02` and horizon `14-day` are explicit. Evidence identifies cumulative demand for 3–16 December. |
| F03 | Risk visibility | `not assessable` | Inventory-risk evidence and provenance are null, with explicit pending-upstream reasons. |
| F03 | Recommendation traceability | `not assessable` | No replenishment recommendation or supporting evidence was supplied; the unavailable reason is retained. |
| F03 | Uncertainty visibility | `not assessable` | Uncertainty/error information is unavailable with reason `no_agreed_method`; retrospective errors are excluded. |
| F03 | Assumption visibility | `met` | `assumptions` explicitly states the inclusive 3–16 December target interval and cumulative-window meaning. |
| F03 | Limitation visibility | `met` | Simulated-data, stockout-label, selection, missing-evidence, prior-exposure and prototype-visibility limitations are explicit. |
| F03 | Human-review transparency | `met` | `not_assessed` is accompanied by its explanatory human-review reason; visibility does not establish completed managerial review. |
| F03 | Source distinction | `met` | Forecast provenance, component ownership and reasons for missing inventory provenance remain distinguishable. |

Each assessed record has five `met` and three `not assessable` checks. Each criterion currently has three assessed applicable cases; the other 17 selected cases remain unassessed. No 20-record completion rate or aggregate transparency proportion is reported, and no summary command has been executed on this partial checklist. Missing upstream information remains explicit rather than being replaced with assumed values.

Before recording an assessment, identify each reviewed record using `SKU_ID`, `Warehouse_ID`, forecast origin and horizon, together with its source artifact/version and upstream provenance. For each applicable check, retain the outcome and a record-specific evidence reference or reason. Do not treat a checklist row as a reviewed record or treat an unperformed review as an observed failure.

## 4. Current Findings and Reporting Limits

- The retained preparation contains **20 selected forecasts, 20 populated records and 3 evaluated records (F01–F03)**. Twenty-four checklist entries contain human-confirmed outcomes; the other 136 remain blank. This document reports their partial matrix, with no full-roster completion rate, aggregate proportion of checks met, or prototype evaluation result.
- Issues [#72](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/72) and [#73](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/73) provide the approved criteria and record implementation. Their completion does not by itself establish evaluated management-facing outputs.
- The [forecast contract](../forecast-api-contract.md) from [Issue #132](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/132) provides reviewed forecasting semantics. Actual assessment must cite the record and evidence used; it must not infer a record's completeness from contract acceptance alone.
- Inventory-dependent findings require reviewed evidence and interpretation from [Issue #85](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/85). Its pending work does not prevent preparation of the presentation requirements below.
- When results are available, report the number of reviewed records, the applicable population for each check, and counts for `met`, `not met` and `not assessable`. Identify the denominator of every reported proportion and retain unavailable cases visibly. Do not calculate a percentage from a zero denominator.
- Synthetic/test records, if reviewed, must be labelled as such and kept distinguishable from assessments using accepted project evidence. Passing implementation tests does not establish presentation quality or operational effectiveness.

## 5. Semantic/Presentation Handoff for Tinosh

The requirements below restate existing methodology and record semantics for human review. They do not introduce a new schema, adapter, uncertainty method or review rule. The current implementation is [DecisionSupportRecord](../../src/decision_support/records.py); technical integration must preserve the reviewed meaning rather than infer unavailable values.

| Information | Presentation requirement |
|---|---|
| Identity and timing | Keep `sku_id`, `warehouse_id`, `forecast_origin` and `forecast_horizon` visible and traceable. Preserve source artifact/version references where available. |
| Forecast | Show `forecast_demand` with its units and horizon meaning. One day means next-day demand; 7/14/28 days mean cumulative demand over the complete window, not a daily path. Twenty-eight days means four weeks, not an exact calendar month ([forecast contract §5](../forecast-api-contract.md#5-forecast-meaning)). |
| Provenance | Preserve `forecast_provenance`, `inventory_risk_provenance` and `component_provenance`. Distinguish forecasting, inventory-risk/replenishment and responsible decision-support sources. |
| Inventory-risk evidence | Present `inventory_risk_evidence` using Didilani's reviewed labels, assumptions and interpretation. Do not relabel threshold-exposure evidence as observed stockout prediction or derive overstock from absence of a crossing. |
| Replenishment | Show `replenishment_recommendation` only when defensibly supplied under an approved method, with its supporting evidence. Keep it advisory; do not present it as an approved purchase order. |
| Error and uncertainty | Preserve the meaning and source of `uncertainty_or_error`. Retrospective forecast error is evaluation evidence, not prospective confidence or an uncertainty interval ([forecast contract §6.2](../forecast-api-contract.md#62-fields-excluded-from-prospective-views)). The forecast contract's `unavailable` / `no_agreed_method` uncertainty information remains explicit. |
| Unavailable information | Show the field and its reason from `unavailable_fields`. Preserve the meanings of `not produced`, `not applicable`, `pending upstream output` and `not assessed` from [methodology §12.3](responsible-decision-support-methodology.md#123-missing-and-unavailable-information). Do not silently map missing information to zero, false or a recommendation. These evaluation states do not define an interchange encoding or authorize automatic mapping of upstream reason codes. |
| Assumptions and limitations | Keep `assumptions`, `limitations` and `evidence` accessible alongside the result. Preserve the publisher-simulated Kaggle-dataset limitation and the fact that zero-variance `Stockout_Flag` cannot validate stockout predictions. Retain any evidence-specific temporal or methodological limitations. |
| Management consideration | Present `management_consideration` as guidance for human consideration. Final decisions remain with a responsible person; presentation must not imply autonomous ordering. |
| Human review | Show `human_review_status` together with `human_review_reasons`. `not_assessed` means review has not been assessed; it is not clearance. `review_required` must retain its stated reason. Do not invent triggers or numerical thresholds. |
| Twenty-eight-day downstream use | Retain approved forecast identity, but do not imply approval of 28-day inventory interpretation, replenishment or human-review triggers. Show the relevant unavailability/approval reason until separately approved ([forecast contract §10](../forecast-api-contract.md#10-shared-forecasting-api-boundaries); [DR-011 component-review boundary](../decisions/DR-011-decision-support-output-structure.md#revised-forecasting-interface-and-component-review)). |

DR-011 explains why information is unavailable, while methodology §12.3 also distinguishes an unperformed assessment. Forecasting reason codes such as `no_agreed_method` remain source information; their mapping to decision-support states and concrete encoding is pending Dewmi's review with the producing owners under [integration blocker B9](../integration-contract-readiness.md#9-blockers) and [forecast contract §9](../forecast-api-contract.md#9-retained-export-unavailable-and-lookup-behaviour). The preparation stores field-specific explanatory reasons in `unavailable_fields` and preserves original producer codes. A final cross-component reason vocabulary remains separate from these internal records.

Dewmi owns responsible-use meaning and reviews the later presentation. Tinosh implements the reviewed technical presentation; Chathuranga and Didilani retain review of their respective upstream semantics.

## 6. Deferred Checks and Completion Requirements

| Pending check | Evidence needed before completion | Owner / tracking issue |
|---|---|---|
| Forecasting evidence access and acceptance | Make the chosen forecasting evidence accessible through an agreed handoff, retaining its source/version and provenance. If the retained export is used, supply the export and its reviewed hash reference; local existence alone does not establish consumer acceptance. Generated artifacts remain outside Git under the [storage policy](../artifact-storage-policy.md). | Chathuranga supplies forecasting evidence; Tinosh reviews technical consumption; Dewmi identifies the assessment source — [#132](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/132), [#168](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/168). |
| Record-level transparency assessment | Identified, reviewable records with identity, timing, provenance and source/version references; an outcome and supporting evidence/reason for each applicable check. | Dewmi — [#168](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/168), using the criteria and implementation from #72/#73. |
| Inventory-risk and recommendation interpretation | Didilani's reviewed evidence and downstream meaning handoff, with approval boundaries and unavailable reasons retained. | Didilani supplies and reviews upstream meaning; Dewmi preserves it in the assessment — [#85](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/85), #168. |
| Unavailable-state mapping | Reviewed mapping and encoding between upstream reason codes and decision-support states; retain the original reason while the mapping remains unresolved. | Dewmi with producing owners — [B9](../integration-contract-readiness.md#9-blockers), #72/#73; presentation implications tracked in #168. |
| Visibility and readability in the prototype | Rendered screens/views from Tinosh showing labels, provenance, unavailable reasons, assumptions, limitations, advisory wording and human-review states/reasons. Record contents alone cannot establish that these are visible in the interface. | Tinosh implements the reviewed presentation; Dewmi evaluates it — [#86](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/86), #168, subject to the agreed integration scope. |
| Report-ready measured findings | A traceable assessment matrix and explicit reviewed/applicable populations and denominators. | Dewmi — #168. |
| Final presentation acceptance | Dewmi's review of Tinosh's implementation, with relevant upstream owner review and unresolved checks recorded explicitly. | Dewmi, with Chathuranga and Didilani reviewing their upstream meaning — #168; Tinosh's integration under #86. |


Issue #145 and Issue #153 are closed. Their completed preparation and historical references remain relevant, but the unfinished record-mapping, transparency assessment and presentation handoff are now tracked under Issue #168. Issue #168 remains open until the required human approvals, record-level evidence, assessment outcomes and handoff reviews are completed. A mapping-only or preparation-only PR must reference Issue #168 without closing it.


## 7. Technical Verification of Decision-Support Records

The existing responsible decision-support implementation was inspected to establish which transparency-related information is supported by the record structure. The review covered `src/decision_support/records.py` and the associated tests in `tests/test_decision_support_records.py`.

The `DecisionSupportRecord` structure includes forecast identity and horizon, forecast demand, inventory-risk evidence, replenishment recommendations, uncertainty or error information, assumptions, limitations, supporting evidence, management considerations, human-review status and reasons, and component provenance.

The implementation also requires explicit reasons when specified upstream information is unavailable. Human-review status is restricted to supported values, and explanatory reasons must be provided. These safeguards help preserve the distinction between available evidence and information that has not been assessed or supplied.

**Validation performed:** The command `python -m pytest tests/test_decision_support_records.py -q` completed successfully, with 11 tests passed.

**Interpretation:** These findings provide evidence that the record structure and its tested validation behaviour support responsible decision-support requirements. However, they do not demonstrate that populated records satisfy every transparency criterion or that the information is clearly presented to managers.

The record-level evaluation outcomes therefore remain pending until applicable decision-support records and supporting upstream evidence have been reviewed. Prototype visibility, managerial interpretation, and final presentation acceptance also require separate assessment.
