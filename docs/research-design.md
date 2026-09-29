# Research Design

> **Documentation alignment — 2026-09-29:** The project owner has approved the 1/7/14/28-day forecasting design and [frozen feature contract](forecasting-feature-engineering.md). This alignment records that human instruction, not new experiment evidence or separate supervisor approval. [Revision and provenance](forecasting-methodology-revision.md) records remaining approval boundaries.

## 1. Purpose

This document defines the current research-design baseline for the COMP1884 group project. Hypotheses are treated as testable statements and will only be finalised when their variables and evaluation methods are operationally defined.

## 2. Main research question

**How can data-driven demand forecasting be used to identify inventory risks and support supply-chain decision-making in retail operations?**

## 2.1 Primary group-level hypothesis

### H0

Demand forecasting does not significantly improve inventory-risk identification and supply-chain decision support.

### H1

Demand forecasting significantly improves inventory-risk identification and supply-chain decision support.

This is the primary hypothesis for the integrated group research. Its baseline, measurable inventory-risk outcome(s), decision-support outcome(s), and statistical testing must be operationally defined before final hypothesis testing.

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

### 6.1 Frozen predictor contract

The [authoritative feature specification](forecasting-feature-engineering.md) freezes exactly **14 conceptual predictors: two categorical context predictors and twelve engineered numerical predictors**, in the same order for Ridge Regression, Random Forest Regressor and LightGBM Regressor across horizons 1/7/14/28.

- Context: `SKU_ID`, `Warehouse_ID`.
- Calendar: `dow_sin`, `dow_cos`, derived from the first target day, origin + 1.
- Demand memory: `lag_1`, `lag_7`, `lag_14`.
- Recent level/dispersion: mean and sample standard deviation (`ddof=1`) over complete 7-, 14- and 28-day histories ending at the origin.
- Direction: `rolling_slope_14` over the ordered fourteen-day history.

The whole vector requires **28 complete consecutive daily observations per SKU–warehouse**. All inputs use only origin-available information; no realised demand inside a forecast window updates the vector. Training rows require complete horizon labels ending by their fitting cutoff. Learned preprocessing fits only eligible training rows.

### 6.2 Representation and raw-field boundaries

Ridge and Random Forest use full one-hot SKU/warehouse encoding: 50 + 5 + 12 = **67 physical columns**. LightGBM uses two native categorical identities plus the twelve numerical features = **14 physical inputs**. Every learned model receives the same fourteen conceptual predictors and equivalent underlying information; fair comparison does not require identical matrix width. IDs are nominal categories, never continuous measurements.

`Date` supplies alignment/calendar construction; `Units_Sold` supplies past demand and outcome labels. The eleven other raw fields are excluded from the forecasting predictor matrix, including promotion, price and inventory variables. They may retain descriptive or downstream roles. A human-readable weekday label may be derived downstream; it is not a predictor.

Raw weekday, weekday dummies, month/quarter and annual/holiday encodings, lag 28, medians, additional windows and unapproved composites are excluded. Exact formulas, ordering, exclusions and availability rules live in the feature specification. The earlier DR-003/Issue #52 catalogues and reviewed alternatives are superseded provenance, not active choices or an ablation plan.

## 7. Forecast horizon

Under the human-approved forecasting design, the project evaluates four decision-support forecast horizons while retaining the approved daily SKU-warehouse analytical grain:

- **1-day horizon** — immediate next-day demand for each SKU-warehouse series;
- **7-day horizon** — cumulative demand over the next 7 days;
- **14-day horizon** — cumulative demand over the next 14 days;
- **28-day horizon** — cumulative demand over the next four weeks / approximately monthly planning, not an exact calendar month.

These horizons are selected as project-specific planning horizons rather than universal retail replenishment rules.

The external inventory literature supports periodic-review inventory systems in which stock is reviewed and replenishment decisions are made at defined review intervals, and it shows that review-period choice interacts with demand, supply variability, and lead time (Silver and Robb, 2008; Lee and Schwarz, 2009). In the verified project dataset, `Supplier_Lead_Time_Days` ranges from 2 to 14 days. The 1-, 7- and 14-day views cover immediate, weekly and lead-time-scale forecasting. Human review adds 28 days for four-week / approximately monthly planning, not an exact calendar month. Supplier lead time alone does not justify this addition. Downstream 28-day use remains subject to component-owner approval.

The daily analytical grain and the forecast horizon are different concepts:

```text
analytical grain = one SKU + one warehouse + one day
forecast horizon = how far ahead demand is predicted
```

A 7-day, 14-day or 28-day demand view must preserve the SKU-warehouse identity and the cumulative-demand meaning recorded in revised DR-004.

[DR-008 — Multi-Step Forecasting Strategy](decisions/DR-008-multi-step-forecasting-strategy.md) selects **direct horizon-specific forecasting** as the primary strategy. Separate horizon targets are predicted directly from information available at the forecast origin:

- 1-day next-day demand;
- 7-day cumulative demand;
- 14-day cumulative demand; and
- 28-day cumulative demand.

Earlier predictions are not fed into later horizon predictions. The 7-, 14- and 28-day cumulative outputs do not imply a daily forecast path. This alignment between training target, evaluation horizon, and downstream cumulative demand avoids recursive error propagation, but it is a project-specific choice rather than a claim that direct forecasting is universally superior.

## 8. Forecasting approach

[DR-007 — Forecasting Model Set](decisions/DR-007-forecasting-model-set.md) approves the following candidates to compare increasing levels of modelling complexity:

| Role | Model | Purpose |
| --- | --- | --- |
| Simple baseline | Naive | Test whether more complex models improve on a simple recent-demand benchmark. |
| Seasonal baseline | Seasonal Naive using lag 7 | Test whether repeating weekly demand provides a useful benchmark. |
| Linear ML baseline | Ridge Regression | Provide a regularised linear baseline for relationships between engineered features and demand. |
| Tree-based ML | Random Forest | Capture non-linear relationships and feature interactions. |
| Gradient-boosting ML | LightGBM | Provide a stronger boosted-tree candidate for comparison with simpler models. |

[DR-009 — Gradient-Boosting Model Choice](decisions/DR-009-gradient-boosting-model-choice.md) selects LightGBM as the single gradient-boosting implementation. The choice controls overlapping dependency and tuning scope for this project; it does not claim that LightGBM is universally better than XGBoost or that it will outperform another candidate. Every candidate must use the same DR-005 validation folds, DR-008 direct targets, and DR-006 evaluation policy.

### 8.1 Hyperparameter-search strategy

[DR-010 — Forecasting Hyperparameter-Search Strategy](decisions/DR-010-hyperparameter-search-strategy.md) defines small, predefined search spaces for Ridge Regression, Random Forest, and LightGBM. Naive and Seasonal Naive remain untuned baselines. Each learned model is tuned separately for the 1-day, 7-day, 14-day, and 28-day horizons by evaluating every approved parameter combination on the same four DR-005 expanding-window folds. Mean WAPE across folds is the primary tuning statistic under DR-006; fold-level stability, MAE, RMSE, and Bias must also be reviewed.

Search spaces must not be changed ad hoc in response to disappointing validation results. Any revision requires a documented reason and approval before rerunning. Selected settings are frozen before evaluation on the revised final evaluation interval, and results from that interval must never inform tuning or search-space changes. DR-005 records its boundaries and prior-validation-exposure provenance. Ordinary random K-fold cross-validation is not permitted because it would break temporal order.

## 9. Validation design

Use four expanding-window chronological folds, with one fixed forecast origin
at the training cutoff for every SKU–warehouse and horizon. There is no updating
with realised demand inside a validation window. All dates are inclusive and
calendar-day counts precede feature warm-up and complete-target exclusions.

| Fold | Training start | Training end / origin | Training days | Validation start | Validation end | Validation days |
|---|---|---|---:|---|---|---:|
| 1 | 2024-01-01 | 2024-03-31 | 91 | 2024-04-01 | 2024-04-28 | 28 |
| 2 | 2024-01-01 | 2024-06-30 | 182 | 2024-07-01 | 2024-07-28 | 28 |
| 3 | 2024-01-01 | 2024-09-30 | 274 | 2024-10-01 | 2024-10-28 | 28 |
| 4 | 2024-01-01 | 2024-11-04 | 309 | 2024-11-05 | 2024-12-02 | 28 |

**Revised final evaluation:** 2024-12-03 to 2024-12-30 inclusive, 28 days;
forecast origin 2024-12-02. No December 31 observation is invented.

### Evidence and the three-fold alternative

Historical EDA reports March/April means of 29.8834/29.8391, July 17.4084,
September/October 10.1739/10.2708 and November 13.0807 units per native observation.
The saved notebook's monthly/quarterly tables and retrospective daily chart
support high levels, decline, low demand and recovery within this simulated year;
they do not establish recurring annual seasonality or formal demand regimes.

Three folds were considered and remain methodologically feasible: April high
demand, July decline and October low demand. They omit separate recovery validation.
**Four folds provide broader validation evidence across distinct observed temporal
demand conditions while preserving expanding-window chronological evaluation.**
The recovery-period evidence in November–early December was considered useful
for this one-year dataset. November 5 is the latest complete 28-day placement
before the revised final interval, not an EDA-established change point.

Four is a project-specific human choice, not statistically optimal. Expanding
folds share training history and are not independent replicates. More folds
increase computational workload and validation-selection exposure; validation
folds do not make models learn more patterns. Training length and evaluation
conditions change together, so differences cannot automatically be attributed
to demand conditions alone. Fold 3/4 origins are only 35 days apart, with seven
unscored days between their validation windows.

### Target completeness, warm-up and non-overlap

At each cutoff, next-day and cumulative 7-, 14- and 28-day targets fit completely
inside its 28-day evaluation window. In this project's selected fixed-origin
protocol, a 28-day validation window is not treated as 28 forecast origins;
one origin and one target per series/horizon are used.
All training labels must end by their training cutoff. Features use only history
available at the row's own origin; scalers/learned transformations fit only training
rows. Never use realised future demand or target labels as predictors.

The four validation windows do not overlap each other or the revised final interval.
Earlier validation outcomes may enter later training only once historical to the
later cutoff. Unscored gaps may enter later training; no final-evaluation observations
may enter fitting or subsequent selection. Missing/incomplete outcomes remain
unavailable, not zero, shortened labels or reasons to borrow later dates.

A 28-day feature warm-up is feasible even in the initial 91-day history. With a
complete 28-day look-back and horizon h, eligibility is N − 28 − h + 1 rows per
series before other exclusions: 63/57/50/36 for h=1/7/14/28 in fold 1. This is
feasibility, not a guarantee of model adequacy. The frozen feature contract requires this complete 28-day history for every learned model and horizon.

### Final-evaluation provenance and protection

The revised 28-day final evaluation window is reserved from all subsequent
feature, model and hyperparameter decisions and fitting. However, December 3–16
had prior validation exposure under the earlier 14-day methodology, so the revised
window is not fully unseen from the historical research process. Full-year
historical EDA also inspected those dates. Final forecasting results must not feed
back into selection, and this prior exposure must be disclosed in reporting.

The September 22 boundaries are retained as historical provenance in DR-005; the earlier Issue #52 protocol and results are not the revised study baseline.

## 10. Approved forecasting metrics and model-selection policy

[DR-006](decisions/DR-006-forecasting-metrics-and-model-selection.md) selects **Weighted Absolute Percentage Error (WAPE)** as the primary forecasting model-selection metric. Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and Forecast Bias / Mean Forecast Error are supporting metrics that must be reviewed before final selection.

For the equations below:

- $y_i$ is actual demand;
- $\hat{y}_i$ is forecast demand; and
- $n$ is the number of observations.

### Mean Absolute Error (MAE)

$$
\mathrm{MAE} =
\frac{1}{n}
\sum_{i=1}^{n}
\left|y_i-\hat{y}_i\right|
$$

### Root Mean Squared Error (RMSE)

$$
\mathrm{RMSE} =
\sqrt{
\frac{1}{n}
\sum_{i=1}^{n}
\left(y_i-\hat{y}_i\right)^2
}
$$

### Weighted Absolute Percentage Error (WAPE)

$$
\mathrm{WAPE} =
\frac{
\sum_{i=1}^{n}
\left|y_i-\hat{y}_i\right|
}{
\sum_{i=1}^{n}
\left|y_i\right|
}
$$

### Forecast Bias / Mean Forecast Error

$$
\mathrm{Bias} =
\frac{1}{n}
\sum_{i=1}^{n}
\left(\hat{y}_i-y_i\right)
$$

### Metric roles and interpretation

| Metric | What it measures | Ideal / best value | Better direction | Role in this research |
| --- | --- | ---: | --- | --- |
| MAE | Average absolute forecast error in demand units. | 0 | Lower is better. | Supporting measure of typical error magnitude. |
| RMSE | Square-root of the average squared error; larger errors receive more weight because errors are squared. | 0 | Lower is better. | Supporting measure that highlights relatively large errors. |
| WAPE | Total absolute error relative to total absolute actual demand. | 0 or 0% | Lower is better. | Primary model-comparison and selection metric. |
| Bias | Average signed error, calculated as forecast minus actual demand. | 0 | Closer to 0 is better. | Supporting measure of systematic overforecasting or underforecasting. |

Positive bias indicates systematic overforecasting, while negative bias indicates systematic underforecasting. A value near zero indicates little net directional error, but positive and negative errors can cancel, so bias must not be interpreted alone.

### Why WAPE is primary

MAE and RMSE are scale-dependent and remain expressed in demand units. Because SKU-warehouse series may operate at different demand scales, WAPE provides a clearer main relative comparison by normalising total absolute error against total actual demand.

This choice is specific to the approved project design. It does not establish that WAPE is universally superior for every forecasting problem, and no universal quality bands such as “WAPE below 10% is good” are adopted. Model quality must be judged relative to the same baseline models, folds, horizons, and evaluation design. WAPE is undefined when the sum of absolute actual demand is zero; any such case must be reported explicitly rather than silently divided by zero.

### Fold and horizon evaluation policy

Every candidate model must be evaluated on the same four DR-005 validation folds for each horizon included in the current methodology at execution time. For each model and each horizon independently:

1. calculate MAE, RMSE, WAPE, and Bias separately for every fold;
2. calculate the arithmetic mean of each metric across the four folds;
3. use mean WAPE across folds as the primary model-selection statistic; and
4. review supporting mean MAE, RMSE, and Bias together with the individual fold results.

Comparisons are made separately for each horizon included in the current methodology at execution time. Metrics must not be averaged or weighted across the 1-day, 7-day, 14-day, and 28-day horizons into one overall score.

The selected model will be the candidate with the lowest mean WAPE across the validation folds included in the current methodology at execution time for the relevant horizon, subject to acceptable fold-to-fold stability and supporting-metric review. Selection must not be based on one fold alone. A candidate with low mean WAPE but highly unstable fold results must be discussed rather than automatically described as robust. No arbitrary numerical stability threshold is introduced by this decision.

Results from the revised final evaluation interval are used only after model selection and must not be used to revise the selected model, features, hyperparameters, metric policy, or other selection decisions.

### Mean Absolute Percentage Error (MAPE)

MAPE is not part of the primary approved model-selection policy. It may be reported only as an optional supplementary metric with appropriate safeguards where actual demand is zero or near zero.

## 11. Secondary forecasting hypothesis

This secondary hypothesis applies to Chathuranga's forecasting / machine-learning component and supports the primary group-level hypothesis.

### H0

Forecasting performance does not significantly differ across temporal demand conditions.

### H1

Forecasting performance significantly differs across temporal demand conditions.

This remains provisional until temporal demand conditions and the statistical testing procedure are operationally defined.

## 12. Inventory-risk and replenishment interpretation

Subject to group approval, Didilani's component would apply [DR-012 — Inventory-Risk and Replenishment Methodology](decisions/DR-012-inventory-risk-replenishment-methodology.md) to project model forecasts and origin-available inventory evidence. The proposed initial interpretation in DR-012 is **origin reorder-threshold exposure**.

For the same SKU-warehouse at forecast origin `t`, define `I_t = Inventory_Level_at_origin`, `R_t = Reorder_Point_at_origin`, and `B_t = I_t - R_t`. For forecast cumulative demand `F_t,h`:

| Condition | Interpretation |
|---|---|
| `B_t <= 0` | Already at/below the origin reorder threshold |
| `B_t > 0` and `F_t,h >= B_t` | Forecast threshold crossing within the horizon |
| `B_t > 0` and `F_t,h < B_t` | No forecast threshold crossing within the horizon |

Use origin-available snapshots, keep the origin threshold fixed, and assume no receipts, transfers, returns, losses or other adjustments during the scenario. The original proposed downstream scope applies separately to next-day, 7-day cumulative and 14-day cumulative demand over `t+1` through `t+h`. The new 28-day forecast is mathematically compatible with the generic formula, but **28-day downstream use requires component-owner/human approval**; the longer no-receipt interpretation is not approved here. Equality counts as reaching the threshold. Missing/invalid required evidence produces unavailable/not assessed, not `FALSE`. Within-day snapshot semantics and handling of problematic forecasts remain explicit input-contract decisions; no forecast clipping is introduced here.

The primary retrospective comparison replaces `F_t,h` with realised cumulative `Units_Sold` over the exact same horizon and uses `B_t > 0` cases. Report origin-known already-at/below-threshold cases separately to avoid inflating agreement. DR-012 defines event prevalence, counts, missed-crossing rate, false-alert rate, agreement, precision, recall and balanced accuracy, with explicit denominators and unavailable results for undefined metrics. Check prevalence and do not artificially rebalance the historical population. The conceptual margins are `B_t - F_t,h` and `B_t - realised_demand`; no numeric near-boundary band is approved.

Relevant evidence includes:

- `Inventory_Level`;
- `Reorder_Point`;
- `Supplier_Lead_Time_Days` as context only: horizon shorter than, equal to, or longer than lead time, without rounding or interpolation;
- `Order_Quantity` as contextual activity, not receipts or optimal-policy ground truth;
- forecast error / uncertainty;
- product and warehouse identifiers.

The goal is to transform the forecast into inventory-risk and replenishment information rather than forecast demand a second time.

Verified profiling shows that `Stockout_Flag` is 0 for every row, so it cannot be used as a stockout classification target or validation label. `Order_Quantity` is also sparse: only 5,027 of 91,250 rows contain a non-zero order quantity. These findings must shape the downstream method.

The output is constructed threshold-exposure evidence, not actual stockout prediction or actual shortage ground truth. Negative arithmetic projected balances do not establish physical negative inventory. Source `Demand_Forecast` is not the project model forecast, and future inventory values cannot be origin-time inputs.

Overstock/excess-stock evaluation and final numerical replenishment quantities remain provisional. Not reaching the threshold is not evidence of overstock. The common method supports the primary forecast-to-decision study, while the cross-component evaluation protocol, uncertainty method, human-review thresholds and final hypothesis operationalisation remain later decisions. DR-006 WAPE-based forecasting selection is unchanged.

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


The management-facing output follows the structure defined in DR-011. It keeps `SKU_ID`, `Warehouse_ID`, forecast origin, and forecast horizon visible so that each output can be traced back to its forecasting context. Under the revised direction, the 7-day, 14-day and 28-day forecasts represent cumulative demand over their respective horizons, without implying a daily forecast path. Representing a 28-day cumulative forecasting output does not itself approve downstream 28-day inventory/replenishment use; that remains subject to component-owner/human approval. DR-012 proposes the initial inventory exposure method; group approval, implementation and the final schema remain pending. Uncertainty, overstock, numerical replenishment and human-review rules remain provisional until their related decisions are approved.

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
