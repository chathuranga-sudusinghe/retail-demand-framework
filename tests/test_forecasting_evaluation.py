"""Small synthetic daily panels; no project dataset reads, training or scores."""
import numpy as np
import pandas as pd
import pytest

from src.forecasting.evaluation import (
    PreflightError, frame_hash, prepare_fold, require_native_roster, validation_view,
)
from src.forecasting.features import KEY_COLUMNS
from src.forecasting.validation import VALIDATION_FOLDS


def synthetic_panel():
    return pd.DataFrame([{"SKU_ID": sku, "Warehouse_ID": warehouse, "Date": day,
                          "Units_Sold": base + offset % 19}
                         for sku, warehouse, base in (("A", "W1", 1), ("B", "W2", 20))
                         for offset, day in enumerate(pd.date_range("2024-01-01", "2024-12-30"))])


@pytest.mark.parametrize("fold_id,days", [(1, 91), (2, 182), (3, 274), (4, 309)])
def test_historical_label_intersection_horizon_cutoff_and_common_candidates(fold_id, days):
    prepared = prepare_fold(synthetic_panel(), fold_id)
    assert len(prepared.origin_features) == 2
    assert prepared.origin_features.Date.eq(pd.Timestamp(prepared.fold.validation.start)).all()
    assert prepared.baseline_evidence[["SKU_ID", "Warehouse_ID"]].equals(
        prepared.origin_features[["SKU_ID", "Warehouse_ID"]])
    for horizon, population in prepared.horizons.items():
        assert len(population.features) == 2 * (days - 28 - horizon + 1)
        assert len(population.labels) == len(population.features)
        assert tuple(population.features.columns)[:3] == KEY_COLUMNS
        assert not any(c.startswith("target_") for c in population.features.columns)
        ends = population.features.Date + pd.Timedelta(days=horizon - 1)
        assert ends.le(pd.Timestamp(prepared.fold.training.end)).all()
        assert population.features.Date.min() == pd.Timestamp("2024-01-29")
        assert population.training_population_hash
        for row in population.eligibility_records:
            assert row["raw_row_count"] == days
            assert row["feature_eligible_count"] == days - 28
            assert row["label_eligible_count"] == days - horizon + 1
            assert row["training_row_count"] == days - 28 - horizon + 1
        matrices = [population.preprocessors[m].transform(population.features)
                    for m in ("xgboost", "lightgbm", "catboost")]
        for matrix in matrices[1:]:
            pd.testing.assert_frame_equal(matrices[0], matrix)
        for state in population.preprocessors.values():
            assert state.training_row_count == len(population.features)
            assert state.horizon == horizon
            assert state.training_end == pd.Timestamp(prepared.fold.training.end)


def test_training_targets_missingness_intersects_before_vocabulary_or_scaler_fit():
    panel = synthetic_panel()
    panel.loc[panel.SKU_ID.eq("A") & panel.Date.eq(pd.Timestamp("2024-02-01")), "Units_Sold"] = np.nan
    prepared = prepare_fold(panel, 1)
    population = prepared.horizons[7]
    affected = population.features.loc[population.features.SKU_ID.eq("A")]
    assert not affected.Date.between(pd.Timestamp("2024-01-26"), pd.Timestamp("2024-02-01")).any()
    assert not affected.Date.between(pd.Timestamp("2024-02-02"), pd.Timestamp("2024-02-29")).any()
    assert np.isfinite(population.labels).all()
    diag = next(d for d in population.eligibility_records if d["SKU_ID"] == "A")
    assert diag["exclusion_counts"]["missing_observed_training_target"] == 7
    ridge = population.preprocessors["ridge"]
    numerical = population.features[list(ridge.numerical_feature_names)].to_numpy()
    np.testing.assert_allclose(ridge.numerical_means, numerical.mean(axis=0))


def test_validation_outcomes_change_only_independent_targets_not_training_or_origin():
    panel = synthetic_panel()
    original = prepare_fold(panel, 1)
    panel.loc[panel.Date.between(pd.Timestamp("2024-04-01"), pd.Timestamp("2024-04-28")), "Units_Sold"] = 999999
    changed = prepare_fold(panel, 1)
    pd.testing.assert_frame_equal(original.origin_features, changed.origin_features)
    for horizon in (1, 7, 14, 28):
        a, b = original.horizons[horizon], changed.horizons[horizon]
        pd.testing.assert_frame_equal(a.features, b.features)
        np.testing.assert_array_equal(a.labels, b.labels)
        assert a.preprocessors == b.preprocessors
        assert a.training_population_hash == b.training_population_hash
        np.testing.assert_array_equal(b.observed_targets, [999999 * horizon] * 2)
        assert not np.array_equal(a.observed_targets, b.observed_targets)


def test_only_authorised_horizons_require_complete_outcomes_and_fitting_vocabulary():
    source = synthetic_panel()
    source.loc[source.SKU_ID.eq("A") & source.Date.eq(pd.Timestamp("2024-04-28")), "Units_Sold"] = np.nan
    prepared = prepare_fold(source, 1, horizons=(1, 7, 14))
    assert tuple(prepared.horizons) == (1, 7, 14)
    with pytest.raises(PreflightError, match="target population"):
        prepare_fold(source, 1)
    source = synthetic_panel()
    source.loc[source.SKU_ID.eq("A") & source.Date.eq(pd.Timestamp("2024-02-15")), "Units_Sold"] = np.nan
    assert tuple(prepare_fold(source, 1, horizons=(1,)).horizons) == (1,)
    with pytest.raises(PreflightError, match="Unknown SKU_ID"):
        prepare_fold(source, 1)


def test_later_folds_learn_only_from_their_own_historical_cutoff():
    panel = synthetic_panel()
    first, second = prepare_fold(panel, 1), prepare_fold(panel, 2)
    assert first.horizons[7].preprocessors["ridge"] != second.horizons[7].preprocessors["ridge"]
    assert first.horizons[7].training_population_hash != second.horizons[7].training_population_hash
    panel.loc[panel.Date.ge(pd.Timestamp("2024-04-01")), "Units_Sold"] = 1000
    changed = prepare_fold(panel, 1)
    assert first.horizons[28].preprocessors == changed.horizons[28].preprocessors
    assert first.horizons[28].training_population_hash == changed.horizons[28].training_population_hash
    later = prepare_fold(panel, 2)
    assert second.horizons[28].training_population_hash != later.horizons[28].training_population_hash


def test_final_quantities_keys_duplicates_and_coverage_are_excluded_before_validation_hashing():
    panel = synthetic_panel()
    before = validation_view(panel)
    panel["Units_Sold"] = panel.Units_Sold.astype(object)
    future = panel.Date.ge(pd.Timestamp("2024-12-03"))
    panel.loc[future, "Units_Sold"] = "forbidden future"
    panel.loc[future, "SKU_ID"] = " invalid future ID "
    panel = pd.concat([panel, panel.loc[future].iloc[:1]], ignore_index=True)
    after = validation_view(panel)
    pd.testing.assert_frame_equal(before, after)
    assert frame_hash(before) == frame_hash(after)
    expected = prepare_fold(synthetic_panel(), 4)
    actual = prepare_fold(panel, 4)
    assert actual.input_view_hash == expected.input_view_hash
    pd.testing.assert_frame_equal(expected.origin_features, actual.origin_features)
    for horizon in (1, 7, 14, 28):
        np.testing.assert_array_equal(expected.horizons[horizon].observed_targets,
                                      actual.horizons[horizon].observed_targets)


def test_final_missing_value_dtype_coercion_cannot_change_authorised_fingerprint():
    original = synthetic_panel()
    changed = original.copy()
    changed.loc[changed.Date.ge(pd.Timestamp("2024-12-03")), "Units_Sold"] = np.nan
    assert original.Units_Sold.dtype != changed.Units_Sold.dtype
    assert frame_hash(validation_view(original)) == frame_hash(validation_view(changed))
    a, b = prepare_fold(original, 4), prepare_fold(changed, 4)
    assert a.input_view_hash == b.input_view_hash
    assert a.pair_key_hash == b.pair_key_hash
    for horizon in (1, 7, 14, 28):
        assert a.horizons[horizon].training_population_hash == b.horizons[horizon].training_population_hash


def test_source_row_index_is_not_a_native_identity_key():
    source = synthetic_panel()
    expected = prepare_fold(source, 1)
    source.index = np.zeros(len(source), dtype=int)
    actual = prepare_fold(source, 1)
    assert actual.input_view_hash == expected.input_view_hash
    pd.testing.assert_frame_equal(actual.origin_features, expected.origin_features)


def test_all_origin_horizon_targets_are_direct_cumulative_not_recursive():
    panel = synthetic_panel()
    prepared = prepare_fold(panel, 1)
    for horizon, population in prepared.horizons.items():
        end = pd.Timestamp("2024-04-01") + pd.Timedelta(days=horizon - 1)
        expected = [panel.loc[panel.SKU_ID.eq(sku) & panel.Date.between(pd.Timestamp("2024-04-01"), end), "Units_Sold"].sum()
                    for sku in ("A", "B")]
        np.testing.assert_array_equal(population.observed_targets, expected)
    raw = [prepared.origin_features[list(pop.preprocessors["xgboost"].conceptual_feature_names)]
           for pop in prepared.horizons.values()]
    for frame in raw[1:]:
        pd.testing.assert_frame_equal(raw[0], frame)


@pytest.mark.parametrize("failure", ["history", "outcome", "date", "whole_pair", "unseen_fitted_category"])
def test_preflight_never_silently_drops_pairs(failure):
    panel = synthetic_panel()
    if failure == "history":
        panel.loc[panel.SKU_ID.eq("A") & panel.Date.eq(pd.Timestamp("2024-03-31")), "Units_Sold"] = np.nan
    elif failure == "outcome":
        panel.loc[panel.SKU_ID.eq("A") & panel.Date.eq(pd.Timestamp("2024-04-28")), "Units_Sold"] = np.nan
    elif failure == "date":
        panel = panel.loc[~(panel.SKU_ID.eq("A") & panel.Date.eq(pd.Timestamp("2024-04-28")))]
    elif failure == "whole_pair":
        panel = panel.loc[~(panel.SKU_ID.eq("A") & panel.Date.ge(pd.Timestamp("2024-04-01")))]
    else:
        panel.loc[panel.SKU_ID.eq("A") & panel.Date.le(pd.Timestamp("2024-03-03")), "Units_Sold"] = np.nan
    with pytest.raises(PreflightError) as error:
        prepare_fold(panel, 1)
    assert error.value.diagnostics


def test_order_is_deterministic_and_source_is_unchanged():
    source = synthetic_panel().sample(frac=1, random_state=52).reset_index(drop=True)
    before = source.copy(deep=True)
    a, b = prepare_fold(source, 1), prepare_fold(source.iloc[::-1], 1)
    assert a.input_view_hash == b.input_view_hash
    assert a.pair_key_hash == b.pair_key_hash
    for horizon in (1, 7, 14, 28):
        assert a.horizons[horizon].training_population_hash == b.horizons[horizon].training_population_hash
        pd.testing.assert_frame_equal(a.horizons[horizon].features, b.horizons[horizon].features)
    pd.testing.assert_frame_equal(source, before)


def test_native_coverage_is_a_real_runner_preflight_not_a_future_roster():
    with pytest.raises(PreflightError, match="native 50-SKU"):
        require_native_roster(synthetic_panel())
    native_keys = pd.DataFrame([{"SKU_ID": f"S{i}", "Warehouse_ID": f"W{j}"}
                               for i in range(50) for j in range(5)])
    require_native_roster(native_keys)
    with pytest.raises(PreflightError):
        require_native_roster(native_keys.iloc[1:])


@pytest.mark.parametrize("fold", [0, 5, True, 1.0, "final_evaluation"])
def test_unapproved_fold_is_blocked(fold):
    with pytest.raises(ValueError):
        validation_view(synthetic_panel(), fold_number=fold)


def test_native_duplicates_and_invalid_historical_demand_are_not_repaired():
    panel = synthetic_panel()
    with pytest.raises(ValueError, match="Duplicate native keys"):
        prepare_fold(pd.concat([panel, panel.iloc[:1]], ignore_index=True), 1)
    panel.loc[0, "Units_Sold"] = -1
    with pytest.raises(ValueError, match="nonnegative whole"):
        prepare_fold(panel, 1)
    assert VALIDATION_FOLDS[-1].validation.end.isoformat() == "2024-12-02"
