"""Agent definition router - manage reusable agent templates."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User, AgentDef
from app.schemas import AgentDefCreate, AgentDefOut
from app.auth import get_current_user
from app.agents.registry import list_agent_types

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/types")
def get_agent_types():
    """List all available agent types."""
    return list_agent_types()


@router.get("/", response_model=list[AgentDefOut])
def list_agent_defs(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List builtin + user's custom agent definitions."""
    agents = (
        db.query(AgentDef)
        .filter((AgentDef.is_builtin == True) | (AgentDef.user_id == user.id))
        .order_by(AgentDef.name)
        .all()
    )
    return [AgentDefOut.model_validate(a) for a in agents]


@router.post("/", response_model=AgentDefOut, status_code=201)
def create_agent_def(data: AgentDefCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a custom agent definition."""
    agent = AgentDef(
        name=data.name,
        description=data.description,
        agent_type=data.agent_type,
        config=data.config,
        user_id=user.id,
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return AgentDefOut.model_validate(agent)


@router.put("/{agent_id}", response_model=AgentDefOut)
def update_agent_def(agent_id: str, data: AgentDefCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    agent = db.query(AgentDef).filter(AgentDef.id == agent_id, AgentDef.user_id == user.id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent.name = data.name
    agent.description = data.description
    agent.agent_type = data.agent_type
    agent.config = data.config
    db.commit()
    db.refresh(agent)
    return AgentDefOut.model_validate(agent)


@router.delete("/{agent_id}", status_code=204)
def delete_agent_def(agent_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    agent = db.query(AgentDef).filter(AgentDef.id == agent_id, AgentDef.user_id == user.id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    db.delete(agent)
    db.commit()
