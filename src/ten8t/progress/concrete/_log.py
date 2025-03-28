import logging

from .._base import Ten8tProgress
from ...ten8t_exception import Ten8tException
from ...ten8t_logging import ten8t_logger
from ...ten8t_result import Ten8tResult
from ...ten8t_util import IntOrNone, StrOrNone


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
            raise Ten8tException("Invalid logger type passed to Ten8tLogProgress.")

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

    def result_msg(
            self,
            current_iter: int,
            max_iter: int,
            msg: StrOrNone = "",
            result: Ten8tResult | None = None,
    ):

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
