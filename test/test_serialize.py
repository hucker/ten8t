"""
Test the serialization code.  At this time this code is VERY crude.

It creates each of the file types using the exposed save functions.  All it does is verifies that a file is created
and that the file has the correct name and the sizes is aproximately correct.  A lot needs to work to get this
far but these tests could be MUCH better.

"""

import pathlib

import pytest

from src import ten8t as t8


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
        yield t8.TR(status=True, msg="Tests Passes.")
        yield t8.TR(status=False, msg="Tests Fails.")
        yield t8.TR(status=True, msg="Tests Passes.")

    checker = t8.Ten8tChecker(check_functions=[simple_check_function])
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
    """
    # Setup the output file path
    output_file = f"{folder}/test_output.{file_extension}"

    # Delete the file if it already exists
    pathlib.Path(output_file).unlink(missing_ok=True)

    # Create the configuration for this format
    cfg = config_factory(output_file)

    # Save using the appropriate function
    save_function(checker_with_simple_check, cfg)

    # Assert file existence and minimum size
    assert pathlib.Path(output_file).exists(), f"{output_format} file was not created"
    assert get_file_size(output_file) > min_size, f"{output_format} file size is too small"
