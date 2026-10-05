"""Lifecycle definitions over temporary synthetic Phase 4 parents; no real data."""
from dataclasses import replace
import json
from pathlib import Path
import shutil
from unittest.mock import Mock

import pytest

from forecasting_handoff_helpers import panel, publish_forecasting_handoff
from src.forecasting import lifecycle, model_ready
from src.forecasting.artifacts import file_hash, json_text
from src.forecasting.metadata import DECISION_REFERENCES
from src.forecasting.paths import REPOSITORY, RepositoryLayout
from src.forecasting.targets import FORECAST_HORIZONS
from src.forecasting.validation import FINAL_HOLDOUT, VALIDATION_FOLDS


GIT_STATE = {"git_commit_sha": "synthetic-revision", "git_branch": "synthetic-branch", "git_dirty": True}


@pytest.fixture(scope="module")
def prepared_repository(tmp_path_factory):
    root = tmp_path_factory.mktemp("synthetic-lifecycle-parents")
    paths = ("docs/protocol.md", "docs/forecasting-feature-engineering.md", "AGENTS.md",
             "requirements.txt", "requirements-dev.txt", "src/forecasting/features.py", *DECISION_REFERENCES)
    for relative in paths:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((REPOSITORY / relative).read_bytes())
    parent = publish_forecasting_handoff(root, panel())
    references = {}
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(model_ready, "git_state", lambda repository: dict(GIT_STATE))
        for fold in VALIDATION_FOLDS:
            result = model_ready.prepare_model_ready(
                repository=root, representation_id=f"synthetic-fold-{fold.number}", fold_number=fold.number,
                expected_provenance_sha256=parent.provenance_sha256,
            )
            references[fold.number] = lifecycle.ModelReadyReference(result.directory.name, result.metadata_sha256)
    return root, references


@pytest.fixture
def parents(tmp_path, prepared_repository, monkeypatch):
    root, references = prepared_repository
    shutil.copytree(root, tmp_path, dirs_exist_ok=True)
    monkeypatch.setattr(lifecycle, "git_state", lambda repository: dict(GIT_STATE))
    return tmp_path, dict(references)


def publish(parents, version="synthetic-v1"):
    root, references = parents
    return lifecycle.publish_lifecycle(repository=root, version=version, representations=references)


def read(root, result, version="synthetic-v1"):
    return lifecycle.read_lifecycle(repository=root, version=version,
                                    expected_validation_sha256=result.validation_sha256,
                                    expected_reserved_final_sha256=result.reserved_final_sha256)


def assert_no_publication(root):
    assert not (root / "data/processed/validation").exists()
    assert not (root / "data/processed/reserved-final").exists()


def change_metadata(root, references, change):
    path = root / "data/processed/model-ready" / references[1].representation_id / model_ready.METADATA_FILE
    metadata = json.loads(path.read_text())
    change(metadata)
    path.write_text(json_text(metadata))
    references[1] = replace(references[1], metadata_sha256=file_hash(path))


def test_complete_views_reference_exact_folds_schemas_hashes_and_populations(parents):
    root, references = parents
    before = {p.relative_to(root): p.read_bytes() for p in (root / "data").rglob("*") if p.is_file()}
    result = publish(parents)
    validation, reserved = read(root, result)
    assert result.validation_directory == root / "data/processed/validation/synthetic-v1"
    assert result.reserved_final_directory == root / "data/processed/reserved-final/synthetic-v1"
    assert validation["schema_version"] == lifecycle.VALIDATION_SCHEMA
    assert reserved["schema_version"] == lifecycle.RESERVED_FINAL_SCHEMA
    for definition in (validation, reserved):
        assert definition["publication_status"] == "complete"
        assert definition["human_review"] == {"status": "pending_human_review", "reference": None}
    assert validation["generation"] == reserved["generation"]
    assert validation["generation"]["implementation"]["git_commit_sha"] == "synthetic-revision"
    assert validation["generation"]["implementation"]["source_hashes"]
    assert validation["validated_parent"] == reserved["validated_parent"]
    assert [view["fold_id"] for view in validation["folds"]] == [1, 2, 3, 4]
    for fold, view in zip(VALIDATION_FOLDS, validation["folds"], strict=True):
        identity = view["model_ready"]
        metadata_path = root / identity["metadata_path"]
        metadata = json.loads(metadata_path.read_text())
        assert identity["metadata_sha256"] == file_hash(metadata_path) == references[fold.number].metadata_sha256
        assert identity["schema_version"] == model_ready.SCHEMA_VERSION
        assert identity["metadata_version"] == model_ready.METADATA_VERSION
        assert view["scope"] == metadata["scope"]
        assert view["pair_key_hash"] == metadata["pair_key_hash"]
        assert view["projection_fingerprint"] == metadata["parent"]["projection_fingerprint"]
        assert view["origin_features"]["schema"] == metadata["files"]["origin-features.parquet"]["schema"]
        for horizon in FORECAST_HORIZONS:
            details = view["horizons"][str(horizon)]
            original = metadata["horizons"][str(horizon)]
            target = details["validation_targets"]
            assert target["sha256"] == file_hash(root / target["path"])
            assert target["schema"] == metadata["files"][f"h{horizon}/validation-targets.parquet"]["schema"]
            assert details["training_population_hash"] == original["training_population_hash"]
            assert details["representations"] == original["representations"]
            assert details["target_start"] == fold.validation.start.isoformat()
            assert details["target_end"] == original["target_end"]
    assert all((root / relative).read_bytes() == contents for relative, contents in before.items())
    new_paths = {p.relative_to(root).as_posix() for p in (root / "data").rglob("*") if p.is_file()} - {
        p.as_posix() for p in before}
    assert new_paths == {"data/processed/validation/synthetic-v1/views.json",
                         "data/processed/reserved-final/synthetic-v1/view.json"}


def test_reserved_final_is_metadata_only_and_cannot_grant_access_or_compute_outcomes(parents, monkeypatch):
    root, _ = parents
    forbidden = Mock(side_effect=AssertionError("No input preparation, final outcome decoding, training or experiment"))
    for name in ("src.data.validated_handoff.read_validated_handoff", "src.data.validated_handoff.read_validated_projection",
                 "src.forecasting.model_ready.prepare_model_ready", "src.forecasting.execution.load_projection",
                 "src.forecasting.model_ready.prepare_fold", "src.forecasting.models.construct_estimator",
                 "src.forecasting.models.fit_estimator", "src.forecasting.orchestration.run_validation",
                 "src.forecasting.orchestration.run_final_evaluation"):
        monkeypatch.setattr(name, forbidden)
    original_read = model_ready.pq.ParquetFile.read
    def scoped_read(parquet, *args, **kwargs):
        table = original_read(parquet, *args, **kwargs)
        # All decoded tables are existing validation-scoped model-ready tables.
        assert all(day < FINAL_HOLDOUT.start for day in table["Date"].to_pylist())
        return table
    monkeypatch.setattr(model_ready.pq.ParquetFile, "read", scoped_read)
    result = publish(parents)
    _, reserved = read(root, result)
    forbidden.assert_not_called()
    assert set(reserved) == {"lifecycle_version", "generation", "protocol", "validated_parent", "publication_status", "human_review",
                             "schema_version", "evaluation_stage", "interval", "forecast_origin", "horizons",
                             "access_status", "evaluation_status", "outcomes_status"}
    assert reserved["interval"] == {"start": "2024-12-03", "end": "2024-12-30"}
    assert reserved["forecast_origin"] == "2024-12-02"
    assert reserved["horizons"] == [1, 7, 14, 28]
    assert reserved["access_status"] == "blocked_pending_separate_human_authorization"
    assert reserved["evaluation_status"] == "blocked"
    assert reserved["outcomes_status"] == "not_materialized"
    text = json_text(reserved)
    for prohibited in ("logical_fingerprint", "projection_fingerprint", "target_column", "Units_Sold", "pair_key_hash"):
        assert prohibited not in text
    assert not (root / "models").exists() and not (root / "artifacts").exists() and not (root / "outputs").exists()


@pytest.mark.parametrize("folds", [(), (1, 2, 3), (1, 2, 3, 5), (True, 2, 3, 4)])
def test_exact_four_integer_folds_required_before_any_publication(parents, folds):
    root, references = parents
    requested = {number: references.get(number, references[1]) for number in folds}
    with pytest.raises(ValueError, match="four authoritative"):
        lifecycle.publish_lifecycle(repository=root, version="invalid", representations=requested)
    assert_no_publication(root)


def test_duplicate_or_wrong_fold_identity_rejected(parents):
    root, references = parents
    references[2] = references[1]
    with pytest.raises(ValueError, match="own explicit"):
        publish(parents)
    references[2] = replace(references[1], representation_id="synthetic-fold-2",
                             metadata_sha256=file_hash(root / "data/processed/model-ready/synthetic-fold-2/model-ready.json"))
    references[1], references[2] = references[2], references[1]
    with pytest.raises(ValueError, match="wrong fold"):
        publish(parents)
    assert_no_publication(root)


@pytest.mark.parametrize("value", ["", "../escape", "/absolute", "a/b", "a\\b", "CON", "name.", "x" * 65])
@pytest.mark.parametrize("field", ["version", "representation_id"])
def test_unsafe_components_rejected_before_publication(parents, field, value):
    root, references = parents
    if field == "representation_id":
        references[1] = replace(references[1], representation_id=value)
    with pytest.raises(ValueError):
        publish(parents, version=value if field == "version" else "synthetic-v1")
    assert_no_publication(root)


@pytest.mark.parametrize("relative", ["model-ready.json", "origin-features.parquet", "h7/validation-targets.parquet",
                                      "h1/ridge/preprocessing.json"])
@pytest.mark.parametrize("defect", ["missing", "corrupt"])
def test_incomplete_or_corrupt_model_ready_parents_are_rejected(parents, relative, defect):
    root, references = parents
    path = root / "data/processed/model-ready" / references[1].representation_id / relative
    if defect == "missing":
        path.unlink()
    else:
        path.write_bytes(path.read_bytes() + b"corrupt")
    with pytest.raises((ValueError, OSError)):
        publish(parents)
    assert_no_publication(root)


@pytest.mark.parametrize("defect", ["chronology", "horizon", "population", "parent_path", "matrix_path", "file_path", "protocol"])
def test_semantically_wrong_metadata_rejected_even_with_updated_external_hash(parents, defect):
    root, references = parents
    def change(metadata):
        if defect == "chronology":
            metadata["scope"]["forecast_origin"] = "2024-04-01"
        elif defect == "horizon":
            metadata["horizons"]["7"]["target_end"] = "2024-04-08"
        elif defect == "population":
            metadata["pair_key_hash"] = "0" * 64
        elif defect == "parent_path":
            metadata["parent"]["directory"] = "data/processed/validated/../other"
        elif defect == "file_path":
            metadata["files"]["origin-features.parquet"]["path"] = "../outside.parquet"
        elif defect == "matrix_path":
            metadata["horizons"]["1"]["representations"]["ridge"]["origin_matrix"] = "../escape.parquet"
        else:
            metadata["protocol"]["sha256"] = "0" * 64
    change_metadata(root, references, change)
    with pytest.raises(ValueError):
        publish(parents)
    assert_no_publication(root)


@pytest.mark.parametrize("filename", ["validated.parquet", "provenance.json", "schema.json", "validation-audit.json"])
@pytest.mark.parametrize("defect", ["missing", "corrupt"])
def test_validated_parent_receipts_and_actual_bytes_are_verified_without_decoding(parents, filename, defect):
    root, _ = parents
    path = RepositoryLayout(root).dataset.parent / filename
    if defect == "missing":
        path.unlink()
    else:
        path.write_bytes(path.read_bytes() + b"corrupt")
    with pytest.raises((ValueError, OSError)):
        publish(parents)
    assert_no_publication(root)


@pytest.mark.parametrize("relative", ["data/processed/validation", "data/processed/reserved-final",
                                      "data/processed/model-ready/synthetic-fold-1/h1/ridge",
                                      "data/processed/validated/supply-chain-dataset1-validated-v1"])
@pytest.mark.parametrize("outside", [False, True])
def test_symlink_redirection_rejected_including_inside_repository(parents, tmp_path, relative, outside):
    root, _ = parents
    source = root / relative
    destination = tmp_path.parent / f"{tmp_path.name}-outside" if outside else root / "redirected"
    if source.exists():
        shutil.move(source, destination)
    else:
        destination.mkdir()
        source.parent.mkdir(parents=True, exist_ok=True)
    source.symlink_to(destination, target_is_directory=True)
    before = {p: p.read_bytes() for p in destination.rglob("*") if p.is_file()}
    with pytest.raises(ValueError):
        publish(parents)
    assert all(p.read_bytes() == contents for p, contents in before.items())
    assert not (destination / "synthetic-v1").exists()


@pytest.mark.parametrize("stage", ["validation", "reserved-final"])
def test_existing_version_even_empty_is_not_overwritten_or_reloaded(parents, monkeypatch, stage):
    root, _ = parents
    directory = root / "data/processed" / stage / "synthetic-v1"
    directory.mkdir(parents=True)
    forbidden = Mock(side_effect=AssertionError("Existing version cannot reload parents"))
    monkeypatch.setattr(model_ready, "read_model_ready", forbidden)
    with pytest.raises(FileExistsError):
        publish(parents)
    forbidden.assert_not_called()
    assert list(directory.iterdir()) == []


@pytest.mark.parametrize("stage,name", [("validation", "views.json"), ("reserved-final", "view.json")])
def test_definition_corruption_or_extra_files_rejected_on_read(parents, stage, name):
    root, _ = parents
    result = publish(parents)
    path = root / "data/processed" / stage / "synthetic-v1" / name
    original = path.read_bytes()
    path.write_bytes(original + b"corrupt")
    with pytest.raises(ValueError, match="hash"):
        read(root, result)
    path.write_bytes(original)
    (path.parent / "extra.json").write_text("{}")
    with pytest.raises(ValueError, match="file set"):
        read(root, result)


@pytest.mark.parametrize("defect", ["unblock", "final_fingerprint", "view_path", "fold_count", "generation"])
def test_wrong_lifecycle_semantics_rejected_even_with_updated_definition_receipts(parents, defect):
    root, _ = parents
    result = publish(parents)
    validation_path = result.validation_directory / lifecycle.VALIDATION_FILE
    reserved_path = result.reserved_final_directory / lifecycle.RESERVED_FINAL_FILE
    validation, reserved = read(root, result)
    if defect == "unblock":
        reserved["access_status"] = "allowed"
    elif defect == "final_fingerprint":
        reserved["outcome_fingerprint"] = "0" * 64
    elif defect == "view_path":
        validation["folds"][0]["origin_features"]["path"] = "../outside.parquet"
    elif defect == "fold_count":
        validation["folds"].append(validation["folds"][0])
    else:
        validation["generation"]["created_at_utc"] = "2024-01-01T00:00:00"
    validation_path.write_text(json_text(validation))
    reserved_path.write_text(json_text(reserved))
    updated = replace(result, validation_sha256=file_hash(validation_path), reserved_final_sha256=file_hash(reserved_path))
    with pytest.raises(ValueError):
        read(root, updated)


def test_parent_corruption_after_publication_is_rejected(parents):
    root, _ = parents
    result = publish(parents)
    path = root / "data/processed/model-ready/synthetic-fold-4/h28/validation-targets.parquet"
    path.write_bytes(path.read_bytes() + b"changed")
    with pytest.raises(ValueError):
        read(root, result)


def test_interrupted_publication_is_not_consumable_or_resumable(parents, monkeypatch):
    root, _ = parents
    original = Path.open
    def fail(path, mode="r", *args, **kwargs):
        if path.name == lifecycle.RESERVED_FINAL_FILE and mode == "x":
            raise OSError("controlled interrupted publication")
        return original(path, mode, *args, **kwargs)
    with monkeypatch.context() as patch:
        patch.setattr(Path, "open", fail)
        with pytest.raises(OSError, match="interrupted"):
            publish(parents)
    assert (root / "data/processed/validation/synthetic-v1/views.json").is_file()
    assert not (root / "data/processed/reserved-final/synthetic-v1/view.json").exists()
    with pytest.raises(FileExistsError):
        publish(parents)
    with pytest.raises((ValueError, OSError)):
        lifecycle.read_lifecycle(repository=root, version="synthetic-v1", expected_validation_sha256="0" * 64,
                                 expected_reserved_final_sha256="0" * 64)


def test_reproducible_definitions_and_alternate_repository_provenance(parents):
    root, _ = parents
    first = publish(parents, "first")
    second = publish(parents, "second")
    first_validation, first_reserved = read(root, first, "first")
    second_validation, second_reserved = read(root, second, "second")
    for a, b in ((first_validation, second_validation), (first_reserved, second_reserved)):
        assert {k: v for k, v in a.items() if k not in {"lifecycle_version", "generation"}} == {
            k: v for k, v in b.items() if k not in {"lifecycle_version", "generation"}}
        assert a["protocol"]["sha256"] == file_hash(root / "docs/protocol.md")
        assert a["generation"]["implementation"]["source_hashes"] == lifecycle.source_hashes(root)


def test_cli_publishes_only_definitions_and_reports_external_receipts(parents, capsys):
    root, references = parents
    arguments = ["--repository", str(root), "--version", "synthetic-v1"]
    for fold, reference in reversed(list(references.items())):
        arguments += ["--fold-reference", str(fold), reference.representation_id, reference.metadata_sha256]
    lifecycle.main(arguments)
    output = capsys.readouterr().out
    assert "Validation views:" in output and "Blocked reserved-final view:" in output
    assert output.count("SHA-256:") == 2
