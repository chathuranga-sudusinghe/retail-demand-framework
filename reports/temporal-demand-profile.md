# Temporal Demand and Inventory-Alignment Profiling

> **Historical EDA provenance — notice added 2026-09-29:** The descriptive results and original methodology wording below are preserved from the earlier research stage; they do not define the current feature set, horizons or experiment authority. References to 1/7/14-day horizons, an unselected lag set or an untouched holdout are historical. The current [frozen feature contract](../docs/forecasting-feature-engineering.md) and [methodology/provenance record](../docs/forecasting-methodology-revision.md) govern forecasting. Final evaluation is December 3–30, 2024, origin December 2, reserved from subsequent selection/fitting but not fully unseen historically: December 3–16 had prior validation exposure and full-year EDA inspected the interval. No results were regenerated or tests/experiments executed for this notice.

**Issue:** #16  
**Branch:** `research/temporal-demand-profile`  
**Status:** Evidence baseline for analytical-unit decision

## 1. Purpose

This profiling stage evaluates the candidate forecasting analytical units before any forecasting model is trained.

The analysis is aligned with the dataset contract and literature review. It focuses on whether the forecasting unit preserves enough temporal evidence for forecasting while remaining compatible with the downstream inventory-risk and replenishment component.

Candidate units:

- SKU-day;
- SKU-warehouse-day;
- SKU-week.

## 2. Verified source constraints

The local dataset contains:

- 91,250 rows;
- 365 observed dates from 2024-01-01 to 2024-12-30;
- 50 SKUs;
- 5 warehouses;
- 91,250 unique `Date + SKU_ID + Warehouse_ID` keys;
- no duplicated rows at that native key;
- `Stockout_Flag` has one unique value and 0 positive rows;
- `Order_Quantity > 0` occurs in 5,027 rows;
- source `Demand_Forecast` is present but is excluded from this profiling and from project forecasting features unless separately justified later.

The native data grain is therefore one record per:

```text
Date + SKU_ID + Warehouse_ID
```

## 3. Candidate analytical-unit comparison

| Analytical unit | Series | Rows | Median observations / series | Median zero-demand share | Median CV | Median lag-1 autocorrelation | Median temporal completeness | Median mean demand |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SKU-day | 50 | 18,250 | 365 | 0.0000 | 0.382685 | 0.898458 | 1.0000 | 100.230137 |
| SKU-warehouse-day | 250 | 91,250 | 365 | 0.005479 | 0.452184 | 0.640139 | 1.0000 | 20.068493 |
| SKU-week | 50 | 2,650 | 53 | 0.0000 | 0.389664 | 0.934990 | 1.0000 | 690.264151 |

### Interpretation

All three candidate units are temporally complete in the profiled dataset.

SKU-day provides 365 observations per SKU and strong short-lag dependence, but it aggregates across warehouses.

SKU-warehouse-day preserves the full native operational grain. It also provides 365 observations per series, so retaining warehouse-level detail does not shorten the individual time series. The median zero-demand share remains very low (approximately 0.55%), although demand is somewhat more variable than at SKU-day level.

SKU-week has only 53 observations per series. It produces a smoother and highly autocorrelated series but substantially reduces the number of time points available for model training and evaluation.

## 4. Inventory alignment across warehouses

Every SKU-day contains all five warehouses:

| Warehouses per SKU-day | SKU-day groups | Share |
|---:|---:|---:|
| 5 | 18,250 | 1.0000 |

The inventory variables show the following cross-warehouse behaviour within the same SKU-day:

| Variable | SKU-day groups | Groups with cross-warehouse variation | Variation share |
|---|---:|---:|---:|
| Inventory_Level | 18,250 | 18,250 | 1.000000 |
| Reorder_Point | 18,250 | 18,250 | 1.000000 |
| Supplier_Lead_Time_Days | 18,250 | 18,250 | 1.000000 |
| Order_Quantity | 18,250 | 4,440 | 0.243288 |

The three core inventory-state variables therefore differ across warehouses for **every SKU-day**.

This is important because a SKU-day demand forecast aggregated across warehouses cannot be mapped directly to one warehouse-specific `Inventory_Level`, `Reorder_Point`, or `Supplier_Lead_Time_Days` without introducing an additional allocation or aggregation rule.

## 5. Promotion alignment

At SKU-day level:

- 18,250 SKU-day groups were examined;
- 7,596 groups contain conflicting `Promotion_Flag` values across warehouses;
- conflict share = 0.416219.

Therefore, a single SKU-day `Promotion_Flag` cannot be carried forward without defining an explicit aggregation rule. Retaining the warehouse dimension avoids discarding this variation.

No causal promotion effect is claimed at this stage.

## 6. Inventory variable ranges

| Variable | Min | Median | Mean | Max | Zero share |
|---|---:|---:|---:|---:|---:|
| Inventory_Level | 168 | 461 | 471.522312 | 990 | 0.000000 |
| Reorder_Point | 201 | 300 | 300.068000 | 398 | 0.000000 |
| Supplier_Lead_Time_Days | 2 | 8 | 7.984000 | 14 | 0.000000 |
| Order_Quantity | 0 | 0 | 19.272493 | 499 | 0.944910 |

The high zero share of `Order_Quantity` confirms that it is sparse and should not be treated as an ordinary dense target without additional methodological justification.

## 7. Analytical-unit recommendation

The profiling evidence supports **SKU-warehouse-day** as the primary forecasting analytical unit.

### Reasons

1. It matches the verified native data grain.
2. It retains 365 observations per series, so warehouse-level forecasting does not reduce the temporal length of each series.
3. The median zero-demand share remains very low.
4. `Inventory_Level`, `Reorder_Point`, and `Supplier_Lead_Time_Days` vary across warehouses in every SKU-day.
5. Aggregating to SKU-day would therefore discard operational information required by the downstream inventory-risk component or force an additional allocation rule not present in the dataset.
6. `Promotion_Flag` also conflicts across warehouses in approximately 41.6% of SKU-days.
7. SKU-week leaves only 53 observations per series, which is less suitable as the primary modelling level given the one-year dataset.

## 8. Methodological boundary

The recommendation above determines only the **primary analytical unit**.

It does **not** yet determine:

- final forecasting models;
- lag structure;
- rolling features;
- promotion feature usage;
- train/validation/test cut points;
- forecast metrics;
- uncertainty method;
- inventory-risk formula;
- replenishment thresholds or quantities.

These remain separate evidence-based decisions.

## 9. Limitations

- the dataset is simulated;
- only approximately one year of data is available;
- strong long-cycle seasonal claims are not supported;
- lag-1 autocorrelation is descriptive and does not establish model suitability;
- promotion differences are descriptive and do not establish causal effects;
- `Stockout_Flag` cannot validate actual stockout prediction;
- sparse `Order_Quantity` limits direct replenishment-target modelling.

## 10. Conclusion

The profiling stage provides sufficient evidence to formalise the primary forecasting analytical unit as:

```text
SKU_ID + Warehouse_ID + Date
```

This preserves the temporal demand series and the warehouse-specific operational context needed for the integrated forecasting -> inventory-risk -> responsible decision-support framework.
