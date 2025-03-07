import logging
import sys
from sys import stderr
from types import FrameType
from typing import Optional, Union

from loguru import logger as logger


# recipe from https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        level: Union[str, int]
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame: Optional[FrameType] = sys._getframe(6)
        depth = 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def set_logger(
    stderr_log_level: str = "DEBUG",
) -> None:
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    logger.remove()
    logger.add(
        stderr,
        level=stderr_log_level,
    )


set_logger()
