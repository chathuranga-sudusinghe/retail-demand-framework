# Dataset Contract

## 1. Selected source dataset

**Dataset:** High-Dimensional Supply Chain Inventory Dataset  
**Publisher:** Ziya on Kaggle  
**Source:** https://www.kaggle.com/datasets/ziya07/high-dimensional-supply-chain-inventory-dataset  
**Type:** Simulated daily SKU-level supply-chain and inventory data  
**Dataset size:** 91,250 records and 15 source columns (verified from the downloaded CSV)  
**Time coverage:** 2024-01-01 to 2024-12-30 (365 dates)  
**Repository rule:** The dataset file itself is not committed to GitHub.

Local raw data should be placed under:

```text
data/raw/
```

The dataset change from UCI Online Retail is recorded in:

```text
docs/decisions/DR-001-dataset-selection.md
```

## 2. Verified dataset profile

The downloaded CSV was profiled before implementation. Verified characteristics:

- 91,250 rows;
- 15 columns;
- 365 dates from 2024-01-01 to 2024-12-30;
- 50 unique SKUs;
- 5 warehouses;
- 10 suppliers;
- 4 regions;
- no missing values in the 15 source columns;
- `Stockout_Flag` is constant at 0 for all 91,250 rows;
- `Order_Quantity` is 0 in 86,223 rows and greater than 0 in 5,027 rows.

The constant `Stockout_Flag` means it cannot be used as a meaningful stockout classification target or validation label. The relatively sparse non-zero `Order_Quantity` values must be profiled carefully before defining replenishment logic.

## 3. Source columns

| Column | Observed dtype | Project role |
|---|---|---|
| `Date` | text/date | Temporal ordering |
| `SKU_ID` | text | Product identifier |
| `Warehouse_ID` | text | Warehouse identifier |
| `Supplier_ID` | text | Supplier identifier |
| `Region` | text | Regional dimension |
| `Units_Sold` | integer | Historical sales / primary demand source |
| `Inventory_Level` | integer | Simulated on-hand inventory level |
| `Supplier_Lead_Time_Days` | integer | Simulated supplier lead time |
| `Reorder_Point` | integer | Inventory-policy threshold |
| `Order_Quantity` | integer | Simulated replenishment quantity; non-zero in 5,027 rows |
| `Unit_Cost` | decimal | Unit cost |
| `Unit_Price` | decimal | Selling price |
| `Promotion_Flag` | integer/binary | Promotion indicator |
| `Stockout_Flag` | integer/binary | Constant 0 in the downloaded CSV; not usable as a target/label |
| `Demand_Forecast` | decimal | Source-provided planning forecast; not the project's forecasting target |

Schema, row count, date coverage, missingness, cardinalities, and key field behaviour above have been verified from the downloaded CSV. Additional distribution and temporal checks will still be performed in the reproducible data-profiling pipeline.

## 4. Forecasting target

The forecasting component will use `Units_Sold` to construct a regular time series.

Candidate target:

```text
Demand(SKU, period) = sum(Units_Sold)
```

The final aggregation level may be SKU-day, SKU-warehouse-day, or another justified regular unit.

### Important leakage rule for `Demand_Forecast`

The dataset already contains a source-generated `Demand_Forecast` field. The group project must build its own forecasting models.

Therefore:

- do not use `Demand_Forecast` as the target for Chathuranga's model;
- do not automatically use it as a model feature;
- do not let it leak future/target information into training;
- it may only be used as a separately documented benchmark after the project's own evaluation design is fixed.

## 5. Inventory-analysis variables

Didilani's component can directly use inventory-related fields that were missing from the original UCI dataset, including:

```text
Inventory_Level
Reorder_Point
Supplier_Lead_Time_Days
Order_Quantity
```

These variables allow inventory-risk and replenishment analysis to be grounded in the simulated operating state instead of inventing a complete hypothetical inventory system.

`Stockout_Flag` exists in the schema but is constant at 0 in the downloaded CSV, so it must not be treated as an observed stockout target or validation label. Stockout-pressure/risk must instead be derived from defensible relationships among forecast demand, inventory state, reorder point, lead time, and replenishment behaviour.

Any derived risk level or recommended replenishment quantity must still have a documented formula/rule and evaluation method.

## 6. Shared data-quality checks

Before model training, the shared pipeline must explicitly check:

- schema and datatypes;
- missing values;
- duplicate rows;
- date continuity and ordering;
- invalid/negative quantities where applicable;
- SKU/warehouse/supplier identifier consistency;
- impossible inventory or price values;
- zero-variance or near-zero-variance fields;
- distribution and range of `Units_Sold`;
- relationship between `Inventory_Level`, `Reorder_Point`, and `Order_Quantity`;
- confirm `Stockout_Flag` remains zero-variance and exclude it from predictive/validation use;
- possible leakage from source-generated fields.

No member should create a conflicting private cleaning rule without documenting the reason.

## 7. Shared processed dataset

The shared processed layer should provide reproducible fields needed by downstream components.

At minimum, the forecasting view should provide:

```text
SKU_ID
period
demand
```

Inventory-analysis views may additionally include:

```text
Warehouse_ID
Supplier_ID
Region
Inventory_Level
Reorder_Point
Supplier_Lead_Time_Days
Order_Quantity
Stockout_Flag
```

plus forecast outputs from Chathuranga's component.

## 8. Member-specific derived datasets

### Chathuranga

Needs:

- regular demand series from `Units_Sold`;
- temporal/calendar features;
- leakage-safe lag/rolling features where used;
- model-ready chronological train/validation/test data;
- model predictions and errors.

### Didilani

Needs:

- Chathuranga's forecast outputs;
- inventory levels;
- reorder points;
- supplier lead times;
- replenishment/order quantities;
- the documented zero-variance limitation of `Stockout_Flag`;
- forecast uncertainty/error fields where available;
- derived risk/replenishment features.

### Dewmi

Needs:

- forecasts;
- inventory-risk/replenishment outputs;
- uncertainty;
- explanatory metadata;
- assumptions and limitations;
- human-review conditions.

## 9. Data leakage rule

No feature used to predict period `t` may contain information that would only be known after the prediction origin.

Particular care is required with:

- source `Demand_Forecast`;
- rolling statistics;
- inventory states recorded after sales for a period;
- replenishment information that may occur after the prediction origin;
- random train/test splitting.

## 10. Local-data rule

The following remain local and are ignored by Git:

```text
data/raw/*
data/processed/*
*.xlsx
*.xls
*.csv
*.parquet
```

Only documentation, code, schemas, tests, and small non-sensitive fixtures should be version controlled.

## 11. Dataset limitation

The selected dataset is **simulated**. It is useful because it provides the connected sales and inventory variables required by the framework, but it is not direct evidence from a real operating company.

Results must therefore be described as evaluation within the simulated supply-chain environment, not proof of real-company operational performance.
