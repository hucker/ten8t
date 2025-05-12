"""
Test the serialization code.  At this time this code is VERY crude.

It creates each of the file types using the exposed save functions.  All it does is verifies that a file is created
and that the file has the correct name and the sizes is aproximately correct.  A lot needs to work to get this
far but these tests could be MUCH better.

"""

import json
import pathlib
import sqlite3

import pytest

from src import ten8t as t8
from ten8t import Ten8tDumpSQLite
from ten8t.serialize import Ten8tDumpHTML, ten8t_save_sqlite


def get_file_size(file_path: pathlib.Path | str) -> int:
    """
    Returns the size of a file in bytes. Returns 0 in case of errors.

    Args:
        file_path: A pathlib.Path object or a string representing the path to the file

    Returns:
        int: The size of the file in bytes, or 0 if the file doesn't exist or is a directory
    """
    path = pathlib.Path(file_path) if isinstance(file_path, str) else file_path

    if not path.exists() or not path.is_file() or path.is_dir():
        return 0

    try:
        return path.stat().st_size
    except Exception:
        # Handle any other exceptions that might occur
        return 0


@pytest.fixture
def folder(folder="serialize_output"):
    """
    Fixture that creates a folder and provides it for tests.

    Args:
        folder: Directory to create (default: "serialize_output")

    Returns:
        Path object pointing to the created directory
    """
    output_dir = pathlib.Path(folder)
    output_dir.mkdir(exist_ok=True)

    yield output_dir


@pytest.fixture
def checker_with_simple_check():
    """
    Fixture that creates a Ten8tChecker with a simple check function.
    """

    def simple_check_function():
        """Simple check function that yields three values."""
        yield t8.TR(status=True, msg="Tests Pass.")
        yield t8.TR(status=False, msg="Tests Fail.")
        yield t8.TR(status=True, msg="Tests Pass.")

    checker = t8.Ten8tChecker(check_functions=[simple_check_function], name="SimpleChecker")
    checker.run_all()
    return checker


@pytest.mark.parametrize(
    "output_format,save_function,file_extension,min_size,config_factory",
    [
        (
                "CSV",
                t8.ten8t_save_csv,
                "csv",
                500,
                lambda file: t8.Ten8tDumpConfig.csv_default(output_file=file)
        ),
        (
                "Markdown",
                t8.ten8t_save_md,
                "md",
                1000,
                lambda file: t8.Ten8tDumpConfig(show_summary=True, show_results=True, output_file=file)
        ),
        (
                "Excel",
                t8.ten8t_save_xls,
                "xlsx",
                6000,
                lambda file: t8.Ten8tDumpConfig.excel_default(output_file=file)
        ),
    ]
)
def test_output_formats(folder, checker_with_simple_check, output_format, save_function,
                        file_extension, min_size, config_factory):
    """
    Parameterized test for different output formats (CSV, Markdown, Excel).

    Tests that each format can be saved properly and has the expected minimum file size.

    This BARELY qualifies as a test and is just here to exercise that a file is created that
    has the minimum amount of info.


    """
    # Set up the output file path
    output_file = f"{folder}/test_output.{file_extension}"

    # Delete the file if it already exists.  Normally we might delete
    # these as part of the test, but it is nice to be able to look at them
    # to verify that they are correct.
    pathlib.Path(output_file).unlink(missing_ok=True)

    assert pathlib.Path(output_file).exists() is False

    # Create the configuration for this format
    cfg = config_factory(output_file)

    # Save using the appropriate function
    save_function(checker_with_simple_check, cfg)

    # Assert file existence and minimum size
    assert pathlib.Path(output_file).exists(), f"{output_format} file was not created"
    assert get_file_size(output_file) > min_size, f"{output_format} file size is too small"


def test_html_format(checker_with_simple_check):
    output_file = f"serialize_output/test_output.html"

    # Delete the file if it already exists
    pathlib.Path(output_file).unlink(missing_ok=True)

    # Save using the appropriate function
    cfg = t8.Ten8tDumpConfig.html_default(output_file=output_file)
    html_out = Ten8tDumpHTML(config=cfg)
    html_out.dump(checker_with_simple_check)

    # Assert file existence and minimum size
    assert pathlib.Path(output_file).exists(), f"HTML file was not created"
    assert get_file_size(output_file) > 100, f"HTML file size is too small"


def test_sqlite(checker_with_simple_check):
    """
    Verify that we can serialize to a SQLite database.

    TODO: This test could be far more rigorous, but for now it verifies most of a round trip through the data
          which lets you know that the residual error would be a missing field.

    WARNING: THere is definitely an issue if the information in the database has an old schema that is not compatible.
             At this time you should read the version field from the header and maker sure you are compatible.
    """
    db_file = f"serialize_output/ten8t.sqlite"
    pathlib.Path(db_file).unlink(missing_ok=True)
    # cfg = t8.Ten8tDumpConfig.sqlite_default(sqlite_file=db_file)
    sql_out = Ten8tDumpSQLite(db_file=db_file)
    sql_out.dump(checker_with_simple_check)
    assert pathlib.Path(db_file).exists(), f"SQL file was not created"
    validate_checker_with_simple_check(db_file=db_file, table_name=sql_out.table_name)


def xxx_test_sqlite_legacy(checker_with_simple_check):
    """
    Verify that we can serialize to a SQLite database.

    TODO: This test could be far more rigorous, but for now it verifies most of a round trip through the data
          which lets you know that the residual error would be a missing field.

    WARNING: THere is definitely an issue if the information in the database has an old schema that is not compatible.
             At this time you should read the version field from the header and maker sure you are compatible.
    """
    db_file = f"serialize_output/ten8t.sqlite"
    pathlib.Path(db_file).unlink(missing_ok=True)
    # cfg = t8.Ten8tDumpConfig.sqlite_default(sqlite_file=db_file)
    ten8t_save_sqlite(checker_with_simple_check)
    assert pathlib.Path(db_file).exists(), f"SQL file was not created"
    validate_checker_with_simple_check(db_file=db_file, table_name='ten8t_results')


def validate_checker_with_simple_check(db_file: str, table_name: str = None):
    # Now verify the data exists.
    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            # Query to get the latest timestamp from the table
            cursor.execute(f"""
                SELECT datetime,header,results 
                FROM {table_name} 
                WHERE datetime = (SELECT MAX(datetime) FROM {table_name});

            """)

            result = cursor.fetchone()
            cols = [desc[0] for desc in cursor.description]
            rec_dict = dict(zip(cols, result))

    except sqlite3.Error as e:
        assert False, f"Database error: {e}"
        return None

    assert len(rec_dict) == 3, f"Expected 3 columns in the results, got {len(rec_dict)}"
    assert set(rec_dict.keys()) == set(['datetime', 'header', 'results'])

    header = json.loads(rec_dict['header'])
    results = json.loads(rec_dict['results'])

    assert header['name'] == 'SimpleChecker'
    assert header['start_time']
    assert header['end_time']
    assert 0 < header['duration_seconds'] < 1, "Should be well under 1 second"
    assert len(header['functions']) == 1
    assert header['pass_count'] == 2
    assert header['fail_count'] == 1
    assert header['skip_count'] == 0
    assert header['total_count'] == 3
    assert header['clean_run'] is True
    assert header['perfect_run'] is False
    assert header['__version__'] == t8.version("ten8t")

    # At this point we can do ALOT of tests
    assert len(results) == 3
    assert results[0]['msg'] == "Tests Pass."
    assert results[1]['msg'] == "Tests Fail."
    assert results[2]['msg'] == "Tests Pass."

    assert results[0]['msg_text'] == "Tests Pass."
    assert results[1]['msg_text'] == "Tests Fail."
    assert results[2]['msg_text'] == "Tests Pass."

    assert results[0]['msg_rendered'] == "Tests Pass."
    assert results[1]['msg_rendered'] == "Tests Fail."
    assert results[2]['msg_rendered'] == "Tests Pass."

    assert results[0]['func_name'] == "simple_check_function"
    assert results[1]['func_name'] == "simple_check_function"
    assert results[2]['func_name'] == "simple_check_function"

    assert results[0]['status'] is True
    assert results[1]['status'] is False
    assert results[2]['status'] is True

    assert results[0]['skipped'] is False
    assert results[1]['skipped'] is False
    assert results[2]['skipped'] is False

    assert results[0]['attempts'] == 1
    assert results[1]['attempts'] == 1
    assert results[2]['attempts'] == 1

    assert results[0]['count'] == 1
    assert results[1]['count'] == 2
    assert results[2]['count'] == 3

    assert results[0]['doc'] == 'Simple check function that yields three values.'
    assert results[1]['doc'] == 'Simple check function that yields three values.'
    assert results[2]['doc'] == 'Simple check function that yields three values.'
