from fastapi import APIRouter
from ..models.business import SalesResponse
from ..services.business_service import BusinessService

router = APIRouter(prefix="/api/sales", tags=["Sales"])


@router.get("", response_model=SalesResponse)
async def get_sales():
    """Returns monthly sales metrics, 6-month revenue history, and top products calculated from SQLite."""
    return BusinessService.get_sales()
