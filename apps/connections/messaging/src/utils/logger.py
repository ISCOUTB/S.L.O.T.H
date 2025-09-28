import logging
import logging.handlers
from pathlib import Path

from src.core.config import settings

logging.basicConfig(level=logging.INFO)

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)


def setup_logger() -> logging.Logger:
    # File formater
    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [server] [Messaging] %(message)s"
    )

    # Console formater
    console_formatter = logging.Formatter(
        "[%(levelname)s] [server] [Messaging] %(message)s"
    )

    # Main logger
    logger = logging.getLogger("Messaging Server")
    logger.setLevel(logging.ERROR)

    if settings.MESSAGING_CONNECTION_DEBUG:
        logger.setLevel(logging.DEBUG)

    logger.handlers.clear()

    # Rotating File Handler
    rotating_handler = logging.handlers.RotatingFileHandler(
        log_dir / "messaging_server.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    rotating_handler.setLevel(logging.DEBUG)
    rotating_handler.setFormatter(file_formatter)

    # 2. Timed Rotating Handler - Logs diarios
    daily_handler = logging.handlers.TimedRotatingFileHandler(
        log_dir / "messaging_server_daily.log",
        when="midnight",
        interval=1,
        backupCount=30,  # Mantener 30 días
        encoding="utf-8",
    )
    daily_handler.setLevel(logging.INFO)
    daily_handler.setFormatter(file_formatter)

    # 3. Error File Handler - Solo errores
    error_handler = logging.FileHandler(
        log_dir / "messaging_server_errors.log", encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(rotating_handler)
    logger.addHandler(daily_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

    logger.propagate = False
    return logger


logger = setup_logger()
