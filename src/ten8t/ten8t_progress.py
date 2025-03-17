"""
Classes to support progress tracking.
"""

import logging
from abc import ABC

from .ten8t_exception import Ten8tException
from .ten8t_logging import ten8t_logger
from .ten8t_result import Ten8tResult
from .ten8t_util import IntOrNone, StrOrNone


# pylint: disable=R0903
class Ten8tProgress(ABC):
    """
    Abstract base class for tracking and managing progress.

    This class serves as a base for defining progress tracking mechanisms in
    iterative processes. It is designed to be subclassed, with custom behavior
    to be implemented in the '__call__' method. Users can leverage this class
    to provide updates for operations with finite or infinite iterations, display
    status messages, and optionally handle results.

    Important point:

    Current Iteration and MaxIteration reflect the number of check functions
    in the list of checks to run and the current value of the check being run.213


    """

    def __init__(self):
        pass

    def __str__(self):
        return "Ten8tProgress base class for tracking progress"

    def __repr__(self):
        return "<Ten8tProgress>"

    def message(self, msg: str):
        """
        Just report an arbitrary message.

        This can be things like starting, stopping, exceptions.  Anything not tied to a result.
        """

    def result_msg(self, current_iteration: int, max_iteration: int, msg: StrOrNone = '',
                   result: Ten8tResult | None = None):
        """
        Report a result.
        This should report progress with the results of a check function.  Note that
        check functions can return multiple results since they are generators.
        """


# pylint: disable=R0903
class Ten8tNoProgress(Ten8tProgress):
    """
     A subclass of Ten8tProgress that overrides progress functionality by
    performing no operation. This class is particularly useful for testing
    purposes when progress tracking is not required.

    """

    def __str__(self):
        return "Ten8tNoProgress - No progress tracking (used primarily for testing)"

    def __repr__(self):
        return "<Ten8tNoProgress>"

    def message(self, msg: str):
        """ Do Nothing"""

    def result_msg(self, current_iteration: int, max_iteration: int, msg: StrOrNone = '',
                   result: Ten8tResult | None = None):
        """ Do Nothing"""


# pylint: disable=R0903
class Ten8tDebugProgress(Ten8tProgress):
    """
    Manages and displays debug progress messages for a process.

    This class is a subclass of `Ten8tProgress` and is specifically
    designed for debugging purposes. It provides functionality to
    print debug messages alongside an optional status indicator based
    on the provided result. Typically used during iterative processes
    to notify about current progress and outcomes.

    Attributes:
        No specific attributes are defined for this subclass.
    """

    def __str__(self):
        return "Ten8tDebugProgress - Debug progress tracker displaying messages in stdout"

    def __repr__(self):
        return "<Ten8tDebugProgress>"

    def message(self, msg: str):
        if msg:
            print(msg)

    def result_msg(self, current_iteration: int, max_iteration: int, msg: StrOrNone = '',
                   result: Ten8tResult | None = None):
        if result:
            print("+" if result.status else "-", end="")


# pylint: disable=R0903
class Ten8tLogProgress(Ten8tProgress):
    """
    Send progress status to ten8t logger.

    This class allows you to set the level of log messages and log
    results independently as well as completely disabling them using None.

    Attributes:
        No specific attributes are defined for this subclass.
    """

    def __init__(self,
                 logger: logging.Logger = ten8t_logger,
                 result_level: IntOrNone = logging.INFO,
                 msg_level: IntOrNone = logging.INFO):

        # Validate result_level
        if result_level is not None and not self._is_valid_log_level(result_level):
            raise Ten8tException(f"Invalid logging level provided for result_level: {result_level}")

        # Validate msg_level
        if msg_level is not None and not self._is_valid_log_level(msg_level):
            raise Ten8tException(f"Invalid logging level provided for msg_level: {msg_level}")

        if not isinstance(logger, logging.Logger):
            raise Ten8tException(f"Invalid logger type passed to Ten8tLogProgress.")

        self.logger: logging.Logger = logger
        self.result_level: int = result_level
        self.msg_level: int = msg_level
        super().__init__()

    def __str__(self):
        return (
            f"Ten8tLogProgress - Logs progress to logger '{self.logger.name}'"
            f" with result_level={self.result_level} and msg_level={self.msg_level}"
        )

    def __repr__(self):
        return (
            f"<Ten8tLogProgress(logger={self.logger.name}, "
            f"result_level={self.result_level}, msg_level={self.msg_level})>"
        )

    def message(self, msg: str):
        # Log the custom message if available and level is set
        if msg and self.msg_level is not None:
            self.logger.log(self.msg_level, msg)

    def result_msg(self, current_iter: int, max_iter: int, msg: StrOrNone = None,
                   result: Ten8tResult | None = None):

        # Log the result object if available and level is set
        if result and self.result_level is not None:
            tag_str = f" tag=[{result.tag}] " if result.tag else ''
            level_str = f" level=[{result.level}] " if result.level else ''
            phase_str = f" phase=[{result.phase}] " if result.phase else ''
            status_str = self._get_status_str(result)
            msg_str = msg + ' ' if msg else ''

            self.logger.log(
                self.result_level,
                f"[{current_iter}/{max_iter}] {status_str}{msg_str}{tag_str}{level_str}{phase_str} - {result.msg}",
            )

    @staticmethod
    def _get_status_str(result: Ten8tResult) -> str:
        """
        Generates a status string based on the result.

        Args:
            result (Ten8tResult): The result object.

        Returns:
            str: The status string ("SKIP ", "PASS ", or "FAIL ").
        """
        if result.skipped:
            return "SKIP "
        if result.status is True:
            return "PASS "
        return "FAIL "

    @staticmethod
    def _is_valid_log_level(level):
        """
        Validates if the provided level is a valid logging level.

        Args:
            level (int): Log level to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        return level in (
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        )


class Ten8tMultiProgress(Ten8tProgress):
    """
    A multi-progress handler for managing and consolidating updates across
    multiple progress tracking objects.

    This class inherits from Ten8tProgress and aggregates progress objects
    to allow broadcasting messages and results to all of them. It is
    especially useful when managing parallel or grouped progress tracking
    scenarios, ensuring consistent updates and communication.

    Normally I would expect that you would always use the logging object and
    perhaps you might use the custom one for whatever UI you might be running under
    so it might look like

    log_prog = Ten8tLogProgress()
    streamlit_prog = Ten8tStreamlitProgress()
    multi_prog = Ten8tMultiProgress([log_prog,streamlit_prog])

    ch = ten8t.ten8t_checker(check_functions=[check1,check2],progress=multi_prog)
    ch.run_all()

    Attributes:
        progress_list (list): A list containing progress tracking objects.
    """

    def __init__(self, progress_list):
        if not isinstance(progress_list, list):
            progress_list = [progress_list]

        self.progress_list = progress_list

    def __str__(self):
        return (
            f"Ten8tMultiProgress - Manages Progress for {len(self.progress_list)} Sub-progress Handlers"
        )

    def __repr__(self):
        return (
            f"<Ten8tMultiProgress(progress_list={len(self.progress_list)} handlers)>"
        )

    def message(self, msg):
        for progress in self.progress_list:
            progress.message(msg)

    def result_msg(self, current_iteration: int, max_iteration: int, msg: StrOrNone = None,
                   result: Ten8tResult | None = None):
        for progress in self.progress_list:
            progress.result_msg(current_iteration, max_iteration, msg=msg, result=result)
