"""Synthetic runtime checks; no models, dataset or research execution."""

from importlib.metadata import PackageNotFoundError
from pathlib import Path
from unittest.mock import Mock

import pytest

from src.forecasting import metadata
from src.forecasting.authorization import ExecutionBlocked


@pytest.mark.parametrize("missing", ["numpy", "requirements-only-package"])
def test_missing_runtime_package_blocks_with_package_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, missing: str
) -> None:
    (tmp_path / "requirements.txt").write_text("requirements-only-package==1.0\n")

    def version(name: str) -> str:
        if name == missing:
            raise PackageNotFoundError(name)
        return "1.0"

    monkeypatch.setattr(metadata.importlib.metadata, "version", version)
    with pytest.raises(ExecutionBlocked, match=f"not installed: {missing}") as error:
        metadata.runtime_versions(tmp_path)
    assert isinstance(error.value.__cause__, PackageNotFoundError)


def test_runtime_versions_retains_successful_version_mapping(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "requirements.txt").write_text("requirements-only-package==1.0\n")
    lookup = Mock(return_value="1.0")
    monkeypatch.setattr(metadata.importlib.metadata, "version", lookup)
    monkeypatch.setattr(metadata.platform, "python_version", lambda: "3.12.3")

    assert metadata.runtime_versions(tmp_path) == dict.fromkeys(
        metadata.LIBRARIES, "1.0"
    )
    lookup.assert_any_call("requirements-only-package")


def test_runtime_versions_still_blocks_pinned_version_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "requirements.txt").write_text("numpy==2.0\n")
    monkeypatch.setattr(metadata.importlib.metadata, "version", lambda name: "1.0")

    with pytest.raises(ExecutionBlocked, match="Pinned version mismatch for numpy"):
        metadata.runtime_versions(tmp_path)


def test_runtime_versions_still_blocks_python_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "requirements.txt").write_text("numpy==1.0\n")
    monkeypatch.setattr(metadata.importlib.metadata, "version", lambda name: "1.0")
    monkeypatch.setattr(metadata.platform, "python_version", lambda: "3.12.2")

    with pytest.raises(ExecutionBlocked, match="frozen Python runtime is 3.12.3"):
        metadata.runtime_versions(tmp_path)
