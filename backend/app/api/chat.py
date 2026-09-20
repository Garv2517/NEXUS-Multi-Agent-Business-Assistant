from fastapi import APIRouter
from ..models.chat import ChatRequest, ChatResponse
from ..services.chat_service import ChatService

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Submits user prompt to Nexus Multi-Agent Assistant.
    Executes real deterministic business tools and returns factual numbers from SQLite.
    """
    return await ChatService.process_chat(request.message)
