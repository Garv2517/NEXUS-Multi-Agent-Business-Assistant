"""
Base agent contract for Phase B3.
All specialist agents inherit from BaseAgent and implement execute().
"""

from abc import ABC, abstractmethod
from .types import AgentTask, AgentResult


class BaseAgent(ABC):
    """Abstract base class establishing the contract for all specialist agents."""
    name: str
    description: str

    @abstractmethod
    async def execute(self, task: AgentTask) -> AgentResult:
        """
        Executes an assigned task and returns structured data.
        Specialist agents do NOT produce conversational prose.
        """
        pass
