from fastapi import APIRouter
from ..models.business import HRResponse
from ..services.business_service import BusinessService

router = APIRouter(prefix="/api/hr", tags=["HR"])


@router.get("", response_model=HRResponse)
async def get_hr():
    """Returns headcount, on-leave metrics, and corporate policy summaries from SQLite."""
    return BusinessService.get_hr()
