from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ToolStatus = Literal["succeeded", "failed", "timeout", "cancelled"]


class ToolUsageCreateRequest(BaseModel):
	execution_id: int = Field(gt=0)
	tool_name: str = Field(min_length=1, max_length=120)
	status: ToolStatus = "succeeded"
	input_payload: dict[str, Any] | None = None
	output_payload: dict[str, Any] | None = None
	error_message: str | None = None
	latency_ms: float | None = Field(default=None, ge=0)
	token_usage: int | None = Field(default=None, ge=0)
	cost_usd: float | None = Field(default=None, ge=0)


class ToolUsageUpdateRequest(BaseModel):
	tool_name: str | None = Field(default=None, min_length=1, max_length=120)
	status: ToolStatus | None = None
	input_payload: dict[str, Any] | None = None
	output_payload: dict[str, Any] | None = None
	error_message: str | None = None
	latency_ms: float | None = Field(default=None, ge=0)
	token_usage: int | None = Field(default=None, ge=0)
	cost_usd: float | None = Field(default=None, ge=0)


class ToolUsageResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	execution_id: int
	tool_name: str
	status: ToolStatus
	input_payload: dict[str, Any] | None
	output_payload: dict[str, Any] | None
	error_message: str | None
	latency_ms: float | None
	token_usage: int | None
	cost_usd: float | None
	created_at: datetime
	updated_at: datetime


class ToolUsageListResponse(BaseModel):
	items: list[ToolUsageResponse]
	total: int
	page: int
	page_size: int
