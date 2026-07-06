from datetime import datetime
from typing import Any

from core.config import settings
from schemas.langfuse_schema import LangfuseCompletionTrackRequest, LangfuseTrackResponse
from telemetry.logging import get_logger

LOGGER = get_logger(__name__)


class LangfuseTracker:
    def __init__(self) -> None:
        self._client = None

        if not settings.LANGFUSE_ENABLED:
            return

        if not settings.LANGFUSE_PUBLIC_KEY or not settings.LANGFUSE_SECRET_KEY:
            LOGGER.warning("Langfuse keys are missing. Tracking will be skipped.")
            return

        try:
            from langfuse import Langfuse

            self._client = Langfuse(
                public_key=settings.LANGFUSE_PUBLIC_KEY,
                secret_key=settings.LANGFUSE_SECRET_KEY,
                host=settings.LANGFUSE_HOST,
            )
        except ImportError:
            LOGGER.warning("langfuse package is not installed. Tracking will be skipped.")

    @property
    def is_ready(self) -> bool:
        return self._client is not None

    def track_completion(
        self,
        payload: LangfuseCompletionTrackRequest,
        user_id: str | None = None,
    ) -> LangfuseTrackResponse:
        prompt_tokens = payload.prompt_tokens
        completion_tokens = payload.completion_tokens

        total_tokens = payload.total_tokens
        if total_tokens is None and prompt_tokens is not None and completion_tokens is not None:
            total_tokens = prompt_tokens + completion_tokens

        latency_ms = payload.latency_ms
        if latency_ms is None and payload.started_at and payload.ended_at:
            latency_ms = (payload.ended_at - payload.started_at).total_seconds() * 1000

        metadata: dict[str, Any] = dict(payload.metadata or {})
        if latency_ms is not None:
            metadata["latency_ms"] = latency_ms
        if payload.cost_usd is not None:
            metadata["cost_usd"] = payload.cost_usd

        if not self.is_ready:
            LOGGER.info(
                "Langfuse tracking skipped model=%s prompt_tokens=%s completion_tokens=%s total_tokens=%s latency_ms=%s cost_usd=%s",
                payload.model,
                prompt_tokens,
                completion_tokens,
                total_tokens,
                latency_ms,
                payload.cost_usd,
            )
            return LangfuseTrackResponse(
                tracked=False,
                trace_id=None,
                generation_id=None,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                latency_ms=latency_ms,
                cost_usd=payload.cost_usd,
                message="Langfuse not configured; tracking logged locally",
            )

        trace_id: str | None = None
        generation_id: str | None = None

        usage: dict[str, int] = {}
        if prompt_tokens is not None:
            usage["prompt_tokens"] = prompt_tokens
        if completion_tokens is not None:
            usage["completion_tokens"] = completion_tokens
        if total_tokens is not None:
            usage["total_tokens"] = total_tokens

        try:
            trace = self._client.trace(
                name=payload.trace_name,
                user_id=user_id,
                session_id=payload.session_id,
                metadata={"source": "backend", **metadata},
            )
            trace_id = getattr(trace, "id", None)

            generation = trace.generation(
                name=payload.generation_name,
                model=payload.model,
                input=payload.prompt,
                output=payload.completion,
                usage=usage if usage else None,
                metadata=metadata if metadata else None,
                start_time=payload.started_at,
                end_time=payload.ended_at,
            )
            generation_id = getattr(generation, "id", None)

            self._client.flush()

            return LangfuseTrackResponse(
                tracked=True,
                trace_id=trace_id,
                generation_id=generation_id,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                latency_ms=latency_ms,
                cost_usd=payload.cost_usd,
                message="Tracked in Langfuse",
            )
        except Exception as exc:
            LOGGER.exception("Failed to send event to Langfuse: %s", exc)
            return LangfuseTrackResponse(
                tracked=False,
                trace_id=trace_id,
                generation_id=generation_id,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                latency_ms=latency_ms,
                cost_usd=payload.cost_usd,
                message="Langfuse tracking failed",
            )


langfuse_tracker = LangfuseTracker()
