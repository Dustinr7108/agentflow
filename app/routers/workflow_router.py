"""Workflow router - CRUD + execution."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User, Workflow, WorkflowRun, AgentDef, UsageRecord
from app.schemas import (
    WorkflowCreate, WorkflowUpdate, WorkflowOut,
    RunWorkflow, WorkflowRunOut,
)
from app.auth import get_current_user, check_usage_limit
from app.workflows.engine import WorkflowEngine

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("/", response_model=list[WorkflowOut])
def list_workflows(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    workflows = db.query(Workflow).filter(Workflow.user_id == user.id).order_by(Workflow.updated_at.desc()).all()
    return [WorkflowOut.model_validate(w) for w in workflows]


@router.post("/", response_model=WorkflowOut, status_code=201)
def create_workflow(data: WorkflowCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wf = Workflow(
        name=data.name,
        description=data.description,
        user_id=user.id,
        graph=data.graph.model_dump(),
        schedule_cron=data.schedule_cron,
    )
    db.add(wf)
    db.commit()
    db.refresh(wf)
    return WorkflowOut.model_validate(wf)


@router.get("/{workflow_id}", response_model=WorkflowOut)
def get_workflow(workflow_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id, Workflow.user_id == user.id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowOut.model_validate(wf)


@router.put("/{workflow_id}", response_model=WorkflowOut)
def update_workflow(workflow_id: str, data: WorkflowUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id, Workflow.user_id == user.id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if data.name is not None:
        wf.name = data.name
    if data.description is not None:
        wf.description = data.description
    if data.graph is not None:
        wf.graph = data.graph.model_dump()
    if data.schedule_cron is not None:
        wf.schedule_cron = data.schedule_cron
    if data.is_active is not None:
        wf.is_active = data.is_active

    wf.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(wf)
    return WorkflowOut.model_validate(wf)


@router.delete("/{workflow_id}", status_code=204)
def delete_workflow(workflow_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id, Workflow.user_id == user.id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    db.delete(wf)
    db.commit()


@router.post("/{workflow_id}/run", response_model=WorkflowRunOut)
def run_workflow(workflow_id: str, data: RunWorkflow, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Execute a workflow and return results."""
    check_usage_limit(user)

    wf = db.query(Workflow).filter(Workflow.id == workflow_id, Workflow.user_id == user.id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Load agent definitions for this workflow
    agent_def_ids = [n.get("agent_def_id", "") for n in wf.graph.get("nodes", []) if n.get("agent_def_id")]
    agent_defs_db = db.query(AgentDef).filter(AgentDef.id.in_(agent_def_ids)).all() if agent_def_ids else []
    agent_defs = {ad.id: {"agent_type": ad.agent_type, "config": ad.config} for ad in agent_defs_db}

    # Create run record
    run = WorkflowRun(
        workflow_id=wf.id,
        trigger="manual",
        input_data=data.input_data,
        started_at=datetime.now(timezone.utc),
    )
    db.add(run)
    db.commit()

    # Execute
    engine = WorkflowEngine(graph=wf.graph, agent_defs=agent_defs)
    result = engine.run(input_data=data.input_data)

    # Update run record
    run.status = result["status"]
    run.output_data = result["output_data"]
    run.node_results = result["node_results"]
    run.total_tokens = result["total_tokens"]
    run.total_cost_usd = result["total_cost_usd"]
    run.duration_ms = result["duration_ms"]
    run.completed_at = datetime.now(timezone.utc)
    if result.get("failed_node"):
        run.error = f"Failed at node: {result['failed_node']}"

    # Track usage
    user.runs_this_month += 1
    usage = UsageRecord(
        user_id=user.id,
        workflow_run_id=run.id,
        tokens_used=result["total_tokens"],
        cost_usd=result["total_cost_usd"],
    )
    db.add(usage)
    db.commit()
    db.refresh(run)

    return WorkflowRunOut.model_validate(run)


@router.get("/{workflow_id}/runs", response_model=list[WorkflowRunOut])
def list_runs(workflow_id: str, limit: int = 20, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id, Workflow.user_id == user.id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    runs = (
        db.query(WorkflowRun)
        .filter(WorkflowRun.workflow_id == workflow_id)
        .order_by(WorkflowRun.created_at.desc())
        .limit(limit)
        .all()
    )
    return [WorkflowRunOut.model_validate(r) for r in runs]
