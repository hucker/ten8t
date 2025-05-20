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
        yield from rule_func(file_name, yielder=ten8t.Ten8tYieldPassFail())

    ch = ten8t.Ten8tChecker(check_functions=[check_func])

    results = ch.run_all()
    # Assertions for expected results
    assert len(results) == 7
    assert ch.perfect_run is False
    assert ch.clean_run
    assert ch.pass_count == 4
    assert ch.fail_count == 2
    assert ch.skip_count == 1
    assert results[0].module_name == 'check_module1'  # Original module from JSON file.


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
    "function_to_test, wait_time_sec, max_age_minutes, expected_status",
    [
        (rule_ten8t_json_file, 0.1, 1.0 / 60.0, True),  # Single file, within age limit
        (rule_ten8t_json_file, 1.2, 1.0 / 60.0, False),  # Single file, exceeds age limit
        (rule_ten8t_json_files, 0.1, 1.0 / 60.0, True),  # Multiple files, within age limit
        (rule_ten8t_json_files, 1.2, 1.0 / 60.0, False),  # Multiple files, exceeds age limit
    ]
)
def test_rule_age_check(function_to_test, wait_time_sec, max_age_minutes, expected_status):
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
        yield from rule_ten8t_json_file(file_path, max_age_minutes=max_age_minutes)

    def check_func2():
        yield from rule_ten8t_json_files([file_path], max_age_minutes=max_age_minutes)

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
        f"Wait time: {wait_time_sec}, Max age: {max_age_minutes}."
    )


def test_rule_glob_import():
    """
    Verify that the globbing mechanism works.
    """

    def check_func():
        yield from rule_ten8t_json_files('rule_ten8t_results/result*.json',
                                         yielder=ten8t.Ten8tYieldPassFail())

    ch = ten8t.Ten8tChecker(check_functions=[check_func])

    results = ch.run_all()
    # Assertions for expected results
    assert len(results) == 8


def test_rule_glob_ruid_check_import():
    """
    Verify that the globbing mechanism works.
    """

    @ten8t.categories(ruid='test')
    def check_func():
        yield from rule_ten8t_json_files('rule_ten8t_results/result*.json',
                                         yielder=ten8t.Ten8tYieldPassFail(),
                                         )

    ch = ten8t.Ten8tChecker(check_functions=[check_func])

    results = ch.run_all()
    # Assertions for expected results
    assert len(results) == 8


@pytest.mark.parametrize(
    "filenames, expected_result_count",
    [
        # Single space-separated string
        ("rule_ten8t_results/result1.json rule_ten8t_results/result2.json", 8),
        # List of string paths
        (["rule_ten8t_results/result1.json", "rule_ten8t_results/result2.json"], 8),
        # List of pathlib.Path objects
        ([pathlib.Path("rule_ten8t_results/result1.json"), pathlib.Path("rule_ten8t_results/result2.json")], 8),
    ]
)
def test_rule_ten8t_json_files(filenames, expected_result_count):
    """
    Parameterized test to verify using rule_ten8t_json_files with various filename input formats.
    """

    def check_func():
        yield from rule_ten8t_json_files(filenames, yielder=ten8t.Ten8tYieldPassFail())

    # Create a checker with the check function
    ch = ten8t.Ten8tChecker(check_functions=[check_func])

    # Run all the checks
    results = ch.run_all()

    # Assertions for expected results
    assert len(results) == expected_result_count, (
        f"Expected {expected_result_count} results, but found {len(results)}. "
        f"Filenames: {filenames}"
    )


def test_rule_ten8t_glob_import_with_summary():
    """Make sure the summary works picking up the file name and the count."""

    def check_func():
        yield from rule_ten8t_json_files('rule_ten8t_results/result2.json',
                                         yielder=ten8t.Ten8tYieldSummaryOnly())

    ch = ten8t.Ten8tChecker(check_functions=[check_func])

    results = ch.run_all()
    # Assertions for expected results
    assert len(results) == 1
    assert results[0].status is True
    assert 'result2.json' in results[0].msg
    assert "1 pass and 0 fail" in results[0].msg
    assert results[0].summary_result is True


def test_rule_ten8t_import_with_ruid_merge():
    """
    Verify the ruids are correctly merged.  If your load_json has a ruid and it loads data
    from a file where each entry has a ruid, this code merges them so the resulting ruid
    is something like;

    current_ruid-loaded_ruid_from_file

    In the below example the top level ruid is 'ruid_1' and the loaded ruid is 'm1_f1'

    at this point the behavior is a bit experimental.

    """

    @ten8t.categories(ruid='ruid_1')
    def check_func1():
        yield from rule_ten8t_json_files('rule_ten8t_results/result2.json',
                                         yielder=ten8t.Ten8tYieldPassFail(),
                                         ruid=check_func1.ruid,
                                         ruid_sep='_'
                                         )

    @ten8t.categories(ruid='ruid_2')
    def check_func2():
        yield from rule_ten8t_json_files('rule_ten8t_results/result1.json',
                                         yielder=ten8t.Ten8tYieldAll(),
                                         ruid=check_func2.ruid,
                                         ruid_sep='.',
                                         )

    ch = ten8t.Ten8tChecker(check_functions=[check_func1, check_func2], auto_ruid=True)
    results = ch.run_all()
    assert results[0].ruid == "ruid_1_m1_f1"
    assert results[1].ruid == "ruid_2.m1_f1"

    # Checkfunc2 has yields a summary which should also have the 'ruid_2' rather than the combined ruid.
    summaray_results = [r for r in results if r.summary_result]
    assert len(summaray_results) == 1
    assert summaray_results[0].ruid == "ruid_2"


def test_rule_ten8t_file_does_not_exist():
    @ten8t.categories(ruid='ruid_1')
    def check_func1():
        yield from rule_ten8t_json_files('rule_ten8t_results/non_existing_file.json',
                                         yielder=ten8t.Ten8tYieldPassFail(),
                                         ruid=check_func1.ruid,
                                         ruid_sep='_'
                                         )

    ch = ten8t.Ten8tChecker(check_functions=[check_func1], auto_ruid=True)

    results = ch.run_all()

    assert len(results) == 1
    assert results[0].status is False
    assert results[0].ruid == "ruid_1"
    assert results[
               0].msg_text == 'The file rule_ten8t_results/non_existing_file.json does not exist default status = False'
