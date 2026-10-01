# Data Cleaning and Validation Contract

**Status:** Issue #99 shared cleaning implementation is merged. The Issue #102 Parquet handoff design is human-approved; its implementation remains under human review. No repair, dataset processing or experiment is authorized by creating this document.
**Scope:** Raw source -> cleaned / validated representation.
**Related implementation:** [Issue #99](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/99) (shared cleaning) and [Issue #102](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/102) (persisted validated handoff).
**Parent architecture refactor:** [Issue #98](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/98).

## 1. Purpose and authority boundaries

This contract defines how source observations become a typed, keyed, ordered and provenance-bound validated representation without changing their observed meaning. Here, “cleaned” means validated representation preparation, not permission to repair observations. It connects existing requirements rather than introducing a second scientific specification.

| Existing authority | Ownership retained |
|---|---|
| [Dataset contract](dataset.md), Sections 1–6 | Source identity, field meanings/roles, native grain, documented quality profile and source-quality requirements |
| [Dataset contract](dataset.md), Sections 7/8 | Shared processed-view intent and member-specific data needs |
| [Shared data foundation](workflows/shared-data-foundation.md) | Repository-wide representation lifecycle and chronological preparation order |
| [Storage policy](artifact-storage-policy.md) | Locations, retention, immutability and archival boundaries |
| [Feature contract](forecasting-feature-engineering.md) | Predictor definitions, temporal availability, completeness and preprocessing semantics |
| [Protocol](protocol.md) | Authorized chronological windows, eligibility, evaluation/selection and experiment gates |
| [Applied MLOps](workflows/applied-mlops.md) | Reproducibility, provenance, integrity and human-review workflow |
| [Research design](research-design.md) and [Decision Records](decisions/README.md) | Research rationale and approved decisions |

This document owns validation/parsing/sorting behavior and the validated-handoff evidence contract. [src/data/data_cleaning.py](../src/data/data_cleaning.py) is the authoritative reusable cleaning/validation implementation owner. [src/data/validated_handoff.py](../src/data/validated_handoff.py) delegates to it and owns persistence/orchestration only. `src/analysis/` owns descriptive research analysis only. Its modules consume a typed, validated shared DataFrame; retained command-line entry points delegate loading and validation to data_cleaning.py. No competing shared-source loader or validation implementation remains in those analysis modules. This does not replace dataset.md's quality requirements or change the frozen forecasting contract. Implementation acceptance and specific dataset preparation remain separate human-review gates.

## 2. Input contract

### Source and observation identity

Use the **High-Dimensional Supply Chain Inventory Dataset**, the simulated source selected in [dataset.md](dataset.md#1-selected-source-dataset) and [DR-001](decisions/DR-001-dataset-selection.md). A file name alone is not a source version: bind preparation to the exact local source snapshot and its provenance. Raw source bytes remain unchanged under data/raw/.

The native observation key is Date + SKU_ID + Warehouse_ID under [DR-002](decisions/DR-002-forecasting-analytical-unit.md). A validated representation preserves one observation per native key; it does not aggregate warehouses, products or dates. Row positions and a regenerated DataFrame index are not observation identities.

### Required schema and validation modes

- **Shared source-quality mode:** Require all fifteen named source columns in [dataset.md Section 3](dataset.md#3-source-column-data-dictionary). Apply the source-quality checks to the explicitly authorized records. Preserve source fields for the approved shared representation; do not equate it with a forecasting-only projection.
- **Downstream forecasting demand-view mode:** Require Date, SKU_ID, Warehouse_ID and Units_Sold. This projection is not the shared cleaned dataset itself. The existing execution loader deliberately projects those columns. Passing this mode validates the demand view only; it does not certify excluded inventory, supplier, price or source-forecast fields.

Record mode, required/observed columns and deliberate projection/scope in the audit. Column names must be unambiguous and unique; missing required fields or duplicate required headers block consumption. Record unexpected columns/schema drift for review rather than silently renaming or treating them as predictors. A declared projection selects fields for a purpose; it is not a repair of the source.

### Type expectations

| Field class | Representation expectation |
|---|---|
| Date | Valid, nonmissing calendar date; timezone-naive and at midnight. Parse calendar text without truncating timestamps or shifting timezones. Reject numeric timestamp interpretations |
| SKU_ID and Warehouse_ID | Nonmissing, nonblank, unpadded text; preserve exact identities, including leading zeros |
| Supplier_ID and Region in shared mode | Nonmissing/nonblank text under the dataset schema; report surrounding whitespace and identity/category inconsistencies without normalization |
| Count fields identified by the dataset dictionary | Finite, nonnegative whole-unit numerical values; do not round fractional input into validity |
| Cost/price fields | Finite, nonnegative numerical values; no source-derived upper cap or price/cost relationship threshold is invented |
| Binary flags | Values in the documented binary domain; preserve zero as a valid value |
| Source Demand_Forecast | Numerical source-quality evidence when authorized; finiteness/parsing checks do not approve its use as a predictor or target |

Numerical parsing may change the storage dtype while preserving each observed value. Missing demand requires explicit unavailable status and the consumption rules below; it must never become zero. Exact on-disk dtypes/serialization belong to the reviewed persistence schema, not an undocumented inference from a CSV file.

## 3. Validation checks and failure handling

Apply [dataset.md Section 6](dataset.md#6-shared-data-quality-checks) within the declared mode and authorized scope. Record checks that are not applicable or not inspected, with reasons; absence of a check is not a pass.

| Check | Required behavior and evidence |
|---|---|
| Required fields/schema | Check required field presence and unique names/headers; record schema differences. Missing/ambiguous required fields fail |
| Parsing/types | Check dates, numerical parses, nonfinite values and declared text domains. Diagnostic parse failures may be represented as missing in an audit copy, but retain the distinction from source missingness; do not publish failed parses as valid observations |
| Duplicate rows/native keys | An exact duplicate has identical values in all fifteen source columns; report every member separately without deleting it. A repeated Date + SKU_ID + Warehouse_ID is a duplicate business key even when other fields differ; report conflicting groups separately. Both block shared handoff pending review; no approved duplicate-deletion rule exists |
| Missing/blank values | Audit by field and scope. Missing keys or invalid parses block use. Shared source-quality defects require review before acceptance; an unavailable demand value in the existing forecasting mode stays missing and is subject to unchanged feature/target eligibility, not imputation or a blanket completeness claim |
| Identifiers | Check presence, text validity, whitespace and SKU/warehouse/supplier consistency. Profile relationships without inventing a fixed supplier/region mapping or merging identities |
| Ordering/continuity | Report source order and daily coverage per SKU–warehouse; sort deterministically for consumption. Record gaps without adding dates. Strict fold/target coverage and predictor-history completeness remain governed by the protocol/feature contract |
| Numerical validity | Check negative counts/costs/prices, fractional count values, invalid binary flags and nonfinite quantities where applicable. Fail/report defects without clipping or rounding |
| Source quality/ranges | Audit authorized demand distribution, inventory/price ranges and the Inventory_Level/Reorder_Point/Order_Quantity relationships required by dataset.md. Documented extrema are observations, not approved rejection thresholds; semantic anomalies require review |
| Zero/near-zero variance | Report relevant field variability and the documented Stockout_Flag limitation. No universal near-zero threshold, automatic field removal or new target use is approved |
| Leakage-sensitive fields | Retain field-role exclusions from dataset.md and the feature contract. Source forecasts and retrospectively recorded operational values do not become origin-time model inputs because they passed quality validation |
| Documented source profile | Compare authorized evidence with the applicable dataset profile. Full-source historical counts/cardinalities are not requirements for a partial chronological view; disclose scope and drift, without manufacturing the documented profile |

Missing Date/SKU_ID/Warehouse_ID, invalid required keys or numeric observations and shared-mode missing/blank source fields block the shared handoff. Diagnostics preserve defects; no accepted dataset is produced by dropping bad rows. Statistical outliers may be profiled/flagged, but unusual magnitude alone is not invalidity and does not justify clipping/deletion. Only objective schema/domain/coverage defects block validation; profiling findings do not establish new numerical thresholds.

A hard validation failure stops dependent consumption and preserves diagnostics where possible. An audit/report-only finding must remain visible and may not be presented as fully validated shared data before review. Record validation mode, findings, failure/unavailable reasons and acceptance status separately from model eligibility and experiment completion.

The current forecasting helpers may retain missing demand or gaps as unavailable history using their existing options. Strict downstream checks still apply. This contract adds no row-exclusion or incomplete-population exception to the protocol.

## 4. Cleaning policy: representation changes versus observation changes

Permitted representation preparation is explicit schema checking, value-preserving date/numerical parsing, declared column projection, authorized chronological isolation and deterministic sorting. Preserve the source and record the preparation steps. Resetting an incidental row index does not replace the native key. Text-to-date and numeric-text-to-number parsing must preserve values; rounding, clipping, ID trimming/recoding or converting invalid input into valid defaults requires separate approval.

Unless a separate reviewed transformation explicitly approves otherwise:

- Do not drop defective rows, select a favorable population or discard missing observations as “cleaning”.
- Do not impute, forward/backward fill, interpolate or replace missing values with zero.
- Do not clip, round, smooth or modify observed demand or other recorded quantities.
- Do not aggregate the native grain or deduplicate by choosing/merging records.
- Do not fill missing dates or invent observations.
- Do not trim, recode, renumber or otherwise alter identifiers.
- Do not use future observations to repair earlier records or estimate cleaning parameters.

Authorized scope isolation excludes records from a purpose-specific view, not from the immutable source. A schema projection excludes unused columns, not observations. A derived roster's unique identities and diagnostic subsets do not deduplicate or delete source rows. Audit copies with invalid parses remain diagnostic evidence, not repaired datasets.

Any future observation-changing transformation requires a documented rationale, affected fields/keys, before/after evidence, temporal availability assessment, rule/version amendment and explicit relevant human approval. Preserve parent lineage and assess whether the change requires a revised dataset, feature or scientific protocol decision. This document approves no such transformation.

## 5. Cleaned / validated output contract

A consumable validated representation must be:

- **Typed:** Values conform to its declared schema; source missingness and parse defects remain distinguishable.
- **Keyed:** Native keys are valid and unique, with declared scope and projection.
- **Chronologically sorted:** Use deterministic SKU_ID, Warehouse_ID, Date ordering, with increasing Date within each series, consistent with current modules.
- **Native-grain preserving:** Retain the same authorized observation keys and observed values; document counts before/after parsing/sorting. No unexplained row loss or gain is allowed.
- **Leakage-safe:** Validate and persist only the authorized scope; retaining an operational field is not certification of its prediction-time availability.
- **Provenance-bound:** Bind parent identity, scope, validation mode/rules, code, schema, audit and output fingerprints.

The expected local ignored location is:

~~~text
data/processed/validated/<data_version>/
~~~

The [storage policy](artifact-storage-policy.md#storage-responsibilities) owns this location. The shared handoff is the validated full fifteen-column source representation, including zero-variance fields such as Stockout_Flag. Predictive-use exclusions belong downstream. At minimum retain the validated dataset, schema metadata, validation audit/report and provenance metadata. The approved Issue #102 bundle contains validated.parquet, schema.json, validation-audit.json and provenance.json. Parquet uses pyarrow; JSON carries schema/audit/provenance metadata. The full fifteen-column order is explicit, calendar dates use Arrow date32, identifiers remain strings, numerical storage follows the accepted dataframe dtype, and no dataframe index is serialized. Shared validation blocks missing/blank values before publication; serialization does not fill them. Failed diagnostic material must not masquerade as an accepted validated version.

Do not overwrite an accepted version. New parents, scope, parsing rules or schema produce a distinguishable version. Validated data are regenerable only from exact retained inputs, code, rules and environment; preserve/archive accepted versions when required to support evidence. Scratch/interim material and run evidence retain their separate storage responsibilities. Large/generated datasets stay local and ignored by Git.

## 6. Provenance and versioning requirements

The persisted handoff must carry the following information, without inventing unavailable provenance:

| Identity/evidence | Required content |
|---|---|
| Parent source | Source citation, snapshot/version identity, local or verified archive reference, parent byte hash and size where available, and acquisition/receipt provenance |
| Authorized scope | Preparation purpose, authorization/reference, date/key scope and projection/mode; scoped input fingerprint distinct from the complete source receipt |
| Rules | Cleaning/validation rule version and contract reference/hash; explicit parsing/sorting steps and any separately approved transformation references |
| Implementation | Code revision and relevant source hashes, dirty-state disclosure and environment/parser versions needed for reproduction |
| Schema | Ordered columns, logical/serialized types, missing-value encoding, schema/version and observation key/order |
| Population | Authorized input/output row counts, unique-key and duplicate counts, missing/invalid counts, series coverage and actual authorized date range |
| Audit/review | Applied checks, findings/reasons, pass/fail/unavailable status, uninspected checks and reasons, preparation time and actual human acceptance reference or pending status |
| Output | Data version, explicit file references, byte hashes and scoped logical fingerprint, linked schema/audit identities and readback validation outcome |

Parent whole-source identity and scoped scientific fingerprints have different purposes. Use an existing acquisition/source receipt when available; do not hash, profile or validate reserved outcomes during a forecasting validation run merely to complete lineage. If permitted parent identity evidence is unavailable, disclose that gap and resolve it through authorized acquisition/provenance review; never substitute a scoped fingerprint and label it the whole-source hash.

Fingerprints require a declared canonical ordering/schema. Serialization readback must preserve identifiers, missingness, observed numerical values, dates, keys and counts. A byte hash identifies exact files; a logical fingerprint identifies the defined scoped representation. Hashes alone cannot reconstruct missing inputs or authenticate approval. Issue #102 uses the reviewed schema_version validated-shared-data-v1, rule_version shared-data-cleaning-v1 and metadata_version validated-handoff-metadata-v1. data_version is a mandatory caller-supplied safe single path component, never an inferred semantic version. A separate generated preparation_id identifies each staging attempt.

## 7. Chronological safety and model-ready boundaries

The lifecycle arrow “raw -> validated” does not authorize inspecting all outcomes first. As in the [shared lifecycle](workflows/shared-data-foundation.md#leakage-safe-order), parse the date information needed to isolate permitted records before validating quantities/identities or collecting outcome-derived audits/fingerprints. The current forecasting implementation follows that scope-first rule. A persisted validated snapshot is purpose/scope-specific, not standing permission to consume every row.

A validated dataset does not authorize full-year feature engineering followed by splitting, access to reserved final outcomes, random train/test splitting or globally fitted preprocessing. Chronological windows, eligibility and final-evaluation protection remain in the protocol. Historical full-year EDA is a separately disclosed activity; this contract does not rerun it or erase prior exposure recorded in the [methodology revision](forecasting-methodology-revision.md).

**Cleaned/validated dataset != feature-engineered dataset != model-ready matrix.**

Validated data retain source observations. Engineered data contain origin-available conceptual predictors and separately identified targets. Model-ready matrices apply the correct training-fitted representation. Their formulas, eligibility and preprocessing are owned by the feature contract/protocol; their storage is owned by the storage policy. Passing source validation neither constructs targets nor certifies a model-ready population or authorizes fitting.

## 8. Current implementation and Issue #102 handoff

| Existing implementation | Current behavior / boundary |
|---|---|
| [data_cleaning.py](../src/data/data_cleaning.py) | Dedicated reusable full-source schema/parsing/domain/missingness/duplicate/coverage validation, audit and scope-aware loading returning an accepted in-memory dataframe. Persistence is delegated to validated_handoff.py. No feature engineering, targets or training; callers must supply authorized scope and reviewed provenance |
| [validated_handoff.py](../src/data/validated_handoff.py) | Single CLI/programmatic scoped preparation stage, Parquet/schema/audit/provenance writing, strict readback and portable exclusive publication; no forecasting preparation or experiment execution |
| [demand_exploratory_analysis.py](../src/analysis/demand_exploratory_analysis.py) | Descriptive demand summaries, temporal/distribution/lag/promotion analysis, figures and historical report rendering only. Consumes validated data; its CLI delegates scoped loading, validation, audit presentation and scoped receipt generation to data_cleaning.py |
| [inventory_alignment_analysis.py](../src/analysis/inventory_alignment_analysis.py) and [forecasting_grain_analysis.py](../src/analysis/forecasting_grain_analysis.py) | Descriptive native-grain/warehouse coverage, inventory variation/ranges and historical candidate-grain comparisons. Consume validated input; their CLIs delegate scoped loading/validation to data_cleaning.py. Descriptive coverage/uniqueness summaries do not establish separate acceptance or repair rules |
| [execution.py](../src/forecasting/execution.py): load_dataset / resolve_execution | Checks reviewed execution identity and required headers, loads the four-column demand projection and preserves text IDs. Loading alone does not constitute complete source validation |
| [features.py](../src/forecasting/features.py): prepare_demand | Validates keys/dates/observed demand, rejects duplicates/invalid quantities and sorts in memory. Missing demand is retained; daily-gap enforcement depends on the existing caller option |
| [evaluation.py](../src/forecasting/evaluation.py): validation_view / prepare_fold | Isolates authorized records before demand checks/fingerprinting; applies fold coverage and separate feature/target eligibility. It does not persist a validated dataset |

Existing runtime validation is implemented but primarily in memory. EDA/profile outputs are quality/descriptive evidence, not a persisted cleaned training dataset. Issue #102 adds the validated-handoff stage, tested with synthetic data only. It is not wired into the forecasting runner and has not processed the project dataset.

Issue #99 shared cleaning and analysis separation are merged; Issue #102 persisted handoff implementation awaits human review. Forecasting orchestration and cross-location integrity integration remain later Issue #98 work. Reuse existing rules without broadening access or changing scientific eligibility. In particular, shared source auditing is stricter/wider than the forecasting demand projection; do not silently replace one with the other. Storage migration and selective model retention remain governed by their separate decisions.

## 9. Human review and remaining decisions

Human review must accept this contract before treating it as the new authoritative validation baseline. Any future repair or observation-changing rule requires separate explicit approval; no repair rule is assumed missing and automatically filled in by implementation.

Before accepting or publishing a persisted project handoff, confirm authorized preparation scope, serialized schema/format/version and source lineage availability. The shared handoff preserves all fifteen fields; the four-column demand view is downstream. A forecasting-only validated view must be labelled accordingly; it must not be presented as a complete shared dataset. Additional anomaly thresholds, identifier mappings or missing-period handling require decisions only if proposed, not speculative defaults.

Relevant component owners retain their existing analytical responsibilities. Contract acceptance, source-quality acceptance, source-code acceptance and specific experiment authorization are separate controls. Creating or reviewing this document does not authorize dataset processing, model training, final evaluation, cleanup or Git operations.

## 10. Executable validated handoff — Issue #102

One owner-triggered command performs loading, authorized date isolation, shared validation, accepted dataframe construction, audit generation, Parquet/JSON serialization, strict readback, hash verification and publication. This example is a command shape, not permission to process the project source:

~~~bash
python -m src.data.validated_handoff \
  --input 'data/raw/<source-file>' \
  --data-version '<reviewed-data-version>' \
  --start '<authorized-start-YYYY-MM-DD>' --end '<authorized-end-YYYY-MM-DD>' \
  --purpose '<preparation-purpose>' \
  --authorization-reference '<human-authorization-reference>' \
  --source-receipt '<verified-source-receipt.json>'
~~~

Quote actual arguments containing spaces. --repository optionally selects the repository root. The programmatic prepare_validated_handoff interface accepts repository/input_path as Path values and data_version, start, end, purpose, authorization_reference and source_receipt explicitly; it returns HandoffResult with directory and provenance_sha256. read_validated_handoff verifies an explicitly named version, optionally against that externally retained provenance hash. Neither interface discovers a latest dataset or runs later forecasting stages.

The source receipt JSON requires exactly identity, citation, snapshot_reference, sha256, size_bytes, receipt_reference and verification_method. snapshot_reference is repository-relative under data/raw/ and must match the input; size_bytes must match the file. verification_method is verified_acquisition_receipt or explicit_verified_metadata. sha256 is a lowercase 64-digit externally verified source hash. The stage validates receipt shape/path/size and detects source stat changes during loading, but does not independently authenticate the supplied whole-source SHA or reread protected quantities to calculate it. An immutable acquired source and trustworthy external receipt are prerequisites. Authorization text records a human decision; it does not itself grant one.

Schema metadata records ordered columns, logical/Arrow storage types, accepted pandas dtypes, native key/order, null/date encoding, format and engine. The audit persists existing cleaner checks/counts, duplicate/conflict positions, generic distinct/range diagnostics, missingness, original ordering, scope and input/output fingerprints. Unperformed semantic inventory interpretation and historical EDA comparisons are explicitly labelled; they remain analysis responsibilities. Blocking defects prevent publication, rather than producing a repaired accepted bundle.

Provenance records source/scope/input/output identities, rule/schema/metadata versions, contract reference/hash where available, UTC preparation time, code revision/dirty disclosure and source hashes, Python/pandas/numpy/pyarrow versions, file paths/sizes/hashes and verification statuses. Unavailable code revision information stays null. Human review always starts pending_human_review with a null reference; successful validation is not human approval, and immutable bundles are not edited to manufacture it. Subsequent review belongs in separately linked reviewed project evidence.

A provenance file cannot contain its own final byte hash. Its self-entry explicitly marks null size/hash with hash_status self_reference; the CLI result and HandoffResult expose its actual SHA-256 for an external integrity anchor. The other three files have byte sizes and SHA-256 recorded in provenance. Without an external anchor, consistent malicious rewriting of provenance and its file hashes is not authenticated by internal checks alone.

Readback verifies declared physical/logical types, exact columns/order/index, dates, IDs, numerical values, missingness, keys/counts and the logical fingerprint against the accepted in-memory frame before rerunning shared validation. It does not sort or repair reloaded data to hide corruption. The logical fingerprint uses the existing pandas-row-hash SHA-256 algorithm; recorded environment versions are required for replay, rather than promising cross-version canonical hashing.

Staging is data/processed/interim/<preparation_id>/validated-handoff/. All stage files are verified before portable exclusive final-directory creation and exclusive file copying. Provenance is copied last as the completion record; completed publication is checked again. This is not an atomic directory rename or a power-loss durability guarantee. An interrupted final copy remains incomplete, fails readback and blocks reuse of that version pending human investigation. Cleanup removes only this attempt’s unpublished staging, never another attempt or a final version. Paths reject traversal and symlink redirection; the local filesystem is assumed trusted during execution, not adversarially mutated concurrently.

No real source was prepared by this implementation. Legacy ignored EDA/profile outputs are untouched and are not inputs to this stage. Feature/target/model-ready/view persistence, forecasting integration, model retention and reports remain outside Issue #102.
