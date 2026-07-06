from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator


class LangfuseCompletionTrackRequest(BaseModel):
    trace_name: str = Field(default="llm-completion", min_length=1, max_length=120)
    generation_name: str = Field(default="completion", min_length=1, max_length=120)
    session_id: str | None = Field(default=None, max_length=120)
    model: str = Field(min_length=1, max_length=120)
    prompt: str = Field(min_length=1)
    completion: str = Field(min_length=1)
    prompt_tokens: int | None = Field(default=None, ge=0)
    completion_tokens: int | None = Field(default=None, ge=0)
    total_tokens: int | None = Field(default=None, ge=0)
    cost_usd: float | None = Field(default=None, ge=0)
    latency_ms: float | None = Field(default=None, ge=0)
    started_at: datetime | None = None
    ended_at: datetime | None = None
    metadata: dict[str, Any] | None = None

    @model_validator(mode="after")
    def validate_times(self) -> "LangfuseCompletionTrackRequest":
        if self.started_at and self.ended_at and self.ended_at < self.started_at:
            raise ValueError("ended_at must be greater than or equal to started_at")
        return self


class LangfuseTrackResponse(BaseModel):
    tracked: bool
    trace_id: str | None
    generation_id: str | None
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    latency_ms: float | None
    cost_usd: float | None
    message: str
