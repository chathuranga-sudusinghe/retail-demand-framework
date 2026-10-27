"""Local FastAPI forecast demonstration using request-time model inference."""

from __future__ import annotations

import json
import math
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Any, Literal

from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.models import Example
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator

from src.decision_support.retained_cases import (
    RetainedCaseSourceError,
    load_retained_case_bundle,
)
from src.forecasting.features import calendar_date
from src.forecasting.inference import ForecastInference, InferenceError, load_inference
from src.forecasting.paths import REPOSITORY


class DemandDay(BaseModel):
    model_config = ConfigDict(extra="forbid")

    Date: Annotated[str, Field(pattern=r"^\d{4}-\d{2}-\d{2}$")]
    Units_Sold: Annotated[int, Field(strict=True, ge=0)]

    @field_validator("Date")
    @classmethod
    def calendar_day(cls, value: str) -> str:
        calendar_date(value)
        return value


class ForecastRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    SKU_ID: Annotated[str, Field(min_length=1, max_length=128)]
    Warehouse_ID: Annotated[str, Field(min_length=1, max_length=128)]
    forecast_origin: Annotated[str, Field(pattern=r"^\d{4}-\d{2}-\d{2}$")]
    horizon: StrictInt
    input_kind: Literal["synthetic_demo", "supplied_history"] = "supplied_history"
    history: Annotated[list[DemandDay], Field(min_length=28, max_length=366)]

    @field_validator("forecast_origin")
    @classmethod
    def calendar_day(cls, value: str) -> str:
        calendar_date(value)
        return value

    @field_validator("SKU_ID", "Warehouse_ID")
    @classmethod
    def unpadded_identifier(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError("Identifiers must not contain surrounding whitespace.")
        return value


class ForecastResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    inference_schema: str
    inference_mode: Literal["request_time"]
    input_kind: Literal["synthetic_demo", "supplied_history"]
    model_source_run_id: str
    manifest_reference: str
    manifest_sha256: str
    SKU_ID: str
    Warehouse_ID: str
    forecast_origin: str
    horizon: int
    target_start_date: str
    target_end_date: str
    forecast_type: Literal["next_day", "cumulative_window"]
    forecast_quantity: Annotated[float, Field(allow_inf_nan=False)]
    model: Literal["lightgbm", "xgboost"]
    configuration_id: str
    producer_designation: str
    provenance: dict[str, str]
    status: Literal["available"]
    unavailable_reasons: list[str]
    assumptions: list[str]
    limitations: list[str]


class RetainedDecisionSupportCase(BaseModel):
    """Unchanged management record plus a separate prospective projection."""

    assessment_id: str
    horizon: StrictInt
    record: dict[str, Any]
    prospective_record: dict[str, Any]


class RetainedDecisionSupportRoster(BaseModel):
    """The existing 20-case retained roster and its source context."""

    mapping_version: str
    source: dict[str, Any]
    scope: str
    records: list[RetainedDecisionSupportCase]


def create_app(
    *,
    repository: Path = REPOSITORY,
    loader: Callable[[Path], ForecastInference] = load_inference,
    retained_case_loader: Callable[[Path], dict[str, Any]] = load_retained_case_bundle,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        application.state.predictor = None
        try:
            application.state.predictor = loader(repository)
        except InferenceError:
            # Keep health and interactive docs usable when local artifacts are absent.
            pass
        yield
        application.state.predictor = None

    application = FastAPI(
        title="Retail Demand Forecast API",
        description="Compute a forecast from supplied daily history using a saved designated model.",
        version="1.0.0",
        lifespan=lifespan,
    )

    @application.exception_handler(RequestValidationError)
    async def invalid_request(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # Invalid numeric inputs must not break serialization of the 422 detail.
        detail = jsonable_encoder(
            exc.errors(),
            custom_encoder={
                float: lambda value: value if math.isfinite(value) else str(value)
            },
        )
        return JSONResponse(status_code=422, content={"detail": detail})

    examples: dict[str, Example] = {
        f"h{horizon}": {
            "summary": f"{horizon}-day synthetic history request",
            "value": json.loads(
                (
                    REPOSITORY / f"examples/forecast-api/forecast-{horizon}-day.json"
                ).read_text()
            ),
        }
        for horizon in (1, 7, 14, 28)
    }

    @application.get("/health")
    def health() -> dict[str, Any]:
        ready = application.state.predictor is not None
        return {
            "status": "ready" if ready else "unavailable",
            "available_horizons": [1, 7, 14, 28] if ready else [],
            "unavailable_reasons": [] if ready else ["source_unverified"],
        }

    @application.post("/forecasts", response_model=ForecastResponse)
    def forecast(
        request: ForecastRequest = Body(openapi_examples=examples),
    ) -> ForecastResponse:
        predictor = application.state.predictor
        if predictor is None:
            raise HTTPException(
                status_code=503,
                detail={
                    "reason_code": "source_unverified",
                    "message": "Saved producer models are unavailable.",
                },
            )
        try:
            result = predictor.predict(
                sku_id=request.SKU_ID,
                warehouse_id=request.Warehouse_ID,
                forecast_origin=request.forecast_origin,
                horizon=request.horizon,
                history=[row.model_dump() for row in request.history],
                input_kind=request.input_kind,
            )
        except InferenceError as exc:
            code = (
                503
                if exc.reason_code in {"source_unverified", "unavailable_forecast"}
                else 422
            )
            raise HTTPException(
                status_code=code,
                detail={"reason_code": exc.reason_code, "message": str(exc)},
            ) from exc
        return ForecastResponse(**result)

    def retained_cases() -> dict[str, Any]:
        try:
            return retained_case_loader(repository)
        except RetainedCaseSourceError as exc:
            raise HTTPException(
                status_code=503,
                detail={"reason_code": "source_unverified", "message": str(exc)},
            ) from exc

    @application.get(
        "/decision-support/cases", response_model=RetainedDecisionSupportRoster
    )
    def decision_support_cases() -> dict[str, Any]:
        return retained_cases()

    @application.get(
        "/decision-support/cases/{assessment_id}",
        response_model=RetainedDecisionSupportCase,
    )
    def decision_support_case(assessment_id: str) -> dict[str, Any]:
        bundle = retained_cases()
        for case in bundle["records"]:
            if case["assessment_id"] == assessment_id:
                return case
        raise HTTPException(
            status_code=404,
            detail={
                "reason_code": "unknown_case",
                "message": f"No retained decision-support case exists for {assessment_id}.",
            },
        )

    return application


app = create_app()
