from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ErrorCategory = Literal[
	"validation",
	"authentication",
	"authorization",
	"network",
	"timeout",
	"database",
	"external_service",
	"tool",
	"unknown",
]

ErrorSeverity = Literal["low", "medium", "high", "critical"]


class FailureCreateRequest(BaseModel):
	execution_id: int = Field(gt=0)
	error_code: str | None = Field(default=None, max_length=100)
	error_message: str = Field(min_length=1)
	error_category: ErrorCategory | None = None
	severity: ErrorSeverity = "medium"
	stack_trace: str | None = None
	context_data: dict[str, Any] | None = None


class FailureUpdateRequest(BaseModel):
	error_code: str | None = Field(default=None, max_length=100)
	error_message: str | None = Field(default=None, min_length=1)
	error_category: ErrorCategory | None = None
	severity: ErrorSeverity | None = None
	stack_trace: str | None = None
	context_data: dict[str, Any] | None = None


class FailureResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	execution_id: int
	error_code: str | None
	error_message: str
	error_category: ErrorCategory
	severity: ErrorSeverity
	stack_trace: str | None
	context_data: dict[str, Any] | None
	occurred_at: datetime
	created_at: datetime


class FailureListResponse(BaseModel):
	items: list[FailureResponse]
	total: int
	page: int
	page_size: int
