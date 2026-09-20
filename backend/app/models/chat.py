from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from .trace import ToolCall, TraceEvent


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User question or prompt for Nexus assistant")

    @field_validator('message')
    @classmethod
    def validate_message_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Message cannot be empty or whitespace only")
        return v.strip()


class ChatResponse(BaseModel):
    session_id: str = Field(..., description="Unique conversation session ID")
    answer: str = Field(..., description="Synthesized multi-agent business answer")
    agents_used: List[str] = Field(..., description="List of agents involved in generating the answer")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="Record of tools executed by agents")
    trace: List[TraceEvent] = Field(default_factory=list, description="Orchestration step events for timeline display")
    plan: Optional[Dict[str, Any]] = Field(default=None, description="Optional deterministic execution plan")
