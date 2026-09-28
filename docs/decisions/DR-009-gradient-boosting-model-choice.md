# DR-009 — Gradient-Boosting Model Choice

> **DR-009 revision — 2026-09-28:** LightGBM remains the accepted gradient-boosting implementation choice. Adding the proposed 28-day target does not reopen the LightGBM-versus-XGBoost decision. The revised 1/7/14/28-day methodology remains under human review; no runtime or forecasting-performance claim is introduced. See the [central methodology-revision record](../forecasting-methodology-revision.md).

**Original decision date:** 2026-09-22
**Original decision status:** Accepted
**Revision date:** 2026-09-28
**Revision status:** Under human review
**Owner:** Chathuranga
**Related issue:** [#42 — Research: decide LightGBM versus XGBoost for gradient-boosting candidate](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/42)
**Supervisor confirmation:** Not required to record the current team methodology baseline. This record does not claim separate supervisor approval; any programme-required supervisor review remains subject to the team's review process.

## Context

[DR-007](DR-007-forecasting-model-set.md) approves one gradient-boosting candidate alongside Naive, Seasonal Naive, Ridge Regression, and Random Forest, but leaves the implementation choice between LightGBM and XGBoost open. The project needs one implementation before training so dependency and tuning scope are fixed without reacting to validation or results from the revised final evaluation interval.

The forecasting data uses structured, tabular features at the `SKU_ID + Warehouse_ID + Date` grain. Under [DR-008](DR-008-multi-step-forecasting-strategy.md), the learned models must support separate direct regression targets for next-day demand, 7-day cumulative demand, 14-day cumulative demand, and 28-day cumulative demand. Each candidate must be refitted repeatedly across the four expanding-window validation folds in [DR-005](DR-005-forecast-validation-design.md).

Neither LightGBM nor XGBoost is currently listed in `requirements.txt` or `requirements-dev.txt`. This decision selects the future dependency but does not add or install it.

## Comparison

No forecasting scores are available because neither library was trained or evaluated for this decision. The comparison is therefore based on fit with the approved methodology and project scope, not invented performance results.

| Criterion | LightGBM | XGBoost | Project assessment |
| --- | --- | --- | --- |
| Structured/tabular forecasting features | Designed for gradient-boosted decision trees over tabular feature matrices. | Designed for gradient-boosted decision trees over tabular feature matrices. | Both suit the tabular calendar, lag and rolling-feature representations considered in the project; the final forecasting feature set remains subject to the separate feature-freeze decision. |
| Regression support | Supports regression objectives suitable for continuous demand targets. | Supports regression objectives suitable for continuous demand targets. | Both can perform the required modelling role. |
| Direct 1-day, 7-day, 14-day, and 28-day cumulative targets | Can fit a separate regressor or horizon-specific output for each direct target included in the current methodology at execution time. | Can fit a separate regressor or horizon-specific output for each direct target included in the current methodology at execution time. | Both are compatible with DR-004 and DR-008; neither changes the target definitions. |
| Expanding-window validation | Can be refitted within every DR-005 training window and evaluated on the common validation schedule. | Can be refitted within every DR-005 training window and evaluated on the common validation schedule. | Both are compatible. Fold construction and leakage control remain responsibilities of the project pipeline. |
| Non-linearity and feature interactions | Tree boosting can capture non-linear relationships and interactions without defining every interaction manually. | Tree boosting can capture non-linear relationships and interactions without defining every interaction manually. | Both provide a higher-capacity comparison with Ridge Regression and Random Forest. |
| Training/runtime practicality | Designed for efficient boosted-tree training and is practical for the project's 91,250-row dataset and repeated fold-by-horizon fitting. | Also provides efficient boosted-tree training and is practical at this dataset scale. | LightGBM is selected as a computationally practical implementation; no empirical runtime advantage is claimed without benchmarking. |
| Reproducibility | Supports explicit random seeds and controlled training parameters. Reproducibility still requires fixed data ordering, folds, features, versions, and documented settings. | Supports explicit random seeds and controlled training parameters, with the same wider reproducibility requirements. | Neither library makes the workflow reproducible automatically. The implementation must control all relevant sources of variation. |
| Dependency/environment simplicity | Requires adding and pinning one currently absent third-party library when implementation begins. | Requires adding and pinning one currently absent third-party library when implementation begins. | Selecting only LightGBM avoids carrying two overlapping boosted-tree dependencies and two integration paths. |
| Hyperparameter complexity | Provides substantial capacity controls and regularisation settings that require a bounded, documented search. | Also provides substantial capacity controls and regularisation settings that require a bounded, documented search. | Neither is simple enough to justify an unrestricted search. Selecting one library keeps the tuning space controlled. |
| Interpretability and diagnostics | Provides feature-importance diagnostics that can support model inspection, subject to known limitations such as importance instability and the absence of causal meaning. | Provides comparable feature-importance diagnostics with the same cautions. | Both are adequate for supporting diagnostics. Importance must not be presented as causal evidence. |
| Maintainability | One documented LightGBM implementation can share the common target, fold, metric, and output interfaces used by the other candidates. | One documented XGBoost implementation could do the same. | Maintaining both would duplicate dependency, tuning, testing, and documentation work without a distinct approved research role. |

## Decision

Select **LightGBM** as the single gradient-boosting candidate in the approved forecasting model set.

LightGBM will fill the gradient-boosting role defined by DR-007. LightGBM itself requires no new methodological approval. Future model execution must wait until the relevant final feature freeze and revised executable forecasting protocol have completed human review and approval. It must then be trained as a regression model for each DR-008 direct horizon-specific target and evaluated using the revised common DR-005 folds and DR-006 metric policy; DR-005 owns final-evaluation provenance.

## Rationale

- The project uses structured/tabular engineered forecasting features, for which gradient-boosted decision trees are suitable.
- LightGBM provides a strong gradient-boosted tree implementation for regression and can model non-linear relationships and feature interactions.
- The original choice considered repeated fits across four folds and three horizons practical. The revised fourth horizon adds workload; no experiment in this amendment establishes its runtime. Existing bounded grids remain unchanged.
- It provides a useful higher-capacity comparison against Ridge Regression and Random Forest without assuming that it will forecast more accurately.
- Selecting one boosted-tree library keeps implementation, dependency, testing, and hyperparameter-tuning scope controlled for the COMP1884 project.
- The decision is project-specific and does not imply that LightGBM is universally better than XGBoost.

## Alternative considered: XGBoost

XGBoost is a mature and strong option for tabular regression. It supports the same general modelling role, including non-linear relationships, feature interactions, direct horizon-specific regression, expanding-window refitting, seeded execution, and feature-importance diagnostics.

It is not selected because including both LightGBM and XGBoost would add overlapping implementation and tuning scope without a clear research need for this MSc project. This is a scope and maintainability decision, not evidence that XGBoost is technically inferior or would produce worse forecasts.

## Implementation constraints

- Do not add XGBoost as a second gradient-boosting candidate without a new approved research decision.
- Add and pin the LightGBM dependency only when the separate implementation task begins; this record does not alter dependency files.
- Use the same leakage-safe features, DR-005 folds, DR-008 direct targets, and DR-006 metrics as the other learned candidates.
- Define a bounded, documented hyperparameter strategy before tuning. Do not use results from the revised final evaluation interval for tuning or selection.
- Record library version, seeds, training settings, feature order, and fold definitions needed for reproducibility.
- Treat feature importance as a supporting diagnostic rather than causal evidence or a substitute for out-of-sample evaluation.

## Limitations

- No LightGBM or XGBoost model was trained, so this decision makes no claim about comparative forecast accuracy or measured runtime.
- LightGBM still introduces an additional project dependency when implementation begins.
- Boosted-tree performance and runtime depend on the final features, hyperparameters, horizon, and execution environment.
- Feature importance can be unstable or misleading when predictors are correlated and must be interpreted cautiously.
- The dataset is simulated and covers one observed year; selecting a suitable implementation does not establish real-retailer effectiveness.

## Impact

- DR-007's gradient-boosting role is now specifically assigned to LightGBM.
- `docs/research-design.md` and `docs/workflows/demand-forecasting.md` identify LightGBM in the approved model set.
- The LightGBM-versus-XGBoost choice is removed from the open-decision list.
- DR-004 horizons, DR-005 validation dates, DR-006 metrics, and DR-008 direct forecasting strategy remain unchanged.
- No dependency, modelling code, training run, forecast score, or use of the revised final evaluation interval is introduced by this decision.
