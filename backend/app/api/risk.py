"""
FastAPI Router for NEXUS Phase D2: Risk Management.

Provides read-only deterministic risk metrics backed by RiskService and AnalyticsRepository.
Prefix: /api/risk
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..models.risk import (
    RiskThresholdConfigModel,
    RiskOverview,
    StockoutExposureResponse,
    InventoryPressureResponse,
    SlowMovingResponse,
    ConcentrationResponse,
    SalesVelocityResponse
)
from ..services.risk_service import RiskService

router = APIRouter(prefix="/api/risk", tags=["Risk Management"])


def get_risk_service() -> RiskService:
    """Dependency helper returning an instance of RiskService."""
    return RiskService()


@router.get("/config", response_model=RiskThresholdConfigModel)
async def get_risk_config(service: RiskService = Depends(get_risk_service)):
    """Returns the centralized immutable risk configuration and empirical thresholds."""
    return service.get_config()


@router.get("/overview", response_model=RiskOverview)
async def get_risk_overview(service: RiskService = Depends(get_risk_service)):
    """Returns independent domain risk statuses across stockouts, pressure, slow-moving, velocity, and concentration."""
    return service.get_risk_overview()


@router.get("/stockouts", response_model=StockoutExposureResponse)
async def get_stockout_exposure(
    limit: Optional[int] = Query(50, ge=1, le=500, description="Sample limit for zero-stock placements"),
    service: RiskService = Depends(get_risk_service)
):
    """Returns verified stockout exposure metrics and historical revenue associated with zero-stock placements."""
    try:
        return service.get_stockout_exposure(sample_limit=limit or 50)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/inventory-pressure", response_model=InventoryPressureResponse)
async def get_inventory_pressure(
    limit: Optional[int] = Query(100, ge=1, le=1000, description="Maximum placements to evaluate"),
    category: Optional[str] = Query(None, description="Filter by product category"),
    service: RiskService = Depends(get_risk_service)
):
    """Returns placement-level Days of Supply and empirical coverage tier classifications."""
    try:
        return service.get_inventory_pressure(limit=limit or 100, category=category)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/slow-moving", response_model=SlowMovingResponse)
async def get_slow_moving_inventory(
    limit: Optional[int] = Query(50, ge=1, le=500, description="Maximum candidate products/placements to return"),
    service: RiskService = Depends(get_risk_service)
):
    """Returns inventory items meeting the dual-condition slow-moving criteria (DOS > P90 and capital >= P75)."""
    try:
        return service.get_slow_moving_inventory(limit=limit or 50)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/concentration", response_model=ConcentrationResponse)
async def get_revenue_concentration(service: RiskService = Depends(get_risk_service)):
    """Returns internal portfolio revenue concentration and HHI metrics across products, categories, and stores."""
    return service.get_concentration()


@router.get("/sales-velocity", response_model=SalesVelocityResponse)
async def get_sales_velocity(
    limit: Optional[int] = Query(10, ge=1, le=100, description="Top products limit for contracting/growing tails"),
    service: RiskService = Depends(get_risk_service)
):
    """Returns 28-day sales velocity comparison across company, 16 categories, and individual products."""
    try:
        return service.get_sales_velocity(limit=limit or 10)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
