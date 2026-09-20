# Research Design

## 1. Purpose

This document defines the current research-design baseline for the COMP1884 group project. Hypotheses are treated as testable statements and will only be finalised when their variables and evaluation methods are operationally defined.

## 2. Main research question

**How can data-driven demand forecasting be used to identify inventory risks and support supply-chain decision-making in retail operations?**

## 3. Analytical unit

The raw dataset is invoice-line transactional data. Forecasting requires conversion into a regular time series.

Candidate analytical units include:

- product-day demand;
- product-week demand;
- category-day demand, if a defensible category representation is developed;
- category-week demand.

The first implementation decision will be whether daily or weekly product demand provides the best balance between temporal detail, sparsity, and the approximately one-year dataset horizon.

## 4. Target variable

Raw source variable:

```text
Quantity
```

Forecasting target:

```text
Demand(product, period) = sum(Quantity)
```

for each selected product and time period after agreed cleaning and transaction-handling rules.

## 5. Temporal characteristics to investigate

The project should examine:

- trend;
- seasonality;
- autocorrelation / lag dependence;
- volatility;
- intermittency / zero-demand periods;
- changes in demand level;
- product-to-product heterogeneity.

Seasonality is not a source column. It is a temporal property inferred from demand series created from `InvoiceDate` and `Quantity`.

## 6. Candidate feature families

### Calendar features
- day of week;
- week of year;
- month;
- quarter;
- potentially hour, if intraday forecasting becomes relevant.

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
- rolling minimum / maximum where useful;
- recent growth or decline indicators.

All rolling and lag features must be generated without future-data leakage.

## 7. Forecasting approach

The group forecasting component should compare appropriate levels of complexity, for example:

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

Where feasible, use rolling-origin or walk-forward evaluation to test forecasting stability across time.

## 9. Forecasting metrics

Candidate metrics include:

### Mean Absolute Error (MAE)

```text
MAE = (1 / n) * sum(|p_i - y_i|)
```

Primary candidate because it is easy to interpret in demand units.

### Root Mean Squared Error (RMSE)

```text
RMSE = sqrt((1 / n) * sum((p_i - y_i)^2))
```

Provides stronger penalty for large errors.

### Weighted Absolute Percentage Error (WAPE)

```text
WAPE = sum(|p_i - y_i|) / sum(|y_i|)
```

Useful as a scale-normalised aggregate measure when the denominator is meaningful.

### Mean Absolute Percentage Error (MAPE)

MAPE is part of the original proposal but must be used carefully because zero or near-zero actual demand can make it unstable or undefined.

### Forecast Bias / Mean Forecast Error

Using the project convention:

```text
Bias = (1 / n) * sum(p_i - y_i)
```

Interpretation:

- positive bias -> systematic overforecasting;
- negative bias -> systematic underforecasting;
- near zero -> little net directional error.

Bias is diagnostic and should not replace an absolute-error metric.

## 10. Group-level hypothesis direction

A strong testable time-series hypothesis direction is:

### H0
Forecasting performance does not significantly vary across different temporal demand behaviours.

### H1
Forecasting performance varies significantly across different temporal demand behaviours, and different forecasting approaches show different suitability across demand regimes.

Potential regimes include:

- stable;
- seasonal;
- volatile;
- intermittent;
- low-volume.

This hypothesis will only be locked after the regime definitions, model comparison design, and statistical test are defined.

## 11. Inventory-risk interpretation

Risk analysis may use combinations of:

- forecast demand level;
- recent demand trend;
- demand volatility;
- intermittency;
- forecast error;
- forecast bias;
- forecast uncertainty.

Because true inventory state is absent, outputs must initially be described as **inventory-risk proxies**, not observed stockout/overstock events.

## 12. Responsible decision support

The system should communicate:

- what the model predicts;
- how uncertain the prediction is;
- what evidence contributes to the risk interpretation;
- what limitations apply;
- that final operational judgement remains with a human decision-maker.

## 13. Threats to validity

Important threats include:

- approximately one year of data limits long-cycle seasonal inference;
- missing customer identifiers;
- cancellations/returns and negative quantities;
- no direct inventory-level fields;
- product heterogeneity;
- sparse/intermittent demand;
- changes in assortment over time;
- possible abnormal purchasing periods;
- evaluation sensitivity to aggregation frequency.

These limitations must be considered in method selection and conclusions.
