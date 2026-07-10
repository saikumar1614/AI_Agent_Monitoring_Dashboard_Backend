from datetime import date, datetime, time

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from repositories.analytics_repository import (
	get_daily_latency_aggregation,
	get_hourly_latency_aggregation,
)
from schemas.analytics_schema import LatencyAggregationResponse, LatencyBucketResponse


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
