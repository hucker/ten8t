from typing import Any, TextIO

from ten8t.serialize._base import Ten8tDump
from ten8t.serialize._config import Ten8tDumpConfig
from ten8t.ten8t_checker import Ten8tChecker


class Ten8tDumpHTML(Ten8tDump):
    """
    HTML serialization implementation for Ten8t test results.

    Outputs test results as an HTML file with configurable columns and table formatting.
    Can include both summary and results tables.
    """

    def __init__(self, config: Ten8tDumpConfig = None):
        """
        Initialize HTML serializer with options.

        Args:
            config: Configuration object for the dump process
        """
        # Use default config if none provided
        if config is None:
            config = Ten8tDumpConfig.html_default()  # Use HTML-specific default config

        super().__init__(config)

    def _get_cell_value(self, result: Any, col: str) -> Any:
        """
        Extract and format cell value based on column name.
        """
        if col == "status":
            return "PASS" if result.status else "FAIL"
        elif col == "runtime_sec":
            return f"{result.runtime_sec:.4f}"  # Use 4 decimal places
        else:
            val = getattr(result, col, None)
            return val if val is not None else ""

    def _format_header(self, cols: list[str]) -> list[str]:
        """
        Format column headers for HTML table.

        Args:
            cols (list[str]): List of column names to format.

        Returns:
            list[str]: Formatted column names suitable for HTML (escaped, title-cased).
        """
        return [col.replace("_", " ").title() for col in cols]

    def _dump_pre_text(self, output_file: TextIO, pre_text: str = None, title=None):
        """
        For HTML setting the pretext allows you to dump a full page (or just pass in the current
        state of the rendering page.
        """
        if self.config.pre_text:
            title = title or "Ten8t Test Results"
            if not pre_text:
                # Start the HTML document
                output_file.write("<!DOCTYPE html>\n")
                output_file.write(f"<html>\n<head>\n<title>{title}</title>\n</head>\n<body>\n")
                output_file.write("<h1>{title}</h1>\n")
            else:
                output_file.write(pre_text)

    def _dump_post_text(self, output_file: TextIO, post_text: str = None):
        """
        For HTML setting the pretext allows you to dump a full page (or just pass in the current
        state of the rendering page.
        """
        if self.config.post_text:
            if not post_text:
                output_file.write("</body>\n</html>")
            else:
                output_file.write(post_text)

    def _dump_implementation(self, checker: Ten8tChecker, output_file: TextIO) -> None:
        """
        Implement HTML-specific dumping logic.

        Args:
            checker: Ten8tChecker instance containing results
            output_file: File handle for writing output
        """

        self._dump_pre_text(output_file)

        # Add summary section if requested
        if self.include_summary:
            output_file.write("<h2>Summary</h2>\n")
            output_file.write("<table border='1'>\n<thead>\n<tr>\n")
            # Create table header for summary
            for col in self._format_header(self.summary_columns):
                output_file.write(f"<th>{col}</th>\n")
            output_file.write("</tr>\n</thead>\n<tbody>\n")

            # Get summary data
            output_file.write("<tr>\n")
            for col in self.summary_columns:
                if col == "pass":
                    value = checker.pass_count
                elif col == "fail":
                    value = checker.fail_count
                elif col == "skip":
                    value = checker.skip_count
                elif col == "perfect_run":
                    value = checker.perfect_run
                elif col == "warn":
                    value = checker.warn_count
                elif col == "duration_seconds":
                    value = f"{float(checker.duration_seconds):.03f}"
                elif col == "end_time":
                    t = checker.end_time
                    value = t.strftime("%H:%M:%S.%f")[:-3]
                elif col == "start_time":
                    t = checker.start_time
                    value = t.strftime("%H:%M:%S.%f")[:-3]
                else:
                    value = ""

                # Add cell value
                output_file.write(f"<td>{value}</td>\n")
            output_file.write("</tr>\n</tbody>\n</table>\n")

        # Add results section if requested
        if self.include_results:
            output_file.write("<h2>Results</h2>\n")
            output_file.write("<table border='1'>\n<thead>\n<tr>\n")
            # Create table header
            for col in self._format_header(self.result_columns):
                output_file.write(f"<th>{col}</th>\n")
            output_file.write("</tr>\n</thead>\n<tbody>\n")

            # Create rows for result data
            for result in checker.results:
                output_file.write("<tr>\n")
                for col in self.result_columns:
                    val = self._get_cell_value(result, col)

                    # Escape special HTML characters
                    if isinstance(val, str) and val:
                        val = val.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

                    # Add quotes to strings if configured
                    if self.config.quoted_strings and isinstance(val, str) and val:
                        val = f"<code>{val}</code>"

                    # Write cell value
                    output_file.write(f"<td>{val}</td>\n")
                output_file.write("</tr>\n")

            output_file.write("</tbody>\n</table>\n")

        self._dump_post_text(output_file)
