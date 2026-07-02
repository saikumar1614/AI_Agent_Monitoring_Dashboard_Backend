import json
import logging
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
	def format(self, record: logging.LogRecord) -> str:
		payload = {
			"timestamp": datetime.now(timezone.utc).isoformat(),
			"level": record.levelname,
			"logger": record.name,
			"message": record.getMessage(),
		}
		if record.exc_info:
			payload["exception"] = self.formatException(record.exc_info)
		return json.dumps(payload)


def configure_logging(level: str = "INFO", json_logs: bool = True) -> None:
	logger = logging.getLogger()
	logger.setLevel(level.upper())
	logger.handlers.clear()

	handler = logging.StreamHandler()
	if json_logs:
		handler.setFormatter(JsonFormatter())
	else:
		handler.setFormatter(
			logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
		)

	logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
	return logging.getLogger(name)
