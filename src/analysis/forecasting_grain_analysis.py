"""Temporal demand profiling for COMP1884 Issue #16.

This module profiles the verified local supply-chain dataset before any
forecasting model is trained. It compares candidate analytical units:

- SKU-day
- SKU-warehouse-day
- SKU-week

The script intentionally does NOT use the source Demand_Forecast field and
does NOT use Stockout_Flag as a target/label.

Example
-------
python -m src.analysis.forecasting_grain_analysis \
    --input data/raw/supply_chain_dataset1.csv \
    --start YYYY-MM-DD --end YYYY-MM-DD \
    --output-dir data/processed/temporal_profile
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.data.data_cleaning import build_validated_dataset, load_raw_source


FORBIDDEN_MODEL_COLUMNS = {
    "Demand_Forecast",
    "Stockout_Flag",
}


def check_source_constraints(df: pd.DataFrame) -> pd.DataFrame:
    """Return a compact table of dataset constraints relevant to Issue #16."""
    rows: list[dict[str, object]] = []

    rows.append(
        {
            "check": "row_count",
            "value": int(len(df)),
            "note": "Source rows loaded",
        }
    )
    rows.append(
        {
            "check": "date_min",
            "value": df["Date"].min().date().isoformat(),
            "note": "Earliest observed date",
        }
    )
    rows.append(
        {
            "check": "date_max",
            "value": df["Date"].max().date().isoformat(),
            "note": "Latest observed date",
        }
    )
    rows.append(
        {
            "check": "unique_dates",
            "value": int(df["Date"].nunique()),
            "note": "Observed dates",
        }
    )
    rows.append(
        {
            "check": "unique_skus",
            "value": int(df["SKU_ID"].nunique()),
            "note": "SKU cardinality",
        }
    )
    rows.append(
        {
            "check": "unique_warehouses",
            "value": int(df["Warehouse_ID"].nunique()),
            "note": "Warehouse cardinality",
        }
    )

    if "Stockout_Flag" in df.columns:
        rows.append(
            {
                "check": "stockout_flag_unique_values",
                "value": int(df["Stockout_Flag"].nunique(dropna=False)),
                "note": (
                    "Must not be used as a classification target when zero-variance"
                ),
            }
        )
        rows.append(
            {
                "check": "stockout_flag_positive_rows",
                "value": int((df["Stockout_Flag"] == 1).sum()),
                "note": "Expected to be 0 in the verified dataset",
            }
        )

    if "Order_Quantity" in df.columns:
        rows.append(
            {
                "check": "nonzero_order_quantity_rows",
                "value": int((df["Order_Quantity"] > 0).sum()),
                "note": "Used only as a dataset constraint at this stage",
            }
        )

    for column in sorted(FORBIDDEN_MODEL_COLUMNS):
        if column in df.columns:
            rows.append(
                {
                    "check": f"{column}_present",
                    "value": True,
                    "note": "Presence does not imply permission to use it for forecasting",
                }
            )

    return pd.DataFrame(rows)


def build_sku_day(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate Units_Sold across warehouses for each SKU and day."""
    return (
        df.groupby(["Date", "SKU_ID"], as_index=False, observed=True)
        .agg(demand=("Units_Sold", "sum"))
        .sort_values(["SKU_ID", "Date"])
        .reset_index(drop=True)
    )


def build_sku_warehouse_day(df: pd.DataFrame) -> pd.DataFrame:
    """Build the SKU-warehouse-day candidate demand series."""
    return (
        df.groupby(
            ["Date", "SKU_ID", "Warehouse_ID"],
            as_index=False,
            observed=True,
        )
        .agg(demand=("Units_Sold", "sum"))
        .sort_values(["SKU_ID", "Warehouse_ID", "Date"])
        .reset_index(drop=True)
    )


def build_sku_week(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate demand to SKU-week using Monday-start weekly periods."""
    temp = df[["Date", "SKU_ID", "Units_Sold"]].copy()
    temp["period"] = temp["Date"].dt.to_period("W-SUN").dt.start_time

    return (
        temp.groupby(["period", "SKU_ID"], as_index=False, observed=True)
        .agg(demand=("Units_Sold", "sum"))
        .sort_values(["SKU_ID", "period"])
        .reset_index(drop=True)
    )


def _series_summary(
    frame: pd.DataFrame,
    *,
    unit_name: str,
    time_col: str,
    series_cols: list[str],
) -> pd.DataFrame:
    """Summarise completeness, sparsity and variation across candidate series."""
    grouped = frame.groupby(series_cols, observed=True, dropna=False)

    series_stats = grouped["demand"].agg(
        n_observations="size",
        mean_demand="mean",
        median_demand="median",
        std_demand="std",
        min_demand="min",
        max_demand="max",
    )

    zero_share = grouped["demand"].apply(lambda s: float((s == 0).mean()))
    series_stats["zero_demand_share"] = zero_share

    mean_nonzero = series_stats["mean_demand"].replace(0, np.nan)
    series_stats["coefficient_of_variation"] = (
        series_stats["std_demand"] / mean_nonzero
    )

    # Short-lag dependence is descriptive only; it is not model selection.
    lag1_values = grouped["demand"].apply(lambda s: s.autocorr(lag=1))
    series_stats["lag1_autocorrelation"] = lag1_values

    date_counts = grouped[time_col].nunique()
    span_days = grouped[time_col].agg(
        lambda s: int((s.max() - s.min()).days) + 1
    )

    expected_step_days = 7 if unit_name == "sku_week" else 1
    expected_observations = (
        (span_days - 1) // expected_step_days + 1
    ).astype(int)

    completeness = (date_counts / expected_observations).clip(upper=1.0)
    series_stats["temporal_completeness"] = completeness

    result = pd.DataFrame(
        {
            "analytical_unit": [unit_name],
            "n_series": [int(len(series_stats))],
            "n_rows": [int(len(frame))],
            "median_observations_per_series": [
                float(series_stats["n_observations"].median())
            ],
            "median_zero_demand_share": [
                float(series_stats["zero_demand_share"].median())
            ],
            "median_coefficient_of_variation": [
                float(series_stats["coefficient_of_variation"].median(skipna=True))
            ],
            "median_lag1_autocorrelation": [
                float(series_stats["lag1_autocorrelation"].median(skipna=True))
            ],
            "median_temporal_completeness": [
                float(series_stats["temporal_completeness"].median())
            ],
            "median_mean_demand": [
                float(series_stats["mean_demand"].median())
            ],
        }
    )

    return result


def profile_candidate_units(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """Build and compare the three candidate analytical units."""
    sku_day = build_sku_day(df)
    sku_warehouse_day = build_sku_warehouse_day(df)
    sku_week = build_sku_week(df)

    summaries = [
        _series_summary(
            sku_day,
            unit_name="sku_day",
            time_col="Date",
            series_cols=["SKU_ID"],
        ),
        _series_summary(
            sku_warehouse_day,
            unit_name="sku_warehouse_day",
            time_col="Date",
            series_cols=["SKU_ID", "Warehouse_ID"],
        ),
        _series_summary(
            sku_week,
            unit_name="sku_week",
            time_col="period",
            series_cols=["SKU_ID"],
        ),
    ]

    return (
        pd.concat(summaries, ignore_index=True),
        {
            "sku_day": sku_day,
            "sku_warehouse_day": sku_warehouse_day,
            "sku_week": sku_week,
        },
    )


def promotion_consistency_check(df: pd.DataFrame) -> pd.DataFrame:
    """Check whether Promotion_Flag is consistent across warehouses per SKU-day.

    No causal promotion effect is estimated here. This only determines whether
    a later SKU-day aggregation can safely carry one promotion state without
    inventing an aggregation rule.
    """
    grouped = (
        df.groupby(["Date", "SKU_ID"], observed=True)["Promotion_Flag"]
        .nunique(dropna=False)
        .rename("n_unique_promotion_values")
        .reset_index()
    )

    conflicts = grouped[grouped["n_unique_promotion_values"] > 1]

    return pd.DataFrame(
        {
            "sku_day_groups": [int(len(grouped))],
            "groups_with_conflicting_promotion_flag": [int(len(conflicts))],
            "conflict_share": [
                float(len(conflicts) / len(grouped)) if len(grouped) else np.nan
            ],
        }
    )


def save_outputs(
    output_dir: Path,
    constraints: pd.DataFrame,
    comparison: pd.DataFrame,
    promotion_check: pd.DataFrame,
) -> None:
    """Save small derived profiling summaries locally.

    The repository .gitignore already excludes generated CSV files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    constraints.to_csv(output_dir / "source_constraints.csv", index=False)
    comparison.to_csv(output_dir / "analytical_unit_comparison.csv", index=False)
    promotion_check.to_csv(output_dir / "promotion_consistency.csv", index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Profile temporal demand for COMP1884 Issue #16."
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
    constraints = check_source_constraints(df)
    comparison, _ = profile_candidate_units(df)
    promotion_check = promotion_consistency_check(df)

    print("\n=== Source constraints ===")
    print(constraints.to_string(index=False))

    print("\n=== Candidate analytical-unit comparison ===")
    print(comparison.to_string(index=False))

    print("\n=== Promotion_Flag consistency at SKU-day level ===")
    print(promotion_check.to_string(index=False))

    save_outputs(
        args.output_dir,
        constraints=constraints,
        comparison=comparison,
        promotion_check=promotion_check,
    )

    print(f"\nSaved local summaries to: {args.output_dir}")


if __name__ == "__main__":
    main()
