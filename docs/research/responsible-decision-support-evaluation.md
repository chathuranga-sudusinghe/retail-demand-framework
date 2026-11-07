# Responsible Decision-Support Evaluation

**Presentation status reconciled — 30 October 2026:** [The C1 decision/closeout record](../research-design.md#164-human-decisions-and-c1-closeout-record) records W1 interpretation/display acceptance and automatic-review-rule deferral as reported by Chathuranga on 29 October. Existing dated preparation/assessment evidence below remains unchanged. W2 actual-view semantic/readability review remains under #182 once #201 supplies a reviewable revision; the 160 record checks are not repeated or treated as managerial clearance.

**Status — 23 October 2026:** PR #175 merged and closed #164/#168 as delivered implementation/evidence milestones. Chathuranga confirmed all 160 record-level checks on the 20 inventory-linked records and manually generated the summaries. Prototype/presentation checks and final component acceptance remain separate. DR-012 group approval is recorded under [#177](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/177); historical record/manifest labels and forecast-only F01–F03 outcomes remain unchanged.

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

This is a purposive, case-based selection of 20 forecasting rows from the retained Issue #132 fixed-origin export. Chathuranga's human-run preparation on 23 October 2026 populated all 20 `DecisionSupportRecord` instances. The historical forecast-only bundle has confirmed outcomes for F01–F03 and leaves F04–F20 unassessed. The separate inventory-linked bundle now has confirmed outcomes for all 20 records, recorded in Section 3.1. The selection does not claim population-wide representativeness.

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

**Record linkage status:** All selected forecasting keys now have populated decision-support records. Numeric forecast horizons map to explicit string labels through Section 2.1, with target meaning retained in evidence. Inventory-risk and replenishment evidence remains unavailable where no matching source was supplied. The 28-day horizon remains restricted to forecast-transparency scope. Section 3 preserves the historical forecast-only F01–F03 findings; Section 3.1 records the separately confirmed assessment of all 20 inventory-linked records.


**Downstream evidence boundary:** Reviewed inventory-risk and replenishment outputs will be linked only where an actual matching source exists. Missing evidence will be recorded explicitly with record-specific reasons rather than replaced with assumptions or used to silently exclude reviewable cases. The implemented inventory bridge and retained results are described below. Remaining consumer/presentation decisions are separate; #164 is a closed historical milestone. The 28-day horizon is retained for forecast-transparency assessment only; downstream inventory and replenishment interpretation remains deferred.

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

The original `issue-168-review-v1` forecast-only bundles remain supported without migration. `summarize_files` first verifies their original record hash, Markdown hash, source binding, blank-template hash and schema agreement with the preparation manifest. It then applies the same identity/coverage/outcome checks. Legacy input files are never rewritten, and legacy assessments cannot be reused for inventory-linked records. Summary metadata preserves the original preparation timestamp and generator code hashes as historical receipts; those hashes need not match current source. The historical forecast-only checklist is incomplete and cannot produce a complete summary in that state. It is retained as history; completing it is not required to repeat the separate, already completed inventory-linked assessment.

After the human-run [inventory evaluation](inventory-risk-evaluation-protocol.md#122-run-the-implemented-inventory-evaluation), prepare a separate bundle that includes its prospective inventory evidence:

```bash
.venv/bin/python -m src.decision_support.assessment prepare \
  --operator Chathuranga \
  --inventory-evidence research-materials/inventory-risk/issue-164/evaluation-v1/prospective.json \
  --output research-materials/decision-support/issue-168-inventory-v1
```

The bridge verifies the adjacent manifest, all three output-file hashes, registered dataset provenance, forecast-source binding and all 1,000 exact forecast keys. Evaluation/report files are hashed as opaque bytes; only prospective records are interpreted. All three snapshot policies are checked for consistent markers, statuses, basis, valid/null balances, exposure states and existing DR-012 margins. It rejects retrospective fields, mismatched values, duplicate keys and any claim that a constructed scenario established source timing. These consistency checks do not authenticate a mutable manifest or prove scientific correctness. It links only matching 1/7/14-day inventory evidence into `inventory_risk_evidence` and `inventory_risk_provenance`, preserving the snapshot assumption, source availability, method status, limitations and original reasons. H=28 remains inventory-gated; numerical replenishment and uncertainty stay unavailable.

This creates the same JSON/Markdown outputs with a fresh blank checklist. The historical forecast-only F01–F03 assessments below remain attached to their original record bundle and are not transferred to changed records. The bridge does not automatically assign human-review states or transparency outcomes.

**Inventory-linked preparation completed — 23 October 2026:** Chathuranga manually ran the inventory-backed command above. Its manifest records preparation time `2026-10-23T06:09:37.526263+00:00`, operator `Chathuranga` and review schema `issue-168-review-v2`. The original local directory is `research-materials/decision-support/issue-168-inventory-v1/`; shared files are available as [records.md](../../reports/decision-support/issue-168-inventory-v1/records.md), [records.json](../../reports/decision-support/issue-168-inventory-v1/records.json), [review.json](../../reports/decision-support/issue-168-inventory-v1/review.json) and [manifest.json](../../reports/decision-support/issue-168-inventory-v1/manifest.json). Fifteen selected 1/7/14-day records contain matching constructed-scenario inventory evidence; the five h=28 records retain gated inventory fields. Preparation initially left all 160 checklist outcomes blank. Chathuranga subsequently confirmed the full assessment in Section 3.1; only the editable checklist was changed, identically in the local and tracked copies. His completed summary run is recorded in Section 3.2; the original records and preparation manifest remain unchanged.

The new record-bundle SHA-256 is `dc029ba66c07009202f17643a3565f550e7ac2aa7c23ac411ea15f964c91937a`. Its source binds prospective SHA-256 `5c731c9e535078caa85a9cad1df49596eda4022dfbcdf5a54c43959dcbcfd8d4` and inventory-manifest SHA-256 `5d9ea6206c277f4853dc39fc5fdffdcd93f1df629c67fc5a8f2b524038c0fda9`; the review's v2 record hash binds this new context. Publication checks matched the JSON/Markdown/template hashes and all four copied files without assigning outcomes or changing the historical F01–F03 checklist. These are local identity checks, not independent peer review. The [evidence index](../../reports/README.md#inventory-linked-records) distinguishes both assessment contexts.

The completed human preparations establish record links and execution attribution above. The historical forecast-only bundle retains its partial F01–F03 findings; the inventory-linked bundle has the separately confirmed full-roster assessment in Section 3.1 and human-generated summaries in Section 3.2. Keep selected, prepared and reviewed populations separate. No outcome is claimed from synthetic tests or a blank template. Prototype-dependent visibility and final presentation acceptance remain separate from record-content assessment.

## 3. Recorded Assessments and Remaining Evidence

**Historical forecast-only assessment:** F01–F03 (`SKU_1`, `WH_1`, origin `2024-12-02`, horizons `1-day`, `7-day` and `14-day` respectively) each have eight human-confirmed record-level assessments dated 23 October 2026, with assessor Chathuranga. The matrix below transcribes those outcomes; all checks are recorded as applicable. Detailed field references and reasons are available in the tracked [review.json](../../reports/decision-support/issue-168-json/review.json), linked by assessment ID and criterion to [records.json](../../reports/decision-support/issue-168-json/records.json) entries `records[0]`, `records[1]` and `records[2]` respectively. The ignored local originals remain unchanged. The source record-bundle hash is documented in Section 2. F04–F20's 136 checks remain blank in this historical bundle and are excluded from this partial matrix.

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

Within this historical forecast-only bundle, each assessed record has five `met` and three `not assessable` checks. Each criterion has three assessed applicable cases; the other 17 selected cases remain unassessed. No full-roster completion rate or aggregate transparency proportion is reported for this historical bundle, and no summary command has been executed on its partial checklist. Missing upstream information remains explicit rather than being replaced with assumed values.

Before recording an assessment, identify each reviewed record using `SKU_ID`, `Warehouse_ID`, forecast origin and horizon, together with its source artifact/version and upstream provenance. For each applicable check, retain the outcome and a record-specific evidence reference or reason. Do not treat a checklist row as a reviewed record or treat an unperformed review as an observed failure.

### 3.1 Human-confirmed inventory-linked record assessment

**Human confirmation — 23 October 2026:** Codex prepared the complete 20-record draft with case-specific evidence for human review. After being shown the proposed outcomes, their scope, assessor attribution and assessment date, Chathuranga explicitly replied, "confirmed. let's move" in the project working conversation. Codex then transcribed those confirmed decisions into both copies of the inventory-linked `review.json`, with assessor `Chathuranga` and date `2026-10-23`. No Dewmi assessment, group approval or independent peer review is inferred from that individual confirmation. Chathuranga subsequently ran the summarizer himself, as recorded in Section 3.2. The historical F01–F03 outcomes above remain unchanged and are not reused for this context.

The confirmed assessment covers all 20 records in [inventory-linked records.json](../../reports/decision-support/issue-168-inventory-v1/records.json), SHA-256 `dc029ba66c07009202f17643a3565f550e7ac2aa7c23ac411ea15f964c91937a`, and the matching [readable records](../../reports/decision-support/issue-168-inventory-v1/records.md). The source index in each row identifies the exact zero-based `records` entry; the existing SKU/warehouse/origin/horizon roster in Section 2 applies to these identities. Only the contents of the prepared records are considered. Visibility/readability in a rendered prototype remains a separate check.

All eight checks are recorded as applicable for all 20 cases, including cases with unavailable upstream evidence, as confirmed by Chathuranga. Following [methodology §12.2](responsible-decision-support-methodology.md#122-measurable-transparency-checks), an unavailable output is recorded as `not assessable`, with its reason retained, rather than treated as a failure or silently removed.

| Code | Existing criterion | Confirmed outcome and record-specific evidence basis |
|---|---|---|
| FV | Forecast visibility | `met`: `record.forecast_demand`, `forecast_origin` and `forecast_horizon` are populated; `evidence` and `assumptions` identify units, inclusive target dates and next-day/cumulative-window meaning. |
| RV | Risk visibility | `met` for the 15 1/7/14-day cases: `record.inventory_risk_evidence` exposes the conditional scenario basis, source status, origin/forecast exposure state, buffer, margin and method status; `inventory_risk_provenance` links the supplied source. This finding concerns visibility of conditional reorder-threshold exposure, not approval of DR-012, a high/low risk classification or actual stockout accuracy. For the five h=28 cases, the outcome is `not assessable`: evidence/provenance are null and their `unavailable_fields` reasons retain `28_day_downstream_use_requires_separate_approval`. |
| RT | Recommendation traceability | `not assessable`: `record.replenishment_recommendation` is null in each case; `unavailable_fields.replenishment_recommendation` states that no approved numerical replenishment output was supplied. An exposed reason does not establish traceability of an actual recommendation. |
| UV | Uncertainty visibility | `not assessable`: `record.uncertainty_or_error` is null in each case; `unavailable_fields.uncertainty_or_error` preserves `no_agreed_method`. Retrospective errors are not substituted for prospective uncertainty. |
| AV | Assumption visibility | `met`: `record.assumptions` states each target window, horizon meaning, fixed reorder point, no-receipt/adjustment scenario and hypothetical starting-balance basis. Their presence in a record does not prove manager-facing display. |
| LV | Limitation visibility | `met`: `record.limitations` discloses publisher-simulated data, zero-variance stockout labels, purposive selection, prior validation/exploratory exposure, unknown source timing and method/unsupported-output restrictions. The h=28 cases additionally retain their scope restriction. |
| HR | Human-review transparency | `met`: `record.human_review_status` is `not_assessed`, accompanied by `human_review_reasons`. The state and reason are visible; this finding does not assert managerial review or clearance. Completing this transparency checklist does not change the managerial-review state inside the immutable prepared records. |
| SD | Source distinction | `met`: `record.forecast_provenance`, `component_provenance`, `evidence` and, where supplied, `inventory_risk_provenance` distinguish the component sources. Gated h=28 inventory provenance remains null with its explicit reason. A component name alone is not treated as evidence of an available inventory result. |

In the matrix, **M means human-confirmed `met`** and **U means human-confirmed `not assessable`**. All source indices below refer to this inventory-linked bundle, not the historical forecast-only bundle. The completed checklist SHA-256 is `91585207e718ada57aa29ffad782eb513638a62d0a98ae8a5a36b3fea1978fa7`. The original manifest still binds the initial blank template; its preparation-status text is historical and is not rewritten to imply assessment completion at preparation time.

| Case | Source index | Horizon | FV | RV | RT | UV | AV | LV | HR | SD |
|---|---|---:|---|---|---|---|---|---|---|---|
| F01 | `records[0]` | 1 | M | M | U | U | M | M | M | M |
| F02 | `records[1]` | 7 | M | M | U | U | M | M | M | M |
| F03 | `records[2]` | 14 | M | M | U | U | M | M | M | M |
| F04 | `records[3]` | 28 | M | U | U | U | M | M | M | M |
| F05 | `records[4]` | 1 | M | M | U | U | M | M | M | M |
| F06 | `records[5]` | 7 | M | M | U | U | M | M | M | M |
| F07 | `records[6]` | 14 | M | M | U | U | M | M | M | M |
| F08 | `records[7]` | 28 | M | U | U | U | M | M | M | M |
| F09 | `records[8]` | 1 | M | M | U | U | M | M | M | M |
| F10 | `records[9]` | 7 | M | M | U | U | M | M | M | M |
| F11 | `records[10]` | 14 | M | M | U | U | M | M | M | M |
| F12 | `records[11]` | 28 | M | U | U | U | M | M | M | M |
| F13 | `records[12]` | 1 | M | M | U | U | M | M | M | M |
| F14 | `records[13]` | 7 | M | M | U | U | M | M | M | M |
| F15 | `records[14]` | 14 | M | M | U | U | M | M | M | M |
| F16 | `records[15]` | 28 | M | U | U | U | M | M | M | M |
| F17 | `records[16]` | 1 | M | M | U | U | M | M | M | M |
| F18 | `records[17]` | 7 | M | M | U | U | M | M | M | M |
| F19 | `records[18]` | 14 | M | M | U | U | M | M | M | M |
| F20 | `records[19]` | 28 | M | U | U | U | M | M | M | M |

### 3.2 Human-run summary and criterion findings

Chathuranga manually executed the existing `assessment summarize` command against `research-materials/decision-support/issue-168-inventory-v1/` on 23 October 2026. It wrote [summary.json](../../reports/decision-support/issue-168-inventory-v1/summary.json) and [summary.md](../../reports/decision-support/issue-168-inventory-v1/summary.md), now copied unchanged into the shared report bundle. AI assistance did not rerun the summary command; it checked the saved outputs against the confirmed checklist and their source bindings.

The human-generated summary reports **20 selected forecasts, 20 prepared records, 20 reviewed records and 160 reviewed checks**, with assessor `Chathuranga`. Each criterion has 20 applicable cases and zero non-applicable cases. All applicable cases, including `not assessable`, remain in the met-proportion denominator.

| Criterion | Applicable denominator | Met | Not met | Not assessable | Met proportion |
|---|---:|---:|---:|---:|---:|
| Forecast visibility | 20 | 20 | 0 | 0 | 100% |
| Risk visibility | 20 | 15 | 0 | 5 | 75% |
| Recommendation traceability | 20 | 0 | 0 | 20 | 0% |
| Uncertainty visibility | 20 | 0 | 0 | 20 | 0% |
| Assumption visibility | 20 | 20 | 0 | 0 | 100% |
| Limitation visibility | 20 | 20 | 0 | 0 | 100% |
| Human-review transparency | 20 | 20 | 0 | 0 | 100% |
| Source distinction | 20 | 20 | 0 | 0 | 100% |

The five unassessable risk-visibility cases are F04/F08/F12/F16/F20, whose h=28 inventory fields remain gated. The zero met proportions for recommendation traceability and uncertainty reflect 20 unavailable upstream outputs in each criterion, not 20 observed `not met` failures. All records retain their unavailable reasons. The met risk-visibility findings concern disclosure of conditional reorder-threshold exposure and its provenance, not approved risk classifications or actual stockout accuracy. No overall cross-criterion score is introduced.

The summary binds record SHA-256 `dc029ba66c07009202f17643a3565f550e7ac2aa7c23ac411ea15f964c91937a` and completed-checklist SHA-256 `91585207e718ada57aa29ffad782eb513638a62d0a98ae8a5a36b3fea1978fa7`. Summary JSON SHA-256 is `6c3ba9308455c6df1de10f68b1afd8227797231738f490865fca14b99a9b8f5d`; summary Markdown SHA-256 is `41d0534d619dd6194a496ef52c4ec9329c2a30e11511e63defce375c95a2d7f3`. Read-only checks matched both summary copies to their human-generated originals, all criterion counts/denominators to the checklist, and the original preparation timestamp/code-hash receipt to the manifest. These are local consistency checks at repository HEAD `dd5bc9abffb468d9aff306011a068111d34e923d`, not independent peer approval. The retained `prepared_at` value describes record preparation; it is not a new summary-execution timestamp.

The record-level assessment and its summary are complete for this limited purposive roster. Rendered-prototype visibility/readability, final semantic/presentation acceptance and relevant component handoff reviews remain separate. Preserve the original records, preparation manifest and historical forecast-only checklist when reviewing or publishing these findings.

## 4. Current Findings and Reporting Limits

- The historical forecast-only bundle contains **20 selected forecasts, 20 populated records and 3 evaluated records (F01–F03)**. Its 24 confirmed outcomes and 136 blank entries remain unchanged. The inventory-linked bundle separately contains **20 assessed records and 160 human-confirmed outcomes**, with the completed human-run criterion summary in Section 3.2. No prototype evaluation result is claimed.
- Issues [#72](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/72) and [#73](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/73) provide the approved criteria and record implementation. Their completion does not by itself establish evaluated management-facing outputs.
- The [forecast contract](../forecast-api-contract.md) from [Issue #132](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/132) provides reviewed forecasting semantics. Actual assessment must cite the record and evidence used; it must not infer a record's completeness from contract acceptance alone.
- Inventory-dependent findings require reviewed evidence and interpretation from [Issue #85](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/85). The specification issue is closed; remaining interpretation and rendered review are scoped after #177. Existing evidence supports the presentation requirements below.
- Section 3.2 reports reviewed records, applicable populations, outcomes and every proportion denominator for the inventory-linked assessment. Unavailable cases remain visible; no zero-denominator proportion or pooled overall score is used.
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
| Twenty-eight-day downstream use | Retain approved forecast identity, but do not imply approval of 28-day inventory interpretation, replenishment or human-review triggers. Show the existing source reason with the accepted deferral context; any future inventory extension needs separate approval ([forecast contract §10](../forecast-api-contract.md#10-shared-forecasting-api-boundaries); [DR-011 component-review boundary](../decisions/DR-011-decision-support-output-structure.md#revised-forecasting-interface-and-component-review)). |

**Current handoff status — reconciled 5 November 2026:** DR-011 explains unavailable information, while methodology §12.3 distinguishes an unperformed assessment. [Dewmi’s direct W1 acceptance on 1 November](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/182#issuecomment-6555332904) accepts the documented interpretation/display baseline. The implemented preparation preserves source-specific reasons such as `no_agreed_method` in `unavailable_fields`; this accepted baseline does not require a new universal reason vocabulary. B9’s remaining presentation acceptance is the actual W2 review under #182/#201, not a repeat of W1 or the 160 record checks. Preserve the [forecast contract’s source meanings](../forecast-api-contract.md#9-retained-export-unavailable-and-lookup-behaviour).

Dewmi owns responsible-use meaning and reviews the later presentation. Tinosh implements the reviewed technical presentation; Chathuranga and Didilani retain review of their respective upstream semantics.

## 6. Deferred Checks and Completion Requirements

### W2 findings received — 7 November 2026

[Dewmi's eight-figure W2 review](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/182#issuecomment-6702201368)
supports content clarity and responsible interpretation subject to four
clarifications. It does not verify source data/hashes, rendering implementation
or other component acceptance. The comment does not identify the inspected Git
revision or bundle hash; Dewmi should supply that reference with her final scoped
decision. This records findings received, not final W2 acceptance.

| Requested clarification | Existing evidence / bounded follow-up |
|---|---|
| Zero source-confirmed origin crossings do not establish snapshot availability | Figure 01 already states that its origin counts do not establish source snapshot availability. |
| Define TN and FN in the worked inventory case | Figure 05 now spells out true negative (TN): neither forecast nor retrospective proxy crosses; false negative (FN): the proxy crosses but the forecast misses. Chathuranga regenerated the bundle on 7 November; Dewmi's affected-view recheck remains pending. These outcomes do not establish observed stockouts. |
| Show missed-crossing rates alongside agreement | Figure 02 already contains both rates; its accompanying caption states that high agreement can coexist with missed proxy events. |
| Do not reselect forecasting producers using final-origin results | Figure 08 already disclaims result-driven reselection; its accompanying caption states that designation was frozen before final results. |

After human regeneration, record the delivered revision and bundle identity and
ask Dewmi to recheck the affected Figure 05 and confirm the other three existing
explanations. Preserve the original 20 records, 160 outcomes and historical
manifests. Link the final scoped outcome from #201/#179 rather than duplicating
the review. [PR #218](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/218)
is Dewmi's separate group-report wording contribution. Its duplicated paragraph
was corrected at `b02c41f`; Chathuranga confirmed approval and merge on 7 November.
This follow-up does not rewrite that contribution or infer final W2 acceptance.

**Delivery tracking — updated 25 October 2026:** [PR #197](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/197) delivered the source-bound retained roster/case API and synthetic checks, closing #183. [#201](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/201), assigned to Didilani, continues the human-observed retained handoff, approved inventory views and component acceptance. Dewmi's interpretation/display handoff remains under [#182](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/182); subsequent acceptance is recorded under [#179](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/179). Tinosh retains his documented technical role and original implementation attribution. API code approval and automated serving evidence do not complete the rendered review below.

| Check | Current status / evidence needed before completion | Owner / tracking issue |
|---|---|---|
| Forecasting evidence access and acceptance | The merged retained API loads the exact assessed records and validates their forecast/inventory joins. Independently reviewed installed-source verification and actual producer/consumer acceptance remain separate; local existence and automated HTTP success do not establish them. Protected inputs remain outside Git under the [storage policy](../artifact-storage-policy.md). | Chathuranga supplies/reviews forecast meaning; Tinosh reviews technical consumption; Dewmi reviews assessment-source meaning; Didilani executes the bounded retained continuation — #201/#179. #132/#168 remain historical evidence references. |
| Record-level transparency assessment | Completed for the 20 inventory-linked records: Chathuranga confirmed all 160 outcomes with case-specific evidence/reasons; identities, timing and provenance are retained in Section 3.1 and the completed checklist. This individual assessment is distinct from component/presentation acceptance. | Dewmi — [#168](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/168), using the criteria and implementation from #72/#73; recorded assessor: Chathuranga. |
| Inventory-risk and recommendation interpretation | Inventory interpretation/report insertion and analytical reviews were delivered under #181/#188/#190. Review the actual consumer/rendered representation separately, retaining approval boundaries and unavailable reasons. | Didilani reviews upstream meaning; Dewmi preserves it in responsible presentation — #201/#182/#179. #85/#168 remain historical evidence references. |
| Unavailable-state mapping | Reviewed mapping and encoding between upstream reason codes and decision-support states; retain the original reason while the mapping remains unresolved. | Dewmi with producing owners — [B9](../integration-contract-readiness.md#9-blockers), #182; implementation/review handoff under #201/#179. #72/#73/#168 remain historical context. |
| Visibility and readability in the prototype | Actual rendered screens/views showing labels, provenance, unavailable reasons, assumptions, limitations, advisory wording and human-review states/reasons. Record contents and retained HTTP responses alone cannot establish visibility/readability. | Didilani executes the bounded #201 continuation; Tinosh retains technical integration/review responsibility; Dewmi evaluates responsible presentation, with upstream reviewers under #179. |
| Report-ready measured findings | Available for the limited record-level roster in Section 3.2 and the human-run summary: 20 reviewed records, 160 checks, criterion-level counts, applicable populations and explicit denominators. Interpretation/component review remains separate. | Dewmi's interpretation under #182/#179; historical evidence #168; recorded assessment and summary execution: Chathuranga. |
| Final presentation acceptance | Dewmi's review of the actual delivered views, with relevant upstream owner review and unresolved checks recorded explicitly. | Dewmi, with Chathuranga and Didilani reviewing their upstream meaning; #201 delivery and #179 acceptance record. Tinosh retains technical review; closed #86/#168 are historical context. |


**Issue closeout scope — 23 October 2026:** Merged PR #175 closed #164/#168 for the mapping, inventory scenario runner/results, populated records, completed record-level assessment, summaries and presentation requirements. This does not claim every original acceptance item or the full prototype is complete. DR-012 approval is recorded separately in [its approval record](../decisions/DR-012-inventory-risk-replenishment-methodology.md#group-approval-record); original preparation/run metadata remains unchanged. All closed issue references here are historical context, not active assignments. The next member tasks follow the reviewed #177 readiness baseline.


## 7. Technical Verification of Decision-Support Records

The existing responsible decision-support implementation was inspected to establish which transparency-related information is supported by the record structure. The review covered `src/decision_support/records.py` and the associated tests in `tests/test_decision_support_records.py`.

The `DecisionSupportRecord` structure includes forecast identity and horizon, forecast demand, inventory-risk evidence, replenishment recommendations, uncertainty or error information, assumptions, limitations, supporting evidence, management considerations, human-review status and reasons, and component provenance.

The implementation also requires explicit reasons when specified upstream information is unavailable. Human-review status is restricted to supported values, and explanatory reasons must be provided. These safeguards help preserve the distinction between available evidence and information that has not been assessed or supplied.

**Validation performed:** The command `python -m pytest tests/test_decision_support_records.py -q` completed successfully, with 11 tests passed.

**Interpretation:** These findings provide evidence that the record structure and its tested validation behaviour support responsible decision-support requirements. However, they do not demonstrate that populated records satisfy every transparency criterion or that the information is clearly presented to managers.

The completed inventory-linked record-level outcomes and human-generated summary are recorded in Sections 3.1–3.2. Prototype visibility, managerial interpretation and final presentation acceptance require separate assessment; closing the current milestone issues does not represent those checks as completed.
