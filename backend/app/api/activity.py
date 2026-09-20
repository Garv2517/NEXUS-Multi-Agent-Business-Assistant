from typing import List
from fastapi import APIRouter
from ..models.business import ActivityLogItem
from ..services.business_service import BusinessService

router = APIRouter(prefix="/api/activity", tags=["Activity"])


@router.get("", response_model=List[ActivityLogItem])
async def get_activity():
    """Returns actual recorded multi-agent execution logs and tool call durations from SQLite."""
    return BusinessService.get_activity_logs()
