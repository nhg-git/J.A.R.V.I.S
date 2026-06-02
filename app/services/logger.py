import logging
import sys
from pathlib import Path
from datetime import datetime

LOG_DIR = Path(__file__).parent.parent.parent / "data"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Console handler — colored output
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(
        logging.Formatter(
            "\033[36m%(asctime)s\033[0m │ \033[35m%(name)-20s\033[0m │ "
            "%(levelname)-8s │ %(message)s",
            datefmt="%H:%M:%S",
        )
    )

    # File handler
    log_file = LOG_DIR / f"jarvis_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s"
        )
    )

    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger


logger = get_logger("jarvis")
