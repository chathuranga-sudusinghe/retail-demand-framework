"""Descriptive EDA at Date + SKU_ID + Warehouse_ID; no modelling decisions.

Run from the repository root:
    python -m src.analysis.demand_exploratory_analysis --input data/raw/supply_chain_dataset1.csv
Detailed CSV tables are written only beneath data/processed/.
Historical EDA provenance: original descriptive computations and results are
preserved. The frozen fourteen-predictor specification and current methodology
record govern forecasting; this module does not authorise models or experiments.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, cast

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.analysis.inventory_alignment_analysis import profile_native_grain
from src.data.data_cleaning import (
    KEY, build_validated_dataset, load_raw_source, scoped_source_receipt,
    quality_tables as validation_quality_tables,
)

ROOT = Path(__file__).resolve().parents[2]
LAGS = (1, 7, 14, 28)


def historical_baseline_comparison(validated: pd.DataFrame) -> pd.DataFrame:
    """Compare descriptive observations with the documented historical profile.

    A partial authorized scope can validate successfully without matching these
    historical facts. This comparison is research context, never a cleaning rule.
    """
    observed = [len(validated), len(validated.columns), validated.Date.nunique(), validated.SKU_ID.nunique(),
                validated.Warehouse_ID.nunique(), validated.Date.min().date().isoformat(), validated.Date.max().date().isoformat(),
                validated.Supplier_ID.nunique(), validated.Region.nunique(), int(validated.Stockout_Flag.eq(0).sum()),
                int(validated.Order_Quantity.gt(0).sum())]
    baseline = pd.DataFrame({"check": ["rows", "columns", "dates", "skus", "warehouses", "date_min", "date_max", "suppliers", "regions", "stockout_zero_rows", "nonzero_order_rows"],
                             "documented": [91250, 15, 365, 50, 5, "2024-01-01", "2024-12-30", 10, 4, 91250, 5027], "observed": observed})
    baseline["matches"] = baseline.documented.eq(baseline.observed)
    return baseline


def quality_tables(validated: pd.DataFrame, audit: dict[str, Any]) -> dict[str, pd.DataFrame]:
    """Combine shared validation evidence with analysis-local historical context."""
    return {**validation_quality_tables(validated, audit),
            "baseline": historical_baseline_comparison(validated)}


def summarize(df: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    """Units per native observation; totals explicitly aggregate for description."""
    return df.groupby(groups, observed=True, sort=True).agg(
        rows=("Units_Sold", "size"), days=("Date", "nunique"),
        total=("Units_Sold", "sum"), mean=("Units_Sold", "mean"),
        median=("Units_Sold", "median"), std=("Units_Sold", "std"),
        zero_share=("Units_Sold", lambda s: s.eq(0).mean()),
        promotion_share=("Promotion_Flag", "mean"),
    ).reset_index()


def lag_correlation(values: pd.Series, lag: int) -> float:
    """Pearson correlation with calendar-lagged values; undefined is NaN."""
    pair = pd.concat([values, values.shift(lag)], axis=1).dropna()
    if len(pair) < 3 or (pair.nunique() < 2).any():
        return float("nan")
    return float(pair.iloc[:, 0].corr(pair.iloc[:, 1]))


def analyze_demand(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Analyze a shared validated/typed DataFrame; never clean source records."""
    df = df[KEY + ["Units_Sold", "Promotion_Flag"]].copy()
    df["month"] = df.Date.dt.to_period("M").astype(str)
    df["quarter"] = df.Date.dt.to_period("Q").astype(str)
    daily = summarize(df, ["Date"])
    for window in (7, 14):
        # Includes the displayed day: retrospective EDA, never a model feature.
        daily[f"rolling_mean_{window}"] = daily.total.rolling(window, min_periods=window).mean()
    daily["change"] = daily.total.diff()
    daily["change_pct"] = daily.total.div(daily.total.shift().replace(0, np.nan)).sub(1).mul(100)
    monthly = summarize(df, ["month"])
    monthly["calendar_days"] = pd.PeriodIndex(monthly.month, freq="M").days_in_month
    monthly["mean_daily_total"] = monthly.total / monthly.days
    for c in ("total", "mean"):
        monthly[f"{c}_change_pct"] = monthly[c].div(monthly[c].shift().replace(0, np.nan)).sub(1).mul(100)
    tables = {"daily": daily, "monthly": monthly, "quarterly": summarize(df, ["quarter"]),
              "distribution": df.Units_Sold.describe(percentiles=[.01, .05, .25, .5, .75, .95, .99]).rename("Units_Sold").to_frame().reset_index(names="statistic"),
              "promotion": summarize(df, ["Promotion_Flag"]),
              "promotion_monthly": summarize(df, ["month", "Promotion_Flag"]),
              "promotion_series": summarize(df, KEY[1:] + ["Promotion_Flag"]),
              "series": summarize(df, KEY[1:])}
    tables["series"]["coefficient_of_variation"] = tables["series"]["std"] / tables["series"]["mean"].replace(0, np.nan)
    for group, label in [("SKU_ID", "sku"), ("Warehouse_ID", "warehouse")]:
        m = summarize(df, [group, "month"])
        overall = df.groupby(group).Units_Sold.mean()
        m["mean_index"] = m["mean"] / m[group].map(overall).replace(0, np.nan)
        tables[f"{label}_monthly"] = m
        matrix = m.pivot(index=group, columns="month", values="mean")
        pattern = matrix.T.corr()
        upper = pattern.to_numpy()[np.triu_indices(len(pattern), k=1)]
        tables[f"{label}_pattern_similarity"] = pd.Series(upper).describe().rename("pairwise_monthly_correlation").to_frame().reset_index(names="statistic")
        heterogeneity = m.groupby(group).agg(min_month_mean=("mean", "min"), max_month_mean=("mean", "max"))
        heterogeneity["max_min_ratio"] = heterogeneity.max_month_mean / heterogeneity.min_month_mean.replace(0, np.nan)
        tables[f"{label}_variation"] = heterogeneity.reset_index()
    lag_rows = []
    for (sku, warehouse), frame in df.groupby(KEY[1:]):
        s = frame.set_index("Date").Units_Sold.sort_index().asfreq("D")
        for lag in LAGS:
            lag_rows.append({"SKU_ID": sku, "Warehouse_ID": warehouse, "lag_days": lag,
                             "correlation": lag_correlation(s, lag),
                             "differenced_correlation": lag_correlation(s.diff(), lag)})
    tables["lags"] = pd.DataFrame(lag_rows)
    tables["lag_summary"] = tables["lags"].groupby("lag_days").agg(
        defined_series=("correlation", "count"), median=("correlation", "median"),
        q25=("correlation", lambda s: s.quantile(.25)), q75=("correlation", lambda s: s.quantile(.75)),
        min=("correlation", "min"), max=("correlation", "max"),
        differenced_median=("differenced_correlation", "median")).reset_index()
    tables["extremes"] = pd.concat([daily.nlargest(5, "total").assign(kind="highest daily totals"),
                                          daily.nsmallest(5, "total").assign(kind="lowest daily totals")], ignore_index=True)
    tables["largest_changes"] = daily.loc[daily.change.abs().nlargest(10).index].sort_values("Date")
    return tables


def make_figures(df: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> dict[str, plt.Figure]:
    """Return figures without writing them; notebook displays then saves each."""
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                         "figure.dpi": 110, "axes.grid": True, "grid.alpha": .18})
    figures = {}
    daily, monthly = tables["daily"], tables["monthly"]
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), layout="constrained")
    axes[0].plot(daily.Date, daily.total, color="#23688c", lw=1, label="Daily total")
    for w, color, style in [(7, "#cf6819", "-"), (14, "#553b91", "--")]:
        axes[0].plot(daily.Date, daily[f"rolling_mean_{w}"], color=color, ls=style, label=f"{w}-day trailing mean")
    axes[0].set(title="Daily demand and retrospective smoothing", ylabel="Units / day (all series)")
    axes[0].legend()
    axes[1].plot(daily.Date, daily["mean"], color="#23688c")
    axes[1].set(title="Daily mean at native grain", ylabel="Units / SKU-warehouse-day", xlabel="Date (2024)")
    figures["daily-demand"] = fig
    fig, ax = plt.subplots(figsize=(10, 4), layout="constrained")
    ax.hist(df.Units_Sold, bins=np.arange(df.Units_Sold.min() - .5, df.Units_Sold.max() + 1.5).tolist(), color="#23688c", edgecolor="white")
    ax.set(title="Units_Sold distribution — all native observations", xlabel="Units sold / SKU-warehouse-day", ylabel="Number of observations")
    figures["demand-distribution"] = fig
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), layout="constrained")
    labels = [pd.Period(x).strftime("%b") for x in monthly.month]
    axes[0].bar(labels, monthly.total, color="#23688c")
    axes[0].set(title="Monthly totals — December contains 30 observed days", ylabel="Units / observed month")
    axes[1].plot(labels, monthly["mean"], marker="o", color="#23688c")
    axes[1].set(title="Monthly mean removes unequal observation-count effects", ylabel="Units / SKU-warehouse-day", xlabel="Month (2024)")
    figures["monthly-demand"] = fig
    for label, group in [("sku", "SKU_ID"), ("warehouse", "Warehouse_ID")]:
        data = tables[f"{label}_monthly"]
        matrix = data.pivot(index=group, columns="month", values="mean_index")
        fig, ax = plt.subplots(figsize=(11, 12 if label == "sku" else 4), layout="constrained")
        im = ax.imshow(matrix, aspect="auto", cmap="viridis", vmin=0, vmax=max(2, matrix.max().max()))
        ax.set_yticks(range(len(matrix)), matrix.index)
        ax.set_xticks(range(len(matrix.columns)), [pd.Period(x).strftime("%b") for x in matrix.columns])
        ax.set(title=f"Monthly {label} demand / its full-period mean (1 = baseline)", xlabel="Month (2024)", ylabel=group)
        ax.grid(False)
        fig.colorbar(im, ax=ax, label="Mean demand index")
        figures[f"{label}-monthly-patterns"] = fig
    fig, ax = plt.subplots(figsize=(11, 5), layout="constrained")
    for (name, warehouse_data), marker in zip(tables["warehouse_monthly"].groupby("Warehouse_ID"), ["o", "s", "^", "D", "x"], strict=False):
        ax.plot(labels, warehouse_data["mean"], marker=marker, label=name)
    ax.set(title="Warehouse monthly mean demand", xlabel="Month (2024)", ylabel="Units / SKU-warehouse-day")
    ax.legend(ncol=5)
    figures["warehouse-monthly-means"] = fig
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), layout="constrained")
    groups = [df.loc[df.Promotion_Flag.eq(v), "Units_Sold"] for v in (0, 1)]
    axes[0].boxplot(groups, tick_labels=["No promotion", "Promotion"], showfliers=False)
    axes[0].set(title="Demand by promotion status (fliers hidden)", ylabel="Units / native observation")
    p = tables["promotion_monthly"]
    for flag, style in [(0, "o-"), (1, "s--")]:
        part = p.loc[p.Promotion_Flag.eq(flag)]
        axes[1].plot(part.month.str[-2:], part["mean"], style, label=f"Flag {flag}")
    axes[1].set(title="Within-month descriptive comparison", xlabel="Month (2024)", ylabel="Mean units / native observation")
    axes[1].legend()
    figures["promotion-comparison"] = fig
    fig, ax = plt.subplots(figsize=(10, 4), layout="constrained")
    lag = tables["lag_summary"]
    ax.errorbar(lag.lag_days, lag["median"], yerr=[lag["median"] - lag.q25, lag.q75 - lag["median"]], fmt="o-", capsize=5, label="Levels: median and interquartile range")
    ax.plot(lag.lag_days, lag.differenced_median, "s--", label="First differences: median")
    ax.axhline(0, color="grey", lw=.8)
    ax.set(title="Within-series lag dependence — spread is not a confidence interval", xlabel="Calendar lag (days)", ylabel="Pearson correlation", xticks=list(LAGS), ylim=(-1, 1))
    ax.legend()
    figures["lag-dependence"] = fig
    return figures


def save_tables(tables: dict[str, pd.DataFrame], output_dir: Path) -> None:
    """Constrain detailed generated data to the repository's ignored area."""
    output_dir = output_dir.resolve()
    if not output_dir.is_relative_to((ROOT / "data/processed").resolve()):
        raise ValueError("Generated tables must stay under data/processed/.")
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, table in tables.items():
        table.to_csv(output_dir / f"{name}.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/raw/supply_chain_dataset1.csv")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/processed/demand_eda")
    parser.add_argument("--start", required=True, help="Explicitly authorized scope start")
    parser.add_argument("--end", required=True, help="Explicitly authorized scope end")
    args = parser.parse_args()
    raw = load_raw_source(args.input, start=args.start, end=args.end)
    df, validation_audit = build_validated_dataset(raw)
    audit = quality_tables(df, validation_audit)
    audit["native_grain"] = profile_native_grain(df)
    save_tables(audit, args.output_dir)
    print(audit["validation"].to_string(index=False))
    tables = analyze_demand(df)
    save_tables({**tables, "source_receipt": scoped_source_receipt(raw, args.input)}, args.output_dir)
    print(tables["monthly"].to_string(index=False))
    print("Detailed local tables saved. Execute notebooks/eda/demand_eda.ipynb for inline figures and PNG exports.")


def markdown_table(table: pd.DataFrame) -> str:
    """Small report tables without an additional tabulate dependency."""
    def fmt(value: Any) -> str:
        if pd.isna(value):
            return "—"
        if isinstance(value, (float, np.floating)):
            return f"{value:,.4f}"
        return str(value).replace("|", "\\|")
    return "\n".join(["| " + " | ".join(map(str, table.columns)) + " |",
                      "| " + " | ".join(["---"] * len(table.columns)) + " |"] +
                     ["| " + " | ".join(fmt(v) for v in row) + " |" for row in table.itertuples(index=False, name=None)])


def interpretations(tables: dict[str, pd.DataFrame]) -> dict[str, str]:
    """Data-bound prose shared by notebook and Markdown report."""
    m, d, s = tables["monthly"], tables["daily"], tables["series"]
    high, low = m.loc[cast(Any, m["mean"].idxmax())], m.loc[cast(Any, m["mean"].idxmin())]
    peak, trough = d.loc[cast(Any, d.total.idxmax())], d.loc[cast(Any, d.total.idxmin())]
    p = tables["promotion"].set_index("Promotion_Flag")
    promotion_rows = cast(int, p.loc[1, "rows"])
    nonpromotion_rows = cast(int, p.loc[0, "rows"])
    promotion_mean = cast(float, p.loc[1, "mean"])
    nonpromotion_mean = cast(float, p.loc[0, "mean"])
    lag = tables["lag_summary"].set_index("lag_days")
    zero_count = round((s.rows * s.zero_share).sum())
    result = {
        "overall": f"Total demand is {d.total.sum():,} units. There are {zero_count:,} zero-demand observations ({100 * zero_count / s.rows.sum():.3f}%). Native-series means range from {s['mean'].min():.3f} to {s['mean'].max():.3f} units; median coefficient of variation is {s.coefficient_of_variation.median():.6f}.",
        "monthly": f"The highest monthly mean is {high['month']} ({high['mean']:.3f} units per SKU-warehouse-day); the lowest is {low['month']} ({low['mean']:.3f}), a {high['mean'] / low['mean']:.2f}× ratio. Monthly totals reflect month length as well as demand level. These are observed within-year patterns, not evidence of recurring annual seasonality.",
        "extremes": f"The largest daily total is {int(peak.total):,} on {peak.Date:%Y-%m-%d}; the smallest is {int(trough.total):,} on {trough.Date:%Y-%m-%d}. The extreme tables rank observations, not statistical anomalies or records to remove. Large day-to-day moves are retained and have no inferred holiday explanation.",
        "rolling": "Trailing 7- and 14-day averages summarize the displayed day and preceding days. The first 6 and 13 outputs respectively are undefined because a full window is required. These retrospective EDA summaries are not forecasting features; smoothing alone is not evidence of predictive skill.",
        "promotion": f"Promotion rows number {int(promotion_rows):,}, with mean demand {promotion_mean:.3f}; non-promotion rows number {int(nonpromotion_rows):,}, with mean {nonpromotion_mean:.3f}. The unadjusted difference is {promotion_mean - nonpromotion_mean:.3f} units ({100 * (promotion_mean / nonpromotion_mean - 1):.2f}%). Monthly and within-series comparisons provide descriptive context, not causal identification or permission to use future promotion flags.",
        "lags": f"Median level correlations at lags 1, 7, 14 and 28 are {lag.loc[1, 'median']:.3f}, {lag.loc[7, 'median']:.3f}, {lag.loc[14, 'median']:.3f} and {lag.loc[28, 'median']:.3f}. After first differencing, medians at lags 7, 14 and 28 are {lag.loc[7, 'differenced_median']:.3f}, {lag.loc[14, 'differenced_median']:.3f} and {lag.loc[28, 'differenced_median']:.3f}. Broad level movement may contribute substantially to raw dependence; lag 7 is not uniquely elevated. Differencing is a diagnostic, not an approved preprocessing choice. Its negative lag-1 correlation can arise mechanically. No final lag set is selected.",
        "validation_design": "Historical EDA design context, superseded by the current forecasting methodology: the original wording below records then-approved horizons and intended holdout protection, not current instructions. The monthly and quarterly summaries show differing demand levels across the observed year. Expanding-window evaluation origins spaced across the year could therefore test materially different demand levels and transitions, whereas adjacent origins could cover similar periods. This is evidence to consider, not proof of differing model performance. Later design must balance initial history, the approved 1-/7-/14-day horizons, available future outcomes, possible overlap between evaluation windows, and an untouched final holdout. Full-year EDA has already exposed broad future-period patterns, so this influence on validation design must be disclosed. No fold dates, final split, seasonal regimes or models are defined here.",
    }
    for label, group in [("sku", "SKU_ID"), ("warehouse", "Warehouse_ID")]:
        stat = tables[f"{label}_pattern_similarity"].set_index("statistic").iloc[:, 0]
        variation = tables[f"{label}_variation"]
        result[label] = f"Across {len(variation)} {label}s, median pairwise correlation of the 12 monthly mean profiles is {stat['50%']:.6f} (minimum {stat['min']:.6f}). Within-{label} highest/lowest monthly mean ratios range from {variation.max_min_ratio.min():.2f} to {variation.max_min_ratio.max():.2f}. Broad temporal shapes are similar; this evidence does not suggest strongly distinct {label} patterns at monthly resolution. Aggregation can conceal daily differences, and correlation does not establish equal levels or forecasting performance."
    return result


def build_report(audit: dict[str, pd.DataFrame], tables: dict[str, pd.DataFrame], receipt: pd.DataFrame) -> str:
    """Render only reviewed aggregate evidence, never raw records."""
    if not audit["baseline"]["matches"].all():
        raise ValueError("Source differs from documented baseline; report the contradiction before regenerating the report.")
    notes = interpretations(tables)
    m = tables["monthly"]
    checks = audit["validation"]
    findings = checks.loc[checks.affected.gt(0)]
    validation_text = ("All implemented quality checks passed. No rows were dropped, imputed, clipped or aggregated at the native key. Cleaning was limited to in-memory date/numeric parsing and chronological sorting."
                       if findings.empty else "Quality failures require review:\n" + markdown_table(findings))
    chunks = ["# Demand exploratory data analysis\n",
        "**Scope:** Local simulated supply-chain data; `Units_Sold` at `Date + SKU_ID + Warehouse_ID`. No model training, final feature engineering, validation folds or new research decisions.\n\n> **Historical EDA provenance — notice added 2026-09-29:** The descriptive results and original methodology wording below are preserved from the earlier research stage; they do not define the current feature set, horizons or experiment authority. References to 1/7/14-day horizons, an unselected lag set or an untouched holdout are historical. The current [frozen feature contract](../docs/forecasting-feature-engineering.md) and [methodology/provenance record](../docs/forecasting-methodology-revision.md) govern forecasting. Final evaluation is December 3–30, 2024, origin December 2, reserved from subsequent selection/fitting but not fully unseen historically: December 3–16 had prior validation exposure and full-year EDA inspected the interval. No results were regenerated or tests/experiments executed for this notice.\n",
        "## Reproduction and provenance\n",
        "Use the repository virtual environment and install `requirements-dev.txt`. After separate human scope authorization, replace the date placeholders below and set notebook SCOPE_START/SCOPE_END explicitly. Stored full-year outputs are historical; the full-source report renderer must not relabel a partial scope as that evidence. From the repository root, the entry points are:\n\n```bash\n.venv/bin/python -m src.analysis.demand_exploratory_analysis --start YYYY-MM-DD --end YYYY-MM-DD\n.venv/bin/python - <<'PY'\nimport nbformat\nfrom nbclient import NotebookClient\np = 'notebooks/eda/demand_eda.ipynb'\nnb = nbformat.read(p, as_version=4)\nNotebookClient(nb, timeout=180, kernel_name='python3', resources={'metadata': {'path': '.'}}).execute()\nnbformat.write(nb, p)\nPY\n```\n",
        "The notebook uses the shared scoped loader/validator, displays summary tables and every figure inline, then saves those same figure objects as PNGs. It regenerates this report. Full generated tables stay under ignored `data/processed/demand_eda/`. The executed notebook contains aggregate outputs, not source-record previews.\n",
        markdown_table(receipt), "\n## Verified validation and cleaning\n", validation_text,
        "\n" + markdown_table(audit["baseline"]),
        "\nCoverage is measured for every observed SKU × warehouse combination against the global observed daily span, so missing edge days or an entirely absent combination cannot be hidden by each series' own span. Cardinalities and endpoints are separately compared with the documented baseline. Every current series has 365 dates; all 250 series occur on every observed day. The span ends 2024-12-30: December has 30/31 days and the leap year has 365/366 calendar dates. December 31 is outside the observed source span; it is not silently added or treated as zero demand.\n",
        "No missing/blank cells, invalid dates, duplicate native keys, negative count/cost/price values, fractional count values, non-finite numbers or non-binary flags were found. Observed ranges are descriptive, not newly approved bounds. `Demand_Forecast` is inspected only as source-quality metadata and is excluded from every demand calculation. `Stockout_Flag` remains zero-variance and is not a validation label.\n",
        markdown_table(audit["numeric_ranges"]), "\n## Overall demand and temporal extremes\n", notes["overall"],
        "\n" + markdown_table(tables["distribution"]), "\n" + notes["extremes"],
        "\n" + markdown_table(tables["extremes"][["kind", "Date", "total", "mean"]]),
        "\nLargest absolute changes from the preceding day (ranked, not anomaly classifications):\n",
        markdown_table(tables["largest_changes"][["Date", "total", "change", "change_pct"]]),
        "\n![Demand distribution](figures/demand-eda/demand-distribution.png)\n",
        "## Monthly behaviour and smoothing\n", notes["monthly"],
        "\nMonthly mean denominator = native observations; mean daily total denominator = observed dates. Month-to-month percentage change uses the preceding observed month; the first change is undefined.\n",
        markdown_table(m[["month", "days", "calendar_days", "total", "mean", "total_change_pct", "mean_change_pct", "zero_share"]]),
        "\n![Monthly demand](figures/demand-eda/monthly-demand.png)\n", notes["rolling"],
        "\n![Daily demand](figures/demand-eda/daily-demand.png)\n",
        "## SKU and warehouse comparisons\n", notes["sku"],
        "\n![SKU monthly profiles](figures/demand-eda/sku-monthly-patterns.png)\n", notes["warehouse"],
        "\nProfile indices divide each entity's monthly mean by its own full-observed-period mean; 1 is its baseline. These are retrospective descriptive normalizations only. Pairwise correlations use 12 monthly means, with each distinct entity pair counted once.\n",
        "![Warehouse monthly profiles](figures/demand-eda/warehouse-monthly-patterns.png)\n",
        "![Warehouse monthly means](figures/demand-eda/warehouse-monthly-means.png)\n",
        "## Promotion relationship\n", notes["promotion"],
        "\n" + markdown_table(tables["promotion"][["Promotion_Flag", "rows", "mean", "median", "std", "zero_share"]]),
        "\n![Promotion comparison](figures/demand-eda/promotion-comparison.png)\n",
        "## Lag evidence\n", notes["lags"],
        "\nCorrelations are Pearson correlations of each complete, date-sorted native series with itself shifted by the stated calendar lag. Undefined/constant correlations are omitted from summaries and counted by `defined_series`. No series are concatenated across boundaries. Interquartile ranges describe between-series spread, not confidence intervals.\n",
        markdown_table(tables["lag_summary"]),
        "\n![Lag dependence](figures/demand-eda/lag-dependence.png)\n",
        "## Evidence for future expanding-window validation\n",
        markdown_table(tables["quarterly"][["quarter", "days", "mean", "std", "zero_share", "promotion_share"]]),
        "\n" + notes["validation_design"],
        "\n## Limitations and decision-record consistency\n",
        "- This is simulated data, not evidence from an operating retailer.\n- One observed within-year cycle cannot establish recurring annual seasonality. No Sri Lankan holiday or other external-event effects are inferred.\n- `Units_Sold` is the approved demand proxy; zero-variance `Stockout_Flag` cannot verify unconstrained demand or observed stockouts.\n- Promotion differences and temporal correlations are descriptive and may reflect simulation design or confounding. No causal effects or significance tests are claimed.\n- Monthly aggregation smooths native daily heterogeneity. Full-year normalization and differencing are EDA diagnostics, not model features.\n- Validation rules detect specified defects, not every possible semantic error. Unexpected defects require an explicit handling decision rather than automatic repair.\n- The verified counts, native grain, median coefficient of variation, median zero-demand share and lag-1 correlation agree with the existing profile and DR-002. Nothing here contradicts DR-003 or DR-004; no decision record was changed.\n",
        "## Project references\n",
        "[Dataset contract](../docs/dataset.md), [prior temporal profile](temporal-demand-profile.md), [DR-002](../docs/decisions/DR-002-forecasting-analytical-unit.md), [DR-003](../docs/decisions/DR-003-forecasting-feature-engineering-baseline.md), [DR-004](../docs/decisions/DR-004-forecast-horizons.md).\n"]
    return "\n".join(chunks)


if __name__ == "__main__":
    main()
