"""
CSV serialization implementation for Ten8t test results.
"""
import csv
from typing import Any, TextIO

from ten8t.serialize._base import Ten8tDump
from ten8t.serialize._config import Ten8tDumpConfig
from ten8t.ten8t_checker import Ten8tChecker


class Ten8tDumpCSV(Ten8tDump):
    """
    CSV serialization implementation for Ten8t test results.

    Outputs test results as a CSV file with configurable columns and quoting options.
    """

    def __init__(self, config: Ten8tDumpConfig = None):
        """
        Initialize CSV serializer with options.

        Args:
            config: Configuration object for the dump process
        """
        # Use default config if none provided
        if config is None:
            config = Ten8tDumpConfig.csv_default()

        super().__init__(config)

        # Set quoting based on the quoted_strings config parameter
        self.quoting = csv.QUOTE_MINIMAL if self.config.quoted_strings else csv.QUOTE_NONE

    def _format_result_header(self, cols: list[str]) -> list[str]:
        """Format column names for CSV header (replace underscores, title case)."""
        return [c.replace("_", " ").title() for c in cols]

    def _format_summary_header(self, cols: list[str]) -> list[str]:
        """Format summary column names for CSV header."""
        return [c.title() for c in cols]

    def _get_cell_value(self, result: Any, col: str) -> Any:
        """Extract and format cell value based on column name."""
        if col == "status":
            return "PASS" if result.status else "FAIL"
        elif col == "runtime_sec":
            return f"{result.runtime_sec:.6f}"  # Format with 4 decimal places
        else:
            # Get attribute directly
            return getattr(result, col)

    def _dump_implementation(self, checker: Ten8tChecker, output_file: TextIO) -> None:
        """
        Implement CSV-specific dumping logic.

        Args:
            checker: Ten8tChecker instance containing results
            output_file: File handle for writing
        """
        writer = csv.writer(
            output_file,
            quoting=self.quoting,
            # Add escapechar when QUOTE_NONE to ensure proper escaping
            escapechar='\\' if self.quoting == csv.QUOTE_NONE else None
        )

        # Write summary section if enabled
        if self.include_summary:
            pass  # CSV does not support summary info

        # Write results section if enabled
        if self.include_results:
            # Write results header
            writer.writerow(self._format_result_header(self.result_columns))

            # Write data rows
            for result in checker.results:
                row_values = [self._get_cell_value(result, col) for col in self.result_columns]
                writer.writerow(row_values)
