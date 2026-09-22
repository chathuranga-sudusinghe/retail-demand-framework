# Literature Review

**Project:** A Data-Driven Decision Support Framework for Retail Demand Forecasting and Inventory Risk Analysis  
**Module:** COMP1884 Group Project, MSc Data Science, University of Greenwich  
**Status:** Working literature-review baseline for group review  
**Last updated:** 2026-09-22

## 1. Purpose and scope

This literature review establishes the academic basis for the COMP1884 group project. It is deliberately aligned with the project's verified dataset, research questions, and integrated architecture:

```text
historical demand
    -> demand forecasting
    -> inventory-risk / replenishment analysis
    -> responsible management-facing decision support
```

The review is not intended to justify a pre-selected model. Instead, it identifies evidence that can guide methodological decisions. Since this baseline review was created, dataset profiling and DR-002 have fixed the primary analytical unit as SKU-warehouse-day. The exact model set, inventory-risk formula, replenishment logic, uncertainty treatment, and human-review rules remain open and must be operationally justified before they are fixed.

The review concentrates on five connected areas:

1. retail and SKU-level demand forecasting;
2. forecast evaluation and time-aware validation;
3. promotion-aware forecasting and forecast uncertainty;
4. the interface between forecasting, inventory control, and replenishment;
5. explainable and human-centred decision support in supply-chain settings.

This is a **structured narrative review**, not a claimed systematic literature review. Peer-reviewed journal literature was prioritised, with emphasis on recent work and selected foundational studies where they remain methodologically important. Papers were retained when they materially support the research design and when their assumptions can be related to variables actually available in the selected dataset.

## 2. Dataset-informed boundary of the review

The selected High-Dimensional Supply Chain Inventory Dataset contains daily simulated supply-chain records for 2024, including `Units_Sold`, `Inventory_Level`, `Supplier_Lead_Time_Days`, `Reorder_Point`, `Order_Quantity`, `Promotion_Flag`, identifiers for SKU/warehouse/supplier/region, cost and price variables, and a source-generated `Demand_Forecast`.

These characteristics constrain what the literature can legitimately support in this project.

- `Units_Sold` is the project's historical demand source.
- `Promotion_Flag` makes promotion-aware forecasting literature potentially relevant, provided the promotion state would be known at the prediction origin.
- `Inventory_Level`, `Reorder_Point`, `Supplier_Lead_Time_Days`, and `Order_Quantity` provide a basis for downstream inventory-risk and replenishment analysis.
- `Stockout_Flag` is constant at 0 in all 91,250 records and therefore cannot support supervised stockout classification or serve as stockout validation ground truth.
- `Order_Quantity` is sparse, with relatively few non-zero order events, which limits direct modelling of replenishment quantities as an ordinary target.
- the source `Demand_Forecast` must not be used in a way that leaks future or target information into the project's own forecasting models.
- only approximately one year of observations is available, so strong claims about long-cycle or multi-year seasonality would not be defensible.
- because the dataset is simulated, conclusions must describe performance within the simulated environment rather than claim proven effectiveness in a real retailer.

These constraints mean that literature on stockout classification, rich customer-level demand, weather-driven retail demand, or multi-year seasonal modelling may provide background context but cannot automatically define the project's main method.

## 3. Retail demand forecasting

Retail forecasting differs from generic time-series prediction because decisions are often required at relatively fine product and location levels, while demand is affected by promotions, aggregation, heterogeneity, intermittency, and changing business conditions. Fildes, Ma and Kolassa (2022) review retail forecasting research and show that product-level forecasts are closely connected to operational decisions. They also emphasise that promotional information can substantially increase forecasting complexity. This is directly relevant to the present dataset because demand is represented at SKU level and a binary `Promotion_Flag` is available.

The same authors' post-script highlights the increasing importance of machine-learning approaches and structural instability in retail forecasting (Fildes, Kolassa and Ma, 2022). For this project, the implication is not that machine learning should automatically replace statistical methods. Rather, the literature supports comparing methods of different complexity and assessing them under a common time-aware evaluation design.

Nasseri et al. (2023) compare tree-based ensembles with LSTM-based deep learning for retail demand prediction using more than six years of daily demand for over 330 products. Their work demonstrates that both modern ensemble learning and sequence-based deep learning can be evaluated in a retail context, but their much longer real-world history differs materially from the present project's one-year simulated dataset. Consequently, this paper supports the relevance of comparing model families, but does **not** by itself justify using an LSTM or any other deep architecture in this project.

Feizabadi (2022) connects machine-learning-based demand forecasting to wider supply-chain performance and argues that forecasting should be considered in relation to operational outcomes rather than only statistical accuracy. This perspective is especially important to the COMP1884 architecture, where the forecast is explicitly an upstream input to inventory-risk and replenishment analysis.

Recent work also reinforces the importance of promotions. Hewage, Perera and Bandara (2026) examine demand behaviour across the promotional life cycle and compare traditional and contemporary forecasting approaches. Their results show that promotions can generate demand volatility extending beyond the promotion period. The current dataset does not contain the rich promotional descriptors used in many retail studies, but its `Promotion_Flag` can still justify testing whether known promotion status adds useful, leakage-safe explanatory information.

### Implication for this project

The retail forecasting literature supports the following research direction without yet fixing an exact model set:

```text
simple benchmark
    vs
statistical forecasting
    vs
regression / machine-learning forecasting
```

Model complexity should be justified by out-of-sample evidence, data volume, temporal behaviour, interpretability, and downstream usefulness. A complex model should not be selected merely because it is technically more advanced.

## 4. Time-aware validation and forecast evaluation

Forecasting differs from ordinary i.i.d. prediction because temporal order is part of the information structure. Tashman (2000) shows that out-of-sample evaluation design involves choices such as rolling versus fixed origins, updating, test periods, and rolling versus fixed windows. Bergmeir and Benítez (2012) likewise discuss why ordinary cross-validation assumptions can be problematic for dependent time-series data and evaluate alternatives for time-series predictor assessment.

These studies support the project's existing decision to avoid random train/test splitting for the main forecasting evaluation. A chronological design in which earlier observations train the model and later observations evaluate it is more consistent with the actual forecasting task. Where data volume permits, rolling-origin or walk-forward evaluation can provide evidence across several prediction origins rather than relying on a single split.

Forecast-error metrics also require care. Hyndman and Koehler (2006) demonstrate that commonly used percentage-based measures can behave poorly in some situations and propose scaled-error approaches for comparison across series. For the current project, this is relevant because multiple SKUs may have different demand levels and some periods may contain low or zero demand. It therefore supports the repository's cautious treatment of MAPE and the use of complementary metrics such as MAE, RMSE, WAPE, bias, and potentially a scaled error measure where appropriate.

No single metric should automatically determine the selected forecasting method. RMSE gives greater weight to large errors, MAE is easier to interpret in the target's units, WAPE can provide an aggregate relative measure where the denominator is well behaved, and forecast bias can reveal systematic over- or under-forecasting. The final metric set should match the observed demand distributions and downstream decision needs.

### Implication for this project

The literature supports:

- preserving temporal order;
- using future holdout data not seen during training;
- considering rolling-origin evaluation where feasible;
- comparing models against a simple benchmark;
- reporting multiple complementary error measures rather than relying on a single score;
- examining systematic forecast bias because under-forecasting and over-forecasting can have different inventory consequences.

## 5. Forecast uncertainty and operational relevance

A central issue in this project is that a point forecast alone does not express the uncertainty faced by an inventory decision-maker. This is particularly important because downstream replenishment risk depends not only on expected demand but also on how wrong the forecast may be.

Theodorou, Spiliotis and Assimakopoulos (2025) investigate the relationship between forecast accuracy and inventory performance using M5 competition data. Their results show that better statistical forecast accuracy does not always translate directly into better inventory outcomes; the relationship also depends on demand characteristics, inventory-policy settings, review periods, lead times, and cost structures. This is a critical finding for the present research because it discourages treating the forecast model with the smallest error as automatically the best decision-support model.

Feizabadi (2022) similarly treats forecasting as part of a wider supply-chain performance problem. Taken together, these studies support the project's integrated research question: the meaningful question is not only "Which method predicts demand most accurately?" but also "How can the forecast be translated into useful inventory-risk information?"

The present dataset does not contain all variables necessary for a complete real-world cost optimisation model. Therefore, this project should not claim to optimise total inventory cost unless the required cost and operational assumptions are explicitly defined and justified. Instead, forecast error, bias, and where feasible prediction intervals or another defensible uncertainty representation can be passed downstream as evidence for inventory-risk and human-review logic.

## 6. Forecasting and inventory-control integration

The strongest literature support for the overall COMP1884 architecture comes from work examining the forecasting-inventory interface.

Goltsos et al. (2022) identify a substantial separation between forecasting and inventory-control research. Forecasting studies often treat the forecast as the endpoint, whereas inventory models frequently assume demand information is already known. Their review argues for stronger integration between these stages. This directly motivates the present project's architecture, where forecasting is not an isolated task but an input to subsequent inventory-risk and replenishment analysis.

Bergsma, de Ruijt and Bhulai (2025) systematically review 122 studies applying machine learning within inventory-control optimisation. They distinguish between approaches in which forecasting and optimisation remain separate, approaches that embed machine learning into static optimisation, and dynamic approaches such as reinforcement learning. Their review is useful for positioning the current MSc project: given the available variables, one-year horizon, sparse order events, and absence of usable stockout labels, the project is better framed as a transparent **forecast-to-inventory decision-support pipeline** than as a claim to solve a full dynamic inventory-control optimisation problem.

Theodorou et al. (2025) further show why the downstream inventory stage matters: forecast ranking can change once inventory objectives and policies are considered. Therefore, the forecasting component should expose enough information for downstream analysis, such as point forecasts, forecast errors, model identifier, and uncertainty where feasible.

### Inventory-risk implications of the available features

The literature does not justify inventing operational variables that do not exist in the dataset. The current inventory-risk component should therefore concentrate on evidence that is available or defensibly derived from:

```text
forecast demand
+ current inventory level
+ reorder point
+ supplier lead time
+ observed order quantity
+ forecast error / uncertainty
```

Because `Stockout_Flag` has no positive examples, the project cannot empirically learn or validate a stockout classifier from this dataset. A more defensible output is therefore a **stockout-pressure**, **shortage-risk**, **overstock-pressure**, or **replenishment-risk** indicator derived from documented relationships among forecast demand and inventory-state variables.

The exact formula, threshold levels, and replenishment quantity rule remain open research decisions. Literature can inform them, but the final implementation must also be tested against the empirical ranges and relationships in this specific dataset.

## 7. Responsible and explainable decision support

Forecasting and replenishment outputs become useful to managers only when their meaning, evidence, assumptions, and uncertainty are communicated appropriately. This motivates the third component of the group project.

Kosasih et al. (2024) review explainable AI in supply-chain management and identify limited explainability as a barrier to broader use of AI-based supply-chain systems. Olan et al. (2024) similarly examine explainable-AI capabilities in supply-chain decision support and emphasise the role of explanation in informed decision-making.

Reis et al. (2025) provide particularly relevant evidence because their decision-support system selects explanation methods according to stakeholder needs and includes a human-in-the-loop. Their system was evaluated in a real supply-chain demand context with end users. The study supports an important design principle for this project: explanation should be adapted to the actual decision context rather than added as a purely technical afterthought.

For the current framework, responsible decision support does not require an autonomous agent or automatic ordering system. The repository already defines a more defensible boundary: the system should present the forecast, inventory-risk interpretation, uncertainty, evidence, assumptions, and limitations, then preserve managerial review for consequential or uncertain cases.

### Implication for this project

The downstream decision-support layer should aim to make visible:

- the forecast and relevant period/SKU;
- the inventory evidence supporting the risk assessment;
- forecast error or uncertainty where available;
- the reason for any replenishment recommendation;
- important assumptions and dataset limitations;
- conditions that warrant explicit human review.

Claims such as "improved trust", "improved interpretability", or "better decision quality" should only be made if the project defines and evaluates measurable criteria for those concepts.

## 8. Critical synthesis and provisional research gap

The literature reveals three connected issues.

First, retail-demand forecasting research provides many statistical, machine-learning, and deep-learning alternatives, but method suitability depends on the data, forecasting level, promotions, temporal behaviour, and evaluation design (Fildes, Ma and Kolassa, 2022; Nasseri et al., 2023; Hewage, Perera and Bandara, 2026). This argues against assuming that one model family is universally superior.

Second, forecasting and inventory control are still frequently evaluated as separate problems. Goltsos et al. (2022) explicitly identify this separation, while Theodorou et al. (2025) show that forecast accuracy and inventory performance are related but not interchangeable. Bergsma, de Ruijt and Bhulai (2025) demonstrate that the integration of machine learning and inventory control is developing through multiple methodological approaches.

Third, recent supply-chain decision-support research increasingly recognises that explanation and stakeholder involvement matter when analytical outputs are used for business decisions (Kosasih et al., 2024; Olan et al., 2024; Reis et al., 2025).

On this basis, the provisional research gap for COMP1884 is not that demand forecasting, inventory control, or explainable decision support are individually new. The opportunity is at their **application-level integration** under the constraints of the selected dataset:

> There is scope to evaluate how SKU-warehouse-level demand forecasts can be transformed, using available warehouse-specific inventory-state and lead-time information, into transparent inventory-risk and replenishment evidence, and then communicated through a responsible management-facing decision-support layer that retains uncertainty and human oversight.

This is an MSc-level applied contribution rather than a claim of new forecasting theory. The contribution will need to be demonstrated through the reproducible integration and evaluation of the three components.

## 9. Alignment with the project research questions

### RQ1 — What demand patterns can be identified from historical SKU-level sales data?

Supported by literature on retail-demand heterogeneity, temporal behaviour, promotion effects, and SKU-level forecasting. Temporal and inventory-alignment profiling has now been completed, and DR-002 selects SKU-warehouse-day as the primary analytical unit. Lag structure and any demand-regime definitions remain open.

### RQ2 — Which forecasting methods are suitable for predicting future product demand?

Supported by comparative retail-forecasting, validation, and forecast-accuracy literature. Suitability must be determined through time-aware out-of-sample evidence rather than complexity alone.

### RQ3 — How can forecasting outputs and inventory-state variables be combined to identify stockout, overstock, and replenishment risks?

Supported by integrated forecasting-inventory literature. Because `Stockout_Flag` is unusable as a target, this RQ should be answered through defensible derived risk/pressure measures rather than supervised stockout classification.

### RQ4 — How can uncertainty, transparency, governance, and human oversight guide the responsible use of the resulting decision-support outputs?

Supported by XAI and human-centred decision-support literature. The project should expose evidence, uncertainty, assumptions, limitations, and human-review conditions without presenting recommendations as automatic managerial actions.

## 10. Methodological decisions: resolved and still open

### Resolved after literature review and dataset profiling

- **Primary analytical unit:** SKU-warehouse-day, recorded in DR-002.
- **Primary forecasting target:** `Units_Sold` at `SKU_ID + Warehouse_ID + Date` grain.
- **Stockout label limitation:** `Stockout_Flag` is zero-variance and cannot support supervised stockout classification or validation.

### Still open

- exact forecasting model set;
- exact lag and rolling-window definitions;
- whether and how `Promotion_Flag` is used;
- exact train/validation/test dates and rolling-origin design;
- final metric set;
- demand-regime definitions and statistical tests;
- uncertainty representation;
- inventory-risk / shortage-pressure / overstock formulas and thresholds;
- use of sparse `Order_Quantity` in validation or rule construction;
- replenishment-quantity formula;
- human-review rules and evaluation criteria;
- whether the source `Demand_Forecast` is used later as a separately documented benchmark.

These remaining items should be converted into explicit decision records only after literature evidence and reproducible dataset evidence are considered together.

## 11. References

Bergmeir, C. and Benítez, J.M. (2012) 'On the use of cross-validation for time series predictor evaluation', *Information Sciences*, 191, pp. 192-213. https://doi.org/10.1016/j.ins.2011.12.028

Bergsma, R., de Ruijt, C. and Bhulai, S. (2025) 'A systematic review of machine learning approaches in inventory control optimization', *Operations Research Perspectives*, 15, 100367. https://doi.org/10.1016/j.orp.2025.100367

Feizabadi, J. (2022) 'Machine learning demand forecasting and supply chain performance', *International Journal of Logistics Research and Applications*, 25(2), pp. 119-142. https://doi.org/10.1080/13675567.2020.1803246

Fildes, R., Kolassa, S. and Ma, S. (2022) 'Post-script—Retail forecasting: Research and practice', *International Journal of Forecasting*, 38(4), pp. 1319-1324. https://doi.org/10.1016/j.ijforecast.2021.09.012

Fildes, R., Ma, S. and Kolassa, S. (2022) 'Retail forecasting: Research and practice', *International Journal of Forecasting*, 38(4), pp. 1283-1318. https://doi.org/10.1016/j.ijforecast.2019.06.004

Goltsos, T.E., Syntetos, A.A., Glock, C.H. and Ioannou, G. (2022) 'Inventory–forecasting: Mind the gap', *European Journal of Operational Research*, 299(2), pp. 397-419. https://doi.org/10.1016/j.ejor.2021.07.040

Hewage, H.C., Perera, H.N. and Bandara, K. (2026) 'Enhancing Demand Forecasting in Retail: A Comprehensive Analysis of Sales Promotional Effects on the Entire Demand Life Cycle', *Journal of Forecasting*, 45(1), pp. 293-315. https://doi.org/10.1002/for.70039

Hyndman, R.J. and Koehler, A.B. (2006) 'Another look at measures of forecast accuracy', *International Journal of Forecasting*, 22(4), pp. 679-688. https://doi.org/10.1016/j.ijforecast.2006.03.001

Kosasih, E.E., Papadakis, E., Baryannis, G. and Brintrup, A. (2024) 'A review of explainable artificial intelligence in supply chain management using neurosymbolic approaches', *International Journal of Production Research*, 62(4), pp. 1510-1540. https://doi.org/10.1080/00207543.2023.2281663

Nasseri, M., Falatouri, T., Brandtner, P. and Darbanian, F. (2023) 'Applying Machine Learning in Retail Demand Prediction—A Comparison of Tree-Based Ensembles and Long Short-Term Memory-Based Deep Learning', *Applied Sciences*, 13(19), 11112. https://doi.org/10.3390/app131911112

Olan, F., Spanaki, K., Ahmed, W. and Zhao, G. (2024) 'Enabling explainable artificial intelligence capabilities in supply chain decision support making', *Production Planning & Control*. https://doi.org/10.1080/09537287.2024.2313514

Reis, M.I., Gonçalves, J.N.C., Cortez, P., Carvalho, M.S. and Fernandes, J.M. (2025) 'A context-aware decision support system for selecting explainable artificial intelligence methods in business organizations', *Computers in Industry*, 165, 104233. https://doi.org/10.1016/j.compind.2024.104233

Tashman, L.J. (2000) 'Out-of-sample tests of forecasting accuracy: an analysis and review', *International Journal of Forecasting*, 16(4), pp. 437-450. https://doi.org/10.1016/S0169-2070(00)00065-0

Theodorou, E., Spiliotis, E. and Assimakopoulos, V. (2025) 'Forecast accuracy and inventory performance: Insights on their relationship from the M5 competition data', *European Journal of Operational Research*, 322(2), pp. 414-426. https://doi.org/10.1016/j.ejor.2024.12.033

---

## Review note

This file is a working research artifact for COMP1884. The first data-profiling stage and analytical-unit decision are now complete; the review should continue to be refined as later methodology decisions are made. References should be re-checked against the final University-required reference style before inclusion in the submitted report.
