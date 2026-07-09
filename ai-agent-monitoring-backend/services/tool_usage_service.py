from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.execution import Execution
from models.tool_usage import ToolUsage
from repositories.tool_usage_repository import (
	create_tool_usage,
	delete_tool_usage,
	get_tool_usage_by_id,
	list_tool_usage,
	update_tool_usage,
)
from schemas.tool_usage_schema import ToolUsageCreateRequest, ToolUsageUpdateRequest
from telemetry.logging import get_logger
from services.telemetry_service import export_event

LOGGER = get_logger(__name__)


def _validate_execution_exists(db: Session, execution_id: int) -> None:
	execution = db.query(Execution).filter(Execution.id == execution_id).first()
	if not execution:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"Execution with ID {execution_id} not found",
		)


def get_tool_usage_or_404(db: Session, tool_usage_id: int) -> ToolUsage:
	item = get_tool_usage_by_id(db, tool_usage_id)
	if not item:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"Tool usage with ID {tool_usage_id} not found",
		)
	return item


def create_tool_usage_service(db: Session, payload: ToolUsageCreateRequest) -> ToolUsage:
	_validate_execution_exists(db, payload.execution_id)

	item = create_tool_usage(
		db,
		execution_id=payload.execution_id,
		tool_name=payload.tool_name,
		status=payload.status,
		input_payload=payload.input_payload,
		output_payload=payload.output_payload,
		error_message=payload.error_message,
		latency_ms=payload.latency_ms,
		token_usage=payload.token_usage,
		cost_usd=payload.cost_usd,
	)

	if payload.status != "succeeded" or payload.error_message:
		LOGGER.error(
			"tool_usage_error execution_id=%s tool_name=%s status=%s error=%s",
			payload.execution_id,
			payload.tool_name,
			payload.status,
			payload.error_message,
		)
		export_event(
			"tool_usage_error",
			{
				"execution_id": payload.execution_id,
				"tool_name": payload.tool_name,
				"status": payload.status,
				"error_message": payload.error_message,
			},
		)

	return item


def list_tool_usage_service(
	db: Session,
	skip: int = 0,
	limit: int = 20,
	execution_id: int | None = None,
	status_filter: str | None = None,
) -> tuple[list[ToolUsage], int]:
	if skip < 0 or limit < 1 or limit > 100:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid pagination parameters")
	if execution_id is not None:
		_validate_execution_exists(db, execution_id)
	return list_tool_usage(db, skip=skip, limit=limit, execution_id=execution_id, status=status_filter)


def update_tool_usage_service(db: Session, tool_usage_id: int, payload: ToolUsageUpdateRequest) -> ToolUsage:
	get_tool_usage_or_404(db, tool_usage_id)

	item = update_tool_usage(
		db,
		tool_usage_id,
		tool_name=payload.tool_name,
		status=payload.status,
		input_payload=payload.input_payload,
		output_payload=payload.output_payload,
		error_message=payload.error_message,
		latency_ms=payload.latency_ms,
		token_usage=payload.token_usage,
		cost_usd=payload.cost_usd,
	)
	if not item:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool usage not found")

	if payload.status in {"failed", "timeout", "cancelled"} or payload.error_message:
		LOGGER.error(
			"tool_usage_error_update tool_usage_id=%s status=%s error=%s",
			tool_usage_id,
			payload.status,
			payload.error_message,
		)
		export_event(
			"tool_usage_error_update",
			{
				"tool_usage_id": tool_usage_id,
				"status": payload.status,
				"error_message": payload.error_message,
			},
		)
	return item


def delete_tool_usage_service(db: Session, tool_usage_id: int) -> bool:
	get_tool_usage_or_404(db, tool_usage_id)
	return delete_tool_usage(db, tool_usage_id)
