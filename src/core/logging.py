import sys

from loguru import logger

from core.config import settings

logger.remove()

LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> - <level>{level: <8}</level> - <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
LOG_LEVEL = "DEBUG" if settings.DEBUG else "INFO"

logger.add(sys.stdout, format=LOG_FORMAT, level=LOG_LEVEL, colorize=True)


def setup_logger(name: str) -> logger:
    return logger.bind(name=name)
