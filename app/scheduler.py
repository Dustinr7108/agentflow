"""APScheduler for cron-based workflow execution."""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def start_scheduler() -> None:
    global _scheduler
    _scheduler = BackgroundScheduler(timezone="UTC")
    _scheduler.start()
    _reload_scheduled_workflows()
    logger.info("APScheduler started")


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped")


def get_scheduler() -> BackgroundScheduler | None:
    return _scheduler


def _reload_scheduled_workflows() -> None:
    """Load all active scheduled workflows from DB and register them."""
    try:
        from app.db import SessionLocal
        from app.models import Workflow
        db = SessionLocal()
        try:
            workflows = db.query(Workflow).filter(
                Workflow.schedule_cron.isnot(None),
                Workflow.is_active == True,
            ).all()
            for wf in workflows:
                schedule_workflow(wf.id, wf.schedule_cron)
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Could not load scheduled workflows: {e}")


def schedule_workflow(workflow_id: str, cron_expr: str) -> None:
    """Add or replace a scheduled job for a workflow."""
    global _scheduler
    if not _scheduler:
        return
    job_id = f"workflow_{workflow_id}"
    # Remove existing job if any
    if _scheduler.get_job(job_id):
        _scheduler.remove_job(job_id)
    try:
        parts = cron_expr.strip().split()
        if len(parts) != 5:
            logger.warning(f"Invalid cron expression for workflow {workflow_id}: {cron_expr}")
            return
        minute, hour, day, month, day_of_week = parts
        _scheduler.add_job(
            _run_scheduled_workflow,
            trigger=CronTrigger(
                minute=minute, hour=hour, day=day,
                month=month, day_of_week=day_of_week,
            ),
            id=job_id,
            args=[workflow_id],
            replace_existing=True,
            misfire_grace_time=300,
        )
        logger.info(f"Scheduled workflow {workflow_id} with cron: {cron_expr}")
    except Exception as e:
        logger.error(f"Failed to schedule workflow {workflow_id}: {e}")


def unschedule_workflow(workflow_id: str) -> None:
    global _scheduler
    if not _scheduler:
        return
    job_id = f"workflow_{workflow_id}"
    if _scheduler.get_job(job_id):
        _scheduler.remove_job(job_id)
        logger.info(f"Unscheduled workflow {workflow_id}")


def _run_scheduled_workflow(workflow_id: str) -> None:
    """Execute a workflow from the scheduler (runs in background thread)."""
    from app.db import SessionLocal
    from app.models import Workflow, WorkflowRun, AgentDef, UsageRecord
    from app.workflows.engine import WorkflowEngine
    from app.services.email_service import send_workflow_notification

    db = SessionLocal()
    try:
        wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not wf or not wf.is_active:
            return

        # Load agent defs
        agent_def_ids = [n.get("agent_def_id", "") for n in wf.graph.get("nodes", []) if n.get("agent_def_id")]
        agent_defs_db = db.query(AgentDef).filter(AgentDef.id.in_(agent_def_ids)).all() if agent_def_ids else []
        agent_defs = {ad.id: {"agent_type": ad.agent_type, "config": ad.config} for ad in agent_defs_db}

        run = WorkflowRun(
            workflow_id=wf.id,
            trigger="scheduled",
            input_data={},
            started_at=datetime.now(timezone.utc),
        )
        db.add(run)
        db.commit()

        engine = WorkflowEngine(graph=wf.graph, agent_defs=agent_defs)
        result = engine.run(input_data={})

        run.status = result["status"]
        run.output_data = result["output_data"]
        run.node_results = result["node_results"]
        run.total_tokens = result["total_tokens"]
        run.total_cost_usd = result["total_cost_usd"]
        run.duration_ms = result["duration_ms"]
        run.completed_at = datetime.now(timezone.utc)
        if result.get("failed_node"):
            run.error = f"Failed at node: {result['failed_node']}"

        usage = UsageRecord(
            user_id=wf.user_id,
            workflow_run_id=run.id,
            tokens_used=result["total_tokens"],
            cost_usd=result["total_cost_usd"],
        )
        db.add(usage)
        db.commit()

        logger.info(f"Scheduled run for workflow {workflow_id} completed: {result['status']}")

        # Send email notification if configured
        user = wf.user
        if user:
            import asyncio
            asyncio.run(send_workflow_notification(
                to_email=user.email,
                workflow_name=wf.name,
                status=result["status"],
                run_id=run.id,
                tokens=result["total_tokens"],
                cost=result["total_cost_usd"],
            ))

    except Exception as e:
        logger.error(f"Scheduled workflow {workflow_id} failed: {e}")
        if 'run' in dir() and run.id:
            run.status = "failed"
            run.error = str(e)
            run.completed_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()
