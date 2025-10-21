import logging
import logging.handlers
from pathlib import Path

from src.core.config import settings

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
    - Production mode: INFO level and above (shows INFO, WARNING, ERROR, CRITICAL)

    Returns:
        logging.Logger: Configured logger instance with all handlers attached

    Handler Configuration:
        - Rotating Handler: 10MB max size, 5 backup files, DEBUG level
        - Daily Handler: Midnight rotation, 30 days retention, INFO level
        - Error Handler: ERROR level only, persistent file
        - Console Handler: INFO level and above, simplified formatting

    Note:
        The logger's propagate setting is disabled to prevent duplicate
        messages from parent loggers.
    """
    # File formatter with timestamp and detailed context
    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [server] [ddl-generator] %(message)s"
    )

    # Console formatter with simplified format for readability
    console_formatter = logging.Formatter(
        "[%(levelname)s] [server] [ddl-generator] %(message)s"
    )

    # Create main logger instance
    logger = logging.getLogger("DDLGeneratorServer")

    # Adjust log level based on debug configuration
    if settings.DDL_GENERATOR_DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Clear any existing handlers to prevent duplication
    logger.handlers.clear()

    # 1. Rotating File Handler - Size-based rotation for main logs
    rotating_handler = logging.handlers.RotatingFileHandler(
        log_dir / "ddlgenerator_server.log",
        maxBytes=10 * 1024 * 1024,  # 10MB per file
        backupCount=5,  # Keep 5 backup files
        encoding="utf-8",
    )
    rotating_handler.setLevel(logging.DEBUG)
    rotating_handler.setFormatter(file_formatter)

    # 2. Daily Rotating Handler - Time-based rotation for daily logs
    daily_handler = logging.handlers.TimedRotatingFileHandler(
        log_dir / "ddlgenerator_server_daily.log",
        when="midnight",  # Rotate at midnight
        interval=1,  # Every day
        backupCount=30,  # Keep 30 days of logs
        encoding="utf-8",
    )
    daily_handler.setLevel(logging.INFO)
    daily_handler.setFormatter(file_formatter)

    # 3. Error File Handler - Dedicated error logging
    error_handler = logging.FileHandler(
        log_dir / "ddlgenerator_server_errors.log", encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)

    # 4. Console Handler - Real-time console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Set explicit level for console
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
