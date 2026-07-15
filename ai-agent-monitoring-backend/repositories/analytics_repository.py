from models.execution import Execution
from models.agent import Agent
from sqlalchemy.orm import load_only


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


def _get_executions_in_range(db, start_dt, end_dt) -> list[Execution]:
	return (
		db.query(Execution)
		.options(
			load_only(
				Execution.id,
				Execution.agent_id,
				Execution.status,
				Execution.created_at,
				Execution.started_at,
				Execution.completed_at,
				Execution.execution_metadata,
			)
		)
		.filter(Execution.created_at >= start_dt, Execution.created_at <= end_dt)
		.order_by(Execution.created_at.asc())
		.all()
	)


def _bucket_from_datetime(dt, granularity: str) -> str:
	if granularity == "hourly":
		return dt.strftime("%Y-%m-%d %H:00")
	return dt.strftime("%Y-%m-%d")


def _build_latency_aggregation(rows: list[Execution], granularity: str) -> list[dict]:
	agg: dict[str, dict] = {}
	for row in rows:
		bucket = _bucket_from_datetime(row.created_at, granularity)
		if bucket not in agg:
			agg[bucket] = {
				"bucket": bucket,
				"latency_sum": 0.0,
				"latency_count": 0,
				"sample_size": 0,
			}

		latency = _extract_latency_ms(row)
		if latency > 0:
			agg[bucket]["latency_sum"] += latency
			agg[bucket]["latency_count"] += 1

		agg[bucket]["sample_size"] += 1

	results: list[dict] = []
	for bucket in sorted(agg.keys()):
		latency_count = agg[bucket]["latency_count"]
		avg_latency = (agg[bucket]["latency_sum"] / latency_count) if latency_count else 0.0
		results.append(
			{
				"bucket": bucket,
				"average_latency_ms": avg_latency,
				"sample_size": agg[bucket]["sample_size"],
			}
		)

	return results


def _build_token_aggregation(rows: list[Execution], granularity: str) -> list[dict]:
	agg: dict[str, dict] = {}
	for row in rows:
		bucket = _bucket_from_datetime(row.created_at, granularity)
		if bucket not in agg:
			agg[bucket] = {
				"bucket": bucket,
				"prompt_tokens": 0,
				"completion_tokens": 0,
				"total_tokens": 0,
				"execution_count": 0,
			}

		metadata = row.execution_metadata
		agg[bucket]["prompt_tokens"] += _extract_prompt_tokens(metadata)
		agg[bucket]["completion_tokens"] += _extract_completion_tokens(metadata)
		agg[bucket]["total_tokens"] += _extract_tokens(metadata)
		agg[bucket]["execution_count"] += 1

	return [agg[key] for key in sorted(agg.keys())]


def _build_cost_trend_aggregation(rows: list[Execution], granularity: str) -> list[dict]:
	agg: dict[str, dict] = {}
	for row in rows:
		bucket = _bucket_from_datetime(row.created_at, granularity)
		if bucket not in agg:
			agg[bucket] = {
				"bucket": bucket,
				"total_cost_usd": 0.0,
				"execution_count": 0,
			}

		agg[bucket]["total_cost_usd"] += _extract_cost(row.execution_metadata)
		agg[bucket]["execution_count"] += 1

	return [agg[key] for key in sorted(agg.keys())]


def get_dashboard_kpis(db) -> dict[str, float | int]:
	executions = (
		db.query(Execution)
		.options(
			load_only(
				Execution.id,
				Execution.status,
				Execution.started_at,
				Execution.completed_at,
				Execution.execution_metadata,
			)
		)
		.all()
	)
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

	latencies = []
	for execution in executions:
		latency = _extract_latency_ms(execution)
		if latency > 0:
			latencies.append(latency)
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
	rows = _get_executions_in_range(db, start_dt, end_dt)
	return _build_latency_aggregation(rows, "hourly")


def get_daily_latency_aggregation(db, start_dt, end_dt) -> list[dict]:
	rows = _get_executions_in_range(db, start_dt, end_dt)
	return _build_latency_aggregation(rows, "daily")


def get_hourly_token_aggregation(db, start_dt, end_dt) -> list[dict]:
	rows = _get_executions_in_range(db, start_dt, end_dt)
	return _build_token_aggregation(rows, "hourly")


def get_daily_token_aggregation(db, start_dt, end_dt) -> list[dict]:
	rows = _get_executions_in_range(db, start_dt, end_dt)
	return _build_token_aggregation(rows, "daily")


def get_daily_cost_trend_aggregation(db, start_dt, end_dt) -> list[dict]:
	rows = _get_executions_in_range(db, start_dt, end_dt)
	return _build_cost_trend_aggregation(rows, "daily")


def get_cost_per_agent_aggregation(db, start_dt, end_dt) -> list[dict]:
	rows = _get_executions_in_range(db, start_dt, end_dt)
	agent_ids = {item.agent_id for item in rows}
	agent_name_map = {
		agent_id: agent_name
		for agent_id, agent_name in db.query(Agent.id, Agent.name).filter(Agent.id.in_(agent_ids)).all()
	}

	agg: dict[int, dict] = {}
	for item in rows:
		agent_id = int(item.agent_id)
		agent_name = agent_name_map.get(agent_id, f"Agent {agent_id}")
		if agent_id not in agg:
			agg[agent_id] = {
				"agent_id": agent_id,
				"agent_name": agent_name,
				"total_cost_usd": 0.0,
				"execution_count": 0,
			}

		agg[agent_id]["total_cost_usd"] += _extract_cost(item.execution_metadata)
		agg[agent_id]["execution_count"] += 1

	return [agg[key] for key in sorted(agg.keys(), key=lambda k: agg[k]["agent_name"])]
