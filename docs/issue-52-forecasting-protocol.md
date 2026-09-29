# Issue #52 — frozen validation experiment protocol

> **Historical Issue #52 evidence — earlier 1/7/14-day methodology.** The protocol/results below retain their original feature set, 14-day windows and boundaries. They are not the official baseline or results for the revised study. December 3–16 had prior validation exposure; the revised December 3–30 final interval is reserved from subsequent selection, not fully unseen historically. Further execution of this archived protocol is not authorised. Any future forecasting experiment must use a separately reviewed revised protocol after the required feature freeze and other methodology approvals. See [revision and provenance](forecasting-methodology-revision.md).


> **Source/artifact provenance — 2026-09-29:** This body records the original experiment only. The current feature contract is frozen; further execution remains NOT authorised. Its ignored artifacts are under `outputs/issue-52-validation/`, with no tracked comparison report under `reports/`. The reproduction command below references a historical runner absent from the current checkout. Metadata records the original Git HEAD and source fingerprints; reproduction would require that matching source snapshot and separate human authorisation. Compiled caches are not a source archive. See [current approval and provenance](forecasting-methodology-revision.md).

## Authority and scope

The user explicitly approved this implementation protocol on 2026-09-28,
following the pre-implementation review of Issue #52. It supplements DR-003
through DR-010 for this experiment without rewriting those decision records.
It does not finalise scientific feature selection for future experiments.

## Frozen inputs, before training

Use these **13 features in this exact order**, unchanged across learned models,
horizons, folds and configurations:

```text
day_of_week
month
quarter
lag_1
lag_7
lag_14
lag_28
rolling_mean_7
rolling_median_7
rolling_std_7
rolling_mean_14
rolling_median_14
rolling_std_14
```

These are the existing `features.py` baseline columns. Calendar features refer
to the first target day; demand features use only earlier days. Rolling standard
deviation uses ddof=1. `SKU_ID` and `Warehouse_ID` are identity keys, not predictors.
Promotion, growth indicators, source forecasts and inventory inputs are excluded.
The runner checks this frozen list against the feature module and fails if it
changes. Any later feature change needs a separate methodology decision and a
separate experiment; it must not silently replace these results.

## Training and validation

- One pooled learned model per candidate × horizon × fold. Histories and target
  construction remain isolated within each SKU–warehouse series.
- One origin per DR-005 fold, exactly its training cutoff. All three horizons
  share that origin. No validation-window updating or refitting.
- `forecast_origin` is the last observed day. `Date` and `target_start_date`
  both mean origin + 1; `target_end_date` is origin + horizon.
- Fit only rows with finite complete features and complete horizon targets
  contained in training. Do not impute. Report counts and exclusion reasons
  separately per fold and horizon, including overlapping reasons explicitly.
- StandardScaler followed by Ridge; fit both only on eligible training rows.
  Tree models receive the same unscaled columns. No sample weights.
- Apply DR-007 baselines to observations through the origin, inclusive.
- Score the same complete validation population for every candidate. If any
  expected origin lacks complete features, baseline history or target outcomes,
  fail with a diagnostic rather than inventing an exclusion/imputation policy.
- Use the exact DR-010 exhaustive grids: 492 learned fits plus 24 baseline
  evaluations. No early stopping, grid expansion, or feature tuning.
- Tree seeds are 42. Estimators use one thread; independent fits may run in
  parallel. Ridge uses the deterministic SVD solver. LightGBM uses CPU regression,
  deterministic mode and forced column-wise construction. Other estimator
  defaults remain fixed by pinned versions and are recorded with `get_params`.
- WAPE is a ratio (multiply by 100 for percent); Bias is prediction minus actual.
  Means use all four fold metrics, never a silent mean over available folds.
  Undefined WAPE prevents automatic ranking for that configuration.
- Lowest mean WAPE identifies a validation leader, pending supporting-metric
  and fold-stability review. For an exact numerical tie only, retain the first
  configuration in the declared grid order as a reproducible representative
  and report all tied configurations. This is bookkeeping, not evidence of
  superiority. There is no near-tie or stability threshold.

## Holdout and evidence boundary

Only keys and `Units_Sold` are loaded. Rows outside 2024-01-01 through 2024-12-16
are removed before demand validation, feature construction, fingerprints or
fitting. Reading a CSV to filter dates is not holdout evaluation; no holdout
outcomes enter the experiment or its metadata fingerprints.

No DR-012 inventory calculations, uncertainty method, forecast clipping,
rounding, or downstream selection criterion is implemented. Raw negative
predictions remain unchanged and are scored as produced.

## Reproduction and artifacts

From the repository root, after installing `requirements-dev.txt`:

**Historical reproduction command only — not authorised for execution under the revised study.**

```bash
python -m src.forecasting.experiment --input data/raw/supply_chain_dataset1.csv --output outputs/issue-52-validation --workers 6
```

The output directory must be a new directory beneath the ignored `outputs/`
tree; existing runs are never overwritten. Metadata is written before fitting.
Full candidate fold metrics, four-fold means, selected configurations, training
eligibility counts, and selected-configuration predictions for **all five models**
are saved locally. A compact Markdown comparison is generated alongside them.
No fitted-model binary is required. A reviewed lightweight report may be copied
to `reports/` while full prediction tables remain ignored.

Each retained prediction contains identity, explicit origin, target start/end,
horizon, fold, model, selected configuration, training cutoff, raw forecast,
actual cumulative demand, target/eligibility status, signed/absolute error,
validation-selection status, seed and run/metadata references. No processed
forecast is emitted because no processing rule is approved.

Selected-configuration validation predictions are out of sample with respect
to fitting but **not independent of configuration selection**. They support
descriptive validation comparisons, not unbiased final generalisation claims.
Retrospective actuals/errors must not become prospective downstream review inputs.
The four temporal origins and simulated year limit inference; paired series
within folds and expanding training histories are not independent replications.
