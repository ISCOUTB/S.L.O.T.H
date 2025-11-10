import logging
import logging.handlers

from src.utils.rootdir import ROOTDIR

log_dir = ROOTDIR / "logs"
log_dir.mkdir(exist_ok=True)


def setup() -> logging.Logger:
    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [scaler] %(message)s"
    )
    console_formatter = logging.Formatter("[%(levelname)s] [scaler] %(message)s")

    logger = logging.getLogger("scaler")

    logger.handlers.clear()
    logger.setLevel(logging.INFO)

    rotating_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "scaler.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    rotating_handler.setLevel(logging.DEBUG)
    rotating_handler.setFormatter(file_formatter)

    daily_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_dir / "scaler_daily.log",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    daily_handler.setLevel(logging.INFO)
    daily_handler.setFormatter(file_formatter)

    error_handler = logging.FileHandler(
        filename=log_dir / "scaler_errors.log", encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(rotating_handler)
    logger.addHandler(daily_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

    logger.propagate = False

    return logger


logger = setup()

if __name__ == "__main__":
    pass
