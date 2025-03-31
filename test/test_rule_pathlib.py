import pathlib
import time

import pytest

from src import ten8t as t8


def test_rule_file_exist():
    """Verify that we can use the rule_path_exists rule in a function that we build."""

    @t8.attributes(tag="tag")
    def check_rule1():
        yield t8.rule_path_exists(path_="./rule_files_/my_file.txt")

    @t8.attributes(tag="tag")
    def check_rule2():
        yield t8.rule_path_exists(path_="./rule_files_/my_file.dummy")

    for result in t8.Ten8tFunction(check_rule1, '')():
        assert result.status

    for result in t8.Ten8tFunction(check_rule2, '')():
        assert result.status is False


@pytest.mark.parametrize("paths", [
    (["rule_files_/my_file.txt", "rule_files_/my_big_file.txt"]),  # Test with a list of paths
    ("rule_files_/my_file.txt rule_files_/my_big_file.txt"),  # Test with a string of paths

])
def test_rule_files_as_list_exist(paths):
    @t8.attributes(tag="tag")
    def check_files():
        yield from t8.rule_paths_exist(paths=paths)

    for result in t8.Ten8tFunction(check_files)():
        assert result.status is True


def test_rule_files_as_string_pathlib_exist():
    path = "rule_files_/my_file.txt rule_files_/my_file.txt"

    @t8.attributes(tag="tag")
    def check_files():
        yield from t8.rule_paths_exist(paths=path)

    for result in t8.Ten8tFunction(check_files)():
        assert result.status is True


@pytest.mark.parametrize("path_string, expected_status", [
    # 1 valid path
    ("rule_files_/my_file.txt", True),

    # 2 valid paths, space-separated
    ("rule_files_/my_file.txt rule_files_/my_file.txt", True),

    # 1 invalid (non-existing) path (assuming it doesn't exist)
    ("rule_files_/nonexistent.txt", False),

    # mixed valid and invalid paths
    ("rule_files_/nonexistent.txt rule_files_/nonexistent.txt", False),

])
def test_rule_files_as_string_pathlib_exist(path_string, expected_status):
    """Handle various cases of arbitrary string cases.

    This is a little bit testing the code that decodes the path list but I think
    it is important to make sure this capability is working.
    """

    @t8.attributes(tag="tag")
    def check_files():
        yield from t8.rule_paths_exist(paths=path_string)

    for result in t8.Ten8tFunction(check_files)():
        assert result.status is expected_status


def test_rule_files_exist_no_files():
    """ This test the flag that determines what to do if files don't exist"""
    path = ""

    @t8.attributes(tag="tag")
    def check_true_no_files():
        yield from t8.rule_paths_exist(paths=path, no_paths_pass_status=True)

    @t8.attributes(tag="tag")
    def check_false_no_files():
        yield from t8.rule_paths_exist(paths=path, no_paths_pass_status=False)

    for result in t8.Ten8tFunction(check_true_no_files)():
        assert result.status is True

    for result in t8.Ten8tFunction(check_false_no_files)():
        assert result.status is False



def test_rule_large_files():
    """Verify that we can use the rule_path_exists rule in a function that we build."""

    @t8.attributes(tag="tag")
    def check_rule1():
        for result_ in t8.rule_large_files(folders="./rule_files_", pattern="my_big_file.txt", max_size=1000):
            yield result_

    def check_rule2():
        for result_ in t8.rule_large_files(folders="./rule_files_", pattern="my_big_file.txt", max_size=2000):
            yield result_

    ch = t8.Ten8tChecker(check_functions=[check_rule1, check_rule2])
    results = ch.run_all()
    assert results[0].status is False
    assert results[1].status is True



def test_rule_large_file_bad_setup():
    """Handled exception for file size."""
    def check_rule_bad_setup():
        yield from t8.rule_large_files(folders="./rule_files_",
                                       pattern="*.foobar",
                                       max_size=-50,
                                       no_files_pass_status=True)

    s_func1 = t8.Ten8tFunction(check_rule_bad_setup)
    for result in s_func1():
        assert result.status is False
        assert result.except_


@pytest.mark.parametrize(
    "folder_str, no_files_pass_status, expected_status",
    [
        # Existing folder, no files match
        ("./rule_files_", True, True),
        ("./rule_files_", False, False),

        # Non-existent folder
        ("./nonexistent_folder", True, True),
        ("./nonexistent_folder", False, False),
    ]
)
def test_rule_large_files_parameterized(folder_str, no_files_pass_status, expected_status):
    """
    Verify the rule_large_files behavior with folder paths as both strings and pathlib.Path objects.

    Args:
        folder_str (str): String folder path to check.
        no_files_pass_status (bool): Status to return when no matching files are found.
        expected_status (bool): Expected result status from rule evaluation.

    """
    for folder in [folder_str, pathlib.Path(folder_str)]:

        @t8.attributes(tag="tag")
        def check_rule_large_files():
            yield from t8.rule_large_files(
                folders=folder,
                pattern="*.foobar",
                max_size=50,
                no_files_pass_status=no_files_pass_status
            )

        s_func = t8.Ten8tFunction(check_rule_large_files)
        for result in s_func():
            assert result.status is expected_status



@pytest.mark.parametrize("days, hours, minutes, seconds", [
    (0, 0, 0, -1),  # Test case for seconds=-1
    (0, 0, -1, 0),  # Test case for minutes=-1
    (0, -1, 0, 0),  # Test case for hours=-1
    (-1, 0, 0, 0),  # Test case for days=1
    (0, 0, 0, 0)  # Test case for all zero
])
def test_bad_stale_file_setup(days, hours, minutes, seconds):
    """Test that the check_rule_file function works with different values of days, hours, minutes, and seconds"""
    file_path = pathlib.Path("./rule_files_")

    def check_rule_files():
        yield from t8.rule_stale_files(folders=file_path, pattern="my_file*.txt", days=days, hours=hours,
                                       minutes=minutes, seconds=seconds)

    s_func = t8.Ten8tFunction(check_rule_files)
    for result in s_func():
        assert result.except_
        assert result.status is False


def test_stale_file_no_match():
    """No files is an interesting case as it"""
    file_path = pathlib.Path("./rule_files_")

    def check_rule_missing_true():
        yield from t8.rule_stale_files(folders=file_path, pattern="my_file*.foobar", days=0, hours=0, minutes=0,
                                       seconds=.5, no_files_pass_status=True)

    def check_rule_missing_false():
        yield from t8.rule_stale_files(folders=file_path, pattern="my_file*.foobar", days=0, hours=0, minutes=0,
                                       seconds=.5, no_files_pass_status=False)

    s_func1 = t8.Ten8tFunction(check_rule_missing_true)
    for result in s_func1():
        assert result.status

    s_func2 = t8.Ten8tFunction(check_rule_missing_false)
    for result in s_func2():
        assert not result.status


def test_stale_files_noage():
    """
    Verify that we can use the rule_stale_files rule in a function that we build.

    This is kind of ugly but having individual functions. All of these functions should reduce
    to the same number of seconds so the test can run with the same delay
    """
    file_path = pathlib.Path("./rule_files_")

    @t8.attributes(tag="tag")
    def check_rule_no_age():
        yield from t8.rule_stale_files(folders=file_path,
                                       pattern="my_file*.txt",
                                       days=0,
                                       hours=0,
                                       minutes=0,
                                       seconds=0)

    s_func1 = t8.Ten8tFunction(check_rule_no_age, '')
    for result in s_func1():
        assert not result.status
        assert result.traceback
        assert result.except_
        assert "Age for stale file check" in result.msg


def test_stale_files():
    """
    Verify that we can use the rule_stale_files rule in a function that we build.

    This is kind of ugly but having individual functions. All of these functions should reduce
    to the same number of seconds so the test can run with the same delay
    """
    file_path = pathlib.Path("./rule_files_")

    @t8.attributes(tag="tag")
    def check_rule_sec():
        yield from t8.rule_stale_files(folders=file_path,
                                       pattern="my_file*.txt",
                                       days=0,
                                       hours=0,
                                       minutes=0,
                                       seconds=.5)

    @t8.attributes(tag="tag")
    def check_rule_min():
        yield from t8.rule_stale_files(folders=file_path,
                                       pattern="my_file*.txt",
                                       days=0,
                                       hours=0,
                                       minutes=1 / (2 * 60.0),
                                       seconds=0)

    @t8.attributes(tag="tag")
    def check_rule_hour():
        yield from t8.rule_stale_files(folders=file_path,
                                       pattern="my_file*.txt",
                                       days=0,
                                       hours=1 / (2 * 3600.0),
                                       minutes=0,
                                       seconds=0)

    @t8.attributes(tag="tag")
    def check_rule_day():
        yield from t8.rule_stale_files(folders=file_path,
                                       pattern="my_file*.txt",
                                       days=1 / (2 * 86400.0),
                                       hours=0,
                                       minutes=0,
                                       seconds=0)

    # We need to check that each of the units is used
    for rule in [check_rule_sec, check_rule_min, check_rule_hour, check_rule_day]:

        # Touch the file
        pathlib.Path("./rule_files_/my_file.txt").touch()

        s_func1 = t8.Ten8tFunction(rule, '')
        for result in s_func1():
            assert result.status

        # Wait for a bit more than .5 sec
        time.sleep(.6)

        results = list(s_func1())

        for result in results:
            assert not result.status


@pytest.mark.xfail(reason="Reason, this feature will be fixed in a future branch and is caused by a " \
                          "single summary being elevated to non-summary.")
def test_stale_file_summary():
    """
    Verify that the stale check works with summary only.
    """
    file_path = pathlib.Path("./rule_files_")

    @t8.attributes(tag="tag")
    def check_rule_sec():
        yield from t8.rule_stale_files(folders=file_path, pattern="my_file*.txt", days=0, hours=0, minutes=0,
                                       seconds=.5, summary_only=True, summary_name="Rule_files_ stale check")

    sfunc = t8.Ten8tFunction(check_rule_sec)
    # Touch the file
    pathlib.Path("./rule_files_/my_file.txt").touch()

    for result in sfunc():
        assert result.status
        assert result.summary_result
        assert result.msg.startswith("Rule_files_ stale check had")


@pytest.mark.parametrize(
    "test_name, folder, max_files, expected_status",
    [
        ("test_max_files_too_many", ["./rule_files_"], 10, True),
        ("test_rule_on_boundary", ["./rule_files_"], 2, True),
        ("test_max_files_too_few", ["./rule_files_"], 1, False),
    ]
)
def test_check_rule(test_name, folder, max_files, expected_status):
    @t8.attributes(tag="tag")
    def check_rule():
        yield from t8.rule_max_files(folders=folder, max_files=max_files)

    for result in check_rule():
        assert result.status is expected_status


def test_bad_max_files():
    def check_rule1():
        yield from t8.rule_max_files(folders=["./rule_files_"], max_files=[10, 20, 30])

    sfunc = t8.Ten8tFunction(check_rule1)
    results = list(sfunc())
    assert len(results) == 1
    assert results[0].except_
    assert results[0].status is False


def test_max_file_summary():
    @t8.attributes(tag="tag")
    def check_rule():
        yield from t8.rule_max_files(folders='./rule_files_',
                                     max_files=10,
                                     summary_only=True,
                                     summary_name="Rule_files max check.")

    for result in check_rule():
        assert result.status is True

