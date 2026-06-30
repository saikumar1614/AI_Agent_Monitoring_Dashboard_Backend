from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.agent import Agent
from repositories.agent_repository import (
    create_agent,
    delete_agent,
    get_agent_by_id,
    get_agent_by_name,
    list_agents,
    update_agent,
)
from schemas.agent_schema import AgentCreateRequest, AgentUpdateRequest


def get_agent_or_404(db: Session, agent_id: int) -> Agent:
    agent = get_agent_by_id(db, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found",
        )
    return agent


def create_agent_service(db: Session, payload: AgentCreateRequest) -> Agent:
    # Check for duplicate name
    existing = get_agent_by_name(db, payload.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Agent with name '{payload.name}' already exists",
        )
    
    return create_agent(
        db,
        name=payload.name,
        version=payload.version,
        description=payload.description,
        owner_team=payload.owner_team,
    )


def list_agents_service(db: Session, skip: int = 0, limit: int = 20, is_active: bool | None = None) -> tuple[list[Agent], int]:
    if skip < 0 or limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid pagination parameters",
        )
    return list_agents(db, skip=skip, limit=limit, is_active=is_active)


def update_agent_service(db: Session, agent_id: int, payload: AgentUpdateRequest) -> Agent:
    agent = get_agent_or_404(db, agent_id)
    
    # Check for name conflict if name is being updated
    if payload.name and payload.name != agent.name:
        existing = get_agent_by_name(db, payload.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Agent with name '{payload.name}' already exists",
            )
    
    updated = update_agent(
        db,
        agent_id,
        name=payload.name,
        version=payload.version,
        description=payload.description,
        owner_team=payload.owner_team,
        is_active=payload.is_active,
    )
    return updated


def delete_agent_service(db: Session, agent_id: int) -> bool:
    agent = get_agent_or_404(db, agent_id)
    return delete_agent(db, agent_id)
