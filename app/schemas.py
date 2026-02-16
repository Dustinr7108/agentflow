"""Pydantic schemas for API request/response validation."""
from pydantic import BaseModel, EmailStr
from typing import Optional, Any
from datetime import datetime


# --- Auth ---
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str = ""


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: str
    email: str
    name: str
    plan: str
    runs_this_month: int
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Agent Defs ---
class AgentDefCreate(BaseModel):
    name: str
    description: str = ""
    agent_type: str  # llm, web_search, code_exec, api_call, data_transform, conditional
    config: dict = {}


class AgentDefOut(BaseModel):
    id: str
    name: str
    description: str
    agent_type: str
    config: dict
    is_builtin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Workflows ---
class WorkflowNode(BaseModel):
    id: str
    agent_def_id: str = ""
    agent_type: str = "llm"
    objective: str = ""
    position: dict = {"x": 0, "y": 0}
    config_overrides: dict = {}
    stop_on_failure: bool = True


class WorkflowEdge(BaseModel):
    source_id: str
    target_id: str
    condition: str = ""  # For conditional branching: "true" or "false"


class WorkflowGraph(BaseModel):
    nodes: list[WorkflowNode] = []
    edges: list[WorkflowEdge] = []


class WorkflowCreate(BaseModel):
    name: str
    description: str = ""
    graph: WorkflowGraph = WorkflowGraph()
    schedule_cron: Optional[str] = None


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    graph: Optional[WorkflowGraph] = None
    schedule_cron: Optional[str] = None
    is_active: Optional[bool] = None


class WorkflowOut(BaseModel):
    id: str
    name: str
    description: str
    graph: dict
    is_active: bool
    schedule_cron: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Workflow Runs ---
class RunWorkflow(BaseModel):
    input_data: dict = {}


class WorkflowRunOut(BaseModel):
    id: str
    workflow_id: str
    status: str
    trigger: str
    input_data: dict
    output_data: Optional[Any]
    node_results: dict
    total_tokens: int
    total_cost_usd: float
    duration_ms: int
    error: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Usage ---
class UsageStats(BaseModel):
    runs_this_month: int
    total_tokens: int
    total_cost_usd: float
    plan: str
    runs_limit: int


# --- Templates ---
class TemplateInfo(BaseModel):
    id: str
    name: str
    description: str
    category: str
    agent_count: int
    graph: WorkflowGraph
