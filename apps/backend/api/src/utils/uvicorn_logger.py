from pathlib import Path
from typing import Any, Dict

# Ensure logs directory exists
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)


LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
        "file": {
            "format": "[%(asctime)s] [%(levelname)s] [server] [API] %(name)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "access_file": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '[%(asctime)s] [%(levelname)s] [server] [API] [access] %(client_addr)s - "%(request_line)s" %(status_code)s',
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        # File handlers for persistent logging
        "file": {
            "formatter": "file",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(log_dir / "api_server.log"),
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 5,
            "encoding": "utf-8",
        },
        "daily": {
            "formatter": "file",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": str(log_dir / "api_server_daily.log"),
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,
            "encoding": "utf-8",
        },
        "error": {
            "formatter": "file",
            "class": "logging.FileHandler",
            "filename": str(log_dir / "api_server_errors.log"),
            "encoding": "utf-8",
            "level": "ERROR",
        },
        "access_file": {
            "formatter": "access_file",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(log_dir / "api_access.log"),
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["default", "file", "daily", "error"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["default", "file", "daily", "error"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["access", "access_file"],
            "level": "INFO",
            "propagate": False,
        },
        # Add custom loggers for your API components
        "API": {
            "handlers": ["default", "file", "daily", "error"],
            "level": "INFO",
            "propagate": False,
        },
        # Silence noisy third-party loggers
        "sqlalchemy.engine": {
            "handlers": ["file", "error"],
            "level": "WARNING",
            "propagate": False,
        },
        "sqlalchemy.pool": {
            "handlers": ["file", "error"],
            "level": "WARNING",
            "propagate": False,
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["default", "file", "daily", "error"],
    },
}
