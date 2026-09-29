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

## 3. Source-column data dictionary

The table below explains each source field in plain language so that a reader can understand the dataset without inferring meaning from the column name alone.

| Column | Observed dtype | Plain-language definition | Project use / caution |
|---|---|---|---|
| `Date` | text/date | Calendar date for the recorded observation. | Defines temporal order. Forecasting and validation must preserve this order. |
| `SKU_ID` | text | Identifier for the product / stock-keeping unit (SKU). | Categorical forecasting context predictor and product-level series key under the frozen feature contract. |
| `Warehouse_ID` | text | Identifier for the warehouse in which the observation is recorded. | Categorical forecasting context predictor and series key; preserves warehouse-specific downstream alignment. |
| `Supplier_ID` | text | Identifier for the supplier associated with the recorded product / supply relationship. | May support descriptive analysis or downstream operational interpretation. It is not automatically a forecasting feature. |
| `Region` | text | Geographic region associated with the operational record. | May support descriptive segmentation. It is not automatically included in the forecasting model. |
| `Units_Sold` | integer | Number of units sold for the given SKU, warehouse, and date. | **Primary forecasting target / demand source.** At the selected analytical grain, the model aims to predict future `Units_Sold` for each SKU-warehouse series. |
| `Inventory_Level` | integer | Simulated quantity of stock available on hand for the given warehouse record. | Core downstream variable for inventory-risk analysis. It should not be assumed to be known at a future prediction point unless timing is explicitly defined. |
| `Supplier_Lead_Time_Days` | integer | Simulated number of days expected between placing a replenishment order and receiving supply from the supplier. | Core downstream variable because longer lead time increases exposure to demand while waiting for replenishment. |
| `Reorder_Point` | integer | Simulated inventory threshold at which replenishment should be considered under the source inventory policy. | Used as inventory-policy evidence in the downstream risk / replenishment component. It is not itself a stockout label. |
| `Order_Quantity` | integer | Simulated quantity ordered for replenishment on the recorded row. A value of 0 indicates no recorded replenishment quantity for that row. | Sparse: non-zero in 5,027 of 91,250 rows. It must not be treated as a normal dense target without additional justification. |
| `Unit_Cost` | decimal | Simulated cost to the business for one unit of the product. | Potentially useful for later business interpretation or cost-aware analysis, but no cost-optimisation claim is made unless a method is explicitly defined. |
| `Unit_Price` | decimal | Simulated selling price of one unit of the product. | Potentially useful for descriptive or business interpretation. It is not automatically a forecasting feature. |
| `Promotion_Flag` | integer/binary | Indicator showing whether a promotion is active for the recorded SKU-warehouse-date observation. | Excluded from the frozen forecasting predictor set. Descriptive promotion analysis remains useful; warehouse-level states can differ within the same SKU-day. Any later predictor use requires separate approval and availability review. |
| `Stockout_Flag` | integer/binary | Indicator intended to represent whether a stockout occurred. | **Not usable as a target or validation label in this dataset** because it is 0 for all 91,250 rows. Stockout / shortage pressure must be derived from other evidence. |
| `Demand_Forecast` | decimal | Demand forecast supplied by the dataset creator / simulation. | **Not the project's forecasting target.** It is leakage-sensitive and must not be used as an ordinary model feature. It may only be considered later as a separately documented benchmark if methodologically justified. |

Schema, row count, date coverage, missingness, cardinalities, and key field behaviour above have been verified from the downloaded CSV.

### 3.1 Frozen forecasting roles

The [authoritative feature contract](forecasting-feature-engineering.md) distinguishes raw-data roles from model inputs:

- **KEEP as categorical predictors:** `SKU_ID`, `Warehouse_ID`.
- **Construction/alignment/target only:** `Date`, `Units_Sold`.
- **EXCLUDE from forecasting predictors:** `Supplier_ID`, `Region`, `Inventory_Level`, `Supplier_Lead_Time_Days`, `Reorder_Point`, `Order_Quantity`, `Unit_Cost`, `Unit_Price`, `Promotion_Flag`, `Stockout_Flag`, `Demand_Forecast`.

Exclusion does not make these fields useless to the project. Origin-aligned inventory, reorder point, lead time and order activity may support downstream analysis under its separately approved methods; other fields may support descriptive/business interpretation. The zero-variance stockout field remains a limitation, and source forecasts require separate leakage-safe benchmark approval.

All learned models use two categorical context and twelve engineered predictors (fourteen conceptual predictors), with complete 28-day history. Ridge/Random Forest encode those as 67 columns; LightGBM uses 14 inputs. The forecast target is next-day demand or direct cumulative 7/14/28-day demand from one fixed origin.

### 3.2 Primary modelling identifiers and target

Following DR-002, the primary forecasting analytical unit is:

```text
Date + SKU_ID + Warehouse_ID
```

The target at that grain is:

```text
target = Units_Sold
```

In practical terms, the forecasting component asks:

> For a given SKU in a given warehouse, how many units are expected to be sold in a future date / forecast period?

This distinction is important because `Demand_Forecast` is a source-provided value, while `Units_Sold` is the observed demand variable that the project uses to train and evaluate its own forecasting models.

## 4. Forecasting target

The forecasting component uses `Units_Sold` as the observed demand target.

DR-002 selected **SKU-warehouse-day** as the primary analytical unit after temporal-demand and inventory-alignment profiling.

Therefore, the primary modelling grain is:

```text
SKU_ID + Warehouse_ID + Date
```

and the target is:

```text
Demand(SKU_ID, Warehouse_ID, Date) = Units_Sold
```

The verified source data already contains one unique row per `Date + SKU_ID + Warehouse_ID`, so no additional demand aggregation is required for the primary forecasting view.

SKU-day and SKU-week views may still be used for descriptive analysis, visualisation, or sensitivity checks, but they are not the primary modelling grain.

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
Warehouse_ID
period
demand
```

where `period` represents the date / forecast period and `demand` is derived from `Units_Sold` at the selected SKU-warehouse-day grain.

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
- the exact frozen categorical/calendar/lag/rolling/slope contract;
- complete 28-day origin-available demand histories;
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
