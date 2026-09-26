"""Descriptive inventory evidence; outputs are not risk classifications.

The functions in this module summarize the source inventory fields for later
methodology decisions. They do not infer inventory timing, calculate shortage
or excess risk, create risk labels, or recommend or calculate orders.
``Demand_Forecast`` remains the source-provided reference forecast.
"""
from __future__ import annotations

import pandas as pd

from src.inventory_risk.input_preparation import prepare_inventory_inputs

SUMMARY_FIELDS = (
    "Units_Sold",
    "Inventory_Level",
    "Reorder_Point",
    "Supplier_Lead_Time_Days",
    "Order_Quantity",
    "Demand_Forecast",
)
DESCRIPTIVE_DIFFERENCE = "inventory_minus_reorder_point"


def analyze_inventory_evidence(data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Return validated observations and methodology-neutral summaries.

    The result contains:

    - ``observations``: source fields with SKU, warehouse, and date preserved,
      plus ``inventory_minus_reorder_point`` as a same-record descriptive
      difference only (not a risk score or classification);
    - ``descriptive_summary``: count, mean, median, sample standard deviation,
      minimum, and maximum for each listed source field and the difference;
    - ``order_quantity_availability``: zero/nonzero counts and shares, using
      the dataset contract's meaning that zero indicates no recorded order
      quantity for that row.

    Input validation is delegated to ``prepare_inventory_inputs``. No source
    values are imputed or repaired. The source ``Demand_Forecast`` is described
    as a reference field and is never renamed as a model-generated forecast.
    No temporal join, future inventory assumption, risk rule, threshold,
    stockout label, or replenishment calculation is introduced.
    """
    observations = prepare_inventory_inputs(data)
    observations[DESCRIPTIVE_DIFFERENCE] = (
        observations["Inventory_Level"] - observations["Reorder_Point"]
    )

    summary_fields = [*SUMMARY_FIELDS, DESCRIPTIVE_DIFFERENCE]
    descriptive_summary = (
        observations[summary_fields]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .T.rename_axis("field")
        .reset_index()
    )

    order_quantity = observations["Order_Quantity"]
    row_count = len(observations)
    zero_count = int(order_quantity.eq(0).sum())
    nonzero_count = int(order_quantity.gt(0).sum())
    order_quantity_availability = pd.DataFrame(
        [
            {
                "observations": row_count,
                "zero_quantity_rows": zero_count,
                "nonzero_quantity_rows": nonzero_count,
                "zero_quantity_share": zero_count / row_count,
                "nonzero_quantity_share": nonzero_count / row_count,
            }
        ]
    )

    return {
        "observations": observations,
        "descriptive_summary": descriptive_summary,
        "order_quantity_availability": order_quantity_availability,
    }
