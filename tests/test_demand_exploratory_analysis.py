"""Small synthetic panels; no project dataset is needed or embedded."""
import numpy as np
import pandas as pd
import pytest

from src.analysis.demand_exploratory_analysis import (
    analyze_demand, historical_baseline_comparison, lag_correlation, quality_tables, save_tables,
)


def test_analysis_preserves_validated_input(panel):
    original = panel.copy(deep=True)
    analyze_demand(panel)
    pd.testing.assert_frame_equal(panel, original)


def test_totals_month_lengths_rolling_and_promotion(panel):
    tables = analyze_demand(panel)
    daily, monthly = tables["daily"], tables["monthly"]
    assert daily.total.sum() == monthly.total.sum() == tables["promotion"].total.sum() == 7080
    assert monthly.days.tolist() == [31, 29]
    assert monthly["mean"].tolist() == [15, 45]
    assert monthly.iloc[1].mean_change_pct == 200
    assert daily.rolling_mean_7.iloc[:6].isna().all()
    assert daily.rolling_mean_7.iloc[6] == 12
    assert daily.rolling_mean_14.iloc[13] == 26
    assert daily.iloc[0].change_pct != daily.iloc[0].change_pct  # undefined first change
    assert tables["promotion"].set_index("Promotion_Flag").loc[0, "rows"] == 120
    assert tables["series"].zero_share.eq(1 / 60).all()


def test_partial_month_uses_observed_denominator(panel):
    tables = analyze_demand(panel.loc[panel.Date.le(pd.Timestamp("2024-02-28"))])
    feb = tables["monthly"].iloc[1]
    assert feb.days == 28 and feb.calendar_days == 29
    assert feb["mean"] == 44.5
    assert feb.mean_daily_total == 178


def test_lag_is_within_series_and_source_forecast_unused(panel):
    tables = analyze_demand(panel.sample(frac=1, random_state=9))
    assert np.allclose(tables["lags"].correlation, 1)
    changed = panel.copy()
    changed["Demand_Forecast"] = 1000000
    other = analyze_demand(changed)
    for name in tables:
        pd.testing.assert_frame_equal(tables[name], other[name])
    assert np.isnan(lag_correlation(pd.Series([1, 1, 1, 1]), 1))
    assert np.isnan(lag_correlation(pd.Series([1, 2]), 1))


def test_all_zero_demand_is_valid_and_changes_undefined(panel):
    panel["Units_Sold"] = 0
    tables = analyze_demand(panel)
    assert tables["monthly"].mean_change_pct.isna().all()
    assert tables["lags"].correlation.isna().all()
    assert tables["series"].zero_share.eq(1).all()


def test_tables_cannot_be_written_outside_ignored_processed_path(tmp_path):
    with pytest.raises(ValueError, match="data/processed"):
        save_tables({"unsafe": pd.DataFrame({"a": [1]})}, tmp_path)
    assert not (tmp_path / "unsafe.csv").exists()


@pytest.mark.parametrize("module_name", [
    "src.analysis.demand_exploratory_analysis",
    "src.analysis.inventory_alignment_analysis",
    "src.analysis.forecasting_grain_analysis",
])
def test_analysis_cli_delegates_loading_and_validation(panel, tmp_path, monkeypatch, module_name):
    import importlib
    import sys
    from src.data import data_cleaning as cleaning

    module = importlib.import_module(module_name)
    calls = []
    def load(path, *, start, end):
        calls.append(("load", path, start, end))
        return panel
    def validate(raw):
        calls.append(("validate", len(raw)))
        return cleaning.build_validated_dataset(raw)
    monkeypatch.setattr(module, "load_raw_source", load)
    monkeypatch.setattr(module, "build_validated_dataset", validate)
    monkeypatch.setattr(module, "save_tables" if module_name.endswith("demand_exploratory_analysis") else "save_outputs", lambda *a, **kw: None)
    source = tmp_path / "never-opened.csv"
    monkeypatch.setattr(sys, "argv", [module_name, "--input", str(source),
        "--start", "2024-01-01", "--end", "2024-02-29", "--output-dir", str(tmp_path)])
    module.main()
    assert calls == [("load", source, "2024-01-01", "2024-02-29"), ("validate", len(panel))]
    assert not source.exists()


def test_historical_baseline_is_analysis_context_not_validation(panel):
    from src.data import data_cleaning as cleaning

    original = panel.copy(deep=True)
    validated, audit = cleaning.build_validated_dataset(panel)
    assert audit["status"] == "passed"
    expected = pd.DataFrame({
        "check": ["rows", "columns", "dates", "skus", "warehouses", "date_min", "date_max",
                  "suppliers", "regions", "stockout_zero_rows", "nonzero_order_rows"],
        "documented": [91250, 15, 365, 50, 5, "2024-01-01", "2024-12-30", 10, 4, 91250, 5027],
        "observed": [240, 15, 60, 2, 2, "2024-01-01", "2024-02-29", 1, 1, 240, 0],
    })
    expected["matches"] = expected.documented.eq(expected.observed)
    pd.testing.assert_frame_equal(historical_baseline_comparison(validated), expected)
    tables = quality_tables(validated, audit)
    pd.testing.assert_frame_equal(tables["baseline"], expected)
    assert tables["validation"].affected.eq(0).all()
    assert not tables["baseline"].matches.all()
    pd.testing.assert_frame_equal(panel, original)
