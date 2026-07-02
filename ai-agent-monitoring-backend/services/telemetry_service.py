from typing import Any

from telemetry.logging import get_logger

LOGGER = get_logger(__name__)


def export_event(event_name: str, payload: dict[str, Any]) -> None:
	"""Export telemetry payload through structured logs for downstream collectors."""
	LOGGER.info("telemetry_event name=%s payload=%s", event_name, payload)
