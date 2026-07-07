from models.execution import Execution


SUCCESS_STATUSES = {"succeeded"}
FAILURE_STATUSES = {"failed", "cancelled", "timed_out"}


def _extract_cost(metadata: dict | None) -> float:
	if not metadata:
		return 0.0
	for key in ("cost_usd", "total_cost", "cost"):
		value = metadata.get(key)
		if isinstance(value, (int, float)):
			return float(value)
	return 0.0


def _extract_tokens(metadata: dict | None) -> int:
	if not metadata:
		return 0
	total_tokens = metadata.get("total_tokens")
	if isinstance(total_tokens, (int, float)):
		return int(total_tokens)

	prompt_tokens = metadata.get("prompt_tokens")
	completion_tokens = metadata.get("completion_tokens")
	if isinstance(prompt_tokens, (int, float)) and isinstance(completion_tokens, (int, float)):
		return int(prompt_tokens + completion_tokens)

	return 0


def _extract_latency_ms(execution: Execution) -> float:
	metadata = execution.execution_metadata or {}
	latency_ms = metadata.get("latency_ms")
	if isinstance(latency_ms, (int, float)):
		return float(latency_ms)

	if execution.started_at and execution.completed_at:
		delta_seconds = (execution.completed_at - execution.started_at).total_seconds()
		if delta_seconds >= 0:
			return delta_seconds * 1000

	return 0.0


def get_dashboard_kpis(db) -> dict[str, float | int]:
	executions = db.query(Execution).all()
	total_executions = len(executions)

	if total_executions == 0:
		return {
			"total_executions": 0,
			"success_rate": 0.0,
			"failure_rate": 0.0,
			"total_cost": 0.0,
			"total_tokens": 0,
			"average_latency": 0.0,
		}

	success_count = sum(1 for e in executions if e.status in SUCCESS_STATUSES)
	failure_count = sum(1 for e in executions if e.status in FAILURE_STATUSES)

	total_cost = sum(_extract_cost(e.execution_metadata) for e in executions)
	total_tokens = sum(_extract_tokens(e.execution_metadata) for e in executions)

	latencies = [
		_extract_latency_ms(e)
		for e in executions
		if _extract_latency_ms(e) > 0
	]
	average_latency = (sum(latencies) / len(latencies)) if latencies else 0.0

	return {
		"total_executions": total_executions,
		"success_rate": (success_count / total_executions) * 100,
		"failure_rate": (failure_count / total_executions) * 100,
		"total_cost": total_cost,
		"total_tokens": total_tokens,
		"average_latency": average_latency,
	}
