"""Database models for AgentFlow."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


def utcnow():
    return datetime.now(timezone.utc)


def new_id():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), default="")
    hashed_password: Mapped[str] = mapped_column(String(255))
    plan: Mapped[str] = mapped_column(String(20), default="free")  # free, starter, pro, enterprise
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    runs_this_month: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    workflows: Mapped[list["Workflow"]] = relationship(back_populates="user")


class AgentDef(Base):
    """Reusable agent definitions - templates users can drag into workflows."""
    __tablename__ = "agent_defs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, default="")
    agent_type: Mapped[str] = mapped_column(String(50))  # llm, web_search, code_exec, data_transform, api_call, conditional
    config: Mapped[dict] = mapped_column(JSON, default=dict)  # model, prompt template, tools, etc
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Workflow(Base):
    """A workflow is a directed graph of agent nodes."""
    __tablename__ = "workflows"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    # The workflow graph: list of nodes + edges
    # nodes: [{id, agent_def_id, position: {x,y}, config_overrides: {}}]
    # edges: [{source_id, target_id, condition: optional}]
    graph: Mapped[dict] = mapped_column(JSON, default=lambda: {"nodes": [], "edges": []})
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    schedule_cron: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g. "0 8 * * *"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    user: Mapped["User"] = relationship(back_populates="workflows")
    runs: Mapped[list["WorkflowRun"]] = relationship(back_populates="workflow")


class WorkflowRun(Base):
    """A single execution of a workflow."""
    __tablename__ = "workflow_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    workflow_id: Mapped[str] = mapped_column(String(36), ForeignKey("workflows.id"))
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, running, completed, failed
    trigger: Mapped[str] = mapped_column(String(20), default="manual")  # manual, scheduled, webhook
    input_data: Mapped[dict] = mapped_column(JSON, default=dict)
    output_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Per-node results: {node_id: {status, output, duration_ms, tokens_used}}
    node_results: Mapped[dict] = mapped_column(JSON, default=dict)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    workflow: Mapped["Workflow"] = relationship(back_populates="runs")


class UsageRecord(Base):
    """Track usage for billing."""
    __tablename__ = "usage_records"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    workflow_run_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("workflow_runs.id"), nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
