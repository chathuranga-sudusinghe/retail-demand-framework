"""Synthetic full-source panels only; never load project data."""

import numpy as np
import pandas as pd
import pytest

from src.data import data_cleaning as cleaning


@pytest.fixture
def panel():
    return pd.DataFrame([{**dict.fromkeys(cleaning.COLUMNS, 0), "Date": date.strftime("%Y-%m-%d"),
                          "SKU_ID": sku, "Warehouse_ID": "W1", "Supplier_ID": "S1", "Region": "R1",
                          "Units_Sold": day, "Inventory_Level": 100, "Supplier_Lead_Time_Days": 2,
                          "Reorder_Point": 20, "Unit_Cost": 1.5, "Unit_Price": 2.5, "Demand_Forecast": 9.2}
                         for day, date in enumerate(pd.date_range("2024-01-01", periods=4))
                         for sku in ("001", "002")])


def test_valid_full_schema_native_grain_and_deterministic_sort(panel):
    original = panel.copy(deep=True)
    first, audit = cleaning.build_validated_dataset(panel.sample(frac=1, random_state=1))
    second, _ = cleaning.build_validated_dataset(panel.sample(frac=1, random_state=2))
    pd.testing.assert_frame_equal(first, second)
    pd.testing.assert_frame_equal(panel, original)
    assert len(first) == len(panel) and list(first.columns) == cleaning.COLUMNS
    assert first.Stockout_Flag.eq(0).all() and audit["status"] == "passed"
    assert not first.duplicated(cleaning.KEY).any()


@pytest.mark.parametrize("column,value", [("Date", "2024-02-30"), ("Date", "2024-01-01 12:00:00"),
    ("Units_Sold", "invalid"), ("Units_Sold", -1), ("Units_Sold", 1.5), ("Units_Sold", np.inf),
    ("Unit_Price", -1), ("Promotion_Flag", 2), ("SKU_ID", None), ("Warehouse_ID", None),
    ("Date", None), ("Date", 0), ("SKU_ID", 1), ("Supplier_ID", " "), ("SKU_ID", " 001"), ("Units_Sold", None)])
def test_blocking_bad_records_never_accept_or_mutate(panel, column, value):
    panel[column] = panel[column].astype(object)
    panel.loc[0, column] = value
    original = panel.copy(deep=True)
    with pytest.raises(ValueError):
        cleaning.build_validated_dataset(panel)
    pd.testing.assert_frame_equal(panel, original)


def test_missing_or_duplicate_schema_fails(panel):
    with pytest.raises(ValueError, match="schema"):
        cleaning.build_validated_dataset(panel.drop(columns="Units_Sold"))
    duplicate = pd.concat([panel, panel[["Date"]]], axis=1)
    with pytest.raises(ValueError, match="unique"):
        cleaning.build_validated_dataset(duplicate)


@pytest.mark.parametrize("conflict", [False, True])
def test_exact_duplicate_and_conflicting_key_are_distinct_and_not_deleted(panel, conflict):
    extra = panel.iloc[[0]].copy()
    if conflict:
        extra["Inventory_Level"] = 999
    raw = pd.concat([panel, extra], ignore_index=True)
    parsed = cleaning.parse_datatypes(raw)
    audit = cleaning.build_validation_audit(raw, parsed)
    assert len(parsed) == len(raw)
    assert audit["checks"]["duplicate_native_key_rows"] == 2
    assert audit["checks"]["exact_duplicate_rows"] == (0 if conflict else 2)
    assert audit["checks"]["conflicting_native_key_rows"] == (2 if conflict else 0)
    with pytest.raises(ValueError):
        cleaning.build_validated_dataset(raw)


def test_missing_values_preserved_for_diagnostics_not_imputed(panel):
    panel.loc[0, "Units_Sold"] = np.nan
    parsed = cleaning.parse_datatypes(panel)
    assert pd.isna(parsed.loc[0, "Units_Sold"]) and len(parsed) == len(panel)
    assert cleaning.build_validation_audit(panel, parsed)["checks"]["missing_cells"] == 1
    with pytest.raises(ValueError):
        cleaning.build_validated_dataset(panel)


def test_outlier_is_not_clipped_and_dates_not_filled(panel):
    panel.loc[0, "Units_Sold"] = 10_000_000
    validated, _ = cleaning.build_validated_dataset(panel)
    assert validated.Units_Sold.max() == 10_000_000
    gapped = panel.drop(index=2)
    parsed = cleaning.parse_datatypes(gapped)
    assert len(parsed) == len(gapped)
    assert cleaning.build_validation_audit(gapped.reset_index(drop=True), parsed.reset_index(drop=True))["checks"]["missing_series_days_in_observed_span"] == 1
    with pytest.raises(ValueError):
        cleaning.build_validated_dataset(gapped)


def test_scoped_loader_preserves_ids_and_does_not_validate_excluded_quantities(panel, tmp_path):
    path = tmp_path / "synthetic.csv"
    panel["Units_Sold"] = panel.Units_Sold.astype(object)
    panel.loc[panel.Date.eq("2024-01-04"), "Units_Sold"] = "excluded-invalid"
    panel.to_csv(path, index=False)
    scoped = cleaning.load_raw_source(path, start="2024-01-01", end="2024-01-03")
    validated, _ = cleaning.build_validated_dataset(scoped)
    assert len(validated) == 6 and set(validated.SKU_ID) == {"001", "002"}


@pytest.mark.parametrize("removal", ["edge", "whole_pair"])
def test_coverage_defects_are_owned_by_shared_cleaner(panel, removal):
    second_warehouse = panel.copy(deep=True)
    second_warehouse["Warehouse_ID"] = "W2"
    source = pd.concat([panel, second_warehouse], ignore_index=True)
    if removal == "edge":
        source = source.drop(index=0)
    else:
        source = source.loc[~(source.SKU_ID.eq("001") & source.Warehouse_ID.eq("W1"))]
    source = source.reset_index(drop=True)
    audit = cleaning.build_validation_audit(source, cleaning.parse_datatypes(source))
    assert audit["checks"]["missing_series_days_in_observed_span"] == (1 if removal == "edge" else 4)
    with pytest.raises(ValueError):
        cleaning.build_validated_dataset(source)


def test_quality_presentation_and_scoped_receipt_use_shared_evidence(panel, tmp_path):
    validated, audit = cleaning.build_validated_dataset(panel)
    tables = cleaning.quality_tables(validated, audit)
    assert tables["coverage"].completeness.eq(1).all()
    assert tables["validation"].affected.eq(0).all()
    assert "baseline" not in tables  # shared validation has no historical expectations
    path = tmp_path / "not-opened.csv"
    receipt = cleaning.scoped_source_receipt(panel, path).set_index("item").value
    assert receipt["scoped_fingerprint"] == cleaning.frame_fingerprint(panel)
    assert receipt["scoped_rows"] == str(len(panel))
    assert not path.exists()
    failed = {**audit, "status": "failed"}
    with pytest.raises(ValueError):
        cleaning.quality_tables(validated, failed)


def test_fingerprint_is_deterministic_and_sensitive_to_observations(panel):
    original = panel.copy(deep=True)
    assert cleaning.frame_fingerprint(panel) == cleaning.frame_fingerprint(panel.copy(deep=True))
    changed = panel.copy(deep=True)
    changed.loc[0, "Units_Sold"] += 1
    assert cleaning.frame_fingerprint(changed) != cleaning.frame_fingerprint(panel)
    pd.testing.assert_frame_equal(panel, original)
