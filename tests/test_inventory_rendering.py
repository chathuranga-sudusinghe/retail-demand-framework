"""Synthetic contract tests for the static inventory-view renderers."""

from __future__ import annotations

from copy import deepcopy

import pytest

from src.visualization.inventory_rendering import (
    render_availability_provenance,
    render_exposure_coverage,
    render_margin_comparison,
    render_proxy_crossing_comparison,
)
from src.visualization.render_issue_201_views import render_issue_201

_H28_IDENTITY_FIELDS = (
    "SKU_ID",
    "Warehouse_ID",
    "forecast_origin",
    "horizon",
    "target_start_date",
    "target_end_date",
)
_H28_GATE_FIELDS = _H28_IDENTITY_FIELDS + (
    "downstream_use_status",
    "downstream_use_reason",
)


def _texts(figures):
    values = []
    for figure in figures:
        values.extend(text.get_text() for text in figure.texts)
        for axis in figure.axes:
            values.extend(
                title
                for location in ("left", "center", "right")
                if (title := axis.get_title(loc=location))
            )
            values.extend(text.get_text() for text in axis.texts)
            for table in axis.tables:
                for cell in table.get_celld().values():
                    values.append(cell.get_text().get_text())
    return "\n".join(values)


def _first_table_headers(figure):
    table = figure.axes[0].tables[0]
    return tuple(
        cell.get_text().get_text()
        for (row, _column), cell in sorted(table.get_celld().items())
        if row == 0
    )


def _h28_panels(figures):
    h28_figures = tuple(
        figure
        for figure in figures
        if "h28 retained forecast identity" in figure.get_suptitle()
    )
    return (
        tuple(figure for figure in h28_figures if "Panel A:" in figure.get_suptitle()),
        tuple(figure for figure in h28_figures if "Panel B:" in figure.get_suptitle()),
    )


def _h28_identity_rows(figures):
    columns = [_table_column_values(figures, field) for field in _H28_IDENTITY_FIELDS]
    return list(zip(*columns, strict=True))


def _table_column_width(figure, header):
    cells = figure.axes[0].tables[0].get_celld()
    column = next(
        index
        for (row, index), cell in cells.items()
        if row == 0 and cell.get_text().get_text() == header
    )
    return cells[(1, column)].get_width()


def _table_column_values(
    figures, header, *, section_heading=None, panel=None, preserve_wrapping=False
):
    values = []
    for figure in figures:
        if panel is not None and f"Panel {panel}/" not in figure.get_suptitle():
            continue
        for axis in figure.axes:
            if (
                section_heading is not None
                and axis.get_title(loc="left") != section_heading
            ):
                continue
            for table in axis.tables:
                cells = table.get_celld()
                columns = {
                    column: cell.get_text().get_text()
                    for (row, column), cell in cells.items()
                    if row == 0
                }
                column = next(
                    (index for index, value in columns.items() if value == header),
                    None,
                )
                if column is None:
                    continue
                row_indexes = sorted(
                    {row for row, cell_column in cells if cell_column == column and row}
                )
                for row in row_indexes:
                    value = cells[(row, column)].get_text().get_text()
                    values.append(
                        value if preserve_wrapping else value.replace("\n", "")
                    )
    return values


def _identity(horizon):
    return {
        "SKU_ID": f"SKU_{horizon}",
        "Warehouse_ID": "WH_1",
        "forecast_origin": "2024-12-02",
        "horizon": horizon,
        "target_start_date": "2024-12-03",
        "target_end_date": {
            1: "2024-12-03",
            7: "2024-12-09",
            14: "2024-12-16",
            28: "2024-12-30",
        }[horizon],
    }


def _exposure_view():
    prospective = []
    for horizon in (1, 7, 14):
        prospective.append(
            {
                **_identity(horizon),
                "origin_exposure_state": "scenario_initially_above_threshold",
                "forecast_exposure_state": "no_forecast_crossing",
                "inventory_state_available": False,
                "origin_snapshot_status": "unknown",
                "origin_snapshot_reason": "",
                "method_assumptions": ["constructed-origin; no receipts"],
                "method_limitations": ["source timing unknown"],
            }
        )
    prospective.append(
        {
            **_identity(28),
            "downstream_use_status": "not_approved_for_downstream_use",
            "downstream_use_reason": "28_day_downstream_use_requires_separate_approval",
        }
    )
    summaries = [
        {
            "horizon": horizon,
            "N": 239,
            "TP": 5,
            "TN": 230,
            "FP": 0,
            "FN": 4,
            "origin_known_at_or_below_count": 0,
            "scenario_at_or_below_count": 11,
            "initially_above_threshold_count": 239,
            "evaluable_paired_case_count": 239,
            "unavailable_case_count": 0,
            "forecast_unavailable_or_gated_count": 0,
            "retrospective_unavailable_or_gated_count": 0,
        }
        for horizon in (1, 7, 14)
    ]
    return {
        "source": {"snapshot_policy": "unknown", "snapshot_basis": "not verified"},
        "horizon_population": [
            {
                "forecast_origin": "2024-12-02",
                "horizon": horizon,
                "horizon_forecast_population_count": 250,
            }
            for horizon in (1, 7, 14, 28)
        ],
        "prospective_records": prospective,
        "evaluation_only": {
            "summary": summaries,
            "cases": [
                {
                    **_identity(horizon),
                    "comparison_case": "evaluable_paired_case",
                    "retrospective_exposure_state": "realised_crossing",
                    "retrospective_input_status": "available",
                    "retrospective_input_reason": "",
                    "target_status": "complete",
                    "target_unavailable_reason": "",
                    "evaluation_unavailable_reasons": [],
                }
                for horizon in (1, 7, 14)
            ],
        },
    }


def _proxy_view():
    metric_names = (
        "event_prevalence",
        "missed_crossing_rate",
        "false_alert_rate",
        "agreement",
        "precision",
        "recall",
        "balanced_accuracy",
    )
    summaries = [
        {
            "group": {"forecast_origin": "2024-12-02", "horizon": horizon},
            "counts": {"N": 239, "TP": 5, "TN": 230, "FP": 0, "FN": 4},
            "metrics": {
                name: {
                    "value": None if name == "precision" else 0.0,
                    "denominator": 0 if name == "precision" else 239,
                    "status": "unavailable" if name == "precision" else "available",
                }
                for name in metric_names
            },
        }
        for horizon in (1, 7, 14)
    ]
    summaries.append(
        {
            "group": {"forecast_origin": "2024-12-02", "horizon": 28},
            "counts": {"N": 999, "TP": 999, "TN": 0, "FP": 0, "FN": 0},
            "metrics": {},
        }
    )
    cases = [
        {
            **_identity(horizon),
            "comparison_case": "evaluable_paired_case",
            "confusion_cell": "TN",
            "target_status": "complete",
            "target_unavailable_reason": "",
            "evaluation_unavailable_reasons": [],
            "method_assumptions": ["same target window"],
            "method_limitations": ["not observed stockout"],
        }
        for horizon in (1, 7, 14)
    ]
    cases.append({**_identity(28), "confusion_cell": "PROHIBITED_H28_PROXY"})
    return {
        "label": "Retrospective threshold-crossing proxy based on Units_Sold; not observed stockout.",
        "source": {"run_id": "synthetic-run", "evaluation_stage": "final_evaluation"},
        "summaries": summaries,
        "cases": cases,
    }


def _margin_view():
    prospective = [
        {
            **_identity(horizon),
            "inventory_buffer": 0,
            "predicted_margin": None if horizon == 1 else 0,
            "forecast_input_status": "available",
            "forecast_input_reason": "",
            "methodology_status": "approved",
            "method_assumptions": ["no receipts"],
            "method_limitations": ["constructed scenario"],
        }
        for horizon in (1, 7, 14)
    ]
    evaluation = [
        {
            **_identity(horizon),
            "inventory_buffer": 0,
            "retrospective_margin": None if horizon == 1 else 0,
            "retrospective_input_status": "available",
            "retrospective_input_reason": "",
            "target_status": "complete",
            "target_unavailable_reason": "",
            "evaluation_unavailable_reasons": [],
            "method_assumptions": ["same target window"],
            "method_limitations": ["retrospective only"],
        }
        for horizon in (1, 7, 14)
    ]
    prospective.append({**_identity(28), "predicted_margin": "PROHIBITED_H28_MARGIN"})
    evaluation.append(
        {**_identity(28), "retrospective_margin": "PROHIBITED_H28_MARGIN"}
    )
    return {
        "reference_value": 0,
        "reference_meaning": "Existing reorder-reference boundary; no tolerance band.",
        "prospective": {"records": prospective},
        "evaluation_only": {"records": evaluation},
    }


def _availability_view():
    prospective = []
    for horizon, status, available in (
        (1, "unknown", None),
        (7, "unavailable", False),
        (14, "not_assessed", None),
    ):
        prospective.append(
            {
                **_identity(horizon),
                "prediction": 12,
                "forecast_status": "available",
                "producer_status": "designated_producer",
                "origin_snapshot_available": available,
                "origin_snapshot_status": status,
                "origin_snapshot_reason": "synthetic reason" if not available else "",
                "inventory_state_available": False,
                "scenario_inventory_state_available": True,
                "analysis_inventory_state_available": True,
                "downstream_use_status": "accepted",
                "downstream_use_reason": "",
                "source_export_sha256": "a" * 64,
                "method_assumptions": ["constructed-origin"],
                "method_limitations": ["source timing unknown"],
            }
        )
    prospective.append(
        {
            **_identity(28),
            "downstream_use_status": "not_approved_for_downstream_use",
            "downstream_use_reason": "28_day_downstream_use_requires_separate_approval",
        }
    )
    return {
        "source": {"snapshot_policy": "unknown", "snapshot_basis": "not verified"},
        "dataset_provenance_sha256": "b" * 64,
        "prospective": {"records": prospective},
        "evaluation_only": {
            "records": [
                {
                    **_identity(horizon),
                    "prediction_status": "available",
                    "eligibility_status": "eligible",
                    "target_status": "complete",
                    "target_unavailable_reason": "",
                    "evaluation_unavailable_reasons": [],
                    "method_assumptions": ["same target window"],
                    "method_limitations": ["retrospective only"],
                }
                for horizon in (1, 7, 14)
            ]
        },
    }


def test_exposure_rendering_keeps_populations_horizons_and_h28_gate_separate():
    view = _exposure_view()
    figures = render_exposure_coverage(view)
    rendered = _texts(figures)

    assert "Prospective forecast population" in rendered
    assert "Evaluation-only coverage" in rendered
    assert "Prospective population: 4 records" in rendered
    assert "Retrospective evaluation population: 3 cases" in rendered
    assert "horizon_forecast_population_count" in rendered
    assert "250" in rendered
    assert "239" in rendered
    assert "h1 next-day" in rendered
    assert "h7 cumulative" in rendered
    assert "h14 cumulative" in rendered
    panel_a, panel_b = _h28_panels(figures)
    assert len(panel_a) == len(panel_b) == 1
    panel_a_text = _texts(panel_a)
    panel_b_text = _texts(panel_b)
    assert _first_table_headers(panel_a[0]) == _H28_IDENTITY_FIELDS
    assert _first_table_headers(panel_b[0]) == _H28_GATE_FIELDS
    assert "downstream-gated" in panel_a[0].get_suptitle()
    assert "downstream-gated" in panel_b[0].get_suptitle()
    assert "SKU_28" in panel_a_text and "SKU_28" in panel_b_text
    assert "not_approved_for_downstream_use" not in panel_a_text
    assert "downstream_use_status" not in panel_a_text
    assert "not_approved_for_downstream_use" in panel_b_text
    assert "28_day_downstream_use_requires_separate_approval" in panel_b_text
    assert "downstream_use_status" in panel_b_text
    assert "downstream_use_reason" in panel_b_text
    assert _h28_identity_rows(panel_a) == _h28_identity_rows(panel_b)
    assert "Inventory_Level" not in panel_a_text + panel_b_text
    assert "predicted_margin" not in panel_a_text + panel_b_text
    assert "retrospective_margin" not in panel_a_text + panel_b_text
    assert "confusion_cell" not in panel_a_text + panel_b_text
    assert "observed_target" not in panel_a_text + panel_b_text
    assert "retrospective_exposure_state" not in panel_a_text + panel_b_text


def test_exposure_horizon_tables_render_in_ascending_order_without_mutation():
    view = _exposure_view()
    view["horizon_population"] = [
        *reversed(view["horizon_population"][:3]),
        view["horizon_population"][3],
    ]
    view["evaluation_only"]["summary"] = [
        view["evaluation_only"]["summary"][1],
        view["evaluation_only"]["summary"][0],
        view["evaluation_only"]["summary"][2],
    ]
    population_order_before = [row["horizon"] for row in view["horizon_population"]]
    evaluation_order_before = [
        row["horizon"] for row in view["evaluation_only"]["summary"]
    ]

    figures = render_exposure_coverage(view)
    prospective_figures = tuple(
        figure
        for figure in figures
        if "prospective horizon population" in figure.get_suptitle()
    )
    evaluation_figures = tuple(
        figure
        for figure in figures
        if "evaluation-only coverage" in figure.get_suptitle()
    )

    assert _table_column_values(prospective_figures, "horizon") == [
        "1",
        "7",
        "14",
        "28",
    ]
    assert len(evaluation_figures) == 2
    for panel in (1, 2):
        assert _table_column_values(evaluation_figures, "horizon", panel=panel) == [
            "1",
            "7",
            "14",
        ]
    assert [row["horizon"] for row in view["horizon_population"]] == (
        population_order_before
    )
    assert [row["horizon"] for row in view["evaluation_only"]["summary"]] == (
        evaluation_order_before
    )


def test_proxy_rendering_keeps_existing_metric_denominators_statuses_and_label():
    figures = render_proxy_crossing_comparison(_proxy_view())
    assert any("existing counts" in figure.get_suptitle() for figure in figures)
    assert any("existing metrics" in figure.get_suptitle() for figure in figures)
    rendered = _texts(figures)

    assert "Retrospective threshold-crossing proxy based on Units_Sold" in rendered
    assert "not observed stockout" in rendered
    assert "denominator" in rendered
    assert "status" in rendered
    assert "unavailable" in rendered
    assert "0" in rendered
    assert "239" in rendered
    assert all("h28" not in figure._suptitle.get_text() for figure in figures)
    assert "confusion_cell" in rendered
    assert "method_limitations" in rendered
    assert "PROHIBITED_H28_PROXY" not in rendered


def test_proxy_case_records_sort_naturally_and_paginate_without_mutation():
    view = _proxy_view()
    view["summaries"] = [view["summaries"][0]]
    lexical_skus = sorted(f"SKU_{number}" for number in range(1, 51))
    warehouse_ids = [f"WH_{number}" for number in range(1, 6)]
    cases = [
        {
            **_identity(1),
            "SKU_ID": sku_id,
            "Warehouse_ID": warehouse_id,
            "comparison_case": "evaluable_paired_case",
            "confusion_cell": "TN",
            "target_status": "complete",
            "target_unavailable_reason": "",
            "evaluation_unavailable_reasons": [],
            **{
                f"source_field_{field}": f"{sku_id}-{warehouse_id}-{field}"
                for field in range(10)
            },
        }
        for sku_id in lexical_skus
        for warehouse_id in warehouse_ids
    ]
    view["cases"] = cases
    original_view = deepcopy(view)

    figures = render_proxy_crossing_comparison(view)
    case_figures = tuple(
        figure
        for figure in figures
        if "evaluation-only case records" in figure.get_suptitle()
    )
    panel_figures = {
        panel: tuple(
            figure
            for figure in case_figures
            if f"Panel {panel}/" in figure.get_suptitle()
        )
        for panel in (1, 2)
    }
    expected_identities = [
        (sku_id, warehouse_id)
        for sku_number in range(1, 51)
        for warehouse_id in warehouse_ids
        for sku_id in (f"SKU_{sku_number}",)
    ]

    for panel, pages in panel_figures.items():
        assert len(pages) == 7
        assert [
            max(row for row, _column in figure.axes[0].tables[0].get_celld() if row > 0)
            for figure in pages
        ] == [36, 36, 36, 36, 36, 36, 34]
        sku_ids = _table_column_values(
            pages,
            "SKU_ID",
            section_heading="Evaluation-only case identity, outcomes, statuses and provenance",
            panel=panel,
        )
        warehouse_ids_rendered = _table_column_values(
            pages,
            "Warehouse_ID",
            section_heading="Evaluation-only case identity, outcomes, statuses and provenance",
            panel=panel,
        )
        assert list(zip(sku_ids, warehouse_ids_rendered, strict=True)) == (
            expected_identities
        )
        assert len(set(zip(sku_ids, warehouse_ids_rendered, strict=True))) == 250
        assert all(
            figure.axes[0].tables[0].get_celld()[(1, 0)].get_text().get_fontsize()
            == 7.0
            for figure in pages
        )

    count_figure = next(
        figure for figure in figures if "existing counts" in figure.get_suptitle()
    )
    metric_figure = next(
        figure for figure in figures if "existing metrics" in figure.get_suptitle()
    )
    assert (
        count_figure.axes[0].tables[0].get_celld()[(1, 0)].get_text().get_fontsize()
        == 6.5
    )
    assert (
        metric_figure.axes[0].tables[0].get_celld()[(1, 0)].get_text().get_fontsize()
        == 6.5
    )
    assert view == original_view


def test_margin_rendering_keeps_null_zero_and_prospective_evaluation_separate():
    figures = render_margin_comparison(_margin_view())
    assert any("prospective records" in figure.get_suptitle() for figure in figures)
    assert any("evaluation-only records" in figure.get_suptitle() for figure in figures)
    rendered = _texts(figures)

    assert "Prospective predicted_margin" in rendered
    assert "Evaluation-only retrospective_margin" in rendered
    assert "null" in rendered
    assert "0" in rendered
    assert "Existing reorder-reference boundary; no tolerance band." in rendered
    assert all("h28" not in figure._suptitle.get_text() for figure in figures)
    assert "PROHIBITED_H28_MARGIN" not in rendered
    assert any(
        "retrospective_margin" in _texts((figure,))
        for figure in figures
        if "evaluation-only records" in figure.get_suptitle()
    )
    assert "predicted_margin" in _texts((figures[0],))


def test_availability_rendering_preserves_states_provenance_and_gate_only_h28():
    figures = render_availability_provenance(_availability_view())
    assert any("source metadata" in figure.get_suptitle() for figure in figures)
    rendered = _texts(figures)

    assert "unknown" in rendered
    assert "unavailable" in rendered
    assert "not_assessed" in rendered
    assert "accepted" in rendered
    assert "not_approved_for_downstream_use" in rendered
    assert "false" in rendered
    assert "scenario_inventory_state_available" in rendered
    assert "Dataset provenance SHA-256" in rendered
    assert "b" * 64 in rendered
    assert "method_assumptions" in rendered
    assert "method_limitations" in rendered
    panel_a, panel_b = _h28_panels(figures)
    assert len(panel_a) == len(panel_b) == 1
    panel_a_text = _texts(panel_a)
    panel_b_text = _texts(panel_b)
    assert _first_table_headers(panel_a[0]) == _H28_IDENTITY_FIELDS
    assert _first_table_headers(panel_b[0]) == _H28_GATE_FIELDS
    assert "downstream-gated" in panel_a[0].get_suptitle()
    assert "downstream-gated" in panel_b[0].get_suptitle()
    assert "not_approved_for_downstream_use" not in panel_a_text
    assert "not_approved_for_downstream_use" in panel_b_text
    assert "Inventory_Level" not in panel_a_text + panel_b_text
    assert "inventory_buffer" not in panel_a_text + panel_b_text
    assert "predicted_margin" not in panel_a_text + panel_b_text
    assert "retrospective_margin" not in panel_a_text + panel_b_text
    assert "confusion_cell" not in panel_a_text + panel_b_text
    assert _h28_identity_rows(panel_a) == _h28_identity_rows(panel_b)


def test_renderers_do_not_mutate_builder_outputs():
    views = (
        _exposure_view(),
        _proxy_view(),
        _margin_view(),
        _availability_view(),
    )
    before = deepcopy(views)
    render_exposure_coverage(views[0])
    render_proxy_crossing_comparison(views[1])
    render_margin_comparison(views[2])
    render_availability_provenance(views[3])
    assert views == before


def test_exposure_pagination_preserves_every_row_once_in_source_order():
    view = _exposure_view()
    rows = [
        {
            **_identity(1),
            "SKU_ID": f"SYN_{index:03d}",
            "origin_exposure_state": "scenario_initially_above_threshold",
            "forecast_exposure_state": "no_forecast_crossing",
            "inventory_state_available": False,
        }
        for index in range(93)
    ]
    view["prospective_records"] = rows
    view["horizon_population"] = [
        {
            "forecast_origin": "2024-12-02",
            "horizon": 1,
            "horizon_forecast_population_count": len(rows),
        }
    ]
    view["evaluation_only"] = {"summary": [], "cases": []}

    figures = render_exposure_coverage(view)
    pages = tuple(
        figure
        for figure in figures
        if "Prospective exposure records" in figure.get_suptitle()
    )
    rendered_ids = _table_column_values(pages, "SKU_ID", panel=1)
    expected_ids = [row["SKU_ID"] for row in rows]

    assert len(pages) > 1
    assert rendered_ids == expected_ids
    assert len(rendered_ids) == len(set(rendered_ids))
    assert all("page " in figure.get_suptitle() for figure in pages)


def test_margin_pagination_keeps_both_populations_complete_and_separate():
    view = _margin_view()
    prospective = [
        {
            **_identity(1),
            "SKU_ID": f"P_{index:03d}",
            "inventory_buffer": index,
            "predicted_margin": index,
        }
        for index in range(93)
    ]
    evaluation = [
        {
            **_identity(1),
            "SKU_ID": f"E_{index:03d}",
            "inventory_buffer": index,
            "retrospective_margin": index,
        }
        for index in range(93)
    ]
    view["prospective"]["records"] = prospective
    view["evaluation_only"]["records"] = evaluation

    figures = render_margin_comparison(view)
    pages = tuple(
        figure for figure in figures if "h1 next-day" in figure.get_suptitle()
    )
    prospective_ids = _table_column_values(
        pages,
        "SKU_ID",
        section_heading="Prospective predicted_margin (buffer − forecast demand)",
        panel=1,
    )
    evaluation_ids = _table_column_values(
        pages,
        "SKU_ID",
        section_heading="Evaluation-only retrospective_margin (buffer − realised Units_Sold)",
        panel=1,
    )
    prospective_margins = _table_column_values(
        pages,
        "predicted_margin",
        section_heading="Prospective predicted_margin (buffer − forecast demand)",
    )
    evaluation_margins = _table_column_values(
        pages,
        "retrospective_margin",
        section_heading="Evaluation-only retrospective_margin (buffer − realised Units_Sold)",
    )

    assert len(pages) > 1
    assert prospective_ids == [row["SKU_ID"] for row in prospective]
    assert evaluation_ids == [row["SKU_ID"] for row in evaluation]
    assert prospective_margins == [str(row["predicted_margin"]) for row in prospective]
    assert evaluation_margins == [
        str(row["retrospective_margin"]) for row in evaluation
    ]
    assert len(prospective_ids) == len(set(prospective_ids))
    assert len(evaluation_ids) == len(set(evaluation_ids))


def test_case_table_panels_repeat_identity_and_preserve_every_field_value():
    view = _availability_view()
    base_rows = [
        {
            **_identity(1),
            "SKU_ID": f"SKU_{index:03d}",
            "prediction": index,
            "forecast_status": "available",
            "origin_snapshot_status": "unknown",
            "origin_snapshot_reason": "reason with complete text " + ("R" * 90),
            **{
                f"source_detail_{field}": f"row-{index}-value-{field}"
                for field in range(14)
            },
        }
        for index in range(43)
    ]
    view["prospective"]["records"] = base_rows
    view["evaluation_only"]["records"] = []
    figures = render_availability_provenance(view)
    heading = "Prospective source/scenario availability and provenance"
    pages = tuple(
        figure
        for figure in figures
        if heading in "\n".join(axis.get_title(loc="left") for axis in figure.axes)
    )
    panel_pages = {}
    for figure in pages:
        panel_number = int(figure.get_suptitle().split("Panel ", 1)[1].split("/", 1)[0])
        panel_pages.setdefault(panel_number, []).append(figure)

    expected_ids = [row["SKU_ID"] for row in base_rows]
    expected_source_fields = {field for row in base_rows for field in row}
    rendered_source_fields = set()
    panel_identity_rows = {}
    for panel_number, panel_figures in panel_pages.items():
        headers = tuple(
            field.replace("\n", "") for field in _first_table_headers(panel_figures[0])
        )
        rendered_source_fields.update(headers)
        panel_identity_rows[panel_number] = _table_column_values(
            panel_figures, "SKU_ID", panel=panel_number, section_heading=heading
        )
        assert panel_identity_rows[panel_number] == expected_ids
        assert len(panel_identity_rows[panel_number]) == len(set(expected_ids))
        for field in headers:
            expected_values = [
                "null"
                if row[field] is None
                else "false"
                if row[field] is False
                else "true"
                if row[field] is True
                else str(row[field])
                for row in base_rows
            ]
            assert (
                _table_column_values(
                    panel_figures,
                    field,
                    panel=panel_number,
                    section_heading=heading,
                )
                == expected_values
            )

    assert len(panel_pages) > 1
    assert rendered_source_fields == expected_source_fields
    assert all(rows == expected_ids for rows in panel_identity_rows.values())
    assert len(pages) > len(panel_pages)
    wrapped_reasons = _table_column_values(
        pages,
        "origin_snapshot_reason",
        panel=next(
            panel_number
            for panel_number, panel_figures in panel_pages.items()
            if "origin_snapshot_reason"
            in tuple(
                field.replace("\n", "")
                for field in _first_table_headers(panel_figures[0])
            )
        ),
        section_heading=heading,
        preserve_wrapping=True,
    )
    assert any("\n" in value for value in wrapped_reasons)
    assert [value.replace("\n", "") for value in wrapped_reasons] == [
        row["origin_snapshot_reason"] for row in base_rows
    ]


def test_wrapped_cell_rows_expand_without_losing_the_full_value():
    view = _availability_view()
    long_reason = "source reason " + ("complete detail " * 90)
    rows = [
        {
            **_identity(1),
            "SKU_ID": "SKU_LONG_REASON",
            "origin_snapshot_status": "unavailable",
            "origin_snapshot_reason": long_reason,
        },
        {
            **_identity(1),
            "SKU_ID": "SKU_SHORT_REASON",
            "origin_snapshot_status": "unknown",
            "origin_snapshot_reason": "short reason",
        },
    ]
    view["prospective"]["records"] = rows
    view["evaluation_only"]["records"] = []

    figures = render_availability_provenance(view)
    figure = next(
        figure
        for figure in figures
        if any(
            row == 0 and cell.get_text().get_text() == "origin_snapshot_reason"
            for axis in figure.axes
            for table in axis.tables
            for (row, _column), cell in table.get_celld().items()
        )
    )
    figure.canvas.draw()
    table = figure.axes[0].tables[0]
    reason_column = next(
        column
        for (row, column), cell in table.get_celld().items()
        if row == 0 and cell.get_text().get_text() == "origin_snapshot_reason"
    )
    long_cell = table.get_celld()[(1, reason_column)]
    short_cell = table.get_celld()[(2, reason_column)]
    displayed_long_reason = long_cell.get_text().get_text()

    assert "\n" in displayed_long_reason
    assert displayed_long_reason.replace("\n", "") == long_reason
    assert long_cell.get_height() > short_cell.get_height()
    assert long_cell.get_y() >= short_cell.get_y() + short_cell.get_height() - 1e-9


def test_repeated_snapshot_assumption_is_kept_verbatim_on_metadata_page():
    view = _exposure_view()
    assumption = "Constructed no-receipt assumption: " + ("full source wording " * 30)
    h1_rows = [row for row in view["prospective_records"] if row["horizon"] == 1]
    h1_rows[0]["snapshot_assumption"] = assumption
    second_h1 = {**h1_rows[0], "SKU_ID": "SKU_1_SECOND"}
    view["prospective_records"].append(second_h1)

    figures = render_exposure_coverage(view)
    metadata = next(
        figure for figure in figures if "source metadata" in figure.get_suptitle()
    )
    metadata_text = _texts((metadata,))
    h1_pages = tuple(
        figure
        for figure in figures
        if "Prospective exposure records — h1 next-day" in figure.get_suptitle()
    )
    assumption_cells = _table_column_values(h1_pages, "snapshot_assumption")

    assert assumption in metadata_text.replace("\n", "")
    assert "Horizon-specific assumptions" in metadata_text
    assert "Constructed no-receipt scenario assumption" in metadata_text
    assert (
        assumption_cells
        == [
            "Full snapshot_assumption is on the A source-metadata page for h1 next-day."
        ]
        * 2
    )
    assert [row["snapshot_assumption"] for row in h1_rows] == [assumption]
    assert second_h1["snapshot_assumption"] == assumption


def test_exposure_metadata_sections_wrap_and_preserve_all_source_values():
    view = _exposure_view()
    scenario_text = (
        "Constructed no-receipt scenario assumption; fixed reorder reference: "
        + ("source wording remains unchanged " * 18)
    )
    limitation = "Source inventory snapshot timing remains unknown. " + ("L" * 180)
    provenance_hash = "a" * 64
    provenance = (
        '{"export_sha256": "'
        + provenance_hash
        + '", "run": "approved-export-run", "detail": "'
        + ("R" * 60)
        + '"}'
    )
    source_metadata = {
        "nullable_value": None,
        "zero_value": 0,
        "false_value": False,
        "forecast_export": "validated export metadata",
        "snapshot_policy": "constructed-origin",
        "snapshot_assumption": "Recorded inventory is a constructed starting balance; "
        + ("exact source wording " * 20),
    }
    view["source"] = source_metadata
    for row in view["prospective_records"]:
        if row["horizon"] in (1, 7, 14):
            row["method_assumptions"] = [scenario_text]
            row["method_limitations"] = [limitation]
            row["source_provenance"] = provenance
            row["snapshot_assumption"] = f"h{row['horizon']}: {scenario_text}"
    for horizon in (1, 7, 14):
        original = next(
            row for row in view["prospective_records"] if row["horizon"] == horizon
        )
        view["prospective_records"].append(
            {**original, "SKU_ID": f"{original['SKU_ID']}_SECOND"}
        )

    original_view = deepcopy(view)
    figures = render_exposure_coverage(view)
    metadata = next(
        figure for figure in figures if "source metadata" in figure.get_suptitle()
    )
    axis = metadata.axes[0]
    headings = [
        text.get_text() for text in axis.texts if text.get_fontweight() == "bold"
    ]
    expected_headings = [
        "Shared source fields",
        "Constructed no-receipt scenario assumption",
        "Method limitations",
        "Source provenance",
        "Horizon-specific assumptions",
    ]
    all_text = _texts((metadata,))
    reconstructed_text = all_text.replace("\n", "")

    assert headings == expected_headings
    for required_value in (
        scenario_text,
        limitation,
        provenance_hash,
        "approved-export-run",
        source_metadata["forecast_export"],
        source_metadata["snapshot_policy"],
        source_metadata["snapshot_assumption"],
        "null",
        "0",
        "false",
    ):
        assert required_value in reconstructed_text
    for horizon in (1, 7, 14):
        assert f"h{horizon}: {scenario_text}" in reconstructed_text
    assert view == original_view

    metadata.canvas.draw()
    renderer = metadata.canvas.get_renderer()
    axis_bounds = axis.get_window_extent(renderer)
    text_bounds = [text.get_window_extent(renderer) for text in axis.texts]
    long_lines = [
        (len(line), line)
        for text in axis.texts
        for line in text.get_text().splitlines()
        if len(line) > 140
    ]
    assert not long_lines, long_lines
    assert all(
        bounds.x0 >= axis_bounds.x0 - 1
        and bounds.x1 <= axis_bounds.x1 + 1
        and bounds.y0 >= axis_bounds.y0 - 1
        and bounds.y1 <= axis_bounds.y1 + 1
        for bounds in text_bounds
    )
    assert all(
        previous.y0 >= following.y1 - 1
        for previous, following in zip(text_bounds, text_bounds[1:])
    )


def test_shared_provenance_and_caveats_have_a_wrapped_metadata_page():
    view = _availability_view()
    provenance = {"export": "full provenance value " + ("P" * 220)}
    assumptions = ["constructed-origin assumption " + ("A" * 160)]
    limitations = ["snapshot timing remains unknown " + ("L" * 180)]
    for row in view["prospective"]["records"][:3]:
        row["source_provenance"] = provenance
        row["method_assumptions"] = assumptions
        row["method_limitations"] = limitations
    view["source"] = {"export_metadata": "complete source metadata " + ("M" * 240)}

    figures = render_availability_provenance(view)
    metadata = next(
        figure for figure in figures if "source metadata" in figure.get_suptitle()
    )
    text = metadata.axes[0].texts[0]

    assert text.get_wrap() is True
    assert "dataset_provenance_sha256" in text.get_text()
    assert provenance["export"] in text.get_text()
    assert assumptions[0] in text.get_text()
    assert limitations[0] in text.get_text()
    assert view["source"]["export_metadata"] in text.get_text()
    prospective_headings = [
        header
        for figure in figures
        for axis in figure.axes
        if axis.get_title(loc="left")
        == "Prospective source/scenario availability and provenance"
        for table in axis.tables
        for (row, _column), cell in table.get_celld().items()
        if row == 0
        for header in (cell.get_text().get_text().replace("\n", ""),)
    ]
    assert "source_provenance" not in prospective_headings
    assert "method_assumptions" not in prospective_headings
    assert "method_limitations" not in prospective_headings


def test_paginated_h28_exposure_remains_identity_and_gate_only():
    view = _exposure_view()
    rows = [
        {
            **_identity(28),
            "SKU_ID": f"GATED_{index:03d}",
            "downstream_use_status": f"status_{index:03d}_not_approved_for_downstream_use",
            "downstream_use_reason": (
                f"reason_{index:03d}_28_day_downstream_use_requires_separate_approval"
            ),
            "inventory_buffer": "PROHIBITED",
            "predicted_margin": "PROHIBITED",
            "confusion_cell": "PROHIBITED",
        }
        for index in range(93)
    ]
    view["prospective_records"] = rows
    view["horizon_population"] = [
        {
            "forecast_origin": "2024-12-02",
            "horizon": 28,
            "horizon_forecast_population_count": len(rows),
        }
    ]
    view["evaluation_only"] = {"summary": [], "cases": []}

    figures = render_exposure_coverage(view)
    panel_a, panel_b = _h28_panels(figures)
    rendered_ids_a = _table_column_values(panel_a, "SKU_ID")
    rendered_ids_b = _table_column_values(panel_b, "SKU_ID")
    rendered_statuses = _table_column_values(panel_b, "downstream_use_status")
    rendered_reasons = _table_column_values(panel_b, "downstream_use_reason")
    rendered_text_a = _texts(panel_a)
    rendered_text_b = _texts(panel_b)
    expected_identity_rows = [
        tuple(str(row[field]) for field in _H28_IDENTITY_FIELDS) for row in rows
    ]

    assert len(panel_a) == len(panel_b) == 3
    assert all(
        _first_table_headers(figure) == _H28_IDENTITY_FIELDS for figure in panel_a
    )
    assert all(_first_table_headers(figure) == _H28_GATE_FIELDS for figure in panel_b)
    assert all("downstream gate only" in figure.get_suptitle() for figure in panel_a)
    assert all("downstream gate only" in figure.get_suptitle() for figure in panel_b)
    assert all(
        "remains downstream-gated" in _texts((figure,))
        for figure in (*panel_a, *panel_b)
    )
    assert rendered_ids_a == [row["SKU_ID"] for row in rows]
    assert rendered_ids_b == rendered_ids_a
    assert len(rendered_ids_a) == len(set(rendered_ids_a))
    assert _h28_identity_rows(panel_a) == expected_identity_rows
    assert _h28_identity_rows(panel_b) == expected_identity_rows
    assert len(set(_h28_identity_rows(panel_a))) == len(rows)
    assert len(set(_h28_identity_rows(panel_b))) == len(rows)
    assert rendered_statuses == [row["downstream_use_status"] for row in rows]
    assert rendered_reasons == [row["downstream_use_reason"] for row in rows]
    assert panel_b[0].get_size_inches()[0] == 36.0
    assert (
        _table_column_width(panel_b[0], "downstream_use_reason")
        > _table_column_width(panel_b[0], "downstream_use_status")
        > _table_column_width(panel_b[0], "SKU_ID")
    )
    assert "downstream_use_status" not in rendered_text_a
    assert "downstream_use_reason" not in rendered_text_a
    assert "inventory_buffer" not in rendered_text_a + rendered_text_b
    assert "predicted_margin" not in rendered_text_a + rendered_text_b
    assert "confusion_cell" not in rendered_text_a + rendered_text_b
    assert "PROHIBITED" not in rendered_text_a + rendered_text_b


def test_render_script_refuses_to_reuse_an_existing_output_directory(tmp_path):
    output_directory = tmp_path / "existing-render"
    output_directory.mkdir()
    sentinel = output_directory / "keep.txt"
    sentinel.write_text("preserve", encoding="utf-8")

    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        render_issue_201(tmp_path, output_directory)

    assert sentinel.read_text(encoding="utf-8") == "preserve"
