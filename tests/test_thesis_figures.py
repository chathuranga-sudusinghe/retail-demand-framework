"""Synthetic-only contracts for the eight-figure thesis delivery workflow."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
from typing import Any

from matplotlib.text import Text
import pytest

from src.visualization import render_issue_201_views as cli
from src.visualization import thesis_evidence as evidence_module
from src.visualization.inventory_views import InventoryViewSourceError
from src.visualization.thesis_evidence import (
    CRITERIA,
    MODELS,
    FigureEvidence,
    build_figure_evidence,
    parse_final_comparison,
)
from src.visualization.thesis_figures import render_figure
from test_inventory_views import _load, _write_fixture


@pytest.fixture
def inputs(
    tmp_path: Path,
) -> tuple[Any, dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    root, export = _write_fixture(tmp_path)
    inventory = _load(root, export)
    rows = [
        r
        for r in inventory.prospective["records"]
        if r["SKU_ID"] == "SKU_3" and r["Warehouse_ID"] == "WH_1"
    ]
    evaluated = {
        r["horizon"]: r
        for r in inventory.evaluation["cases"]
        if r["SKU_ID"] == "SKU_3" and r["Warehouse_ID"] == "WH_1"
    }
    results, observations = [], []
    for row in rows:
        h = row["horizon"]
        results.append(
            {
                "horizon": h,
                "retained_case": {"prospective_record": deepcopy(row)},
                "api_response": {
                    "horizon": h,
                    "forecast_quantity": row["prediction"],
                    "target_start_date": row["target_start_date"],
                    "target_end_date": row["target_end_date"],
                },
            }
        )
        observations.append(
            {
                "horizon": h,
                "forecast_quantity": row["prediction"],
                "actual_units_sold": evaluated[h]["observed_target"] if h != 28 else 50,
                "target_start_date": row["target_start_date"],
                "target_end_date": row["target_end_date"],
            }
        )
    source_hash = inventory.manifest["source"]["forecast_export_sha256"]
    trace = {
        "schema": "issue-214-worked-scenario-v1",
        "sources": {"forecast_export_sha256": source_hash},
        "forecast_results": results,
        "retrospective_comparison": {"rows": observations},
        "selection": {"seed": "synthetic-only", "population": "synthetic fixture"},
    }
    assessment = {
        "source": {"export_sha256": source_hash},
        "reviewed_records": 3,
        "reviewed_check_rows": 24,
        "criteria": {
            name: {
                "applicable": 3,
                "not_applicable": 0,
                "met": 1,
                "not met": 1,
                "not assessable": 1,
            }
            for name in CRITERIA
        },
    }
    comparison = [
        {
            "role": "primary"
            if m in MODELS[:3]
            else "supportive"
            if m in MODELS[3:5]
            else "simple_baseline",
            "model": m,
            "horizon": h,
            "configuration_id": "synthetic",
            "status": "valid",
            "WAPE": 0.10 + i * 0.01,
            "MAE": 1.0,
            "RMSE": 2.0,
            "Bias": -0.5,
        }
        for h in (1, 7, 14, 28)
        for i, m in enumerate(MODELS)
    ]
    return inventory, trace, assessment, comparison


@pytest.fixture
def specs(inputs: tuple[Any, ...]) -> tuple[FigureEvidence, ...]:
    return build_figure_evidence(*inputs)


def _texts(figure: Any) -> str:
    return "\n".join(t.get_text() for t in figure.findobj(Text) if t.get_visible())


def test_projections_keep_sources_unchanged_and_separate_evaluation(
    inputs: tuple[Any, ...],
) -> None:
    before = deepcopy(inputs)
    output = build_figure_evidence(*inputs)
    assert len(output) == len({s.name for s in output}) == 8
    assert inputs == before
    margin = output[2].data
    assert all(r["horizon"] in {1, 7, 14} for r in margin["evaluation_only_cases"])
    assert any(r["predicted_margin"] is None for r in margin["evaluation_only_cases"])
    assert all(
        r["horizon"] in {1, 7, 14} for r in output[2].data["evaluation_only_cases"]
    )


@pytest.mark.parametrize(
    "failure", ["forecast", "actual", "window", "missing_horizon", "pair", "counts"]
)
def test_reject_inconsistent_display_sources(
    inputs: tuple[Any, ...], failure: str
) -> None:
    inventory, trace, assessment, comparison = deepcopy(inputs)
    if failure == "forecast":
        trace["forecast_results"][0]["api_response"]["forecast_quantity"] += 1
    elif failure == "actual":
        trace["retrospective_comparison"]["rows"][0]["actual_units_sold"] += 1
    elif failure == "window":
        trace["retrospective_comparison"]["rows"][0]["target_end_date"] = "2099-01-01"
    elif failure == "missing_horizon":
        trace["forecast_results"].pop()
    elif failure == "pair":
        trace["forecast_results"][0]["retained_case"]["prospective_record"][
            "SKU_ID"
        ] = "wrong"
    else:
        assessment["criteria"][CRITERIA[0]]["met"] = 100
    with pytest.raises(InventoryViewSourceError):
        build_figure_evidence(inventory, trace, assessment, comparison)


def test_final_table_requires_complete_unique_finite_rows(
    inputs: tuple[Any, ...],
) -> None:
    rows = inputs[3]
    text = "\n".join(
        "| "
        + " | ".join(
            str(r[k])
            for k in (
                "role",
                "model",
                "horizon",
                "configuration_id",
                "WAPE",
                "MAE",
                "RMSE",
                "Bias",
                "status",
            )
        )
        + " |"
        for r in rows
    )
    assert len(parse_final_comparison(text)) == 28
    with pytest.raises(InventoryViewSourceError):
        parse_final_comparison(text + "\n" + text.splitlines()[0])
    with pytest.raises(InventoryViewSourceError):
        parse_final_comparison(text.replace("0.1", "nan", 1))


@pytest.mark.parametrize("index", range(8))
def test_synthetic_rendering_legibility_bounds_and_no_mutation(
    specs: tuple[FigureEvidence, ...], index: int
) -> None:
    before = deepcopy(specs)
    figure = render_figure(specs[index], index)
    try:
        figure.canvas.draw()
        renderer = figure.canvas.get_renderer()
        bounds = figure.bbox
        for item in figure.findobj(Text):
            if not item.get_visible() or not item.get_text().strip():
                continue
            assert item.get_fontsize() >= 8, item.get_text()
            box = item.get_window_extent(renderer)
            assert box.x0 >= bounds.x0 - 2 and box.x1 <= bounds.x1 + 2, item.get_text()
            assert box.y0 >= bounds.y0 - 2 and box.y1 <= bounds.y1 + 2, item.get_text()
        for axis in figure.axes:
            for table in axis.tables:
                for cell in table.get_celld().values():
                    text_box = cell.get_text().get_window_extent(renderer)
                    cell_box = cell.get_window_extent(renderer)
                    assert text_box.width <= cell_box.width + 2, (
                        cell.get_text().get_text()
                    )
                    assert text_box.height <= cell_box.height + 2, (
                        cell.get_text().get_text()
                    )
        visible = [t for t in figure.texts if t.get_visible() and t.get_text()]
        for i, first in enumerate(visible):
            first_box = first.get_window_extent(renderer)
            for second in visible[i + 1 :]:
                assert not first_box.overlaps(second.get_window_extent(renderer)), (
                    first.get_text(),
                    second.get_text(),
                )
            for axis in figure.axes:
                if axis.title.get_text():
                    assert not first_box.overlaps(
                        axis.title.get_window_extent(renderer)
                    ), first.get_text()
        assert tuple(figure.get_size_inches())[0] == 6.3
        assert specs == before
        if index < 6:
            assert "group-approved" in _texts(figure)
            assert "Source timing unknown" in _texts(figure)
    finally:
        cli._release_figure(figure)


def test_margin_plot_excludes_nulls_and_preserves_all_eligible_points(
    specs: tuple[FigureEvidence, ...],
) -> None:
    figure = render_figure(specs[2], 2)
    try:
        for axis, h in zip(figure.axes, (1, 7, 14), strict=True):
            original = [
                r
                for r in specs[2].data["evaluation_only_cases"]
                if r["horizon"] == h and r["comparison_case"] == "evaluable_paired_case"
            ]
            actual = [
                tuple(pair)
                for collection in axis.collections[:4]
                for pair in collection.get_offsets()
            ]
            assert sorted(actual) == sorted(
                (r["predicted_margin"], r["retrospective_margin"]) for r in original
            )
        assert len({axis.get_xlim() for axis in figure.axes}) == 1
        assert len({axis.get_ylim() for axis in figure.axes}) == 1
        figure.canvas.draw()
        renderer = figure.canvas.get_renderer()
        for axis in figure.axes:
            annotations = [t for t in axis.texts if t.get_text().startswith("SKU_")]
            assert len(annotations) == 1
            annotation = annotations[0]
            assert annotation.arrow_patch is not None
            # Check the label box, excluding the pointer that intentionally reaches the case.
            label_box = annotation.get_bbox_patch().get_window_extent(renderer)
            zero_y = axis.transData.transform((0, 0))[1]
            assert label_box.y0 > zero_y
    finally:
        cli._release_figure(figure)


def test_bar_values_and_zero_baselines(specs: tuple[FigureEvidence, ...]) -> None:
    for index in (3, 4, 6, 7):
        figure = render_figure(specs[index], index)
        try:
            axes = [a for a in figure.axes if a.patches]
            for axis in axes:
                assert axis.get_xlim()[0] <= 0 <= axis.get_xlim()[1]
                assert (
                    axis.get_ylim()[0] <= 0 <= axis.get_ylim()[1]
                    or axis.yaxis_inverted()
                )
            if index == 7:
                assert sum(len(a.patches) for a in axes) == 28
                tick_sets = [tuple(a.get_xticks()) for a in axes]
                assert len(set(tick_sets)) == 1
                ticks = tick_sets[0]
                intervals = [b - a for a, b in zip(ticks, ticks[1:])]
                assert all(abs(step - intervals[0]) < 1e-10 for step in intervals)
                assert len(ticks) >= 4 and ticks[0] == 0
                figure.canvas.draw()
                renderer = figure.canvas.get_renderer()
                for axis in axes:
                    boxes = [
                        t.get_window_extent(renderer)
                        for t in axis.get_xticklabels()
                        if t.get_visible() and t.get_text()
                    ]
                    assert all(a.x1 + 2 <= b.x0 for a, b in zip(boxes, boxes[1:]))
                for axis, h in zip(axes, (1, 7, 14, 28), strict=True):
                    assert [p.get_width() for p in axis.patches] == [
                        r["WAPE"]
                        for r in specs[7].data["comparison"]
                        if r["horizon"] == h
                    ]
            if index == 6:
                assert "not met" in _texts(figure).lower()
                assert "not assessable" in _texts(figure).lower()
                figure.canvas.draw()
                for bar in axes[0].patches:
                    if not bar.get_hatch() or bar.get_width() == 0:
                        continue
                    x = bar.get_x() + bar.get_width() / 2
                    y = bar.get_y() + bar.get_height() / 2
                    label = next(t for t in axes[0].texts if t.get_position() == (x, y))
                    background = label.get_bbox_patch()
                    assert background is not None
                    assert background.get_facecolor() == (1.0, 1.0, 1.0, 1.0)
        finally:
            cli._release_figure(figure)


@pytest.mark.parametrize("index", (2, 4))
def test_margin_figures_explain_physical_stock_limit_and_evaluation_only(
    specs: tuple[FigureEvidence, ...], index: int
) -> None:
    figure = render_figure(specs[index], index)
    try:
        text = " ".join(_texts(figure).split())
        assert "Negative margin is not verified physical negative stock." in text
        assert "evaluation only" in text.lower()
    finally:
        cli._release_figure(figure)


def test_pinned_source_tampering_blocks_loading(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, inputs: tuple[Any, ...]
) -> None:
    monkeypatch.setattr(
        evidence_module, "load_inventory_view_evidence", lambda _: inputs[0]
    )
    relative = Path("synthetic.json")
    (tmp_path / relative).write_text("tampered")
    monkeypatch.setattr(evidence_module, "SOURCE_HASHES", {relative: "0" * 64})
    with pytest.raises(InventoryViewSourceError, match="source hash differs"):
        evidence_module.load_figure_evidence(tmp_path)


def test_gate_only_worked_trace_and_all_source_pins_load(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, inputs: tuple[Any, ...]
) -> None:
    inventory, trace, assessment, comparison = deepcopy(inputs)
    gated = trace["forecast_results"][-1]["retained_case"]["prospective_record"]
    assert gated["horizon"] == 28
    for field in (
        "Inventory_Level",
        "Reorder_Point",
        "inventory_buffer",
        "predicted_margin",
    ):
        gated.pop(field, None)
    markdown = "\n".join(
        "| "
        + " | ".join(
            str(r[k])
            for k in (
                "role",
                "model",
                "horizon",
                "configuration_id",
                "WAPE",
                "MAE",
                "RMSE",
                "Bias",
                "status",
            )
        )
        + " |"
        for r in comparison
    )
    payloads = {
        evidence_module.WORKED_PATH: json.dumps(trace).encode(),
        evidence_module.SUMMARY_PATH: json.dumps(assessment).encode(),
        evidence_module.COMPARISON_PATH: markdown.encode(),
    }
    for relative, payload in payloads.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    monkeypatch.setattr(
        evidence_module,
        "SOURCE_HASHES",
        {p: hashlib.sha256(b).hexdigest() for p, b in payloads.items()},
    )
    monkeypatch.setattr(
        evidence_module, "load_inventory_view_evidence", lambda _: inventory
    )
    assert len(evidence_module.load_figure_evidence(tmp_path)) == 8
    (tmp_path / evidence_module.WORKED_PATH).write_text("tampered trace")
    with pytest.raises(InventoryViewSourceError, match="source hash differs"):
        evidence_module.load_figure_evidence(tmp_path)


def test_cli_updates_managed_output_and_preserves_it_on_render_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, specs: tuple[FigureEvidence, ...]
) -> None:
    monkeypatch.setattr(cli, "load_figure_evidence", lambda _: specs)
    source_paths = [
        *cli.SOURCE_HASHES,
        *(
            cli.INVENTORY_EVIDENCE_DIRECTORY / n
            for n in cli.EVALUATION_FILE_NAMES | {"manifest.json"}
        ),
        cli.FORECAST_EXPORT_PATH,
    ]
    for relative in source_paths:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("synthetic evidence only")
    monkeypatch.setattr(
        cli.subprocess,
        "check_output",
        lambda args, **kw: "f" * 40 if args[1] == "rev-parse" else " M synthetic.py",
    )
    # Actual SVG/PNG writing is tested on tiny synthetic figures, not retained data.
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg

    def tiny(*args: Any) -> Figure:
        fig = Figure(figsize=(1, 1))
        FigureCanvasAgg(fig)
        return fig

    monkeypatch.setattr(cli, "render_figure", tiny)
    output = Path("reports/figures/synthetic-bundle")
    paths = cli.render_issue_201(tmp_path, output)
    assert len(paths) == len(list((tmp_path / output).glob("*.png"))) == 8
    assert len(list((tmp_path / output).glob("*.svg"))) == 8
    manifest = json.loads((tmp_path / output / "manifest.json").read_text())
    assert manifest["figure_count"] == 8
    assert manifest["renderer"]["git_working_tree_clean"] is False
    for figure in manifest["figures"]:
        for name, digest in figure["files"].items():
            assert (
                hashlib.sha256((tmp_path / output / name).read_bytes()).hexdigest()
                == digest
            )
        sidecar = json.loads(
            (tmp_path / output / (figure["name"] + ".json")).read_text()
        )
        assert sidecar["purpose"] and sidecar["data"]
    assert cli.render_issue_201(tmp_path, output) == paths
    assert len(list((tmp_path / output).glob("*.png"))) == 8
    before = {p.name: p.read_bytes() for p in (tmp_path / output).iterdir()}

    def fail_render(*args: Any) -> Figure:
        raise OSError("synthetic render failure")

    monkeypatch.setattr(cli, "render_figure", fail_render)
    with pytest.raises(OSError, match="synthetic render failure"):
        cli.render_issue_201(tmp_path, output)
    assert {p.name: p.read_bytes() for p in (tmp_path / output).iterdir()} == before
    assert not list((tmp_path / "reports/figures").glob(".figure-render-*"))

    monkeypatch.setattr(cli, "render_figure", tiny)
    original_replace = Path.replace
    published = []

    def interrupt_publication(source: Path, destination: Any) -> Path:
        target = Path(destination)
        if target.parent == tmp_path / output:
            published.append(target.name)
            if len(published) == 2:
                raise OSError("synthetic publication interruption")
        return original_replace(source, destination)

    with monkeypatch.context() as scoped:
        scoped.setattr(Path, "replace", interrupt_publication)
        with pytest.raises(OSError, match="publication interruption"):
            cli.render_issue_201(tmp_path, output)
    assert not (tmp_path / output / "manifest.json").exists()
    assert not list((tmp_path / "reports/figures").glob(".figure-render-*"))
    with pytest.raises(FileExistsError, match="unrelated or changed"):
        cli.render_issue_201(tmp_path, output)
    # Model the documented human recovery, only inside this disposable fixture.
    shutil.rmtree(tmp_path / output)
    assert cli.render_issue_201(tmp_path, output) == paths

    extra = tmp_path / output / "unrelated.txt"
    extra.write_text("keep this user file")
    with pytest.raises(FileExistsError, match="unrelated or changed"):
        cli.render_issue_201(tmp_path, output)
    assert extra.read_text() == "keep this user file"
    extra.unlink()
    paths[0].write_bytes(b"manual change")
    with pytest.raises(FileExistsError, match="unrelated or changed"):
        cli.render_issue_201(tmp_path, output)
    assert paths[0].read_bytes() == b"manual change"


def test_output_must_stay_under_trackable_report_figures(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="reports/figures"):
        cli.render_issue_201(tmp_path, tmp_path / "research-materials/old-output")
