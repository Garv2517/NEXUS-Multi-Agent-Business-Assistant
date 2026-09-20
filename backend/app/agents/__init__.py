"""
Agents package for Nexus Phase B3.
Exposes BaseAgent, specialist agents (Sales, Inventory, HR), ManagerAgent, and contracts.
"""

from .types import AgentTask, AgentResult, ToolCallRecord, ExecutionPlan, PlanStep
from .base import BaseAgent
from .sales import SalesAgent
from .inventory import InventoryAgent
from .hr import HRAgent
from .registry import AgentRegistry, create_default_registry
from .manager import ManagerAgent

__all__ = [
    "BaseAgent",
    "AgentTask",
    "AgentResult",
    "ToolCallRecord",
    "ExecutionPlan",
    "PlanStep",
    "SalesAgent",
    "InventoryAgent",
    "HRAgent",
    "AgentRegistry",
    "create_default_registry",
    "ManagerAgent",
]
