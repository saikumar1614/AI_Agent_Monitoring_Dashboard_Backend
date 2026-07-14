from datetime import date, datetime, time

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from repositories.analytics_repository import (
	get_cost_per_agent_aggregation,
	get_daily_cost_trend_aggregation,
	get_daily_token_aggregation,
	get_daily_latency_aggregation,
	get_hourly_token_aggregation,
	get_hourly_latency_aggregation,
)
from schemas.analytics_schema import (
	CostPerAgentAggregationResponse,
	CostPerAgentBucketResponse,
	CostTrendAggregationResponse,
	CostTrendBucketResponse,
	LatencyAggregationResponse,
	LatencyBucketResponse,
	TokenAggregationResponse,
	TokenBucketResponse,
)


def _to_datetime_range(start_date: date, end_date: date) -> tuple[datetime, datetime]:
	if end_date < start_date:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="end_date must be greater than or equal to start_date",
		)

	start_dt = datetime.combine(start_date, time.min)
	end_dt = datetime.combine(end_date, time.max)
	return start_dt, end_dt


def get_hourly_latency_service(db: Session, start_date: date, end_date: date) -> LatencyAggregationResponse:
	start_dt, end_dt = _to_datetime_range(start_date, end_date)
	rows = get_hourly_latency_aggregation(db, start_dt, end_dt)
	items = [
		LatencyBucketResponse(
			bucket=row["bucket"],
			average_latency_ms=round(float(row["average_latency_ms"]), 2),
			sample_size=int(row["sample_size"]),
		)
		for row in rows
	]
	return LatencyAggregationResponse(
		granularity="hourly",
		start_date=start_date,
		end_date=end_date,
		total_buckets=len(items),
		items=items,
	)


def get_daily_latency_service(db: Session, start_date: date, end_date: date) -> LatencyAggregationResponse:
	start_dt, end_dt = _to_datetime_range(start_date, end_date)
	rows = get_daily_latency_aggregation(db, start_dt, end_dt)
	items = [
		LatencyBucketResponse(
			bucket=row["bucket"],
			average_latency_ms=round(float(row["average_latency_ms"]), 2),
			sample_size=int(row["sample_size"]),
		)
		for row in rows
	]
	return LatencyAggregationResponse(
		granularity="daily",
		start_date=start_date,
		end_date=end_date,
		total_buckets=len(items),
		items=items,
	)


def get_hourly_token_service(db: Session, start_date: date, end_date: date) -> TokenAggregationResponse:
	start_dt, end_dt = _to_datetime_range(start_date, end_date)
	rows = get_hourly_token_aggregation(db, start_dt, end_dt)
	items = [
		TokenBucketResponse(
			bucket=row["bucket"],
			prompt_tokens=int(row["prompt_tokens"]),
			completion_tokens=int(row["completion_tokens"]),
			total_tokens=int(row["total_tokens"]),
			execution_count=int(row["execution_count"]),
		)
		for row in rows
	]

	return TokenAggregationResponse(
		granularity="hourly",
		start_date=start_date,
		end_date=end_date,
		total_prompt_tokens=sum(item.prompt_tokens for item in items),
		total_completion_tokens=sum(item.completion_tokens for item in items),
		total_tokens=sum(item.total_tokens for item in items),
		total_buckets=len(items),
		items=items,
	)


def get_daily_token_service(db: Session, start_date: date, end_date: date) -> TokenAggregationResponse:
	start_dt, end_dt = _to_datetime_range(start_date, end_date)
	rows = get_daily_token_aggregation(db, start_dt, end_dt)
	items = [
		TokenBucketResponse(
			bucket=row["bucket"],
			prompt_tokens=int(row["prompt_tokens"]),
			completion_tokens=int(row["completion_tokens"]),
			total_tokens=int(row["total_tokens"]),
			execution_count=int(row["execution_count"]),
		)
		for row in rows
	]

	return TokenAggregationResponse(
		granularity="daily",
		start_date=start_date,
		end_date=end_date,
		total_prompt_tokens=sum(item.prompt_tokens for item in items),
		total_completion_tokens=sum(item.completion_tokens for item in items),
		total_tokens=sum(item.total_tokens for item in items),
		total_buckets=len(items),
		items=items,
	)


def get_daily_cost_trend_service(db: Session, start_date: date, end_date: date) -> CostTrendAggregationResponse:
	start_dt, end_dt = _to_datetime_range(start_date, end_date)
	rows = get_daily_cost_trend_aggregation(db, start_dt, end_dt)
	items = [
		CostTrendBucketResponse(
			bucket=row["bucket"],
			total_cost_usd=round(float(row["total_cost_usd"]), 6),
			execution_count=int(row["execution_count"]),
		)
		for row in rows
	]

	return CostTrendAggregationResponse(
		granularity="daily",
		start_date=start_date,
		end_date=end_date,
		total_cost_usd=round(sum(item.total_cost_usd for item in items), 6),
		total_buckets=len(items),
		items=items,
	)


def get_cost_per_agent_service(db: Session, start_date: date, end_date: date) -> CostPerAgentAggregationResponse:
	start_dt, end_dt = _to_datetime_range(start_date, end_date)
	rows = get_cost_per_agent_aggregation(db, start_dt, end_dt)
	items = [
		CostPerAgentBucketResponse(
			agent_id=int(row["agent_id"]),
			agent_name=row["agent_name"],
			total_cost_usd=round(float(row["total_cost_usd"]), 6),
			execution_count=int(row["execution_count"]),
		)
		for row in rows
	]

	return CostPerAgentAggregationResponse(
		start_date=start_date,
		end_date=end_date,
		total_cost_usd=round(sum(item.total_cost_usd for item in items), 6),
		total_agents=len(items),
		items=items,
	)
