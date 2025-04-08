import sys
from datetime import datetime

from loguru import logger as _logger

from src.config import PROJECT_ROOT


def define_log_level(print_level="INFO", logfile_level="DEBUG", name: str = None):

    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d%H%M%S")
    log_name = f"{name}_{formatted_date}" if name else formatted_date

    _logger.remove()
    _logger.add(sys.stderr, level=print_level)
    _logger.add(PROJECT_ROOT / f"logs/{log_name}.log", level=logfile_level)
    return _logger


logger = define_log_level()

if __name__ == "__main__":
    logger.info("Starting application")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
