# Inventory-Risk and Replenishment Analysis Workflow

## Owner

Primary COMP1884 owner: **Didilani**

## Goal

Translate Chathuranga's demand forecast into transparent inventory-risk and replenishment information using the inventory variables available in the selected dataset.

## Workflow

```text
Forecast demand
        +
Inventory level
        +
Reorder point
        +
Supplier lead time
        +
Replenishment / order quantity
        +
Forecast uncertainty, where available
        |
        v
Inventory-risk and replenishment features
        |
        v
Rules / scoring / justified analytical method
        |
        v
Risk level + replenishment recommendation
        |
        v
Visual analytics and business interpretation
```

## Candidate evidence

- forecast demand;
- inventory level;
- gap between inventory and forecast demand;
- reorder point;
- supplier lead time;
- recent/available order quantity;
- forecast error or uncertainty;
- the known limitation that `Stockout_Flag` is constant and cannot serve as a target/label.

## Candidate outputs

- replenishment alert;
- stockout-pressure / shortage risk;
- overstock / excess-inventory pressure;
- low/medium/high risk level;
- recommended replenishment quantity where justified;
- explanation of the rule/evidence producing the result.

## Replenishment logic

The exact formula must be defined and evaluated before implementation is final.

A simplified conceptual form is:

```text
forecast demand
+ inventory policy / lead-time requirement
- usable inventory position
= replenishment need
```

The actual implementation must match the dataset definitions and avoid inventing unavailable operational variables.

## Verified dataset constraints

- `Stockout_Flag = 0` for all 91,250 rows. It must not be used to train or validate a stockout classifier.
- `Order_Quantity > 0` occurs in 5,027 rows, while 86,223 rows have zero order quantity. Replenishment modelling must account for this sparsity.
- Any stockout-pressure indicator must therefore be a derived decision-support measure based on forecast demand and available inventory-policy variables, not a learned replica of `Stockout_Flag`.

## Critical limitation

The dataset is simulated. Its inventory fields provide a useful controlled environment for testing the framework, but the resulting rules/recommendations are not automatically validated for a real company.

## Evaluation

Potential evaluation approaches include:

- comparison with simulated reorder/replenishment behaviour;
- threshold sensitivity;
- risk consistency across time;
- performance around low-inventory/reorder-point conditions;
- scenario analysis;
- downstream interpretability.

The selected approach must match the final method.
