from fastapi import APIRouter
from ..models.business import InventoryResponse
from ..services.business_service import BusinessService

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])


@router.get("", response_model=InventoryResponse)
async def get_inventory():
    """Returns product stock levels and threshold alerts calculated dynamically from SQLite."""
    return BusinessService.get_inventory()
