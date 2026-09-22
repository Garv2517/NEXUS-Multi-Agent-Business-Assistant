"""FastAPI routes for NEXUS D3B Forecasting & Demand Planning."""
from fastapi import APIRouter, Depends

from ..models.forecast import (
    CategoryForecastResponse,
    CompanyForecastResponse,
    DemandCoverageResponse,
    ForecastConfigResponse,
)
from ..services.forecast_service import ForecastService

router = APIRouter(prefix="/api/forecast", tags=["Forecasting & Demand Planning"])


def get_forecast_service() -> ForecastService:
    return ForecastService()


@router.get("/config", response_model=ForecastConfigResponse)
async def get_forecast_config(service: ForecastService = Depends(get_forecast_service)):
    return service.get_config()


@router.get("/company", response_model=CompanyForecastResponse)
async def get_company_forecast(service: ForecastService = Depends(get_forecast_service)):
    return service.get_company_forecast()


@router.get("/categories", response_model=CategoryForecastResponse)
async def get_category_forecasts(service: ForecastService = Depends(get_forecast_service)):
    return service.get_category_forecasts()


@router.get("/coverage", response_model=DemandCoverageResponse)
async def get_demand_coverage(service: ForecastService = Depends(get_forecast_service)):
    return service.get_demand_coverage()
