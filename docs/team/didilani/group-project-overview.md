# Didilani — COMP1884 Group Project Contribution

## Member details

**Name:** Didilani Prasadika Weerawickrama Pathinayaka  
**Student ID:** 001560460

## Role

**Inventory-Risk Analytics, Visual Analytics, and Business Interpretation**

## Purpose in the group system

This component translates demand behaviour and forecast outputs into interpretable inventory-risk indicators and managerial visualisations.

## Component research question

**How can historical demand behaviour and forecasting outputs be transformed into meaningful indicators of stockout pressure, overstock pressure, slow-moving demand, and stable demand?**

## Working hypothesis

### H0
Demand variability, intermittency, trend, and forecast error are not significantly associated with the resulting inventory-risk proxy classifications.

### H1
Demand variability, intermittency, trend, and forecast error are significantly associated with different inventory-risk proxy classifications.

The variables, risk definitions, and statistical test must be operationalised before this hypothesis is locked.

## Inputs

- historical aggregated demand;
- temporal demand characteristics;
- forecasts;
- forecast error;
- forecast bias;
- uncertainty where available;
- product identifiers.

## Responsibilities

1. Define inventory-risk proxy concepts with explicit assumptions.
2. Analyse demand volatility and intermittency.
3. Analyse rising/falling/stable demand behaviour.
4. Consume forecast outputs from the forecasting component.
5. Develop a defensible risk-scoring, segmentation, classification, or rules-based method.
6. Investigate threshold sensitivity.
7. Create visual analytics that explain the risk outputs.
8. Translate analytical results into business interpretation.
9. Avoid claiming observed inventory states not present in the data.
10. Produce outputs usable by the responsible decision-support component.

## Candidate outputs

```text
StockCode
period
demand_level
trend_indicator
volatility_indicator
intermittency_indicator
forecast_error
forecast_bias
risk_proxy
risk_score / confidence, if justified
supporting_explanation
```

## Important boundary

The source dataset does not contain actual on-hand inventory. Therefore:

- "stockout risk" means a defensible risk proxy/pressure signal;
- "overstock risk" means a defensible risk proxy/pressure signal;
- derived labels must not be presented as observed historical stockout/overstock events.

## Definition of done

- risk definitions are documented;
- features are reproducibly derived;
- mapping logic/model is implemented;
- thresholds/assumptions are justified;
- visual outputs are understandable;
- sensitivity/limitations are reported;
- outputs can be consumed by the decision-support layer.

## Scope boundary

This is not a dashboard-only contribution. The visual layer communicates a substantive inventory-risk analytical method.
