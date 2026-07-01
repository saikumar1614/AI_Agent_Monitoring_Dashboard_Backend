from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from core.security import get_current_user
from database.session import get_db
from models.user import User
from schemas.execution_schema import (
    ExecutionCreateRequest,
    ExecutionListResponse,
    ExecutionResponse,
    ExecutionUpdateRequest,
)
from services.execution_service import (
    create_execution_service,
    delete_execution_service,
    get_execution_or_404,
    list_executions_service,
    update_execution_service,
)


router = APIRouter(prefix="/api/executions", tags=["Executions"])


@router.post("", response_model=ExecutionResponse, status_code=status.HTTP_201_CREATED)
def create_execution(
    payload: ExecutionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExecutionResponse:
    execution = create_execution_service(db, payload)
    return ExecutionResponse.model_validate(execution)


@router.get("", response_model=ExecutionListResponse)
def list_executions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Literal["queued", "running", "succeeded", "failed", "cancelled", "timed_out"] | None = Query(None, alias="status"),
    agent_id: int | None = Query(None, gt=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExecutionListResponse:
    items, total = list_executions_service(
        db,
        skip=skip,
        limit=limit,
        status_filter=status_filter,
        agent_id=agent_id,
    )

    return ExecutionListResponse(
        items=[ExecutionResponse.model_validate(item) for item in items],
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
    )


@router.get("/{execution_id}", response_model=ExecutionResponse)
def get_execution(
    execution_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExecutionResponse:
    execution = get_execution_or_404(db, execution_id)
    return ExecutionResponse.model_validate(execution)


@router.put("/{execution_id}", response_model=ExecutionResponse)
def update_execution(
    execution_id: int,
    payload: ExecutionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExecutionResponse:
    execution = update_execution_service(db, execution_id, payload)
    return ExecutionResponse.model_validate(execution)


@router.delete("/{execution_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_execution(
    execution_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    delete_execution_service(db, execution_id)
