import logging
import logging.config
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        if hasattr(record, 'props'): # For custom properties
            log_record.update(record.props) # type: ignore
        return json.dumps(log_record)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": JsonFormatter, # Use the custom formatter
            # "format" is not strictly needed here as JsonFormatter dictates the output keys
            # but can be kept for reference or if other parts of logging system use it.
            "format": "%(levelname)s %(name)s %(module)s %(funcName)s %(lineno)d %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z" # ISO 8601 format
        },
        "simple": { # A simple formatter for basic console output if needed
            "format": "%(levelname)s:     %(name)s - %(message)s"
        }
    },
    "handlers": {
        "console_json": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "level": "INFO", # Default level for application logs
            "stream": "ext://sys.stdout"
        }
    },
    "root": { # Root logger configuration
        "handlers": ["console_json"],
        "level": "INFO", # Set root logger level
    },
    "loggers": { # Specific loggers can be configured here
        "uvicorn": { # Base uvicorn logger
            "handlers": ["console_json"],
            "level": "INFO",
            "propagate": False
        },
        "uvicorn.error": { # Uvicorn error logs
            "handlers": ["console_json"],
            "level": "INFO", # Or WARNING
            "propagate": False
        },
        "uvicorn.access": { # Uvicorn access logs
            "handlers": ["console_json"], # Format access logs as JSON
            "level": "INFO",
            "propagate": False
        },
        "celery": { # Celery's base logger
            "handlers": ["console_json"],
            "level": "INFO",
            "propagate": False
        },
        "app": { # Example for application-specific loggers (e.g. logging.getLogger("app.services"))
            "handlers": ["console_json"],
            "level": "DEBUG", # More verbose for app-specific logs if needed during dev
            "propagate": False # Don't propagate to root if handled here
        }
    }
}

def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
