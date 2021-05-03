import logging
import logging.config
import socket
import sys
from contextlib import contextmanager
from typing import Any, Optional

import structlog
from structlog.contextvars import (bind_contextvars, merge_contextvars,
                                   unbind_contextvars)


def configure_logging(processor: Any, level: int) -> None:
    level_str = logging.getLevelName(level)
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "formater": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": processor,
                    # Adjust log entries that are not from structlog
                    "foreign_pre_chain": [
                        structlog.stdlib.add_log_level,
                        structlog.stdlib.add_logger_name,
                        timestamper,
                    ],
                },
            },
            "handlers": {
                "default": {
                    "level": level_str,
                    "class": "logging.StreamHandler",
                    "formatter": "formater",
                },
            },
            "loggers": {
                "": {
                    "handlers": ["default"],
                    "level": level_str,
                    "propagate": True,
                },
                "sqlalchemy": {
                    "handlers": ["default"],
                    "level": level_str,
                },
                "PyQt5": {
                    "handlers": ["default"],
                    "level": level_str,
                },
            },
        }
    )

    structlog.configure_once(
        processors=[
            merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.PositionalArgumentsFormatter(),
            timestamper,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=True,
    )


@contextmanager
def bind_remote_address_to_logger(sock: socket.socket):  # type:ignore
    try:
        bind_contextvars(remote=sock.getpeername())
    except socket.error:
        pass

    try:
        yield
    finally:
        unbind_contextvars("remote")


@contextmanager
def bind_client_name_to_logger(name: str):  # type:ignore
    if name:
        bind_contextvars(client=name)

    try:
        yield
    finally:
        unbind_contextvars("client")


def get_logger(name: Optional[str] = None) -> Any:
    if not name:
        f = sys._getframe().f_back
        if f is not None:
            name = f.f_globals.get("__name__") or None

    if name:
        structlog.get_logger(name)

    return structlog.get_logger()
