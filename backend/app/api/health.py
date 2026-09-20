from fastapi import APIRouter
from ..models.business import HealthResponse
from ..services.business_service import BusinessService

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
async def get_health():
    """Returns backend status, mode, and mock status."""
    return BusinessService.get_health()
