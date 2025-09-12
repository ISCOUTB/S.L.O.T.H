import logging

logger = logging.getLogger("DDLGeneratorServer")
handler = logging.StreamHandler()
formatter = logging.Formatter("[server] [excel-reader] %(message)s")
handler.setFormatter(formatter)
logger.handlers = [handler]
logger.propagate = False

LOGGING_CONFIG = { # type: ignore
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[server] [excel-reader] %(message)s",
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["default"],
    },
    "loggers": {
        "uvicorn": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False,
        },
    },
}

if __name__ == "__main__":
    pass
