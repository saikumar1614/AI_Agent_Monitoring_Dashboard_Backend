from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ExecutionStatus = Literal[
    "queued",
    "running",
    "succeeded",
    "failed",
    "cancelled",
    "timed_out",
]


class ExecutionCreateRequest(BaseModel):
    agent_id: int = Field(gt=0)
    status: ExecutionStatus = "queued"
    execution_metadata: dict[str, Any] | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    @model_validator(mode="after")
    def validate_timestamps(self) -> "ExecutionCreateRequest":
        if self.started_at and self.completed_at and self.completed_at < self.started_at:
            raise ValueError("completed_at must be greater than or equal to started_at")
        return self


class ExecutionUpdateRequest(BaseModel):
    status: ExecutionStatus | None = None
    execution_metadata: dict[str, Any] | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    @model_validator(mode="after")
    def validate_timestamps(self) -> "ExecutionUpdateRequest":
        if self.started_at and self.completed_at and self.completed_at < self.started_at:
            raise ValueError("completed_at must be greater than or equal to started_at")
        return self


class ExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    agent_id: int
    status: ExecutionStatus
    execution_metadata: dict[str, Any] | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ExecutionListResponse(BaseModel):
    items: list[ExecutionResponse]
    total: int
    page: int
    page_size: int
