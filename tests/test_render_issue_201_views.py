"""Figure lifecycle tests for the Issue #201 static renderer."""

from __future__ import annotations

from pathlib import Path

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import pytest

from src.visualization.render_issue_201_views import _save_figure_and_release


def _figure() -> Figure:
    figure = Figure(figsize=(2, 1), dpi=96)
    FigureCanvasAgg(figure)
    figure.subplots().plot((0, 1), (0, 1))
    return figure


def test_successful_save_releases_figure_and_later_figure_still_renders(
    tmp_path: Path,
) -> None:
    first = _figure()
    first_canvas = first.canvas
    first_path = tmp_path / "first.png"

    _save_figure_and_release(first, first_path)

    assert first_path.is_file()
    assert first.axes == []
    assert first.canvas is None
    assert first_canvas.renderer is None

    second = _figure()
    second_canvas = second.canvas
    second_path = tmp_path / "second.png"
    _save_figure_and_release(second, second_path)

    assert second_path.is_file()
    assert second.axes == []
    assert second.canvas is None
    assert second_canvas.renderer is None


def test_failed_save_releases_figure_and_propagates_original_exception(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    figure = _figure()
    canvas = figure.canvas
    canvas.draw()
    save_error = OSError("synthetic save failure")

    def fail_save(*args: object, **kwargs: object) -> None:
        raise save_error

    monkeypatch.setattr(figure, "savefig", fail_save)

    with pytest.raises(OSError) as raised:
        _save_figure_and_release(figure, tmp_path / "failed.png")

    assert raised.value is save_error
    assert figure.axes == []
    assert figure.canvas is None
    assert canvas.renderer is None
