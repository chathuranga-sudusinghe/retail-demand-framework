# Forecasting Feature and Preprocessing Contract

This is the final human-reviewed predictor contract. The conceptual membership, definitions and information timing are unchanged. [Protocol](protocol.md) owns experiment design; [DR-013](decisions/DR-013-matched-gradient-boosting-comparison.md) owns the matched primary representation; [DR-014](decisions/DR-014-forecasting-selection-and-final-refit.md) owns final refitting; [final results](forecasting-final-evaluation.md) own performance interpretation.

## 1. Purpose

Predict next-day or cumulative 7/14/28-day demand from the same fixed origin using only information available at that origin. Demand calculations stay within each SKU–warehouse series; pooled learned models do not mix series histories. No feature search, ablation, additional interaction or alternative window is part of the frozen experiment.

## 2. Raw dataset features

The [dataset contract](dataset.md) defines all fifteen fields and their observed profile. Their forecasting roles are:

| Source field(s) | Accepted role / exclusion |
|---|---|
| SKU_ID, Warehouse_ID | Nominal identity predictors and separate alignment keys |
| Date | Chronological alignment and first-target-day calendar construction; not a direct numerical predictor |
| Units_Sold | Historical demand source and future target construction; not an unshifted predictor |
| Supplier_ID, Region | Excluded contextual inputs; identity structure may be redundant with retained keys, and no additional predictive use is frozen |
| Inventory_Level, Reorder_Point, Supplier_Lead_Time_Days, Order_Quantity | Downstream inventory context; same-day availability does not establish origin-time availability or a forecasting feature |
| Promotion_Flag | Excluded: source row values do not supply an origin-time known future promotion plan |
| Unit_Cost, Unit_Price | Excluded contextual/operational inputs; no accepted prediction-time measurement or additional feature policy |
| Demand_Forecast | Source-generated reference only; excluded from normal features and targets to avoid undefined leakage/comparison semantics |
| Stockout_Flag | Constant zero; excluded predictor and invalid stockout target/validation label |

## 3. Final ordered feature contract

### Final model feature vector

Exactly fourteen conceptual predictors, in this order, for every learned model and horizon:

~~~text
SKU_ID
Warehouse_ID
dow_sin
dow_cos
lag_1
lag_7
lag_14
rolling_mean_7
rolling_std_7
rolling_mean_14
rolling_std_14
rolling_mean_28
rolling_std_28
rolling_slope_14
~~~

The two identity predictors encode context; the twelve numerical predictors encode known calendar and past demand. Date and Units_Sold retain construction/target roles only. At an origin the conceptual vector is common across horizons; cumulative labels and eligible training populations differ by horizon.

### Categorical encoding and physical feature counts

All three primary models (XGBoost, LightGBM, CatBoost) and supportive Random Forest use **full one-hot identities followed by the twelve unscaled numerical predictors**. Ridge uses the same identity representation and scales numerical inputs only. No native categorical primary representation is used.

Fit vocabularies on the exact eligible labelled training population for each fold/horizon, retaining all observed levels (drop=None). Sort categories lexically, with SKU indicators before warehouse indicators, then the frozen numerical order. Primary preprocessors share vocabulary, mappings and physical order. With full coverage, 50 SKU + 5 warehouse + 12 numerical inputs gives 67 columns; smaller training coverage gives n_SKU + n_warehouse + 12. Record actual coverage, names, width and population identity. Validation/final origin rows cannot add categories or fit statistics.

Unknown prediction identities **raise an error**. There is no all-zero fallback, future-category discovery or silent population exclusion. Identity indicators remain 0/1. IDs are not continuous measurements; the model intercept is not an additional input column.

For Ridge, fit each numerical column's mean and population standard deviation (ddof=0) on those same eligible training rows, transform as (x - mean) / scale, and use scale=1 for a constant column. This differs from the sample standard deviation (ddof=1) used by rolling features. Preserve fitted state for transformation/replay; do not refit on origin or outcome rows.

## 4. How engineered features are constructed

### Notation and calendar alignment

Let o be the last observed demand day, t=o+1 the first target day, and y_u the same series' Units_Sold on day u. Every historical calculation ends at o. Calendar values describe **t**, including for cumulative horizons; they do not describe a horizon end or average its calendar days.

With Monday=0 through Sunday=6, d(t) is the weekday index:

$$
\mathrm{dow\_sin}=\sin(2\pi d(t)/7),\qquad
\mathrm{dow\_cos}=\cos(2\pi d(t)/7).
$$

These deterministic values are known at the origin and need no learned statistics. Paired cyclic coordinates preserve weekday adjacency; they do not establish that this dataset has a strong weekly seasonal signal. Human-readable weekday labels may be shown downstream but are not additional predictors.

### Lag construction

For k in {1,7,14}:

$$
\mathrm{lag}_k=y_{t-k}=y_{o-k+1}.
$$

Thus lag_1=y_o, lag_7=y_(o-6), lag_14=y_(o-13). lag_7 aligns with the first target weekday, not seven days before the origin. Moving the history boundary into a cumulative target window would leak outcomes.

### Rolling-statistics construction

For w in {7,14,28}, require all w consecutive daily observations ending at o:

$$
M_w(o)=\frac1w\sum_{j=0}^{w-1}y_{o-j},\qquad
S_w(o)=\sqrt{\frac1{w-1}\sum_{j=0}^{w-1}(y_{o-j}-M_w(o))^2}.
$$

rolling_mean_w uses M_w and rolling_std_w uses S_w, with ddof=1. A window is consecutive calendar days, not arbitrary rows. Inputs are shifted relative to the first target day; no target-day demand contributes.

### Trend construction

rolling_slope_14 is the ordinary least-squares slope over the complete last fourteen days, oldest to newest. For x_j=j and z_j=y_(o-13+j), j=0,...,13:

$$
\mathrm{rolling\_slope}_{14}=
\frac{\sum_{j=0}^{13}(x_j-\bar x)(z_j-\bar z)}
{\sum_{j=0}^{13}(x_j-\bar x)^2},\qquad \bar x=6.5.
$$

The slope measures local units/day change. It introduces no percentage-growth denominator, epsilon, clipping or future observation.

### Prediction-time availability

| Predictor group | Latest demand used | Required information |
|---|---|---|
| Identity indicators | No demand calculation | Origin identity must belong to the fitted training vocabulary |
| Weekday sine/cosine | No demand calculation | Known first-target-day date t |
| Lags 1/7/14 | o / o-6 / o-13 | Exact same-series past observation |
| Rolling means/stds 7/14/28 | o | Complete consecutive same-series window |
| Slope 14 | o | Complete fourteen-day window, oldest-to-newest order |

At a validation/final origin, build one row per expected pair and reuse that vector for all four direct forecasts. Do not insert realized window demand, recursively updated forecasts or post-origin operational states. Missing/nonfinite inputs remain unavailable and cause the prescribed eligibility failure; do not impute, shorten windows or fill from the future.

## 5. Retained-feature rationale and exclusions

Identity indicators provide pooled series context. Short lags represent recent level and weekday-aligned history; 7/14/28-day mean/std windows represent local level and dispersion at planning scales; the slope represents local direction. Their inclusion is an approved transparent design, not a claim that ablation proved every feature useful.

The historical EDA shows level autocorrelation but does not prove independent weekly seasonality: the differenced lag-7 median was approximately 0.003. Cyclic weekday representation is retained without claiming predictive superiority. One simulated annual trajectory does not justify month/quarter/year-position features as recurring seasonality.

Excluded alternatives include ordinal day_of_week, month/quarter/year calendars, lag_28, rolling medians, growth ratios/change features, interactions, cumulative/calendar-end encodings and future promotion scenarios. The 28-day mean/std already retain the long local window; extra correlated summaries and denominator-sensitive ratios are outside the accepted feature set. Excluded definitions are not an alternative executable contract.

## 7. Minimum history and training-row completeness

Require **28 complete consecutive daily observations per pair**, ending at each row's own origin, for every model/horizon. This is driven by rolling_mean_28 and rolling_std_28, not lag_28. A labelled row additionally requires all h target days observed by its fitting cutoff, without crossing that cutoff.

For N consecutive historical dates, eligibility before other exclusions is N - 28 - h + 1 rows per series. The initial 91-day history yields 63, 57, 50 and 36 complete rows for horizons 1, 7, 14 and 28. These are feasibility counts, not independent samples or adequacy claims. Overlapping labels create dependence. No partial labels or zero filling are accepted.

## 8. Approval and implementation boundaries

The feature/preprocessing contract is frozen; completed performance and exposure limitations are in [final results](forecasting-final-evaluation.md). Changing this contract requires new human review and cannot be justified using the final interval. Documentation does not authorize preparation, fitting or evaluation.

Implementation: [features.py](../src/forecasting/features.py), [targets.py](../src/forecasting/targets.py), [preprocessing.py](../src/forecasting/preprocessing.py), with [feature tests](../tests/test_forecasting_features.py) and [preprocessing tests](../tests/test_forecasting_preprocessing.py). The [validated handoff](data-cleaning-and-validation.md) owns source preparation; [runner operations](forecasting-runner.md) owns runtime use and persistence.

## Evidence and references

[Historical demand EDA](../reports/demand-eda.md) and [temporal profile](../reports/temporal-demand-profile.md) are descriptive evidence, not renewed feature selection. [References](references.md) holds the literature register. Previously reviewed general guidance includes scikit-learn's [cyclic features](https://scikit-learn.org/stable/auto_examples/applications/plot_cyclical_feature_engineering.html) and [lagged time-series features](https://scikit-learn.org/stable/auto_examples/applications/plot_time_series_lagged_features.html), and FPP3's [useful predictors](https://otexts.com/fpp3/useful-predictors.html) and [regression forecasting](https://otexts.com/fpp3/forecasting-regression.html). Those sources motivate general principles; none proves the exact local windows or final performance on this dataset.
