from sqlalchemy.orm import Session

from models.tool_usage import ToolUsage


def get_tool_usage_by_id(db: Session, tool_usage_id: int) -> ToolUsage | None:
	return db.query(ToolUsage).filter(ToolUsage.id == tool_usage_id).first()


def list_tool_usage(
	db: Session,
	skip: int = 0,
	limit: int = 20,
	execution_id: int | None = None,
	status: str | None = None,
) -> tuple[list[ToolUsage], int]:
	query = db.query(ToolUsage)
	if execution_id is not None:
		query = query.filter(ToolUsage.execution_id == execution_id)
	if status is not None:
		query = query.filter(ToolUsage.status == status)

	total = query.count()
	items = query.order_by(ToolUsage.created_at.desc()).offset(skip).limit(limit).all()
	return items, total


def create_tool_usage(
	db: Session,
	execution_id: int,
	tool_name: str,
	status: str,
	input_payload: dict | None,
	output_payload: dict | None,
	error_message: str | None,
	latency_ms: float | None,
	token_usage: int | None,
	cost_usd: float | None,
) -> ToolUsage:
	item = ToolUsage(
		execution_id=execution_id,
		tool_name=tool_name,
		status=status,
		input_payload=input_payload,
		output_payload=output_payload,
		error_message=error_message,
		latency_ms=latency_ms,
		token_usage=token_usage,
		cost_usd=cost_usd,
	)
	db.add(item)
	db.commit()
	db.refresh(item)
	return item


def update_tool_usage(
	db: Session,
	tool_usage_id: int,
	tool_name: str | None = None,
	status: str | None = None,
	input_payload: dict | None = None,
	output_payload: dict | None = None,
	error_message: str | None = None,
	latency_ms: float | None = None,
	token_usage: int | None = None,
	cost_usd: float | None = None,
) -> ToolUsage | None:
	item = get_tool_usage_by_id(db, tool_usage_id)
	if not item:
		return None

	if tool_name is not None:
		item.tool_name = tool_name
	if status is not None:
		item.status = status
	if input_payload is not None:
		item.input_payload = input_payload
	if output_payload is not None:
		item.output_payload = output_payload
	if error_message is not None:
		item.error_message = error_message
	if latency_ms is not None:
		item.latency_ms = latency_ms
	if token_usage is not None:
		item.token_usage = token_usage
	if cost_usd is not None:
		item.cost_usd = cost_usd

	db.commit()
	db.refresh(item)
	return item


def delete_tool_usage(db: Session, tool_usage_id: int) -> bool:
	item = get_tool_usage_by_id(db, tool_usage_id)
	if not item:
		return False
	db.delete(item)
	db.commit()
	return True
