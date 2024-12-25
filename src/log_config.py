import logging
import logging.config
import sys

# Configure logging
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "custom": {
            "()": "uvicorn.logging.DefaultFormatter",
            "format": "%(asctime)s [%(levelprefix)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "use_colors": True,
        },
        "myapp_formatter": {
            "()": "uvicorn.logging.DefaultFormatter",
            "format": "     [%(levelprefix)s] %(name)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "use_colors": True,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "custom",
            "stream": sys.stdout,
        },
        "myapp_console": {  # Handler specifically for myapp logger
            "class": "logging.StreamHandler",
            "formatter": "myapp_formatter",  # Use the custom formatter for myapp
            "stream": sys.stdout,
        },
    },
    "loggers": {
        "uvicorn.error": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "Main": {
            "handlers": ["myapp_console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "App": {
            "handlers": ["myapp_console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "Updater": {
            "handlers": ["myapp_console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}


def setup_logging():
    # Apply the logging configuration defined above
    logging.config.dictConfig(LOGGING_CONFIG)


loggerMain = logging.getLogger("Main")
loggerApp = logging.getLogger("App")
loggerUpdater = logging.getLogger("Updater")
