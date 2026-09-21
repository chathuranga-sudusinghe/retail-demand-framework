# Research Design

## 1. Purpose

This document defines the current research-design baseline for the COMP1884 group project. Hypotheses are treated as testable statements and will only be finalised when their variables and evaluation methods are operationally defined.

## 2. Main research question

**How can data-driven demand forecasting be used to identify inventory risks and support supply-chain decision-making in retail operations?**

## 3. Source and analytical unit

The selected source is the **High-Dimensional Supply Chain Inventory Dataset**, a simulated daily SKU-level supply-chain dataset.

The primary forecasting unit is expected to be a regular product-demand time series derived from `Units_Sold`.

Candidate units include:

- SKU-day demand aggregated across operational dimensions;
- SKU-warehouse-day demand if warehouse-level forecasting is justified;
- SKU-week demand if daily series prove too noisy or sparse.

The final analytical unit must be documented before model training.

## 4. Forecasting target

Primary source variable:

```text
Units_Sold
```

Candidate primary target:

```text
Demand(SKU, period) = sum(Units_Sold)
```

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

## 6. Candidate feature families

### Calendar features

- day of week;
- week of year;
- month;
- quarter.

### Lag features

Examples may include:

- lag 1;
- lag 7;
- lag 14;
- lag 28.

Exact lags depend on the final aggregation frequency and must not be selected mechanically.

### Rolling features

Examples:

- rolling mean;
- rolling median;
- rolling standard deviation;
- recent growth or decline indicators.

### Exogenous variables

Variables such as `Promotion_Flag` may be considered only when they would genuinely be known at the prediction origin.

Inventory fields should not automatically be inserted into the forecasting model. Their role must be justified separately from their downstream use in inventory analysis.

All features must be generated without future-data leakage.

## 7. Forecasting approach

The forecasting component should compare appropriate levels of complexity, for example:

1. naive / seasonal-naive benchmark;
2. statistical time-series method(s);
3. regression-based forecasting;
4. machine-learning forecasting.

The exact model set will be justified by literature, data behaviour, time available, and the research question.

## 8. Validation design

Random train/test splitting is inappropriate for the main time-series evaluation because it can leak future information into training.

Preferred design:

```text
past -> train
later period -> validation
future holdout -> test
```

Where feasible, use rolling-origin or walk-forward evaluation.

## 9. Forecasting metrics

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

## 10. Group-level forecasting hypothesis direction

### H0

Forecasting performance does not significantly vary across different temporal demand behaviours.

### H1

Forecasting performance varies significantly across different temporal demand behaviours, and different forecasting approaches show different suitability across demand regimes.

This remains provisional until demand-regime definitions and statistical tests are operationalised.

## 11. Inventory-risk and replenishment interpretation

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

## 12. Responsible decision support

Dewmi's component will consume forecast and inventory-risk/replenishment outputs and should communicate:

- what the model predicts;
- inventory/risk interpretation;
- forecast uncertainty;
- evidence used by the rule/model;
- assumptions and limitations;
- management considerations;
- whether human review is required.

The framework supports decisions; it does not automatically execute replenishment actions.

## 13. End-to-end framework

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

## 14. Threats to validity

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
