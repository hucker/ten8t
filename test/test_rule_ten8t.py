import pathlib
import time

import pytest

import ten8t
from src.ten8t.rule_ten8t import get_file_age_in_minutes, rule_ten8t_json_file, rule_ten8t_json_files


@pytest.mark.parametrize("rule_func", [rule_ten8t_json_file, rule_ten8t_json_files])
def test_rule_imports(rule_func):
    """
    Tests the functionality of a rule function by running it through the Ten8tChecker
    and asserting the expected results. The function is parameterized to test with
    multiple rule functions.

    Args:
        rule_func: Callable that represents a rule function to be tested. This
            function takes a file name as input and yields or returns results to
            be processed by the Ten8tChecker.
    """

    file_name = 'rule_ten8t_results/result1.json'

    def check_func():
        yield from rule_func(file_name)

    ch = ten8t.Ten8tChecker(check_functions=[check_func])

    results = ch.run_all()
    # Assertions for expected results
    assert len(results) == 7
    assert ch.perfect_run is False
    assert ch.clean_run
    assert ch.pass_count == 4
    assert ch.fail_count == 2
    assert ch.skip_count == 1
    assert results[0].func_name == 'check_func'
    assert results[0].module_name == 'adhoc'


@pytest.mark.parametrize(
    "rule_func, pass_if_missing, should_pass",
    [
        (rule_ten8t_json_file, True, True),  # Missing file but `pass_if_missing=True`
        (rule_ten8t_json_file, False, False),  # Missing file and `pass_if_missing=False`
        (rule_ten8t_json_files, True, True),  # Same test for `rule_ten8t_json_files`
        (rule_ten8t_json_files, False, False),
    ],
)
def test_pass_if_missing(rule_func, pass_if_missing, should_pass):
    """Test that the pass_if_missing flag behaves as expected."""
    # Simulated filename that does not exist
    missing_file = "nonexistent_file.json"

    def check_func():
        yield from rule_func(missing_file, pass_if_missing=pass_if_missing)

    ch = ten8t.Ten8tChecker(check_functions=[check_func])
    results = ch.run_all()
    assert len(results) == 1
    assert results[0].status == should_pass


@pytest.mark.parametrize(
    "wait_time, expected_age_limit, should_pass",
    [
        (.2, 0.5 / 60.0, True),
        (.7, 0.5 / 60.0, False),
    ]
)
def test_file_age_check(wait_time, expected_age_limit, should_pass):
    # Define the file path
    file_path = pathlib.Path('rule_ten8t_results/result1.json')

    # Ensure the file exists
    if not file_path.is_file():
        pytest.fail(f"The file {file_path} does not exist.")

    # Touch the file to reset its modification time
    file_path.touch()

    # Wait for the specified time
    time.sleep(wait_time)

    # Get the file age in minutes
    file_age_in_minutes = get_file_age_in_minutes(file_path)

    # Adjust the assertions
    if should_pass:
        assert file_age_in_minutes <= expected_age_limit, (
            f"File is older than the expected limit: {file_age_in_minutes:.6f} > {expected_age_limit:.6f}"
        )
    else:
        assert file_age_in_minutes > expected_age_limit, (
            f"File is not old enough to fail: {file_age_in_minutes:.6f} <= {expected_age_limit:.6f}"
        )


def test_get_file_age_in_minutes_file_not_found():
    # Reference a file path that does not exist
    nonexistent_file = pathlib.Path('nonexistent_file.json')

    # Ensure the file truly does not exist
    if nonexistent_file.exists():
        pytest.fail(f"The test file {nonexistent_file} unexpectedly exists.")

    # Try to calculate age and expect FileNotFoundError
    with pytest.raises(FileNotFoundError, match=f"The file {nonexistent_file} does not exist."):
        get_file_age_in_minutes(nonexistent_file)


@pytest.mark.parametrize(
    "function_to_test, wait_time_sec, max_age_min, expected_status",
    [
        (rule_ten8t_json_file, 0.1, 1.0 / 60.0, True),  # Single file, within age limit
        (rule_ten8t_json_file, 1.2, 1.0 / 60.0, False),  # Single file, exceeds age limit
        (rule_ten8t_json_files, 0.1, 1.0 / 60.0, True),  # Multiple files, within age limit
        (rule_ten8t_json_files, 1.2, 1.0 / 60.0, False),  # Multiple files, exceeds age limit
    ]
)
def test_rule_age_check(function_to_test, wait_time_sec, max_age_min, expected_status):
    """
    Verify that file aging is handled properly by both rule_ten8t_json_file and rule_ten8t_json_files,
    basically these functions are the same when only one file is passed in.  The tests verify that both
    cases handle files that are not too old without error and that the fail when the time is too long.
    SInce the code runs in minutes the delay time and the thrsholds are set to short times.  The
    error is for 1 second and
    """

    # Define the file path
    file_path = pathlib.Path('rule_ten8t_results/result2.json')

    # Ensure the file directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Touch the file to reset its modification time
    file_path.touch()

    # Simulate the file aging
    time.sleep(wait_time_sec)

    # Define the checking function based on the function being tested
    def check_func1():
        yield from rule_ten8t_json_file(file_path, max_age_min=max_age_min)

    def check_func2():
        yield from rule_ten8t_json_files([file_path], max_age_min=max_age_min)

    # Instantiate and run the checker
    if function_to_test == rule_ten8t_json_file:
        ch = ten8t.Ten8tChecker(check_functions=[check_func1])
    else:
        ch = ten8t.Ten8tChecker(check_functions=[check_func2])

    results = ch.run_all()

    # Assertions for expected results
    assert len(results) == 1, "Expected exactly one result."
    assert results[0].status == expected_status, (
        f"Expected status {expected_status}, but got {results[0].status}. "
        f"Wait time: {wait_time_sec}, Max age: {max_age_min}."
    )


def test_rule_glob_import():
    """

    """

    def check_func():
        yield from rule_ten8t_json_files('rule_ten8t_results/result*.json')

    ch = ten8t.Ten8tChecker(check_functions=[check_func])

    results = ch.run_all()
    # Assertions for expected results
    assert len(results) == 8
