"""Centralized logging configuration."""

import logging
from pathlib import Path

import structlog

from shopee_cli.config.settings import get_settings

LOG_FILE_NAME = "shopee.log"


def configure_logging(level: int = logging.INFO) -> None:
    """Configure application logging."""
    settings = get_settings()
    settings.log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[
            logging.FileHandler(
                Path(settings.log_dir) / LOG_FILE_NAME,
                encoding="utf-8",
            ),
        ],
    )
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(level),
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a structured logger."""
    return structlog.get_logger(name)
