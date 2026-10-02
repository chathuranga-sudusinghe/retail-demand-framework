"""Fixed paths are independent of cwd and create nothing on import."""
from dataclasses import FrozenInstanceError
import importlib
import pytest
from src.forecasting import paths


def test_fixed_paths_and_no_import_side_effects(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    importlib.reload(paths)
    assert not list(tmp_path.iterdir())
    assert paths.REPOSITORY.name == "retail-demand-framework"
    assert paths.approved_dataset(tmp_path) == tmp_path / "data/processed/validated/supply-chain-dataset1-validated-v1/validated.parquet"
    assert paths.execution_record(tmp_path) == tmp_path / "data/processed/forecasting/validation_authorization.json"
    assert paths.run_directory(tmp_path, "reviewed-01") == tmp_path / "outputs/revised-forecasting/reviewed-01"


@pytest.mark.parametrize("value", ["", "..", "../escape", "/outside", "a/b", None])
def test_unsafe_run_ids_rejected(tmp_path, value):
    with pytest.raises(ValueError):
        paths.run_directory(tmp_path, value)


def test_output_symlink_escape_rejected(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    repository = tmp_path / "repository"
    repository.mkdir()
    (repository / "outputs").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError):
        paths.run_directory(repository, "reviewed")


def test_layout_is_immutable_and_preserves_default_and_alternate_paths(tmp_path):
    layout = paths.RepositoryLayout(tmp_path)
    assert layout.root == tmp_path.resolve()
    with pytest.raises(FrozenInstanceError):
        layout.root = tmp_path / "changed"
    for current in (paths.DEFAULT_LAYOUT, layout):
        assert current.dataset == current.root / "data/processed/validated/supply-chain-dataset1-validated-v1/validated.parquet"
        assert current.execution_record == current.root / "data/processed/forecasting/validation_authorization.json"
        assert current.protocol == current.root / "docs/protocol.md"
        assert current.feature_contract == current.root / "docs/forecasting-feature-engineering.md"
        assert current.output_root == current.root / "outputs/revised-forecasting"
        directory = current.run_directory("reviewed-01")
        assert directory == current.output_root / "reviewed-01"
        assert current.validation_model_directory(directory) == directory / "models/validation"
        assert current.candidate_model_directory(directory, "ridge", 1, "fixed", 1) == directory / "models/validation/ridge/h1/fixed/fold-1"
        assert current.preprocessing_state_directory(directory, "ridge", 1, 1) == directory / "models/preprocessing/ridge/h1/fold-1"
        assert paths.approved_dataset(current.root) == current.dataset
        assert paths.execution_record(current.root) == current.execution_record
        assert paths.output_root(current.root) == current.output_root
        assert paths.run_directory(current.root, "reviewed-01") == directory
        assert paths.validation_models(directory) == current.validation_model_directory(directory)
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("value", ["", "..", "../escape", "/outside", "a/b", None])
def test_layout_rejects_unsafe_run_ids(tmp_path, value):
    with pytest.raises(ValueError):
        paths.RepositoryLayout(tmp_path).run_directory(value)


def test_layout_and_model_paths_preserve_symlink_containment(tmp_path):
    repository, outside = tmp_path / "repository", tmp_path / "outside"
    repository.mkdir()
    outside.mkdir()
    (repository / "outputs").symlink_to(outside, target_is_directory=True)
    layout = paths.RepositoryLayout(repository)
    with pytest.raises(ValueError):
        layout.run_directory("reviewed")
    directory = repository / "isolated-run"
    directory.mkdir()
    (directory / "models").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError):
        layout.validation_model_directory(directory)
    with pytest.raises(ValueError):
        layout.preprocessing_state_directory(directory, "ridge", 1, 1)
    with pytest.raises(ValueError):
        layout.repository_path("../outside")


def test_normal_run_directory_preserves_paths_without_creating_files(tmp_path):
    layout = paths.RepositoryLayout(tmp_path)
    expected = tmp_path / "outputs/revised-forecasting/reviewed-01"
    assert layout.run_directory("reviewed-01") == expected
    assert not list(tmp_path.iterdir())
    expected.mkdir(parents=True)
    before = set(tmp_path.rglob("*"))
    assert layout.run_directory("reviewed-01") == expected
    assert paths.run_directory(tmp_path, "reviewed-01") == expected
    assert set(tmp_path.rglob("*")) == before


@pytest.mark.parametrize("inside_repository", [False, True])
def test_output_root_symlink_redirect_rejected(tmp_path, inside_repository):
    repository = tmp_path / "repository"
    repository.mkdir()
    target = (repository if inside_repository else tmp_path) / "redirected"
    target.mkdir()
    layout = paths.RepositoryLayout(repository)
    layout.output_root.parent.mkdir()
    layout.output_root.symlink_to(target, target_is_directory=True)
    before = set(tmp_path.rglob("*"))
    with pytest.raises(ValueError):
        layout.run_directory("reviewed")
    with pytest.raises(ValueError):
        paths.run_directory(repository, "reviewed")
    assert set(tmp_path.rglob("*")) == before
    assert not list(target.iterdir())


def test_run_directory_symlink_must_remain_inside_output_root(tmp_path):
    layout = paths.RepositoryLayout(tmp_path)
    layout.output_root.mkdir(parents=True)
    target = tmp_path / "other-run-location"
    target.mkdir()
    (layout.output_root / "reviewed").symlink_to(target, target_is_directory=True)
    with pytest.raises(ValueError, match="inside the forecasting output root"):
        layout.run_directory("reviewed")
    assert not list(target.iterdir())
