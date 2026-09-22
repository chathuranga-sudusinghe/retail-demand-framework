"""Small synthetic panels; no project dataset is needed or embedded."""
import numpy as np
import pandas as pd
import pytest

from src.data.demand_eda import analyze_demand, lag_correlation, require_valid, save_tables, validate_data


@pytest.fixture
def panel():
    rows = []
    for day, date in enumerate(pd.date_range("2024-01-01", periods=60)):
        for sku in ["A", "B"]:
            for wh in ["W1", "W2"]:
                rows.append({"Date": date.strftime("%Y-%m-%d"), "SKU_ID": sku, "Warehouse_ID": wh,
                             "Supplier_ID": "S1", "Region": "R1", "Units_Sold": day,
                             "Inventory_Level": 100, "Supplier_Lead_Time_Days": 2,
                             "Reorder_Point": 20, "Order_Quantity": 0, "Unit_Cost": 1.5,
                             "Unit_Price": 2.5, "Promotion_Flag": day % 2,
                             "Stockout_Flag": 0, "Demand_Forecast": 9.2})
    return pd.DataFrame(rows)


def test_valid_panel_preserves_rows_values_and_source(panel):
    original = panel.copy(deep=True)
    cleaned, audit = validate_data(panel.sample(frac=1, random_state=5))
    require_valid(audit)
    assert len(cleaned) == len(panel)
    assert cleaned.Units_Sold.sum() == panel.Units_Sold.sum()
    assert audit["coverage"].completeness.eq(1).all()
    pd.testing.assert_frame_equal(panel, original)


@pytest.mark.parametrize("column,value,check", [
    ("Date", "2024-02-30", "invalid_dates"),
    ("Date", "2024-01-01 12:00:00", "invalid_dates"),
    ("Units_Sold", -1, "Units_Sold_negative"),
    ("Units_Sold", 1.5, "Units_Sold_fractional"),
    ("Units_Sold", np.inf, "Units_Sold_infinite"),
    ("Units_Sold", "broken", "Units_Sold_invalid_numeric"),
    ("Units_Sold", None, "missing_cells"),
    ("Unit_Cost", -1, "Unit_Cost_negative"),
    ("Promotion_Flag", 2, "Promotion_Flag_not_binary"),
    ("SKU_ID", " ", "blank_cells"),
    ("SKU_ID", " A", "SKU_ID_surrounding_whitespace"),
])
def test_invalid_values_are_reported_not_repaired(panel, column, value, check):
    panel[column] = panel[column].astype(object)
    panel.loc[0, column] = value
    _, audit = validate_data(panel)
    assert audit["validation"].set_index("check").loc[check, "affected"] > 0
    with pytest.raises(ValueError, match="Data-quality"):
        require_valid(audit)


@pytest.mark.parametrize("conflicting", [False, True])
def test_duplicate_keys_block_aggregation(panel, conflicting):
    extra = panel.iloc[[0]].copy()
    if conflicting:
        extra["Units_Sold"] = 99
    duplicated = pd.concat([panel, extra], ignore_index=True)
    cleaned, audit = validate_data(duplicated)
    assert len(cleaned) == len(duplicated)
    assert audit["validation"].set_index("check").loc["duplicate_native_key_rows", "affected"] == 2
    with pytest.raises(ValueError, match="duplicate_native_key"):
        analyze_demand(duplicated)


@pytest.mark.parametrize("removal", ["interior", "edge", "whole_pair"])
def test_temporal_coverage_uses_global_span(panel, removal):
    if removal == "interior":
        panel = panel.drop(20)
    elif removal == "edge":
        panel = panel.drop(0)
    else:
        panel = panel.loc[~(panel.SKU_ID.eq("A") & panel.Warehouse_ID.eq("W1"))]
    _, audit = validate_data(panel)
    assert audit["coverage"].missing_days.sum() == (60 if removal == "whole_pair" else 1)
    with pytest.raises(ValueError, match="missing_series_days"):
        require_valid(audit)


def test_empty_and_missing_schema(panel):
    with pytest.raises(ValueError, match="empty"):
        validate_data(panel.iloc[:0])
    with pytest.raises(ValueError, match="Missing required"):
        validate_data(panel.drop(columns="Units_Sold"))


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
    tables = analyze_demand(panel.loc[panel.Date.le("2024-02-28")])
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
