from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from core.security import get_current_user
from database.session import get_db
from models.user import User
from schemas.agent_schema import AgentCreateRequest, AgentListResponse, AgentResponse, AgentUpdateRequest
from services.agent_service import (
    create_agent_service,
    delete_agent_service,
    get_agent_or_404,
    list_agents_service,
    update_agent_service,
)


router = APIRouter(prefix="/api/agents", tags=["Agents"])


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def create_agent(
    payload: AgentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentResponse:
    agent = create_agent_service(db, payload)
    return AgentResponse.model_validate(agent)


@router.get("", response_model=AgentListResponse)
def list_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_active: bool | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentListResponse:
    agents, total = list_agents_service(db, skip=skip, limit=limit, is_active=is_active)
    return AgentListResponse(
        items=[AgentResponse.model_validate(a) for a in agents],
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
    )


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentResponse:
    agent = get_agent_or_404(db, agent_id)
    return AgentResponse.model_validate(agent)


@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(
    agent_id: int,
    payload: AgentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentResponse:
    agent = update_agent_service(db, agent_id, payload)
    return AgentResponse.model_validate(agent)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    delete_agent_service(db, agent_id)
