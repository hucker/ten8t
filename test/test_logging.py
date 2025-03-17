import io
import logging
import pathlib

import pytest

from ten8t import TR, Ten8tLogProgress, ten8t_logger, ten8t_reset_logging, ten8t_setup_logging


@pytest.fixture
def reset_logger():
    """
    Test fixture to reset the logger before and after each test.
    Ensures a clean state for the logger.
    """
    yield
    ten8t_reset_logging()


def test_stream_exception(reset_logger):
    with pytest.raises(ValueError):
        ten8t_setup_logging(
            level=logging.INFO,
            stream_=123  # Convert to string for file path
        )


def test_file_exception(reset_logger):
    with pytest.raises(ValueError):
        ten8t_setup_logging(
            level=logging.INFO,
            file_name="/foo/man/chu.txt"  # folders don't exist
        )


def test_file_logger(reset_logger, tmp_path):
    """
    Test that the logger writes logs to the specified file using the 'file_name' parameter.
    """
    # Create a temporary file for logging
    log_file = tmp_path / "test_log_file.log"

    # Configure the logger with the file_name
    ten8t_setup_logging(
        level=logging.INFO,
        file_name=str(log_file)  # Convert to string for file path
    )

    # Log a message
    test_message = "Hello, this is a test log message."
    ten8t_logger.info(test_message)

    # Verify the log file exists
    assert log_file.exists(), "The log file was not created."

    # Verify the content of the log file
    with open(log_file, "r") as f:
        log_content = f.read()
        assert test_message in log_content, "The expected log message was not found in the log file."
        assert 'ten8t' in log_content, "The expected log message was not found in the log file."

    # Optionally, ensure log formatting looks correct by checking dynamic parts, such as log level
    assert "INFO" in log_content, "Log content does not contain the expected log level."


def test_logger_after_reset():
    """
    Verify that the logger has only a NullHandler attached after a reset.
    """
    # Reset the logger to ensure a consistent state
    ten8t_reset_logging()

    # Check the number of handlers
    assert len(ten8t_logger.handlers) == 1, "Logger should have exactly one handler after reset."

    # Check that the attached handler is a NullHandler
    handler = ten8t_logger.handlers[0]
    assert isinstance(handler, logging.NullHandler), "Logger's handler should be a NullHandler after reset."

    # Confirm that the logger is silent by checking propagation and default behavior
    assert ten8t_logger.propagate is False, "Logger propagate should be False after reset."
    assert ten8t_logger.level == logging.NOTSET, "Logger level should be NOTSET after reset."


def test_stream_logger_installed():
    """
    Verify that a StreamHandler is installed when the 'stream' parameter is passed to setup_logging.
    """
    # Example stream (we'll use a StringIO object for simplicity)
    test_stream = io.StringIO()

    # Set up the logger with the stream parameter
    ten8t_setup_logging(stream_=test_stream)

    # Verify that a StreamHandler is added
    handlers = [handler for handler in ten8t_logger.handlers if isinstance(handler, logging.StreamHandler)]
    assert len(handlers) == 1, "StreamHandler was not added to the logger."

    # Verify that the StreamHandler uses the provided stream
    stream_handler = handlers[0]
    assert stream_handler.stream == test_stream, "StreamHandler does not use the correct stream."


def test_log_progress(reset_logger, tmp_path):
    # Create a temporary file for logging
    log_file = tmp_path / "test_log_file.log"

    # Configure the logger with the file_name
    ten8t_setup_logging(
        level=logging.INFO,
        file_name=str(log_file)  # Convert to string for file path
    )

    prog = Ten8tLogProgress()

    prog.message("Hello")
    prog.result_msg(1, 2, result=TR(status=True, msg="Test Passed"))

    assert pathlib.Path(log_file).exists()
    assert pathlib.Path(log_file).stat().st_size > 0

    # Verify the file contains the expected messages
    content = log_file.read_text()
    assert "Hello" in content, "'Hello' not found in log file"
    assert "Test Passed" in content, "'Test Passed' not found in log file"
