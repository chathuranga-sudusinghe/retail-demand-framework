# DR-005 — Forecast Validation Design

> **Current status cross-reference — Issue #94:** [The frozen protocol](../protocol.md) resolves prior pending supportive settings, baseline and runtime decisions. Issue #89 was merged through PR #90. [Runner operations](../forecasting-runner.md) distinguish approved storage policy from unchanged runtime behavior. Original decision/development wording below remains historical provenance; this status note changes no decision or authorizes any run.

**Original decision date:** 2026-09-22
**Original decision status:** Accepted for the earlier 1/7/14-day baseline
**Revision date:** 2026-09-28
**Revision status:** Current forecasting design human-approved; experiment execution NOT authorised
**Documentation alignment:** 2026-09-29, on the project owner's explicit instruction
**Revision owner:** Chathuranga
**Group-level acceptance:** Pending; separate from the project owner's current forecasting approval
**Related issue:** [#31 — Define expanding-window forecast validation design](https://github.com/chathuranga-sudusinghe/retail-demand-framework/issues/31)
**Approval provenance:** The original design was approved through Issue #31. The project owner supplied the horizon/fold amendment on 2026-09-28 and explicitly confirmed the current forecasting position for this September 29 alignment. Implementation/protocol acceptance and separate group-level matters remain gated. Separate supervisor approval is not asserted.

## Context and revision

DR-002 retains `SKU_ID + Warehouse_ID + Date` and `Units_Sold`. Revised DR-004
adds 28-day cumulative demand; DR-008's direct strategy remains. The verified
source spans 365 complete daily dates from 2024-01-01 to 2024-12-30 for 250 series.
The earlier 14-day fold design cannot accommodate a complete 28-day outcome.
Previous scores were not used to choose this amendment. Historical evidence is
[demand EDA](../../reports/demand-eda.md), its saved notebook and the temporal profile.
[Revision and provenance](../forecasting-methodology-revision.md) records the
current human-approved forecasting scope, frozen feature contract and separate remaining approval boundaries.

## Current human-approved forecasting design

Use four expanding-window chronological folds, with one fixed forecast origin
at the training cutoff for every SKU–warehouse and horizon. This is the project's
selected evaluation protocol. A 28-day validation window could theoretically
support other evaluation-origin designs, but this project intentionally uses one
fixed origin per fold. Realised demand inside the validation window must not
update that fixed-origin forecast. All dates are inclusive and calendar-day counts
precede feature warm-up and complete-target exclusions.

| Fold | Training start | Training end / origin | Training days | Validation start | Validation end | Validation days |
|---|---|---|---:|---|---|---:|
| 1 | 2024-01-01 | 2024-03-31 | 91 | 2024-04-01 | 2024-04-28 | 28 |
| 2 | 2024-01-01 | 2024-06-30 | 182 | 2024-07-01 | 2024-07-28 | 28 |
| 3 | 2024-01-01 | 2024-09-30 | 274 | 2024-10-01 | 2024-10-28 | 28 |
| 4 | 2024-01-01 | 2024-11-04 | 309 | 2024-11-05 | 2024-12-02 | 28 |

**Revised final evaluation:** 2024-12-03 to 2024-12-30 inclusive, 28 days;
forecast origin 2024-12-02. No December 31 observation is invented.

### Evidence and the three-fold alternative

Historical EDA reports March/April means of 29.8834/29.8391, July 17.4084,
September/October 10.1739/10.2708 and November 13.0807 units per native observation.
The saved notebook's monthly/quarterly tables and retrospective daily chart
support high levels, decline, low demand and recovery within this simulated year;
they do not establish recurring annual seasonality or formal demand regimes.

Three folds were considered and remain methodologically feasible: April high
demand, July decline and October low demand. They omit separate recovery validation.
**Four folds provide broader validation evidence across distinct observed temporal
demand conditions while preserving expanding-window chronological evaluation.**
The recovery-period evidence in November–early December was considered useful
for this one-year dataset. November 5 is the latest complete 28-day placement
before the revised final interval, not an EDA-established change point.

Four is a project-specific human choice, not statistically optimal. Expanding
folds share training history and are not independent replicates. More folds
increase computational workload and validation-selection exposure; validation
folds do not make models learn more patterns. Training length and evaluation
conditions change together, so differences cannot automatically be attributed
to demand conditions alone. Fold 3/4 origins are only 35 days apart, with seven
unscored days between their validation windows.

### Target completeness, warm-up and non-overlap

At each cutoff, next-day and cumulative 7-, 14- and 28-day targets fit completely
inside its 28-day evaluation window. A window is not a collection of 28 forecast
origins: the current protocol uses one origin and one target per series/horizon.
All training labels must end by their training cutoff. Features use only history
available at the row's own origin; scalers/learned transformations fit only training
rows. Never use realised future demand or target labels as predictors.

The four validation windows do not overlap each other or the revised final interval.
Earlier validation outcomes may enter later training only once historical to the
later cutoff. Unscored gaps may enter later training; no final-evaluation observations
may enter fitting or subsequent selection. Missing/incomplete outcomes remain
unavailable, not zero, shortened labels or reasons to borrow later dates.

A 28-day feature warm-up is feasible even in the initial 91-day history. With a
complete 28-day look-back and horizon h, eligibility is N − 28 − h + 1 rows per
series before other exclusions: 63/57/50/36 for h=1/7/14/28 in fold 1. This is
feasibility, not a guarantee of model adequacy. The frozen feature contract requires this complete 28-day history for every learned model and horizon.

### Final-evaluation provenance and protection

The revised 28-day final evaluation window is reserved from all subsequent
feature, model and hyperparameter decisions and fitting. However, December 3–16
had prior validation exposure under the earlier 14-day methodology, so the revised
window is not fully unseen from the historical research process. Full-year
historical EDA also inspected those dates. Final forecasting results must not feed
back into selection, and this prior exposure must be disclosed in reporting.

## Limitations and open decisions

The dataset is simulated and contains one year. Four origins and one final interval
cannot establish annual generalisation, recurring seasonal regimes or real-retailer
effectiveness. Prior validation exposure limits the independence of the revised
final evaluation. Overlapping cumulative training labels also create dependence.
WAPE can reflect changing demand denominators, so retain absolute errors and Bias.

The feature contract is frozen with 28 complete consecutive history days. Proposed 28-day baseline approval, implementation/test acceptance, the revised executable protocol, uncertainty, formal demand conditions/statistical tests and downstream/component-owner approval remain separate.
No change to model families, metric equations, grids, inventory rules, ownership
or research hypotheses is made by this validation amendment.

## Historical September 22 schedule — superseded, retained as provenance

The following schedule and holdout wording describe the earlier 1/7/14-day design
only. They are not current boundaries and do not describe an unseen revised test.

### Exact fold schedule

All dates are inclusive. Training-day counts refer to calendar observations per native series, before any future approved feature-history requirements reduce usable fitting rows.

| Fold | Training start | Training end / origin cutoff | Training days | Validation start | Validation end | Validation days |
| --- | --- | --- | ---: | --- | --- | ---: |
| 1 | 2024-01-01 | 2024-03-31 | 91 | 2024-04-01 | 2024-04-14 | 14 |
| 2 | 2024-01-01 | 2024-06-30 | 182 | 2024-07-01 | 2024-07-14 | 14 |
| 3 | 2024-01-01 | 2024-09-30 | 274 | 2024-10-01 | 2024-10-14 | 14 |
| 4 | 2024-01-01 | 2024-12-02 | 337 | 2024-12-03 | 2024-12-16 | 14 |

**Final model-evaluation holdout:** 2024-12-17 to 2024-12-30 inclusive, exactly **14 calendar days**.

Fold 4 validation ends on 2024-12-16; the holdout begins the next day. They do not overlap. All validation windows and the holdout lie within the observed dataset range.

Earlier validation observations can become historical training observations in later folds, as the schedule specifies. This is part of expanding-window evaluation: it does not permit using those observations when fitting or forecasting an earlier fold. Periods between validation windows remain part of subsequent training histories; validation windows are not a partition of the whole year.
