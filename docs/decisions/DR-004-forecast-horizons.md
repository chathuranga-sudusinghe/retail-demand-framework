# DR-004 — Forecast Horizons for Decision Support

**Date:** 2026-09-22  
**Status:** Accepted for the current forecasting-methodology baseline  
**Owner:** Chathuranga  
**Related issue:** #28

## Context

DR-002 fixed the primary forecasting analytical unit as daily SKU-warehouse demand:

```text
SKU_ID + Warehouse_ID + Date
```

The analytical grain defines the level of each prediction, but it does not define how far into the future the project should forecast.

The project's downstream inventory-risk and replenishment component requires demand information over operationally meaningful planning windows, not only a single next-day value.

Periodic-review inventory literature treats replenishment as a process in which inventory is reviewed at defined intervals, and review-period decisions interact with demand, supply variability, and lead time (Silver and Robb, 2008; Lee and Schwarz, 2009).

The verified project dataset contains `Supplier_Lead_Time_Days` values from 2 to 14 days.

## Decision

The forecasting component will evaluate the following horizons:

- **1 day** — immediate next-day SKU-warehouse demand;
- **7 days** — cumulative demand over the next 7 days;
- **14 days** — cumulative demand over the next 14 days.

These are project-specific decision-support horizons. They must not be presented as universal replenishment frequencies for all retailers.

## Analytical grain versus forecast horizon

These concepts are intentionally separate:

```text
analytical grain
= SKU_ID + Warehouse_ID + Date

forecast horizon
= 1 day / 7 days / 14 days ahead
```

The model therefore retains daily SKU-warehouse forecasts. A 7-day or 14-day demand view can be created from the sequence of daily forecasts while preserving warehouse identity.

## Rationale

- **1 day** supports immediate operational visibility.
- **7 days** provides a weekly planning view.
- **14 days** provides a two-week view aligned with the upper end of the dataset's observed supplier lead-time range.
- Periodic-review inventory research supports using explicit review/planning intervals and considering lead time when connecting forecasts to replenishment decisions.

The literature supports the general importance of review intervals and lead time; it does **not** establish that 7 or 14 days are universally optimal. The exact horizons are therefore a project-specific methodological choice informed jointly by literature and the verified dataset.

## Feature-engineering relationship

Forecast horizon and rolling-feature window are different:

- a **rolling window** summarises historical demand used as model input;
- a **forecast horizon** defines how far into the future the target is predicted.

For example, a model may use a 7-day rolling mean as an input while producing forecasts for 1, 7, and 14 days ahead.

All features used for each horizon must remain leakage-safe and must be based only on information available at the prediction origin.

## Still open

This decision does not finalise:

- recursive versus direct multi-step forecasting;
- exact lag set;
- exact model set;
- exact train/validation/test dates;
- final metric set;
- horizon-specific model-selection rules;
- uncertainty method.

## References

- Silver, E.A. and Robb, D.J. (2008) 'Some insights regarding the optimal reorder period in periodic review inventory systems', *International Journal of Production Economics*, 112(1), pp. 354-366. https://doi.org/10.1016/j.ijpe.2007.03.014
- Lee, J.-Y. and Schwarz, L.B. (2009) 'Leadtime management in a periodic-review inventory system: A state-dependent base-stock policy', *European Journal of Operational Research*, 199(1), pp. 122-129. https://doi.org/10.1016/j.ejor.2008.10.024
