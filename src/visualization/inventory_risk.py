"""Descriptive plotting data and figures for inventory-risk evidence.

This module visualizes existing source fields and evidence summaries only. It
does not calculate risk scores, stockout predictions, replenishment quantities,
overstock rules, forecast uncertainty, or human-review logic. In particular,
``Demand_Forecast`` is labelled as a source reference field and is not treated
as a project-generated forecast.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from src.inventory_risk.evidence import (
    DESCRIPTIVE_DIFFERENCE,
    analyze_inventory_evidence,
)

DISTRIBUTION_FIELDS = (
    "Inventory_Level",
    "Reorder_Point",
    "Supplier_Lead_Time_Days",
    "Demand_Forecast",
)
SOURCE_FORECAST_REFERENCE_LABEL = (
    "Source Demand_Forecast (reference; not project-generated)"
)
FIELD_LABELS = {
    "Inventory_Level": "Inventory_Level",
    "Reorder_Point": "Reorder_Point",
    "Supplier_Lead_Time_Days": "Supplier_Lead_Time_Days",
    "Demand_Forecast": SOURCE_FORECAST_REFERENCE_LABEL,
}


def prepare_inventory_visual_data(data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Return validated, identity-preserving data for descriptive plots.

    Input validation and source evidence calculations are delegated to
    :func:`analyze_inventory_evidence`. The result contains the validated
    observations, long-form distribution data, descriptive summaries, a
    zero/nonzero ``Order_Quantity`` count table, and the same-record comparison
    of inventory with reorder point. The comparison is descriptive only.

    Missing required columns, empty input, or invalid source values raise the
    same errors as the existing inventory evidence component. The input is not
    mutated and no timing or same-day interpretation is introduced.
    """
    evidence = analyze_inventory_evidence(data)
    observations = evidence["observations"].copy()
    identity = ["Date", "SKU_ID", "Warehouse_ID"]

    distributions = observations[
        [*identity, *DISTRIBUTION_FIELDS]
    ].melt(
        id_vars=identity,
        value_vars=list(DISTRIBUTION_FIELDS),
        var_name="field",
        value_name="value",
    )
    distributions["display_label"] = distributions["field"].map(FIELD_LABELS)

    descriptive_summary = evidence["descriptive_summary"].copy()
    descriptive_summary["display_label"] = descriptive_summary["field"].map(
        FIELD_LABELS
    ).fillna(descriptive_summary["field"])

    order_availability = evidence["order_quantity_availability"].iloc[0]
    order_quantity_counts = pd.DataFrame(
        [
            {
                "quantity_status": "zero_recorded_quantity",
                "display_label": "Zero recorded Order_Quantity",
                "row_count": int(order_availability["zero_quantity_rows"]),
                "row_share": float(order_availability["zero_quantity_share"]),
            },
            {
                "quantity_status": "nonzero_recorded_quantity",
                "display_label": "Nonzero recorded Order_Quantity",
                "row_count": int(order_availability["nonzero_quantity_rows"]),
                "row_share": float(order_availability["nonzero_quantity_share"]),
            },
        ]
    )

    comparison_columns = [
        *identity,
        "Inventory_Level",
        "Reorder_Point",
        DESCRIPTIVE_DIFFERENCE,
    ]
    inventory_reorder_comparison = observations.loc[:, comparison_columns].copy()

    return {
        "observations": observations,
        "distributions": distributions,
        "descriptive_summary": descriptive_summary,
        "order_quantity_counts": order_quantity_counts,
        "inventory_reorder_comparison": inventory_reorder_comparison,
    }


def make_inventory_figures(data: pd.DataFrame) -> dict[str, Figure]:
    """Build reusable Matplotlib figures from descriptive inventory evidence.

    The returned figures are not displayed or saved automatically. Callers
    choose how to display, style, or export them. ``data`` follows the existing
    inventory evidence input contract.
    """
    visual_data = prepare_inventory_visual_data(data)
    distributions = visual_data["distributions"]
    comparison = visual_data["inventory_reorder_comparison"]
    order_counts = visual_data["order_quantity_counts"]

    distribution_figure, axes = plt.subplots(2, 2, figsize=(10, 7))
    for axis, field in zip(axes.flat, DISTRIBUTION_FIELDS):
        field_data = distributions.loc[distributions["field"].eq(field), "value"]
        axis.hist(field_data)
        axis.set_title(FIELD_LABELS[field])
        axis.set_xlabel(FIELD_LABELS[field])
        axis.set_ylabel("Observation count")
    distribution_figure.tight_layout()

    order_figure, order_axis = plt.subplots(figsize=(7, 4))
    order_axis.bar(order_counts["display_label"], order_counts["row_count"])
    order_axis.set_ylabel("Observation count")
    order_axis.set_title("Recorded Order_Quantity: zero and nonzero rows")
    order_axis.tick_params(axis="x", labelrotation=12)
    order_figure.tight_layout()

    comparison_figure, comparison_axis = plt.subplots(figsize=(6, 6))
    comparison_axis.scatter(
        comparison["Reorder_Point"], comparison["Inventory_Level"]
    )
    comparison_axis.set_xlabel("Reorder_Point")
    comparison_axis.set_ylabel("Inventory_Level")
    comparison_axis.set_title("Inventory_Level and Reorder_Point (descriptive)")
    comparison_figure.tight_layout()

    return {
        "descriptive_distributions": distribution_figure,
        "order_quantity_availability": order_figure,
        "inventory_reorder_comparison": comparison_figure,
    }
