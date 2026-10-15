# DR-014 — Forecasting Selection and Final Refit

**Date:** 2026-10-03 (Asia/Colombo)

**Status:** Scientific freeze and final-refit policy approved by Chathuranga; retained validation and corrected final evaluation completed and integrity verified, as confirmed by Chathuranga under Issue #131. This documentation cleanup changes no decision content.

**Responsible member:** Chathuranga — forecasting methodology and output meaning.

**Related issues:** [#130](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/130) (freeze/refit approval) and [#131](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/131) (final evaluation and repository refinement).

**Approval provenance:** Chathuranga's explicit 2026-10-03 Issue #130 instruction approved the scientific scope, configurations, producer mapping and fresh-refit policy below. Documentation Step 1 and the separate runtime were subsequently accepted by Chathuranga under Issue #131. Chathuranga separately authorized corrected final run final-20261003-02 after a verified implementation defect in final-20261003-01. These approvals were supplied in the conversation between Chathuranga and the AI assistant; no additional GitHub comment, lecturer confirmation or group approval is asserted.

## Context and evidence binding

This decision records the human-reviewed freeze from validation run
`validation-20261002-01`. The existing scientific authorities remain
[DR-013](DR-013-matched-gradient-boosting-comparison.md), the
[frozen protocol](../protocol.md) and the
[feature contract](../forecasting-feature-engineering.md). This dated decision
resolves their previously deferred final selection/refit policy without changing
the completed validation experiment or rewriting its historical approval records.

The exact local completion anchor is
[run_manifest.json](../../artifacts/forecasting/validation-20261002-01/run_manifest.json).

| Evidence identity | Recorded value |
|---|---|
| Run ID | `validation-20261002-01` |
| Evaluation stage | `validation` |
| Manifest version | `2` |
| Recorded final status | `verified_completed` |
| Scientific schema | `issue-65-v2` |
| Protocol version | `issue-65-matched-frozen-1` |
| Recorded completion time (UTC) | `2026-10-02T17:38:14.247307+00:00` |

The SHA-256 of the inspected manifest bytes is:

```text
4b82deefe6932d7fd619f49331b6a77ae0cc41009d1736f74d9bb557625ea3cc
```

The manifest records passed integrity checks for 1,216 evaluations, 304,000
predictions, 304 configuration summaries and 1,184 model replays. These are
retained completion claims, not a new verification or research run performed
while drafting this record. Any separately authorized final run must bind this exact
manifest hash and successfully verify the completed validation bundle.
Missing, changed or unverifiable evidence blocks final consumption; never
refresh this anchor automatically or regenerate evidence under the original ID.

## Frozen primary research configurations

Each cell identifies one newly fitted final candidate. Canonical IDs retain
their exact existing definitions in
[configuration.py](../../src/forecasting/configuration.py).

| Horizon | XGBoost | LightGBM | CatBoost |
|---|---|---|---|
| 1 day | GBM006 | GBM018 | GBM017 |
| 7 days | GBM009 | GBM011 | GBM007 |
| 14 days | GBM022 | GBM014 | GBM021 |
| 28 days | GBM003 | GBM022 | GBM015 |

The validation interpretation supplied by Chathuranga is that XGBoost, LightGBM and
CatBoost showed broadly comparable performance, with no universal primary-model
winner. RQ2 remains descriptive and horizon-specific under DR-013. Ridge and
Random Forest remain supportive; Naive and Seasonal Naive remain contextual
baselines. Seasonal Naive outperformed the learned models in validation at
14 and 28 days and must be reported honestly as the strongest validation
baseline at those horizons. This is validation interpretation, not a prediction
of final-evaluation ordering or a statistical-significance claim.

## Exact final-evaluation research scope

| Role | Exact candidates | Count |
|---|---|---:|
| Primary | The twelve model/horizon/configuration combinations in the preceding table | 12 learned refits |
| Supportive | Ridge/`fixed` and Random Forest/`fixed`, each at 1, 7, 14 and 28 days | 8 learned refits |
| Baselines | Naive/`not_tuned` and Seasonal Naive/`not_tuned`, each at 1, 7, 14 and 28 days | 8 baseline evaluations |
| Total | 20 learned refits plus 8 baseline evaluations at one fixed origin | 28 evaluations |

Supportive parameters and baseline formulas remain those already approved in
the protocol and source. There is no new grid, configuration, seed, model,
baseline exclusion, selective retention or pruning. All approved candidates
remain in the final comparison; the producer mapping does not narrow this scope.

## Separate downstream forecasting-framework producer decision

| Horizon | Producer model | Configuration |
|---|---|---|
| 1 day | LightGBM | GBM018 |
| 7 days | LightGBM | GBM011 |
| 14 days | XGBoost | GBM022 |
| 28 days | XGBoost | GBM003 |

This mapping identifies the intended downstream/API forecast producer per horizon.
It does not rewrite the RQ2 comparison, declare a universal winner or remove
supportive/baseline evidence. It introduces no API implementation or inventory,
replenishment, uncertainty or decision-support method. Downstream component
approvals, including any required 28-day inventory use approval, remain separate.

## Final refit and preprocessing policy

1. Use historical demand from **2024-01-01 through 2024-12-02**, inclusive.
   No reserved-final outcome enters features, labels, vocabulary, scaling,
   fitting, debugging or selection.
2. For a row with first target day `t` and horizon `h`, its predictors use only
   history through `t - 1`. Require the unchanged complete 28-day predictor
   history and every finite frozen predictor. Require complete observed labels
   on `t` through `t + h - 1`, with `t + h - 1 <= 2024-12-02`.
   Join features and labels one-to-one by native keys and intersect these
   eligibility conditions before fitting. Use identical eligible rows for all
   learned models within each horizon; do not impute or shorten windows.
3. Fit **new estimators** for all twenty learned candidates. Do not reuse,
   continue training or promote a Fold 4 estimator.
4. Refit preprocessing on the same horizon-specific eligible labelled
   population used by the estimators. Share eligible-training SKU/warehouse
   vocabularies and ordered full one-hot/unscaled numerical representation
   across primary models. Preserve supportive representations and unknown-ID
   rejection. Refit Ridge numerical means/scales on that same population using
   the existing population-standard-deviation and constant-column rules.
   Origin rows and reserved outcomes do not fit preprocessing.
5. Preserve the canonical parameters, requested iterations, CPU controls,
   seed 42 where already declared, single-thread model controls,
   `worker_count=1`, Ridge solver and all pinned libraries. Ridge receives
   no new seed. Preserve the existing prohibition on early stopping, callbacks,
   adaptive search and score-driven parameter changes.
6. Construct the common fixed-origin predictor vector from history through
   **2024-12-02**, with first target day **2024-12-03**. Reuse that vector
   across direct 1/7/14/28-day forecasts; do not update it with realised demand.
7. Use the latest complete seven-day history ending at the origin:
   **2024-11-26 through 2024-12-02**. Preserve Naive `h * y_o`,
   Seasonal Naive `y_(o-6)` for one day, and `(h / 7) * S_o` otherwise.
   Incomplete origin history fails; no older-week fallback is introduced.
8. Persist and hash **all 28 candidates' predictions before revealing any
   reserved-final outcomes**. Verify the saved prediction evidence before
   reading the outcome interval, then score against immutable predictions.
   Outcome access cannot precede successful completion of every approved
   fit/prediction and its persistence.
9. Any fit, prediction, persistence or integrity failure stops execution and
   preserves available diagnostics. Preserve the original exception and partial
   evidence. Publish no successful completion. Do not retry automatically,
   replace a failed candidate, or use scores to debug, retune or choose another
   candidate. Only a verified implementation/execution defect may support a
   separately approved corrected rerun after its fix, under the separate explicit defect-correction approval; never resume or overwrite the failed run.
10. Final-model handoff must identify each fresh model, fitted preprocessing,
    origin inputs, model/configuration/horizon, training population, hashes and
    provenance. A completed final bundle is evaluation evidence; downstream
    use still requires human acceptance of the handoff. Validation models
    remain validation candidates.

The latest possible labelled training row starts on December 2, November 26,
November 19 and November 5 for horizons 1, 7, 14 and 28 respectively. Actual
eligibility still requires complete labels and predictor history.

## Rationale, alternatives and limits

Fresh estimator and preprocessing fits use all eligible history available at
the approved origin while preserving the frozen recipe. Fold 4 estimator/state
reuse was rejected by Chathuranga's explicit policy. Selecting only the four
producer candidates would omit the approved research comparison. Outcome-driven
search and performance-driven retries would compromise the protected final
evaluation. A separately approved implementation-defect rerun must preserve and
disclose prior execution and outcome exposure.

The reserved interval is **2024-12-03 through 2024-12-30**, with horizon target
ends December 3, 9, 16 and 30. It is reserved from subsequent selection, but
not historically fully unseen: December 3–16 had earlier validation exposure,
and full-year exploratory data analysis inspected the interval. Reports must
repeat both disclosures. The dataset downloaded from Kaggle is simulated by its publisher; results do not establish
effectiveness in a real retailer.

## Impact and remaining human controls

The scientific freeze, validation evidence anchor, targets, features, grid, metrics, seeds and producer mapping are unchanged. Validation and final evaluation use separate persistence/integrity paths. [Runner operations](../forecasting-runner.md) owns execution controls; [final results](../forecasting-final-evaluation.md) owns current interpretation and disclosure of prior outcome exposure.

The earlier final run accessed outcomes before failing integrity completion. The corrected run retained the exact frozen 28-evaluation scope. Preserve both historical bundles and their recorded hashes; do not resume, overwrite or refresh an authorization/evidence record. A document or completed run does not authorize another experiment. Final-result-driven reselection remains prohibited. Downstream handoff acceptance, component approvals and human review of this consolidated narrative remain separate.
