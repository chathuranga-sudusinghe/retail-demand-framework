# Forecasting feature engineering — final human-reviewed contract

Repository-wide authorities: [data lifecycle](workflows/shared-data-foundation.md), [storage and retention](artifact-storage-policy.md), [applied MLOps](workflows/applied-mlops.md), [research reporting](../reports/README.md), and [continuous progress log](research-progress.md). These connect existing scientific/component contracts without replacing them.

> **Current operational alignment — Issue #94:** Issue #89 is closed and its orchestration implementation was merged in [PR #90](https://github.com/chathuranga-sudusinghe/retail-demand-framework/pull/90). See the methodology revision record for validation-run provenance and evidence availability. Merged Issues #92/#93 define the lifecycle/storage/MLOps authorities; runtime migration remains separate. No new experiment or final evaluation is authorized.

**Status:** HUMAN-REVIEWED — FROZEN FOR IMPLEMENTATION

**Prepared:** 2026-09-28
**Feature freeze:** 2026-09-29
**Representation revision:** Issue #66, 2026-09-29; see [DR-013](decisions/DR-013-matched-gradient-boosting-comparison.md)

**Component owner:** Chathuranga

**Issue:** [#57 — Research: define and freeze forecasting feature-engineering methodology](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/57)

**Approval provenance:** After human review of the Codex and Claude
recommendations, the project owner explicitly accepted the ordered contract of
14 conceptual predictors: two context/identity predictors and twelve engineered
predictors. This replaces the earlier 12-predictor-only contract. It records
human acceptance, not an AI-generated approval or separate supervisor approval.

**Scope:** The feature freeze authorises implementation of the feature/preprocessing
pipeline only. It does **not** authorise model training, hyperparameter tuning,
validation scoring, feature ablation, final evaluation or experiment execution.
The original Issue #57 feature-freeze task changed this document only. The September 29 documentation/provenance alignment is now completed and human-reviewed under Issue #61; it does not implement or accept the source/test pipeline.

## Human-reviewed feature contract

Use the same ordered 14 conceptual predictors, definitions and 28-day minimum
history for primary XGBoost, LightGBM and CatBoost and supportive Ridge/Random Forest, across all four
forecast horizons: 1, 7, 14 and 28 days. The contract contains categorical
SKU_ID and Warehouse_ID plus the twelve accepted numerical engineered features.
Section 3 contains the authoritative contract and encoding policy. Physical
representation is shared by the primary models under Issue #66; conceptual membership and formulas are unchanged.
There are no model-specific or horizon-specific predictor substitutions.

The target remains Units_Sold at SKU_ID + Warehouse_ID + Date. The 7/14/28-day
outputs are direct cumulative targets, issued from the same fixed origin as the
1-day forecast. Features use only information available at or before that origin;
realised demand inside the forecast window must never update the inputs.

The project owner has approved the current 1/7/14/28-day forecasting design.
This feature acceptance does not approve baseline extensions,
the revised executable experiment protocol or downstream methods. See
[revision and provenance](forecasting-methodology-revision.md).

The revised December 3–30, 2024 final evaluation interval is reserved from
subsequent selection and fitting. December 3–16 had prior validation exposure
under the earlier methodology, and full-year EDA also inspected these dates.
The revised interval is therefore not fully unseen historically.

Earlier Issue #52 features/results retain their original methodology and are
not the official baseline for the revised study. No Issue #52 scores or other
old model scores were used to select this feature contract. Earlier Options
A/B/C are superseded; none is a current alternative to the frozen list.

## Feature summary

| Item | Final role/count |
|---|---|
| Raw dataset columns | 15 |
| Direct context predictors | 2 — `SKU_ID`, `Warehouse_ID` |
| Engineered predictors | 12 |
| Total conceptual model predictors | 14 |
| Primary XGBoost / LightGBM / CatBoost physical columns | 67 each under full training-category coverage |
| Supportive Ridge / Random Forest physical columns | 67 each under full training-category coverage |
| Minimum predictor history | 28 complete consecutive days per SKU–warehouse |
| Experiment execution | Not authorised |

### Final model feature vector

The final contract contains the following **14 conceptual model predictors**:
two direct context predictors followed by twelve numerical engineered predictors.
All three primary models and both supportive benchmarks receive this same underlying information for
horizons 1, 7, 14 and 28 days.

1. `SKU_ID`
2. `Warehouse_ID`
3. `dow_sin`
4. `dow_cos`
5. `lag_1`
6. `lag_7`
7. `lag_14`
8. `rolling_mean_7`
9. `rolling_std_7`
10. `rolling_mean_14`
11. `rolling_std_14`
12. `rolling_mean_28`
13. `rolling_std_28`
14. `rolling_slope_14`

Raw dataset → group by `SKU_ID` + `Warehouse_ID` → order by `Date`
→ create the 12 approved engineered features → retain the two categorical identities
→ select the 14 conceptual predictors → apply training-fold-fitted preprocessing.

`SKU_ID` and `Warehouse_ID` serve both as grouping/alignment keys and categorical
model predictors. `Date` is an alignment/calendar source, not a direct predictor.
`Units_Sold` supplies historical demand for feature construction and target labels;
target-day or future `Units_Sold` is never part of the predictor vector.

The conceptual predictor count is exactly **14 = 2 + 12**, not 15 + 12.
The primary models use the same full one-hot representation: 67 physical columns under full eligible-training category coverage, representing fourteen conceptual predictors. Supportive Ridge/Random Forest may reuse it, with numerical scaling only for Ridge. This pipeline description does not authorise experiment execution.

## Contents

1. Purpose and authority
2. Raw dataset roles and predictor boundaries
3. Final ordered feature contract
4. Feature definitions, alignment and leakage controls
5. Retained-feature rationale
6. Final KEEP / EXCLUDE decisions
7. Minimum history and training-row completeness
8. Approval and execution boundaries
9. Implementation mapping and current repository status

- Appendix A — Detailed mathematical notation and date alignment
- Appendix B — Evidence and sources

## 1. Purpose

Define the accepted forecasting predictor contract before implementation and
experiments. Retained features have explicit formulas and availability rules;
excluded definitions are kept where useful for calculation provenance and
exclusion rationale. Their presence does not make them active inputs.

The [dataset contract](dataset.md) describes 15 raw columns, 250 daily
SKU–warehouse series and one simulated year. This document uses existing code,
Decision Records, saved descriptive evidence and the independent review's bounded
metadata observations in Section 2.7. This documentation update ran no profiling,
tests or experiments. No model was fitted and no new forecast results from the
revised final evaluation interval were inspected for this freeze.

### 1.1 Authority and earlier experiment provenance

| Evidence | What it establishes | What it does not establish |
|---|---|---|
| Human-reviewed Issue #57 feature-freeze decision | Final order of 14 conceptual predictors, two categorical identities, twelve engineered predictors, encoding policy and common use across learned models and all four horizons; feature/preprocessing implementation authority | Experiment execution, scientific performance claims or wider methodology approval |
| DR-002 | SKU_ID + Warehouse_ID + Date; target Units_Sold | Permission to use identity columns as predictors |
| DR-003 | Initial 7/14-day historical-window baseline and past-only construction | The later 28-day feature extension; that extension is explicitly accepted in this feature freeze |
| DR-004 and DR-008 | Current human-approved direct 1/7/14/28-day design | Daily paths inside cumulative forecasts or approval of unrelated methods |
| DR-005, DR-006 and DR-010 | Revised temporal validation/final-evaluation design and its prior exposure, existing WAPE-led selection and bounded grids | A fully unseen final interval or a feature-search grid |
| Earlier [Issue #52 protocol](issue-52-forecasting-protocol.md) | Historical approval of that experiment's 13 columns and execution protocol | Feature selection evidence or an executable protocol for this frozen contract |
| AGENTS.md Sections 17–19 | Human decisions and specific experiment authorisation remain mandatory | Authority for an AI assistant to approve changes or run experiments independently |

Preserve the earlier protocol/report and their approval history. They must not
be relabelled as results from this contract or the revised study. Historical
descriptive evidence informs rationale; it does not demonstrate incremental
forecast skill. No reference, report or Decision Record is rewritten here.

## 2. Raw dataset features

These classifications record the frozen forecasting boundaries. KEEP/EXCLUDE
refers to predictor membership, not removal of raw fields needed as keys,
calendar sources, labels or downstream evidence. “Recorded on a date” does not prove the field was known when the
forecast was issued. Future calendars are deterministic; future operational rows
require an independent availability contract. Definitions follow [dataset.md](dataset.md).

### 2.1 Raw feature/input table

| Raw column | What it represents | Classification | Prediction-time availability | Leakage concern | Engineered-feature possibility | Forecasting membership / current direct use |
| --- | --- | --- | --- | --- | --- | --- |
| `Date` | Daily observation calendar | Feature construction / grouping / alignment only | Target calendar known at origin | Low for deterministic calendars; time position can act as a proxy for one-year level changes | Selected weekday sine/cosine; other calendar encodings excluded | Used to derive calendars and order history; raw timestamp is not a numeric predictor |
| `SKU_ID` | Product identifier | KEEP as categorical model predictor; grouping/alignment key | Requested product identity known at origin | Wrong joins/target encodings can mix series or use future targets | Training-fold-fitted categorical encoding under Section 3 | Product context for the global model; never a continuous numeric measurement |
| `Warehouse_ID` | Warehouse identifier | KEEP as categorical model predictor; grouping/alignment key | Requested warehouse identity known at origin | Collapsing warehouses or inconsistent category mappings can mix contexts | Training-fold-fitted categorical encoding under Section 3 | Warehouse context for the global model; never a continuous numeric measurement |
| `Supplier_ID` | Recorded supply relationship | EXCLUDE as predictor | Series-level mapping observed in initial training; future reassignment not established | Supplier allocation may depend on operations/demand; full-year target encoding leaks | No supplier-derived forecasting feature accepted | Descriptive/downstream metadata; no independent demand justification established |
| `Region` | Recorded geographic context | EXCLUDE as predictor | Not stable within a series in initial training; future value availability unestablished | Using future record regions or assuming a fixed warehouse geography | No region-derived forecasting feature accepted | Descriptive metadata pending semantic clarification; no country-specific demand assumptions |
| `Units_Sold` | Daily simulated recorded sales | Feature construction / target only | Observed history through origin, subject to reporting latency; future sales unavailable | Same-row/future sales, centred windows and future-filled gaps directly expose targets | Accepted historical demand lags, rolling summaries and slope | Historical source and observed label; only accepted past-derived columns are predictors |
| `Inventory_Level` | Simulated on-hand stock | EXCLUDE as predictor; downstream inventory context | Origin snapshot timing must be established; future snapshot unavailable | End-of-day stock may encode that day's sales/receipts; generated stock may contain target information | No forecasting feature currently allowed; separate exposure calculation | Keep in inventory component; do not assume it corrects censored demand |
| `Supplier_Lead_Time_Days` | Simulated replenishment delay | EXCLUDE as predictor; downstream replenishment context | Origin supply terms require documented availability | Future realised/updated lead time is not an origin input | Context for approved inventory interpretation, not horizon-demand arithmetic predictors | No forecasting use approved; no interpolated targets or feature windows based on it |
| `Reorder_Point` | Source policy threshold | EXCLUDE as predictor; downstream inventory-policy context | Fixed origin policy snapshot needs provenance | Updated or source-generated threshold might reflect future demand/policy | Downstream buffer only under its own methodology | Excluded from predictor construction and feature selection |
| `Order_Quantity` | Quantity ordered on the recorded row | EXCLUDE as predictor; downstream replenishment context | Origin availability and order timing unestablished; not a receipt schedule | Orders are endogenous decisions and may follow realised sales | No forecast input approved; any historical order feature needs a separate decision | Sparse operational evidence; neither normal dense target nor implied incoming receipt |
| `Unit_Cost` | Business purchase cost per unit | EXCLUDE as predictor; downstream business context | Series-level metadata in initial training; effective/publication time not established | Later revisions or simulator relations can expose future/source mechanisms | No cost/margin/price-to-cost feature approved | Business interpretation under current boundaries; cost is not automatically demand information |
| `Unit_Price` | Simulated selling price per unit | EXCLUDE as predictor | Series-level metadata in initial training; future prices need an origin-known plan | Realised future prices, discounts inferred after sales, or unverified source construction | No price transformation accepted | Descriptive/business context; no independent demand justification or causal elasticity established |
| `Promotion_Flag` | Promotion active on a SKU–warehouse day | EXCLUDE as predictor | Future use requires a valid origin-known promotion-plan contract | Actual target-period flags are not automatically known plans | No promotion transformation accepted | Retain warehouse-specific descriptive alignment; no plan availability accepted |
| `Stockout_Flag` | Intended stockout indicator | EXCLUDE as predictor | Even a dated historical flag has no useful variation here | Future stockout would be unavailable and endogenous | None defensible as predictor/label with all-zero verified field | Exclude; cannot establish unconstrained demand or validate stockout accuracy |
| `Demand_Forecast` | Simulator/source-generated forecast | EXCLUDE as predictor; leakage-sensitive/reference-only | Source forecast issuance time and construction unknown | May depend on actual target or information unavailable at origin | No residual, lag, ratio or blend with it is approved | Not the project forecast or an ordinary predictor; separate benchmark requires explicit leakage-safe approval |

Historical [EDA](../reports/demand-eda.md) documents no raw missing values,
all-zero `Stockout_Flag`, and 5,027 nonzero order rows. The earlier
[alignment report](../reports/temporal-demand-profile.md) finds promotion conflicts
in 41.6219% of SKU-day groups across warehouses. These facts support preserving
the native grain and checking availability; they do not approve extra predictors.

### 2.2 Accepted historical and calendar sources

Date supplies deterministic calendar information; historical Units_Sold supplies
past demand memory and the future evaluation target. Their role and availability
remain exactly as described in the 15-column table above.

### 2.3 Identity/context predictors and grouping fields

SKU_ID and Warehouse_ID are **KEEP as categorical model predictors**. They also
identify the native series and control every grouping and alignment operation.
The learned models are global models trained across 250 SKU–warehouse series.
Grouping alone does not expose series identity to the estimator; including the
two categories allows it to distinguish product and warehouse context when
different series have similar lag/rolling values. If numerical feature vectors
are identical, a model without identities cannot distinguish their series.

Neither identifier is a continuous numeric variable. Their inclusion provides
legitimate origin-known context, not proof that identities improve accuracy.
Supplier_ID and Region remain EXCLUDE as predictors. Date remains an alignment
key and calendar source; raw numeric Date is EXCLUDE as a predictor.

### 2.4 Downstream-only fields

Inventory_Level, Supplier_Lead_Time_Days, Reorder_Point, Order_Quantity and
Unit_Cost retain their downstream roles. Their timing, endogeneity and research
boundaries are recorded in the raw input table.

Exclusion from demand predictors does not make these fields useless to the
overall project. The demand model predicts future demand; the downstream
inventory-risk/replenishment component combines that forecast with
Inventory_Level, Reorder_Point, Supplier_Lead_Time_Days and Order_Quantity under
its own approved definitions and origin-alignment rules.

### 2.5 Excluded/leakage-sensitive/reference-only fields

Stockout_Flag remains excluded. Demand_Forecast remains leakage-sensitive and
reference-only, subject to separate benchmark approval. Neither supplies an
ordinary project forecasting feature.

### 2.6 Excluded contextual inputs and availability cautions

Promotion_Flag, Unit_Price, Supplier_ID and Region are EXCLUDE as predictors.
Promotion and price must not be assumed known in advance; recording a value in
a dated source row establishes neither an origin-known plan nor publication
provenance. Any change to these exclusions requires a separate human-reviewed
contract revision before implementation.

### 2.7 Independent-review structural observations

The independent review checked contextual metadata only within the initial
training interval of the local, Git-ignored `data/raw/supply_chain_dataset1.csv`,
January 1–March 31, 2024: 22,750 rows, 250 series, 91 dates per
series, 50 SKU values and five warehouse values. It did not analyse demand values,
model scores or final-period outcomes. This update reuses those observations;
no new profiling was run.

- Region does not behave like stable warehouse geography: every SKU–warehouse
  series contains all four regions during that interval, as does each warehouse.
- Supplier_ID, Unit_Price and Unit_Cost behave as series-level metadata: each is
  constant within every SKU–warehouse series in that interval. Supplier is not
  determined by SKU alone; each SKU has three to five suppliers across warehouses.
  Each SKU also has five distinct prices across warehouses.
- These scoped observations do not prove full-year stability or future plan
  availability. Series-level metadata adds no new pair identity information
  within that interval, but can change a restricted model's representation; its
  exclusion is not a claim of exact linear redundancy with separate ID encodings.
- The saved EDA's promotion association does not establish a future promotion
  schedule. Future Promotion_Flag use requires an origin-known plan contract.
- Demand_Forecast remains reference-only because construction/issuance timing is
  unknown; Stockout_Flag remains excluded because its verified value is always zero.

No new forecasting features are introduced from these excluded fields.


## 3. Final ordered feature contract

The human-reviewed final KEEP list contains exactly 14 conceptual predictors, in
the order shown in [Final model feature vector](#final-model-feature-vector).
It contains two context/identity predictors and twelve engineered predictors,
and is frozen for feature/preprocessing pipeline implementation.

Primary XGBoost, LightGBM and CatBoost and supportive Ridge/Random Forest use this same feature order and
the same definitions for horizons 1/7/14/28. At one origin, the input vector is
shared across horizon models; cumulative labels differ by horizon. SKU_ID and
Warehouse_ID enter the predictor matrix through the categorical representations
below and remain separately available as alignment keys. Date and Units_Sold
have construction/alignment/target roles only, not direct predictor membership.

The calendar is the first target day, t=o+1. Historical inputs end at o.
Preprocessing that learns statistics must fit only eligible training rows;
encoding must preserve conceptual membership and information, with identical physical representation across the three primary models.
Record stable physical column order and category mappings for each fitted pipeline.
No feature ablation, extra interaction, alternative window or feature-search
dimension is authorised by this contract.

### 3.1 Categorical encoding and physical feature counts

[DR-013](decisions/DR-013-matched-gradient-boosting-comparison.md) revises physical representation for the primary controlled RQ2 comparison. The Issue #57 conceptual feature membership, order and numerical definitions remain frozen. XGBoost, LightGBM and CatBoost all use full one-hot SKU_ID and Warehouse_ID encoding with all eligible-training category levels retained (`drop=None`), followed by the same twelve numerical predictors. Do not use native categorical handling in the primary LightGBM or CatBoost model.

| Evidence role / model | Conceptual predictors | Encoding | Physical columns with full training coverage |
|---|---:|---|---:|
| Primary XGBoost | 14 | Full one-hot SKU_ID + Warehouse_ID, then numerical predictors | 67 |
| Primary LightGBM | 14 | Same full one-hot representation | 67 |
| Primary CatBoost | 14 | Same full one-hot representation | 67 |
| Supportive Ridge | 14 | Full one-hot identities, numerical scaling only | 67 |
| Supportive Random Forest | 14 | Full one-hot identities, unscaled numerical inputs | 67 |

Expected full-coverage width is 50 SKU + 5 warehouse + 12 numerical = **67**, representing fourteen conceptual predictors. Fit category vocabularies only on the same eligible training rows for each fold/horizon. Use lexical category ordering, SKU columns before warehouse columns, followed by the frozen numerical order. Share those mappings/order across the primary models; do not infer category levels from validation or final-evaluation data. Smaller training coverage yields `n_SKU + n_warehouse + 12` columns consistently across primary models, rather than fabricating future categories. Record coverage and actual width. Unknown prediction identities raise under the accepted Issue #62 policy; no all-zero fallback or silent population exclusion is approved.

IDs are nominal categories, never continuous measurements. Primary tree inputs and supportive Random Forest numerical inputs are unscaled. Ridge standardises only the twelve numerical predictors using eligible-training means and population standard deviations (`ddof=0`, constant-column scale 1); identity indicators remain 0/1. This scaler convention does not change the engineered demand-window sample standard deviations (`ddof=1`). A model intercept is not an extra input column. No target encoding, interaction ID or additional engineered feature is accepted.

**Earlier representation provenance:** Issue #57 and the accepted Issue #62 implementation used 67 one-hot columns for Ridge/Random Forest and 14 native categorical/numerical inputs for LightGBM. That earlier primary representation is superseded by Issue #66; the current source/tests implement the later common primary representation.

### 3.2 Controlled model comparison

The primary models share the same predictor information and physical encoding, origins, eligible observations, target definitions, temporal folds, complete history rules, metrics, matched four-dimensional grid and seed policy. All learned preprocessing uses eligible training rows only.

The principal experimental variable is the gradient-boosting implementation. Equal external settings do not make internal tree-growing algorithms, capacities, parameter effects or sampling draws identical. Supportive Ridge/Random Forest provide contextual evidence only; their model-appropriate scaling and fixed configuration policy resolved in the frozen protocol do not determine RQ2. Random Forest column-sampling settings from the resolved supportive configuration must be recorded during authorised execution; no tuning dimension is added here.

## 4. How engineered features are constructed

### 4.1 Short mathematical notation

For one SKU–warehouse series, $o$ is the origin, $t=o+1$ is the first target day
(the code's Date), and $y_u$ is Units_Sold on day $u$. Under the current
human-approved 1/7/14/28-day design, the forecast targets are:

$$
Y_{o,h}=\sum_{j=1}^{h}y_{o+j},
\qquad h\in\{1,7,14,28\}.
$$

These are observed labels, not forecasting features. Full symbol definitions and
the detailed date-alignment caution are in Appendix A.

The construction groups below retain every formula, source, availability condition
and leakage caution from the reviewed catalogues. Worked examples follow in
Section 4.8; recommendations and evidence are in Sections 5 and 6.

### 4.2 Calendar construction

Source: Date of the first target day. Calendar values are known at origin and do
not use future demand. A known calendar representation does not establish that a
seasonal effect exists.

EXCLUDE — historical integer calendar definitions, retained for provenance only:

$$
\text{day\_of\_week}(t)=d(t), \qquad d(t)\in\{0,\ldots,6\},
$$

The weekday integer is Monday = 0 through Sunday = 6.

$$
\text{month}(t)=m(t), \qquad m(t)\in\{1,\ldots,12\},
$$

The month integer is January = 1 through December = 12.

$$
\text{quarter}(t)=\left\lfloor\frac{m(t)-1}{3}\right\rfloor+1.
$$

The quarter groups the target-start month into one of four calendar quarters.

KEEP — selected weekday sine/cosine pair:

$$
\text{dow\_sin}(t)=\sin\left(\frac{2\pi d(t)}7\right),
$$

The sine component represents position within a seven-day calendar cycle.

$$
\text{dow\_cos}(t)=\cos\left(\frac{2\pi d(t)}7\right),
$$

The cosine component completes the paired weekday representation.

#### Why weekday sine/cosine encoding is used

Weekday is cyclic rather than purely linear: Sunday is followed by Monday.
The raw weekday integers are Monday=0, Tuesday=1, Wednesday=2, Thursday=3,
Friday=4, Saturday=5 and Sunday=6. With these values as a numeric input, a model
can interpret Monday (`0`) and Sunday (`6`) as far apart, although they are
adjacent in the weekly cycle:

```text
Linear weekday labels                    Cyclic weekday view

Mon → Tue → Wed → Thu → Fri → Sat → Sun              Mon
 ↑                                  ↓            Sun     Tue
 └──────────────────────────────────┘          Sat         Wed
                                                Fri     Thu
```

The left view shows the weekday sequence and the wrap from Sunday back to
Monday. The right view shows the same information as a cycle. This better
reflects the relationship represented by `dow_sin` and `dow_cos`: Sunday (`6`)
and Monday (`0`) are adjacent in the weekly cycle even though their raw integer
values appear far apart.

The frozen weekday representation uses the paired `dow_sin(t)` and
`dow_cos(t)` formulas above to represent position around this cycle. The pair
places weekdays around a unit circle, with $x=\text{dow\_cos}(t)$ and
$y=\text{dow\_sin}(t)$:

$$
x^2+y^2=1.
$$

This representation preserves the cyclic closeness between Sunday and Monday.
The sine/cosine values are input features only; they do not calculate the demand
forecast themselves. The human reviewer has accepted this paired representation
for the common pipeline across all learned models and horizons.

#### Excluded calendar alternatives

$$
\text{month\_sin}(t)=\sin\left(\frac{2\pi(m(t)-1)}{12}\right),
$$

The sine component represents position within a twelve-month calendar cycle.

$$
\text{month\_cos}(t)=\cos\left(\frac{2\pi(m(t)-1)}{12}\right),
$$

The cosine component completes the paired month representation.

$$
\operatorname{dow}_k(t)=\mathbf{1}\{d(t)=k\}, \qquad k=0,\ldots,5.
$$

Each weekday dummy is 1 for its named weekday and 0 otherwise; Sunday is the reference.

The six fixed dummy names and Sunday reference are retained in the worked example.
KEEP applies to the weekday sine/cosine pair together. Raw day_of_week, month,
quarter, month sine/cosine and all weekday dummies are EXCLUDE in this contract.
The raw weekday index is used only to calculate the selected pair.

#### Human-readable weekday labels for downstream interpretation

Derive the forecasting calendar directly as Date → day-of-week index → dow_sin /
dow_cos. No stored `weekday_name` predictor is required.

A human-readable weekday label such as Monday–Sunday may be derived from Date by
downstream inventory-risk, replenishment or decision-support components if useful
for operational interpretation, such as reorder timing, lead-time behaviour,
weekend effects or weekday-based replenishment patterns. This label is **not part
of the forecasting model predictor vector**. Its availability does not establish
that such operational effects exist or approve a new downstream rule.

### 4.3 Lag construction

Source: `Units_Sold` within the same SKU–warehouse history.

Lag features use past demand values from the same series as forecasting inputs.

- `lag_1` = demand from 1 day earlier;
- `lag_7` = demand from 7 days earlier;
- `lag_14` = demand from 14 days earlier.

The retained lag indices are 1, 7 and 14. EXCLUDE: `lag_28` is one older daily
observation, not a four-week demand summary.

Keep lag_7 and lag_14 as historical demand memory at different past positions.
They also match the weekday of the first target day, but their inclusion is not
justified solely as evidence of weekly seasonality; the saved EDA does not
establish a dominant weekly predictive effect.

If the first forecast day is 15 April:

```text
lag_1  → demand from 14 April
lag_7  → demand from 8 April
lag_14 → demand from 1 April
```

For historical comparison only, excluded `lag_28` would use demand from 18 March.

The retained lag rule is:

$$
\text{lag}_k(t)=L_k(t)=y_{t-k}=y_{o-k+1},
\qquad k\in\{1,7,14\}.
$$

$$
L_1(t)=y_o
$$

$$
L_7(t)=y_{o-6},
$$

$$
L_{14}(t)=y_{o-13}
$$

EXCLUDE — historical lag-28 definition:

$$
L_{28}(t)=y_{o-27}.
$$

EXCLUDE — historical lag-difference definitions:

$$
\text{lag\_difference\_7\_14}(o)=L_7(t)-L_{14}(t),
$$

This subtracts the older matching-weekday sales value from the more recent one.

$$
\text{origin\_weekday\_change}(o)=y_o-y_{o-7}=L_1(t)-L_8(t).
$$

This compares sales at the origin with sales seven days before the origin.

History availability requires the exact indicated past dates; the origin comparison
needs eight dates. Shifts remain isolated by both identity keys and must never be
updated with actual demand arriving after the forecast origin.

### 4.4 Rolling-statistics construction

Source: complete historical Units_Sold windows ending at origin, within one series.
The retained window sizes are $w\in\{7,14,28\}$; KEEP applies only to mean and
sample standard deviation for each window:

$$
M_w(o)=\frac1w\sum_{j=0}^{w-1}y_{o-j}.
$$

For `rolling_mean_7`, `rolling_mean_14` and `rolling_mean_28`, average the most
recent 7, 14 or 28 observed daily sales values, ending at the origin.

EXCLUDE — historical median definition for w=7/14/28:

$$
Q_w(o)=\operatorname{median}\{y_o,y_{o-1},\ldots,y_{o-w+1}\}.
$$

The excluded `rolling_median_7`, `rolling_median_14` and `rolling_median_28`
would take the middle of the ordered sales values in the same window.

For an even window, the median averages the two middle ordered values.

KEEP — rolling standard deviation for w=7/14/28:

$$
S_w(o)=\sqrt{\frac{1}{w-1}
\sum_{j=0}^{w-1}\left(y_{o-j}-M_w(o)\right)^2}.
$$

For `rolling_std_7`, `rolling_std_14` and `rolling_std_28`, measure dispersion
around the respective window mean using sample standard deviation.

KEEP: the six rolling mean/std columns use complete windows; sample standard
deviation uses ddof=1. All rolling medians are EXCLUDE. Shift demand before rolling, require the full daily window,
and preserve missing history rather than using centred, partial or future-filled windows.

EXCLUDE — historical relative/robust volatility definitions:

$$
\text{rolling\_cv\_14}(o)=
\begin{cases}
S_{14}(o)/M_{14}(o),&M_{14}(o)>0,\\
\text{unavailable},&M_{14}(o)=0.
\end{cases}
$$

This expresses fourteen-day dispersion relative to the mean; a zero mean leaves the feature unavailable.

$$
\text{rolling\_mad\_14}(o)=
\operatorname{median}_{j=0,\ldots,13}
\left\lvert y_{o-j}-Q_{14}(o)\right\rvert.
$$

This takes the median absolute distance from the fourteen-day median, without rescaling.

$$
\text{volatility\_ratio\_7\_14}(o)=
\begin{cases}
S_7(o)/S_{14}(o),&S_{14}(o)>0,\\
\text{unavailable},&S_{14}(o)=0.
\end{cases}
$$

This compares seven-day and fourteen-day dispersion; a zero denominator leaves the feature unavailable.

Median absolute deviation remains unscaled. No epsilon, normalisation factor,
forecast interval or numerical stability/review threshold is approved.

### 4.5 Trend/growth construction

Source: historical Units_Sold, without future smoothing. The preceding
non-overlapping window has mean:

$$
P_w(o)=\frac1w\sum_{j=0}^{w-1}y_{o-w-j}.
$$

This averages the preceding window of the same length, without overlapping the most recent window.

EXCLUDE — historical adjacent-week and medium-term comparisons:

$$
\text{trend\_week\_difference}(o)=M_7(o)-P_7(o),
$$

This compares the latest seven-day mean with the preceding seven-day mean.

$$
\text{trend\_fortnight\_difference}(o)=M_{14}(o)-P_{14}(o).
$$

This compares the latest fourteen-day mean with the preceding fourteen-day mean.

The first requires fourteen complete dates; the second requires twenty-eight.
The 28-day mean is now retained explicitly; the fortnight difference remains
EXCLUDE because it is derived from retained 14/28-day means.

$$
\text{trend\_week\_growth}(o)=
\begin{cases}
\bigl(M_7(o)-P_7(o)\bigr)/P_7(o),&P_7(o)>0,\\
\text{unavailable},&P_7(o)=0.
\end{cases}
$$

This expresses the change between weekly means relative to the preceding mean; a zero denominator leaves it unavailable.

KEEP — rolling_slope_14 is the linear slope across the most recent fourteen
observed daily Units_Sold values, ordered oldest to newest. Set the time index
$x_j=j$ and demand $z_j=y_{o-14+j}$ for $j=1,\ldots,14$, so $\bar{x}=7.5$:

$$
\text{rolling\_slope\_14}(o)=b=
\frac{\sum_{j=1}^{14}(j-7.5)\bigl(z_j-M_{14}(o)\bigr)}
{\sum_{j=1}^{14}(j-7.5)^2}.
$$

This is equivalent to the historical zero-based index 0,...,13 with centre 6.5.

This measures the fitted change in daily sales per day across the fourteen-day historical window.

The slope uses only fourteen complete origin-available observations, in units
of daily sales change per day. It is a recent direction descriptor, not guaranteed
future growth, an extrapolation rule or a new forecasting model. The ratio
features are EXCLUDE; no denominator workaround is introduced.

The existing redundancy cautions are preserved:

$$
M_7(o)-P_7(o)=2\bigl(M_7(o)-M_{14}(o)\bigr),
$$

$$
M_{14}(o)-P_{14}(o)=2\bigl(M_{14}(o)-M_{28}(o)\bigr).
$$

### 4.6 Excluded contextual and interaction definitions

Every feature in this subsection is EXCLUDE from the frozen predictors. The
historical definitions and availability cautions are retained for provenance.
Historical promotion flags are $p_u$, origin-known promotion
plans are $a_{u\mid o}$, and available effective historical prices are $v_u$.
The source CSV alone establishes neither plan nor publication provenance.

Promotion and pricing constructions:

$$
\text{promotion\_share\_7}(o)=\frac17\sum_{j=0}^{6}p_{o-j},
$$

This is the fraction of the last seven historical days marked as promotional.

$$
\text{planned\_promotion\_days}_h(o)
=
\sum_{j=1}^{h} a_{o+j \mid o}
$$

where \(h \in \{1,7,14,28\}\).

This counts promotional days in the target horizon using only a plan demonstrably known at the origin.

$$
\text{promotion\_origin\_x\_mean\_7}(o)=p_oM_7(o).
$$

This retains the recent mean when the origin is promotional and is zero otherwise.

$$
\text{price\_change\_7}(o)=
\begin{cases}
\bigl(v_o-v_{o-7}\bigr)/v_{o-7},&v_{o-7}>0,\\
\text{unavailable},&v_{o-7}\leq0.
\end{cases}
$$

This expresses the historical price change relative to the price seven days earlier; a nonpositive denominator leaves it unavailable.

Historical flags/prices require evidence that they were available by the
appropriate origin. Planned promotion counts require every target-window value
to have been known at origin. Realised future flags/prices are not substitutes,
and no carryover or elasticity effect is established.

The reviewed calendar/level interaction and weekday-count family are:

$$
\text{weekday\_x\_mean\_7}(o)=\mathbf{1}\{d(t)=0\}M_7(o),
$$

This excluded definition retains the recent mean for a Monday target start and
is zero otherwise; it is not a predictor in the frozen contract.

$$
\text{target\_weekday\_count}_{h,k}(o)=
\sum_{j=1}^{h}\mathbf{1}\{d(o+j)=k\},
\qquad h\in\{1,7,14,28\},\quad k=0,\ldots,6.
$$

This counts how many times each weekday occurs in the target horizon.

The Monday interaction and all weekday-count features are EXCLUDE. Weekday counts
are calendar-known: horizon 7 contains each weekday once, horizon 14 twice, and
horizon 28 four times. These features are therefore constant within each of the
three complete-week cumulative horizons 7/14/28, so they are EXCLUDE
from those horizons. At horizon 1, counts duplicate weekday indicators
and are also EXCLUDE.

The reviewed inventory composite remains outside forecasting:

$$
\text{inventory\_buffer}(o)=I_o-R_o.
$$

This subtracts the origin reorder point from origin inventory; it remains a downstream composite, not an approved forecasting input.

Origin inventory/policy availability and the downstream ownership boundary
continue to apply. This displayed formula does not approve a forecasting input.


### 4.7 Prediction-time availability and leakage controls by retained feature

| Retained feature(s) | Source | Required complete demand history | Availability / leakage control |
|---|---|---:|---|
| SKU_ID, Warehouse_ID | Requested product/warehouse identity | 0 days | Origin-known nominal categories; stable training-fold-fitted encoding, never numeric ordering |
| dow_sin, dow_cos | Date=t=o+1 | 0 days | Known calendar; no demand or fitted outcome statistics |
| lag_1 | Units_Sold at o | 1 day | Observed by origin; reporting latency must not be ignored |
| lag_7 | Units_Sold at o-6 | 7 days | Same series, target-start lag alignment |
| lag_14 | Units_Sold at o-13 | 14 days | Same series, target-start lag alignment |
| rolling_mean_7, rolling_std_7 | Units_Sold at o-6,...,o | 7 days | Shift before rolling; complete window; std ddof=1 |
| rolling_mean_14, rolling_std_14 | Units_Sold at o-13,...,o | 14 days | Same origin restriction and completeness rule |
| rolling_mean_28, rolling_std_28 | Units_Sold at o-27,...,o | 28 days | Same origin restriction and completeness rule |
| rolling_slope_14 | Ordered Units_Sold at o-13,...,o | 14 days | Past-window slope only; no future smoothing |

The whole vector requires 28 complete consecutive daily observations per
SKU_ID + Warehouse_ID. Missing required observations remain unavailable;
no imputation, partial window or future-filled history is approved.
Historical training rows use their own origins. Fixed-origin forecasts mask
later actual demand and use the row at t=o+1 for every horizon.

### 4.8 Historical calculation examples — not the active predictor list


Illustrative inputs only: set $t=\text{2024-04-01}$, $o=\text{2024-03-31}$, with 28 consecutive
historical values `1,2,...,28` from oldest to newest. No source dataset was used
to calculate this example.

| Features | Example outputs | Implementation reference |
|---|---|---|
| `day_of_week`, `month`, `quarter` | `0`, `4`, `2` | `build_features`: calendar assignments |
| `lag_1`, `lag_7`, `lag_14`, `lag_28` | `28`, `22`, `15`, `1` | `build_features`: per-series `groups.shift(lag)` |
| `rolling_mean_7`, `rolling_median_7`, `rolling_std_7` | `25`, `25`, $\sqrt{14/3}$ ≈ `2.1602` | `shift(1).rolling(7,min_periods=7)`; std ddof=1 |
| `rolling_mean_14`, `rolling_median_14`, `rolling_std_14` | `21.5`, `21.5`, $\sqrt{17.5}$ ≈ `4.1833` | Same construction for window 14 |

This example records the historical implementation, including features now
EXCLUDE. It is not the frozen predictor list. Retained formulas are unchanged;
Section 3 alone defines the active feature order.

#### Historical reviewed-definition examples

Using the same synthetic `1..28` history as Section 4.8:

- $\texttt{dow\_sin}=0$, $\texttt{dow\_cos}=1$ and $\texttt{dow\_mon}=1$ for the Monday target start.
- The six fixed dummy names, in weekday order, are `dow_mon`, `dow_tue`,
  `dow_wed`, `dow_thu`, `dow_fri`, `dow_sat`. The Monday example is
  `[1,0,0,0,0,0]`; Sunday is `[0,0,0,0,0,0]` under the stated reference convention.
- For April, $\texttt{month\_sin}=1$ and $\texttt{month\_cos}=0$ (exact trigonometric values).
- $M_7=25$, $P_7=18$; $\texttt{trend\_week\_difference}=7$ and
  $\texttt{trend\_week\_growth}=7/18$ ≈ `0.3889`.
- $\texttt{lag\_difference\_7\_14}=22-15=7$; $\texttt{origin\_weekday\_change}=28-21=7$.
- $\texttt{rolling\_slope\_14}=1$ unit per day; $\texttt{trend\_fortnight\_difference}=21.5-7.5=14$.
- $\texttt{rolling\_cv\_14}=\sqrt{17.5}/21.5$; $\texttt{rolling\_mad\_14}=3.5$;
  $\texttt{volatility\_ratio\_7\_14}=\sqrt{14/3}/\sqrt{17.5}$.
- If independently documented historical promotions were `[0,0,1,0,0,1,0]`,
  $\texttt{promotion\_share\_7}=2/7$; the origin interaction is zero because $p_o=0$.
- If an actual origin-known seven-day plan were `[1,1,0,0,0,0,0]`, its planned
  promotion count would be 2. Reading those values retrospectively from the raw
  target rows would not establish this availability.
- If available prices changed from 10 at $o-7$ to 11 at $o$, $\texttt{price\_change\_7}=0.1$.
- Monday level interaction would be 25; each seven-day weekday count is 1.
  A hypothetical inventory snapshot 400 and threshold 300 gives buffer 100,
  but that computation belongs to the downstream component.

### 4.9 Conditions the frozen feature pipeline must enforce

1. Keep $\texttt{forecast\_origin}=o$, $\texttt{target\_start\_date}=t=o+1$ and target end $o+h$
   explicit. Issue all four direct 1/7/14/28-day forecasts from one origin's
   evidence under the human-selected revised direction, which remains under
   repository-wide human review.
2. Construct each historical row's demand features only from its own earlier
   history. For fitting at cutoff $c$, require its whole cumulative target to end
   by $c$; otherwise future outcomes can leak despite correct lag construction.
3. Group every shift, window, slope and join by both SKU and warehouse. Do not
   concatenate series or silently collapse warehouse-specific promotions.
4. At a fixed validation origin, mask later actual demand before construction.
   Do not compute features at every validation date using newly realised sales
   unless a separately approved updating protocol permits that different experiment.
5. Distinguish raw completeness from feature availability. Do not shorten windows,
   forward/backfill or compute partial means silently. Ratio features are EXCLUDE;
   do not add denominator workarounds or arbitrary epsilons.
6. Fit the approved identity encoders and Ridge numerical scaler only on the
   relevant fold's eligible training data under Section 3.1. Do not scale identity
   indicators or treat category codes as continuous quantities. No imputation,
   target encoding or additional feature selection is authorised.
7. Keep excluded exogenous/operational columns outside this contract. The accepted
   origin-known identities are the only direct context predictors. CSV row dates
   do not establish promotion/price availability. Any separately accepted revision would
   need effective date, publication time, origin-time version and missing-state
   rules; historical lagging alone does not establish availability.
8. Keep source forecasts, future inventory, actual cumulative labels, forecast
   errors and retrospective threshold crossings out of prospective predictors.
9. Enforce exactly the ordered conceptual list in Section 3 for the primary
   XGBoost/LightGBM/CatBoost models and supportive Ridge/Random Forest at every
   horizon. Primary models share full one-hot inputs. Membership or representation
   changes require separate human review.
10. Reserve the revised December 3–30, 2024 final evaluation interval from all
    subsequent feature, model and hyperparameter selection decisions and fitting.
    December 3–16 had prior validation exposure under the earlier 14-day design,
    so this interval is not fully unseen historically. Existing full-year EDA
    also had descriptive exposure to those dates; disclose both sources of exposure.
    Earlier validation results also mean subsequent experiments are not an
    entirely fresh search against unseen validation evidence.

Availability at the origin, rather than a field's eventual existence, is the
requirement for forecasting with predictors. The ex-ante/ex-post distinction is
explained in [Hyndman and Athanasopoulos, FPP3 Section 7.6](https://otexts.com/fpp3/forecasting-regression.html).

### 4.10 Implementation acceptance checks

These are documented checks for subsequent implementation review, not executed
tests or experiment commands. This documentation task runs none of them:

- At origin 2024-03-31, first target date is April 1 and the 28-day outcome ends
  April 28. Changing any April demand must not alter that origin's inputs.
- Changing warehouse B history must not alter warehouse A features for the same SKU.
- Adding a future promotion row must not populate an origin-known plan field.
- Shuffling source rows must not change keyed features after chronological sorting.
- A missing day/value must not become a complete lag/window or a zero-demand observation.
- Exact window lengths, sample/std convention and slope direction must be checked
  with synthetic histories, including a constant and all-zero demand history.
- Conceptual membership/order and formula version must match the frozen contract;
  missing windows stay unavailable and all retained std features use ddof=1.
- Verify both identities enter each model's predictor representation, with all
  category levels retained in one-hot matrices, stable mappings, training-only
  numerical scaling for Ridge and equivalent eligible rows across models.
- With full eligible-training category coverage, expected physical counts are
  67 for each primary model and supportive benchmark; the conceptual count remains 14.
  Primary matrices must have identical values/order and numerical scaling must stay off.
- Derive weekday phase directly from Date; no weekday_name predictor is included.

## 5. Retained-feature rationale

### 5.1 Why the twelve retained engineered features are used

These are human-reviewed design rationales, not demonstrated improvements in
forecast accuracy. The saved EDA is descriptive evidence, not a feature-selection
experiment.

| Retained feature | Purpose | Main limitation |
|---|---|---|
| dow_sin | Cyclic weekday phase without raw integer ordering | Mainly next-day context; no established weekly predictive effect |
| dow_cos | Completes weekday phase together with sine | A single harmonic restricts the shape representable by a linear model |
| lag_1 | Latest daily level/shock | One-day noise |
| lag_7 | Matching weekday of first target day | Raw lag dependence is not proof of weekly seasonality |
| lag_14 | Older matching-weekday and level context | Correlation with shorter lags and rolling summaries |
| rolling_mean_7 | Responsive recent demand level | Can lag sudden changes |
| rolling_std_7 | Recent dispersion | Short-window noise; not forecast uncertainty |
| rolling_mean_14 | Smoother recent level | Overlap with the 7-day mean and slower response |
| rolling_std_14 | Two-week dispersion | Trend contributes to dispersion |
| rolling_mean_28 | Broader historical level reference | Slower response at turning points |
| rolling_std_28 | Broader historical dispersion reference | Mixes changing level with noise; not calibrated forecast uncertainty |
| rolling_slope_14 | Ordered-history direction over the recent fortnight | Noise and direction that may not persist |

### 5.2 Redundancy and exclusion rationale

KEEP/EXCLUDE decisions apply to this research design and simulated dataset;
EXCLUDE does not mean a feature is universally useless.

- lag_28 is one old daily observation, not a four-week summary. The accepted
  broader context is supplied by rolling_mean_28 and rolling_std_28.
- trend_week_difference equals 2(M_7-M_14), and trend_fortnight_difference equals
  2(M_14-M_28). Both are derived from retained rolling means.
- lag_difference_7_14 is exactly lag_7-lag_14.
- rolling_cv_14 and volatility_ratio_7_14 transform retained mean/std values and
  add small/zero-denominator stability and eligibility issues.
- Medians and rolling_mad_14 are excluded to avoid additional centre/dispersion
  summaries without a demonstrated need. No outlier-removal mechanism is assumed.
- Raw day_of_week is excluded because the selected representation is the
  weekday sine/cosine pair; weekday dummies are not combined with that pair.
- Month, quarter and their cyclic alternatives are excluded because one
  simulated year does not establish recurring annual effects.
- Other growth, interactions and contextual expansions are outside the exact
  accepted set; no feature-search dimension is implied.

Derived differences do not add historical information, although they can make
comparisons easier for tree splits. With Ridge, redundant columns can alter
regularisation geometry. Ratios are nonlinear representations, not universally
useless transformations. Their exclusion is a compactness and stability decision,
not an empirical claim about their scores.

The three mean/std scales overlap intentionally. The 28-day summaries provide
a smoother historical reference against recent levels during the documented
within-year rises and declines. They are not retained merely because a forecast
horizon is 28 days; historical windows and future horizons have distinct roles.
Their incremental predictive value remains unproven.

rolling_slope_14 retains the order of observations within its window, which is
not generally recoverable from the retained means/stds and three individual lags.
It is the single accepted additional trend descriptor, not automatic growth
extrapolation or permission to append further trend transformations.

### 5.3 Horizon relevance and limitations

| Horizon | Role of the common retained features | Limitation |
|---|---|---|
| 1 day | Recency, recent level, dispersion, local direction and weekday phase | Single-day noise and unobserved operational effects |
| 7 days | Recent level and direction context for direct cumulative demand | Every weekday occurs once; calendar phase does not change counts |
| 14 days | Recent/broader level and direction context | Every weekday occurs twice; changes may persist or reverse |
| 28 days | Recent and broader historical context for direct cumulative demand | Every weekday occurs four times; no exact calendar-month interpretation |

The weekday pair is retained across all four horizons by explicit human
acceptance of the common pipeline. It represents first-target-day phase, not
changing weekday composition. Its cumulative-horizon predictive benefit is not
claimed. All weekday-count features are EXCLUDE, including the 1-day indicator
alternative.

The saved EDA reports level lag-correlation medians near 0.640/0.642/0.633/0.592
for lags 1/7/14/28, with differenced lag-7 median near 0.003. Changing demand
levels may explain much of this dependence; it does not establish a dominant
weekly seasonal effect or choose features.

No square-root-of-horizon uncertainty scaling follows from rolling std:
cumulative variance depends on individual variances and cross-day covariances.
A separate human-reviewed forecast-error/uncertainty methodology is still needed.

### 5.4 Research-path alignment

The current preferred research path is forecast performance → downstream origin
reorder-threshold exposure → limited robustness and human-review analysis. This
review supports that direction without changing group hypotheses or approving
cross-component methods.

#### Adequate current foundations

The daily native grain, origin-safe demand memory and recent rolling means produce
forecast inputs at the same identity and temporal scope as the later exposure
analysis. Their use is defensible without adding inventory variables to a demand
model. Keeping all candidate models' predictions preserves later paired comparison.

#### Generic features and useful refinements

The historical integer-calendar catalogue is superseded by the frozen set.
The research contribution need not be a unique feature-engineering invention;
the retained scales and single slope have explicit roles, while unnecessary
calendar and summary expansions are excluded.

Historical [demand EDA](../reports/demand-eda.md) reports changing within-year
levels, no uniquely dominant weekly lag after differencing, and descriptive
promotion association. It supports reviewing level/trend representation and
availability, not adding a large feature catalogue or claiming annual recurrence.
The retained slope provides one origin-time direction descriptor for interpreting
longer-horizon forecasts. Whether it improves accuracy is not established here.

#### Connection to downstream exposure

DR-012's documented interpretation uses $B_o=I_o-R_o$. For origin buffers above
zero, forecast-added exposure depends on whether forecast cumulative demand
$F_{o,h}$ reaches or exceeds that buffer. Holding inventory evidence fixed, a small
forecast change near the boundary can change the conclusion even if aggregate
WAPE changes little. Therefore origin alignment, bias, direction and the exact
cumulative target matter more than multiplying the number of features.

The [DR-012 file](decisions/DR-012-inventory-risk-replenishment-methodology.md)
remains “Proposed for group approval” and is used only as the current documented
downstream alignment reference. Merge presence does not make it an accepted
inventory-methodology baseline or resolve its remaining snapshot, processing or
cross-component protocol dependencies. Its formula and decisions remain unchanged.

Keep forecasting selection under DR-006. Selecting demand features to maximise
retrospective inventory agreement would introduce a different objective and
risk circularly optimising the primary forecast-to-decision comparison. The
human-reviewed common feature set frozen across learned candidates makes that
later comparison more interpretable. A feature ablation would be a separate
experiment; none is approved within the fixed hyperparameter grids or by this freeze.

#### Robustness and human review

Historical std, CV, slopes and volatility ratios can explain origin-time demand
context. They are not forecast intervals, error probabilities, final demand-regime
labels or numerical human-review triggers. Future C/D work needs approved
uncertainty estimation, evaluation and review criteria. Retrospective errors and
realised margins must not be used as prospective review inputs. No feature proposal
establishes improved stockout prevention, ordering, trust or managerial decisions.

## 6. Final KEEP / EXCLUDE decisions

Section 3 is the sole authoritative ordered KEEP list. Every entry below is
EXCLUDE from the frozen predictor vector; historical formulas above are
calculation references, not executable alternatives.

| Group | EXCLUDE feature/input | Reason / boundary |
|---|---|---|
| Calendar | day_of_week | Replaced by the selected weekday sine/cosine pair |
| Calendar | Weekday dummy variables, including dow_mon through dow_sat | No second weekday representation |
| Calendar | month, quarter, month_sin, month_cos | One simulated year; recurring annual effects not established |
| Calendar | week_of_year | DR-003 exclusion; no repeated year-over-year numbered weeks |
| Calendar | year | Constant 2024 |
| Calendar | Annual day-of-year cyclic features | No established annual recurrence; no leap-year convention introduced |
| Calendar | Holiday indicators | No verified retail geography/holiday mechanism |
| Calendar | target_weekday_count_h_k | Constant counts at 7/14/28; duplicates weekday indicators at 1 day |
| Calendar | weekday_x_mean_7 | Arbitrary Monday interaction |
| Calendar | Raw numeric Date | Date is an alignment/calendar source, not a numeric predictor |
| Lag/statistical | lag_28 | One older daily observation, not a four-week summary |
| Lag/statistical | rolling_median_7, rolling_median_14, rolling_median_28 | Avoid additional centre summaries |
| Lag/statistical | rolling_cv_14 | Mean/std transformation with denominator-stability issues |
| Lag/statistical | rolling_mad_14 | Additional dispersion summary without demonstrated need |
| Lag/statistical | volatility_ratio_7_14 | Std transformation with denominator-stability issues |
| Lag/statistical | 30-day rolling summaries | No additional nearby window beyond retained 7/14/28 scales |
| Trend/change | trend_week_difference | Derived exactly from retained means |
| Trend/change | trend_week_growth | Additional change representation with denominator issues |
| Trend/change | trend_fortnight_difference | Derived exactly from retained means |
| Trend/change | lag_difference_7_14 | Derived directly from retained lag_7 and lag_14 |
| Trend/change | origin_weekday_change | Additional single-day change descriptor; requires lag-8 alignment |
| Trend/change | Any unspecified extra growth/decline indicator | Outside the exact frozen contract |
| Context/exogenous | promotion_share_7 | Historical flag availability/carryover not established |
| Context/exogenous | planned_promotion_days_h | No accepted origin-known future-plan availability contract |
| Context/exogenous | price_change_7 | Effective/publication timing and relevance not established |
| Context/exogenous | promotion_origin_x_mean_7 | Unestablished flag availability and extra interaction |
| Context/exogenous | Raw Promotion_Flag, raw Unit_Price | Do not assume future availability from dated source rows |
| Context/exogenous | Supplier_ID, Region as predictors | Supplier is series-level metadata without an independent demand justification; Region is not stable warehouse geography |
| Context/exogenous | SKU × warehouse interaction ID | Two accepted categorical identities already specify the pair; no explicit interaction predictor is accepted |
| Context/exogenous | inventory_buffer | Downstream threshold context, outside forecasting |
| Context/exogenous | Inventory_Level, Reorder_Point, Supplier_Lead_Time_Days, Order_Quantity, Unit_Cost | Downstream operational/inventory/replenishment/cost boundary |
| Prohibited/leakage-sensitive | Demand_Forecast and any derivative | Reference-only; unknown issuance and source construction |
| Prohibited/leakage-sensitive | Stockout_Flag | Constant zero; neither useful predictor nor stockout ground truth |
| Prohibited/leakage-sensitive | Future/target-period Units_Sold; cumulative target labels as predictors | Observed outcomes are labels, not prospective features |
| Prohibited/leakage-sensitive | Unshifted or centred rolling demand; future-filled demand history | Unavailable target/future information |
| Prohibited/leakage-sensitive | Realised future promotions, prices or inventory | Hindsight operational information |
| Prohibited/leakage-sensitive | Retrospective forecast errors; retrospective threshold-crossing outputs | Outcome contamination of prospective inputs |
| Prohibited/leakage-sensitive | Full-year fitted demand normalisations; target encodings using observations beyond the fitting cutoff | Leakage from observations unavailable at fitting time |
| Prohibited/leakage-sensitive | Unapproved raw operational composites | Includes price-minus-cost, price/cost, lead-time-demand products and arbitrary combinations |

Historical Units_Sold remains the source for accepted features and observed
labels. Excluding future values as predictors does not remove evaluation labels.
Date, SKU_ID and Warehouse_ID remain mandatory alignment/grouping fields.
SKU_ID and Warehouse_ID additionally belong to the list of fourteen conceptual
predictors as categorical context; Date does not. Demand_Forecast remains reference-only
with any separate benchmark use subject to leakage-safe human approval. No
additional engineered features are currently required or accepted, including
additional rolling windows beyond 7/14/28 days.

### 6.1 Historical review options — superseded

Earlier Options A/B/C were reviewed alternatives: A retained the historical
13 columns, B retained eight historical columns, and C proposed ten columns
including the paired weekday encoding and slope. None is the final contract of
fourteen conceptual predictors. The subsequent contract containing only twelve
engineered predictors also excluded identities and is now superseded by the
human-approved architecture of two context and twelve engineered predictors in
Section 3. These earlier
options/contracts are provenance, not current alternatives, an ablation plan
or experiment authority.

## 7. Minimum history and training-row completeness

The minimum predictor-history requirement is **28 complete consecutive daily
observations per SKU_ID + Warehouse_ID**, ending at forecast origin o. It is
driven by the retained rolling_mean_28 and rolling_std_28, not by excluded lag_28.
The same history requirement applies to all learned models and all horizons.

Twenty-eight days is an input-history requirement, not the total span required
for a labelled training example. A complete training row additionally requires
its whole horizon outcome to be observed by the fitting cutoff. Its own inputs
must use only history available at its own origin.

For N consecutive observed dates, eligibility before other exclusions is
N - 28 - h + 1 rows per series. In the 91-day initial training interval:

| Horizon h | Complete training rows per series |
|---|---:|
| 1 | 63 |
| 7 | 57 |
| 14 | 50 |
| 28 | 36 |

These are feasibility counts, not a claim of model adequacy or independent
samples. Overlapping cumulative labels create dependence. Missing required
demand makes a window or target unavailable; never use a partial window, zero
fill, future fill or shortened cumulative label to manufacture completeness.
The accepted complete-window definitions introduce no imputation policy.

## 8. Human approval and execution boundaries

The human reviewer has accepted the final membership and order of fourteen
conceptual predictors, categorical SKU/warehouse encoding policy, twelve engineered features,
common use across horizons/models, retained 28-day summaries, fourteen-day slope
and minimum predictor history. The contract is **frozen for implementation** of
the feature/preprocessing pipeline. This document update implements neither pipeline.

| Item | Authority / boundary |
|---|---|
| Final feature contract | Human-reviewed and frozen under the Issue #57 feature-freeze decision |
| Feature/preprocessing-pipeline implementation | Authorised by the feature freeze; not performed by this documentation task |
| Source/test acceptance | Issue #62 accepted the earlier contract; common primary alignment is implemented and Issue #89 orchestration was merged through PR #90. Storage migration needs separate acceptance |
| Model training or fitting | Not authorised |
| Hyperparameter tuning or validation scoring | Not authorised |
| Feature ablation | Not authorised |
| Final evaluation or experiment execution | Not authorised |
| Revised executable experiment protocol | Issue #65 scientific protocol is frozen/approved; Issue #94 reconciles operational documentation only |
| 28-day Naive / Seasonal Naive extensions | Formulas are approved in the frozen protocol; specific execution and downstream use remain separate |
| Current forecasting design | Human-approved as recorded by the project owner; no separate supervisor approval asserted |
| Downstream methods | Separate group/component-owner review boundaries remain |
| Earlier Issue #52 evidence | Historical methodology and approval provenance preserved |

Any change to membership, conceptual feature order, categorical encoding policy,
formulas, windows, completeness, calendar convention or horizon policy requires
a separate human-reviewed contract revision. Do not tune feature inclusion with model hyperparameters,
select features from old scores or infer run authority from this freeze.

AGENTS.md Sections 17–19 still control experiment execution. A reviewed feature
pipeline alone does not authorise a training, tuning, scoring, ablation or final-evaluation
command. The revised final evaluation interval stays reserved from subsequent
selection and fitting, with prior validation/EDA exposure disclosed.

## 9. Implementation mapping and current repository status

### 9.1 Current source and tests

Issue #62 is merged (PR #64) and implements the Issue #57 conceptual feature contract and earlier preprocessing representation. It does not implement the Issue #66 primary comparison.

| File | Current observed behaviour | Later alignment boundary |
|---|---|---|
| src/forecasting/features.py | Twelve frozen numerical calculations plus two context identities; 28-day completeness, fixed-origin masking and ordered conceptual vector | Preserve formulas/order and origin-only history; no new feature is required |
| src/forecasting/targets.py | Complete direct 1/7/14/28 labels separated from predictors and bounded by outcome intervals | Preserve targets, grouping and date boundaries |
| src/forecasting/validation.py | Four revised folds and revised final interval; no fitting/scoring | Preserve dates and final-evaluation protection |
| src/forecasting/preprocessing.py | Common primary one-hot representation; Ridge numerical scaling; training-only vocabularies and unknown-ID rejection; versioned fitted-state persistence | Implemented; Issue #89 operational changes were merged through PR #90 |
| tests/test_forecasting_features.py | Synthetic formula, completeness, order, isolation, origin, target and boundary coverage for Issue #62 | Preserve numerical/temporal contract coverage; no estimator fitting authorised here |
| tests/test_forecasting_preprocessing.py | Synthetic common primary representation and identical-matrix checks, mapping, Ridge scaling, training-only fitting, unknown-ID rejection, origin reuse and fitted-state persistence round-trip checks | Implemented/tested; Issue #89 operational changes were merged through PR #90; validation-run provenance and evidence availability are recorded in the methodology revision record |

These tests do not establish forecasting accuracy or acceptance of revised model execution. **Historical Issue #66 provenance:** that documentation-only revision ran static checks without source/test/dependency changes, estimator fitting or experiments. The current implementation includes the tested common primary representation and Issue #89 orchestration work, which was merged through PR #90; validation-run provenance and evidence availability are recorded in the methodology revision record.

For historical first-target row t, predictors end at t-1 and labels cover t,...,t+h-1. At fixed origin o, use t=o+1 with history_end=o and reuse the same conceptual and primary physical vector across all horizons. Training outcomes must be complete by their fitting cutoff. The later caller must check labels before fitting preprocessing; the feature-only preprocessor does not verify outcome values. See [DR-013](decisions/DR-013-matched-gradient-boosting-comparison.md) for model roles and [Issue #65](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/65) for the frozen/approved protocol.

### 9.2 Completed companion-document alignment and provenance

The September 29 documentation/provenance alignment has been completed and human-reviewed under Issue #61. It records the human-reviewed Issue #57 feature-freeze decision in the research design, workflows, dataset roles, decision-record status notes and member overviews. Original decision dates, historical catalogues and descriptive results remain provenance. [The central revision record](forecasting-methodology-revision.md) distinguishes frozen forecasting choices, including the protocol and 28-day baseline formulas, from accepted Issue #89 implementation, run-specific authorization and downstream approvals.

The archived Issue #52 protocol retains its original thirteen-feature methodology; its local artifacts and the matching historical runner/source version required for reproduction are documented in the central record. It must not be rerun or relabelled as evidence for this contract. The revised executable protocol is already frozen/approved under Issue #65; Issue #89 was merged through PR #90; future architecture acceptance and specific execution authorization remain separate.

Issue #62 subsequently implemented the accepted calculations in reusable source under the existing module names. Source/tests remain unchanged by Issue #66. Common primary preprocessing/model interfaces and tests are already implemented, and Issue #65 is frozen/approved. Issue #89 operational changes were merged through PR #90; specific execution authorization remains separate; validation-run provenance and evidence availability are recorded in the methodology revision record. No experiment execution follows automatically.

## Appendix A — Detailed mathematical notation and date alignment

All demand calculations are within one fixed SKU–warehouse series.

| Symbol | Meaning |
|---|---|
| $o$ | Forecast origin, the last day with observed demand available to the forecaster |
| $t=o+1$ | First target day; the existing code's Date |
| $y_u$ | Units_Sold on day $u$ in the same series |
| $d(t)$ | Monday=0 through Sunday=6 |
| $m(t)$ | Month 1 through 12 |
| $Y_{o,h}$ | Observed cumulative target for $h\in\{1,7,14,28\}$ |
| $L_k(t)$ | Past demand at the specified lag |
| $M_w(o)$, $S_w(o)$ | Retained mean and sample standard deviation for complete windows $w\in\{7,14,28\}$ |
| $Q_w(o)$ | Excluded historical median definition |
| $P_w(o)$ | Historical preceding-window mean used only in excluded change definitions |

$$
Y_{o,h}=\sum_{j=1}^{h}y_{o+j},
\qquad h\in\{1,7,14,28\}.
$$

$$
L_k(t)=y_{t-k}=y_{o-k+1}.
$$

$$
M_w(o)=\frac1w\sum_{j=0}^{w-1}y_{o-j}
$$

$$
P_w(o)=\frac1w\sum_{j=0}^{w-1}y_{o-w-j}.
$$

$$
Q_w(o)=\operatorname{median}\{y_o,\ldots,y_{o-w+1}\}.
$$

For an even window, average the two middle values.

$$
S_w(o)=
\sqrt{\frac{1}{w-1}\sum_{j=0}^{w-1}\left(y_{o-j}-M_w(o)\right)^2}.
$$

Full windows require every daily observation, not just $w$ arbitrary rows.
Missing required values remain unavailable. The active predictor set is frozen
in Section 3; historical excluded formulas do not authorise additional features.
No epsilon, clipping or missing-value fill is approved.

**Off-by-one example:** lag_7 predicts the weekday of $t$ using $y_{t-7}$.
At origin $o$, that value is six days before $o$. A comparison of the origin
with seven days earlier is:

$$
y_o-y_{o-7}=L_1(t)-L_8(t).
$$

It is not $\text{lag}_1-\text{lag}_7$. For every cumulative horizon, history
still ends at $o$; it must not advance to $t+6$, $t+13$ or $t+27$ to obtain
supposedly available lag inputs.

## Appendix B — Evidence and sources

Repository evidence:

- [Dataset contract](dataset.md), [research design](research-design.md),
  [forecasting workflow](workflows/demand-forecasting.md) and
  [Chathuranga's overview](team/chathuranga/group-project-overview.md).
- [DR-003](decisions/DR-003-forecasting-feature-engineering-baseline.md),
  [DR-004](decisions/DR-004-forecast-horizons.md),
  [DR-008](decisions/DR-008-multi-step-forecasting-strategy.md),
  [DR-006](decisions/DR-006-forecasting-metrics-and-model-selection.md) and
  [DR-012](decisions/DR-012-inventory-risk-replenishment-methodology.md).
- [Historical demand EDA](../reports/demand-eda.md): level lag-correlation medians
  at lags 1/7/14/28 are approximately 0.640/0.642/0.633/0.592; differenced lag-7
  median is approximately 0.003. This is descriptive evidence, not feature selection.
- [Temporal/inventory alignment](../reports/temporal-demand-profile.md): native
  grain and promotion disagreement; no new profiling was performed.
- [Feature source](../src/forecasting/features.py), [target source](../src/forecasting/targets.py),
  [feature tests](../tests/test_forecasting_features.py) and [AGENTS.md](../AGENTS.md).

Primary external guidance checked on 2026-09-28:

- **E2:** scikit-learn, [Time-related feature engineering](https://scikit-learn.org/stable/auto_examples/applications/plot_cyclical_feature_engineering.html).
  Demonstrates why ordinal calendars can be limiting and how paired trigonometric
  encoding changes representation. It does not prove superiority for this project.
- **E3:** scikit-learn, [Lagged features for time series forecasting](https://scikit-learn.org/stable/auto_examples/applications/plot_time_series_lagged_features.html).
  Demonstrates lagged and shifted historical summaries with chronological evaluation.
  It does not validate the exact daily windows or the slope/ratio definitions here.
- **E2/E4:** Hyndman and Athanasopoulos, [FPP3 Section 7.4, Some useful predictors](https://otexts.com/fpp3/useful-predictors.html).
  Supports seasonal dummy representation and lagged external effects as general ideas;
  project-specific calendars and promotion mechanisms still need justification.
- **E4/E5:** Hyndman and Athanasopoulos, [FPP3 Section 7.6, Forecasting with regression](https://otexts.com/fpp3/forecasting-regression.html).
  Distinguishes available predictors from hindsight and discusses lagged or scenario
  inputs. A scenario assumption cannot manufacture an observed plan-availability contract.
- Hyndman and Athanasopoulos, [FPP3 Section 2.3, Time series patterns](https://otexts.com/fpp3/tspatterns.html).
  Distinguishes trend and fixed-period seasonality. One observed annual trajectory
  alone does not establish a recurring annual pattern in this simulated dataset.

Exact local-window and interaction formulas in this document are transparent
definitions with explicit KEEP/EXCLUDE decisions. No cited source is presented as having tested them on this
dataset. Existing project literature includes retail forecasting and promotional
studies in [references.md](references.md); listing a paper there does not verify
an exact feature formula or its origin-time availability. No reference register
or Decision Record was changed.
