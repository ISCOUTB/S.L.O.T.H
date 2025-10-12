import logging
import logging.handlers
from pathlib import Path

# Ensure logs directory exists for file handlers
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Disable pika's verbose logging
logging.getLogger("pika").setLevel(logging.WARNING)


def create_component_logger(component_name: str) -> logging.Logger:
    """Create a logger with component-specific formatting.

    Args:
        component_name: Name of the component (e.g., 'main', 'validation', 'schemas')

    Returns:
        logging.Logger: Logger instance with component-specific prefix
    """
    component_logger = logging.getLogger(f"Typechecking.{component_name}")
    component_logger.setLevel(logging.DEBUG)  # Allow all levels

    # File formatter with component prefix
    file_formatter = logging.Formatter(
        f"[%(asctime)s] [%(levelname)s] [server] [Typechecking] [{component_name}] %(message)s"
    )

    # Console formatter with component prefix
    console_formatter = logging.Formatter(
        f"[%(levelname)s] [server] [Typechecking] [{component_name}] %(message)s"
    )

    # Clear any existing handlers
    component_logger.handlers.clear()

    # Reuse the same log directory
    log_dir = Path("logs")

    # Component-specific rotating file handler
    rotating_handler = logging.handlers.RotatingFileHandler(
        log_dir / f"typechecking_{component_name}.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    rotating_handler.setLevel(logging.DEBUG)
    rotating_handler.setFormatter(file_formatter)

    # Component-specific daily handler
    daily_handler = logging.handlers.TimedRotatingFileHandler(
        log_dir / f"typechecking_{component_name}_daily.log",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    daily_handler.setLevel(logging.INFO)
    daily_handler.setFormatter(file_formatter)

    # Component-specific error handler
    error_handler = logging.FileHandler(
        log_dir / f"typechecking_{component_name}_errors.log", encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Show INFO and above in console
    console_handler.setFormatter(console_formatter)

    # === CONSOLIDATED LOGS ===
    # Also write to the main consolidated log files

    # Consolidated rotating file handler
    consolidated_rotating_handler = logging.handlers.RotatingFileHandler(
        log_dir / "typechecking_server.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    consolidated_rotating_handler.setLevel(logging.DEBUG)
    consolidated_rotating_handler.setFormatter(file_formatter)

    # Consolidated daily handler
    consolidated_daily_handler = logging.handlers.TimedRotatingFileHandler(
        log_dir / "typechecking_server_daily.log",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    consolidated_daily_handler.setLevel(logging.INFO)
    consolidated_daily_handler.setFormatter(file_formatter)

    # Consolidated error handler
    consolidated_error_handler = logging.FileHandler(
        log_dir / "typechecking_server_errors.log", encoding="utf-8"
    )
    consolidated_error_handler.setLevel(logging.ERROR)
    consolidated_error_handler.setFormatter(file_formatter)

    # Attach all handlers (component-specific + consolidated)
    component_logger.addHandler(rotating_handler)
    component_logger.addHandler(daily_handler)
    component_logger.addHandler(error_handler)
    component_logger.addHandler(console_handler)

    # Add consolidated handlers
    component_logger.addHandler(consolidated_rotating_handler)
    component_logger.addHandler(consolidated_daily_handler)
    component_logger.addHandler(consolidated_error_handler)

    # Disable propagation to prevent duplicate messages
    component_logger.propagate = False
    return component_logger
