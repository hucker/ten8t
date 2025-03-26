from dataclasses import dataclass
from typing import List

from ..ten8t_util import StrListOrNone, StrOrNone


@dataclass
class Ten8tDumpConfig:
    """
    Configuration class for managing output settings for summary and result data.

    This class is used to configure how data summaries and results are presented
    or saved. It allows control over visibility, formatting, and the inclusion of
    specific attributes for summary and result datasets. It also provides several
    preset configurations for common output formats like CSV, Markdown, and Excel.

    At this time having a single config file support all output formats works since
    there is so much overlap, however, eventually we will need to split these up.

    Attributes:
        show_summary (bool): Whether to show the summary data.
        show_results (bool): Whether to show the result data.
        summary_columns (StrListOrNone): Columns to include in the summary output. Default is 'all'.
        result_columns (StrListOrNone): Columns to include in the result output. Default is 'all'.
        output_file (StrOrNone): File path to save the output. Defaults to stdout.
        quoted_strings (bool): Whether strings should be quoted in the output.
        result_sheet_name (str): The sheet name for results in Excel format.
        summary_sheet_name (str): The sheet name for summaries in Excel format.
        summary_title (str): Title for the summary section in certain output formats.
        result_title (str): Title for the result section in certain output formats.
        autobreak_headers (bool): Enables forced line breaks for multiword column headers.
        VALID_SUMMARY_COLUMNS (List[str]): Defines valid column names for summary data.
        VALID_RESULT_COLUMNS (List[str]): Defines valid column names for result data.
    """
    show_summary: bool = True
    show_results: bool = True
    summary_columns: StrListOrNone = 'all'
    result_columns: StrListOrNone = 'all'
    output_file: StrOrNone = None  # None will default to stdout
    quoted_strings: bool = False  # Should strings be quoted.  CSV only?
    result_sheet_name: str = None  # Excel only?
    summary_sheet_name: str = None  # Excel only?
    summary_title:str=None
    result_title:str=None
    autobreak_headers: bool = True  # for multiword columns this forces a break to keep columns narrow

    # Define valid columns
    VALID_SUMMARY_COLUMNS = ["pass", "fail", "skip",
                             'duration_seconds','start_time','end_time',
                             'perfect_run']

    VALID_RESULT_COLUMNS = [
        "status", "msg_rendered", "ruid", "tag", "level", "phase",
        "skipped", "count", "thread_id", "runtime_sec", "ttl_minutes",
        "summary_result", "msg", "func_name", "module_name", "pkg_name", "doc",
        "skip_on_none", "fail_on_none", "mit_msg", "owner_list"
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
