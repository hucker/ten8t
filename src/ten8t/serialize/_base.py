"""Base class for serialzation implementations."""
import sys
from abc import ABC, abstractmethod
from typing import List, TextIO

from ..ten8t_checker import Ten8tChecker
from ..ten8t_types import StrOrNone


class Ten8tDump(ABC):
    """
    Abstract base class for serializing Ten8t test results to various formats.

    Provides the interface and common functionality for all serialization formats.
    """

    def __init__(self, config=None):
        """
        Initialize the Ten8tDump with configuration.

        Args:
            config: Configuration object for the dump process
        """
        from ._config import Ten8tDumpConfig
        self.config = config or Ten8tDumpConfig()

        # Process columns to get valid lists
        self.summary_columns = self._process_summary_columns()
        self.result_columns = self._process_result_columns()

        # Determine what to include based on config and available columns
        self.include_summary = self.config.show_summary and self.summary_columns
        self.include_results = self.config.show_results and self.result_columns

    def _process_summary_columns(self) -> List[str]:
        """Process summary columns from config into a valid list."""
        columns = self.config.summary_columns

        if not columns or columns == 'all':
            from ._config import Ten8tDumpConfig
            return Ten8tDumpConfig.VALID_SUMMARY_COLUMNS.copy()

        return columns if isinstance(columns, list) else [columns]

    def _process_result_columns(self) -> List[str]:
        """Process result columns from config into a valid list."""
        columns = self.config.result_columns

        if not columns or columns == 'all':
            from ._config import Ten8tDumpConfig
            return Ten8tDumpConfig.VALID_RESULT_COLUMNS.copy()

        return columns if isinstance(columns, list) else [columns]

    def get_output_file(self, encoding="utf8") -> TextIO:
        """
        Get file handle for output based on config.

        Returns:
            File handle for writing
        """
        filename = self.config.output_file
        if filename:
            return open(filename, "w", newline="", encoding=encoding)
        return sys.stdout

    def dump(self, checker: Ten8tChecker) -> None:
        """
        Dump checker results to the specified format.

        Args:
            checker: Ten8tChecker instance containing results to dump

        Raises:
            
            Ten8tException: If serialization fails
        """
        output_file = self.get_output_file()

        try:
            self._dump_implementation(checker, output_file)
        except Exception as e:
            raise Exception(f"Error serializing results: {e}") from e
        finally:
            if self.config.output_file and output_file != sys.stdout:
                output_file.close()

    def _dump_pre_text(self, output_file: TextIO, title: StrOrNone = None):
        """Optional pre_text to render"""

    def _dump_post_text(self, output_file: TextIO):
        """Optional post_text to render"""

    @abstractmethod
    def _dump_implementation(self, checker: Ten8tChecker, output_file: TextIO) -> None:
        """
        Implementation-specific dumping logic to be overridden by subclasses.

        Args:
            checker: Ten8tChecker instance containing results to dump
            output_file: File handle for writing output
        """
        pass
