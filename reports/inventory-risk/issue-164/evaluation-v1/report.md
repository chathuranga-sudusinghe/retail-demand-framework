# Inventory reorder-threshold exposure evaluation

Snapshot policy: **constructed-origin**.

Constructed no-receipt scenario: take the recorded Inventory_Level and Reorder_Point on 2024-12-02 as hypothetical starting balances immediately before the 2024-12-03 target window. Hold Reorder_Point fixed; model no receipts, transfers, returns, losses or other adjustments. This is not verified source timing or a reconstruction of realised inventory.

## Population and counts

| Horizon | Paired N | TP | TN | FP | FN | Source-known at/below | Scenario at/below | Unavailable |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 7 | 239 | 54 | 168 | 0 | 17 | 0 | 11 | 0 |
| 1 | 239 | 5 | 230 | 0 | 4 | 0 | 11 | 0 |
| 14 | 239 | 121 | 78 | 0 | 40 | 0 | 11 | 0 |

## Horizon-specific proxy metrics

| Horizon | Metric | Value | Denominator | Status |
|---|---|---:|---:|---|
| 7 | event_prevalence | 0.2971 | 239 | available |
| 7 | missed_crossing_rate | 0.2394 | 71 | available |
| 7 | false_alert_rate | 0.0000 | 168 | available |
| 7 | agreement | 0.9289 | 239 | available |
| 7 | precision | 1.0000 | 54 | available |
| 7 | recall | 0.7606 | 71 | available |
| 7 | balanced_accuracy | 0.8803 | positive=71; negative=168 | available |
| 1 | event_prevalence | 0.0377 | 239 | available |
| 1 | missed_crossing_rate | 0.4444 | 9 | available |
| 1 | false_alert_rate | 0.0000 | 230 | available |
| 1 | agreement | 0.9833 | 239 | available |
| 1 | precision | 1.0000 | 5 | available |
| 1 | recall | 0.5556 | 9 | available |
| 1 | balanced_accuracy | 0.7778 | positive=9; negative=230 | available |
| 14 | event_prevalence | 0.6736 | 239 | available |
| 14 | missed_crossing_rate | 0.2484 | 161 | available |
| 14 | false_alert_rate | 0.0000 | 78 | available |
| 14 | agreement | 0.8326 | 239 | available |
| 14 | precision | 1.0000 | 121 | available |
| 14 | recall | 0.7516 | 161 | available |
| 14 | balanced_accuracy | 0.8758 | positive=161; negative=78 | available |

## Interpretation and limitations

These results compare a fixed-origin, fixed-reorder-point, no-receipt scenario with a constructed retrospective demand proxy. They do not establish actual stockout accuracy, optimal orders, real-retailer effectiveness or managerial benefit.

Already-at/below-threshold cases are excluded from paired forecast-skill comparisons. Missing targets and invalid forecasts remain unavailable. Undefined denominators remain null, not zero. Horizons are separate; 28-day inventory evaluation is excluded.

The Kaggle dataset is publisher-simulated and Stockout_Flag has zero variance. Order_Quantity is not treated as receipts. Numerical replenishment, overstock, uncertainty and managerial review rules remain unavailable.

The final interval has December 3–16 prior validation exposure and full-year exploratory exposure. This conditional secondary analysis does not change frozen forecasting producers or replay their final evaluation.

Use prospective.json for downstream records. Evaluation-only observations, confusion cells and metrics remain in evaluation.json.

Forecast export SHA-256: `c823f1bc7e44ee41f75a56545e2ccc26e2a6662366f593a669f990f3b856b863`.
