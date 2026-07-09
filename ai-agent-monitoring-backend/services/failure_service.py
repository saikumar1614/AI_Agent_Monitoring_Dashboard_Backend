from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.execution import Execution
from models.failure import Failure
from repositories.failure_repository import (
	create_failure,
	delete_failure,
	get_failure_by_id,
	list_failures,
	update_failure,
)
from schemas.failure_schema import FailureCreateRequest, FailureUpdateRequest
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


def _categorize_error(message: str) -> str:
	normalized = message.lower()
	if any(k in normalized for k in ["validation", "invalid", "missing field", "schema"]):
		return "validation"
	if any(k in normalized for k in ["unauthorized", "authentication", "invalid token"]):
		return "authentication"
	if any(k in normalized for k in ["forbidden", "permission", "access denied"]):
		return "authorization"
	if any(k in normalized for k in ["timeout", "timed out"]):
		return "timeout"
	if any(k in normalized for k in ["connection", "network", "dns", "socket"]):
		return "network"
	if any(k in normalized for k in ["database", "sql", "constraint", "transaction"]):
		return "database"
	if any(k in normalized for k in ["api", "provider", "service unavailable", "third-party"]):
		return "external_service"
	if any(k in normalized for k in ["tool", "function", "plugin"]):
		return "tool"
	return "unknown"


def get_failure_or_404(db: Session, failure_id: int) -> Failure:
	item = get_failure_by_id(db, failure_id)
	if not item:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"Failure with ID {failure_id} not found",
		)
	return item


def create_failure_service(db: Session, payload: FailureCreateRequest) -> Failure:
	_validate_execution_exists(db, payload.execution_id)
	category = payload.error_category or _categorize_error(payload.error_message)

	item = create_failure(
		db,
		execution_id=payload.execution_id,
		error_code=payload.error_code,
		error_message=payload.error_message,
		error_category=category,
		severity=payload.severity,
		stack_trace=payload.stack_trace,
		context_data=payload.context_data,
	)

	LOGGER.error(
		"failure_logged execution_id=%s category=%s severity=%s code=%s message=%s",
		payload.execution_id,
		category,
		payload.severity,
		payload.error_code,
		payload.error_message,
	)
	export_event(
		"failure_logged",
		{
			"execution_id": payload.execution_id,
			"error_code": payload.error_code,
			"error_category": category,
			"severity": payload.severity,
			"error_message": payload.error_message,
		},
	)
	return item


def list_failures_service(
	db: Session,
	skip: int = 0,
	limit: int = 20,
	execution_id: int | None = None,
	error_category: str | None = None,
	severity: str | None = None,
) -> tuple[list[Failure], int]:
	if skip < 0 or limit < 1 or limit > 100:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid pagination parameters")
	if execution_id is not None:
		_validate_execution_exists(db, execution_id)
	return list_failures(
		db,
		skip=skip,
		limit=limit,
		execution_id=execution_id,
		error_category=error_category,
		severity=severity,
	)


def update_failure_service(db: Session, failure_id: int, payload: FailureUpdateRequest) -> Failure:
	current = get_failure_or_404(db, failure_id)

	message_for_category = payload.error_message or current.error_message
	category = payload.error_category or _categorize_error(message_for_category)

	item = update_failure(
		db,
		failure_id,
		error_code=payload.error_code,
		error_message=payload.error_message,
		error_category=category,
		severity=payload.severity,
		stack_trace=payload.stack_trace,
		context_data=payload.context_data,
	)
	if not item:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Failure not found")

	LOGGER.error(
		"failure_updated failure_id=%s category=%s severity=%s",
		failure_id,
		category,
		payload.severity or current.severity,
	)
	export_event(
		"failure_updated",
		{
			"failure_id": failure_id,
			"error_category": category,
			"severity": payload.severity or current.severity,
		},
	)
	return item


def delete_failure_service(db: Session, failure_id: int) -> bool:
	get_failure_or_404(db, failure_id)
	return delete_failure(db, failure_id)
