# Inventory-Risk and Replenishment Analysis Workflow

## Owner

Primary COMP1884 owner: **Didilani**

## Goal

Translate Chathuranga's demand forecast into **origin reorder-threshold exposure** under the proposed [DR-012](../decisions/DR-012-inventory-risk-replenishment-methodology.md), subject to group approval, with transparent evidence, assumptions and limitations.

## Workflow

```text
Project forecast at a defined origin and horizon
        +
Origin inventory level and reorder point
        |
        v
Origin buffer B_t = I_t - R_t
        |
        v
Three exposure states under the no-receipt scenario
        |
        v
Exposure evidence + margins + assumptions / limitations
        |
        v
Visual interpretation and responsible decision-support handoff
```

## Proposed interpretation

For the same SKU-warehouse, `I_t` and `R_t` are inventory and reorder-point values available at origin `t`; `B_t = I_t - R_t`. Forecast demand covers `t+1` through `t+h`, inclusive.

| Condition | State |
|---|---|
| `B_t <= 0` | Already at/below the origin reorder threshold |
| `B_t > 0` and forecast cumulative demand `>= B_t` | Forecast threshold crossing within the horizon |
| `B_t > 0` and forecast cumulative demand `< B_t` | No forecast threshold crossing within the horizon |

Apply the same rule separately to 1-day, 7-day cumulative and 14-day cumulative forecasts. Equality counts as reaching the threshold. Keep the origin threshold fixed and assume no receipts, transfers, returns, losses or other adjustments. Future inventory values must not be joined as origin inputs. Document snapshot availability and within-day interpretation before integration.

Missing/invalid required evidence produces unavailable/not assessed with a reason, not `FALSE`. DR-012 leaves problematic-forecast handling open and does not approve clipping. Negative arithmetic projected balances are not verified physical negative inventory.

## Context and output boundary

- Retain `SKU_ID`, `Warehouse_ID`, forecast origin, horizon and model provenance.
- Retain origin inventory, reorder point, buffer, exposure state/reason and the conceptual predicted margin `B_t - forecast_demand`.
- Retain origin-available supplier lead time as context only: horizon shorter than, equal to or longer than lead time. Do not round lead time, interpolate a daily path or claim an exact lead-time-demand forecast.
- Retain `Order_Quantity` as contextual recorded activity only after its availability at the forecast origin is established; it is neither receipts nor optimal-policy ground truth.
- Include available approved forecast-error/uncertainty context and the scenario assumptions and limitations.
- Follow DR-011 field groups and unavailable-information semantics; final names, types and interchange format remain open.

## Replenishment and overstock scope

Origin reorder-threshold exposure supplies replenishment-related evidence. Final numerical replenishment quantity and overstock/excess-stock evaluation remain provisional until separately justified and approved. Not reaching the threshold is not evidence of overstock. No low/medium/high risk scale or autonomous order instruction is defined.

## Verified dataset constraints

- `Stockout_Flag = 0` for all 91,250 rows. It must not be used to train or validate a stockout classifier.
- `Order_Quantity > 0` occurs in 5,027 rows, while 86,223 rows have zero order quantity. Replenishment modelling must account for this sparsity.
- Source `Demand_Forecast` is not Chathuranga's project model output.
- The proposed exposure output is a constructed scenario proxy, not actual stockout prediction or actual shortage ground truth.

## Critical limitation

The dataset is simulated. Its inventory fields provide a useful controlled environment for testing the framework, but the resulting rules/recommendations are not automatically validated for a real company.

## Evaluation

Replace forecast demand with realised cumulative `Units_Sold` over the exact same horizon, retaining the origin inventory and threshold. Use `B_t > 0` cases for the primary forecast comparison; report already-at/below-threshold cases separately, together with unavailable evidence and reasons.

Use DR-012's explicitly defined counts, event prevalence, missed-crossing rate, false-alert rate, agreement, precision, recall and balanced accuracy. Report denominators and undefined metrics as unavailable; inspect prevalence before interpretation and do not artificially rebalance the population. Compare the same cases and method across candidates, separately by horizon. No single rate establishes a universally best downstream model.

The retrospective margin is `B_t - realised_demand`. Near-zero predicted or retrospective margins indicate sensitivity, but no numeric tolerance is approved. Retrospective evidence must not enter forecast-time inputs or review triggers.

Subject to group approval, DR-012 would supply the method for later forecast-to-decision evaluation. The A/C/D cross-component protocol, uncertainty method, human-review rules and implementation remain separate work. DR-006 forecasting selection remains WAPE-based.
