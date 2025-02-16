"""
This module provides functions for conducting PDF file checks and handling their responses.

The main feature is to extract tables with the following headings.

RuleId  Description Status


"""

from typing import Generator, Sequence

import camelot  # type: ignore
import pandas as pd

from .ten8t_exception import Ten8tException
from .ten8t_result import TR
from .ten8t_util import str_to_bool


def extract_tables_from_pdf(file_path: str,
                            required_columns: Sequence[str] | None = None,
                            pages: str = 'all') -> list[pd.DataFrame]:
    """
    Extracts tables from a PDF file that include specified columns, and returns them in a list.


        | RuleID     | Status | Skip  | None          |
        |------------|--------|-------|---------------|
        | Rule ID 1  | pass   | no    | Rule desc 1   |
        | Rule ID 2  | fail   | yes   | Rule desc 2   |
        |    ...     |  ...   |  ...  |     ...       |

    Args:
        file_path: The path to the PDF file.
        required_columns: The list of columns that must be present in the table.
            Defaults to ["RuleId", "Note", "Status"].
        pages: The pages of the PDF to process. It could be 'all', a range like '1-7', or
            specific pages like '1,3,5'. Defaults to 'all'.

    Returns:
        A list of pandas DataFrames representing the tables extracted from the PDF file.
    """
    required_columns = required_columns or ["RuleId", "Note", "Status"]
    filtered_tables = []
    try:
        tables = camelot.read_pdf(file_path, flavor='stream', pages=pages)
        for table in tables:
            # The table that camelot returns seems to have the columns in
            # the first row, this code moves those values into column names.
            df = table.df
            df.columns = df.iloc[0]
            df = df.drop(df.index[0])
            if set(required_columns).issubset(df.columns):
                filtered_tables.append(df)
    except IOError as ioex:
        raise Ten8tException(f"IO Error reading PDF file {file_path}.") from ioex
    except Exception as exc:
        raise Ten8tException(f"Error extracting tables from PDF: {file_path}") from exc

    return filtered_tables


DEFAULT_COL_NAMES = {
    'status_col': 'Status',
    'note_col': 'Note',
    'rule_col': 'RuleId',
    'skip_col': 'Skip',
}


def rule_from_pdf_rule_ids(file_path: str,
                           rule_id: str,
                           default_msg: str | None = None,
                           col_names: dict | None = None,
                           max_results: int = 1,
                           pages="all") -> Generator[TR, None, None]:
    """
        Yield matching rule ID results from tables contained in a specified PDF file.


        The tables within the PDF file are expected to have the following columns structure with these default names:

        Reads tables from a specified PDF file and inspects each table for data that matches
        the supplied `rule_id`. For each match found, the function extracts the corresponding status, note,
        and skip values, and yields these in a namedtuple. If multiple tables exist or the `rule_id` does not
        match any table, the function continues execution.

        Parameters:
        ----------
        file_path : str
           Path to the PDF file to extract tables from.
        rule_id : str
           Specific rule ID to search for within the tables.
        default_msg : str, optional
           Default message to return with the rule result. If provided, it overrides column name information.
           Defaults to None.
        col_names : dict, optional
           Dictionary for renaming column names. Defaults to None.
        max_results : int, optional
           Maximum number of results to yield. The function raises an exception when exceed this number. Defaults to 1.
        pages : str
           Specific pages from the PDF file to be read. Defaults to 'all'.

        Yields:
        -------
        namedtuple
           Namedtuple represented by BR where:
           `status` (bool) : Indicates 'pass' if True and 'fail' if False.
           `msg` (str) : Contains messages or notes associated with the rule.
           `skipped` (bool) : Indicates if the rule was skipped. True if yes, False otherwise.

        Raises:
        -------
        Ten8tException
           If the number of yielded results exceeds the maximum limit specified by `max_results`.
        """
    col_names = DEFAULT_COL_NAMES | col_names if col_names else DEFAULT_COL_NAMES
    status_col = col_names['status_col']
    note_col = col_names['note_col']
    rule_col = col_names['rule_col']
    skip_col = col_names['skip_col']

    tables = extract_tables_from_pdf(file_path,
                                     required_columns=[rule_col, note_col, status_col],
                                     pages=pages)
    count = 0
    for table in tables:
        if rule_col in table.columns:
            df = table[table[rule_col] == rule_id]
            for _, rule_data in df.iterrows():
                status = str_to_bool(rule_data[status_col])
                skip = rule_data.get(skip_col, False)
                msg = default_msg or rule_data[note_col]
                yield TR(status=status, msg=msg, skipped=skip)
                count += 1
                if count > max_results:
                    raise Ten8tException(f"Maximum number of results ({max_results}) exceeded for {file_path}")
    if count == 0:
        yield TR(status=None, skipped=True, msg=f"No results found in {file_path}")
