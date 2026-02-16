"""Base agent interface - all agents implement this contract."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResult:
    """Standardized result from any agent execution."""
    success: bool
    output: Any
    tokens_used: int = 0
    cost_usd: float = 0.0
    duration_ms: int = 0
    metadata: dict = field(default_factory=dict)


class BaseAgent(ABC):
    """Abstract base for all agents in the system."""
    name: str = "base"
    description: str = "Base agent"

    def __init__(self, config: dict | None = None, tools: dict | None = None):
        self.config = config or {}
        self.tools = tools or {}

    @abstractmethod
    def run(self, objective: str, context: dict | None = None) -> AgentResult:
        """Execute the agent's task.

        Args:
            objective: What the agent should accomplish
            context: Data from upstream agents in the workflow

        Returns:
            AgentResult with output and metadata
        """
        ...
