"""
Markdown serialization implementation for Ten8t test results.
"""

from typing import Any, TextIO

from ten8t.serialize._base import Ten8tDump
from ten8t.serialize._config import Ten8tDumpConfig
from ten8t.ten8t_checker import Ten8tChecker


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

    def _format_header(self, cols: list[str]) -> list[str]:
        """Format column names for Markdown header (replace underscores, title case)."""
        if self.config.autobreak_headers:
            return [c.replace("_", "<br>").title() for c in cols]
        else:
            return [c.replace("_", " ").title() for c in cols]

    def _format_alignment_row(self, cols: list[str]) -> str:
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

    def _dump_implementation(self, checker: Ten8tChecker, output_file: TextIO) -> None:
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
