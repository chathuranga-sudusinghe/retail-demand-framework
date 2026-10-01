"""Responsible decision-support record structures.

This module preserves reviewed upstream forecasting and inventory-risk
information for transparent, management-facing decision support.

It does not calculate forecasts, recalculate inventory risk, or make
autonomous replenishment decisions.
"""

from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class DecisionSupportRecord:
    """Management-facing responsible decision-support record."""

    sku_id: str
    warehouse_id: str
    forecast_origin: str
    forecast_horizon: str
    forecast_demand: Optional[float] = None
    forecast_provenance: Optional[str] = None
    inventory_risk_evidence: Optional[Any] = None
    inventory_risk_provenance: Optional[str] = None
    replenishment_recommendation: Optional[Any] = None
    uncertainty_or_error: Optional[Any] = None
    assumptions: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    management_consideration: Optional[str] = None
    human_review_status: str = "not_assessed"
    human_review_reasons: list[str] = field(
    default_factory=lambda: ["Human review has not yet been assessed."]
)
    unavailable_fields: dict[str, str] = field(default_factory=dict)
    component_provenance: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate responsible decision-support semantics."""
        if self.human_review_status == "review_required" and not self.human_review_reasons:
            raise ValueError(
                "human_review_reasons must be provided when review is required."
            )

        allowed_statuses = {"not_assessed", "review_required", "no_additional_review"}
        if self.human_review_status not in allowed_statuses:
            raise ValueError(
                f"Unsupported human_review_status: {self.human_review_status}"
            )