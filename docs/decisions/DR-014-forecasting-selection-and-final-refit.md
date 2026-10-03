# DR-014 — Forecasting Selection and Final Refit

**Date:** 2026-10-03 (Asia/Colombo)

**Status:** Scientific freeze and refit policy approved by the project owner under
Issue #130; Documentation Step 1 approved. Phase 1 runtime merged in PR #133 and
explicitly accepted by the owner under Issue #131 on 2026-10-03. Historical-only
preflight completed successfully on 2026-10-03: `READY FOR AUTHORIZATION PREPARATION`.
Exact one-time final-run authorization remains pending. No real
`final_authorization.json` exists, final-run bindings are not frozen, and no
reserved-final outcomes were accessed. Final evaluation has not been executed.
Implementation acceptance establishes readiness
only; it grants no authorization-record creation, reserved-outcome access or run
execution.

**Owner:** Chathuranga — forecasting methodology and output meaning.

**Related issue:** [#130 — Phase 1: Freeze forecasting decisions and implement final evaluation](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/130)

**Approval provenance:** The project owner's explicit Issue #130 instruction dated
2026-10-03, beginning "Proceed with Issue #130 Phase 1 implementation", approves
the separate final-evaluation architecture, confirms the exact research scope,
and supplies the frozen configurations, producer mapping and final refit policy
below. The same instruction requires documentation review before runtime code
and forbids real final evaluation, commits and pushes. This record documents
that human instruction; it does not supply implementation acceptance or execution
permission. No separate supervisor/group approval is asserted. Any required
supervisor confirmation remains a human/team responsibility.

**Subsequent review provenance — 2026-10-03:** The owner explicitly approved
Documentation Step 1 under Issue #130. Phase 1 was then merged through
[PR #133](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/133).
In the subsequent explicit Issue #131 instruction, the owner accepted the
implemented final-evaluation runtime and recorded test/integrity evidence as
conforming to the approved DR-014 scope, refit/preprocessing policy, frozen
28-candidate scope, producer mapping and predict-before-reveal protections.
This acceptance establishes implementation readiness only, not final-run
authorization. This approving instruction was supplied in the owner-agent conversation;
it is not asserted to be a GitHub Issue comment or an additional supervisor/group
approval. A separate explicit one-time final-run authorization is still required
under [Issue #131](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/131).

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
while drafting this record. Future final authorization must bind this exact
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

The owner-supplied validation interpretation is that XGBoost, LightGBM and
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
   candidate.
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
reuse was rejected by the owner's explicit policy. Selecting only the four
producer candidates would omit the approved research comparison. Outcome-driven
search or retry would compromise the protected final evaluation.

The reserved interval is **2024-12-03 through 2024-12-30**, with horizon target
ends December 3, 9, 16 and 30. It is reserved from subsequent selection, but
not historically fully unseen: December 3–16 had earlier validation exposure,
and full-year exploratory data analysis inspected the interval. Reports must
repeat both disclosures. The dataset is simulated; results do not establish
effectiveness in a real retailer.

## Impact and remaining human controls

The existing validation runner, folds, features, targets, metrics, 24-configuration
primary grid, selection rules and completed evidence remain unchanged.
Implementation uses a separate final-evaluation path and a separate
`final_artifacts.py` persistence/integrity boundary, reusing shared scientific
functions where appropriate. Validation is not routed through model-ready exports.

The [final-evaluation guide](../forecasting-final-evaluation.md) documents the
merged and accepted runtime ordering and authorization requirements. Scientific
approval, merged implementation, implementation acceptance, historical-only
preflight and exact one-time final-run authorization remain distinct. The Issue #131
historical-only preflight completed successfully on 2026-10-03 with outcome
`READY FOR AUTHORIZATION PREPARATION`; specific final-run authorization remains
pending. Retained validation verification, environment/dependency matching and
historical eligibility/origin/baseline checks passed. The frozen 28-candidate
scope and producer mapping remained unchanged. No estimator was fitted or
reserved-final outcome accessed. Final evaluation has not been executed.
Exact final-run authorization bindings must be recalculated only after this
preflight-status update is reviewed and merged. These corrections create no
authorization record, calculate or freeze no final-run bindings and execute no
experiment.
