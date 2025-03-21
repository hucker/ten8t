"""
Ten8t CSV Output Module

This module provides functionality to save Ten8t test results to CSV files with
proper handling of field quoting and escaping. It leverages Python's built-in
csv module to ensure compatibility with standard CSV parsers and spreadsheet applications.

The module supports:
- Configurable column selection from test results
- Output to file or standard output
- Customizable CSV quoting behavior
- Proper handling of special characters in test result fields
- Pretty formatting of column headers

Examples:
    Basic usage with a Ten8tChecker instance:

    ```python
    from ten8t import Ten8tChecker, ten8t_save_csv

    # Create and run tests
    checker = Ten8tChecker(check_functions=[check1,check2,check3])
    checker.run_all()

    # Save all results to CSV file
    ten8t_save_csv(checker, None, "test_results.csv")

    # Save selected columns to console
    ten8t_save_csv(checker, ["status", "msg", "runtime_sec"], None)
    ```

    Using custom quoting behavior:

    ```python
    import csv
    from ten8t import Ten8tChecker, ten8t_save_csv

    checker = Ten8tChecker()
    # ... run tests ...

    # Quote all fields, even numeric ones
    ten8t_save_csv(checker, None, "test_results.csv", quoting=csv.QUOTE_ALL)
    ```

Available columns:
    status: Test pass/fail status
    msg: Raw test message
    msg_rendered: Formatted test message
    ruid: Unique result identifier
    tag: Test category or tag
    level: Test importance level
    phase: Test execution phase
    skipped: Whether the test was skipped
    count: Test counter value
    func_name: Name of the test function
    thread_id: ID of thread that executed the test
    runtime_sec: Test execution time in seconds
    summary_result: Summarized test result

Notes:
    - Column names in output CSV files have underscores replaced with spaces and are title-cased
    - The runtime_sec field is formatted to 4 decimal places for readability
    - When no output file is specified, results are printed to stdout
"""

import csv
import sys
from typing import TextIO

from .ten8t_checker import Ten8tChecker
from .ten8t_exception import Ten8tException
from .ten8t_util import StrListOrNone, StrOrNone, any_to_str_list


def ten8t_save_csv(ch:Ten8tChecker, csv_cols: StrListOrNone, csv_file: StrOrNone,quoting=csv.QUOTE_MINIMAL):
    """
    Save test results to a CSV file using the CSV module for proper quoting and escaping.

    Args:
        results: List of test result objects
        csv_cols: Columns to include in CSV (or None for defaults)
        csv_file: Output CSV filename (or None for stdout)
        quoting: This does its best to find strings and " them correctly.
    """

    # Define all valid column names
    valid_cols = any_to_str_list(
        "status msg_rendered ruid tag level phase skipped count func_name "
        "thread_id runtime_sec summary_result msg warn_msg info_msg except"
    )

    # Use default columns if none specified
    if not csv_cols or csv_cols=='all':
        csv_cols = valid_cols

    cols = any_to_str_list(csv_cols)



    # Check for invalid columns
    invalid_cols = set(cols) - set(valid_cols)

    if invalid_cols:
        raise Ten8tException(f"Invalid CSV cols were used ({invalid_cols}), please select from {valid_cols}")

        # Choose output destination: file or stdout
    output_file: TextIO
    if csv_file:
        output_file = open(csv_file, "w", newline="")
    else:
        output_file = sys.stdout

    try:
        # Create CSV writer with proper quoting
        writer = csv.writer(output_file, quoting=quoting)

        # Write header row with nice formatting (replace underscores with spaces and title case)
        writer.writerow([c.replace("_", " ").title() for c in cols])

        # Write data rows
        for result in ch.results:
            row_values = []
            for col in cols:
                if col == "status":
                    row_values.append("PASS" if result.status else "FAIL")
                elif col == "msg":
                    row_values.append(result.msg)
                elif col == "msg_rendered":
                    row_values.append(result.msg_rendered)
                elif col == "skipped":
                    row_values.append(1 if result.skipped else 0)
                elif col == "level":
                    row_values.append(result.level)
                elif col == "tag":
                    row_values.append(result.tag)
                elif col == "phase":
                    row_values.append(result.phase)
                elif col == "ruid":
                    row_values.append(result.ruid)
                elif col == "count":
                    row_values.append(result.count)
                elif col == "thread_id":
                    row_values.append(result.thread_id)
                elif col == "func_name":
                    row_values.append(result.func_name)
                elif col == "warn_msg":
                    row_values.append(result.warn_msg)
                elif col == "info_msg":
                    row_values.append(result.info_msg)
                elif col == "summary_result":
                    row_values.append(result.summary_result)
                elif col == "module_name":
                    row_values.append(result.module_name)
                elif col == "pkg_name":
                    row_values.append(result.pkg_name)
                elif col == "except":
                    row_values.append(1 if result.except_ else 0)
                elif col == "runtime_sec":
                    row_values.append(
                        f"{result.runtime_sec:.4f}"
                    )  # Fixed formatting to 4 decimal places

            writer.writerow(row_values)
    except Exception as e:
        raise Ten8tException(f"Error saving CSV: {e}") from e
    finally:
        # Close the file if it was opened by this function
        if csv_file and output_file != sys.stdout:
            output_file.close()
