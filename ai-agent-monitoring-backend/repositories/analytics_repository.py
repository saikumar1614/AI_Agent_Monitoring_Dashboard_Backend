from models.execution import Execution
from models.agent import Agent
from sqlalchemy import func


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


def _extract_prompt_tokens(metadata: dict | None) -> int:
	if not metadata:
		return 0
	value = metadata.get("prompt_tokens")
	if isinstance(value, (int, float)):
		return int(value)
	return 0


def _extract_completion_tokens(metadata: dict | None) -> int:
	if not metadata:
		return 0
	value = metadata.get("completion_tokens")
	if isinstance(value, (int, float)):
		return int(value)
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


def get_hourly_latency_aggregation(db, start_dt, end_dt) -> list[dict]:
	bucket_expr = func.strftime("%Y-%m-%d %H:00", Execution.created_at)
	rows = (
		db.query(bucket_expr.label("bucket"), func.count(Execution.id).label("sample_size"))
		.filter(Execution.created_at >= start_dt, Execution.created_at <= end_dt)
		.group_by(bucket_expr)
		.order_by(bucket_expr.asc())
		.all()
	)

	results: list[dict] = []
	for row in rows:
		latency_rows = (
			db.query(Execution)
			.filter(bucket_expr == row.bucket)
			.filter(Execution.created_at >= start_dt, Execution.created_at <= end_dt)
			.all()
		)
		latencies = [_extract_latency_ms(item) for item in latency_rows if _extract_latency_ms(item) > 0]
		avg_latency = (sum(latencies) / len(latencies)) if latencies else 0.0
		results.append(
			{
				"bucket": row.bucket,
				"average_latency_ms": avg_latency,
				"sample_size": int(row.sample_size),
			}
		)

	return results


def get_daily_latency_aggregation(db, start_dt, end_dt) -> list[dict]:
	bucket_expr = func.strftime("%Y-%m-%d", Execution.created_at)
	rows = (
		db.query(bucket_expr.label("bucket"), func.count(Execution.id).label("sample_size"))
		.filter(Execution.created_at >= start_dt, Execution.created_at <= end_dt)
		.group_by(bucket_expr)
		.order_by(bucket_expr.asc())
		.all()
	)

	results: list[dict] = []
	for row in rows:
		latency_rows = (
			db.query(Execution)
			.filter(bucket_expr == row.bucket)
			.filter(Execution.created_at >= start_dt, Execution.created_at <= end_dt)
			.all()
		)
		latencies = [_extract_latency_ms(item) for item in latency_rows if _extract_latency_ms(item) > 0]
		avg_latency = (sum(latencies) / len(latencies)) if latencies else 0.0
		results.append(
			{
				"bucket": row.bucket,
				"average_latency_ms": avg_latency,
				"sample_size": int(row.sample_size),
			}
		)

	return results


def get_hourly_token_aggregation(db, start_dt, end_dt) -> list[dict]:
	bucket_expr = func.strftime("%Y-%m-%d %H:00", Execution.created_at)
	rows = (
		db.query(bucket_expr.label("bucket"), Execution.execution_metadata)
		.filter(Execution.created_at >= start_dt, Execution.created_at <= end_dt)
		.order_by(bucket_expr.asc())
		.all()
	)

	agg: dict[str, dict] = {}
	for bucket, metadata in rows:
		if bucket not in agg:
			agg[bucket] = {
				"bucket": bucket,
				"prompt_tokens": 0,
				"completion_tokens": 0,
				"total_tokens": 0,
				"execution_count": 0,
			}

		agg[bucket]["prompt_tokens"] += _extract_prompt_tokens(metadata)
		agg[bucket]["completion_tokens"] += _extract_completion_tokens(metadata)
		agg[bucket]["total_tokens"] += _extract_tokens(metadata)
		agg[bucket]["execution_count"] += 1

	return [agg[key] for key in sorted(agg.keys())]


def get_daily_token_aggregation(db, start_dt, end_dt) -> list[dict]:
	bucket_expr = func.strftime("%Y-%m-%d", Execution.created_at)
	rows = (
		db.query(bucket_expr.label("bucket"), Execution.execution_metadata)
		.filter(Execution.created_at >= start_dt, Execution.created_at <= end_dt)
		.order_by(bucket_expr.asc())
		.all()
	)

	agg: dict[str, dict] = {}
	for bucket, metadata in rows:
		if bucket not in agg:
			agg[bucket] = {
				"bucket": bucket,
				"prompt_tokens": 0,
				"completion_tokens": 0,
				"total_tokens": 0,
				"execution_count": 0,
			}

		agg[bucket]["prompt_tokens"] += _extract_prompt_tokens(metadata)
		agg[bucket]["completion_tokens"] += _extract_completion_tokens(metadata)
		agg[bucket]["total_tokens"] += _extract_tokens(metadata)
		agg[bucket]["execution_count"] += 1

	return [agg[key] for key in sorted(agg.keys())]


def get_daily_cost_trend_aggregation(db, start_dt, end_dt) -> list[dict]:
	bucket_expr = func.strftime("%Y-%m-%d", Execution.created_at)
	rows = (
		db.query(bucket_expr.label("bucket"), Execution.execution_metadata)
		.filter(Execution.created_at >= start_dt, Execution.created_at <= end_dt)
		.order_by(bucket_expr.asc())
		.all()
	)

	agg: dict[str, dict] = {}
	for bucket, metadata in rows:
		if bucket not in agg:
			agg[bucket] = {
				"bucket": bucket,
				"total_cost_usd": 0.0,
				"execution_count": 0,
			}

		agg[bucket]["total_cost_usd"] += _extract_cost(metadata)
		agg[bucket]["execution_count"] += 1

	return [agg[key] for key in sorted(agg.keys())]


def get_cost_per_agent_aggregation(db, start_dt, end_dt) -> list[dict]:
	rows = (
		db.query(Execution.agent_id, Agent.name, Execution.execution_metadata)
		.join(Agent, Agent.id == Execution.agent_id)
		.filter(Execution.created_at >= start_dt, Execution.created_at <= end_dt)
		.order_by(Agent.name.asc())
		.all()
	)

	agg: dict[int, dict] = {}
	for agent_id, agent_name, metadata in rows:
		if agent_id not in agg:
			agg[agent_id] = {
				"agent_id": int(agent_id),
				"agent_name": agent_name,
				"total_cost_usd": 0.0,
				"execution_count": 0,
			}

		agg[agent_id]["total_cost_usd"] += _extract_cost(metadata)
		agg[agent_id]["execution_count"] += 1

	return [agg[key] for key in sorted(agg.keys(), key=lambda k: agg[k]["agent_name"])]
