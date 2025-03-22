from dataclasses import dataclass
from typing import List

from ..ten8t_util import StrListOrNone, StrOrNone


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

