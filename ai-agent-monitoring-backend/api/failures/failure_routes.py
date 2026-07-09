from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from core.security import get_current_user
from database.session import get_db
from models.user import User
from schemas.failure_schema import (
	FailureCreateRequest,
	FailureListResponse,
	FailureResponse,
	FailureUpdateRequest,
)
from services.failure_service import (
	create_failure_service,
	delete_failure_service,
	get_failure_or_404,
	list_failures_service,
	update_failure_service,
)


router = APIRouter(prefix="/api/failures", tags=["Failures"])


@router.post("", response_model=FailureResponse, status_code=status.HTTP_201_CREATED)
def create_failure_endpoint(
	payload: FailureCreateRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> FailureResponse:
	item = create_failure_service(db, payload)
	return FailureResponse.model_validate(item)


@router.get("", response_model=FailureListResponse)
def list_failures_endpoint(
	skip: int = Query(0, ge=0),
	limit: int = Query(20, ge=1, le=100),
	execution_id: int | None = Query(None, gt=0),
	error_category: Literal[
		"validation",
		"authentication",
		"authorization",
		"network",
		"timeout",
		"database",
		"external_service",
		"tool",
		"unknown",
	]
	| None = None,
	severity: Literal["low", "medium", "high", "critical"] | None = None,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> FailureListResponse:
	items, total = list_failures_service(
		db,
		skip=skip,
		limit=limit,
		execution_id=execution_id,
		error_category=error_category,
		severity=severity,
	)
	return FailureListResponse(
		items=[FailureResponse.model_validate(item) for item in items],
		total=total,
		page=(skip // limit) + 1,
		page_size=limit,
	)


@router.get("/{failure_id}", response_model=FailureResponse)
def get_failure_endpoint(
	failure_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> FailureResponse:
	item = get_failure_or_404(db, failure_id)
	return FailureResponse.model_validate(item)


@router.put("/{failure_id}", response_model=FailureResponse)
def update_failure_endpoint(
	failure_id: int,
	payload: FailureUpdateRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> FailureResponse:
	item = update_failure_service(db, failure_id, payload)
	return FailureResponse.model_validate(item)


@router.delete("/{failure_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_failure_endpoint(
	failure_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> None:
	delete_failure_service(db, failure_id)
