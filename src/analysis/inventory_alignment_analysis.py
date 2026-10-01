"""Inventory-alignment profiling for COMP1884 Issue #16.

This module checks whether the forecasting analytical unit should preserve
warehouse-level granularity so that forecast outputs can align with downstream
inventory-risk and replenishment analysis.

It does NOT train forecasting models and does NOT use Stockout_Flag as a target.

Example
-------
python -m src.analysis.inventory_alignment_analysis \
    --input data/raw/supply_chain_dataset1.csv \
    --start YYYY-MM-DD --end YYYY-MM-DD \
    --output-dir data/processed/temporal_profile
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.data.data_cleaning import build_validated_dataset, load_raw_source


KEY_COLUMNS = ["Date", "SKU_ID", "Warehouse_ID"]

INVENTORY_COLUMNS = [
    "Inventory_Level",
    "Reorder_Point",
    "Supplier_Lead_Time_Days",
    "Order_Quantity",
]


def profile_native_grain(df: pd.DataFrame) -> pd.DataFrame:
    """Check whether Date + SKU + Warehouse uniquely identifies source rows."""
    duplicate_mask = df.duplicated(KEY_COLUMNS, keep=False)

    return pd.DataFrame(
        {
            "check": [
                "source_rows",
                "unique_date_sku_warehouse_keys",
                "duplicate_rows_at_native_key",
                "native_key_is_unique",
            ],
            "value": [
                int(len(df)),
                int(df[KEY_COLUMNS].drop_duplicates().shape[0]),
                int(duplicate_mask.sum()),
                bool(not duplicate_mask.any()),
            ],
            "note": [
                "Total source records",
                "Distinct Date + SKU_ID + Warehouse_ID combinations",
                "Rows participating in duplicated native keys",
                "Whether the source grain is one row per Date + SKU + Warehouse",
            ],
        }
    )


def profile_cross_warehouse_variation(df: pd.DataFrame) -> pd.DataFrame:
    """Measure whether inventory state varies across warehouses for a SKU-day."""
    grouped = df.groupby(["Date", "SKU_ID"], observed=True)

    rows: list[dict[str, object]] = []

    total_groups = grouped.ngroups

    for column in INVENTORY_COLUMNS:
        n_unique = grouped[column].nunique(dropna=False)

        conflict_groups = int((n_unique > 1).sum())
        constant_groups = int((n_unique == 1).sum())

        rows.append(
            {
                "variable": column,
                "sku_day_groups": int(total_groups),
                "groups_with_cross_warehouse_variation": conflict_groups,
                "groups_constant_across_warehouses": constant_groups,
                "variation_share": (
                    float(conflict_groups / total_groups)
                    if total_groups
                    else float("nan")
                ),
            }
        )

    return pd.DataFrame(rows)


def profile_warehouse_coverage(df: pd.DataFrame) -> pd.DataFrame:
    """Check how many warehouses are represented per SKU-day."""
    counts = (
        df.groupby(["Date", "SKU_ID"], observed=True)["Warehouse_ID"]
        .nunique()
        .rename("warehouse_count")
    )

    distribution = (
        counts.value_counts()
        .sort_index()
        .rename_axis("warehouses_per_sku_day")
        .reset_index(name="sku_day_groups")
    )

    distribution["share"] = distribution["sku_day_groups"] / len(counts)

    return distribution


def profile_inventory_ranges(df: pd.DataFrame) -> pd.DataFrame:
    """Summarise warehouse-level inventory variables."""
    rows: list[dict[str, object]] = []

    for column in INVENTORY_COLUMNS:
        series = df[column]

        rows.append(
            {
                "variable": column,
                "min": float(series.min()),
                "median": float(series.median()),
                "mean": float(series.mean()),
                "max": float(series.max()),
                "zero_share": float((series == 0).mean()),
            }
        )

    return pd.DataFrame(rows)


def save_outputs(
    output_dir: Path,
    native_grain: pd.DataFrame,
    cross_warehouse: pd.DataFrame,
    warehouse_coverage: pd.DataFrame,
    inventory_ranges: pd.DataFrame,
) -> None:
    """Save derived profiling summaries locally."""
    output_dir.mkdir(parents=True, exist_ok=True)

    native_grain.to_csv(output_dir / "native_grain_check.csv", index=False)
    cross_warehouse.to_csv(
        output_dir / "cross_warehouse_inventory_variation.csv",
        index=False,
    )
    warehouse_coverage.to_csv(
        output_dir / "warehouse_coverage_per_sku_day.csv",
        index=False,
    )
    inventory_ranges.to_csv(
        output_dir / "inventory_variable_ranges.csv",
        index=False,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check warehouse-level inventory alignment for COMP1884 Issue #16."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/raw/supply_chain_dataset1.csv"),
        help="Path to the local raw CSV dataset.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/processed/temporal_profile"),
        help="Directory for generated local profiling summaries.",
    )
    parser.add_argument("--start", required=True, help="Explicitly authorized scope start")
    parser.add_argument("--end", required=True, help="Explicitly authorized scope end")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    raw = load_raw_source(args.input, start=args.start, end=args.end)
    df, _ = build_validated_dataset(raw)

    native_grain = profile_native_grain(df)
    cross_warehouse = profile_cross_warehouse_variation(df)
    warehouse_coverage = profile_warehouse_coverage(df)
    inventory_ranges = profile_inventory_ranges(df)

    print("\n=== Native source grain ===")
    print(native_grain.to_string(index=False))

    print("\n=== Cross-warehouse inventory variation within SKU-day ===")
    print(cross_warehouse.to_string(index=False))

    print("\n=== Warehouse coverage per SKU-day ===")
    print(warehouse_coverage.to_string(index=False))

    print("\n=== Inventory variable ranges ===")
    print(inventory_ranges.to_string(index=False))

    save_outputs(
        args.output_dir,
        native_grain=native_grain,
        cross_warehouse=cross_warehouse,
        warehouse_coverage=warehouse_coverage,
        inventory_ranges=inventory_ranges,
    )

    print(f"\nSaved local summaries to: {args.output_dir}")


if __name__ == "__main__":
    main()
