"""Prepare row-aligned forecasting and inventory evidence for Issue #70.

This is an internal analysis input, not a final cross-component interchange
schema. It consumes rows that have already been paired by an upstream caller;
it never joins an inventory row to a forecast or infers same-day availability.
The caller must supply explicit evidence that the inventory snapshot was
available at the forecast origin before snapshot values can support exposure
evidence.

The DR-012 exposure method is retained as *proposed for group approval*. Source
``Demand_Forecast`` is preserved if present but is never used as the project
forecast. Values are not clipped, rounded, imputed, or silently dropped.
"""
from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

METHOD_STATUS = "proposed_for_group_approval"
SUPPORTED_HORIZONS = (1, 7, 14, 28)
EVALUABLE_HORIZONS = (1, 7, 14)

REQUIRED_COLUMNS = (
    "SKU_ID",
    "Warehouse_ID",
    "forecast_origin",
    "horizon",
    "target_start_date",
    "target_end_date",
    "prediction",
    "run_id",
    "evaluation_stage",
    "evidence_role",
    "model",
    "configuration_id",
    "Date",
    "Inventory_Level",
    "Reorder_Point",
)

REQUIRED_PROVENANCE_COLUMNS = (
    "run_id",
    "evaluation_stage",
    "evidence_role",
    "model",
    "configuration_id",
)

METHOD_ASSUMPTIONS = (
    "Inventory_Level and Reorder_Point support exposure only when their origin availability is explicitly established.",
    "Reorder_Point is held fixed for the proposed scenario.",
    "No receipts, transfers, returns, losses, or other inventory adjustments are modelled.",
    "Realised Units_Sold is a demand proxy used retrospectively, not at forecast time.",
)
METHOD_LIMITATIONS = (
    "DR-012 is proposed for group approval; the exposure evidence is not an approved risk classification.",
    "The dataset is simulated and Stockout_Flag is not stockout ground truth.",
    "Source Demand_Forecast is a reference field, not the project forecast input.",
    "Order_Quantity is contextual recorded activity, not confirmed receipts or an optimal order.",
    "Negative scenario balances are not verified physical negative inventory.",
    "Snapshot within-day semantics remain unresolved and are not inferred here.",
    "Numerical replenishment quantity, overstock evaluation, uncertainty, and human-review rules are not provided.",
    "Twenty-eight-day downstream exposure requires separate component-owner/human approval.",
)


def _calendar_date(value: object) -> pd.Timestamp | pd.NaT:
    """Parse one calendar date without accepting numeric timestamps or tz values."""
    if pd.isna(value) or isinstance(value, (int, float, np.number)):
        return pd.NaT
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed) or getattr(parsed, "tzinfo", None) is not None:
        return pd.NaT
    parsed = pd.Timestamp(parsed)
    if parsed != parsed.normalize():
        return pd.NaT
    return parsed


def _missing_scalar(value: object) -> bool:
    if value is None or value is pd.NA:
        return True
    try:
        missing = pd.isna(value)
        return isinstance(missing, (bool, np.bool_)) and bool(missing)
    except (TypeError, ValueError):
        return False


def _finite_number(value: object, *, nonnegative: bool = False) -> float | None:
    """Return a finite parsed number, retaining invalid source cells untouched."""
    if pd.isna(value) or isinstance(value, (bool, np.bool_)):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if not np.isfinite(number) or (nonnegative and number < 0):
        return None
    return number


def _valid_count(value: object) -> float | None:
    number = _finite_number(value, nonnegative=True)
    if number is None or not number.is_integer():
        return None
    return number


def _nonblank(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value == value.strip()


def _reason_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, Iterable):
        return [str(item) for item in value if str(item).strip()]
    try:
        if bool(pd.isna(value)):
            return []
    except (TypeError, ValueError):
        pass
    return [str(value)]


def _horizon(value: object) -> int | None:
    if isinstance(value, (bool, np.bool_)) or pd.isna(value):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if not np.isfinite(number) or not number.is_integer():
        return None
    result = int(number)
    return result if result in SUPPORTED_HORIZONS else None


def prepare_inventory_risk_inputs(records: pd.DataFrame) -> pd.DataFrame:
    """Validate a row-aligned forecast/inventory panel without joining or repair.

    Required forecast columns use the current forecasting artifact vocabulary.
    ``Date`` is the source inventory-record date, kept
    separate from ``forecast_origin``. The optional boolean
    ``origin_snapshot_available`` must be supplied by the caller; a same-date
    match alone does not establish availability or before/after-sales timing.
    ``Supplier_Lead_Time_Days`` and ``Order_Quantity`` remain context-only and
    receive availability status only when their own origin-availability marker
    is explicitly supplied.

    Rows with unusable values are retained and receive explicit availability
    reasons. Missing columns, invalid identities, and duplicate prediction
    records are schema errors. Extra source/provenance fields—including the
    dataset's ``Demand_Forecast`` and ``Stockout_Flag``—are preserved unchanged.
    """
    if not isinstance(records, pd.DataFrame):
        raise TypeError("records must be a pandas DataFrame.")
    if not records.columns.is_unique:
        raise ValueError("Input column names must be unique.")
    missing = sorted(set(REQUIRED_COLUMNS) - set(records.columns))
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))
    if records.empty:
        raise ValueError("Inventory-risk input panel is empty.")

    frame = records.copy(deep=True).reset_index(drop=True)
    for column in ("SKU_ID", "Warehouse_ID", "run_id", "evaluation_stage", "evidence_role", "model", "configuration_id"):
        if not frame[column].map(_nonblank).all():
            raise ValueError(f"{column} must contain nonblank, unpadded text identifiers.")

    duplicate_key = [
        "run_id", "evaluation_stage", "evidence_role", "model", "configuration_id",
        "SKU_ID", "Warehouse_ID", "forecast_origin",
    ]
    if "fold_id" in frame.columns:
        duplicate_key.append("fold_id")
    if frame.duplicated(duplicate_key, keep=False).any():
        raise ValueError("Duplicate forecast records at run/model/configuration/SKU/warehouse/origin grain.")

    frame["_forecast_origin_date"] = frame["forecast_origin"].map(_calendar_date)
    frame["_inventory_record_date"] = frame["Date"].map(_calendar_date)
    frame["_target_start_date"] = frame["target_start_date"].map(_calendar_date)
    frame["_target_end_date"] = frame["target_end_date"].map(_calendar_date)
    frame["_horizon_days"] = frame["horizon"].map(_horizon)
    frame["_forecast_demand_value"] = frame["prediction"].map(_finite_number)
    frame["_inventory_level_value"] = frame["Inventory_Level"].map(_valid_count)
    frame["_reorder_point_value"] = frame["Reorder_Point"].map(_valid_count)
    frame["_observed_demand_value"] = (
        frame["observed_target"].map(_valid_count)
        if "observed_target" in frame.columns
        else pd.Series([None] * len(frame), index=frame.index, dtype=object)
    )

    if "origin_snapshot_available" not in frame.columns:
        frame["origin_snapshot_available"] = pd.NA
    if "origin_snapshot_unavailable_reason" not in frame.columns:
        frame["origin_snapshot_unavailable_reason"] = pd.NA

    frame["methodology_status"] = METHOD_STATUS
    frame["origin_snapshot_status"] = "unknown"
    frame["origin_snapshot_reason"] = "origin_snapshot_availability_not_established"
    frame["inventory_state_available"] = False
    frame["forecast_input_status"] = "unavailable"
    frame["forecast_input_reason"] = ""
    frame["downstream_use_status"] = "unavailable"
    frame["downstream_use_reason"] = ""
    frame["retrospective_input_status"] = "unavailable"
    frame["retrospective_input_reason"] = ""
    frame["lead_time_horizon_relation"] = pd.NA
    frame["preparation_unavailable_reasons"] = [[] for _ in range(len(frame))]
    frame["method_assumptions"] = [METHOD_ASSUMPTIONS for _ in range(len(frame))]
    frame["method_limitations"] = [METHOD_LIMITATIONS for _ in range(len(frame))]

    for index, row in frame.iterrows():
        reasons = _reason_list(row.get("unavailable_information_reasons"))
        origin, record_date = row["_forecast_origin_date"], row["_inventory_record_date"]

        marker = row["origin_snapshot_available"]
        if isinstance(marker, (bool, np.bool_)) and bool(marker):
            if pd.isna(origin) or pd.isna(record_date):
                snapshot_status, snapshot_reason = "unavailable", "invalid_origin_or_inventory_record_date"
            elif record_date != origin:
                snapshot_status, snapshot_reason = "unavailable", "inventory_record_date_does_not_match_forecast_origin"
            else:
                snapshot_status, snapshot_reason = "available", ""
        elif isinstance(marker, (bool, np.bool_)):
            snapshot_status = "unavailable"
            snapshot_reason = row.get("origin_snapshot_unavailable_reason")
            if not isinstance(snapshot_reason, str) or not snapshot_reason.strip():
                snapshot_reason = "origin_snapshot_not_available_at_forecast_origin"
        else:
            snapshot_status = "unknown"
            snapshot_reason = "origin_snapshot_availability_not_established"
        frame.at[index, "origin_snapshot_status"] = snapshot_status
        frame.at[index, "origin_snapshot_reason"] = snapshot_reason

        inventory_valid = (
            snapshot_status == "available"
            and row["_inventory_level_value"] is not None
            and row["_reorder_point_value"] is not None
        )
        frame.at[index, "inventory_state_available"] = bool(inventory_valid)
        if snapshot_status != "available":
            reasons.append(str(snapshot_reason))
        if row["_inventory_level_value"] is None:
            reasons.append("inventory_level_missing_or_invalid")
        if row["_reorder_point_value"] is None:
            reasons.append("reorder_point_missing_or_invalid")

        horizon = row["_horizon_days"]
        if horizon == 28:
            downstream_status = "not_approved_for_downstream_use"
            downstream_reason = "28_day_downstream_use_requires_separate_approval"
        elif horizon in EVALUABLE_HORIZONS:
            downstream_status = "proposed_method_not_group_approved"
            downstream_reason = "DR-012_remains_proposed_for_group_approval"
        else:
            downstream_status = "unavailable"
            downstream_reason = "unsupported_or_invalid_forecast_horizon"
        frame.at[index, "downstream_use_status"] = downstream_status
        frame.at[index, "downstream_use_reason"] = downstream_reason

        forecast_reasons: list[str] = []
        if horizon is None:
            forecast_reasons.append("unsupported_or_invalid_forecast_horizon")
        if pd.isna(row["_forecast_origin_date"]):
            forecast_reasons.append("forecast_origin_missing_or_invalid")
        if horizon is not None and (
            row["_target_start_date"] != row["_forecast_origin_date"] + pd.Timedelta(days=1)
            or row["_target_end_date"] != row["_forecast_origin_date"] + pd.Timedelta(days=horizon)
        ):
            forecast_reasons.append("forecast_target_interval_does_not_match_origin_and_horizon")
        if row["_forecast_demand_value"] is None:
            forecast_reasons.append("forecast_missing_or_nonfinite")
        elif row["_forecast_demand_value"] < 0:
            forecast_reasons.append("negative_forecast_handling_not_approved")
        if "prediction_status" not in frame.columns:
            forecast_reasons.append("forecast_prediction_status_not_provided")
        elif row["prediction_status"] != "available":
            forecast_reasons.append("forecast_prediction_status_not_available")
        if "eligibility_status" not in frame.columns:
            forecast_reasons.append("forecast_eligibility_status_not_provided")
        elif row["eligibility_status"] != "eligible":
            forecast_reasons.append("forecast_eligibility_status_not_eligible")
        if any(not _nonblank(row[column]) for column in REQUIRED_PROVENANCE_COLUMNS):
            forecast_reasons.append("forecast_provenance_incomplete")
        forecast_status = "available" if not forecast_reasons else "unavailable"
        frame.at[index, "forecast_input_status"] = forecast_status
        frame.at[index, "forecast_input_reason"] = ";".join(forecast_reasons)
        reasons.extend(forecast_reasons)

        retrospective_reasons: list[str] = []
        if horizon is None:
            retrospective_reasons.append("unsupported_or_invalid_forecast_horizon")
        if row["_observed_demand_value"] is None:
            retrospective_reasons.append("realised_horizon_demand_unavailable")
        elif row["_observed_demand_value"] < 0:
            retrospective_reasons.append("realised_horizon_demand_invalid")
        if "target_status" not in frame.columns:
            retrospective_reasons.append("retrospective_target_status_not_provided")
        elif row["target_status"] != "complete":
            retrospective_reasons.append("retrospective_target_status_not_complete")
        retrospective_status = "available" if not retrospective_reasons else "unavailable"
        frame.at[index, "retrospective_input_status"] = retrospective_status
        frame.at[index, "retrospective_input_reason"] = ";".join(retrospective_reasons)
        reasons.extend(retrospective_reasons)

        for value_name, availability_column, output_name in (
            ("Supplier_Lead_Time_Days", "supplier_lead_time_available_at_origin", "lead_time_context_status"),
            ("Order_Quantity", "order_quantity_available_at_origin", "order_quantity_context_status"),
        ):
            if value_name not in frame.columns:
                frame.at[index, output_name] = "unavailable"
                reasons.append(f"{value_name}_not_provided")
            elif availability_column not in frame.columns or _missing_scalar(row.get(availability_column)):
                frame.at[index, output_name] = "unknown"
                reasons.append(f"{value_name}_availability_at_origin_not_established")
            elif not isinstance(row[availability_column], (bool, np.bool_)):
                frame.at[index, output_name] = "unknown"
                reasons.append(f"{value_name}_availability_marker_invalid")
            elif not bool(row[availability_column]):
                frame.at[index, output_name] = "unavailable"
                reasons.append(f"{value_name}_not_available_at_origin")
            elif snapshot_status != "available":
                frame.at[index, output_name] = "unavailable"
                reasons.append(f"{value_name}_origin_record_not_available")
            elif _valid_count(row[value_name]) is None:
                frame.at[index, output_name] = "unavailable"
                reasons.append(f"{value_name}_missing_or_invalid")
            else:
                frame.at[index, output_name] = "available_as_context_only"

        if frame.at[index, "lead_time_context_status"] == "available_as_context_only" and horizon is not None:
            lead_time = _valid_count(row["Supplier_Lead_Time_Days"])
            if lead_time is not None:
                relation = (
                    "horizon_shorter_than_lead_time"
                    if horizon < lead_time
                    else "horizon_equal_to_lead_time"
                    if horizon == lead_time
                    else "horizon_longer_than_lead_time"
                )
                frame.at[index, "lead_time_horizon_relation"] = relation

        frame.at[index, "preparation_unavailable_reasons"] = list(dict.fromkeys(reasons))

    return frame
