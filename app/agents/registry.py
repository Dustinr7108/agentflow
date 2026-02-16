"""Agent Registry - maps agent types to implementations."""
from app.agents.base import BaseAgent
from app.agents.llm_agent import LLMAgent
from app.agents.web_search_agent import WebSearchAgent
from app.agents.code_exec_agent import CodeExecAgent
from app.agents.api_call_agent import APICallAgent
from app.agents.data_transform_agent import DataTransformAgent
from app.agents.conditional_agent import ConditionalAgent


AGENT_REGISTRY: dict[str, type[BaseAgent]] = {
    "llm": LLMAgent,
    "web_search": WebSearchAgent,
    "code_exec": CodeExecAgent,
    "api_call": APICallAgent,
    "data_transform": DataTransformAgent,
    "conditional": ConditionalAgent,
}


def get_agent(agent_type: str, config: dict | None = None, tools: dict | None = None) -> BaseAgent:
    """Instantiate an agent by type."""
    cls = AGENT_REGISTRY.get(agent_type)
    if not cls:
        raise ValueError(f"Unknown agent type: {agent_type}. Available: {list(AGENT_REGISTRY.keys())}")
    return cls(config=config, tools=tools)


def list_agent_types() -> list[dict]:
    """List all available agent types with descriptions."""
    return [
        {
            "type": agent_type,
            "name": cls.name,
            "description": cls.description,
        }
        for agent_type, cls in AGENT_REGISTRY.items()
    ]
