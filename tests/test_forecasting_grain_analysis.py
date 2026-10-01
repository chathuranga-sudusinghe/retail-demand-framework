"""Historical candidate-grain summaries; no forecasting methodology changes."""
import numpy as np
import pandas as pd

from src.analysis.forecasting_grain_analysis import (
    check_source_constraints, profile_candidate_units, promotion_consistency_check,
)


def test_candidate_grains_preserve_totals_and_week_alignment(panel):
    original = panel.copy(deep=True)
    summary, views = profile_candidate_units(panel)
    assert summary.analytical_unit.tolist() == ["sku_day", "sku_warehouse_day", "sku_week"]
    assert summary.n_series.tolist() == [2, 4, 2]
    assert summary.n_rows.tolist() == [120, 240, 18]
    assert summary.median_temporal_completeness.eq(1).all()
    assert summary.median_mean_demand.iloc[:2].tolist() == [59, 29.5]
    assert np.allclose(summary.median_lag1_autocorrelation.iloc[:2], 1)
    for view in views.values():
        assert view.demand.sum() == 7080
    assert views["sku_week"].period.dt.dayofweek.eq(0).all()
    assert views["sku_week"].iloc[0].demand == 42
    pd.testing.assert_frame_equal(panel, original)


def test_promotion_conflicts_and_source_constraints(panel):
    assert promotion_consistency_check(panel).conflict_share.iloc[0] == 0
    changed = panel.copy(deep=True)
    changed.loc[0, "Promotion_Flag"] = 1
    result = promotion_consistency_check(changed).iloc[0]
    assert result.sku_day_groups == 120
    assert result.groups_with_conflicting_promotion_flag == 1
    assert result.conflict_share == 1 / 120
    constraints = check_source_constraints(panel).set_index("check").value
    assert constraints["row_count"] == 240
    assert constraints["stockout_flag_positive_rows"] == 0
    assert constraints["Demand_Forecast_present"]


def test_source_forecast_does_not_change_candidate_analysis(panel):
    expected, _ = profile_candidate_units(panel)
    changed = panel.copy(deep=True)
    changed["Demand_Forecast"] = 999999
    actual, _ = profile_candidate_units(changed)
    pd.testing.assert_frame_equal(expected, actual)
