from time import perf_counter

from fastapi import FastAPI, Request, Response

try:
	from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
except ImportError:
	CONTENT_TYPE_LATEST = "text/plain; version=0.0.4"
	Counter = None
	Histogram = None
	generate_latest = None


REQUEST_COUNT = (
	Counter(
		"http_requests_total",
		"Total HTTP requests",
		["method", "path", "status_code"],
	)
	if Counter
	else None
)

REQUEST_DURATION = (
	Histogram(
		"http_request_duration_seconds",
		"HTTP request duration seconds",
		["method", "path"],
	)
	if Histogram
	else None
)


def configure_metrics(app: FastAPI, metrics_path: str = "/metrics") -> None:
	@app.middleware("http")
	async def metrics_middleware(request: Request, call_next):
		start = perf_counter()
		response = await call_next(request)
		duration = perf_counter() - start

		path = request.url.path
		method = request.method
		status_code = str(response.status_code)

		if REQUEST_COUNT:
			REQUEST_COUNT.labels(method=method, path=path, status_code=status_code).inc()
		if REQUEST_DURATION:
			REQUEST_DURATION.labels(method=method, path=path).observe(duration)

		return response

	@app.get(metrics_path, include_in_schema=False)
	async def metrics_endpoint() -> Response:
		if generate_latest is None:
			return Response(
				content="# prometheus_client not installed\n",
				media_type="text/plain",
				status_code=503,
			)
		return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
