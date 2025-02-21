import logging

# Create a library-specific logger
ten8t_logger = logging.getLogger("ten8t")
ten8t_logger.addHandler(logging.NullHandler())  # Default to NullHandler


def ten8t_setup_logging(
        level: int = logging.WARNING,
        propagate: bool = True,
        file_name: str | None = None,
        stream=None,
        format_string: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
) -> None:
    """
    Configure the global logger for the 'ten8t' package.

    Args:
        level (int): Logging level (default=logging.WARNING).
        propagate (bool): If True, propagates logs to the parent logger (default=True).
        file_name (str): Optional file path to save logs.
        stream (io.TextIOWrapper | None): Optional stream (e.g., sys.stdout, sys.stderr).
        format_string (str): Format string for log messages (default includes timestamp, name, level, and message).

    Returns:
        None: Configures the global `ten8t_logger`.
    """
    global ten8t_logger

    # Create a formatter
    formatter = logging.Formatter(format_string)

    # Add a file handler if file_name is provided
    if file_name:
        try:
            file_handler = logging.FileHandler(file_name)
            file_handler.setFormatter(formatter)
            ten8t_logger.addHandler(file_handler)
        except (OSError, PermissionError) as e:
            raise ValueError(f"Error setting up file handler for '{file_name}'. Details: {e}")

    # Add a stream handler if stream is specified
    if stream:
        if not hasattr(stream, "write"):
            raise ValueError(f"The provided stream '{stream}' is not a valid writable stream.")
        stream_handler = logging.StreamHandler(stream)
        stream_handler.setFormatter(formatter)
        ten8t_logger.addHandler(stream_handler)

    # Configure logger settings
    ten8t_logger.setLevel(level)
    ten8t_logger.propagate = propagate


def ten8t_reset_logging():
    """
    Reset the logger to its initial state by removing all handlers and reinstating a NullHandler.

    NOTE: This function is intended for testing purposes ONLY.
          Using this in production code may disrupt logging configurations.
    """
    global ten8t_logger
    # Remove all existing handlers
    for handler in list(ten8t_logger.handlers):  # Make a copy to avoid modifying the list during iteration
        ten8t_logger.removeHandler(handler)

    # Add a NullHandler to restore the default silent state
    ten8t_logger.addHandler(logging.NullHandler())

    # Reset the logger's level and propagation settings
    ten8t_logger.setLevel(logging.NOTSET)
    ten8t_logger.propagate = False
