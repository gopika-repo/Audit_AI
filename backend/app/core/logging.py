"""
Structured logging configuration using Loguru.
Provides JSON logging in production and human-readable format in development.
"""

import sys
import json
from datetime import datetime
from pathlib import Path

from loguru import logger


def setup_logging(debug: bool = False, environment: str = "development") -> None:
    """
    Configure structured logging with loguru.
    
    Args:
        debug: Enable debug logging
        environment: Current environment (development, staging, production)
    """
    # Remove default handler
    logger.remove()

    # Log level based on environment and debug flag
    log_level = "DEBUG" if debug or environment == "development" else "INFO"

    if environment == "production":
        # Production: JSON structured logging to file and stderr
        logger.add(
            sys.stderr,
            format=_json_format,
            level=log_level,
            serialize=True,
            backtrace=True,
            diagnose=False,
        )

        # Add file logging for production
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        logger.add(
            log_dir / "app.log",
            format=_json_format,
            level=log_level,
            serialize=True,
            rotation="00:00",  # Rotate at midnight
            retention="7 days",
            backtrace=True,
            diagnose=False,
        )
    else:
        # Development: Human-readable logging
        logger.add(
            sys.stderr,
            format=_dev_format,
            level=log_level,
            colorize=True,
            backtrace=True,
            diagnose=True,
        )


def _json_format(record: dict) -> str:
    """
    Format log record as JSON.
    
    Args:
        record: Log record from loguru
        
    Returns:
        JSON formatted log string
    """
    log_data = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "logger": record["name"],
        "message": record["message"],
        "function": record["function"],
        "line": record["line"],
    }

    if record["extra"]:
        log_data.update(record["extra"])

    if record["exception"]:
        log_data["exception"] = {
            "type": record["exception"][0].__name__,
            "value": str(record["exception"][1]),
            "traceback": record["exc_info"],
        }

    return json.dumps(log_data)


_dev_format = (
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)


def get_logger():
    """
    Get logger instance.
    
    Returns:
        logger: Configured loguru logger
    """
    return logger
