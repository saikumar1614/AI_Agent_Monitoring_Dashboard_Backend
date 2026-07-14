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


class TokenBucketResponse(BaseModel):
	bucket: str
	prompt_tokens: int = Field(ge=0)
	completion_tokens: int = Field(ge=0)
	total_tokens: int = Field(ge=0)
	execution_count: int = Field(ge=0)


class TokenAggregationResponse(BaseModel):
	granularity: str
	start_date: date
	end_date: date
	total_prompt_tokens: int = Field(ge=0)
	total_completion_tokens: int = Field(ge=0)
	total_tokens: int = Field(ge=0)
	total_buckets: int = Field(ge=0)
	items: list[TokenBucketResponse]


class CostTrendBucketResponse(BaseModel):
	bucket: str
	total_cost_usd: float = Field(ge=0)
	execution_count: int = Field(ge=0)


class CostTrendAggregationResponse(BaseModel):
	granularity: str
	start_date: date
	end_date: date
	total_cost_usd: float = Field(ge=0)
	total_buckets: int = Field(ge=0)
	items: list[CostTrendBucketResponse]


class CostPerAgentBucketResponse(BaseModel):
	agent_id: int = Field(ge=1)
	agent_name: str
	total_cost_usd: float = Field(ge=0)
	execution_count: int = Field(ge=0)


class CostPerAgentAggregationResponse(BaseModel):
	start_date: date
	end_date: date
	total_cost_usd: float = Field(ge=0)
	total_agents: int = Field(ge=0)
	items: list[CostPerAgentBucketResponse]
