from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Failure(Base):
	__tablename__ = "failures"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	execution_id: Mapped[int] = mapped_column(ForeignKey("executions.id"), nullable=False, index=True)
	error_code: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
	error_message: Mapped[str] = mapped_column(Text, nullable=False)
	error_category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
	severity: Mapped[str] = mapped_column(String(20), nullable=False, default="medium", index=True)
	stack_trace: Mapped[str | None] = mapped_column(Text, nullable=True)
	context_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
	occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
