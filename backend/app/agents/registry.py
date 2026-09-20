"""
Agent Registry for Phase B3.
Provides decoupled registration and lookup of specialist agents.
ManagerAgent receives an AgentRegistry instance in its constructor.
"""

from typing import Dict, Optional, List
from .base import BaseAgent
from .sales import SalesAgent
from .inventory import InventoryAgent
from .hr import HRAgent


class AgentRegistry:
    """Stores and resolves specialist agents by domain key."""

    def __init__(self, agents: Optional[Dict[str, BaseAgent]] = None):
        self._agents: Dict[str, BaseAgent] = agents or {}

    def register(self, name: str, agent: BaseAgent) -> None:
        self._agents[name] = agent

    def get(self, name: str) -> Optional[BaseAgent]:
        return self._agents.get(name)

    def list_agents(self) -> List[str]:
        return list(self._agents.keys())


def create_default_registry() -> AgentRegistry:
    """Factory creating a standard registry with Sales, Inventory, and HR agents."""
    reg = AgentRegistry()
    reg.register("sales", SalesAgent())
    reg.register("inventory", InventoryAgent())
    reg.register("hr", HRAgent())
    return reg
