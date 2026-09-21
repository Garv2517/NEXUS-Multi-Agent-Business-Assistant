from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..models.analytics import (
    AnalyticsMetadata,
    CompanySummary,
    MonthlySalesResponse,
    CategoryPerformanceResponse,
    ProductPerformanceResponse,
    StorePerformanceResponse,
    LocationPerformanceResponse,
    InventoryAnalyticsModel,
    InventoryProductResponse
)
from ..services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


def get_analytics_service() -> AnalyticsService:
    """Dependency helper returning an instance of AnalyticsService."""
    return AnalyticsService()


@router.get("/metadata", response_model=AnalyticsMetadata)
async def get_metadata(service: AnalyticsService = Depends(get_analytics_service)):
    """Returns provenance and operational assumptions of the external Kaggle dataset."""
    return service.get_metadata()


@router.get("/summary", response_model=CompanySummary)
async def get_company_summary(service: AnalyticsService = Depends(get_analytics_service)):
    """Returns executive company totals, gross profit, margin, and order metrics."""
    return service.get_company_summary()


@router.get("/monthly", response_model=MonthlySalesResponse)
@router.get("/monthly-sales", response_model=MonthlySalesResponse)
async def get_monthly_sales(service: AnalyticsService = Depends(get_analytics_service)):
    """Returns chronological monthly sales trend across the dataset window (Jan-Dec 2025)."""
    return service.get_monthly_sales()


@router.get("/categories", response_model=CategoryPerformanceResponse)
async def get_category_performance(service: AnalyticsService = Depends(get_analytics_service)):
    """Returns category-level revenue, unit volumes, profit, and revenue share."""
    return service.get_category_performance()


@router.get("/products", response_model=ProductPerformanceResponse)
async def get_product_performance(
    limit: Optional[int] = Query(None, description="Maximum number of products to return (1-1000)"),
    order_by: str = Query("revenue", description="Sort order: revenue, units, profit, margin"),
    category: Optional[str] = Query(None, description="Filter by product category"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Returns SKU-level sales, gross revenue, and profitability metrics."""
    try:
        return service.get_product_performance(limit=limit, order_by=order_by, category=category)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/stores", response_model=StorePerformanceResponse)
async def get_store_performance(
    limit: Optional[int] = Query(None, description="Maximum number of stores to return (1-1000)"),
    order_by: str = Query("revenue", description="Sort order: revenue, units, profit, transactions"),
    location: Optional[str] = Query(None, description="Filter by store location classification"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Returns store-level transaction counts, volume, and revenue rankings."""
    try:
        return service.get_store_performance(limit=limit, order_by=order_by, location=location)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/locations", response_model=LocationPerformanceResponse)
async def get_location_performance(service: AnalyticsService = Depends(get_analytics_service)):
    """Returns performance aggregated across commercial location zoning types."""
    return service.get_location_performance()


@router.get("/inventory", response_model=InventoryAnalyticsModel)
@router.get("/inventory/summary", response_model=InventoryAnalyticsModel)
async def get_inventory_analytics(service: AnalyticsService = Depends(get_analytics_service)):
    """Returns point-in-time warehouse and store inventory valuation and health."""
    return service.get_inventory_analytics()


@router.get("/inventory/products", response_model=InventoryProductResponse)
async def get_inventory_by_product(
    limit: Optional[int] = Query(10, description="Maximum number of products to return (1-1000)"),
    order_by: str = Query("stock_units", description="Sort order: stock_units, cost_value, retail_value, placements, zero_stock"),
    category: Optional[str] = Query(None, description="Filter by product category"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Returns product-level inventory metrics across all store placements."""
    try:
        return service.get_inventory_by_product(limit=limit, order_by=order_by, category=category)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
