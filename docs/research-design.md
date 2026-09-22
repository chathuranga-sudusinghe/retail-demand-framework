# Research Design

## 1. Purpose

This document defines the current research-design baseline for the COMP1884 group project. Hypotheses are treated as testable statements and will only be finalised when their variables and evaluation methods are operationally defined.

## 2. Main research question

**How can data-driven demand forecasting be used to identify inventory risks and support supply-chain decision-making in retail operations?**

## 3. Source and analytical unit

The selected source is the **High-Dimensional Supply Chain Inventory Dataset**, a simulated daily SKU-level supply-chain dataset.

The primary forecasting unit is a regular **SKU-warehouse-day** demand time series derived from `Units_Sold`.

This decision is recorded in `docs/decisions/DR-002-forecasting-analytical-unit.md` and is supported by the temporal and inventory-alignment profiling in `reports/temporal-demand-profile.md`.

The selected grain is:

```text
SKU_ID + Warehouse_ID + Date
```

Profiling showed that each SKU-warehouse series has 365 observations with complete temporal coverage and very low median zero-demand frequency. It also showed that `Inventory_Level`, `Reorder_Point`, and `Supplier_Lead_Time_Days` vary across warehouses for every SKU-day, so aggregating demand across warehouses would discard operational context needed by the downstream inventory-risk component.

SKU-day and SKU-week may still be used for descriptive comparison, visualisation, or sensitivity analysis, but they are not the primary modelling grain.

## 4. Forecasting target

Primary source variable:

```text
Units_Sold
```

Primary target at the selected analytical unit:

```text
Demand(SKU_ID, Warehouse_ID, Date) = Units_Sold
```

Because the verified native source grain is one unique row per `Date + SKU_ID + Warehouse_ID`, no additional demand aggregation is required for the primary forecasting view.

The project will build its own forecasting models. The dataset's source-provided `Demand_Forecast` field is **not the project's target** and must not be used as an ordinary predictor if doing so would leak target/future information. It may only be used later as a clearly separated external/source benchmark if methodologically justified.

## 5. Temporal characteristics to investigate

The forecasting component may examine:

- trend;
- seasonality;
- autocorrelation / lag dependence;
- volatility;
- changes in demand level;
- SKU-to-SKU heterogeneity;
- promotion-related effects where leakage-safe.

## 6. Forecasting feature engineering

Feature engineering converts the approved SKU-warehouse-day demand history into model inputs that represent recent demand memory, short-term demand behaviour, and calendar effects without exposing the model to future information.

### 6.1 Calendar features

#### `day_of_week`

**Definition:** day of the week associated with the forecast date.

**Why considered:** daily retail demand may differ between weekdays and weekends or show repeating weekly behaviour.

**Leakage rule:** it is derived only from the known calendar date.

#### `month`

**Definition:** calendar month associated with the forecast date.

**Why considered:** it may capture broad within-year demand differences.

**Caution:** the dataset contains only approximately one year of data, so month effects must not be interpreted as robust multi-year seasonality.

#### `quarter`

**Definition:** calendar quarter associated with the forecast date.

**Why considered:** it may provide a coarse within-year temporal grouping.

**Caution:** as with month, the one-year dataset limits claims about repeated annual seasonal behaviour.

#### `week_of_year` — excluded from the primary feature set

`week_of_year` is not included in the primary forecasting feature set. The dataset contains only one year of observations, so each numbered week occurs only once. The project therefore lacks repeated year-over-year evidence from which a model could learn a stable week-number effect.

This does not mean that weekly behaviour is ignored. Weekly demand structure can instead be represented through features such as `day_of_week`, lagged demand, and 7-day rolling statistics.

### 6.2 Lag features

Lag features represent demand observed at an earlier point in the same SKU-warehouse series.

Candidate lags currently include:

- `lag_1` — `Units_Sold` one day earlier;
- `lag_7` — `Units_Sold` seven days earlier;
- `lag_14` — `Units_Sold` fourteen days earlier;
- `lag_28` — `Units_Sold` twenty-eight days earlier.

**Why considered:** lag features provide the model with direct information about recent demand and possible repeating short-cycle behaviour.

**Leakage rule:** for a forecast at time `t`, the lagged value must come only from observations strictly before `t`.

The exact final lag set remains open and must be justified through modelling evidence rather than selected mechanically.

### 6.3 Rolling features

Rolling features summarise recent historical demand over a fixed look-back window for the same SKU-warehouse series.

The initial approved rolling windows are:

- **7 days** — represents recent weekly demand behaviour;
- **14 days** — provides a smoother two-week view of recent demand.

Candidate rolling statistics are:

- `rolling_mean_7` and `rolling_mean_14` — average historical demand in the previous 7 or 14 days;
- `rolling_median_7` and `rolling_median_14` — typical recent demand with reduced sensitivity to unusual spikes;
- `rolling_std_7` and `rolling_std_14` — recent demand variability / volatility.

A 30-day rolling window is not part of the initial primary feature set. It may be examined later as a sensitivity or alternative feature only if evidence justifies it.

**Leakage rule:** the current target value must never be included in its own rolling calculation. Rolling statistics for time `t` must be calculated from observations before `t` only.

### 6.4 Recent growth / decline indicators

A recent growth or decline feature would summarise whether recent demand is increasing, decreasing, or broadly stable.

**Why considered:** it may help represent short-term direction that is not fully captured by one individual lag.

**Status:** candidate only. The exact calculation has not yet been approved and must not be invented during implementation.

### 6.5 Exogenous variables

`Promotion_Flag` may be considered only when it would genuinely be known at the prediction origin. Profiling found that promotion status conflicts across warehouses in approximately 41.6% of SKU-day groups, which further supports retaining the warehouse dimension rather than collapsing to one SKU-day promotion value.

The final treatment of `Promotion_Flag` remains an open methodology decision.

Inventory fields should not automatically be inserted into the forecasting model. Their role must be justified separately from their downstream use in inventory analysis.

### 6.6 Features not yet defined

The project has not approved additional composite forecasting features created by summing, subtracting, multiplying, or dividing multiple raw columns.

Examples that are **not currently approved forecasting features** include:

- `Inventory_Level - Reorder_Point`;
- `Unit_Price - Unit_Cost`;
- `Unit_Price / Unit_Cost`;
- lead-time-demand combinations;
- other inventory-policy-derived variables.

Such variables may belong more naturally to downstream inventory-risk analysis and must not be added to the forecasting model without separate evidence and approval.

All forecasting features must be generated without future-data leakage.

## 7. Forecast horizon

The project will evaluate three decision-support forecast horizons while retaining the approved daily SKU-warehouse analytical grain:

- **1-day horizon** — immediate next-day demand for each SKU-warehouse series;
- **7-day horizon** — cumulative demand over the next 7 days;
- **14-day horizon** — cumulative demand over the next 14 days.

These horizons are selected as project-specific planning horizons rather than universal retail replenishment rules.

The external inventory literature supports periodic-review inventory systems in which stock is reviewed and replenishment decisions are made at defined review intervals, and it shows that review-period choice interacts with demand, supply variability, and lead time (Silver and Robb, 2008; Lee and Schwarz, 2009). In the verified project dataset, `Supplier_Lead_Time_Days` ranges from 2 to 14 days. The 1-, 7-, and 14-day horizons therefore provide an interpretable set of immediate, weekly, and lead-time-scale demand views for downstream inventory-risk and replenishment analysis.

The daily analytical grain and the forecast horizon are different concepts:

```text
analytical grain = one SKU + one warehouse + one day
forecast horizon = how far ahead demand is predicted
```

A 7-day or 14-day demand view may be produced from daily forecasts while preserving daily SKU-warehouse predictions.

This horizon decision does **not** yet determine the multi-step forecasting strategy (for example, recursive versus direct multi-horizon forecasting). That implementation choice remains open and must be evaluated without future-data leakage.

## 8. Forecasting approach

The forecasting component should compare appropriate levels of complexity, for example:

1. naive / seasonal-naive benchmark;
2. statistical time-series method(s);
3. regression-based forecasting;
4. machine-learning forecasting.

The exact model set will be justified by literature, data behaviour, time available, and the research question.

## 9. Validation design

[DR-005 — Forecast Validation Design](decisions/DR-005-forecast-validation-design.md), approved through [Issue #31](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/31), selects **expanding-window time-series validation**: rolling-origin / walk-forward evaluation with an expanding training window. Random train/test splitting must not be used.

All candidate models use the same four folds at the approved `SKU_ID + Warehouse_ID + Date` grain and evaluate `Units_Sold` over the 1-day, 7-day and 14-day horizons. Training begins on 2024-01-01 in every fold. All dates below are inclusive; training-day counts are per series before any approved feature-history requirements.

| Fold | Training start | Training end / origin cutoff | Training days | Validation start | Validation end | Validation days |
| --- | --- | --- | ---: | --- | --- | ---: |
| 1 | 2024-01-01 | 2024-03-31 | 91 | 2024-04-01 | 2024-04-14 | 14 |
| 2 | 2024-01-01 | 2024-06-30 | 182 | 2024-07-01 | 2024-07-14 | 14 |
| 3 | 2024-01-01 | 2024-09-30 | 274 | 2024-10-01 | 2024-10-14 | 14 |
| 4 | 2024-01-01 | 2024-12-02 | 337 | 2024-12-03 | 2024-12-16 | 14 |

**Final model-evaluation holdout:** 2024-12-17 to 2024-12-30 inclusive, exactly **14 calendar days**.

Fold 4 validation ends on 2024-12-16, immediately before the holdout, without overlap. Earlier validation observations enter later training histories only once they are historical relative to the later cutoff.

### Evidence and fold-count rationale

The [completed EDA](../reports/demand-eda.md) reports monthly means of approximately 29.883 in March and 10.174 in September, with Q1/Q2 means around 26.6 and Q3/Q4 means around 13.5–13.6. These are means per native SKU-warehouse-day observation. They support placing validation origins across different observed demand periods, without claiming recurring annual seasonality or defining final seasonal regimes.

Four folds balance temporal coverage, a 91-day initial history, the maximum 14-day forecast horizon, consistent 14-day validation windows, repeated out-of-sample evaluation and a separate 14-day final holdout. They also avoid unnecessarily dense or similar origins. Four is a project-specific choice, not a universal optimum. Two folds are technically valid but less informative; three are methodologically reasonable, while four adds coverage without sacrificing the initial history or holdout. Five or more folds may, depending on their placement, require shorter early histories or create closer, more similar, or overlapping evaluation periods and additional opportunities for validation over-tuning. They do not automatically cause model overfitting. DR-005 records the full comparison.

### Windows, horizons and leakage

A **training window** contains historical observations used to fit the model. A **validation window** contains future observations used to compare models and settings. A **forecast horizon** is the look-ahead from a prediction origin: next-day demand or cumulative demand over the next 7 or 14 days, as defined in DR-004. A **final test holdout** is evaluated only after model selection is complete. A 14-day validation window accommodates the maximum horizon but is not the same concept as a 14-day forecast horizon.

Fit learned preprocessing and models within each fold's training window. Construct features only from information available at the prediction origin; current targets and later actual demand must not enter their own forecasts. Source `Demand_Forecast` remains excluded from ordinary forecasting features. Any eventual promotion or inventory input must satisfy its approved availability rules. Require complete horizon outcomes inside the assigned evaluation interval; validation scoring must not extend into the final holdout.

### Final holdout and disclosure

The final holdout must not be used for model fitting, feature/model selection, hyperparameter tuning or validation decisions. Final-test forecasting results are examined only after model selection is complete and must not inform subsequent model-selection choices.

Full-year descriptive EDA has already inspected the complete dataset, including the dates later assigned to this holdout. **Untouched final test** describes its exclusion from fitting and selection/tuning decisions and the protection of its forecasting results; it does not claim the dates were never descriptively inspected. Disclose that prior exposure. The 14-day late-December holdout is also a limited evaluation period, and expanding folds share history rather than being independent replicates.

Exact model families, recursive versus direct multi-step forecasting, final lags, `Promotion_Flag` usage, final model-selection metric policy, hyperparameter search strategy, uncertainty method and demand-regime definitions remain open. This documentation decision introduces no split-generation or modelling implementation.

## 10. Forecasting metrics

Candidate metrics include:

### Mean Absolute Error (MAE)

```text
MAE = (1 / n) * sum(|p_i - y_i|)
```

### Root Mean Squared Error (RMSE)

```text
RMSE = sqrt((1 / n) * sum((p_i - y_i)^2))
```

### Weighted Absolute Percentage Error (WAPE)

```text
WAPE = sum(|p_i - y_i|) / sum(|y_i|)
```

### Mean Absolute Percentage Error (MAPE)

MAPE may be reported with appropriate safeguards where actual demand is zero or near zero.

### Forecast Bias / Mean Forecast Error

```text
Bias = (1 / n) * sum(p_i - y_i)
```

Interpretation:

- positive bias -> systematic overforecasting;
- negative bias -> systematic underforecasting;
- near zero -> little net directional error.

## 11. Group-level forecasting hypothesis direction

### H0

Forecasting performance does not significantly vary across different temporal demand behaviours.

### H1

Forecasting performance varies significantly across different temporal demand behaviours, and different forecasting approaches show different suitability across demand regimes.

This remains provisional until demand-regime definitions and statistical tests are operationalised.

## 12. Inventory-risk and replenishment interpretation

Didilani's component will consume the selected forecast outputs together with relevant inventory variables, potentially including:

- `Inventory_Level`;
- `Reorder_Point`;
- `Supplier_Lead_Time_Days`;
- `Order_Quantity`;
- forecast error / uncertainty;
- product and warehouse identifiers.

The goal is to transform the forecast into inventory-risk and replenishment information rather than forecast demand a second time.

Verified profiling shows that `Stockout_Flag` is 0 for every row, so it cannot be used as a stockout classification target or validation label. `Order_Quantity` is also sparse: only 5,027 of 91,250 rows contain a non-zero order quantity. These findings must shape the downstream method.

Candidate downstream outputs include:

- low/medium/high replenishment risk;
- stockout-pressure indicators;
- overstock/excess-inventory indicators;
- reorder alerts;
- recommended replenishment quantity where a defensible method is defined.

The exact formula/rules must be operationalised and evaluated before implementation is considered final.

## 13. Responsible decision support

Dewmi's component will consume forecast and inventory-risk/replenishment outputs and should communicate:

- what the model predicts;
- inventory/risk interpretation;
- forecast uncertainty;
- evidence used by the rule/model;
- assumptions and limitations;
- management considerations;
- whether human review is required.

The framework supports decisions; it does not automatically execute replenishment actions.

## 14. End-to-end framework

```text
Historical sales and supply-chain data
        ->
Forecasting model
        ->
Forecast output
        ->
Inventory-risk / replenishment analysis
        ->
Responsible decision-support logic
        ->
Management-facing output
```

## 15. Threats to validity

Important threats include:

- the dataset is simulated, not observed from a real operating retailer;
- approximately one year of data limits long-cycle seasonal inference;
- source-generated variables may embed assumptions from the simulation;
- `Demand_Forecast` may create leakage if incorrectly used;
- product/warehouse aggregation choices may affect conclusions;
- `Stockout_Flag` is zero-variance in the downloaded dataset and cannot validate stockout predictions;
- non-zero `Order_Quantity` events are sparse and may limit direct replenishment-target modelling;
- model and inventory thresholds may be sensitive to the chosen evaluation period;
- performance on the simulated dataset does not establish production effectiveness in a real company.

These limitations must be considered in method selection and conclusions.
