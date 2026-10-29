"""JSON logger for structured logging."""

import json
import logging
import os
import time
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """Format log records as JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logger(
    name: str = "hotel-service",
    log_file: str | None = "logs/app.log",
    level: str | None = None,
) -> logging.Logger:
    """Configure and return a JSON logger.

    Args:
        name: Logger name.
        log_file: Path to log file. Set to None to disable file logging.
        level: Logging level (DEBUG, INFO, WARNING, ERROR).
    """
    level = level or os.getenv("LOG_LEVEL", "INFO")
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    formatter = JsonFormatter()

    # File handler
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


def log_timing(logger: logging.Logger, label: str):
    """Context manager to log duration of an operation."""
    start = time.time()

    class TimingContext:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            duration_ms = round((time.time() - start) * 1000)
            logger.info(
                "duration_ms=%d label=%s",
                duration_ms,
                label,
            )

    return TimingContext()
