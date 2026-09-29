"""Synthetic Issue #62 contract tests; retained target/fold boundary coverage."""
from datetime import date

import numpy as np
import pandas as pd
import pytest

from src.forecasting.features import (
    CATEGORICAL_FEATURE_COLUMNS, CONCEPTUAL_FEATURE_COLUMNS, FEATURE_COLUMNS,
    build_features, build_origin_features, feature_eligibility, prepare_demand,
)
from src.forecasting.targets import FORECAST_HORIZONS, TARGET_COLUMNS, build_horizon_targets
from src.forecasting.validation import FINAL_HOLDOUT, VALIDATION_FOLDS, split_fold


def make_panel(periods: int = 40) -> pd.DataFrame:
    """Return two deliberately different complete daily demand series."""
    rows = []
    for offset, current_date in enumerate(pd.date_range("2024-01-01", periods=periods)):
        rows.extend(
            (
                {
                    "Date": current_date.strftime("%Y-%m-%d"),
                    "SKU_ID": "A",
                    "Warehouse_ID": "W1",
                    "Units_Sold": offset + 1,
                    "Demand_Forecast": -999,
                    "Promotion_Flag": offset % 2,
                    "Inventory_Level": 500,
                },
                {
                    "Date": current_date.strftime("%Y-%m-%d"),
                    "SKU_ID": "B",
                    "Warehouse_ID": "W2",
                    "Units_Sold": 1001 + offset,
                    "Demand_Forecast": 999_999,
                    "Promotion_Flag": (offset + 1) % 2,
                    "Inventory_Level": 5,
                },
            )
        )
    return pd.DataFrame(rows)


def series_rows(features: pd.DataFrame, sku: str, warehouse: str) -> pd.DataFrame:
    return features.loc[
        features.SKU_ID.eq(sku) & features.Warehouse_ID.eq(warehouse)
    ].reset_index(drop=True)


# Literal expectations are independent of the implementation catalogue.
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
EXCLUDED_RAW = (
    "Supplier_ID", "Region", "Inventory_Level", "Supplier_Lead_Time_Days",
    "Reorder_Point", "Order_Quantity", "Unit_Cost", "Unit_Price",
    "Promotion_Flag", "Stockout_Flag", "Demand_Forecast",
)


def make_crossed_panel(periods=40):
    rows = []
    for sku, warehouse, base, slope in (
        ("A", "W1", 1, 1), ("A", "W2", 100, 2),
        ("B", "W1", 1000, 3), ("B", "W2", 10000, 4),
    ):
        for offset, day in enumerate(pd.date_range("2024-01-01", periods=periods)):
            rows.append({"Date": day, "SKU_ID": sku, "Warehouse_ID": warehouse,
                         "Units_Sold": base + offset * slope})
    return pd.DataFrame(rows)


def test_literal_frozen_membership_and_order_exclude_the_historical_catalogue():
    features = build_features(make_panel())
    assert FEATURE_COLUMNS == EXPECTED_NUMERICAL
    assert CONCEPTUAL_FEATURE_COLUMNS == EXPECTED_CONCEPTUAL
    assert CATEGORICAL_FEATURE_COLUMNS == ("SKU_ID", "Warehouse_ID")
    assert features.columns.tolist() == ["SKU_ID", "Warehouse_ID", "Date", *EXPECTED_NUMERICAL]
    assert features.loc[:, list(EXPECTED_CONCEPTUAL)].shape[1] == 14
    assert not set(features.columns).intersection({
        "day_of_week", "month", "quarter", "lag_28", "rolling_median_7",
        "rolling_median_14", "rolling_median_28", *EXCLUDED_RAW, "Units_Sold",
    })


def test_all_seven_weekday_values_and_cyclic_wraparound():
    features = series_rows(build_features(make_panel()), "A", "W1").iloc[:7]
    expected_sin = [0, 0.7818314824680298, 0.9749279121818236, 0.4338837391175582,
                    -0.4338837391175582, -0.9749279121818236, -0.7818314824680298]
    expected_cos = [1, 0.6234898018587336, -0.2225209339563144, -0.9009688679024191,
                    -0.9009688679024191, -0.2225209339563144, 0.6234898018587336]
    np.testing.assert_allclose(features.dow_sin, expected_sin, atol=1e-15)
    np.testing.assert_allclose(features.dow_cos, expected_cos, atol=1e-15)
    points = features[["dow_sin", "dow_cos"]].to_numpy()
    np.testing.assert_allclose((points ** 2).sum(axis=1), 1)
    assert np.linalg.norm(points[6] - points[0]) == pytest.approx(
        np.linalg.norm(points[1] - points[0])
    )
    assert np.linalg.norm(points[6] - points[0]) < np.linalg.norm(points[3] - points[0])


def test_origin_weekday_and_lags_use_first_target_day_not_origin():
    # Origin Jan 28 is Sunday; first target day Jan 29 is Monday.
    row = series_rows(build_origin_features(make_panel(28), origin="2024-01-28"), "A", "W1").iloc[0]
    assert row.Date == pd.Timestamp("2024-01-29")
    assert row.dow_sin == pytest.approx(0)
    assert row.dow_cos == pytest.approx(1)
    assert (row.lag_1, row.lag_7, row.lag_14) == (28, 22, 15)
    assert "lag_28" not in row.index


@pytest.mark.parametrize("lag", [1, 7, 14])
def test_retained_lags_respect_series_boundaries_and_off_by_one(lag):
    features = build_features(make_panel().sample(frac=1, random_state=35))
    first = series_rows(features, "A", "W1")
    second = series_rows(features, "B", "W2")
    assert first.loc[: lag - 1, f"lag_{lag}"].isna().all()
    assert second.loc[: lag - 1, f"lag_{lag}"].isna().all()
    assert first.loc[lag, f"lag_{lag}"] == 1
    assert second.loc[lag, f"lag_{lag}"] == 1001
    assert first.loc[28, f"lag_{lag}"] == 29 - lag


@pytest.mark.parametrize("window", [7, 14, 28])
def test_rolling_features_use_complete_past_windows_and_sample_std(window):
    features = series_rows(build_features(make_panel()), "A", "W1")
    historical = np.arange(1, window + 1, dtype=float)
    row = features.loc[window]
    assert features.loc[:window - 1, f"rolling_mean_{window}"].isna().all()
    assert features.loc[:window - 1, f"rolling_std_{window}"].isna().all()
    assert row[f"rolling_mean_{window}"] == historical.mean()
    assert row[f"rolling_std_{window}"] == pytest.approx(historical.std(ddof=1))
    assert row[f"rolling_std_{window}"] != pytest.approx(historical.std(ddof=0))
    assert row[f"rolling_mean_{window}"] != np.arange(2, window + 2).mean()


@pytest.mark.parametrize("level", [0, 5])
def test_constant_and_zero_demand_have_zero_dispersion_and_slope(level):
    panel = make_panel(28)
    panel["Units_Sold"] = level
    features = build_origin_features(panel, origin="2024-01-28")
    assert feature_eligibility(features).all()
    for window in [7, 14, 28]:
        assert features[f"rolling_mean_{window}"].eq(level).all()
        assert features[f"rolling_std_{window}"].eq(0).all()
    assert features.rolling_slope_14.eq(0).all()


@pytest.mark.parametrize("slope", [2, -3, 0])
def test_rolling_slope_14_uses_oldest_to_newest_units_per_day(slope):
    panel = make_panel()
    panel["Units_Sold"] = panel.groupby(["SKU_ID", "Warehouse_ID"]).cumcount() * slope + 200
    features = build_features(panel)
    first = series_rows(features, "A", "W1")
    assert first.loc[:13, "rolling_slope_14"].isna().all()
    np.testing.assert_allclose(first.loc[14:, "rolling_slope_14"], slope)


@pytest.mark.parametrize("periods,eligible", [(27, False), (28, True)])
def test_minimum_history_is_exactly_28_complete_days(periods, eligible):
    panel = make_panel(periods)
    origin = pd.Timestamp("2024-01-01") + pd.Timedelta(days=periods - 1)
    features = build_origin_features(panel, origin=origin)
    assert feature_eligibility(features).tolist() == [eligible, eligible]
    assert len(features) == 2


@pytest.mark.parametrize("offset", [0, 6, 20, 27])
@pytest.mark.parametrize("missing", ["date", "value"])
def test_missing_required_history_makes_only_affected_pair_ineligible(offset, missing):
    panel = make_panel(28)
    day = str((pd.Timestamp("2024-01-01") + pd.Timedelta(days=offset)).date())
    affected = panel.SKU_ID.eq("A") & panel.Date.eq(day)
    if missing == "date":
        panel = panel.loc[~affected]
    else:
        panel.loc[affected, "Units_Sold"] = np.nan
    features = build_origin_features(panel, origin="2024-01-28")
    assert feature_eligibility(features).tolist() == [False, True]
    assert pd.isna(features.iloc[0].rolling_mean_28)
    assert pd.isna(features.iloc[0].rolling_std_28)
    if offset >= 14:
        assert pd.isna(features.iloc[0].rolling_slope_14)


@pytest.mark.parametrize("lag", [1, 7, 14])
def test_missing_lag_date_does_not_substitute_an_older_row(lag):
    panel = make_panel(28)
    missing_day = str((pd.Timestamp("2024-01-29") - pd.Timedelta(days=lag)).date())
    panel = panel.loc[~(panel.SKU_ID.eq("A") & panel.Date.eq(missing_day))]
    features = build_origin_features(panel, origin="2024-01-28")
    assert pd.isna(series_rows(features, "A", "W1").iloc[0][f"lag_{lag}"])
    assert series_rows(features, "B", "W2").iloc[0][f"lag_{lag}"] == 1029 - lag


def test_old_gap_outside_required_history_does_not_disqualify_complete_window():
    panel = make_panel(60)
    panel = panel.loc[~(panel.SKU_ID.eq("A") & panel.Date.eq("2024-01-02"))]
    assert feature_eligibility(build_origin_features(panel, origin="2024-02-29")).all()
    # The existing strict target/fold preparation default is preserved.
    with pytest.raises(ValueError, match="daily without gaps"):
        prepare_demand(panel)


def test_future_demand_cannot_change_earlier_features():
    panel = make_panel()
    original = build_features(panel)
    changed = panel.copy()
    changed.loc[changed.Date.ge("2024-01-31"), "Units_Sold"] = 1_000_000
    modified = build_features(changed)
    earlier = original.Date.le(pd.Timestamp("2024-01-31"))
    pd.testing.assert_frame_equal(original.loc[earlier], modified.loc[earlier])


@pytest.mark.parametrize("future_value", [1_000_000, -999, np.nan, "unavailable"])
def test_fixed_origin_masks_all_post_origin_actuals_before_construction(future_value):
    panel = make_panel()
    original = build_features(panel, history_end="2024-01-28")
    changed = panel.copy()
    changed["Units_Sold"] = changed.Units_Sold.astype(object)
    changed.loc[changed.Date.gt("2024-01-28"), "Units_Sold"] = future_value
    pd.testing.assert_frame_equal(original, build_features(changed, history_end="2024-01-28"))
    origin = series_rows(original, "A", "W1")
    assert origin.loc[28, "lag_1"] == 28
    assert pd.isna(origin.loc[29, "lag_1"])
    assert not feature_eligibility(origin.loc[29:]).any()


def test_fixed_origin_rows_need_no_future_actuals_and_are_shared_across_horizons():
    historical = make_crossed_panel(28)
    original = historical.copy(deep=True)
    expected = build_origin_features(historical, origin="2024-01-28")
    with_future = make_crossed_panel(60)
    with_future.loc[with_future.Date.gt("2024-01-28"), "Units_Sold"] = 9_999_999
    pd.testing.assert_frame_equal(expected, build_origin_features(with_future, origin="2024-01-28"))
    assert len(expected) == 4
    assert not expected.duplicated(["SKU_ID", "Warehouse_ID"]).any()
    assert expected.Date.eq(pd.Timestamp("2024-01-29")).all()
    assert feature_eligibility(expected).all()
    vectors = {h: expected.loc[:, list(EXPECTED_CONCEPTUAL)].copy() for h in (1, 7, 14, 28)}
    for h in (7, 14, 28):
        pd.testing.assert_frame_equal(vectors[1], vectors[h])
    pd.testing.assert_frame_equal(historical, original)


@pytest.mark.parametrize("sku,warehouse", [("A", "W1"), ("A", "W2"), ("B", "W1"), ("B", "W2")])
def test_crossed_pair_histories_cannot_contaminate_other_pairs(sku, warehouse):
    panel = make_crossed_panel()
    original = build_origin_features(panel, origin="2024-02-09")
    panel.loc[panel.SKU_ID.eq(sku) & panel.Warehouse_ID.eq(warehouse), "Units_Sold"] *= 100_000
    changed = build_origin_features(panel, origin="2024-02-09")
    others = ~(original.SKU_ID.eq(sku) & original.Warehouse_ID.eq(warehouse))
    pd.testing.assert_frame_equal(original.loc[others], changed.loc[others])
    for pair, base, slope in [(("A", "W1"), 1, 1), (("A", "W2"), 100, 2),
                              (("B", "W1"), 1000, 3), (("B", "W2"), 10000, 4)]:
        row = series_rows(original, *pair).iloc[0]
        assert row.lag_1 == base + 39 * slope
        assert row.lag_7 == base + 33 * slope
        assert row.lag_14 == base + 26 * slope
        assert row.rolling_mean_28 == pytest.approx(base + 25.5 * slope)
        assert row.rolling_std_28 == pytest.approx(np.arange(28).std(ddof=1) * slope)
        assert row.rolling_slope_14 == pytest.approx(slope)


def test_native_grain_and_row_count_are_preserved_without_mutating_input():
    panel = make_panel().sample(frac=1, random_state=12).reset_index(drop=True)
    original = panel.copy(deep=True)
    features = build_features(panel)
    assert len(features) == len(panel)
    assert not features.duplicated(["SKU_ID", "Warehouse_ID", "Date"]).any()
    assert set(map(tuple, features[["SKU_ID", "Warehouse_ID", "Date"]].to_numpy())) == set(
        map(tuple, panel.assign(Date=pd.to_datetime(panel.Date))[["SKU_ID", "Warehouse_ID", "Date"]].to_numpy())
    )
    pd.testing.assert_frame_equal(panel, original)
    pd.testing.assert_frame_equal(features, build_features(panel.sort_values("Date")))


@pytest.mark.parametrize("column", EXCLUDED_RAW)
def test_every_excluded_raw_field_is_ignored_even_when_mutated(column):
    panel = make_panel()
    for name in EXCLUDED_RAW:
        panel[name] = "original metadata"
    first = build_origin_features(panel, origin="2024-01-28")
    panel[column] = "changed excluded information"
    second = build_origin_features(panel, origin="2024-01-28")
    pd.testing.assert_frame_equal(first, second)
    assert column not in first.columns


@pytest.mark.parametrize("column,value", [
    ("Units_Sold", -1), ("Units_Sold", 1.5), ("Units_Sold", np.inf),
    ("SKU_ID", " A"), ("Warehouse_ID", " "), ("Date", "2024-01-01 12:00:00"),
])
def test_invalid_historical_demand_and_keys_are_rejected(column, value):
    panel = make_panel()
    panel[column] = panel[column].astype(object)
    panel.loc[0, column] = value
    with pytest.raises(ValueError):
        build_features(panel)


def test_duplicate_keys_and_missing_schema_are_rejected():
    panel = make_panel()
    with pytest.raises(ValueError, match="Duplicate native keys"):
        build_features(pd.concat([panel, panel.iloc[[0]]]))
    with pytest.raises(ValueError, match="Missing required columns"):
        build_features(panel.drop(columns="Units_Sold"))


def test_horizon_targets_are_cumulative_observed_outcomes_not_features():
    targets = series_rows(
        build_horizon_targets(
            make_panel(), window_start="2024-01-01", window_end="2024-01-14"
        ),
        "A",
        "W1",
    )

    assert targets.loc[0, "target_1_day"] == 1
    assert targets.loc[0, "target_7_day"] == sum(range(1, 8))
    assert targets.loc[0, "target_14_day"] == sum(range(1, 15))
    assert np.isnan(targets.loc[1, "target_14_day"])
    assert not set(targets.columns).intersection(FEATURE_COLUMNS)


def test_dr005_boundaries_are_exact_and_final_evaluation_does_not_overlap_fold_4():
    expected = (
        (date(2024, 1, 1), date(2024, 3, 31), date(2024, 4, 1), date(2024, 4, 28)),
        (date(2024, 1, 1), date(2024, 6, 30), date(2024, 7, 1), date(2024, 7, 28)),
        (date(2024, 1, 1), date(2024, 9, 30), date(2024, 10, 1), date(2024, 10, 28)),
        (date(2024, 1, 1), date(2024, 11, 4), date(2024, 11, 5), date(2024, 12, 2)),
    )

    assert tuple(
        (fold.training.start, fold.training.end, fold.validation.start, fold.validation.end)
        for fold in VALIDATION_FOLDS
    ) == expected
    assert FINAL_HOLDOUT == type(FINAL_HOLDOUT)(date(2024, 12, 3), date(2024, 12, 30))
    assert VALIDATION_FOLDS[-1].validation.end < FINAL_HOLDOUT.start


@pytest.mark.parametrize("fold_number,training_days", [(1, 91), (2, 182), (3, 274), (4, 309)])
def test_fold_split_uses_inclusive_boundaries_and_never_returns_holdout(
    fold_number, training_days
):
    panel = make_panel(periods=365)
    training, validation = split_fold(panel, fold_number)
    fold = VALIDATION_FOLDS[fold_number - 1]

    assert len(training) == training_days * 2
    assert len(validation) == 28 * 2
    assert training.Date.min() == pd.Timestamp(fold.training.start)
    assert training.Date.max() == pd.Timestamp(fold.training.end)
    assert validation.Date.min() == pd.Timestamp(fold.validation.start)
    assert validation.Date.max() == pd.Timestamp(fold.validation.end)
    assert validation.Date.max() < pd.Timestamp(FINAL_HOLDOUT.start)


@pytest.mark.parametrize("window", [*(fold.validation for fold in VALIDATION_FOLDS), FINAL_HOLDOUT])
def test_all_four_targets_fit_exactly_inside_revised_evaluation_windows(window):
    # Synthetic data only; never evaluate real final-window outcomes.
    panel = make_panel(periods=365)
    targets = build_horizon_targets(panel, window_start=window.start, window_end=window.end)
    assert FORECAST_HORIZONS == (1, 7, 14, 28)
    assert TARGET_COLUMNS == tuple(f"target_{h}_day" for h in (1, 7, 14, 28))
    first = series_rows(targets, "A", "W1").set_index("Date")
    for h in FORECAST_HORIZONS:
        column = f"target_{h}_day"
        start = pd.Timestamp(window.start)
        end = start + pd.Timedelta(days=h - 1)
        actual = panel.loc[(panel.SKU_ID == "A") & panel.Date.between(str(start.date()), str(end.date())), "Units_Sold"].sum()
        assert first.loc[start, column] == actual
        assert first[column].notna().sum() == 28 - h + 1
        last = pd.Timestamp(window.end) - pd.Timedelta(days=h - 1)
        assert first.loc[last, column] == panel.loc[(panel.SKU_ID == "A") & panel.Date.between(str(last.date()), str(window.end)), "Units_Sold"].sum()
        assert first.loc[first.index > last, column].isna().all()


def test_28_day_targets_require_complete_outcomes_and_daily_series_continuity():
    panel = make_panel(periods=365)
    window = VALIDATION_FOLDS[0].validation
    panel.loc[(panel.SKU_ID == "A") & (panel.Date == "2024-04-28"), "Units_Sold"] = np.nan
    targets = build_horizon_targets(panel, window_start=window.start, window_end=window.end)
    assert pd.isna(series_rows(targets, "A", "W1").loc[91, "target_28_day"])
    assert pd.notna(series_rows(targets, "B", "W2").loc[91, "target_28_day"])
    incomplete = make_panel(periods=365)
    incomplete = incomplete.loc[~((incomplete.SKU_ID == "A") & (incomplete.Date == "2024-04-28"))]
    with pytest.raises(ValueError):
        split_fold(incomplete, 1)


@pytest.mark.parametrize("fold", VALIDATION_FOLDS)
def test_28_day_training_targets_never_cross_the_training_cutoff(fold):
    panel = make_panel(periods=365)
    targets = build_horizon_targets(panel, window_start=fold.training.start, window_end=fold.training.end)
    valid = targets.loc[targets.target_28_day.notna()]
    assert (valid.Date + pd.Timedelta(days=27)).le(pd.Timestamp(fold.training.end)).all()
    changed = panel.copy()
    changed.loc[pd.to_datetime(changed.Date).gt(pd.Timestamp(fold.training.end)), "Units_Sold"] = 999999
    pd.testing.assert_frame_equal(targets, build_horizon_targets(changed, window_start=fold.training.start, window_end=fold.training.end))
