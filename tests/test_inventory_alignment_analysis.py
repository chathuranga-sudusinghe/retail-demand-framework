"""Descriptive inventory summaries consume shared validated synthetic data."""
import pandas as pd

from src.analysis.inventory_alignment_analysis import (
    profile_cross_warehouse_variation, profile_inventory_ranges,
    profile_native_grain, profile_warehouse_coverage,
)


def test_native_grain_and_coverage(panel):
    checks = profile_native_grain(panel).set_index("check").value
    assert checks["source_rows"] == checks["unique_date_sku_warehouse_keys"] == 240
    assert checks["duplicate_rows_at_native_key"] == 0
    assert checks["native_key_is_unique"]
    coverage = profile_warehouse_coverage(panel)
    assert coverage.warehouses_per_sku_day.tolist() == [2]
    assert coverage.sku_day_groups.tolist() == [120]
    assert coverage.share.tolist() == [1.0]


def test_inventory_variation_ranges_and_no_mutation(panel):
    frame = panel.copy(deep=True)
    frame.loc[frame.Warehouse_ID.eq("W2"), "Inventory_Level"] = 200
    original = frame.copy(deep=True)
    variation = profile_cross_warehouse_variation(frame).set_index("variable")
    assert variation.loc["Inventory_Level", "variation_share"] == 1
    assert variation.loc["Reorder_Point", "variation_share"] == 0
    ranges = profile_inventory_ranges(frame).set_index("variable")
    assert ranges.loc["Inventory_Level", ["min", "median", "mean", "max"]].tolist() == [100, 150, 150, 200]
    assert ranges.loc["Order_Quantity", "zero_share"] == 1
    pd.testing.assert_frame_equal(frame, original)
