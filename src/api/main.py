"""Local FastAPI forecast demonstration using request-time model inference."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
import json
from pathlib import Path
from typing import Annotated, Any, Literal

from fastapi import Body, FastAPI, HTTPException
from fastapi.openapi.models import Example
from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator

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


def create_app(
    *,
    repository: Path = REPOSITORY,
    loader: Callable[[Path], ForecastInference] = load_inference,
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

    return application


app = create_app()
