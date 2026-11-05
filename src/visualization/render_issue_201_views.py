"""Export eight approved thesis/presentation figures from retained evidence.

Run from the repository root with the project environment:

    python -m src.visualization.render_issue_201_views

The script only reads the retained forecast/inventory evidence and writes a
trackable bundle under reports/figures/final-thesis-figures/. Reruns replace this
generated bundle after rendering succeeds; unrelated or changed files are refused.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

import matplotlib
from matplotlib.figure import Figure

from src.forecasting.export import DESTINATION as FORECAST_EXPORT_PATH
from src.forecasting.paths import REPOSITORY
from src.visualization.inventory_views import (
    EVALUATION_FILE_NAMES,
    INVENTORY_EVIDENCE_DIRECTORY,
)
from src.visualization.thesis_evidence import SOURCE_HASHES, load_figure_evidence
from src.visualization.thesis_figures import render_figure

# Schema versions identify file formats, not output folder versions.
OUTPUT_DIRECTORY = Path("reports/figures/final-thesis-figures")
RENDER_SCHEMA = "retail-thesis-figure-bundle-v1"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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


def _save_figure_and_release(
    figure: Figure, destination: Path, *, vector_path: Path | None = None
) -> None:
    """Save one figure and release it, preserving a save failure if cleanup fails."""
    try:
        figure.savefig(destination, format="png", dpi=300, facecolor="white")
        if vector_path is not None:
            figure.savefig(vector_path, format="svg", facecolor="white")
    except BaseException:
        try:
            _release_figure(figure)
        except BaseException:
            # Cleanup must not replace the original save exception.
            pass
        raise
    else:
        _release_figure(figure)


def _render_new_bundle(
    repository: Path = REPOSITORY,
    output_directory: Path = OUTPUT_DIRECTORY,
) -> tuple[Path, ...]:
    """Human-executed export of exactly eight PNGs with SVG and source sidecars."""
    repository = repository.resolve()
    if not output_directory.is_absolute():
        output_directory = repository / output_directory
    output_directory = output_directory.resolve()
    if output_directory.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing render directory: {output_directory}"
        )
    allowed = repository / "reports/figures"
    if not output_directory.is_relative_to(allowed):
        raise ValueError("Figure bundles must stay under repository reports/figures/.")
    specs = load_figure_evidence(repository)
    if len(specs) != 8:
        raise ValueError(
            "The approved figure selection must contain exactly eight figures."
        )
    inventory_directory = repository / INVENTORY_EVIDENCE_DIRECTORY
    sources = [repository / path for path in SOURCE_HASHES]
    sources += [
        inventory_directory / name
        for name in sorted(EVALUATION_FILE_NAMES | {"manifest.json"})
    ]
    sources.append(repository / FORECAST_EXPORT_PATH)
    hashes = {
        path.relative_to(repository).as_posix(): _sha256(path) for path in sources
    }
    module_names = (
        "inventory_views.py",
        "thesis_evidence.py",
        "thesis_figures.py",
        "render_issue_201_views.py",
    )
    code_hashes = {
        name: _sha256(Path(__file__).with_name(name)) for name in module_names
    }
    git_head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repository, text=True
    ).strip()
    git_state = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=repository, text=True
    )
    output_directory.mkdir(parents=True, exist_ok=False)
    rendered_files = []
    figures = []
    for index, spec in enumerate(specs):
        png = output_directory / f"{spec.name}.png"
        svg = png.with_suffix(".svg")
        sidecar = png.with_suffix(".json")
        print(f"Rendering {index + 1}/8: {spec.name}", flush=True)
        figure = render_figure(spec, index)
        dimensions = list(figure.get_size_inches())
        _save_figure_and_release(figure, png, vector_path=svg)
        sidecar.write_bytes(
            _json_bytes(
                {
                    "schema": "retail-thesis-figure-evidence-v1",
                    "figure": spec.name,
                    "purpose": spec.purpose,
                    "caption": spec.caption,
                    "source_file_sha256": hashes,
                    "data": spec.data,
                    "identity_status": "Pinned/local byte identity; not independent review or acceptance.",
                }
            )
        )
        rendered_files.append(png)
        figures.append(
            {
                "name": spec.name,
                "title": spec.title,
                "purpose": spec.purpose,
                "caption": spec.caption,
                "size_inches": dimensions,
                "png_dpi": 300,
                "files": {path.name: _sha256(path) for path in (png, svg, sidecar)},
            }
        )
    # Catch concurrent input edits; a failed bundle has no completion manifest.
    if any(_sha256(repository / path) != digest for path, digest in hashes.items()):
        raise ValueError(
            "Source evidence changed during rendering; bundle is incomplete."
        )
    if any(
        _sha256(Path(__file__).with_name(name)) != digest
        for name, digest in code_hashes.items()
    ):
        raise ValueError(
            "Renderer source changed during rendering; bundle is incomplete."
        )
    manifest = {
        "schema": RENDER_SCHEMA,
        "status": "rendered; human visual/component review pending",
        "figure_count": len(figures),
        "source_file_sha256": hashes,
        "renderer": {
            "python": sys.version.split()[0],
            "matplotlib": matplotlib.__version__,
            "code_sha256": code_hashes,
            "git_head": git_head,
            "git_working_tree_clean": not bool(git_state.strip()),
        },
        "figures": figures,
    }
    index_lines = [
        "# Thesis / presentation figures",
        "",
        "Human visual and component review remains required.",
        "",
    ]
    for spec in specs:
        index_lines += [
            f"## {spec.title}",
            "",
            spec.purpose,
            "",
            f"![{spec.title}]({spec.name}.png)",
            "",
            spec.caption,
            "",
            f"[Vector]({spec.name}.svg) | [Full evidence]({spec.name}.json)",
            "",
        ]
    (output_directory / "README.md").write_text(
        "\n".join(index_lines), encoding="utf-8"
    )
    manifest["readme_sha256"] = _sha256(output_directory / "README.md")
    (output_directory / "manifest.json").write_bytes(_json_bytes(manifest))
    return tuple(rendered_files)


def _existing_bundle_state(directory: Path) -> dict[str, str] | None:
    """Recognise an intact generated bundle; preserve all other contents."""
    if not directory.exists():
        return None
    message = (
        f"Refusing to overwrite unrelated or changed render directory: {directory}"
    )
    try:
        manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
        if manifest["schema"] != RENDER_SCHEMA or manifest["figure_count"] != 8:
            raise ValueError(message)
        figures = manifest["figures"]
        if len(figures) != 8 or len({f["name"] for f in figures}) != 8:
            raise ValueError(message)
        expected = {"README.md": manifest["readme_sha256"]}
        for figure in figures:
            name = figure["name"]
            if not name.startswith("fig") or Path(name).name != name:
                raise ValueError(message)
            if set(figure["files"]) != {
                f"{name}.{suffix}" for suffix in ("png", "svg", "json")
            }:
                raise ValueError(message)
            expected.update(figure["files"])
        entries = list(directory.iterdir())
        if {p.name for p in entries} != set(expected) | {"manifest.json"}:
            raise ValueError(message)
        if any(p.is_symlink() or not p.is_file() for p in entries):
            raise ValueError(message)
        if any(
            _sha256(directory / name) != digest for name, digest in expected.items()
        ):
            raise ValueError(message)
        return {p.name: _sha256(p) for p in entries}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise FileExistsError(message) from exc


def render_issue_201(
    repository: Path = REPOSITORY,
    output_directory: Path = OUTPUT_DIRECTORY,
) -> tuple[Path, ...]:
    """Update the stable final folder, staging all rendering before replacement."""
    repository = repository.resolve()
    output_directory = (repository / output_directory).resolve()
    previous = _existing_bundle_state(output_directory)
    allowed = repository / "reports/figures"
    if output_directory == allowed or not output_directory.is_relative_to(allowed):
        raise ValueError("Figure bundles must stay under repository reports/figures/.")
    allowed.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".figure-render-", dir=allowed
    ) as temporary:
        staging = Path(temporary) / "bundle"
        rendered = _render_new_bundle(repository, staging)
        if _existing_bundle_state(output_directory) != previous:
            raise FileExistsError(
                "Output changed during rendering; refusing replacement."
            )
        incoming = {p.name for p in staging.iterdir()}
        if previous is not None and incoming != set(previous):
            raise FileExistsError(
                "Existing output filenames differ; refusing replacement."
            )
        output_directory.mkdir(parents=True, exist_ok=True)
        # Publish the completion receipt last; interrupted replacement is incomplete.
        (output_directory / "manifest.json").unlink(missing_ok=True)
        for source in staging.iterdir():
            if source.name != "manifest.json":
                source.replace(output_directory / source.name)
        (staging / "manifest.json").replace(output_directory / "manifest.json")
        return tuple(output_directory / path.name for path in rendered)


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
    print(f"Output directory: {files[0].parent}")
    for path in files:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
