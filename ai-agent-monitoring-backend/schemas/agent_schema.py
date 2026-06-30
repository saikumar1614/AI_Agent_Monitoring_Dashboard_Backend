from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AgentCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1024)
    version: str = Field(min_length=1, max_length=50)
    owner_team: str | None = Field(None, max_length=255)


class AgentUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1024)
    version: str | None = Field(None, min_length=1, max_length=50)
    owner_team: str | None = Field(None, max_length=255)
    is_active: bool | None = None


class AgentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    version: str
    owner_team: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AgentListResponse(BaseModel):
    items: list[AgentResponse]
    total: int
    page: int
    page_size: int
