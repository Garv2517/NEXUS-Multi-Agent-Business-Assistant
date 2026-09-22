"""Chat Service.

Generates a session UUID and delegates orchestration to ManagerAgent. Production chat
requests always use the unified read-only analytics database for Sales and Inventory;
HR/activity remain on the operational Nexus database. If analytics data is unavailable,
Sales/Inventory fail cleanly rather than silently falling back to legacy dummy data.
"""

import uuid
from typing import Optional

from ..agents.manager import ManagerAgent
from ..core.config import settings
from ..models.chat import ChatResponse


class ChatService:
    @staticmethod
    async def process_chat(
        message: str,
        db_path: Optional[str] = None,
        analytics_db_path: Optional[str] = None,
    ) -> ChatResponse:
        session_id = str(uuid.uuid4())
        try:
            manager = ManagerAgent()
            resolved_analytics = analytics_db_path or settings.get_analytics_database_path()
            return await manager.orchestrate(
                query=message.strip(),
                session_id=session_id,
                db_path=db_path,
                analytics_db_path=resolved_analytics,
            )
        except Exception:
            return ChatResponse(
                session_id=session_id,
                answer="An unexpected error occurred while processing your request.",
                agents_used=[],
                tool_calls=[],
                trace=[],
            )
