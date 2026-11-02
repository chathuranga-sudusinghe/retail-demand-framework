"""Render the four approved inventory evidence views as static Matplotlib tables.

The renderers accept outputs from :mod:`inventory_views`; they do not load,
validate, or calculate research evidence. Each returned figure contains the
source fields selected from those outputs without modifying the input mapping.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import json
import re
from typing import Any

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

_HORIZONS = (1, 7, 14)
_HORIZON_LABELS = {
    1: "h1 next-day",
    7: "h7 cumulative",
    14: "h14 cumulative",
    28: "h28 downstream-gated",
}
_H28_FIELDS = (
    "SKU_ID",
    "Warehouse_ID",
    "forecast_origin",
    "horizon",
    "target_start_date",
    "target_end_date",
    "downstream_use_status",
    "downstream_use_reason",
)
_H28_IDENTITY_FIELDS = _H28_FIELDS[:6]
_H28_WARNING = (
    "h28 remains downstream-gated; no inventory exposure, margin, or "
    "retrospective evaluation fields are shown."
)
_H28_COLUMN_WIDTHS = (0.85, 0.85, 1.2, 0.5, 0.9, 0.9, 3.0, 7.0)
_MAX_TABLE_ROWS_PER_PAGE = 40
_MAX_PANEL_FIELDS = 8
_IDENTITY_FIELDS = (
    "SKU_ID",
    "Warehouse_ID",
    "forecast_origin",
    "horizon",
    "target_start_date",
    "target_end_date",
)
_GROUP_FIELDS = (
    "forecast_origin",
    "horizon",
    "run_id",
    "evaluation_stage",
    "evidence_role",
    "model",
    "configuration_id",
    "canonical_config_id",
    "forecast_type",
)
_SHARED_CONTEXT_FIELDS = (
    "source_provenance",
    "method_assumptions",
    "method_limitations",
)


def _display(value: Any) -> str:
    """Make null, zero, false, and empty strings visibly distinct."""
    if value is None:
        return "null"
    if value is False:
        return "false"
    if value is True:
        return "true"
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    if value == "":
        return '""'
    return str(value)


def _natural_identifier_key(value: str) -> tuple[tuple[int, int | str], ...]:
    """Tokenize identifier digits numerically for presentation ordering."""
    return tuple(
        (0, int(part)) if part.isdigit() else (1, part.casefold())
        for part in re.split(r"(\d+)", value)
    )


def _columns(rows: Sequence[Mapping[str, Any]]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(name for row in rows for name in row))


def _shared_context(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Return only long source fields identical in every row of a projection."""
    shared: dict[str, Any] = {}
    if not rows:
        return shared
    for field in _SHARED_CONTEXT_FIELDS:
        if not all(field in row for row in rows):
            continue
        first = _display(rows[0][field])
        if len(first) < 120:
            continue
        if all(_display(row[field]) == first for row in rows[1:]):
            shared[field] = rows[0][field]
    return shared


def _without_shared_context(
    rows: Sequence[Mapping[str, Any]], shared: Mapping[str, Any]
) -> list[Mapping[str, Any]]:
    """Keep common long values in the metadata block, not repeated case cells."""
    if not shared:
        return list(rows)
    return [
        {field: value for field, value in row.items() if field not in shared}
        for row in rows
    ]


def _repeated_long_field(rows: Sequence[Mapping[str, Any]], field: str) -> Any | None:
    """Return a long field value when it is identical across multiple rows."""
    if len(rows) < 2 or not all(field in row for row in rows):
        return None
    value = rows[0][field]
    rendered = _display(value)
    if len(rendered) < 120:
        return None
    if all(_display(row[field]) == rendered for row in rows[1:]):
        return value
    return None


def _reference_repeated_field(
    rows: Sequence[Mapping[str, Any]], field: str, reference: str
) -> list[Mapping[str, Any]]:
    """Keep a concise pointer in each row while the complete value is elsewhere."""
    return [{**row, field: reference} if field in row else dict(row) for row in rows]


def _table_panels(columns: Sequence[str]) -> tuple[tuple[str, ...], ...]:
    """Split fields into readable panels while repeating case/group identity."""
    identity_order = (*_IDENTITY_FIELDS, *_GROUP_FIELDS, "metric")
    repeated = tuple(
        dict.fromkeys(field for field in identity_order if field in columns)
    )
    remaining = [field for field in columns if field not in repeated]
    if not remaining:
        return (tuple(columns),) if columns else ((),)
    chunks = [
        remaining[index : index + _MAX_PANEL_FIELDS]
        for index in range(0, len(remaining), _MAX_PANEL_FIELDS)
    ]
    return tuple((*repeated, *chunk) for chunk in chunks)


def _column_widths(
    columns: Sequence[str], rows: Sequence[Mapping[str, Any]], width: float
) -> tuple[list[float], list[int]]:
    """Allocate more space to longer fields and derive lossless wrap widths."""
    weights = [
        min(
            52,
            max(
                8,
                len(column),
                max((len(_display(row.get(column))) for row in rows), default=0),
            ),
        )
        for column in columns
    ]
    total = sum(weights) or 1
    fractions = [weight / total for weight in weights]
    characters = [max(8, int(width * 72 * fraction / 3.6)) for fraction in fractions]
    return fractions, characters


def _hard_wrap(value: str, characters: int) -> str:
    """Insert visual line breaks without removing or shortening any character."""
    return "\n".join(
        value[index : index + characters] for index in range(0, len(value), characters)
    )


def _metadata_figure(title: str, metadata: Mapping[str, Any]) -> Figure:
    """Place complete source metadata and shared caveats on a wrapped page."""
    serialized = json.dumps(
        metadata, ensure_ascii=False, sort_keys=True, indent=2, default=str
    )
    estimated_lines = sum(
        max(1, (len(line) + 119) // 120) for line in serialized.splitlines()
    )
    height = max(5.0, 2.4 + estimated_lines * 0.18)
    figure = Figure(figsize=(18.0, height))
    FigureCanvasAgg(figure)
    figure.suptitle(title, fontsize=12)
    axis = figure.add_axes((0.025, 0.025, 0.95, 0.90))
    axis.axis("off")
    axis.text(
        0.0,
        1.0,
        serialized,
        va="top",
        ha="left",
        transform=axis.transAxes,
        family="monospace",
        fontsize=7,
        wrap=True,
    )
    return figure


def _metadata_entries(label: str, value: Any) -> list[str]:
    """Render metadata as labeled entries without changing source values."""
    if isinstance(value, Mapping):
        if not value:
            return [f"{label}: {{}}"]
        return [
            entry
            for key, item in value.items()
            for entry in _metadata_entries(f"{label} / {key}", item)
        ]
    if isinstance(value, (list, tuple)):
        if not value:
            return [f"{label}: []"]
        return [
            entry
            for index, item in enumerate(value, start=1)
            for entry in _metadata_entries(f"{label} [{index}]", item)
        ]
    return [f"{label}: {_display(value)}"]


def _wrap_metadata_line(value: str, width: int) -> list[str]:
    """Wrap on word boundaries where possible while retaining all characters."""
    wrapped: list[str] = []
    for source_line in value.split("\n"):
        remaining = source_line
        while len(remaining) > width:
            boundary = remaining.rfind(" ", 0, width)
            if boundary <= 0:
                boundary = width
            else:
                boundary += 1
            wrapped.append(remaining[:boundary])
            remaining = remaining[boundary:]
        wrapped.append(remaining)
    return wrapped


def _exposure_metadata_figure(title: str, metadata: Mapping[str, Any]) -> Figure:
    """Render A metadata in readable sections while preserving every value."""
    shared_fields = metadata.get("shared_source_fields", {})
    if not isinstance(shared_fields, Mapping):
        shared_fields = {"shared_source_fields": shared_fields}

    shared: dict[str, Any] = {}
    scenario: dict[str, Any] = {}
    source_metadata = metadata.get("source_metadata")
    if isinstance(source_metadata, Mapping):
        common_source: dict[str, Any] = {}
        scenario_source: dict[str, Any] = {}
        for key, value in source_metadata.items():
            if key in {"snapshot_assumption", "snapshot_policy"}:
                scenario_source[key] = value
            else:
                common_source[key] = value
        if common_source or not source_metadata:
            shared["source_metadata"] = common_source
        if scenario_source:
            scenario["source_metadata"] = scenario_source
    elif "source_metadata" in metadata:
        shared["source_metadata"] = source_metadata
    if "shared_field_note" in metadata:
        shared["shared_field_note"] = metadata["shared_field_note"]

    limitations: dict[str, Any] = {}
    provenance: dict[str, Any] = {}
    horizon_assumptions: Any = {}
    other_shared: dict[str, Any] = {}
    for scope, fields in shared_fields.items():
        if scope == "prospective scenario assumptions by horizon":
            horizon_assumptions = fields
            continue
        if not isinstance(fields, Mapping):
            other_shared[scope] = fields
            continue
        for field, value in fields.items():
            destination = {
                "method_assumptions": scenario,
                "method_limitations": limitations,
                "source_provenance": provenance,
            }.get(field)
            if destination is None:
                other_shared.setdefault(scope, {})[field] = value
            else:
                if field == "source_provenance" and isinstance(value, str):
                    try:
                        decoded = json.loads(value)
                    except json.JSONDecodeError:
                        pass
                    else:
                        if isinstance(decoded, (Mapping, list)):
                            value = decoded
                destination.setdefault(scope, {})[field] = value
    if other_shared:
        shared["shared_source_fields"] = other_shared

    known_top_level = {
        "source_metadata",
        "shared_field_note",
        "shared_source_fields",
        "prospective scenario assumptions by horizon",
    }
    for key, value in metadata.items():
        if key not in known_top_level:
            shared[key] = value
    if "prospective scenario assumptions by horizon" in metadata:
        horizon_assumptions = metadata["prospective scenario assumptions by horizon"]

    sections = (
        ("Shared source fields", shared),
        ("Constructed no-receipt scenario assumption", scenario),
        ("Method limitations", limitations),
        ("Source provenance", provenance),
        ("Horizon-specific assumptions", horizon_assumptions),
    )

    section_lines = [
        (
            heading,
            [
                line
                for key, value in content.items()
                for line in _metadata_entries(key, value)
            ],
        )
        for heading, content in sections
    ]
    wrap_width = 140
    wrapped = [
        (
            heading,
            [part for line in lines for part in _wrap_metadata_line(line, wrap_width)],
        )
        for heading, lines in section_lines
    ]
    body_line_points = 15.0
    heading_points = 19.0
    section_gap_points = 8.0
    required_points = sum(
        heading_points + max(1, len(lines)) * body_line_points + section_gap_points
        for _, lines in wrapped
    )
    figure_height = max(8.0, (required_points + 100.0) / (72.0 * 0.90))
    figure = Figure(figsize=(18.0, figure_height))
    FigureCanvasAgg(figure)
    figure.suptitle(title, fontsize=12)
    axis = figure.add_axes((0.035, 0.035, 0.93, 0.90))
    axis.axis("off")
    content_height_points = figure_height * 72.0 * 0.90
    y = 1.0
    for heading, lines in wrapped:
        axis.text(
            0.0,
            y,
            heading,
            va="top",
            ha="left",
            transform=axis.transAxes,
            fontsize=11,
            fontweight="bold",
        )
        y -= heading_points / content_height_points
        body = "\n".join(lines) if lines else ""
        if body:
            axis.text(
                0.012,
                y,
                body,
                va="top",
                ha="left",
                transform=axis.transAxes,
                fontsize=9,
                family="sans-serif",
                linespacing=1.15,
            )
        y -= max(1, len(lines)) * body_line_points / content_height_points
        y -= section_gap_points / content_height_points
    return figure


def _metadata_context(
    source: Any,
    scopes: Mapping[str, Mapping[str, Any]],
    **additional: Any,
) -> dict[str, Any]:
    return {
        "source_metadata": source,
        "shared_source_fields": {
            scope: dict(fields) for scope, fields in scopes.items() if fields
        },
        "shared_field_note": (
            "Shared source-field values are shown once only when identical in every "
            "record of the named projection; case records and source values are unchanged."
        ),
        **additional,
    }


def _table_figures(
    title: str,
    heading: str,
    rows: Sequence[Mapping[str, Any]],
    *,
    notes: str = "",
    columns: Sequence[str] | None = None,
    rows_per_page: int | None = None,
    table_fontsize: float | None = None,
) -> tuple[Figure, ...]:
    """Render a row population in coordinated column panels and ordered pages."""
    selected_columns = tuple(columns or _columns(rows))
    panels = _table_panels(selected_columns)
    figures: list[Figure] = []
    for panel_index, panel_columns in enumerate(panels, start=1):
        panel_title = f"{title} — Panel {panel_index}/{len(panels)}"
        figures.extend(
            _figure_pages(
                panel_title,
                ((heading, panel_columns, rows),),
                notes=notes,
                rows_per_page=rows_per_page,
                table_fontsize=table_fontsize,
            )
        )
    return tuple(figures)


def _horizon(row: Mapping[str, Any]) -> int:
    return int(row["horizon"])


def _rows_at_horizon(
    rows: Sequence[Mapping[str, Any]], horizon: int
) -> list[Mapping[str, Any]]:
    return [row for row in rows if _horizon(row) == horizon]


def _figure(
    title: str,
    sections: Sequence[tuple[str, Sequence[str], Sequence[Mapping[str, Any]]]],
    *,
    notes: str = "",
    table_fontsize: float | None = None,
) -> Figure:
    """Create a headless figure containing source-backed tables."""
    row_count = sum(max(1, len(rows)) for _, _, rows in sections)
    column_count = max((len(columns) for _, columns, _ in sections), default=1)
    has_h28_gate_table = any(
        tuple(columns) == _H28_FIELDS for _, columns, _ in sections
    )
    has_h28_identity_table = any(
        tuple(columns) == _H28_IDENTITY_FIELDS for _, columns, _ in sections
    )
    has_h28_layout = has_h28_gate_table or has_h28_identity_table
    content_width = max(
        (
            sum(min(52, max(8, len(column))) for column in columns)
            for _, columns, _ in sections
        ),
        default=column_count * 8,
    )
    width = (
        36.0
        if has_h28_gate_table
        else 13.0
        if has_h28_identity_table
        else max(18.0, min(36.0, 8.0 + content_width * 0.08))
    )
    line_counts_by_section: list[list[int]] = []
    if not has_h28_layout:
        for _, columns, rows in sections:
            if not columns:
                line_counts_by_section.append([1] * max(1, len(rows)))
                continue
            _, wrap_widths = _column_widths(columns, rows, width)
            line_counts_by_section.append(
                [
                    max(
                        (
                            len(
                                _hard_wrap(
                                    _display(row.get(column)), wrap_width
                                ).splitlines()
                            )
                            for column, wrap_width in zip(
                                columns, wrap_widths, strict=True
                            )
                        ),
                        default=1,
                    )
                    for row in rows
                ]
                or [1]
            )
    else:
        line_counts_by_section = [[1] * max(1, len(rows)) for _, _, rows in sections]

    section_visual_lines = [sum(row_lines) + 1 for row_lines in line_counts_by_section]
    total_visual_lines = sum(section_visual_lines) or 1
    if has_h28_layout:
        row_count = sum(max(1, len(rows)) for _, _, rows in sections)
        height = max(4.5, 2.6 + row_count * 0.16)
    else:
        height = max(4.5, 2.6 + total_visual_lines * 0.16)
    # These figures contain one table per axis. Default subplot spacing leaves
    # room for the title without constrained-layout's repeated text-measurement
    # passes over every table cell during savefig().
    figure = Figure(figsize=(width, height))
    FigureCanvasAgg(figure)
    suptitle = figure.suptitle(
        f"{title}\n{notes}" if has_h28_layout and notes else title, fontsize=12
    )
    suptitle.set_wrap(True)
    if notes and not has_h28_layout:
        figure.text(0.02, 0.94, notes, ha="left", va="top", fontsize=8, wrap=True)
    grid = figure.add_gridspec(
        max(1, len(sections)),
        1,
        height_ratios=section_visual_lines if sections else [1],
    )

    for index, (heading, columns, rows) in enumerate(sections):
        axis = figure.add_subplot(grid[index, 0])
        axis.set_title(heading, loc="left", fontsize=9, pad=4)
        axis.title.set_wrap(True)
        axis.axis("off")
        if not columns:
            axis.text(0.01, 0.8, "No source fields supplied.", transform=axis.transAxes)
            continue
        column_widths, wrap_widths = _column_widths(columns, rows, width)
        cell_text = [
            [
                _display(row.get(column))
                if has_h28_layout
                else _hard_wrap(_display(row.get(column)), wrap_width)
                for column, wrap_width in zip(columns, wrap_widths, strict=True)
            ]
            for row in rows
        ]
        display_columns = [
            column if has_h28_layout else _hard_wrap(column, wrap_width)
            for column, wrap_width in zip(columns, wrap_widths, strict=True)
        ]
        if tuple(columns) == _H28_FIELDS:
            total_width = sum(_H28_COLUMN_WIDTHS)
            column_widths = [width / total_width for width in _H28_COLUMN_WIDTHS]
        table = axis.table(
            cellText=cell_text,
            colLabels=display_columns,
            cellLoc="left",
            colLoc="left",
            loc="upper left",
            colWidths=column_widths,
        )
        if not has_h28_layout:
            row_lines = line_counts_by_section[index]
            section_lines = section_visual_lines[index] * 1.08
            for column in range(len(columns)):
                table.get_celld()[(0, column)].set_height(1 / section_lines)
            for row_index, line_count in enumerate(row_lines, start=1):
                for column in range(len(columns)):
                    table.get_celld()[(row_index, column)].set_height(
                        line_count / section_lines
                    )
        table.auto_set_font_size(False)
        table.set_fontsize(
            table_fontsize
            if table_fontsize is not None
            else 6.5
            if has_h28_layout or row_count < 60
            else 5.5
        )
        table.scale(1.0, 1.08)
        for cell in table.get_celld().values():
            cell.get_text().set_wrap(True)
    return figure


def _figure_pages(
    title: str,
    sections: Sequence[tuple[str, Sequence[str], Sequence[Mapping[str, Any]]]],
    *,
    notes: str = "",
    rows_per_page: int | None = None,
    table_fontsize: float | None = None,
) -> tuple[Figure, ...]:
    """Paginate table rows without changing their order, columns, or values."""
    page_size = rows_per_page or _MAX_TABLE_ROWS_PER_PAGE
    page_count = max(
        (
            max(
                1,
                (len(rows) + page_size - 1) // page_size,
            )
            for _, _, rows in sections
        ),
        default=1,
    )
    figures: list[Figure] = []
    for page_index in range(page_count):
        start = page_index * page_size
        stop = start + page_size
        page_sections = []
        for heading, columns, rows in sections:
            page_rows = rows[start:stop]
            if page_rows or page_index == 0:
                page_sections.append((heading, columns, page_rows))
        page_title = (
            title
            if page_count == 1
            else f"{title} — page {page_index + 1}/{page_count}"
        )
        figures.append(
            _figure(
                page_title,
                page_sections,
                notes=notes,
                table_fontsize=table_fontsize,
            )
        )
    return tuple(figures)


def _h28_panel_pages(
    title: str, rows: Sequence[Mapping[str, Any]]
) -> tuple[Figure, ...]:
    """Render coordinated h28 identity and downstream-gate panels."""
    identity_rows = [
        {field: row[field] for field in _H28_IDENTITY_FIELDS} for row in rows
    ]
    gate_rows = [{field: row[field] for field in _H28_FIELDS} for row in rows]
    panel_a = _figure_pages(
        f"{title} — Panel A: identity and target dates",
        (
            (
                "Approved identity and target-date fields",
                _H28_IDENTITY_FIELDS,
                identity_rows,
            ),
        ),
        notes=_H28_WARNING,
    )
    panel_b = _figure_pages(
        f"{title} — Panel B: downstream gate status and reason",
        (
            (
                "Identity, downstream_use_status, and downstream_use_reason",
                _H28_FIELDS,
                gate_rows,
            ),
        ),
        notes=_H28_WARNING,
    )
    return tuple(
        figure for pair in zip(panel_a, panel_b, strict=True) for figure in pair
    )


def render_exposure_coverage(view: Mapping[str, Any]) -> tuple[Figure, ...]:
    """Render horizon coverage, separate evaluation counts, and h28 gate rows."""
    prospective = list(view["prospective_records"])
    evaluation = view["evaluation_only"]
    population_rows = sorted(view["horizon_population"], key=_horizon)
    summary_rows = sorted(evaluation["summary"], key=_horizon)
    prospective_method_rows = [row for row in prospective if _horizon(row) in _HORIZONS]
    evaluation_cases = list(evaluation["cases"])
    prospective_context = _shared_context(prospective_method_rows)
    evaluation_context = _shared_context(evaluation_cases)
    prospective_records = _without_shared_context(prospective, prospective_context)
    evaluation_records = _without_shared_context(evaluation_cases, evaluation_context)
    scenario_assumptions: dict[str, dict[str, Any]] = {}
    figures = list(
        _table_figures(
            "A. Exposure state and population coverage — prospective horizon population",
            "Prospective forecast population by origin and horizon (not pooled)",
            population_rows,
            notes=(
                f"Prospective population: {len(prospective)} records. "
                f"Retrospective evaluation population: {len(evaluation_cases)} cases. "
                "Horizons are not pooled."
            ),
        )
    )
    figures.extend(
        _table_figures(
            "A. Exposure state and population coverage — evaluation-only coverage",
            "Evaluation-only coverage and confusion counts; denominators remain source fields",
            summary_rows,
            notes="Evaluation population remains separate from the forecast export population.",
        )
    )

    for horizon in (*_HORIZONS, 28):
        rows = _rows_at_horizon(prospective_records, horizon)
        if not rows:
            continue
        if horizon == 28:
            # The builder's h28 projection is intentionally gate-only.
            rows = [{name: row[name] for name in _H28_FIELDS} for row in rows]
            title = "h28 retained forecast identity and downstream gate only"
            figures.extend(_h28_panel_pages(title, rows))
            continue
        else:
            title = f"Prospective exposure records — {_HORIZON_LABELS[horizon]}"
            columns = _columns(rows)
            repeated_assumption = _repeated_long_field(rows, "snapshot_assumption")
            if repeated_assumption is not None:
                horizon_label = _HORIZON_LABELS[horizon]
                scenario_assumptions[horizon_label] = {
                    "snapshot_assumption": repeated_assumption
                }
                rows = _reference_repeated_field(
                    rows,
                    "snapshot_assumption",
                    "Full snapshot_assumption is on the A source-metadata page "
                    f"for {horizon_label}.",
                )
        figures.extend(
            _table_figures(
                title,
                title,
                rows,
                columns=columns,
                notes=(
                    "Source-level method fields and full repeated scenario assumptions "
                    "are on the A source-metadata page."
                )
                if prospective_context or scenario_assumptions
                else "",
            )
        )

    for horizon in _HORIZONS:
        rows = _rows_at_horizon(evaluation_records, horizon)
        if rows:
            title = f"Evaluation-only exposure status and reasons — {_HORIZON_LABELS[horizon]}"
            figures.extend(
                _table_figures(
                    title,
                    title,
                    rows,
                    notes="Retrospective fields are restricted to this evaluation-labeled view.",
                )
            )
    figures.append(
        _exposure_metadata_figure(
            "A. Exposure state and population coverage — source metadata and shared method fields",
            _metadata_context(
                view["source"],
                {
                    "prospective h1/h7/h14 records": prospective_context,
                    "prospective scenario assumptions by horizon": scenario_assumptions,
                    "evaluation-only records": evaluation_context,
                },
            ),
        )
    )
    return tuple(figures)


def render_proxy_crossing_comparison(view: Mapping[str, Any]) -> tuple[Figure, ...]:
    """Render per-horizon retrospective proxy counts, metrics, and case rows."""
    figures: list[Figure] = []
    for horizon in _HORIZONS:
        summaries = [
            summary
            for summary in view["summaries"]
            if _horizon(summary["group"]) == horizon
        ]
        source_cases = list(view["cases"])
        shared = _shared_context(source_cases)
        cases = sorted(
            _rows_at_horizon(_without_shared_context(source_cases, shared), horizon),
            key=lambda row: _natural_identifier_key(str(row["SKU_ID"])),
        )
        if not summaries:
            continue
        summary = summaries[0]
        group = summary["group"]
        counts = summary["counts"]
        count_row = {**group, **counts}
        metric_rows = [
            {
                "metric": name,
                "value": values["value"],
                "denominator": values["denominator"],
                "status": values["status"],
            }
            for name, values in summary["metrics"].items()
        ]
        title = f"B. Retrospective proxy comparison — {_HORIZON_LABELS[horizon]}"
        notes = (
            f"{view['label']} This is not an observed-stockout result. "
            "TP: both cross; TN: neither crosses; FN: proxy crosses only; "
            "FP: forecast crosses only."
        )
        figures.extend(
            _table_figures(
                f"{title} — existing counts",
                "Existing counts and evaluator grouping",
                [count_row],
                notes=notes,
            )
        )
        figures.extend(
            _table_figures(
                f"{title} — existing metrics",
                "Existing metrics with source denominator and status",
                metric_rows,
            )
        )
        figures.extend(
            _table_figures(
                f"{title} — evaluation-only case records",
                "Evaluation-only case identity, outcomes, statuses and provenance",
                cases,
                notes=(
                    "Long identical source assumptions and limitations are shown on the "
                    "B source-metadata page."
                    if shared
                    else ""
                ),
                rows_per_page=36,
                table_fontsize=7.0,
            )
        )
    figures.append(
        _metadata_figure(
            "B. Retrospective proxy comparison — source metadata and shared caveats",
            _metadata_context(
                view["source"],
                {"evaluation-only case records": _shared_context(list(view["cases"]))},
                proxy_label=view["label"],
            ),
        )
    )
    return tuple(figures)


def render_margin_comparison(view: Mapping[str, Any]) -> tuple[Figure, ...]:
    """Render distinct prospective and evaluation margin tables per horizon."""
    figures: list[Figure] = []
    prospective = list(view["prospective"]["records"])
    retrospective = list(view["evaluation_only"]["records"])
    prospective_context = _shared_context(
        [row for row in prospective if _horizon(row) in _HORIZONS]
    )
    retrospective_context = _shared_context(retrospective)
    prospective = _without_shared_context(prospective, prospective_context)
    retrospective = _without_shared_context(retrospective, retrospective_context)
    notes = (
        f"Zero is the existing reorder-reference boundary; {view['reference_meaning']} "
        "Null margins remain null and are not placed on either side of zero."
    )
    for horizon in _HORIZONS:
        prospective_rows = _rows_at_horizon(prospective, horizon)
        evaluation_rows = _rows_at_horizon(retrospective, horizon)
        if not prospective_rows and not evaluation_rows:
            continue
        title = f"C. Margin comparison — {_HORIZON_LABELS[horizon]}"
        figures.extend(
            _table_figures(
                f"{title} — prospective records",
                "Prospective predicted_margin (buffer − forecast demand)",
                prospective_rows,
                notes=notes,
            )
        )
        figures.extend(
            _table_figures(
                f"{title} — evaluation-only records",
                "Evaluation-only retrospective_margin (buffer − realised Units_Sold)",
                evaluation_rows,
                notes=notes,
            )
        )
    figures.append(
        _metadata_figure(
            "C. Margin comparison — source metadata and shared caveats",
            _metadata_context(
                {
                    "reference_value": view["reference_value"],
                    "reference_meaning": view["reference_meaning"],
                },
                {
                    "prospective records": prospective_context,
                    "evaluation-only records": retrospective_context,
                },
            ),
        )
    )
    return tuple(figures)


def render_availability_provenance(view: Mapping[str, Any]) -> tuple[Figure, ...]:
    """Render per-horizon availability/provenance, with h28 identity/gate only."""
    prospective = list(view["prospective"]["records"])
    evaluation = list(view["evaluation_only"]["records"])
    prospective_context = _shared_context(
        [row for row in prospective if _horizon(row) in _HORIZONS]
    )
    evaluation_context = _shared_context(evaluation)
    prospective = _without_shared_context(prospective, prospective_context)
    evaluation = _without_shared_context(evaluation, evaluation_context)
    scenario_assumptions: dict[str, dict[str, Any]] = {}
    figures: list[Figure] = []
    for horizon in _HORIZONS:
        prospective_rows = _rows_at_horizon(prospective, horizon)
        evaluation_rows = _rows_at_horizon(evaluation, horizon)
        if not prospective_rows and not evaluation_rows:
            continue
        title = f"D. Availability and provenance — {_HORIZON_LABELS[horizon]}"
        repeated_assumption = _repeated_long_field(
            prospective_rows, "snapshot_assumption"
        )
        if repeated_assumption is not None:
            horizon_label = _HORIZON_LABELS[horizon]
            scenario_assumptions[horizon_label] = {
                "snapshot_assumption": repeated_assumption
            }
            prospective_rows = _reference_repeated_field(
                prospective_rows,
                "snapshot_assumption",
                "Full snapshot_assumption is on the D source-metadata page "
                f"for {horizon_label}.",
            )
        figures.extend(
            _table_figures(
                f"{title} — prospective records",
                "Prospective source/scenario availability and provenance",
                prospective_rows,
                notes=f"Dataset provenance SHA-256: {view['dataset_provenance_sha256']}",
            )
        )
        figures.extend(
            _table_figures(
                f"{title} — evaluation-only records",
                "Evaluation-only status, reasons and provenance",
                evaluation_rows,
            )
        )

    gated_rows = _rows_at_horizon(prospective, 28)
    if gated_rows:
        gated_rows = [{name: row[name] for name in _H28_FIELDS} for row in gated_rows]
        figures.extend(
            _h28_panel_pages(
                "D. h28 retained forecast identity and downstream gate only",
                gated_rows,
            )
        )
    figures.append(
        _metadata_figure(
            "D. Availability and provenance — source metadata and shared caveats",
            _metadata_context(
                view["source"],
                {
                    "prospective h1/h7/h14 records": prospective_context,
                    "prospective scenario assumptions by horizon": scenario_assumptions,
                    "evaluation-only records": evaluation_context,
                },
                current_method_approval=view.get("current_method_approval", {}),
                dataset_provenance_sha256=view["dataset_provenance_sha256"],
            ),
        )
    )
    return tuple(figures)
