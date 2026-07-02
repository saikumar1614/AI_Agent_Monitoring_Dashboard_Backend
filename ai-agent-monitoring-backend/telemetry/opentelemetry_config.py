from fastapi import FastAPI
from sqlalchemy.engine import Engine

from core.config import settings
from telemetry.logging import configure_logging, get_logger
from telemetry.metrics import configure_metrics
from telemetry.tracing import configure_tracing

LOGGER = get_logger(__name__)


def configure_telemetry(app: FastAPI, db_engine: Engine | None = None) -> None:
	if settings.ENABLE_LOGGING:
		configure_logging(level=settings.LOG_LEVEL, json_logs=settings.LOG_JSON)

	if settings.ENABLE_METRICS:
		configure_metrics(app, metrics_path=settings.METRICS_PATH)

	if settings.ENABLE_TRACING:
		enabled = configure_tracing(
			app,
			service_name=settings.OTEL_SERVICE_NAME,
			otlp_endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
			db_engine=db_engine,
		)
		if not enabled:
			LOGGER.warning("Tracing requested but OpenTelemetry is not available")
