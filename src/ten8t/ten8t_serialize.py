"""
Ten8t Serialization Module

This module provides classes for serializing Ten8tChecker test results to various formats.
It uses an abstract base class Ten8tDump as the foundation, with concrete implementations for
different output formats such as CSV and Markdown.

The module supports:
- Configurable column selection from test results
- Output to file or standard output
- Header inclusion for formats that support it
- Proper handling of special characters and formatting
- Format-specific customization options

Examples:
    Basic usage with CSV output:

    ```python
    from ten8t import Ten8tChecker
    from ten8t.serialization import Ten8tDumpCSV

    # Create and run tests
    checker = Ten8tChecker()
    checker.test_something()

    # Save all results to CSV file
    dumper = Ten8tDumpCSV()
    dumper.dump(checker, "test_results.csv")

    # Save selected columns to console
    dumper = Ten8tDumpCSV(columns=["status", "msg", "runtime_sec"])
    dumper.dump(checker)
    ```

    Using Markdown output:

    ```python
    from ten8t import Ten8tChecker
    from ten8t.serialization import Ten8tDumpMarkdown

    checker = Ten8tChecker()
    # ... run tests ...

    # Create markdown report with header
    dumper = Ten8tDumpMarkdown(include_header=True)
    dumper.dump(checker, "test_results.md")
    ```
"""

import csv
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, TextIO

from .ten8t_checker import Ten8tChecker
from .ten8t_util import StrListOrNone, StrOrNone


@dataclass
class Ten8tDumpConfig:
    show_summary: bool = True
    show_results: bool = True
    summary_columns: StrListOrNone = 'all'
    result_columns: StrListOrNone = 'all'
    output_file: StrOrNone = None  # None will default to stdout
    quoted_strings:bool=False # Should strings be quoted
    result_sheet_name:str=None
    summary_sheet_name:str=None
    summary_title:str=None
    result_title:str=None
    autobreak_headers:bool=True # for multiword columns this forces a break.

    # Define valid columns
    VALID_SUMMARY_COLUMNS = ["pass", "fail", "skip",
                             'duration_seconds','start_time','end_time',
                             'perfect_run']

    VALID_RESULT_COLUMNS = [
        "status", "msg_rendered", "ruid", "tag", "level", "phase",
        "skipped", "count", "func_name", "thread_id", "runtime_sec",
        "summary_result", "msg"
    ]

    @classmethod
    def summary_only(cls, **kwargs):
        """Creates a configuration for summary-only output."""
        return cls(show_summary=True, show_results=False, **kwargs)

    @classmethod
    def result_only(cls, **kwargs):
        """Creates a configuration for result-only output."""
        return cls(show_summary=False, show_results=True, **kwargs)

    @classmethod
    def csv_default(cls, **kwargs):
        """Creates a default configuration for CSV output."""
        return cls(show_summary=False, show_results=True, quoted_strings=True, **kwargs)

    @classmethod
    def markdown_default(cls, **kwargs):
        """Creates a default configuration for Markdown output."""
        return cls(
            show_summary=True,
            show_results=True,
            summary_title="### Summary Information",
            result_title="### Raw Results",
            **kwargs,
        )

    @classmethod
    def excel_default(cls, **kwargs):
        """Creates a default configuration for Excel output."""
        return cls(
            show_summary=True,
            show_results=True,
            summary_sheet_name="Summary",
            result_sheet_name="Result",
            **kwargs,
        )

    def __post_init__(self):
        """Validate column names after initialization."""
        self._validate_columns(self.summary_columns, self.VALID_SUMMARY_COLUMNS, "summary_columns")
        self._validate_columns(self.result_columns, self.VALID_RESULT_COLUMNS, "result_columns")

    def _validate_columns(self, columns: StrListOrNone, valid_columns: List[str], param_name: str) -> None:
        """Helper method to validate column lists."""
        if columns is None or columns == 'all':
            return

        # Convert to list if it's a string
        cols = columns if isinstance(columns, list) else [columns]

        # Check for invalid column names
        invalid_cols = set(cols) - set(valid_columns)
        if invalid_cols:
            raise ValueError(
                f"Invalid {param_name} specified: {invalid_cols}. "
                f"Valid columns are: {valid_columns}"
            )


class Ten8tDump(ABC):
    """
    Abstract base class for serializing Ten8t test results to various formats.

    Provides the interface and common functionality for all serialization formats.
    """

    def __init__(self, config: Ten8tDumpConfig = None):
        """
        Initialize the Ten8tDump with configuration.

        Args:
            config: Configuration object for the dump process
        """
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
            return Ten8tDumpConfig.VALID_SUMMARY_COLUMNS.copy()

        return columns if isinstance(columns, list) else [columns]

    def _process_result_columns(self) -> List[str]:
        """Process result columns from config into a valid list."""
        columns = self.config.result_columns

        if not columns or columns == 'all':
            return Ten8tDumpConfig.VALID_RESULT_COLUMNS.copy()

        return columns if isinstance(columns, list) else [columns]

    def get_output_file(self) -> TextIO:
        """
        Get file handle for output based on config.

        Returns:
            File handle for writing
        """
        filename = self.config.output_file
        if filename:
            return open(filename, "w", newline="")
        return sys.stdout

    def dump(self, checker: 'Ten8tChecker') -> None:
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

    @abstractmethod
    def _dump_implementation(self, checker: 'Ten8tChecker', output_file: TextIO) -> None:
        """
        Implementation-specific dumping logic to be overridden by subclasses.

        Args:
            checker: Ten8tChecker instance containing results to dump
            output_file: File handle for writing output
        """
        pass


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

    def _format_result_header(self, cols: List[str]) -> List[str]:
        """Format column names for CSV header (replace underscores, title case)."""
        return [c.replace("_", " ").title() for c in cols]

    def _format_summary_header(self, cols: List[str]) -> List[str]:
        """Format summary column names for CSV header."""
        return [c.title() for c in cols]

    def _get_cell_value(self, result: Any, col: str) -> Any:
        """Extract and format cell value based on column name."""
        if col == "status":
            return "PASS" if result.status else "FAIL"
        elif col == "runtime_sec":
            return f"{result.runtime_sec:.4f}"  # Format with 4 decimal places
        else:
            # Get attribute directly
            return getattr(result, col)

    def _dump_implementation(self, checker: 'Ten8tChecker', output_file: TextIO) -> None:
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
            # Write summary header
            writer.writerow(self._format_summary_header(self.summary_columns))

            # Extract and write summary data
            summary = checker.summary()
            summary_row = [summary.get(col, 0) for col in self.summary_columns]
            writer.writerow(summary_row)

            # Add an empty row to separate summary from results
            if self.include_results:
                writer.writerow([])

        # Write results section if enabled
        if self.include_results:
            # Write results header
            writer.writerow(self._format_result_header(self.result_columns))

            # Write data rows
            for result in checker.results:
                row_values = [self._get_cell_value(result, col) for col in self.result_columns]
                writer.writerow(row_values)



class Ten8tDumpMarkdown(Ten8tDump):
    """
    Markdown serialization implementation for Ten8t test results.

    Outputs test results as a Markdown file with configurable columns and proper table formatting.
    Can include both summary and results tables.
    """

    def __init__(self, config: Ten8tDumpConfig = None):
        """
        Initialize Markdown serializer with options.

        Args:
            config: Configuration object for the dump process
        """
        # Use default config if none provided
        if config is None:
            config = Ten8tDumpConfig.markdown_default()  # Use default (show both summary and results)

        super().__init__(config)

    def _format_header(self, cols: List[str]) -> List[str]:
        """Format column names for Markdown header (replace underscores, title case)."""
        if self.config.autobreak_headers:
            return [c.replace("_", "<br>").title() for c in cols]
        else:
            return [c.replace("_", " ").title() for c in cols]

    def _format_alignment_row(self, cols: List[str]) -> str:
        """Create the Markdown table alignment row."""
        return "| " + " | ".join(["---" for _ in cols]) + " |"

    def _get_cell_value(self, result: Any, col: str) -> Any:
        """
        Extract and format cell value based on column name.
        """
        if col == "status":
            return "PASS" if result.status else "FAIL"
        elif col == "runtime_sec":
            return f"{result.runtime_sec:.4f}"  # Format with 4 decimal places
        else:
            # Get attribute directly
            val = getattr(result, col)
            return val if val is not None else ""

    def _dump_implementation(self, checker: 'Ten8tChecker', output_file: TextIO) -> None:
        """
        Implement Markdown-specific dumping logic.

        Args:
            checker: Ten8tChecker instance containing results
            output_file: File handle for writing output
        """
        # Add title
        output_file.write("# Ten8t Test Results\n\n")

        # Add summary section if requested
        if self.include_summary:
            output_file.write("## Summary\n\n")

            # Create summary table header
            header_row = self._format_header(self.summary_columns)
            output_file.write("| " + " | ".join(header_row) + " |\n")
            output_file.write(self._format_alignment_row(self.summary_columns) + "\n")

            # Get summary data
            summary_values = []
            for col in self.summary_columns:
                if col == "pass":
                    summary_values.append(checker.pass_count)
                elif col =='fail':
                    summary_values.append(checker.fail_count)
                elif col =='skip':
                    summary_values.append(checker.skip_count)
                elif col == 'perfect_run':
                     summary_values.append(checker.perfect_run)
                elif col =='warn':
                     summary_values.append(checker.warn_count)
                elif col == 'duration_seconds':
                    summary_values.append(f'{float(checker.duration_seconds):.03f}')
                elif col == 'end_time':
                    t = checker.end_time
                    summary_values.append(t.strftime("%H:%M:%S.%f")[:-3])
                elif col == 'start_time':
                    t = checker.start_time
                    summary_values.append(t.strftime("%H:%M:%S.%f")[:-3])
                else:
                    pass
            output_file.write("| " + " | ".join(str(value) for value in summary_values) + " |\n\n")


        # Add results section if requested
        if self.include_results:
            output_file.write("## Results\n\n")

            # Create results table header
            header_row = self._format_header(self.result_columns)
            output_file.write("| " + " | ".join(header_row) + " |\n")
            output_file.write(self._format_alignment_row(self.result_columns) + "\n")

            # Apply quoting for values if configured
            for result in checker.results:
                # Escape pipe characters in values and convert to strings
                row_values = []
                for col in self.result_columns:
                    val = self._get_cell_value(result, col)
                    # Always escape pipe characters in Markdown tables
                    val_str = str(val).replace("|", "\\|") if val is not None else ""

                    # Add quotes if configured and the value is a string
                    if self.config.quoted_strings and isinstance(val, str) and val:
                        val_str = f"`{val_str}`"

                    row_values.append(val_str)

                output_file.write("| " + " | ".join(row_values) + " |\n")


# Backward compatibility function
def ten8t_save_csv(ch: Ten8tChecker, config: Ten8tDumpConfig = None):
    """
    Legacy function for backward compatibility.

    Args:
        ch: Ten8tChecker instance containing results
        config: Configuration object for the dump process (None for default)
        quoting: CSV quoting style (if None, determined by config.quoted_strings)
    """
    # Use default config if none provided
    config = config or Ten8tDumpConfig.csv_default()

    # Create CSV dumper with config
    dumper = Ten8tDumpCSV(config)

    # Dump to the output file specified in config
    dumper.dump(ch)


def ten8t_save_md(ch: Ten8tChecker,
                  config:Ten8tDumpConfig=None):
    """
    Legacy function for backward compatibility.

    Args:
        ch: Ten8tChecker instance containing results
        csv_cols: Columns to include in CSV (None for default)
        csv_file: Output CSV filename (None for stdout)
        quoting: CSV quoting style
    """
    config = config or Ten8tDumpDefaultMarkDownConfig
    dumper = Ten8tDumpMarkdown(config)
    dumper.dump(ch)

