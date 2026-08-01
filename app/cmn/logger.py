import logging
import sys
from pathlib import Path
from cmn.resource_helper import PathManager
from logging.handlers import RotatingFileHandler
import traceback
import functools
import traceback


log_dir = PathManager.log_DIR

handlers = [
    RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=2 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
]

if hasattr(sys, "__stdout__") and sys.__stdout__:
    handlers.append(logging.StreamHandler(sys.__stdout__))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers= handlers
)

logger = logging.getLogger("App")

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.exception(
        "Unhandled Exception",
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    traceback.print_exception(exc_type, exc_value, exc_traceback)

def debug_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Exception in {func.__name__}: {e}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            raise
    return wrapper


sys.excepthook = handle_exception