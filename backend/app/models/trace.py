from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    id: str = Field(..., description="Unique identifier for the tool execution")
    agent: str = Field(..., description="Agent that initiated the tool call (e.g. sales, inventory)")
    tool: str = Field(..., description="Name of the tool executed (e.g. get_top_products)")
    status: str = Field(default="success", description="Status of tool execution")
    duration_ms: Optional[int] = Field(default=None, description="Execution duration in milliseconds")


class TraceEvent(BaseModel):
    id: str = Field(..., description="Unique event identifier (e.g. event_001)")
    type: str = Field(..., description="Event type matching multi-agent orchestration lifecycle")
    agent: Optional[str] = Field(default=None, description="Agent associated with this event")
    tool: Optional[str] = Field(default=None, description="Tool invoked if this is a tool event")
    status: str = Field(default="success", description="Status (running, success, error)")
    message: str = Field(..., description="Human-readable event description")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Context transfer or step metadata")
    duration_ms: Optional[int] = Field(default=None, description="Execution duration in milliseconds")
