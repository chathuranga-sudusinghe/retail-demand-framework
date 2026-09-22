"""Deterministic tests for the Issue #35 forecasting feature pipeline."""
from datetime import date

import numpy as np
import pandas as pd
import pytest

from src.forecasting.features import FEATURE_COLUMNS, build_features
from src.forecasting.targets import build_horizon_targets
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


def test_calendar_features_are_derived_from_each_rows_date():
    features = series_rows(build_features(make_panel()), "A", "W1")

    jan_1 = features.loc[features.Date.eq(pd.Timestamp("2024-01-01"))].iloc[0]
    apr_1 = build_features(
        pd.DataFrame(
            [{"Date": "2024-04-01", "SKU_ID": "A", "Warehouse_ID": "W1", "Units_Sold": 1}]
        )
    ).iloc[0]

    assert (jan_1.day_of_week, jan_1.month, jan_1.quarter) == (0, 1, 1)
    assert (apr_1.day_of_week, apr_1.month, apr_1.quarter) == (0, 4, 2)


def test_lag_1_is_previous_observation_within_each_series():
    features = build_features(make_panel().sample(frac=1, random_state=35))
    first = series_rows(features, "A", "W1")
    second = series_rows(features, "B", "W2")

    assert np.isnan(first.loc[0, "lag_1"])
    assert first.loc[1, "lag_1"] == 1
    assert second.loc[1, "lag_1"] == 1001


@pytest.mark.parametrize("lag", [7, 14, 28])
def test_candidate_lags_respect_series_boundaries(lag):
    features = build_features(make_panel())
    first = series_rows(features, "A", "W1")
    second = series_rows(features, "B", "W2")

    assert first.loc[: lag - 1, f"lag_{lag}"].isna().all()
    assert second.loc[: lag - 1, f"lag_{lag}"].isna().all()
    assert first.loc[lag, f"lag_{lag}"] == 1
    assert second.loc[lag, f"lag_{lag}"] == 1001


@pytest.mark.parametrize("window", [7, 14])
def test_rolling_features_exclude_current_target(window):
    features = series_rows(build_features(make_panel()), "A", "W1")
    historical = pd.Series(range(1, window + 1), dtype=float)
    row = features.loc[window]

    assert row[f"rolling_mean_{window}"] == historical.mean()
    assert row[f"rolling_median_{window}"] == historical.median()
    assert row[f"rolling_std_{window}"] == pytest.approx(historical.std(ddof=1))
    assert row[f"rolling_mean_{window}"] != pd.Series(
        range(1, window + 2), dtype=float
    ).tail(window).mean()


def test_future_demand_cannot_change_earlier_features():
    panel = make_panel()
    original = build_features(panel)
    changed = panel.copy()
    changed.loc[changed.Date.eq("2024-01-31"), "Units_Sold"] = 1_000_000
    modified = build_features(changed)

    earlier = original.Date.lt(pd.Timestamp("2024-01-31"))
    pd.testing.assert_frame_equal(original.loc[earlier], modified.loc[earlier])


def test_fixed_history_cutoff_masks_later_actuals():
    features = series_rows(
        build_features(make_panel(), history_end="2024-01-20"), "A", "W1"
    )

    assert features.loc[20, "lag_1"] == 20
    assert np.isnan(features.loc[21, "lag_1"])
    assert np.isnan(features.loc[27, "rolling_mean_7"])


def test_one_series_cannot_influence_another():
    panel = make_panel()
    original = series_rows(build_features(panel), "A", "W1")
    panel.loc[panel.SKU_ID.eq("B"), "Units_Sold"] *= 100_000
    unchanged = series_rows(build_features(panel), "A", "W1")

    pd.testing.assert_frame_equal(original, unchanged)


def test_early_rows_retain_missing_history_values():
    features = series_rows(build_features(make_panel()), "A", "W1")

    assert features.loc[:27, "lag_28"].isna().all()
    assert features.loc[:6, ["rolling_mean_7", "rolling_median_7", "rolling_std_7"]].isna().all().all()
    assert features.loc[:13, ["rolling_mean_14", "rolling_median_14", "rolling_std_14"]].isna().all().all()


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


def test_feature_contract_excludes_source_and_unapproved_columns():
    panel = make_panel()
    first = build_features(panel)
    panel["Demand_Forecast"] = np.arange(len(panel)) * 1_000_000
    second = build_features(panel)

    assert first.columns.tolist() == ["SKU_ID", "Warehouse_ID", "Date", *FEATURE_COLUMNS]
    assert "Demand_Forecast" not in first.columns
    assert "Promotion_Flag" not in first.columns
    assert "Inventory_Level" not in first.columns
    pd.testing.assert_frame_equal(first, second)


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


def test_dr005_boundaries_are_exact_and_holdout_does_not_overlap_fold_4():
    expected = (
        (date(2024, 1, 1), date(2024, 3, 31), date(2024, 4, 1), date(2024, 4, 14)),
        (date(2024, 1, 1), date(2024, 6, 30), date(2024, 7, 1), date(2024, 7, 14)),
        (date(2024, 1, 1), date(2024, 9, 30), date(2024, 10, 1), date(2024, 10, 14)),
        (date(2024, 1, 1), date(2024, 12, 2), date(2024, 12, 3), date(2024, 12, 16)),
    )

    assert tuple(
        (fold.training.start, fold.training.end, fold.validation.start, fold.validation.end)
        for fold in VALIDATION_FOLDS
    ) == expected
    assert FINAL_HOLDOUT == type(FINAL_HOLDOUT)(date(2024, 12, 17), date(2024, 12, 30))
    assert VALIDATION_FOLDS[-1].validation.end < FINAL_HOLDOUT.start


@pytest.mark.parametrize("fold_number,training_days", [(1, 91), (2, 182), (3, 274), (4, 337)])
def test_fold_split_uses_inclusive_boundaries_and_never_returns_holdout(
    fold_number, training_days
):
    panel = make_panel(periods=365)
    training, validation = split_fold(panel, fold_number)
    fold = VALIDATION_FOLDS[fold_number - 1]

    assert len(training) == training_days * 2
    assert len(validation) == 14 * 2
    assert training.Date.min() == pd.Timestamp(fold.training.start)
    assert training.Date.max() == pd.Timestamp(fold.training.end)
    assert validation.Date.min() == pd.Timestamp(fold.validation.start)
    assert validation.Date.max() == pd.Timestamp(fold.validation.end)
    assert validation.Date.max() < pd.Timestamp(FINAL_HOLDOUT.start)
