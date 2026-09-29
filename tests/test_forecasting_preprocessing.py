"""Synthetic representation checks only; never create or fit a forecasting model."""
import numpy as np
import pandas as pd
import pytest

from src.forecasting.features import build_features, build_origin_features
from src.forecasting.preprocessing import fit_preprocessor, fit_primary_preprocessors

EXPECTED_NUMERICAL = (
    "dow_sin", "dow_cos", "lag_1", "lag_7", "lag_14",
    "rolling_mean_7", "rolling_std_7", "rolling_mean_14", "rolling_std_14",
    "rolling_mean_28", "rolling_std_28", "rolling_slope_14",
)
EXPECTED_CONCEPTUAL = (
    "SKU_ID", "Warehouse_ID", "dow_sin", "dow_cos", "lag_1", "lag_7", "lag_14",
    "rolling_mean_7", "rolling_std_7", "rolling_mean_14", "rolling_std_14",
    "rolling_mean_28", "rolling_std_28", "rolling_slope_14",
)
PRIMARY_MODELS = ["xgboost", "lightgbm", "catboost"]
MODELS = [*PRIMARY_MODELS, "ridge", "random_forest"]


def synthetic_panel(skus=2, warehouses=2, periods=40):
    rows = []
    for sku in range(skus):
        for warehouse in range(warehouses):
            for offset, day in enumerate(pd.date_range("2024-01-01", periods=periods)):
                rows.append({"Date": day, "SKU_ID": f"S{sku:02d}",
                             "Warehouse_ID": f"W{warehouse}",
                             "Units_Sold": 1 + sku * 10 + warehouse + offset * (warehouse + 1)})
    return pd.DataFrame(rows)


def training_preprocessor(model, panel=None, horizon=1):
    panel = synthetic_panel() if panel is None else panel
    features = build_features(panel)
    fitted = fit_preprocessor(features, model, training_end=panel.Date.max(), horizon=horizon)
    return fitted, features.loc[features.Date.ge(pd.Timestamp("2024-01-29"))].copy()


@pytest.mark.parametrize("model", MODELS)
def test_metadata_exposes_literal_conceptual_numerical_categorical_order(model):
    fitted, eligible = training_preprocessor(model)
    assert fitted.conceptual_feature_names == EXPECTED_CONCEPTUAL
    assert fitted.numerical_feature_names == EXPECTED_NUMERICAL
    assert fitted.categorical_feature_names == ("SKU_ID", "Warehouse_ID")
    assert fitted.category_vocabularies == {"SKU_ID": ("S00", "S01"), "Warehouse_ID": ("W0", "W1")}
    assert fitted.category_mappings == {"SKU_ID": {"S00": 0, "S01": 1}, "Warehouse_ID": {"W0": 0, "W1": 1}}
    expected = (
        "SKU_ID=S00", "SKU_ID=S01", "Warehouse_ID=W0", "Warehouse_ID=W1", *EXPECTED_NUMERICAL,
    )
    assert fitted.physical_feature_names == expected
    assert fitted.physical_feature_count == 16
    matrix = fitted.transform(eligible)
    assert tuple(matrix.columns) == expected
    assert fitted.training_row_count == 48
    pd.testing.assert_index_equal(matrix.index, eligible.index)
    assert "Date" not in matrix.columns


@pytest.mark.parametrize("model", MODELS)
def test_full_50_sku_5_warehouse_training_coverage_gives_67_columns(model):
    fitted, eligible = training_preprocessor(model, synthetic_panel(50, 5, 30))
    matrix = fitted.transform(eligible)
    assert len(fitted.category_vocabularies["SKU_ID"]) == 50
    assert len(fitted.category_vocabularies["Warehouse_ID"]) == 5
    assert matrix.shape == (500, 67)
    expected = (
        *(f"SKU_ID=S{i:02d}" for i in range(50)),
        *(f"Warehouse_ID=W{i}" for i in range(5)), *EXPECTED_NUMERICAL,
    )
    assert tuple(matrix.columns) == expected
    indicators = matrix.iloc[:, :55]
    assert np.isin(indicators.to_numpy(), [0, 1]).all()
    assert indicators.iloc[:, :50].sum(axis=1).eq(1).all()
    assert indicators.iloc[:, 50:].sum(axis=1).eq(1).all()


def test_ridge_scales_only_numerical_columns_using_training_statistics():
    fitted, eligible = training_preprocessor("ridge")
    matrix = fitted.transform(eligible)
    raw = eligible.loc[:, list(EXPECTED_NUMERICAL)].to_numpy()
    means = raw.mean(axis=0)
    std = raw.std(axis=0, ddof=0)
    np.testing.assert_allclose(fitted.numerical_means, means)
    np.testing.assert_allclose(fitted.numerical_scales, np.where(std == 0, 1, std))
    np.testing.assert_allclose(matrix.loc[:, list(EXPECTED_NUMERICAL)], (raw - means) / np.where(std == 0, 1, std))
    indicators = matrix.iloc[:, :4]
    assert np.isin(indicators.to_numpy(), [0, 1]).all()
    assert indicators.iloc[:, :2].sum(axis=1).eq(1).all()
    assert indicators.iloc[:, 2:].sum(axis=1).eq(1).all()
    # Held-out synthetic inputs can have new values, but must use the frozen stats.
    held = eligible.iloc[[0]].copy()
    held.loc[:, "lag_1"] = 100_000
    transformed = fitted.transform(held)
    lag_index = EXPECTED_NUMERICAL.index("lag_1")
    assert transformed.lag_1.iloc[0] == pytest.approx((100_000 - means[lag_index]) / std[lag_index])
    np.testing.assert_array_equal(fitted.numerical_means, means)


def test_ridge_constant_training_numerical_columns_use_unit_scale_and_keep_identity_one():
    panel = synthetic_panel(1, 1, 30)
    panel["Units_Sold"] = 0
    fitted, eligible = training_preprocessor("ridge", panel)
    matrix = fitted.transform(eligible)
    assert tuple(matrix.columns[:2]) == ("SKU_ID=S00", "Warehouse_ID=W0")
    assert matrix.iloc[:, :2].eq(1).all().all()  # No dropped reference level or scaling.
    assert matrix.iloc[:, 4:].eq(0).all().all()
    assert fitted.numerical_scales[2:] == (1.0,) * 10


@pytest.mark.parametrize("model", [*PRIMARY_MODELS, "random_forest"])
def test_unscaled_models_preserve_all_numerical_information(model):
    fitted, eligible = training_preprocessor(model)
    matrix = fitted.transform(eligible)
    pd.testing.assert_frame_equal(matrix.loc[:, list(EXPECTED_NUMERICAL)], eligible.loc[:, list(EXPECTED_NUMERICAL)])
    assert fitted.numerical_means == ()
    assert fitted.numerical_scales == ()


def test_lightgbm_primary_path_uses_numeric_full_one_hot_without_mutating_inputs():
    fitted, eligible = training_preprocessor("lightgbm")
    original = eligible.copy(deep=True)
    matrix = fitted.transform(eligible)
    assert "SKU_ID" not in matrix.columns
    assert "Warehouse_ID" not in matrix.columns
    assert all(pd.api.types.is_float_dtype(dtype) for dtype in matrix.dtypes)
    for column in ("SKU_ID", "Warehouse_ID"):
        for category in fitted.category_vocabularies[column]:
            np.testing.assert_array_equal(
                matrix[f"{column}={category}"], eligible[column].eq(category).astype(float),
            )
    pd.testing.assert_frame_equal(eligible, original)


@pytest.mark.parametrize("model", MODELS)
def test_row_shuffling_does_not_change_category_mappings_or_physical_order(model):
    panel = synthetic_panel()
    features = build_features(panel)
    original = fit_preprocessor(features, model, training_end="2024-02-09", horizon=1)
    shuffled = fit_preprocessor(features.sample(frac=1, random_state=62), model, training_end="2024-02-09", horizon=1)
    assert shuffled.category_mappings == original.category_mappings
    assert shuffled.physical_feature_names == original.physical_feature_names
    origin = build_origin_features(panel, origin="2024-02-09")
    pd.testing.assert_frame_equal(shuffled.transform(origin), original.transform(origin), atol=1e-12, rtol=1e-12)


@pytest.mark.parametrize("model", MODELS)
def test_fit_ignores_categories_with_insufficient_training_history(model):
    panel = synthetic_panel(1, 1)
    recent = synthetic_panel(1, 1, 10)
    recent["Date"] = recent.Date + pd.Timedelta(days=30)
    recent["SKU_ID"] = "NEW_SKU"
    recent["Warehouse_ID"] = "NEW_WAREHOUSE"
    features = build_features(pd.concat([panel, recent], ignore_index=True))
    fitted = fit_preprocessor(features, model, training_end="2024-02-09", horizon=1)
    assert fitted.category_vocabularies == {"SKU_ID": ("S00",), "Warehouse_ID": ("W0",)}
    assert fitted.training_row_count == 12
    assert fitted.physical_feature_count == 14  # Smaller fold coverage, no future padding.


@pytest.mark.parametrize("model", MODELS)
def test_fit_rejects_future_rows_instead_of_learning_their_categories_or_scaling(model):
    features = build_features(synthetic_panel())
    with pytest.raises(ValueError, match="after training_end"):
        fit_preprocessor(features, model, training_end="2024-01-31", horizon=1)
    training = features.loc[features.Date.le(pd.Timestamp("2024-01-31"))]
    fitted = fit_preprocessor(training, model, training_end="2024-01-31", horizon=1)
    assert fitted.training_row_count == 12


@pytest.mark.parametrize("model", MODELS)
def test_horizon_end_boundary_is_enforced_before_learning_categories(model):
    panel = synthetic_panel(1, 1)
    late = synthetic_panel(1, 1, 31)
    late["Date"] = late.Date + pd.Timedelta(days=9)
    late["SKU_ID"] = "LATE"
    late["Warehouse_ID"] = "OTHER"
    features = build_features(pd.concat([panel, late], ignore_index=True))
    fitted = fit_preprocessor(features, model, training_end="2024-02-09", horizon=7)
    assert fitted.training_row_count == 6  # Jan 29..Feb 3 only; every label ends by Feb 9.
    assert fitted.category_vocabularies == {"SKU_ID": ("S00",), "Warehouse_ID": ("W0",)}


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("column", ["SKU_ID", "Warehouse_ID"])
def test_unseen_prediction_identity_is_rejected_without_silent_encoding(model, column):
    fitted, eligible = training_preprocessor(model)
    held = eligible.iloc[[0]].copy()
    held[column] = "UNSEEN"
    before = fitted.category_mappings
    with pytest.raises(ValueError, match=f"Unknown {column}"):
        fitted.transform(held)
    assert fitted.category_mappings == before


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("column", ["SKU_ID", "Warehouse_ID"])
def test_integer_identity_codes_cannot_enter_as_continuous_predictors(model, column):
    features = build_features(synthetic_panel())
    features[column] = 123
    with pytest.raises(ValueError, match="text categories"):
        fit_preprocessor(features, model, training_end="2024-02-09", horizon=1)


@pytest.mark.parametrize("model", MODELS)
def test_no_preprocessing_imputation_or_ineligible_matrix_rows(model):
    fitted, eligible = training_preprocessor(model)
    partial = eligible.iloc[[0]].copy()
    partial.loc[:, "rolling_mean_28"] = np.nan
    with pytest.raises(ValueError, match="feature-ineligible"):
        fitted.transform(partial)
    with pytest.raises(ValueError, match="No eligible training"):
        fit_preprocessor(partial, model, training_end="2024-02-09", horizon=1)


@pytest.mark.parametrize("model", MODELS)
def test_preprocessing_excludes_raw_fields_labels_and_alignment_date(model):
    fitted, eligible = training_preprocessor(model)
    before = fitted.transform(eligible)
    extra = eligible.copy()
    for column in (
        "Units_Sold", "Supplier_ID", "Region", "Inventory_Level", "Supplier_Lead_Time_Days",
        "Reorder_Point", "Order_Quantity", "Unit_Cost", "Unit_Price", "Promotion_Flag",
        "Stockout_Flag", "Demand_Forecast", "target_28_day",
    ):
        extra[column] = 999_999
    pd.testing.assert_frame_equal(before, fitted.transform(extra))


@pytest.mark.parametrize("model", MODELS)
def test_physical_representations_retain_the_same_conceptual_identity_and_values(model):
    panel = synthetic_panel()
    fitted, _ = training_preprocessor(model, panel)
    origin = build_origin_features(panel, origin="2024-02-09")
    matrix = fitted.transform(origin)
    for column in ["SKU_ID", "Warehouse_ID"]:
        for category in fitted.category_vocabularies[column]:
            assert matrix[f"{column}={category}"].tolist() == origin[column].eq(category).astype(float).tolist()
    numeric = matrix.loc[:, list(EXPECTED_NUMERICAL)].to_numpy()
    if model == "ridge":
        numeric = numeric * np.asarray(fitted.numerical_scales) + np.asarray(fitted.numerical_means)
    np.testing.assert_allclose(numeric, origin.loc[:, list(EXPECTED_NUMERICAL)], atol=1e-12)


@pytest.mark.parametrize("horizon", [1, 7, 14, 28])
def test_primary_models_share_one_fitted_vocabulary_and_identical_matrices(horizon):
    panel = synthetic_panel(periods=80)
    features = build_features(panel)
    before = features.copy(deep=True)
    fitted = fit_primary_preprocessors(features, training_end=panel.Date.max(), horizon=horizon)
    assert tuple(fitted) == tuple(PRIMARY_MODELS)
    expected = fitted["xgboost"]
    origin = build_origin_features(panel, origin=panel.Date.max())
    matrices = {model: state.transform(origin) for model, state in fitted.items()}
    for model, state in fitted.items():
        assert state.model == model
        assert state.vocabularies is expected.vocabularies
        assert state.category_vocabularies == {
            "SKU_ID": ("S00", "S01"), "Warehouse_ID": ("W0", "W1"),
        }
        assert state.category_mappings == expected.category_mappings
        assert state.physical_feature_names == expected.physical_feature_names
        assert state.training_row_count == 4 * (80 - 28 - horizon + 1)
        assert state.numerical_means == state.numerical_scales == ()
        pd.testing.assert_frame_equal(matrices[model], matrices["xgboost"])
        pd.testing.assert_frame_equal(
            matrices[model].loc[:, list(EXPECTED_NUMERICAL)],
            origin.loc[:, list(EXPECTED_NUMERICAL)],
        )
        independent = fit_preprocessor(
            features, model, training_end=panel.Date.max(), horizon=horizon,
        )
        pd.testing.assert_frame_equal(independent.transform(origin), matrices[model])
    pd.testing.assert_frame_equal(features, before)



def test_shared_primary_full_category_coverage_produces_identical_67_column_matrices():
    panel = synthetic_panel(50, 5, 30)
    features = build_features(panel)
    fitted = fit_primary_preprocessors(features, training_end=panel.Date.max(), horizon=1)
    eligible = features.loc[features.Date.ge(pd.Timestamp("2024-01-29"))]
    expected_columns = (
        *(f"SKU_ID=S{i:02d}" for i in range(50)),
        *(f"Warehouse_ID=W{i}" for i in range(5)), *EXPECTED_NUMERICAL,
    )
    reference = fitted["xgboost"].transform(eligible)
    for state in fitted.values():
        matrix = state.transform(eligible)
        assert matrix.shape == (500, 67)
        assert tuple(matrix.columns) == expected_columns
        assert len(state.category_vocabularies["SKU_ID"]) == 50
        assert len(state.category_vocabularies["Warehouse_ID"]) == 5
        pd.testing.assert_frame_equal(matrix, reference)
        pd.testing.assert_frame_equal(
            matrix.loc[:, list(EXPECTED_NUMERICAL)],
            eligible.loc[:, list(EXPECTED_NUMERICAL)],
        )

def test_shared_primary_fit_excludes_incomplete_and_outcome_crossing_categories():
    panel = synthetic_panel(1, 1)
    late = synthetic_panel(1, 1, 31)
    late["Date"] = late.Date + pd.Timedelta(days=9)
    late["SKU_ID"] = "LATE"
    late["Warehouse_ID"] = "OTHER"
    features = build_features(pd.concat([panel, late], ignore_index=True))
    states = fit_primary_preprocessors(features, training_end="2024-02-09", horizon=7)
    for state in states.values():
        assert state.training_row_count == 6
        assert state.category_vocabularies == {"SKU_ID": ("S00",), "Warehouse_ID": ("W0",)}
        assert state.physical_feature_count == 14
        complete_but_late = features.loc[
            features.SKU_ID.eq("LATE") & features.Date.eq(pd.Timestamp("2024-02-09"))
        ]
        with pytest.raises(ValueError, match="Unknown SKU_ID"):
            state.transform(complete_but_late)


@pytest.mark.parametrize("model", ["native_lightgbm", "naive", "unknown", None])
def test_unapproved_representation_is_rejected(model):
    with pytest.raises(ValueError, match="model must be"):
        fit_preprocessor(build_features(synthetic_panel()), model, training_end="2024-02-09", horizon=1)
