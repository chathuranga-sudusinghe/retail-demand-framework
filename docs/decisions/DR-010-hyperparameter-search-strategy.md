# DR-010 — Forecasting Hyperparameter-Search Strategy

> **Current status cross-reference — Issue #89:** [The frozen protocol](../protocol.md) resolves prior pending supportive configuration, 28-day baseline and numeric runtime wording. Primary scientific decisions remain unchanged. [Runner operations](../forecasting-runner.md) describe current implementation and separate approval gates. Original decision/development wording below is retained as provenance and does not supersede later recorded approvals. Issue #89 implementation awaits human review; no new run or final evaluation is authorized here.

**Status:** PRIMARY SEARCH DESIGN SUPERSEDED BY DR-013

## Current status and effect

[DR-013](DR-013-matched-gradient-boosting-comparison.md) is the current authority for the matched primary RQ2 grid. The primary implementations are XGBoost Regressor, LightGBM Regressor and CatBoost Regressor.

The primary models use the same four matched hyperparameter dimensions and values defined in DR-013: learning rate, boosting iterations, maximum tree depth and row subsampling. Each primary model receives **24 configurations per horizon** over the same four forecast horizons and four temporal validation folds:

**24 × 3 primary models × 4 horizons × 4 folds = 1,152 planned primary validation fits.**

These are planned counts, not executed evidence. Canonical configuration identities, API mappings, fixed seed policy, representation and pending runtime controls remain governed by DR-013.

The supportive Ridge Regression / Random Forest configuration policy remains pending separate human approval. No supportive configuration policy is selected by this record. Naive and Seasonal Naive remain separate untuned baselines under the retained provisions in [DR-007](DR-007-forecasting-model-set.md).

The earlier primary grids and fit-count plan are preserved only in the historical block below. This record authorises no experiment execution; protocol approval, implementation acceptance and specific run authorisation remain separate human gates.

## Historical original decision body

> The content below is retained verbatim as historical provenance and is non-operative where superseded by DR-013.

<details>
<summary>Show superseded historical DR-010 body</summary>

# DR-010 — Forecasting Hyperparameter-Search Strategy

> **Documentation alignment — 2026-09-29:** The project owner has approved the current 1/7/14/28-day forecasting design and [frozen feature contract](../forecasting-feature-engineering.md). This record's original date and decision history remain intact. Proposed 28-day baseline formulas, the executable protocol and downstream methods retain separate approval boundaries; experiment execution is NOT authorised. See [current approval and provenance](../forecasting-methodology-revision.md).

**Original decision date:** 2026-09-23
**Original decision status:** Accepted for the earlier 1/7/14-day baseline
**Revision date:** 2026-09-28
**Revision status:** Current forecasting design human-approved; separate execution/implementation gates remain
**Documentation alignment:** 2026-09-29, on the project owner's explicit instruction
**Owner:** Chathuranga
**Related issue:** [#44 — Research: define forecasting hyperparameter-search strategy](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/44)
**Supervisor confirmation:** Not required to record the current team methodology baseline. This record does not claim separate supervisor approval; any programme-required supervisor review remains subject to the team's review process.

## Context

[DR-007](DR-007-forecasting-model-set.md) approves Naive, Seasonal Naive, Ridge Regression, Random Forest, and one gradient-boosting candidate. [DR-009](DR-009-gradient-boosting-model-choice.md) selects LightGBM for that gradient-boosting role. Before implementation begins, the project needs a bounded and reproducible method for selecting settings for the three learned models without adapting the search repeatedly to disappointing validation results.

[DR-005](DR-005-forecast-validation-design.md) defines four expanding-window validation folds that preserve temporal order. [DR-006](DR-006-forecasting-metrics-and-model-selection.md) defines mean WAPE across those folds as the primary selection statistic, with MAE, RMSE, Bias, fold-level results, and fold-to-fold stability retained for review. [DR-008](DR-008-multi-step-forecasting-strategy.md) requires separate direct models or outputs for the 1-day, 7-day cumulative, 14-day cumulative, and 28-day cumulative targets.

## Decision

Use a small, predefined, bounded exhaustive search for each learned model and each horizon included in the current methodology at execution time. Generate every combination from the grids below, evaluate every combination on the same four DR-005 expanding-window folds, and select one configuration per model and horizon before evaluation on the revised final evaluation interval.

Naive and Seasonal Naive are fixed baselines under DR-007. They have no hyperparameter search.

Ordinary random K-fold cross-validation must not be used because it would break the temporal ordering required by DR-005. The revised final evaluation interval must never be used for hyperparameter tuning, search-space revision, or model selection.

## Approved bounded search spaces

### Ridge Regression

Tune only the regularisation strength:

```text
alpha = [0.01, 0.1, 1.0, 10.0, 100.0]
```

This produces five candidate configurations per horizon. All other Ridge Regression settings must remain fixed and be recorded. Changing another setting requires a separate approved decision.

### Random Forest

Use the Cartesian product of:

```text
n_estimators = [100, 300]
max_depth = [None, 10, 20]
min_samples_leaf = [1, 5]
```

This produces 12 candidate configurations per horizon. Use `random_state = 42` for every candidate, fold, and horizon. All other settings must remain fixed and be recorded. No additional search dimension is approved.

### LightGBM

Use the Cartesian product of:

```text
learning_rate = [0.03, 0.05, 0.1]
num_leaves = [15, 31]
n_estimators = [100, 300]
max_depth = [-1, 10]
```

This produces 24 candidate configurations per horizon. Use `random_state = 42`, or the equivalent supported seed value of 42, consistently across candidates, folds, and horizons. All other settings must remain fixed and be recorded. No additional search dimension is approved.

These deliberately modest spaces bound the initial search to 41 learned-model configurations per horizon. Their purpose is controlled comparison within the MSc project, not exhaustive optimisation of every setting exposed by each library.

## Revised workload and provenance

The earlier three-horizon/four-fold protocol planned 492 learned fits and 24 baseline evaluations. The revised direction plans 4 horizons × 4 folds × 41 configurations = 656 learned fits. The planned 2 baseline roles × 4 horizons × 4 folds = 32 baseline evaluations apply only if/after both proposed 28-day baseline definitions receive explicit human approval. These are planned workload counts, not executed experiment results. The 41 configurations per horizon and all grids remain unchanged. The feature set is frozen. No training or search may run until implementation/tests and the revised executable protocol are accepted and the specific run is authorised. No experiment is authorised by this documentation revision.

## Search procedure

For each learned model and each horizon included in the current methodology at execution time:

1. Generate only the predefined candidate parameter combinations.
2. Evaluate every candidate using the same four DR-005 expanding-window validation folds.
3. Fit all learned preprocessing and the model only on the relevant fold's training data.
4. Calculate WAPE, MAE, RMSE, and Bias separately for every fold.
5. Calculate the arithmetic mean of each metric across the four folds.
6. Use mean WAPE as the primary hyperparameter-selection statistic under DR-006.
7. Review fold-level stability and the supporting MAE, RMSE, and Bias results before finalising the setting; do not select from one favourable fold alone.
8. Choose and document one hyperparameter configuration for that model and horizon.
9. Freeze the selected configuration before evaluation on the revised final evaluation interval.

The 1-day, 7-day, 14-day, and 28-day horizons remain separate tuning tasks. Their metrics must not be averaged or weighted into one tuning score unless a later approved decision explicitly introduces that policy.

If two or more settings are not meaningfully distinguishable from the recorded validation evidence, the selected setting and rationale must be documented without expanding the grid or consulting results from the revised final evaluation interval. This decision does not invent an automatic numerical stability or tie threshold beyond DR-006.

## Reproducibility requirements

The implementation must record, in machine-readable outputs where practical:

- random seeds;
- Python and library versions;
- feature names and feature order;
- the exact DR-005 fold definitions;
- the complete candidate parameter grids and generated combinations;
- model name and forecast horizon;
- WAPE, MAE, RMSE, and Bias for every candidate and fold;
- arithmetic mean metrics across folds;
- the selected parameter configuration; and
- the selection rationale, including any fold-stability or supporting-metric concern.

The same preprocessing, feature availability, target construction, metric implementation, and fold boundaries must be used consistently when comparing settings for a model and horizon.

## Frozen representation and comparison inputs

Use the [authoritative fourteen-predictor contract](../forecasting-feature-engineering.md): Ridge/Random Forest use 67 physical columns and LightGBM uses 14 native categorical/numerical inputs. All receive equivalent information and the same origin, eligible population and targets within each horizon. Fit preprocessing only on eligible training rows; record conceptual/physical order and category mappings. Representation does not change the approved grids or approve feature search. The revised executable protocol must document estimator settings, including any encoded-column subsampling behaviour, without silently changing the grid.

## Search-space changes

If an approved search value is technically invalid for the implemented library version or the bounded space is clearly inadequate:

1. stop rather than silently changing or extending the grid;
2. document the technical or methodological reason;
3. approve a revised bounded space before rerunning the search; and
4. preserve the earlier search definition and results as part of the decision trail where applicable.

Performance on the revised final evaluation interval must never be used to justify expanding, narrowing, or rerunning a hyperparameter search. Validation results may identify a limitation, but repeated ad-hoc boundary expansion in response to disappointing results is not approved.

## Alternatives considered

### Ad-hoc manual tuning

Repeatedly changing individual parameters after inspecting validation results is not selected because it is difficult to reproduce and increases the risk of tuning decisions becoming tailored to the four validation periods. Manual tuning is not universally invalid, but it does not provide the controlled decision trail required here.

### Unrestricted GridSearch

A large combinatorial grid could examine more settings but would increase runtime, tuning complexity, and opportunities for validation over-tuning. The selected approach still evaluates a grid exhaustively, but the grid is small and fixed before results are inspected.

### RandomizedSearchCV with ordinary cross-validation

Random search can be useful for larger spaces. It is not selected for the initial scope because the approved spaces are already small enough to enumerate, and ordinary cross-validation defaults are not an acceptable substitute for the chronological DR-005 folds. Any future randomised method would still need explicit temporal folds and reproducible sampling.

### Bayesian optimisation or Optuna-style tuning

Adaptive optimisation can search complex spaces efficiently, but it adds tooling, tuning policy, and stopping-rule complexity. That scope is unnecessary for the current dataset and three deliberately small grids, and repeated adaptive feedback can increase validation over-tuning risk. These methods are not considered universally inferior; they are outside the initial COMP1884 scope.

## Limitations

- The bounded grids may omit a stronger configuration outside their approved values.
- Reusing four validation folds across configurations creates validation over-tuning risk even with a bounded search; limiting and predeclaring the spaces reduces but does not remove that risk.
- Mean WAPE can hide fold-level variation, so fold results and supporting metrics remain mandatory.
- A fixed random seed improves reproducibility but does not establish robustness across all possible random seeds.
- Separate tuning by horizon increases the number of fits but preserves DR-006's horizon-specific comparison policy.
- This decision defines the search method only; it introduces no training results or claim about which configuration or model will perform best.

## Impact

- Ridge Regression, Random Forest, and LightGBM now have fixed initial search spaces and a common temporal tuning procedure.
- Naive and Seasonal Naive remain untuned baselines.
- `docs/research-design.md` and `docs/workflows/demand-forecasting.md` summarise the approved strategy.
- The hyperparameter-search strategy is removed from the open-decision list.
- The original search decision did not change the other DRs. The September 28 human-selected revision under review extends application of the unchanged grids to four horizons and the revised DR-005 schedule; metric policy, model families and direct strategy remain.
- No dependency, modelling code, training run, forecast result, or use of the revised final evaluation interval is introduced by this decision.

</details>
