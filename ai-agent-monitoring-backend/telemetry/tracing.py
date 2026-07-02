import logging

from fastapi import FastAPI
from sqlalchemy.engine import Engine

LOGGER = logging.getLogger(__name__)


def configure_tracing(
	app: FastAPI,
	service_name: str,
	otlp_endpoint: str,
	db_engine: Engine | None = None,
) -> bool:
	try:
		from opentelemetry import trace
		from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
		from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
		from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
		from opentelemetry.sdk.resources import Resource
		from opentelemetry.sdk.trace import TracerProvider
		from opentelemetry.sdk.trace.export import BatchSpanProcessor
	except ImportError:
		LOGGER.warning("OpenTelemetry dependencies are missing. Tracing disabled.")
		return False

	resource = Resource.create({"service.name": service_name})
	tracer_provider = TracerProvider(resource=resource)
	span_exporter = OTLPSpanExporter(endpoint=f"{otlp_endpoint.rstrip('/')}/v1/traces")
	tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
	trace.set_tracer_provider(tracer_provider)

	FastAPIInstrumentor.instrument_app(app)
	if db_engine is not None:
		SQLAlchemyInstrumentor().instrument(engine=db_engine)
	LOGGER.info("Tracing configured for service: %s", service_name)
	return True
