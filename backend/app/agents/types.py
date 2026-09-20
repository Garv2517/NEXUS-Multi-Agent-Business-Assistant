"""
Shared agent types and data contracts for Phase B3.
Defines AgentTask, AgentResult, ToolCallRecord, and ExecutionPlan.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentTask(BaseModel):
    """Encapsulates a unit of work assigned to a specialist agent."""
    task_id: str
    operation: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)


class ToolCallRecord(BaseModel):
    """Captures the execution details and measured latency of a tool call."""
    id: str
    agent: str
    tool: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    status: str = "success"  # "success" or "error"
    duration_ms: int = 0
    result_summary: str = ""
    error: Optional[str] = None


class AgentResult(BaseModel):
    """Structured data returned by a specialist agent upon task completion."""
    task_id: str
    agent: str
    status: str = "success"  # "success" or "error"
    data: Optional[Dict[str, Any]] = None
    tool_calls: List[ToolCallRecord] = Field(default_factory=list)
    error: Optional[Dict[str, Any]] = None


class PlanStep(BaseModel):
    """A discrete step in an execution plan."""
    step: int
    agent: str
    operation: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    depends_on: Optional[int] = None
    description: Optional[str] = None


class ExecutionPlan(BaseModel):
    """Deterministic routing and execution plan created by the router."""
    plan_id: str
    intent: str
    query: str
    agents: List[str] = Field(default_factory=list)
    steps: List[PlanStep] = Field(default_factory=list)
