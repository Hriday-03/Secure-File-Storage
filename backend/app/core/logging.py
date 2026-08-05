"""Structured logging configuration using loguru."""

import sys
from pathlib import Path

from loguru import logger

from app.core.config import settings


def setup_logging() -> None:
    """Configure loguru sinks for console and file output."""
    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        format=log_format,
        colorize=True,
    )

    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.add(
        log_dir / "app.log",
        level="DEBUG",
        format=log_format,
        rotation="10 MB",
        retention="10 days",
        compression="zip",
        enqueue=True,
    )

    logger.info("Logging configured. Log level: {}", settings.LOG_LEVEL)
