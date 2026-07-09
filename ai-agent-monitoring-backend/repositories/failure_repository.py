from sqlalchemy.orm import Session

from models.failure import Failure


def get_failure_by_id(db: Session, failure_id: int) -> Failure | None:
	return db.query(Failure).filter(Failure.id == failure_id).first()


def list_failures(
	db: Session,
	skip: int = 0,
	limit: int = 20,
	execution_id: int | None = None,
	error_category: str | None = None,
	severity: str | None = None,
) -> tuple[list[Failure], int]:
	query = db.query(Failure)
	if execution_id is not None:
		query = query.filter(Failure.execution_id == execution_id)
	if error_category is not None:
		query = query.filter(Failure.error_category == error_category)
	if severity is not None:
		query = query.filter(Failure.severity == severity)

	total = query.count()
	items = query.order_by(Failure.occurred_at.desc()).offset(skip).limit(limit).all()
	return items, total


def create_failure(
	db: Session,
	execution_id: int,
	error_code: str | None,
	error_message: str,
	error_category: str,
	severity: str,
	stack_trace: str | None,
	context_data: dict | None,
) -> Failure:
	item = Failure(
		execution_id=execution_id,
		error_code=error_code,
		error_message=error_message,
		error_category=error_category,
		severity=severity,
		stack_trace=stack_trace,
		context_data=context_data,
	)
	db.add(item)
	db.commit()
	db.refresh(item)
	return item


def update_failure(
	db: Session,
	failure_id: int,
	error_code: str | None = None,
	error_message: str | None = None,
	error_category: str | None = None,
	severity: str | None = None,
	stack_trace: str | None = None,
	context_data: dict | None = None,
) -> Failure | None:
	item = get_failure_by_id(db, failure_id)
	if not item:
		return None

	if error_code is not None:
		item.error_code = error_code
	if error_message is not None:
		item.error_message = error_message
	if error_category is not None:
		item.error_category = error_category
	if severity is not None:
		item.severity = severity
	if stack_trace is not None:
		item.stack_trace = stack_trace
	if context_data is not None:
		item.context_data = context_data

	db.commit()
	db.refresh(item)
	return item


def delete_failure(db: Session, failure_id: int) -> bool:
	item = get_failure_by_id(db, failure_id)
	if not item:
		return False
	db.delete(item)
	db.commit()
	return True
