import logging
from logging.handlers import RotatingFileHandler

# Define the logger and set its name
logger = logging.getLogger("pytest_logger")
logger.setLevel(logging.DEBUG)  # Set the minimum log level (DEBUG will capture everything)

# Ensure handlers aren't added multiple times
if not logger.hasHandlers():
    # Stream Handler for console output
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)  # Only log INFO and above to the console
    logger.addHandler(console_handler)

    # File Handler (RotatingFileHandler) for file output
    file_handler = RotatingFileHandler(
        "pytest.log",  # Log file name
        maxBytes=10 * 1024 * 1024,  # Max size of each log file (10 MB)
        backupCount=5  # Keep up to 5 rotated log files
    )
    file_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)  # Log DEBUG and above to the file
    logger.addHandler(file_handler)


# Make the logger available to the pytest framework
def pytest_configure(config):
    """
    This is a pytest hook that runs once at the start of the test session.
    Useful for setting up global configurations.
    """
    logger.info("Global pytest logger initialized.")
