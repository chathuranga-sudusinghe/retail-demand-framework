# DR-004 — Forecast Horizons for Decision Support

> **Horizon revision — 2026-09-28:** [Revision and provenance](../forecasting-methodology-revision.md) records the human-selected revised 1/7/14/28-day forecasting direction currently under repository-wide human review. The added 28-day horizon represents four-week / approximately monthly planning. See [DR-005](DR-005-forecast-validation-design.md) for validation-window details. No separate supervisor approval or new experiment result is claimed.

**Original decision date:** 2026-09-22
**Original decision status:** Accepted for the 1/7/14-day forecasting-methodology baseline
**Revision date:** 2026-09-28
**Revision status:** Under human review
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

The original accepted decision covered 1-, 7- and 14-day horizons. The human-selected revised direction adds 28 days; the following revised set remains under repository-wide human review:

- **1 day** — immediate next-day SKU-warehouse demand;
- **7 days** — cumulative demand over the next 7 days;
- **14 days** — cumulative demand over the next 14 days;
- **28 days** — cumulative demand over the next four weeks / approximately monthly planning (not an exact calendar month).

These are project-specific decision-support horizons. They must not be presented as universal replenishment frequencies for all retailers.

## Analytical grain versus forecast horizon

These concepts are intentionally separate:

```text
analytical grain
= SKU_ID + Warehouse_ID + Date

forecast horizon
= 1 day / 7 days / 14 days / 28 days ahead
```

The analytical grain remains daily SKU–warehouse. The 7-, 14- and 28-day outputs are direct cumulative targets from the same fixed origin under DR-008 and do not imply a daily forecast path.

## Rationale

- **1 day** supports immediate operational visibility.
- **7 days** provides a weekly planning view.
- **14 days** provides a two-week view aligned with the upper end of the dataset's observed supplier lead-time range.
- **28 days** adds the human-selected four-week / approximately monthly planning view; it is not justified by supplier lead time alone.
- Periodic-review inventory research supports using explicit review/planning intervals and considering lead time when connecting forecasts to replenishment decisions.

The literature supports the general importance of review intervals and lead time; it does **not** establish that 7, 14, or 28 days are universally optimal. All selected horizons are project-specific methodological choices informed by planning needs, the verified dataset, relevant inventory literature, and human review; the literature does not establish that 28 days is optimal.

## Feature-engineering relationship

Forecast horizon and rolling-feature window are different:

- a **rolling window** summarises historical demand used as model input;
- a **forecast horizon** defines how far into the future the target is predicted.

For example, a model may use a 7-day rolling mean as an input while producing forecasts for 1, 7, 14, and 28 days ahead.

All features used for each horizon must remain leakage-safe and must be based only on information available at the prediction origin.

## Revision rationale and provenance

The accepted September 22 decision approved only 1/7/14 days. On September 28, human review selected an extension to 28 days for four-week / approximately monthly planning, not an exact calendar month. This revision remains under repository-wide human review and does not imply final acceptance of the entire revised methodology. Verified supplier lead times remain 2–14 days and do not alone justify 28 days. Historical feature windows do not automatically change.

Final feature freeze remains pending. Proposed 28-day baseline definitions require separate human approval. Downstream 28-day inventory-risk use requires component-owner/human approval; no human-review rule is approved here. Uncertainty methodology remains open. The direct forecasting strategy is unchanged.

## Original open items and subsequent decisions

At the original September 22 horizon decision, the following items were not finalised. DR-005 records the revised validation details under human review; DR-006 defines the metrics, DR-007/009 the model families and DR-008 the direct strategy. Final feature freeze, proposed 28-day baselines and uncertainty remain open. This list is retained as original decision provenance:

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
