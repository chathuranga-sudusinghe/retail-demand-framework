"""Read-only API for the 20 retained research cases (Issue #183).

Fixed-origin research evidence only. These routes never call the request-time
predictor used by ``POST /forecasts`` and accept no request body.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from fastapi import APIRouter, HTTPException, Path, Request
from pydantic import BaseModel, ConfigDict

from src.decision_support.retained_cases import RetainedCaseCatalog


class InventoryScenario(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["available", "unavailable", "gated"]
    reason: str | None
    evidence: dict[str, Any] | None
    provenance: dict[str, Any] | None


class RetainedCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_schema: str
    evidence_mode: Literal["fixed_origin_retained_research"]
    mapping_version: str
    assessment_id: str
    SKU_ID: str
    Warehouse_ID: str
    forecast_origin: str
    horizon: int
    forecast: dict[str, Any]
    inventory_scenario: InventoryScenario
    decision_support_record: dict[str, Any]
    advisory_notice: str


class CaseSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assessment_id: str
    SKU_ID: str
    Warehouse_ID: str
    forecast_origin: str
    horizon: int
    inventory_status: Literal["available", "unavailable", "gated"]
    human_review_status: str


class CaseList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_mode: Literal["fixed_origin_retained_research"]
    case_count: int
    source: dict[str, Any]
    cases: list[CaseSummary]


router = APIRouter(prefix="/research-cases", tags=["retained research cases"])


def _catalog(request: Request) -> RetainedCaseCatalog:
    catalog = request.app.state.research_cases
    if catalog is None:
        raise HTTPException(
            status_code=503,
            detail={
                "reason_code": request.app.state.research_cases_reason,
                "message": "Retained research-case sources are unavailable or unverified.",
            },
        )
    return catalog


def _not_found(description: str) -> HTTPException:
    return HTTPException(
        status_code=404,
        detail={
            "reason_code": "case_not_in_retained_roster",
            "message": f"{description} is not one of the 20 retained research cases.",
        },
    )


@router.get("", response_model=CaseList)
def list_cases(request: Request) -> CaseList:
    catalog = _catalog(request)
    summaries = catalog.summaries()
    return CaseList(
        evidence_mode="fixed_origin_retained_research",
        case_count=len(summaries),
        source=catalog.source_document(),
        cases=[CaseSummary(**item) for item in summaries],
    )


@router.get("/{assessment_id}", response_model=RetainedCase)
def get_case(
    request: Request,
    assessment_id: Annotated[str, Path(min_length=1, max_length=16)],
) -> RetainedCase:
    case = _catalog(request).get(assessment_id)
    if case is None:
        raise _not_found(f"Assessment ID {assessment_id!r}")
    return RetainedCase(**case)


@router.get(
    "/{sku_id}/{warehouse_id}/{forecast_origin}/{horizon}",
    response_model=RetainedCase,
)
def find_case(
    request: Request,
    sku_id: Annotated[str, Path(min_length=1, max_length=128)],
    warehouse_id: Annotated[str, Path(min_length=1, max_length=128)],
    forecast_origin: Annotated[str, Path(pattern=r"^\d{4}-\d{2}-\d{2}$")],
    horizon: int,
) -> RetainedCase:
    case = _catalog(request).find(sku_id, warehouse_id, forecast_origin, horizon)
    if case is None:
        raise _not_found(
            f"Forecast key ({sku_id}, {warehouse_id}, {forecast_origin}, h={horizon})"
        )
    return RetainedCase(**case)
