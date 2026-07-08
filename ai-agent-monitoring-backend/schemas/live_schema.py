from datetime import datetime

from pydantic import BaseModel, Field

from schemas.dashboard_schema import DashboardKpiResponse


class LiveMetricsResponse(DashboardKpiResponse):
    generated_at: datetime
    refresh_interval_seconds: int = Field(ge=1, le=300)