import logging
import sys
from pathlib import Path
from cmn.resource_helper import PathManager
from logging.handlers import RotatingFileHandler

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

sys.excepthook = handle_exception