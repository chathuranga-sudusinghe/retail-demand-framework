"""Render Issue #201 views from validated retained evidence into a new folder.

Run from the repository root with the project environment:

    python -m src.visualization.render_issue_201_views

The script only reads the retained forecast/inventory evidence and writes a
new, ignored rendering bundle. Existing output directories are never reused.
"""

from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

import matplotlib
from matplotlib.figure import Figure

from src.forecasting.export import DESTINATION as FORECAST_EXPORT_PATH
from src.forecasting.paths import REPOSITORY
from src.visualization.inventory_rendering import (
    render_availability_provenance,
    render_exposure_coverage,
    render_margin_comparison,
    render_proxy_crossing_comparison,
)
from src.visualization.inventory_views import (
    EVALUATION_FILE_NAMES,
    INVENTORY_EVIDENCE_DIRECTORY,
    build_availability_provenance,
    build_exposure_coverage,
    build_margin_comparison,
    build_proxy_crossing_comparison,
    load_inventory_view_evidence,
)

OUTPUT_DIRECTORY = Path("research-materials/inventory-risk/issue-201-views-v6")
RENDER_SCHEMA = "issue-201-inventory-view-render-v4"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "figure"


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode(
        "utf-8"
    )


def _release_figure(figure: Figure) -> None:
    """Clear a directly-created figure and release its Agg renderer buffer."""
    canvas = figure.canvas
    try:
        figure.clear()
    finally:
        try:
            if getattr(canvas, "renderer", None) is not None:
                setattr(canvas, "renderer", None)
        finally:
            setattr(figure, "canvas", None)


def _save_figure_and_release(figure: Figure, destination: Path) -> None:
    """Save one figure and release it, preserving a save failure if cleanup fails."""
    try:
        figure.savefig(destination, format="png", dpi=96)
    except BaseException:
        try:
            _release_figure(figure)
        except BaseException:
            # Cleanup must not replace the original save exception.
            pass
        raise
    else:
        _release_figure(figure)


def render_issue_201(
    repository: Path = REPOSITORY,
    output_directory: Path = OUTPUT_DIRECTORY,
) -> tuple[Path, ...]:
    """Validate sources, render A–D, then publish files into a new directory."""
    repository = repository.resolve()
    output_directory = output_directory.resolve()
    if output_directory.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing render directory: {output_directory}"
        )

    evidence = load_inventory_view_evidence(repository)
    prepared_views = (
        ("A", build_exposure_coverage(evidence), render_exposure_coverage),
        (
            "B",
            build_proxy_crossing_comparison(evidence),
            render_proxy_crossing_comparison,
        ),
        ("C", build_margin_comparison(evidence), render_margin_comparison),
        ("D", build_availability_provenance(evidence), render_availability_provenance),
    )

    output_directory.mkdir(parents=True, exist_ok=False)
    rendered_files: list[Path] = []
    for view_name, view, renderer in prepared_views:
        print(f"Preparing view {view_name}...", flush=True)
        figures = deque(renderer(view))
        figure_count = len(figures)
        index = 0
        while figures:
            figure = figures.popleft()
            index += 1
            title = figure.get_suptitle().splitlines()[0]
            filename = f"{view_name}-{index:02d}-{_slug(title)}.png"
            destination = output_directory / filename
            print(
                f"Rendering and saving {view_name} figure {index}/{figure_count}: "
                f"{filename}",
                flush=True,
            )
            _save_figure_and_release(figure, destination)
            rendered_files.append(destination)
            print(f"Saved {destination}", flush=True)
            del figure

    inventory_directory = repository / INVENTORY_EVIDENCE_DIRECTORY
    forecast_path = repository / FORECAST_EXPORT_PATH
    source_paths = {
        str((INVENTORY_EVIDENCE_DIRECTORY / "manifest.json").as_posix()): _sha256(
            inventory_directory / "manifest.json"
        ),
        **{
            str((INVENTORY_EVIDENCE_DIRECTORY / name).as_posix()): _sha256(
                inventory_directory / name
            )
            for name in sorted(EVALUATION_FILE_NAMES)
        },
        str(FORECAST_EXPORT_PATH): _sha256(forecast_path),
    }
    manifest = {
        "schema": RENDER_SCHEMA,
        "inputs": {
            "source_file_sha256": source_paths,
            "forecast_export_sha256": evidence.manifest["source"][
                "forecast_export_sha256"
            ],
            "dataset_provenance_sha256": evidence.manifest["dataset_provenance_sha256"],
        },
        "renderer": {
            "python": sys.version.split()[0],
            "matplotlib": matplotlib.__version__,
            "inventory_views_sha256": _sha256(
                Path(__file__).with_name("inventory_views.py")
            ),
            "inventory_rendering_sha256": _sha256(
                Path(__file__).with_name("inventory_rendering.py")
            ),
            "render_script_sha256": _sha256(Path(__file__)),
        },
        "figures": [
            {
                "path": path.name,
                "sha256": _sha256(path),
            }
            for path in rendered_files
        ],
    }
    (output_directory / "manifest.json").write_bytes(_json_bytes(manifest))
    return tuple(rendered_files)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPOSITORY)
    parser.add_argument("--output-directory", type=Path, default=OUTPUT_DIRECTORY)
    arguments = parser.parse_args()
    try:
        files = render_issue_201(arguments.root, arguments.output_directory)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(f"Figures rendered: {len(files)}")
    print(f"Output directory: {arguments.output_directory.resolve()}")
    for path in files:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
