#!/usr/bin/env python3
"""
Logging configuration for MySearchEngine.

Provides unified logging setup with console and file output to logs directory.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


def setup_logger(
    name: str = "mysearchengine",
    level: int = logging.DEBUG,
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """
    Set up and configure the logger.

    Args:
        name: Logger name
        level: Logging level (default: DEBUG)
        log_file: Optional path to log file (if None, uses timestamped file in logs dir)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding duplicate handlers if logger is already configured
    if logger.handlers:
        return logger

    # Format for log messages - detailed with module name and level
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler - always enabled
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler - default to logs directory with timestamp
    if log_file is None:
        # Create logs directory in project root
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"search-engine-{timestamp}.log"

    try:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.info(f"Logging to file: {log_file}")
    except Exception as e:
        logger.warning(f"Failed to set up file logging: {e}", exc_info=True)

    # Configure third-party library loggers - let them propagate to our logger
    for lib_name in ["httpx", "urllib3", "asyncio"]:
        lib_logger = logging.getLogger(lib_name)
        # Let us see httpx requests at DEBUG level for debugging
        if lib_name == "httpx":
            lib_logger.setLevel(logging.DEBUG)
        else:
            lib_logger.setLevel(logging.WARNING)
        # Ensure they propagate to our handlers
        lib_logger.propagate = True

    return logger


def get_logger(name: str = "mysearchengine") -> logging.Logger:
    """
    Get a logger instance. Will create a default one if not already set up.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # If not configured, set up with defaults
    if not logger.handlers:
        return setup_logger(name)

    return logger
