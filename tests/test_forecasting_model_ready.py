"""Phase 4 lifecycle evidence using temporary synthetic data only; no experiment."""
import json
from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest

from src.forecasting import execution, model_ready, preprocessing
from src.forecasting.artifacts import file_hash
from src.forecasting.authorization import ExecutionBlocked
from src.forecasting.evaluation import frame_hash, prepare_fold
from src.forecasting.features import FEATURE_COLUMNS, KEY_COLUMNS
from src.forecasting.paths import REPOSITORY, RepositoryLayout
from src.forecasting.metadata import DECISION_REFERENCES
from src.forecasting.targets import FORECAST_HORIZONS
from forecasting_handoff_helpers import panel, publish_forecasting_handoff


@pytest.fixture
def provenance_repository(monkeypatch):
    git = Mock(return_value={"git_commit_sha": "synthetic-repository-revision",
                            "git_branch": "synthetic-repository-branch", "git_dirty": True})
    monkeypatch.setattr(model_ready, "git_state", git)
    def initialize(root):
        # Explicit synthetic repository inputs; no real Git operations.
        paths = ("docs/protocol.md", "docs/forecasting-feature-engineering.md", "AGENTS.md",
                 "requirements.txt", "requirements-dev.txt", "src/forecasting/features.py", *DECISION_REFERENCES)
        for relative in paths:
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((REPOSITORY / relative).read_bytes())
        return RepositoryLayout(root)
    return initialize


@pytest.fixture
def validated_source(tmp_path, provenance_repository):
    provenance_repository(tmp_path)
    return publish_forecasting_handoff(tmp_path, panel())


@pytest.fixture
def ready(tmp_path, validated_source):
    return model_ready.prepare_model_ready(repository=tmp_path, representation_id="synthetic-fold-1", fold_number=1,
                                          expected_provenance_sha256=validated_source.provenance_sha256)


def test_complete_lifecycle_separation_horizons_and_exact_existing_semantics(tmp_path, ready):
    metadata, tables = model_ready.read_model_ready(repository=tmp_path, representation_id="synthetic-fold-1",
                                                   expected_metadata_sha256=ready.metadata_sha256)
    source = execution.load_projection(RepositoryLayout(tmp_path), fold_number=1).frame
    expected = prepare_fold(source, 1)
    assert list(tables["projection.parquet"].columns) == list(execution.FORECAST_INPUT_COLUMNS)
    pd.testing.assert_frame_equal(tables["projection.parquet"], source, check_exact=True)
    origin = tables["origin-features.parquet"]
    pd.testing.assert_frame_equal(origin, expected.origin_features, check_exact=True)
    assert len(origin) == 4 and origin.Date.eq(pd.Timestamp("2024-04-01")).all()
    assert list(origin.columns) == [*KEY_COLUMNS, *FEATURE_COLUMNS]
    for horizon in FORECAST_HORIZONS:
        features = tables[f"h{horizon}/training-features.parquet"]
        targets = tables[f"h{horizon}/training-targets.parquet"]
        outcomes = tables[f"h{horizon}/validation-targets.parquet"]
        pd.testing.assert_frame_equal(features, expected.horizons[horizon].features, check_exact=True)
        assert list(features.columns) == [*KEY_COLUMNS, *FEATURE_COLUMNS]
        assert list(targets.columns) == list(outcomes.columns) == [*KEY_COLUMNS, f"target_{horizon}_day"]
        pd.testing.assert_frame_equal(features.loc[:, list(KEY_COLUMNS)], targets.loc[:, list(KEY_COLUMNS)])
        np.testing.assert_array_equal(targets[f"target_{horizon}_day"], expected.horizons[horizon].labels)
        np.testing.assert_array_equal(outcomes[f"target_{horizon}_day"], expected.horizons[horizon].observed_targets)
        for pair, group in source.groupby(["SKU_ID", "Warehouse_ID"], sort=True):
            realised = group.loc[group.Date.between("2024-04-01", pd.Timestamp("2024-03-31") + pd.Timedelta(days=horizon)), "Units_Sold"].sum()
            row = outcomes.loc[outcomes.SKU_ID.eq(pair[0]) & outcomes.Warehouse_ID.eq(pair[1])]
            assert row[f"target_{horizon}_day"].iloc[0] == realised
        assert (features.Date + pd.Timedelta(days=horizon - 1)).le(pd.Timestamp("2024-03-31")).all()
        for model in model_ready.MODELS:
            matrix = tables[f"h{horizon}/{model}/training-matrix.parquet"]
            state = expected.horizons[horizon].preprocessors[model]
            pd.testing.assert_frame_equal(matrix.loc[:, list(state.physical_feature_names)], state.transform(features), check_exact=True)
            assert list(matrix.columns) == [*KEY_COLUMNS, *state.physical_feature_names]
            assert not any(c.startswith("target_") or c == "Units_Sold" for c in matrix.columns)
    assert metadata["experiment_execution"] == metadata["model_training"] == "not_performed"
    assert metadata["human_review"] == {"status": "pending_human_review", "reference": None}
    assert not (tmp_path / "outputs").exists()
    assert not (tmp_path / "models").exists()


def test_provenance_parent_receipts_schema_versions_and_output_hashes(tmp_path, validated_source, ready):
    metadata, tables = model_ready.read_model_ready(repository=tmp_path, representation_id="synthetic-fold-1")
    parent = metadata["parent"]
    original = json.loads((validated_source.directory / "provenance.json").read_text())
    assert parent["provenance_sha256"] == validated_source.provenance_sha256
    assert parent["files"] == original["files"]
    assert parent["source_receipt"] == original["source"]
    assert parent["data_version"] == original["data_version"]
    assert parent["projection_fingerprint"] == frame_hash(tables["projection.parquet"])
    assert metadata["schema_version"] == model_ready.SCHEMA_VERSION
    assert metadata["metadata_version"] == model_ready.METADATA_VERSION
    assert metadata["protocol"]["sha256"]
    assert metadata["implementation"]["source_hashes"]["src/forecasting/features.py"]
    assert metadata["scope"]["reserved_final"]["status"] == "blocked_not_materialized"
    for relative, record in metadata["files"].items():
        assert record["sha256"] == file_hash(ready.directory / relative)
        if relative in tables:
            assert record["columns"] == list(tables[relative].columns)
            assert record["logical_fingerprint"] == frame_hash(tables[relative])
            assert record["row_count"] == len(tables[relative])
    assert ready.metadata_sha256 == file_hash(ready.directory / model_ready.METADATA_FILE)


def test_preprocessing_is_fitted_only_on_eligible_historical_rows(tmp_path, validated_source, monkeypatch):
    original = preprocessing.fit_preprocessor
    seen = []
    def fit(features, model, **kwargs):
        seen.append((model, kwargs["horizon"], features.copy(), kwargs["training_end"]))
        assert features.Date.le(pd.Timestamp("2024-03-31")).all()
        assert (features.Date + pd.Timedelta(days=kwargs["horizon"] - 1)).le(pd.Timestamp("2024-03-31")).all()
        assert not any(c.startswith("target_") or c == "Units_Sold" for c in features.columns)
        return original(features, model, **kwargs)
    # Primary states call this owner through fit_primary_preprocessors; supportive calls are imported by evaluation.
    monkeypatch.setattr(preprocessing, "fit_preprocessor", fit)
    monkeypatch.setattr("src.forecasting.evaluation.fit_preprocessor", fit)
    result = model_ready.prepare_model_ready(repository=tmp_path, representation_id="training-only", fold_number=1)
    metadata, tables = model_ready.read_model_ready(repository=tmp_path, representation_id="training-only")
    assert len(seen) == 12  # One shared primary fit + Ridge + Random Forest for each horizon.
    for model, horizon, rows, cutoff in seen:
        persisted = tables[f"h{horizon}/training-features.parquet"]
        pd.testing.assert_frame_equal(rows, persisted, check_exact=True)
        state_path = result.directory / metadata["horizons"][str(horizon)]["representations"][model]["preprocessing_path"]
        state = preprocessing.restore_preprocessor(json.loads(state_path.read_text()))
        assert state.training_row_count == len(rows)
        if model == "ridge":
            np.testing.assert_array_equal(state.numerical_means, rows.loc[:, list(FEATURE_COLUMNS)].mean().to_numpy())
    assert all(cutoff.isoformat() == "2024-03-31" for _, _, _, cutoff in seen)


def test_future_outcomes_cannot_change_features_or_preprocessing(tmp_path, provenance_repository):
    baseline = panel()
    changed = baseline.copy()
    changed.loc[changed.Date.gt(pd.Timestamp("2024-03-31")), "Units_Sold"] += 10000
    provenance_repository(tmp_path / "before")
    provenance_repository(tmp_path / "after")
    publish_forecasting_handoff(tmp_path / "before", baseline)
    publish_forecasting_handoff(tmp_path / "after", changed)
    for root in (tmp_path / "before", tmp_path / "after"):
        model_ready.prepare_model_ready(repository=root, representation_id="same-scope", fold_number=1)
    before_meta, before = model_ready.read_model_ready(repository=tmp_path / "before", representation_id="same-scope")
    after_meta, after = model_ready.read_model_ready(repository=tmp_path / "after", representation_id="same-scope")
    for relative in before:
        if "validation-targets" not in relative and relative != "projection.parquet":
            pd.testing.assert_frame_equal(before[relative], after[relative], check_exact=True)
    for horizon in FORECAST_HORIZONS:
        a, b = (meta["horizons"][str(horizon)] for meta in (before_meta, after_meta))
        assert a["training_population_hash"] == b["training_population_hash"]
        assert a["representations"] == b["representations"]
        # The existing eligibility receipt fingerprints the scoped input, including validation outcomes.
        assert [{k: v for k, v in row.items() if k != "input_view_hash"} for row in a["eligibility"]] == [
            {k: v for k, v in row.items() if k != "input_view_hash"} for row in b["eligibility"]]
        for model in model_ready.MODELS:
            path = f"data/processed/model-ready/same-scope/h{horizon}/{model}/preprocessing.json"
            assert (tmp_path / "before" / path).read_bytes() == (tmp_path / "after" / path).read_bytes()
    assert not before["h28/validation-targets.parquet"].equals(after["h28/validation-targets.parquet"])


@pytest.mark.parametrize("fold_number", [1, 2, 3, 4])
def test_each_frozen_fold_scopes_before_preparation_and_preserves_origin(tmp_path, validated_source, monkeypatch, fold_number):
    from src.forecasting.validation import VALIDATION_FOLDS
    original = model_ready.prepare_fold
    seen = []
    def prepare(data, number):
        seen.append(data.Date.max())
        return original(data, number)
    monkeypatch.setattr(model_ready, "prepare_fold", prepare)
    result = model_ready.prepare_model_ready(repository=tmp_path, representation_id=f"fold-{fold_number}", fold_number=fold_number)
    metadata, tables = model_ready.read_model_ready(repository=tmp_path, representation_id=result.directory.name)
    fold = VALIDATION_FOLDS[fold_number - 1]
    assert seen == [pd.Timestamp(fold.validation.end)]
    assert tables["origin-features.parquet"].Date.eq(pd.Timestamp(fold.validation.start)).all()
    assert metadata["scope"]["forecast_origin"] == fold.training.end.isoformat()
    assert all(frame.Date.lt(pd.Timestamp("2024-12-03")).all() for frame in tables.values())


@pytest.mark.parametrize("stage,fold", [("final_evaluation", 4), ("final_refit", 4), ("validation", 0), ("validation", 5), ("validation", True)])
def test_final_evaluation_and_invalid_folds_block_before_any_input_or_output(tmp_path, monkeypatch, stage, fold):
    forbidden = Mock(side_effect=AssertionError("No protected data or fitting"))
    monkeypatch.setattr(model_ready, "load_projection", forbidden)
    with pytest.raises(ExecutionBlocked):
        model_ready.prepare_model_ready(repository=tmp_path, representation_id="blocked", fold_number=fold, stage=stage)
    forbidden.assert_not_called()
    assert not list(tmp_path.iterdir())


def test_no_estimator_or_experiment_entry_is_called(tmp_path, validated_source, monkeypatch):
    forbidden = Mock(side_effect=AssertionError("Data preparation must not train or execute"))
    for target in ("src.forecasting.models.construct_estimator", "src.forecasting.models.fit_estimator",
                   "src.forecasting.orchestration.run_validation", "src.forecasting.experiment.run_validation"):
        monkeypatch.setattr(target, forbidden)
    model_ready.prepare_model_ready(repository=tmp_path, representation_id="preparation-only", fold_number=1)
    forbidden.assert_not_called()


def test_existing_version_is_immutable_before_data_loading(tmp_path, ready, monkeypatch):
    before = {p: p.read_bytes() for p in ready.directory.rglob("*") if p.is_file()}
    forbidden = Mock(side_effect=AssertionError("Existing representation must not be recomputed"))
    monkeypatch.setattr(model_ready, "load_projection", forbidden)
    with pytest.raises(FileExistsError):
        model_ready.prepare_model_ready(repository=tmp_path, representation_id="synthetic-fold-1", fold_number=1)
    assert before == {p: p.read_bytes() for p in before}
    forbidden.assert_not_called()


def test_incomplete_persistence_is_not_a_consumable_version(tmp_path, validated_source, monkeypatch):
    original = model_ready._parquet
    calls = []
    def fail(directory, relative, *args):
        calls.append(relative)
        if len(calls) == 2:
            raise OSError("controlled persistence failure")
        return original(directory, relative, *args)
    monkeypatch.setattr(model_ready, "_parquet", fail)
    with pytest.raises(OSError, match="controlled"):
        model_ready.prepare_model_ready(repository=tmp_path, representation_id="incomplete", fold_number=1)
    directory = tmp_path / "data/processed/model-ready/incomplete"
    assert directory.exists() and not (directory / model_ready.METADATA_FILE).exists()
    with pytest.raises(ValueError, match="Incomplete"):
        model_ready.read_model_ready(repository=tmp_path, representation_id="incomplete")


@pytest.mark.parametrize("relative", ["projection.parquet", "h7/training-targets.parquet", "h1/ridge/preprocessing.json", "model-ready.json"])
def test_corrupt_persisted_data_or_metadata_is_rejected(tmp_path, ready, relative):
    path = ready.directory / relative
    path.write_bytes(path.read_bytes() + b"corrupt")
    with pytest.raises(ValueError):
        model_ready.read_model_ready(repository=tmp_path, representation_id="synthetic-fold-1",
                                    expected_metadata_sha256=ready.metadata_sha256)


@pytest.mark.parametrize("name", ["../escape", "", "/absolute", "a/b", "CON", "name."])
def test_unsafe_representation_ids_reject_before_data_loading(tmp_path, monkeypatch, name):
    forbidden = Mock()
    monkeypatch.setattr(model_ready, "load_projection", forbidden)
    with pytest.raises(ValueError):
        model_ready.prepare_model_ready(repository=tmp_path, representation_id=name, fold_number=1)
    forbidden.assert_not_called()


def test_model_ready_path_cannot_redirect_even_inside_repository(tmp_path, monkeypatch):
    (tmp_path / "data/processed").mkdir(parents=True)
    destination = tmp_path / "redirected"
    destination.mkdir()
    (tmp_path / "data/processed/model-ready").symlink_to(destination, target_is_directory=True)
    with pytest.raises(ValueError, match="redirect"):
        model_ready.prepare_model_ready(repository=tmp_path, representation_id="bad-link", fold_number=1)
    assert not list(destination.iterdir())


def test_changed_parent_projection_prevents_completed_publication(tmp_path, validated_source, monkeypatch):
    original = model_ready.load_projection
    calls = []
    def load(*args, **kwargs):
        result = original(*args, **kwargs)
        calls.append(kwargs)
        if len(calls) == 2:
            result.frame.loc[0, "Units_Sold"] += 1
        return result
    monkeypatch.setattr(model_ready, "load_projection", load)
    with pytest.raises(ValueError, match="changed during preparation"):
        model_ready.prepare_model_ready(repository=tmp_path, representation_id="changed-parent", fold_number=1)
    assert calls[1]["expected_provenance_sha256"] == validated_source.provenance_sha256
    assert not (tmp_path / "data/processed/model-ready/changed-parent/model-ready.json").exists()


def test_alternate_layout_provenance_uses_its_own_repository(tmp_path, validated_source, monkeypatch):
    layout = RepositoryLayout(tmp_path)
    # Make the supplied protocol, feature contract and source distinguishable from globals.
    for path in (layout.protocol, layout.feature_contract, layout.repository_path("src/forecasting/features.py")):
        path.write_bytes(path.read_bytes() + b"\n# synthetic alternate-layout provenance marker\n")
    expected_sources = model_ready.source_hashes(layout.root)
    sources = Mock(wraps=model_ready.source_hashes)
    monkeypatch.setattr(model_ready, "source_hashes", sources)
    monkeypatch.setattr(model_ready, "REPOSITORY", tmp_path / "forbidden-global-root")
    result = model_ready.prepare_model_ready(repository=layout.root, representation_id="alternate-provenance", fold_number=1)
    metadata, _ = model_ready.read_model_ready(repository=layout.root, representation_id=result.directory.name)
    assert metadata["protocol"]["sha256"] == file_hash(layout.protocol) != file_hash(REPOSITORY / "docs/protocol.md")
    assert metadata["protocol"]["feature_contract_sha256"] == file_hash(layout.feature_contract) != file_hash(
        REPOSITORY / "docs/forecasting-feature-engineering.md")
    assert metadata["implementation"]["source_hashes"] == expected_sources
    assert expected_sources["src/forecasting/features.py"] != file_hash(REPOSITORY / "src/forecasting/features.py")
    sources.assert_called_once_with(layout.root)
    model_ready.git_state.assert_called_once_with(layout.root)
    for key, value in model_ready.git_state.return_value.items():
        assert metadata["implementation"][key] == value
