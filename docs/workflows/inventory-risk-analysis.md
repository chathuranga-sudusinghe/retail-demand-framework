# Inventory-Risk Analysis Workflow

## Owner

Primary COMP1884 owner: **Didilani**

## Goal

Translate demand behaviour and forecasting evidence into transparent inventory-risk proxies.

## Workflow

```text
Historical demand behaviour
        +
Forecast outputs
        +
Forecast error / bias / uncertainty
        |
        v
Risk features
        |
        v
Risk scoring / segmentation / classification method
        |
        v
Risk proxy
        |
        v
Visual analytics and business interpretation
```

## Candidate evidence

- demand level;
- recent trend;
- volatility;
- intermittency;
- forecast error;
- forecast bias;
- forecast uncertainty.

## Candidate proxy states

- stockout-pressure / high-demand risk;
- overstock-pressure / declining-demand risk;
- slow-moving risk;
- stable-demand state.

Final names and definitions must be justified.

## Critical limitation

No true inventory-on-hand series exists in the source dataset. Risk outputs are analytical proxies unless additional valid inventory data are introduced.

## Evaluation

Potential evaluation approaches:

- stability across time;
- sensitivity to thresholds;
- consistency with observed demand behaviour;
- comparison of alternative risk definitions;
- scenario analysis;
- downstream interpretability.

The selected approach must match the final method.
