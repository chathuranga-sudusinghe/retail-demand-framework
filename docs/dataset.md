# Dataset Contract

## 1. Source dataset

**Dataset:** UCI Machine Learning Repository — Online Retail  
**Type:** Historical transactional retail data  
**Repository rule:** The dataset file itself is not committed to GitHub.

Local raw data should be placed under:

```text
data/raw/
```

## 2. Source columns

| Column | Role |
|---|---|
| `InvoiceNo` | Invoice / transaction identifier |
| `StockCode` | Product identifier |
| `Description` | Product description |
| `Quantity` | Units recorded on the invoice line |
| `InvoiceDate` | Transaction date and time |
| `UnitPrice` | Unit price |
| `CustomerID` | Customer identifier |
| `Country` | Customer / transaction country |

## 3. Forecasting target

`Quantity` is the raw demand-related source variable.

The model should not normally predict an arbitrary individual invoice-line quantity. The intended forecasting target is an aggregated demand series, for example:

```text
weekly_product_demand
= sum(Quantity)
grouped by StockCode and week
```

The final aggregation frequency must be justified.

## 4. Time variable

`InvoiceDate` is the source of temporal ordering.

Derived calendar variables may include:

- date;
- day of week;
- week;
- month;
- quarter;
- hour if justified.

Seasonality is **not** directly stored in the dataset. It must be detected or modelled from repeated temporal demand patterns.

## 5. Shared cleaning principles

Cleaning decisions must be documented before model training.

The shared pipeline should explicitly address:

- cancelled invoices;
- returns;
- negative quantities;
- zero quantities if present;
- non-positive prices;
- missing descriptions;
- missing customer identifiers;
- duplicate or suspicious transaction lines;
- inconsistent product descriptions;
- temporal ordering;
- product coverage and minimum-history rules.

No member should create a conflicting private cleaning rule for the same shared source without documenting the reason.

## 6. Returns and cancellations

Negative quantities and cancellation-style transactions may represent returns or reversed transactions rather than ordinary demand.

They must not be silently converted to positive sales or dropped without a documented analytical decision.

The project may need separate concepts such as:

```text
gross demand
returns / cancellations
net demand
```

The selected target definition must be consistent across the group.

## 7. Shared processed dataset

The shared processed layer should provide reproducible fields needed by downstream components, such as:

- product identifier;
- period start/end;
- aggregated demand;
- relevant price aggregates where justified;
- calendar fields;
- availability/history flags;
- optional return/cancellation summaries.

## 8. Member-specific derived datasets

All members use the same source and shared cleaning baseline, but they may derive different analytical tables.

### Chathuranga
Needs:
- regular demand series;
- temporal/calendar features;
- lag features;
- rolling features;
- model-ready train/validation/test data.

### Didilani
Needs:
- historical demand behaviour;
- trend;
- volatility;
- intermittency;
- forecast outputs;
- forecast error/bias/uncertainty;
- risk-analysis features.

### Dewmi
Needs:
- forecasts;
- risk outputs;
- uncertainty;
- explanatory/model metadata;
- segment-level results for transparency, robustness, or limitation analysis.

## 9. Data leakage rule

No feature used to predict period `t` may contain information that would only be known after period `t`.

This includes careless rolling calculations, target-based aggregates, and random splitting.

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

## 11. Critical limitation

This dataset does not provide complete observed inventory state such as:

- on-hand stock;
- reorder point;
- safety stock;
- replenishment orders;
- supplier lead time.

Therefore, the project must avoid presenting a derived score as a directly observed stockout or overstock event unless supported by additional data.
