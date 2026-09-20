"""
Chat Service for Phase B3.
Generates session UUID, delegates query orchestration to ManagerAgent,
and performs top-level safe error handling.
Contains no routing logic or direct tool executions.
"""

import uuid
from typing import Optional
from ..agents.manager import ManagerAgent
from ..models.chat import ChatResponse


class ChatService:
    @staticmethod
    async def process_chat(message: str, db_path: Optional[str] = None) -> ChatResponse:
        """
        Coordinates chat request by issuing a unique session UUID and delegating
        execution to the local ManagerAgent orchestrator.
        """
        session_id = str(uuid.uuid4())
        try:
            manager = ManagerAgent()
            return await manager.orchestrate(
                query=message.strip(),
                session_id=session_id,
                db_path=db_path
            )
        except Exception as e:
            # Top-level failure protection: never leak raw exceptions or stack traces
            return ChatResponse(
                session_id=session_id,
                answer="An unexpected error occurred while processing your request.",
                agents_used=[],
                tool_calls=[],
                trace=[]
            )
