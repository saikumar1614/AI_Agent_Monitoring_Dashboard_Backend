from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.agent import Agent
from models.execution import Execution
from repositories.execution_repository import (
    create_execution,
    delete_execution,
    get_execution_by_id,
    list_executions,
    update_execution,
)
from schemas.execution_schema import ExecutionCreateRequest, ExecutionUpdateRequest

TERMINAL_STATUSES = {"succeeded", "failed", "cancelled", "timed_out"}


def get_execution_or_404(db: Session, execution_id: int) -> Execution:
    execution = get_execution_by_id(db, execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution with ID {execution_id} not found",
        )
    return execution


def validate_agent_exists(db: Session, agent_id: int) -> None:
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found",
        )


def create_execution_service(db: Session, payload: ExecutionCreateRequest) -> Execution:
    validate_agent_exists(db, payload.agent_id)

    started_at = payload.started_at
    completed_at = payload.completed_at

    if payload.status == "running" and started_at is None:
        started_at = datetime.utcnow()

    if payload.status in TERMINAL_STATUSES and completed_at is None:
        completed_at = datetime.utcnow()

    if started_at and completed_at and completed_at < started_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="completed_at must be greater than or equal to started_at",
        )

    return create_execution(
        db,
        agent_id=payload.agent_id,
        status=payload.status,
        execution_metadata=payload.execution_metadata,
        started_at=started_at,
        completed_at=completed_at,
    )


def list_executions_service(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    status_filter: str | None = None,
    agent_id: int | None = None,
) -> tuple[list[Execution], int]:
    if skip < 0 or limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid pagination parameters",
        )

    if agent_id is not None:
        validate_agent_exists(db, agent_id)

    return list_executions(db, skip=skip, limit=limit, status=status_filter, agent_id=agent_id)


def update_execution_service(db: Session, execution_id: int, payload: ExecutionUpdateRequest) -> Execution:
    current = get_execution_or_404(db, execution_id)

    status_value = payload.status if payload.status is not None else current.status
    started_at = payload.started_at if payload.started_at is not None else current.started_at
    completed_at = payload.completed_at if payload.completed_at is not None else current.completed_at

    if status_value == "running" and started_at is None:
        started_at = datetime.utcnow()

    if status_value in TERMINAL_STATUSES and completed_at is None:
        completed_at = datetime.utcnow()

    if started_at and completed_at and completed_at < started_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="completed_at must be greater than or equal to started_at",
        )

    updated = update_execution(
        db,
        execution_id,
        status=payload.status,
        execution_metadata=payload.execution_metadata,
        started_at=started_at,
        completed_at=completed_at,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution with ID {execution_id} not found",
        )

    return updated


def delete_execution_service(db: Session, execution_id: int) -> bool:
    get_execution_or_404(db, execution_id)
    return delete_execution(db, execution_id)
