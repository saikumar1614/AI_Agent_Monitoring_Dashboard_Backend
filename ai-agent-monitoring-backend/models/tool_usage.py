from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class ToolUsage(Base):
	__tablename__ = "tool_usage"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	execution_id: Mapped[int] = mapped_column(ForeignKey("executions.id"), nullable=False, index=True)
	tool_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
	status: Mapped[str] = mapped_column(String(32), nullable=False, default="succeeded", index=True)
	input_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
	output_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
	error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
	latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
	token_usage: Mapped[int | None] = mapped_column(Integer, nullable=True)
	cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
	updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
