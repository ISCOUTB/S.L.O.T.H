"""Uvicorn logging configuration for minimal HTTP server.

This module provides logging configuration for Uvicorn that integrates with
the existing typechecking logging system. It ensures consistent log formatting
and proper routing of Uvicorn's logs to the same handlers used by workers.
"""

from pathlib import Path

# Ensure logs directory exists
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(levelname)s] [server] [Typechecking] [http-server] %(message)s",
        },
        "access": {
            "format": "[%(levelname)s] [server] [Typechecking] [http-server] %(message)s",
        },
        "file": {
            "format": "[%(asctime)s] [%(levelname)s] [server] [Typechecking] [http-server] %(message)s",
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        # Component-specific file handlers
        "file": {
            "formatter": "file",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(log_dir / "typechecking_http-server.log"),
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 5,
            "encoding": "utf-8",
        },
        "daily": {
            "formatter": "file",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": str(log_dir / "typechecking_http-server_daily.log"),
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,
            "encoding": "utf-8",
        },
        "error": {
            "formatter": "file",
            "class": "logging.FileHandler",
            "filename": str(log_dir / "typechecking_http-server_errors.log"),
            "encoding": "utf-8",
            "level": "ERROR",
        },
        # Consolidated file handlers (shared with other components)
        "consolidated_file": {
            "formatter": "file",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(log_dir / "typechecking_server.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
        },
        "consolidated_daily": {
            "formatter": "file",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": str(log_dir / "typechecking_server_daily.log"),
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,
            "encoding": "utf-8",
        },
        "consolidated_error": {
            "formatter": "file",
            "class": "logging.FileHandler",
            "filename": str(log_dir / "typechecking_server_errors.log"),
            "encoding": "utf-8",
            "level": "ERROR",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": [
            "default",
            "access",
            "file",
            "daily",
            "error",
            "consolidated_file",
            "consolidated_daily",
            "consolidated_error",
        ],
    },
    "loggers": {
        "uvicorn": {
            "handlers": [
                "default",
                "file",
                "daily",
                "error",
                "consolidated_file",
                "consolidated_daily",
                "consolidated_error",
            ],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": [
                "default",
                "file",
                "daily",
                "error",
                "consolidated_file",
                "consolidated_daily",
                "consolidated_error",
            ],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": [
                "access",
                "file",
                "daily",
                "consolidated_file",
                "consolidated_daily",
            ],
            "level": "INFO",
            "propagate": False,
        },
        # FastAPI application logger
        "src.minimal_server": {
            "handlers": [
                "default",
                "file",
                "daily",
                "error",
                "consolidated_file",
                "consolidated_daily",
                "consolidated_error",
            ],
            "level": "INFO",
            "propagate": False,
        },
    },
}
