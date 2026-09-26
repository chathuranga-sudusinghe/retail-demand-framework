# Inventory-Risk and Replenishment Methodology — Research Brief

**Status:** Working research brief for team review; not an approved methodology decision.
**Owner:** Didilani
**Related work:** Issue #22; [inventory-risk workflow](../workflows/inventory-risk-analysis.md); [dataset contract](../dataset.md); [research design](../research-design.md); [project boundaries](../project-boundaries.md).

This document addresses Issue #22's methodology-first requirement before inventory-risk or replenishment logic is implemented. It separates repository-approved facts from literature-informed candidates and questions still requiring a team decision. It does not approve a risk formula, threshold, category, or ordering rule.

## 1. Problem definition

**Documented evidence:** The component is intended to take Chathuranga's demand forecasts and warehouse-specific inventory information and turn them into transparent inventory-risk and replenishment decision support. Its research question is how demand forecasts and inventory-state variables can be combined to identify inventory risk and support replenishment decisions. It does not forecast demand a second time. The group research framing includes shortage/stockout pressure, excess-stock pressure, and replenishment risk, while keeping management responsible for decisions ([Didilani's overview](../team/didilani/group-project-overview.md); [project overview](../project-overview.md)).

**Documented limitation:** `Stockout_Flag` is zero for all 91,250 verified rows. It cannot provide a positive/negative ground-truth label or validate a stockout classifier. Any future output must be described as derived pressure/risk evidence, not an observed stockout prediction validated against that field ([dataset contract](../dataset.md); [DR-001](../decisions/DR-001-dataset-selection.md)).

**Still unresolved:** The operational definitions of shortage pressure, excess-stock pressure, and replenishment risk; the forecast/inventory timing contract; the output evaluation target; and whether the final output will use continuous indicators, alerts, categories, or some combination.

## 2. Literature evidence

The repository's literature review and accepted forecast-horizon decision provide a starting point, not a preselected inventory policy:

| Evidence | What it supports | What it does not decide for this project |
|---|---|---|
| Silver and Robb (2008) examine how periodic-review reorder-period choices interact with demand and supply parameters. | Review interval and uncertainty matter to inventory policy; a planning period should be justified in context. | No universal review period, project threshold, or formula. The paper notes that cost behaviour can be complex, so its results do not justify an arbitrary fixed period. |
| Lee and Schwarz (2009) study a periodic-review system with stochastic lead times and a state-dependent base-stock policy. | Lead time and current inventory state can interact in replenishment decisions. | Their policy depends on a specified model and assumptions; it is not directly transferable as a rule for this dataset. |
| Goltsos et al. (2022), *Inventory–forecasting: Mind the gap*, review the separation between forecasting and inventory-control research. | Forecast outputs should be considered in relation to inventory outcomes, rather than treating forecast accuracy as the only objective. | It does not provide this project with a validated label or directly determine its inventory formula. |
| Theodorou et al. (2025) study the relationship between forecast accuracy and inventory performance using M5 competition data. | Forecast accuracy and downstream inventory performance are related research concerns and should be examined together. | Results on another dataset do not validate this project's simulated inventory rules or thresholds. |

The first two sources are already cited in [DR-004](../decisions/DR-004-forecast-horizons.md). The latter two are included in the repository's [literature review](../literature/literature-review.md) and [reference register](../references.md). Publisher/DOI records: [Silver and Robb (2008)](https://doi.org/10.1016/j.ijpe.2007.03.014), [Lee and Schwarz (2009)](https://doi.org/10.1016/j.ejor.2008.10.024), [Goltsos et al. (2022)](https://doi.org/10.1016/j.ejor.2021.07.040), and [Theodorou et al. (2025)](https://doi.org/10.1016/j.ejor.2024.12.033).

**Suggested, not approved:** These sources make a transparent, lead-time-aware connection between forecast evidence and inventory state a defensible area to investigate. They do not establish that any one candidate method is best for this project. The final choice must account for the observed dataset, its timing, and what can actually be evaluated.

## 3. Dataset-variable mapping

The selected source is simulated daily supply-chain data. The verified profile is 91,250 rows, 15 columns, 50 SKUs, five warehouses, and dates from 2024-01-01 through 2024-12-30. Its native record key is `Date + SKU_ID + Warehouse_ID` ([dataset contract](../dataset.md); [DR-002](../decisions/DR-002-forecasting-analytical-unit.md)).

| Variable | Documented meaning / potential role | Status or caution |
|---|---|---|
| `Date`, `SKU_ID`, `Warehouse_ID` | Identify the daily SKU-warehouse record and preserve the join grain. | **Approved grain** under DR-002. A forecast join must preserve warehouse identity. |
| Chathuranga's forecast output | Future demand evidence at the forecast origin and SKU-warehouse grain. Approved project horizons are next-day demand and cumulative demand over the next 7 and 14 days. | **Forecasting decisions approved** in DR-004 and DR-008; the cross-component schema and exact period-date alignment remain open in the shared-data workflow. |
| `Inventory_Level` | Simulated stock on hand for the recorded warehouse observation. | Candidate inventory-state input. Do not assume a future value is available at the forecast origin. |
| `Reorder_Point` | Simulated policy threshold at which replenishment should be considered. | Candidate policy evidence; not a stockout label and not yet a project risk threshold. |
| `Supplier_Lead_Time_Days` | Simulated expected days between ordering and receipt; verified range is 2–14 days. | Candidate supply-exposure evidence. How this range maps to the 1/7/14-day forecast views is not approved. |
| `Order_Quantity` | Recorded replenishment quantity; non-zero in 5,027 of 91,250 records. | Sparse historical activity. Its meaning relative to forecast origin and whether it is on-order, placed, or received inventory is not defined sufficiently for direct target use. |
| `Units_Sold` | Historical observed demand; the approved forecasting target. | Use as demand history through the forecasting output contract, not as a future known value. |
| `Demand_Forecast` | Dataset creator/simulation-provided reference forecast. | **Not** Chathuranga's model output or a required input to Didilani's component. Any benchmark use would need separate justification and leakage review. |
| `Stockout_Flag` | Source field intended to indicate stockout. | Constant zero in the verified data; retain only as a documented limitation, not as ground truth or a validation label. |

The forecasting component's currently approved horizon targets are direct horizon-specific predictions: one-day next-day demand, seven-day cumulative demand, and fourteen-day cumulative demand ([DR-004](../decisions/DR-004-forecast-horizons.md); [DR-008](../decisions/DR-008-multi-step-forecasting-strategy.md)). The cumulative outputs do not supply a daily path within those windows. The final forecast-to-inventory schema, origin date convention, and inventory snapshot timing are still to be agreed ([shared-data workflow](../workflows/shared-data-foundation.md)).

## 4. Candidate inventory-risk / replenishment methods

The inventory workflow explicitly lists candidate evidence: forecast demand, inventory level, an inventory/forecast gap, reorder point, supplier lead time, recent/available order quantity, and forecast error or uncertainty where available. It also lists rule-based, scoring, or another justified analytical method as possibilities. These are **candidates**, not approved definitions ([inventory-risk workflow](../workflows/inventory-risk-analysis.md)).

### Candidate method families

1. **Reorder-point comparison:** Examine recorded `Inventory_Level` in relation to the dataset's `Reorder_Point` as policy context. The repository's evidence layer may describe this relationship, but the comparison has not been approved as a complete risk definition or as a future-time decision rule.
2. **Forecast-horizon and lead-time alignment:** Investigate whether approved 1-, 7-, or 14-day cumulative forecast evidence is appropriate for the observed 2–14-day supplier lead-time context. DR-004 motivates those horizons but does not specify an alignment rule or make each horizon equivalent to a replenishment review period.
3. **Transparent rule or score:** A shortage/excess indicator, score, or risk category could be considered if its definition is justified, temporally aligned, and sensitivity-tested. The repository has not approved its formula, categories, or cut points.
4. **Replenishment analysis:** The workflow records this simplified conceptual relationship: “forecast demand + inventory policy / lead-time requirement - usable inventory position = replenishment need.” The same workflow says the exact formula must be defined and evaluated and must match the dataset definitions. This is a conceptual prompt only, not an executable formula or an approved calculation.
5. **Historical replenishment comparison:** Compare a future candidate method with simulated reorder/replenishment behaviour, as listed among possible evaluation approaches. Sparse `Order_Quantity` and unresolved event timing limit what such a comparison could establish.

**Suggested but not approved:** Start methodology comparison with transparent evidence tied to the existing inventory policy (`Inventory_Level` and `Reorder_Point`) and test whether forecast-horizon/lead-time information adds useful evidence. Compare candidate rules or scores only after their timing and evaluation basis are specified. This sequence is a proposal for team review, not a project decision.

**Not supported as a current method:** A cost-optimal inventory policy cannot be claimed from the dataset documentation alone. The repository notes that the data do not define a complete real-company inventory system and warns against total-cost optimisation claims without the necessary cost and operational assumptions ([literature review](../literature/literature-review.md)).

## 5. Assumptions

No new operational assumptions are adopted by this brief.

| Item | Status | Why it matters |
|---|---|---|
| Dataset records are simulated daily SKU-warehouse observations. | **Documented fact.** | Conclusions describe this dataset and do not establish real-retailer performance. |
| Inventory fields represent the recorded observation; availability at a future forecast origin is not guaranteed. | **Documented caution.** | Inventory state must be joined to a defined origin, not silently taken from a future date. |
| `Order_Quantity` is a sparse recorded quantity. | **Documented fact; event semantics unresolved.** | It cannot be assumed to mean received stock or known outstanding orders. |
| A selected forecast window represents the stock-planning exposure interval. | **Unresolved assumption.** | Needs a team decision using forecast-date semantics and lead-time/review context. |
| The inventory observation used with a forecast is the stock state available at the forecast origin. | **Candidate integration assumption, not approved.** | Must be confirmed in the cross-component timing contract. |
| Historical simulated reorder/order activity is an adequate proxy for good inventory decisions. | **Unresolved and not established by the repository.** | It may support descriptive comparison, but not ground truth without additional evidence. |

## 6. Threshold / sensitivity approach

**Documented requirement:** Thresholds, if used, must be defined, justified, and tested rather than chosen arbitrarily. The component definition of done also calls for threshold justification and sensitivity consideration. The workflow lists threshold sensitivity, time consistency, performance around low-inventory/reorder-point conditions, scenario analysis, and interpretability as possible evaluation approaches ([Didilani's overview](../team/didilani/group-project-overview.md); [inventory-risk workflow](../workflows/inventory-risk-analysis.md)).

**Still unresolved:** Whether this project needs thresholds or categories at all; what operational evidence would justify any cut points; which temporal evaluation window or comparison basis is valid; and what stability constitutes an acceptable result.

**Suggested process, not an approved threshold method:** If the chosen approach requires a threshold, document its rationale before examining final evaluation results, compare more than one defensible setting, and report how outputs change across the selected validation periods or scenarios. Do not infer a “correct” threshold from `Stockout_Flag`, since it has no positive cases. This process does not specify numeric thresholds or a selection formula.

## 7. Limitations

- The dataset is simulated, and results cannot establish real-retailer effectiveness.
- The source has only about one year of daily coverage, limiting evidence about longer seasonal or replenishment cycles.
- `Stockout_Flag` has no variation and cannot validate stockout predictions.
- Non-zero `Order_Quantity` is sparse, and order timing/state semantics need clarification.
- Inventory state must be aligned to the forecast origin; future `Inventory_Level` cannot be presumed available.
- The direct 7-day and 14-day forecast outputs are cumulative quantities and do not provide the daily path inside each interval ([DR-008](../decisions/DR-008-multi-step-forecasting-strategy.md)).
- The project has not finalised the forecast-output schema, inventory-state timing, or inventory-to-decision-support contract ([shared-data workflow](../workflows/shared-data-foundation.md)).
- The source `Demand_Forecast` is creator/simulation-provided, not the project's forecast, and is leakage-sensitive.
- A simulated reorder or order event is not necessarily an optimal-policy label.
- Cost optimisation, service-level claims, or real-world purchasing recommendations would require definitions and evidence not currently established in the repository.

## 8. Recommended methodology direction

**Proposal for team review; not agreed or approved:** Develop a transparent, SKU-warehouse-level inventory-pressure method that retains the approved forecasting grain, uses the selected model's forecast output as its forecast input, and relates that forecast to inventory state/policy and supplier lead-time context only after the timing contract is fixed. Begin by evaluating whether the documented reorder-point relationship provides a defensible baseline; then assess whether approved horizon-specific forecasts add useful shortage/excess evidence. Treat historical order quantities as sparse context rather than ground truth. Make any risk categories or replenishment recommendation conditional on explicit justification, sensitivity analysis, and an evaluation strategy that does not rely on `Stockout_Flag`.

This direction is consistent with the project's stated need for transparent forecast-to-inventory decision support and with research that treats forecasting and inventory performance as connected problems. It does **not** choose the calculation, horizon-to-lead-time mapping, risk labels, thresholds, or replenishment rule. Those remain research decisions for team review and, where needed, a separate accepted decision record before implementation.

### Decisions still needed before implementation

1. Define the forecast origin and how each forecast period maps to the inventory snapshot date.
2. Decide how 1-, 7-, and 14-day forecast outputs relate to supplier lead time and any review interval.
3. Select and justify what shortage pressure and excess-stock pressure mean for this study.
4. Decide whether outputs are continuous evidence, alerts, categories, or a combination; define and sensitivity-test any thresholds only after that choice.
5. Decide whether replenishment quantity is in scope and what dataset fields can support/evaluate it without assuming unknown on-order or receipt semantics.
6. Define an evaluation/comparison strategy given there is no valid stockout label and recorded orders are sparse.
7. Agree the forecast-to-inventory input schema and the output fields required by Dewmi's decision-support component.

## References

- Goltsos, T.E., Syntetos, A.A., Glock, C.H. and Ioannou, G. (2022). “Inventory–forecasting: Mind the gap.” *European Journal of Operational Research*, 299(2), 397–419. https://doi.org/10.1016/j.ejor.2021.07.040
- Lee, J.-Y. and Schwarz, L.B. (2009). “Leadtime management in a periodic-review inventory system: A state-dependent base-stock policy.” *European Journal of Operational Research*, 199(1), 122–129. https://doi.org/10.1016/j.ejor.2008.10.024
- Silver, E.A. and Robb, D.J. (2008). “Some insights regarding the optimal reorder period in periodic review inventory systems.” *International Journal of Production Economics*, 112(1), 354–366. https://doi.org/10.1016/j.ijpe.2007.03.014
- Theodorou, E., Spiliotis, E. and Assimakopoulos, V. (2025). “Forecast accuracy and inventory performance: Insights on their relationship from the M5 competition data.” *European Journal of Operational Research*, 322(2), 414–426. https://doi.org/10.1016/j.ejor.2024.12.033
