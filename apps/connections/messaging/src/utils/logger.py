"""Logging configuration and setup for the messaging gRPC server.

This module provides centralized logging configuration with multiple handlers
for different log levels and output destinations. It supports both file-based
and console logging with configurable verbosity levels based on debug settings.

Functions:
    setup_logger: Configure and return the main application logger

Constants:
    logger: Pre-configured logger instance ready for use throughout the application

Logging Features:
    - Rotating file logs with size-based rotation (10MB per file, 5 backups)
    - Daily rotating logs with time-based rotation (midnight, 30 days retention)
    - Error-only logs for critical issue tracking
    - Console output with simplified formatting
    - Debug level control via configuration settings
    - UTF-8 encoding for proper character handling

Log Files:
    - logs/messaging_server.log: Main rotating log file
    - logs/messaging_server_daily.log: Daily rotating log file
    - logs/messaging_server_errors.log: Error-only log file
"""

import logging
import logging.handlers
from pathlib import Path

from src.core.config import settings

# Set basic logging configuration for the application
logging.basicConfig(level=logging.INFO)

# Ensure logs directory exists for file handlers
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)


def setup_logger() -> logging.Logger:
    """Configure and return the main application logger.

    Sets up a comprehensive logging system with multiple handlers for different
    log levels and output destinations. The logger configuration includes:

    - Rotating file handler for general application logs
    - Daily rotating handler for day-based log organization
    - Error-specific handler for critical issue tracking
    - Console handler for real-time monitoring

    Log levels are configured based on the debug setting:
    - DEBUG mode: All log levels (DEBUG and above)
    - Production mode: ERROR level and above

    Returns:
        logging.Logger: Configured logger instance with all handlers attached

    Handler Configuration:
        - Rotating Handler: 10MB max size, 5 backup files, DEBUG level
        - Daily Handler: Midnight rotation, 30 days retention, INFO level
        - Error Handler: ERROR level only, persistent file
        - Console Handler: All levels, simplified formatting

    Note:
        The logger's propagate setting is disabled to prevent duplicate
        messages from parent loggers.
    """
    # File formatter with timestamp and detailed context
    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [server] [Messaging] %(message)s"
    )

    # Console formatter with simplified format for readability
    console_formatter = logging.Formatter(
        "[%(levelname)s] [server] [Messaging] %(message)s"
    )

    # Create main logger instance
    logger = logging.getLogger("Messaging Server")
    logger.setLevel(logging.ERROR)

    # Adjust log level based on debug configuration
    if settings.MESSAGING_CONNECTION_DEBUG:
        logger.setLevel(logging.DEBUG)

    # Clear any existing handlers to prevent duplication
    logger.handlers.clear()

    # 1. Rotating File Handler - Size-based rotation for main logs
    rotating_handler = logging.handlers.RotatingFileHandler(
        log_dir / "messaging_server.log",
        maxBytes=10 * 1024 * 1024,  # 10MB per file
        backupCount=5,  # Keep 5 backup files
        encoding="utf-8",
    )
    rotating_handler.setLevel(logging.DEBUG)
    rotating_handler.setFormatter(file_formatter)

    # 2. Daily Rotating Handler - Time-based rotation for daily logs
    daily_handler = logging.handlers.TimedRotatingFileHandler(
        log_dir / "messaging_server_daily.log",
        when="midnight",  # Rotate at midnight
        interval=1,  # Every day
        backupCount=30,  # Keep 30 days of logs
        encoding="utf-8",
    )
    daily_handler.setLevel(logging.INFO)
    daily_handler.setFormatter(file_formatter)

    # 3. Error File Handler - Dedicated error logging
    error_handler = logging.FileHandler(
        log_dir / "messaging_server_errors.log", encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)

    # 4. Console Handler - Real-time console output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    # Attach all handlers to the logger
    logger.addHandler(rotating_handler)
    logger.addHandler(daily_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

    # Disable propagation to prevent duplicate log messages
    logger.propagate = False
    return logger


# Global logger instance for application-wide use
logger = setup_logger()
