"""Eight purpose-driven figures from display projections of retained evidence.

Callers own saving and cleanup. Synthetic callers can exercise every renderer
without accessing research data, loading models or invoking any producer.
"""

from __future__ import annotations

from collections.abc import Sequence
import textwrap
from typing import Any

from matplotlib.axes import Axes
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.colors import Normalize
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator, PercentFormatter
from matplotlib.transforms import Bbox

from src.visualization.thesis_evidence import CRITERIA, MODELS, FigureEvidence

BLUE = "#0072B2"
ORANGE = "#D55E00"
INK = "#25313B"
GREY = "#66717B"
LIGHT = "#EDF1F4"
HORIZONS = (1, 7, 14)
LABELS = {
    1: "h1: next-day",
    7: "h7: cumulative",
    14: "h14: cumulative",
    28: "h28: cumulative",
}
MODEL_LABELS = {
    "xgboost": "XGBoost",
    "lightgbm": "LightGBM",
    "catboost": "CatBoost",
    "ridge": "Ridge",
    "random_forest": "Random Forest",
    "naive": "Naive",
    "seasonal_naive": "Seasonal Naive",
}
APPROVAL = "DR-012: h1/h7/h14 method group-approved 12 Oct 2026; reported 23 Oct."
SCENARIO = (
    "Constructed origin; fixed reorder point; no receipts. Source timing unknown."
)
LIMIT = "Publisher-simulated data. Scenario proxy, not observed stockout or purchasing advice."


def _wrapped(value: str, width: int = 94) -> str:
    return "\n".join(textwrap.fill(line, width) for line in value.splitlines())


def _new(
    spec: FigureEvidence, height: float, subtitle: str, *, scenario: bool = True
) -> Figure:
    figure = Figure(figsize=(6.3, height), dpi=100, facecolor="white")
    FigureCanvasAgg(figure)
    figure.suptitle(
        spec.title, x=0.07, y=0.98, ha="left", fontsize=12, fontweight="bold", color=INK
    )
    figure.text(0.07, 0.925, _wrapped(subtitle, 91), va="top", fontsize=8.5, color=INK)
    notes = (
        [APPROVAL, SCENARIO, LIMIT]
        if scenario
        else ["Publisher-simulated data; retained results only."]
    )
    notes.append("Full values, source hashes and case identities: accompanying JSON.")
    figure.text(
        0.07,
        0.025,
        "\n".join(notes),
        va="bottom",
        fontsize=8,
        color=INK,
        linespacing=1.4,
    )
    return figure


def _style(axis: Axes, *, grid: bool = True) -> None:
    axis.tick_params(labelsize=8)
    axis.spines[["top", "right"]].set_visible(False)
    axis.spines[["left", "bottom"]].set_color(GREY)
    axis.xaxis.label.set_fontsize(8.5)
    axis.yaxis.label.set_fontsize(8.5)
    if grid:
        axis.grid(axis="x", color=LIGHT, linewidth=0.7)
        axis.set_axisbelow(True)


def _table(
    axis: Axes,
    headers: Sequence[str],
    rows: Sequence[Sequence[Any]],
    *,
    widths: Sequence[float] | None = None,
    size: float = 8.5,
) -> None:
    axis.axis("off")
    table = axis.table(
        cellText=[[str(v) for v in row] for row in rows],
        colLabels=list(headers),
        colWidths=widths,
        cellLoc="left",
        colLoc="left",
        bbox=Bbox.from_bounds(0, 0, 1, 1),
    )
    table.auto_set_font_size(False)
    table.set_fontsize(size)
    for (r, _), cell in table.get_celld().items():
        cell.set_edgecolor("white")
        cell.PAD = 0.06
        cell.set_text_props(color=INK, family="DejaVu Sans")
        if r == 0:
            cell.set_facecolor(INK)
            cell.set_text_props(color="white", weight="bold")
        else:
            cell.set_facecolor(LIGHT if r % 2 else "white")


def _rate(metric: dict[str, Any]) -> str:
    value = metric["value"]
    if value is None:
        return f"Unavailable\n{metric['status']}"
    return f"{value:.2%}\n(n={metric['denominator']})"


def coverage(spec: FigureEvidence) -> Figure:
    data = spec.data
    figure = _new(
        spec,
        5.3,
        f"Origin {data['forecast_origin']}. Counts are separate for each horizon.",
    )
    summary = {r["horizon"]: r for r in data["evaluation_only"]["summary"]}
    rows = []
    for pop in sorted(data["horizon_population"], key=lambda r: r["horizon"]):
        h = pop["horizon"]
        r = summary.get(h)
        rows.append(
            [
                LABELS[h],
                pop["horizon_forecast_population_count"],
                r["evaluable_paired_case_count"] if r else "Gated",
                r["scenario_at_or_below_count"] if r else "Not assessed",
                r["unavailable_case_count"] if r else "Not assessed",
            ]
        )
    _table(
        figure.add_axes((0.07, 0.44, 0.88, 0.36)),
        [
            "Horizon",
            "Forecast\nrecords",
            "Paired\ncases",
            "Scenario\nat/below",
            "Unavailable\nin evaluation",
        ],
        rows,
        widths=(0.25, 0.15, 0.15, 0.20, 0.25),
        size=8,
    )
    source_counts = "; ".join(
        f"h{h}={summary[h]['origin_known_at_or_below_count']}" for h in HORIZONS
    )
    figure.text(
        0.07,
        0.36,
        _wrapped(
            f"Source-confirmed origin at/below counts: {source_counts}. "
            "These counts do not establish source snapshot availability.",
            88,
        ),
        fontsize=8.5,
        va="top",
    )
    figure.text(
        0.07,
        0.255,
        "h28: forecasts available; inventory use deferred.\n"
        "Scenario-at/below cases are outside the paired forecast comparison.",
        fontsize=8.5,
        va="top",
    )
    return figure


def proxy_crossings(spec: FigureEvidence) -> Figure:
    summaries = sorted(spec.data["summaries"], key=lambda r: r["group"]["horizon"])
    figure = _new(
        spec,
        6.7,
        "Evaluation only: retrospective threshold-crossing proxy from Units_Sold.\n"
        "Cell counts retain the existing eligible population; horizons are not pooled.",
    )
    maximum = max(
        max(s["counts"][k] for k in ("TP", "TN", "FP", "FN")) for s in summaries
    )
    norm = Normalize(vmin=0, vmax=max(1, maximum))
    for i, s in enumerate(summaries):
        c, h = s["counts"], s["group"]["horizon"]
        axis = figure.add_axes((0.105 + i * 0.30, 0.56, 0.235, 0.24))
        values = [[c["TP"], c["FN"]], [c["FP"], c["TN"]]]
        axis.imshow(values, cmap="Blues", norm=norm)
        axis.set_title(f"{LABELS[h]}\nPaired N={c['N']}", fontsize=8.5, pad=7)
        axis.set_xticks((0, 1), ("Yes", "No"), fontsize=8)
        axis.set_yticks((0, 1), ("Yes", "No"), fontsize=8)
        axis.set_xlabel("Forecast crossing", fontsize=8)
        if i == 0:
            axis.set_ylabel("Retrospective crossing", fontsize=8)
        for y, labels in enumerate((("TP", "FN"), ("FP", "TN"))):
            for x, label in enumerate(labels):
                axis.text(
                    x,
                    y,
                    f"{label}\n{c[label]}",
                    ha="center",
                    va="center",
                    fontsize=9,
                    color="white" if norm(c[label]) > 0.55 else INK,
                )
    rows = []
    for label, key in (
        ("Event prevalence", "event_prevalence"),
        ("Missed-crossing rate", "missed_crossing_rate"),
        ("False-alert rate", "false_alert_rate"),
        ("Agreement", "agreement"),
    ):
        rows.append([label, *(_rate(s["metrics"][key]) for s in summaries)])
    _table(
        figure.add_axes((0.07, 0.24, 0.88, 0.245)),
        ["Existing metric", "h1", "h7", "h14"],
        rows,
        widths=(0.37, 0.21, 0.21, 0.21),
        size=8,
    )
    figure.text(
        0.07,
        0.19,
        "TP: both cross; FN: proxy only; FP: forecast only; TN: neither.\n"
        "n is the metric-specific denominator; all other retained metrics are in JSON.",
        fontsize=8,
        va="top",
    )
    return figure


def population_margins(spec: FigureEvidence) -> Figure:
    cases = spec.data["evaluation_only_cases"]
    paired = [
        r
        for r in cases
        if r["comparison_case"] == "evaluable_paired_case"
        and r["predicted_margin"] is not None
        and r["retrospective_margin"] is not None
    ]
    values = [
        r[k] for r in paired for k in ("predicted_margin", "retrospective_margin")
    ]
    low, high = min([0, *values]), max([0, *values])
    pad = max(1, (high - low) * 0.08)
    ticks = MaxNLocator(nbins=4).tick_values(low - pad, high + pad)
    figure = _new(
        spec,
        7.6,
        "Evaluation only: paired margins in units (origin buffer minus demand).\n"
        "Matching linear scales across panels; no tolerance bands or daily trajectories.",
    )
    markers = {
        "TN": ("o", GREY, 11),
        "TP": ("^", BLUE, 17),
        "FN": ("D", ORANGE, 23),
        "FP": ("s", INK, 23),
    }
    identity = tuple(spec.data["worked_identity"])
    for i, h in enumerate(HORIZONS):
        axis = figure.add_axes(
            (0.12 + (i % 2) * 0.48, 0.57 - (i // 2) * 0.38, 0.35, 0.26)
        )
        group = [r for r in paired if r["horizon"] == h]
        for cell, (marker, color, size) in markers.items():
            records = [r for r in group if r["confusion_cell"] == cell]
            points = axis.scatter(
                [r["predicted_margin"] for r in records],
                [r["retrospective_margin"] for r in records],
                marker=marker,
                s=size,
                edgecolors=color,
                facecolors="none" if cell in {"FN", "FP"} else color,
                linewidths=0.65,
                alpha=0.8,
            )
            points.set_gid(f"h{h}-{cell}-case-order-in-sidecar")
        selected = [
            r
            for r in group
            if (r["SKU_ID"], r["Warehouse_ID"], r["forecast_origin"]) == identity
        ]
        for row in selected:
            axis.scatter(
                [row["predicted_margin"]],
                [row["retrospective_margin"]],
                s=75,
                facecolors="none",
                edgecolors=INK,
                linewidths=1.2,
            )
            axis.annotate(
                f"{identity[0]} / {identity[1]}",
                (row["predicted_margin"], row["retrospective_margin"]),
                xytext=(0.06, 0.94),
                textcoords="axes fraction",
                fontsize=8,
                ha="left",
                va="top",
                bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.5},
                arrowprops={
                    "arrowstyle": "->",
                    "color": INK,
                    "linewidth": 0.7,
                    "shrinkA": 4,
                    "shrinkB": 6,
                },
            )
        axis.axhline(0, color=INK, linewidth=0.8)
        axis.axvline(0, color=INK, linewidth=0.8)
        axis.set(xlim=(ticks[0], ticks[-1]), ylim=(ticks[0], ticks[-1]))
        axis.set_xticks(ticks)
        axis.set_yticks(ticks)
        axis.set_aspect("equal", adjustable="box")
        excluded = len([r for r in cases if r["horizon"] == h]) - len(group)
        axis.set_title(
            f"{LABELS[h]} | paired n={len(group)}\nExcluded from margin plot: {excluded}",
            fontsize=8,
            pad=4,
        )
        _style(axis, grid=False)
        axis.set_xlabel("Predicted margin (units)")
        if i % 2 == 0:
            axis.set_ylabel("Retrospective margin (units)")
    handles = [
        Line2D(
            [],
            [],
            marker=m,
            color="none",
            markeredgecolor=c,
            markerfacecolor="none" if cell in {"FN", "FP"} else c,
            markersize=4,
            label={
                "TN": "TN: neither crosses",
                "TP": "TP: both cross",
                "FN": "FN: proxy only",
                "FP": "FP: forecast only",
            }[cell],
        )
        for cell, (m, c, _) in markers.items()
    ]
    figure.legend(
        handles=handles,
        loc="center",
        bbox_to_anchor=(0.73, 0.40),
        fontsize=8,
        frameon=False,
    )
    figure.text(
        0.60,
        0.30,
        "Ring: existing worked case\nNull/non-paired margins\nare excluded, never zero.\nFull case index: JSON.\n\nNegative margin is not\nverified physical negative\nstock.",
        fontsize=8,
        va="top",
        linespacing=1.3,
    )
    return figure


def _worked_subtitle(spec: FigureEvidence) -> str:
    row = spec.data["worked"][0]["prospective"]
    return f"{row['SKU_ID']} / {row['Warehouse_ID']} | origin {row['forecast_origin']} | illustrative case"


def worked_forecast(spec: FigureEvidence) -> Figure:
    rows = spec.data["worked"]
    figure = _new(spec, 5.9, _worked_subtitle(spec))
    axis = figure.add_axes((0.12, 0.54, 0.81, 0.27))
    positions = list(range(len(rows)))
    predicted = [r["prospective"]["prediction"] for r in rows]
    actual = [r["observations_evaluation_only"]["actual_units_sold"] for r in rows]
    for offset, values, color, hatch, label in (
        (-0.19, predicted, BLUE, "", "Forecast"),
        (0.19, actual, ORANGE, "//", "Actual sales (retrospective)"),
    ):
        bars = axis.bar(
            [p + offset for p in positions],
            values,
            width=0.36,
            color=color,
            edgecolor=INK,
            linewidth=0.5,
            hatch=hatch,
            label=label,
        )
        axis.bar_label(bars, labels=[f"{v:.2f}" for v in values], fontsize=8, padding=3)
    axis.set_xticks(
        positions,
        ["h1\nnext-day", "h7\ncumulative", "h14\ncumulative", "h28\ncumulative"],
    )
    axis.set_ylabel("Demand over target window (units)")
    axis.set_ylim(0, max([1, *predicted, *actual]) * 1.20)
    _style(axis, grid=False)
    figure.legend(
        *axis.get_legend_handles_labels(),
        loc="upper right",
        bbox_to_anchor=(0.94, 0.87),
        fontsize=8,
        frameon=False,
        ncol=2,
    )
    table_rows = [
        [
            f"h{r['prospective']['horizon']}",
            f"{r['prospective']['target_start_date']}\nto {r['prospective']['target_end_date']}",
            f"{MODEL_LABELS[r['prospective']['model']]}\n{r['prospective']['configuration_id']}",
        ]
        for r in rows
    ]
    _table(
        figure.add_axes((0.07, 0.205, 0.88, 0.23)),
        ["Horizon", "Target window (inclusive)", "Frozen producer"],
        table_rows,
        widths=(0.17, 0.45, 0.38),
        size=8,
    )
    figure.text(
        0.07,
        0.17,
        "Actuals are evaluation only. Windows overlap and are not additive.",
        fontsize=8,
        va="top",
    )
    return figure


def worked_margins(spec: FigureEvidence) -> Figure:
    rows = [r for r in spec.data["worked"] if r["prospective"]["horizon"] in HORIZONS]
    row = rows[0]["prospective"]
    figure = _new(
        spec,
        5.9,
        _worked_subtitle(spec) + "\n"
        f"Starting inventory {row['Inventory_Level']:g}; reorder reference {row['Reorder_Point']:g}; buffer {row['inventory_buffer']:g} units.\n"
        "h28 inventory use deferred.",
    )
    axis = figure.add_axes((0.16, 0.39, 0.75, 0.41))
    for offset, field, color, hatch, label in (
        (-0.18, "predicted_margin", BLUE, "", "Predicted margin"),
        (
            0.18,
            "retrospective_margin",
            ORANGE,
            "//",
            "Retrospective margin (evaluation only)",
        ),
    ):
        values = [r["evaluation_only"][field] for r in rows]
        positions = [i + offset for i, _ in enumerate(rows)]
        valid = [
            (p, v) for p, v in zip(positions, values, strict=True) if v is not None
        ]
        bars = axis.barh(
            [p for p, _ in valid],
            [v for _, v in valid],
            height=0.31,
            color=color,
            hatch=hatch,
            edgecolor=INK,
            linewidth=0.5,
            label=label,
        )
        axis.bar_label(
            bars, labels=[f"{v:+.2f}" for _, v in valid], fontsize=8, padding=4
        )
    all_values = [
        r["evaluation_only"][k]
        for r in rows
        for k in ("predicted_margin", "retrospective_margin")
        if r["evaluation_only"][k] is not None
    ]
    span = max([1, *all_values]) - min([0, *all_values])
    axis.set_xlim(
        min([0, *all_values]) - span * 0.20, max([0, *all_values]) + span * 0.22
    )
    axis.axvline(0, color=INK, linewidth=1)
    axis.set_yticks(range(len(rows)), [f"h{r['prospective']['horizon']}" for r in rows])
    axis.invert_yaxis()
    axis.set_xlabel("Margin relative to origin reorder reference (units)")
    _style(axis)
    figure.legend(
        *axis.get_legend_handles_labels(),
        loc="upper left",
        bbox_to_anchor=(0.07, 0.33),
        fontsize=8,
        frameon=False,
        ncol=2,
    )
    states = [
        [
            f"h{r['prospective']['horizon']}",
            r["evaluation_only"]["confusion_cell"],
            {
                "FN": "Missed proxy crossing",
                "TN": "Neither crosses",
                "TP": "Both cross",
                "FP": "Forecast-only crossing",
            }.get(
                r["evaluation_only"]["confusion_cell"], "Unavailable; see source reason"
            ),
        ]
        for r in rows
    ]
    _table(
        figure.add_axes((0.07, 0.19, 0.88, 0.10)),
        ["Horizon", "Outcome", "Retrospective comparison"],
        states,
        widths=(0.18, 0.18, 0.64),
        size=8,
    )
    figure.text(
        0.07,
        0.17,
        "Negative margin is not verified physical negative stock.",
        fontsize=8,
        va="top",
    )
    return figure


def evidence_status(spec: FigureEvidence) -> Figure:
    figure = _new(
        spec,
        6.8,
        "Evidence presence, method approval and consumer acceptance are different statuses.",
    )
    rows = [
        ["h1 / h7 / h14", "Available", "Constructed\nscenario", "Evaluation\nonly"],
        ["h28", "Available", "Deferred / gated", "Not assessed"],
    ]
    _table(
        figure.add_axes((0.07, 0.65, 0.88, 0.17)),
        ["Horizon", "Forecast", "Inventory exposure", "Retrospective\nevidence"],
        rows,
        widths=(0.24, 0.18, 0.30, 0.28),
        size=8,
    )
    status_rows = [
        [
            "Current method approval",
            "h1/h7/h14 group-approved;\n12 Oct, reported 23 Oct 2026",
        ],
        [
            "Historical source label",
            "proposed_for_group_approval\nPreserved; not the current approval status",
        ],
        ["Source snapshot timing", "Unknown; scenario availability is separate"],
        ["Numerical replenishment /\noverstock", "Unavailable; deferred extensions"],
        [
            "Forecast uncertainty /\nauto-review rules",
            "Unavailable; no approved method supplied",
        ],
        [
            "Consumer / rendered-view\nacceptance",
            "Separate source- and revision-specific reviews;\nnot established by method approval or hashes",
        ],
    ]
    _table(
        figure.add_axes((0.07, 0.21, 0.88, 0.38)),
        ["Evidence / status", "Meaning and boundary"],
        status_rows,
        widths=(0.41, 0.59),
        size=8,
    )
    figure.text(
        0.07,
        0.17,
        "Stockout_Flag is zero-variance and cannot validate observed stockouts.",
        fontsize=8,
        va="top",
    )
    return figure


def transparency(spec: FigureEvidence) -> Figure:
    assessment = spec.data["assessment"]
    figure = _new(
        spec,
        5.7,
        f"Human-entered record assessment: {assessment['reviewed_records']} purposive records; "
        f"{assessment['reviewed_check_rows']} checks.\nNot assessable is distinct from not met; no overall success score.",
        scenario=False,
    )
    axis = figure.add_axes((0.36, 0.30, 0.55, 0.50))
    left = [0] * len(CRITERIA)
    styles = (
        ("met", BLUE, ""),
        ("not met", ORANGE, "xx"),
        ("not assessable", LIGHT, "///"),
    )
    for label, color, hatch in styles:
        counts = [assessment["criteria"][c][label] for c in CRITERIA]
        bars = axis.barh(
            range(len(CRITERIA)),
            counts,
            left=left,
            color=color,
            hatch=hatch,
            edgecolor=INK,
            linewidth=0.5,
            height=0.6,
            label=label.capitalize(),
        )
        for bar, value in zip(bars, counts, strict=True):
            if value:
                axis.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_y() + bar.get_height() / 2,
                    str(value),
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="white" if label == "met" else INK,
                    bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.0}
                    if hatch
                    else None,
                )
        left = [a + b for a, b in zip(left, counts, strict=True)]
    axis.set_yticks(
        range(len(CRITERIA)),
        [c.replace(" ", "\n", 1) if len(c) > 23 else c for c in CRITERIA],
    )
    axis.invert_yaxis()
    axis.set_xlim(0, assessment["reviewed_records"])
    axis.xaxis.set_major_locator(MaxNLocator(integer=True))
    axis.set_xlabel("Applicable record checks (count)")
    _style(axis)
    axis.legend(
        loc="upper right",
        bbox_to_anchor=(1.0, -0.18),
        fontsize=8,
        frameon=False,
        ncol=3,
    )
    figure.text(
        0.07,
        0.15,
        "Counts describe record transparency, not usability, trust or decision quality.\n"
        "Human-review transparency does not mean managerial review was completed.",
        fontsize=8,
        va="top",
    )
    return figure


def forecasting_comparison(spec: FigureEvidence) -> Figure:
    rows = spec.data["comparison"]
    figure = _new(
        spec,
        7.6,
        f"One final origin: {spec.data['forecast_origin']}. WAPE = Weighted Absolute Percentage Error.\n"
        "All frozen models; lower WAPE is better. D denotes the pre-frozen designated producer.",
        scenario=False,
    )
    maximum = max(r["WAPE"] for r in rows)
    ticks = MaxNLocator(nbins=3, steps=[1, 2, 5, 10]).tick_values(
        0, max(0.01, maximum) * 1.32
    )
    for i, h in enumerate((1, 7, 14, 28)):
        axis = figure.add_axes(
            (0.20 + (i % 2) * 0.46, 0.57 - (i // 2) * 0.35, 0.27, 0.25)
        )
        group = {r["model"]: r for r in rows if r["horizon"] == h}
        labels = []
        for j, model in enumerate(MODELS):
            r = group[model]
            role = r["role"]
            color = (
                BLUE
                if role == "primary"
                else "#9DC5DC"
                if role == "supportive"
                else LIGHT
            )
            bars = axis.barh(
                j,
                r["WAPE"],
                height=0.65,
                color=color,
                edgecolor=INK,
                linewidth=0.5,
                hatch="//" if role == "simple_baseline" else "",
            )
            axis.bar_label(bars, labels=[f"{r['WAPE']:.2%}"], padding=3, fontsize=8)
            labels.append(
                MODEL_LABELS[model] + (" [D]" if r["designated_producer"] else "")
            )
        axis.set_yticks(range(len(MODELS)), labels)
        axis.invert_yaxis()
        axis.set_xlim(0, ticks[-1])
        axis.set_xticks(ticks)
        axis.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
        axis.set_title(LABELS[h], fontsize=9, loc="left")
        axis.set_xlabel("WAPE (%)")
        _style(axis)
        axis.tick_params(axis="y", labelsize=8)
    figure.legend(
        handles=[
            Patch(facecolor=BLUE, label="Primary"),
            Patch(facecolor="#9DC5DC", label="Supportive"),
            Patch(facecolor=LIGHT, hatch="//", edgecolor=INK, label="Baseline"),
        ],
        loc="lower center",
        bbox_to_anchor=(0.5, 0.13),
        frameon=False,
        fontsize=8,
        ncol=3,
    )
    figure.text(
        0.07,
        0.105,
        "December 3–16 had prior validation exposure; full-year EDA included the final interval.\n"
        "No pooled ranking, significance claim or result-driven producer reselection.",
        fontsize=8,
        va="top",
    )
    return figure


RENDERERS = (
    coverage,
    proxy_crossings,
    population_margins,
    worked_forecast,
    worked_margins,
    evidence_status,
    transparency,
    forecasting_comparison,
)


def render_figure(spec: FigureEvidence, index: int) -> Figure:
    """Render one projection with explicit typography, without global style changes."""
    figure = RENDERERS[index](spec)
    for axis in figure.axes:
        for text in axis.texts:
            text.set_fontfamily("DejaVu Sans")
    return figure
