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

    # This indent stuff is the minimum possible indent that is useful
    SPACE = ' '
    INDENT_LVL_0 = ""  # Root level, no indentation
    INDENT_LVL_1 = 1 * SPACE
    INDENT_LVL_2 = 2 * SPACE
    INDENT_LVL_3 = 3 * SPACE
    INDENT_LVL_4 = 4 * SPACE

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

    def _dump_pre_text(self, output_file: TextIO, title=None):
        """
            Write pre-text containing the HTML boilerplate if not provided.

            Using pre/post text allows you to make a valid standalone
            web page.  If you omit this you get an HTML fragment.
            Args:
                output_file: The output text stream
                pre_text: Custom pre-text to include instead of default boilerplate.
                title: Title of the HTML document.
            """
        if self.config.pre_text is not None:
            title = title or "Ten8t Test Results"
            output_file.write("<!DOCTYPE html>\n")
            output_file.write("<html>\n")
            output_file.write(f"{self.INDENT_LVL_1}<head>\n")
            output_file.write(f"{self.INDENT_LVL_2}<title>{title}</title>\n")
            output_file.write(f"{self.INDENT_LVL_1}</head>\n")
            output_file.write(f"{self.INDENT_LVL_1}<body>\n")

    def _dump_post_text(self, output_file: TextIO):
        """
            Write post-text closing the HTML document structure if not provided.

            Args:
                output_file: The output text stream
                post_text: Custom post-text to include instead of default closing tags.
            """
        if self.config.post_text is not None:
            output_file.write(f"{self.INDENT_LVL_1}</body>\n")
            output_file.write("</html>\n")

    def _dump_summary(self, checker: Ten8tChecker, output_file: TextIO, title='Summary'):
        if self.include_summary:
            output_file.write(f"{self.INDENT_LVL_1}<h2>{title}</h2>\n")
            output_file.write(f"{self.INDENT_LVL_1}<table border='1'>\n")
            output_file.write(f"{self.INDENT_LVL_2}<thead>\n")
            output_file.write(f"{self.INDENT_LVL_3}<tr>\n")
            for col in self._format_header(self.summary_columns):
                output_file.write(f"{self.INDENT_LVL_4}<th>{col}</th>\n")
            output_file.write(f"{self.INDENT_LVL_3}</tr>\n")
            output_file.write(f"{self.INDENT_LVL_2}</thead>\n")
            output_file.write(f"{self.INDENT_LVL_2}<tbody>\n")

            # Populate summary content
            output_file.write(f"{self.INDENT_LVL_3}<tr>\n")
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
                elif col == "start_time":
                    value = checker.start_time.strftime("%H:%M:%S.%f")[:-3]
                elif col == "end_time":
                    value = checker.end_time.strftime("%H:%M:%S.%f")[:-3]
                else:
                    value = ""
                output_file.write(f"{self.INDENT_LVL_4}<td>{value}</td>\n")
            output_file.write(f"{self.INDENT_LVL_3}</tr>\n")
            output_file.write(f"{self.INDENT_LVL_2}</tbody>\n")
            output_file.write(f"{self.INDENT_LVL_1}</table>\n")

    def _dump_results(self, checker: Ten8tChecker, output_file: TextIO):
        # Add results section
        if self.include_results:
            output_file.write(f"{self.INDENT_LVL_1}<h2>Results</h2>\n")
            output_file.write(f"{self.INDENT_LVL_1}<table border='1'>\n")
            output_file.write(f"{self.INDENT_LVL_2}<thead>\n")
            output_file.write(f"{self.INDENT_LVL_3}<tr>\n")
            for col in self._format_header(self.result_columns):
                output_file.write(f"{self.INDENT_LVL_4}<th>{col}</th>\n")
            output_file.write(f"{self.INDENT_LVL_3}</tr>\n")
            output_file.write(f"{self.INDENT_LVL_2}</thead>\n")
            output_file.write(f"{self.INDENT_LVL_2}<tbody>\n")

            # Populate results table
            for result in checker.results:
                output_file.write(f"{self.INDENT_LVL_3}<tr>\n")
                for col in self.result_columns:
                    value = self._get_cell_value(result, col)
                    value = (
                        value.replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                        if isinstance(value, str) and value
                        else value
                    )

                    # Add quotes around strings if configured
                    if self.config.quoted_strings and isinstance(value, str) and value:
                        value = f"<code>{value}</code>"

                    output_file.write(f"{self.INDENT_LVL_4}<td>{value}</td>\n")
                output_file.write(f"{self.INDENT_LVL_3}</tr>\n")
            output_file.write(f"{self.INDENT_LVL_2}</tbody>\n")
            output_file.write(f"{self.INDENT_LVL_1}</table>\n")

    def _dump_implementation(self, checker: Ten8tChecker, output_file: TextIO) -> None:
        """
            Implement hierarchical HTML dump with flexible pre/post-text.

            Args:
                checker: Contains test result data.
                output_file: File-like object to write the HTML.
            """

        # Write opening HTML elements
        self._dump_pre_text(output_file)
        self._dump_summary(checker, output_file)
        self._dump_results(checker, output_file)

        # Write closing HTML elements
        self._dump_post_text(output_file)
