from datetime import date

from pydantic import BaseModel, Field


class LatencyBucketResponse(BaseModel):
	bucket: str
	average_latency_ms: float = Field(ge=0)
	sample_size: int = Field(ge=0)


class LatencyAggregationResponse(BaseModel):
	granularity: str
	start_date: date
	end_date: date
	total_buckets: int = Field(ge=0)
	items: list[LatencyBucketResponse]
