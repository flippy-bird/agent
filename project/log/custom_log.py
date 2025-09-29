import sys
from datetime import datetime

from loguru import logger

_print_level = "INFO"


def define_log_level(print_level="INFO", logfile_level="DEBUG", name: str = None):
    """Adjust the log level to above level"""
    global _print_level
    _print_level = print_level

    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d%H%M%S")
    log_name = (
        f"{name}_{formatted_date}" if name else formatted_date
    )  # name a log with prefix name

    logger.remove()
    logger.add(sys.stderr, level=print_level)
    logger.add( f"./logs/{log_name}.log", level=logfile_level)
    return logger


custom_logger = define_log_level()


if __name__ == "__main__":
    custom_logger.info("Starting application")
    custom_logger.debug("Debug message")
    custom_logger.warning("Warning message")
    custom_logger.error("Error message")
    custom_logger.critical("Critical message")

    try:
        raise ValueError("Test error")
    except Exception as e:
        custom_logger.exception(f"An error occurred: {e}")