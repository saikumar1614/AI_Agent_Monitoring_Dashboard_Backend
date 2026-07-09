from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from core.security import get_current_user
from database.session import get_db
from models.user import User
from schemas.tool_usage_schema import (
	ToolUsageCreateRequest,
	ToolUsageListResponse,
	ToolUsageResponse,
	ToolUsageUpdateRequest,
)
from services.tool_usage_service import (
	create_tool_usage_service,
	delete_tool_usage_service,
	get_tool_usage_or_404,
	list_tool_usage_service,
	update_tool_usage_service,
)


router = APIRouter(prefix="/api/tool-usage", tags=["Tool Usage"])


@router.post("", response_model=ToolUsageResponse, status_code=status.HTTP_201_CREATED)
def create_tool_usage_endpoint(
	payload: ToolUsageCreateRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> ToolUsageResponse:
	item = create_tool_usage_service(db, payload)
	return ToolUsageResponse.model_validate(item)


@router.get("", response_model=ToolUsageListResponse)
def list_tool_usage_endpoint(
	skip: int = Query(0, ge=0),
	limit: int = Query(20, ge=1, le=100),
	execution_id: int | None = Query(None, gt=0),
	status_filter: Literal["succeeded", "failed", "timeout", "cancelled"] | None = Query(None, alias="status"),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> ToolUsageListResponse:
	items, total = list_tool_usage_service(
		db,
		skip=skip,
		limit=limit,
		execution_id=execution_id,
		status_filter=status_filter,
	)
	return ToolUsageListResponse(
		items=[ToolUsageResponse.model_validate(item) for item in items],
		total=total,
		page=(skip // limit) + 1,
		page_size=limit,
	)


@router.get("/{tool_usage_id}", response_model=ToolUsageResponse)
def get_tool_usage_endpoint(
	tool_usage_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> ToolUsageResponse:
	item = get_tool_usage_or_404(db, tool_usage_id)
	return ToolUsageResponse.model_validate(item)


@router.put("/{tool_usage_id}", response_model=ToolUsageResponse)
def update_tool_usage_endpoint(
	tool_usage_id: int,
	payload: ToolUsageUpdateRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> ToolUsageResponse:
	item = update_tool_usage_service(db, tool_usage_id, payload)
	return ToolUsageResponse.model_validate(item)


@router.delete("/{tool_usage_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tool_usage_endpoint(
	tool_usage_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> None:
	delete_tool_usage_service(db, tool_usage_id)
