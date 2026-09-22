# DR-005 — Forecast Validation Design

**Date:** 2026-09-22  
**Status:** Accepted for the current forecasting-methodology baseline  
**Owner:** Chathuranga  
**Decision approval:** Approved for the current forecasting-methodology baseline through Issue #31  
**Related issue:** [#31 — Define expanding-window forecast validation design](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/31)

## Context and EDA evidence

[DR-002](DR-002-forecasting-analytical-unit.md) fixes the forecasting grain as `SKU_ID + Warehouse_ID + Date`, with `Units_Sold` as the target. [DR-003](DR-003-forecasting-feature-engineering-baseline.md) establishes the initial feature-engineering baseline, and [DR-004](DR-004-forecast-horizons.md) approves 1-day, 7-day and 14-day forecast horizons. This decision settles the validation design that those records left open; their other decisions remain unchanged.

The simulated dataset contains 365 observed daily dates from 2024-01-01 to 2024-12-30, with complete coverage within that span for each of 250 SKU-warehouse series. Although 2024 is a leap year, December 31 is outside the source span; it is not added to any evaluation window.

The completed [demand EDA](../../reports/demand-eda.md) reports the following means of `Units_Sold` per native SKU-warehouse-day observation:

| Observed period | Mean demand |
| --- | ---: |
| March 2024 | 29.8834 |
| September 2024 | 10.1739 |
| 2024 Q1 | 26.6138 |
| 2024 Q2 | 26.5779 |
| 2024 Q3 | 13.4886 |
| 2024 Q4, through December 30 | 13.6101 |

These materially different observed demand levels support distributing validation origins across different parts of the observed annual timeline. They do not establish recurring annual seasonality, final seasonal regimes, or differences in forecasting accuracy before models are evaluated. No Sri Lankan holiday effects are inferred.

## Decision

Use **expanding-window time-series validation**, also described as rolling-origin or walk-forward evaluation with an expanding training window. Random train/test splitting must not be used.

All candidate models must use the same four-fold schedule. Each fold starts its training history on 2024-01-01, extends that history to a later cutoff, and uses the next 14 calendar days as its validation window. Each fold evaluates the approved 1-day, 7-day and 14-day horizons while preserving warehouse identity and chronological order.

### Exact fold schedule

All dates are inclusive. Training-day counts refer to calendar observations per native series, before any future approved feature-history requirements reduce usable fitting rows.

| Fold | Training start | Training end / origin cutoff | Training days | Validation start | Validation end | Validation days |
| --- | --- | --- | ---: | --- | --- | ---: |
| 1 | 2024-01-01 | 2024-03-31 | 91 | 2024-04-01 | 2024-04-14 | 14 |
| 2 | 2024-01-01 | 2024-06-30 | 182 | 2024-07-01 | 2024-07-14 | 14 |
| 3 | 2024-01-01 | 2024-09-30 | 274 | 2024-10-01 | 2024-10-14 | 14 |
| 4 | 2024-01-01 | 2024-12-02 | 337 | 2024-12-03 | 2024-12-16 | 14 |

**Final model-evaluation holdout:** 2024-12-17 to 2024-12-30 inclusive, exactly **14 calendar days**.

Fold 4 validation ends on 2024-12-16; the holdout begins the next day. They do not overlap. All validation windows and the holdout lie within the observed dataset range.

Earlier validation observations can become historical training observations in later folds, as the schedule specifies. This is part of expanding-window evaluation: it does not permit using those observations when fitting or forecasting an earlier fold. Periods between validation windows remain part of subsequent training histories; validation windows are not a partition of the whole year.

## Terminology and horizon alignment

| Term | Meaning in this project |
| --- | --- |
| Training window | Historical observations used to fit the model, beginning on January 1 and ending at the fold's cutoff. |
| Validation window | Future observations used during model and model-setting comparison; each scheduled window contains 14 days. |
| Forecast horizon | How far beyond a prediction origin the model predicts: 1, 7 or 14 days. Under DR-004, these represent next-day demand and cumulative demand over the next 7 or 14 days. |
| Final test holdout | The final period used for model evaluation only after model selection is complete. |

A 14-day validation window defines the available evaluation interval; a 14-day forecast horizon defines the prediction's look-ahead and cumulative target. Their lengths match here to accommodate the maximum approved horizon, but they are different concepts. At a fold's training cutoff, the following 1, 7 and 14 days all fit inside its validation window. The daily forecasting grain remains unchanged.

The recursive versus direct multi-step strategy, any within-window forecast-update protocol, and detailed horizon-specific scoring policy remain separate implementation/methodology decisions. Any later choice must respect this schedule, use a common comparison protocol across models, and require complete horizon outcomes within the assigned evaluation window. It must not extend validation scoring into the final holdout or use later actuals in a forecast issued at an earlier origin.

## Why expanding-window validation

Chronological evaluation reflects forecasting from available history into a later period. Expanding windows retain all earlier history as more observations become available, providing training spans of 91, 182, 274 and 337 calendar days. The same schedule gives candidate models comparable out-of-sample periods rather than different opportunities chosen for each model.

The EDA shows why evaluation at multiple separated origins is useful: nearby origins may cover similar demand levels, whereas the approved schedule samples different portions of the observed rise, decline, lower-demand period and recovery. These descriptions are contextual observations, not formal demand-regime definitions. Expanding history does not guarantee better forecasts; suitability of candidate models still requires evaluation.

## Why four folds

Four folds are a project-specific balance between:

1. temporal coverage across materially different observed demand periods;
2. a meaningful initial training history of 91 daily observations per series;
3. accommodation of the approved maximum 14-day forecasting horizon;
4. consistent 14-day validation windows and repeated out-of-sample evaluation;
5. preservation of a separate 14-day final model-evaluation holdout; and
6. avoiding unnecessarily dense or highly similar validation origins.

The initial history is the group's chosen balance, not a guarantee that it is sufficient for every possible model or feature set. Four is not a universal optimum.

### Alternatives considered

| Fold count | Assessment |
| --- | --- |
| Two | Technically valid, but less informative for this dataset: temporal coverage and observed demand conditions would be limited, and conclusions would depend more heavily on a few periods. Two folds are not statistically invalid. |
| Three | Methodologically reasonable. Four adds one evaluation origin and broader coverage of observed demand levels or transitions without making the initial history unreasonably short or sacrificing the final holdout. Three folds are not wrong. |
| Four | Selected as the preferred balance of broad temporal coverage, meaningful initial history, repeated out-of-sample evaluation, consistent 14-day windows and a separate 14-day final holdout for this 365-observation daily dataset. |
| Five or more | Additional folds may require earlier/shorter initial histories, closer origins, or more overlapping or similar evaluation periods, depending on placement. Repeated validation feedback also creates more opportunities to over-tune model and hyperparameter choices to validation results. This is validation over-tuning risk, not evidence that the forecasting model will automatically overfit. The group did not judge the extra validation resolution necessary relative to the complexity it adds for this one-year dataset. |

## Final holdout rule and prior EDA exposure

**Final model-evaluation holdout:** 2024-12-17 to 2024-12-30 inclusive, exactly **14 calendar days**.

The final test must not be used for model fitting, feature/model selection, hyperparameter tuning, or validation decisions. Final-test forecasting results are examined only after model selection is complete; they must not feed back into model-selection decisions. Any fitting associated with final evaluation must exclude all holdout observations.

**Disclosure:** full-year descriptive EDA has already inspected the complete dataset, including dates now assigned to the final holdout. The final period is therefore not unseen in an exploratory sense. Here, **untouched final test** means reserved from fitting and selection/tuning decisions and from use of its forecasting results during validation. Prior descriptive exposure must be reported honestly and does not permit using final-test forecasting results to select features, models, hyperparameters or validation policies.

## Leakage rules

- Preserve chronological order and the native `SKU_ID + Warehouse_ID + Date` grain. Apply identical temporal boundaries to all candidate models.
- Fit learned preprocessing, transformations and models only on the relevant fold's training observations. Validation data must not influence fitted transformation parameters.
- Construct lags and rolling features within each native series using only information available at the prediction origin. Exclude the current target and future observations, consistent with DR-003.
- Do not substitute realised validation/test demand for unavailable future inputs in a multi-step forecast issued at an earlier origin. Recursive versus direct prediction remains open.
- Do not use source `Demand_Forecast` as an ordinary forecasting feature. `Stockout_Flag` remains unusable as a stockout target or validation label.
- `Promotion_Flag` treatment remains open; any eventual use must be justified as known at the prediction origin. Do not assume future inventory state is available.
- Keep all validation horizon outcomes inside the assigned validation interval and all final-test horizon outcomes inside the holdout. Do not borrow later outcomes or silently score incomplete horizons.
- Exclude the final holdout from fitting, feature/model selection, hyperparameter tuning and validation decisions. Do not adjust the schedule in response to final-test performance.

## Impact and limitations

The research design, forecasting workflow and decision index now use this approved schedule. The earlier EDA remains historical descriptive evidence; it is not rewritten as if these folds had been selected before exploration. No training, feature-generation, forecasting-model or split-generation code is introduced by this decision.

The dataset is simulated and covers only one observed year. Four validation windows cannot represent every possible demand condition or establish recurring annual seasonality or real-retailer effectiveness. Expanding folds share training history, so their results should not be treated as independent replicates without justification. More training history and a different evaluation period change together across folds; performance differences cannot automatically be attributed to demand behaviour alone. The final holdout covers only 14 days in late December and cannot independently establish performance throughout a full year. Prior EDA exposure and validation over-tuning remain limitations to disclose.

## Decisions still open

- Exact forecasting model families.
- Recursive versus direct multi-step forecasting and any within-window forecast-update protocol.
- Final lag set.
- `Promotion_Flag` usage.
- Final model-selection metric policy, including horizon/fold aggregation and scoring details.
- Hyperparameter search strategy.
- Uncertainty method.
- Demand-regime definitions.

These require separate evidence and approval. This decision records the approved forecasting-methodology direction in Issue #31; it does not assert separate supervisor approval. Any supervisor confirmation required by the project remains subject to the team's review process.
