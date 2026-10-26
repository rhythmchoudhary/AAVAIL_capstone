import json
import logging
import time
from pathlib import Path

class JsonLineFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "level": record.levelname,
            "message": record.getMessage(),
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
        }
        if hasattr(record, "event_data"):
            payload.update(record.event_data)
        return json.dumps(payload)

def build_logger(path: str | Path) -> logging.Logger:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.Logger(f"forecast_api_{path.resolve()}", logging.INFO)
    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setFormatter(JsonLineFormatter())
    logger.addHandler(handler)
    logger.propagate = False
    return logger

def log_event(logger, message: str, **fields):
    record = logger.makeRecord(logger.name, logging.INFO, "", 0, message, (), None)
    record.event_data = fields
    logger.handle(record)
