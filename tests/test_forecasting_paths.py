"""Approved forecasting paths, confinement and no-write resolution."""
from dataclasses import FrozenInstanceError
import importlib
import pytest
from src.forecasting import paths


RUN_METHODS = ("run_directory", "model_run_directory", "draft_report_directory")


def test_fixed_paths_and_no_import_side_effects(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    importlib.reload(paths)
    assert not list(tmp_path.iterdir())
    assert paths.REPOSITORY.name == "retail-demand-framework"
    assert paths.approved_dataset(tmp_path) == tmp_path / "data/processed/validated/supply-chain-dataset1-validated-v1/validated.parquet"
    assert paths.execution_record(tmp_path) == tmp_path / "data/processed/forecasting/validation_authorization.json"
    assert paths.run_directory(tmp_path, "reviewed-01") == tmp_path / "artifacts/forecasting/reviewed-01"
    assert not list(tmp_path.iterdir())


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
        assert current.artifact_root == current.root / "artifacts/forecasting"
        assert current.model_root == current.root / "models/forecasting"
        assert current.draft_report_root == current.root / "reports/forecasting/drafts"
        assert current.output_root == current.artifact_root
        directory = current.run_directory("reviewed-01")
        models = current.model_run_directory("reviewed-01")
        assert directory == current.artifact_root / "reviewed-01"
        assert models == current.model_root / "reviewed-01"
        assert current.draft_report_directory("reviewed-01") == current.draft_report_root / "reviewed-01"
        assert current.validation_model_directory(directory) == models / "validation"
        assert current.candidate_model_directory(directory, "ridge", 1, "fixed", 1) == models / "validation/ridge/h1/fixed/fold-1"
        assert current.preprocessing_state_directory(directory, "ridge", 1, 1) == models / "preprocessing/ridge/h1/fold-1"
        assert paths.approved_dataset(current.root) == current.dataset
        assert paths.execution_record(current.root) == current.execution_record
        assert paths.output_root(current.root) == current.artifact_root
        assert paths.run_directory(current.root, "reviewed-01") == directory
        assert paths.validation_models(directory) == current.validation_model_directory(directory)
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("method", RUN_METHODS)
@pytest.mark.parametrize("value", ["", ".", "..", "../escape", "/outside", "a/b", "a\\b", "a" * 65, None, True])
def test_layout_rejects_unsafe_run_ids(tmp_path, method, value):
    with pytest.raises(ValueError, match="run_id"):
        getattr(paths.RepositoryLayout(tmp_path), method)(value)
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("value", ["", "..", "../escape", "/outside", "a/b", None])
def test_unsafe_run_ids_rejected_by_compatibility_wrapper(tmp_path, value):
    with pytest.raises(ValueError):
        paths.run_directory(tmp_path, value)


@pytest.mark.parametrize("method", RUN_METHODS)
def test_normal_run_paths_preserve_existing_files_without_creating_any(tmp_path, method):
    layout = paths.RepositoryLayout(tmp_path)
    directory = getattr(layout, method)("reviewed-01")
    assert not list(tmp_path.iterdir())
    directory.mkdir(parents=True)
    marker = directory / "partial-evidence"
    marker.write_bytes(b"original")
    before = set(tmp_path.rglob("*"))
    assert getattr(layout, method)("reviewed-01") == directory
    assert set(tmp_path.rglob("*")) == before
    assert marker.read_bytes() == b"original"


@pytest.mark.parametrize("relative,method", [
    ("artifacts", "run_directory"),
    ("artifacts/forecasting", "run_directory"),
    ("artifacts/forecasting/reviewed", "run_directory"),
    ("models", "model_run_directory"),
    ("models/forecasting", "model_run_directory"),
    ("models/forecasting/reviewed", "model_run_directory"),
    ("reports", "draft_report_directory"),
    ("reports/forecasting", "draft_report_directory"),
    ("reports/forecasting/drafts", "draft_report_directory"),
    ("reports/forecasting/drafts/reviewed", "draft_report_directory"),
])
@pytest.mark.parametrize("target_kind", ["inside", "outside", "missing"])
def test_storage_components_reject_symlink_redirection_without_writes(tmp_path, relative, method, target_kind):
    repository = tmp_path / "repository"
    repository.mkdir()
    target = (repository if target_kind == "inside" else tmp_path) / "redirected"
    if target_kind != "missing":
        target.mkdir()
    link = repository / relative
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(target, target_is_directory=True)
    before = set(tmp_path.rglob("*"))
    with pytest.raises(ValueError, match="symlink"):
        getattr(paths.RepositoryLayout(repository), method)("reviewed")
    assert set(tmp_path.rglob("*")) == before
    if target.exists():
        assert not list(target.iterdir())


@pytest.mark.parametrize("relative", [
    "models/forecasting/reviewed/validation",
    "models/forecasting/reviewed/validation/ridge/h1/fixed/fold-1",
    "models/forecasting/reviewed/preprocessing",
    "models/forecasting/reviewed/preprocessing/ridge/h1/fold-1",
])
@pytest.mark.parametrize("inside_repository", [False, True])
def test_model_and_preprocessing_paths_reject_redirected_descendants(tmp_path, relative, inside_repository):
    repository = tmp_path / "repository"
    repository.mkdir()
    layout = paths.RepositoryLayout(repository)
    directory = layout.run_directory("reviewed")
    target = (repository if inside_repository else tmp_path) / "redirected"
    target.mkdir()
    link = repository / relative
    link.parent.mkdir(parents=True)
    link.symlink_to(target, target_is_directory=True)
    before = set(tmp_path.rglob("*"))
    with pytest.raises(ValueError):
        if "validation" in relative:
            layout.candidate_model_directory(directory, "ridge", 1, "fixed", 1)
        else:
            layout.preprocessing_state_directory(directory, "ridge", 1, 1)
    assert set(tmp_path.rglob("*")) == before
    assert not list(target.iterdir())


def test_canonical_artifact_anchor_resolves_exact_run_in_nested_alternate_layout(tmp_path, monkeypatch):
    layout = paths.RepositoryLayout(tmp_path / "nested/alternate-repository")
    directory = layout.run_directory("reviewed-01")
    monkeypatch.chdir(tmp_path)
    restored = paths.RepositoryLayout.from_artifact_directory(directory)
    assert restored == layout
    assert restored.model_run_directory(directory.name) == layout.model_run_directory("reviewed-01")
    assert restored.draft_report_directory(directory.name) == layout.draft_report_directory("reviewed-01")
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("relative", [
    "outputs/revised-forecasting/reviewed",
    "models/forecasting/reviewed",
    "reports/forecasting/drafts/reviewed",
    "artifacts/forecasting",
    "artifacts/forecasting/reviewed/extra",
    "artifacts/forecasting/reviewed/../other",
])
def test_noncanonical_anchors_are_rejected(tmp_path, relative):
    directory = tmp_path / relative
    with pytest.raises(ValueError):
        paths.RepositoryLayout.from_artifact_directory(directory)
    with pytest.raises(ValueError):
        paths.validation_models(directory)
    assert not list(tmp_path.iterdir())


def test_relative_artifact_anchor_is_rejected(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="canonical"):
        paths.RepositoryLayout.from_artifact_directory(paths.Path("artifacts/forecasting/reviewed"))
    assert not list(tmp_path.iterdir())


def test_artifact_anchor_cannot_redirect_to_another_run(tmp_path):
    layout = paths.RepositoryLayout(tmp_path)
    other = layout.run_directory("other")
    other.mkdir(parents=True)
    directory = layout.artifact_root / "reviewed"
    directory.symlink_to(other, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        paths.RepositoryLayout.from_artifact_directory(directory)
    assert not list(other.iterdir())


@pytest.mark.parametrize("model,configuration", [("../escape", "fixed"), ("ridge", "../../escape")])
def test_model_components_cannot_traverse_storage_paths(tmp_path, model, configuration):
    layout = paths.RepositoryLayout(tmp_path)
    directory = layout.run_directory("reviewed")
    with pytest.raises(ValueError):
        layout.candidate_model_directory(directory, model, 1, configuration, 1)
    with pytest.raises(ValueError):
        layout.preprocessing_state_directory(directory, "../escape", 1, 1)
    assert not list(tmp_path.iterdir())


def test_repository_reference_cannot_escape_root(tmp_path):
    with pytest.raises(ValueError, match="escapes"):
        paths.RepositoryLayout(tmp_path).repository_path("../outside")


@pytest.mark.parametrize("relative,method", [
    ("artifacts", "run_directory"),
    ("artifacts/forecasting", "run_directory"),
    ("models", "model_run_directory"),
    ("models/forecasting", "model_run_directory"),
    ("reports", "draft_report_directory"),
    ("reports/forecasting", "draft_report_directory"),
    ("reports/forecasting/drafts", "draft_report_directory"),
])
def test_existing_non_directory_storage_ancestor_rejected_without_writes(tmp_path, relative, method):
    blocker = tmp_path / relative
    blocker.parent.mkdir(parents=True, exist_ok=True)
    blocker.write_bytes(b"original file")
    before = set(tmp_path.rglob("*"))
    with pytest.raises(ValueError, match="ancestors must be directories"):
        getattr(paths.RepositoryLayout(tmp_path), method)("reviewed")
    assert set(tmp_path.rglob("*")) == before
    assert blocker.read_bytes() == b"original file"
