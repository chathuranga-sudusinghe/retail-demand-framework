# DR-004 — Forecast Horizons for Decision Support

> **Current status cross-reference — Issue #94:** [The frozen protocol](../protocol.md) resolves prior pending supportive settings, baseline and runtime decisions. Issue #89 was merged through PR #90. [Runner operations](../forecasting-runner.md) distinguish approved storage policy from unchanged runtime behavior. Original decision/development wording below remains historical provenance; this status note changes no decision or authorizes any run.

> **Documentation alignment — 2026-09-29:** The project owner has approved the current 1/7/14/28-day forecasting design and [frozen feature contract](../forecasting-feature-engineering.md). This record's original date and decision history remain intact. Proposed 28-day baseline formulas, the executable protocol and downstream methods retain separate approval boundaries; experiment execution is NOT authorised. See [current approval and provenance](../forecasting-methodology-revision.md).

**Original decision date:** 2026-09-22
**Original decision status:** Accepted for the 1/7/14-day forecasting-methodology baseline
**Revision date:** 2026-09-28
**Revision status:** Current forecasting design human-approved; separate execution/implementation gates remain
**Documentation alignment:** 2026-09-29, on the project owner's explicit instruction
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

The original September 22 decision covered 1/7/14 days. The current owner-approved design adds 28 days:

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

The accepted September 22 decision approved only 1/7/14 days. On September 28, human review selected an extension to 28 days for four-week / approximately monthly planning, not an exact calendar month. The current forecasting design is human-approved; this does not approve the executable protocol, experiments or downstream methods. Verified supplier lead times remain 2–14 days and do not alone justify 28 days. Historical windows and forecast horizons remain different concepts; the separate frozen feature contract explicitly approves complete 7/14/28-day mean/std summaries.

The [final feature contract](../forecasting-feature-engineering.md) is frozen for feature/preprocessing implementation. Proposed 28-day baseline definitions require separate human approval. Downstream 28-day inventory-risk use requires component-owner/human approval; no human-review rule is approved here. Uncertainty methodology remains open. The direct forecasting strategy is unchanged.

## Original open items and subsequent decisions

At the original September 22 horizon decision, the following items were not finalised. DR-005 records the approved revised validation details; DR-006 defines the metrics, [DR-013](DR-013-matched-gradient-boosting-comparison.md) supersedes DR-007/009 learned-model roles, and DR-008 defines the direct strategy. The feature contract is frozen; proposed 28-day baseline formulas and uncertainty retain separate approval requirements. This list is retained as original decision provenance:

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
