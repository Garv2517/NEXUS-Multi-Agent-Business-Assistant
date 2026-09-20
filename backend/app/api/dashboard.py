from fastapi import APIRouter
from ..models.business import DashboardResponse
from ..services.business_service import BusinessService

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard():
    """Returns executive overview metrics dynamically calculated from SQLite via business tools."""
    return BusinessService.get_dashboard()
