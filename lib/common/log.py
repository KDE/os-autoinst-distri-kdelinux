# SPDX-License-Identifier: LGPL-2.0-only OR LGPL-3.0-only OR LicenseRef-KDE-Accepted-LGPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
import logging
import time
import shutil
from colorlog import ColoredFormatter
from typing import Any, cast

_SUCCESS_LEVEL = logging.ERROR - 5
_MESSAGE_LEVEL = logging.WARNING - 5
_configured = False


class MessageFormatter(ColoredFormatter):
    def format(self, record):
        formatted = super().format(record)

        if record.levelname in ["MESSAGE", "SUCCESS", "WARNING", "ERROR"]:
            line = "─" * shutil.get_terminal_size(fallback=(100, 24)).columns
            return f"{line}\n{formatted}\n{line}"

        return formatted


class Logger(logging.Logger):
    def success(
        self,
        message: object,
        *args: object,
        **kwargs: Any,
    ) -> None:
        if self.isEnabledFor(_SUCCESS_LEVEL):
            self._log(_SUCCESS_LEVEL, message, args, **kwargs)

    def message(
        self,
        message: object,
        *args: object,
        **kwargs: Any,
    ) -> None:
        if self.isEnabledFor(_MESSAGE_LEVEL):
            self._log(_MESSAGE_LEVEL, message, args, **kwargs)


def configure_logging() -> None:
    """Configure logging on module import."""

    global _configured

    if _configured:
        return

    logging.addLevelName(_SUCCESS_LEVEL, "SUCCESS")
    logging.addLevelName(_MESSAGE_LEVEL, "MESSAGE")
    logging.setLoggerClass(Logger)

    handler = logging.StreamHandler()
    formatter = MessageFormatter(
        "[%(asctime)s.%(msecs)03dZ] "
        "%(log_color)s%(levelname)-10s%(reset)s "
        "%(purple)s%(name)-30s%(reset)s "
        "%(message_log_color)s%(message)s%(reset)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "blue",
            "MESSAGE": "bold_cyan",
            "WARNING": "bold_yellow",
            "SUCCESS": "bold_green",
            "ERROR": "bold_red",
            "CRITICAL": "bold_red,bg_white",
        },
        secondary_log_colors={
            "message": {
                "DEBUG": "white",
                "INFO": "white",
                "MESSAGE": "bold_white",
                "WARNING": "bold_white",
                "SUCCESS": "bold_white",
                "ERROR": "bold_white",
                "CRITICAL": "bold_white",
            },
        },
    )
    formatter.converter = time.gmtime
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    _configured = True


def get_logger(name: str) -> Logger:
    """Get a logger to use in each calling module."""
    return cast(Logger, logging.getLogger(name))


def set_log_level(level: int) -> None:
    """Set the log level."""
    logging.getLogger().setLevel(level)


configure_logging()
