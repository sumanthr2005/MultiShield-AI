"""Central logging configuration for the backend."""

from __future__ import annotations

import logging
import logging.config


def configure_logging(level: str = "INFO") -> None:
    """Configure application-wide structured logging.

    The format is intentionally compact so it works in Docker logs and most
    observability pipelines without additional parsing glue.
    """

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                }
            },
            "root": {"handlers": ["default"], "level": level.upper()},
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named application logger."""

    return logging.getLogger(name)
