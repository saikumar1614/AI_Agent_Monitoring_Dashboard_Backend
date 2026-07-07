from pydantic import BaseModel, Field


class MetricValueResponse(BaseModel):
	metric: str
	value: float = Field(ge=0)


class DashboardKpiResponse(BaseModel):
	total_executions: int = Field(ge=0)
	success_rate: float = Field(ge=0, le=100)
	failure_rate: float = Field(ge=0, le=100)
	total_cost: float = Field(ge=0)
	total_tokens: int = Field(ge=0)
	average_latency: float = Field(ge=0)
