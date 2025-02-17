"""
TODO: This file is a mess.  I had issues getting the testing to work correctly.  I'm sure this can be 1/2 the size.
"""

import pathlib
import shutil
import tempfile
import time

import pytest
from fs.base import FS
from fs.osfs import OSFS

import ten8t.rule_fs as rule_fs
from src import ten8t


@pytest.fixture
def temp_fs():
    """Create a temporary FS object that points to the file system"""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # Create a filesystem object pointing to the temporary directory
    fs_obj = OSFS(temp_dir)

    # Create a file and write data to it
    with fs_obj.open('test.txt', 'w') as f:
        f.write('abcdefghijklmnopqrstuvwxyz')

    # Pass the temporary directory path and filesystem object to the test,
    # then cleanup after the test is done.
    yield fs_obj

    # Clean up: remove the temporary directory after the test is done.
    # This also removes all files under the directory.
    fs_obj.close()
    shutil.rmtree(temp_dir)


@pytest.fixture
def empty_fs():
    """Create a temporary empty FS object that points to the file system"""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # Create a filesystem object pointing to the temporary directory
    fs_obj = OSFS(temp_dir)

    # Pass the temporary directory path and filesystem object to the test,
    # then cleanup after the test is done.
    yield fs_obj

    # Clean up: remove the temporary directory after the test is done.
    # This also removes all files under the directory.
    fs_obj.close()
    shutil.rmtree(temp_dir)


@pytest.fixture
def os_fs():
    # Create a temporary directory and instantiate the filesystem object
    with tempfile.TemporaryDirectory() as temp_dir:
        fs_obj = OSFS(temp_dir)

        # Define our directories and file
        foo_dir = fs_obj.makedir('foo')
        quux_dir = foo_dir.makedir('quux')
        txt_file = quux_dir.open('text1.txt', 'w')

        # Create directories and file
        txt_file.write('Sample text')
        txt_file.close()

        yield fs_obj  # return the FS object to the root of temp directory


def test_os_fs(os_fs):
    assert os_fs.exists('/foo/quux/text1.txt')
    assert not os_fs.exists('/foo/quux/text2.txt')
    os_fs.remove('/foo/quux/text1.txt')
    assert not os_fs.exists('/foo/quux/text1.txt')


def test_fs_fixture_exists(temp_fs: FS):
    """This just checks that the fixture is doing what we expect"""
    assert temp_fs.exists('test.txt')

    @ten8t.attributes(tag='tag')
    def check_temp_file(filesys: FS):
        yield ten8t.TR(status=filesys.exists('test.txt'), msg="Check if file exists")

    sfunc = ten8t.Ten8tFunction(check_temp_file)
    chk = ten8t.Ten8tChecker(check_functions=[sfunc], env={'filesys': temp_fs}, auto_setup=True)
    for result in chk.run_all():
        assert result.status
        assert result.msg == 'Check if file exists'


def test_fs_rule_exists(temp_fs: FS):
    def check_temp_file(filesys: FS):
        yield from rule_fs.rule_fs_path_exists(filesys, 'test.txt')  # Should pass
        yield from rule_fs.rule_fs_path_exists(filesys, 'test1.txt')  # Should fail

    sfunc = ten8t.Ten8tFunction(check_temp_file)
    chk = ten8t.Ten8tChecker(check_functions=[sfunc], env={'filesys': temp_fs}, auto_setup=True)
    results = chk.run_all()
    assert results[0].status is True
    assert results[1].status is False


def test_fs_rule_files_exist(temp_fs: FS):
    def check_temp_files(filesys: FS):
        yield from rule_fs.rule_fs_paths_exist(filesys, ['test.txt', 'test1.txt'])  # Should pass

    sfunc = ten8t.Ten8tFunction(check_temp_files)
    chk = ten8t.Ten8tChecker(check_functions=[sfunc], env={'filesys': temp_fs}, auto_setup=True)
    results = chk.run_all()
    assert results[0].status is True
    assert results[1].status is False


@pytest.fixture
def setup_temp_file(tmp_path):
    filesys = OSFS(str(tmp_path))
    file = tmp_path / "test.txt"
    file.write_text("content")
    return filesys, str(tmp_path)


def test_oldest_file_within_max_age():
    # Get the absolute path to the current script's directory
    current_dir = pathlib.Path(__file__).resolve().parent

    # Combine it with your directory structure to the 'rule_fs' directory
    rule_fs_dir = current_dir / 'rule_fs'
    filesys = OSFS(str(rule_fs_dir))

    # Create files with current timestamps
    files = ['folder1/file1.txt', 'folder2/file2.txt']
    for file_ in files:
        with filesys.open(file_, "wt", encoding='utf8') as f:
            f.write(f"{file_}\n")
    time.sleep(.5)  # Wait for 2 seconds

    folders = ['folder1', 'folder2']
    for folder in folders:
        filesys_ = filesys.opendir(folder)
        for result in rule_fs.rule_fs_oldest_file_age(filesys_, max_age_seconds=1, patterns='*.txt'):
            assert result.status is True, "No files are too old."


def test_oldest_file_outside_max_age():
    # Get the absolute path to the current script's directory
    current_dir = pathlib.Path(__file__).resolve().parent

    # Combine it with your directory structure to the 'rule_fs' directory
    rule_fs_dir = current_dir / 'rule_fs'
    filesys = OSFS(str(rule_fs_dir))

    # Create files with current timestamps
    files = ['folder1/file1.txt', 'folder2/file2.txt']
    for file_ in files:
        with filesys.open(file_, "wt", encoding='utf8') as f:
            f.write(f"{file_}\n")
    time.sleep(1.1)  # Wait for 2 seconds

    folders = ['folder1', 'folder2']
    for folder in folders:
        filesys_ = filesys.opendir(folder)
        for result in rule_fs.rule_fs_oldest_file_age(filesys_, max_age_seconds=1, patterns='*.txt'):
            assert result.status is False, "Supposed to be too old."


def test_oldest_file_inside_max_age_no_files(empty_fs):
    for result in rule_fs.rule_fs_oldest_file_age(empty_fs, max_age_seconds=1, patterns='*.txt', no_files_skip=True):
        assert result.skipped is True
    for result in rule_fs.rule_fs_oldest_file_age(empty_fs, max_age_seconds=1, patterns='*.txt', no_files_skip=False):
        assert result.skipped is False


@pytest.mark.parametrize("seconds, expected_output", [
    (1.9996, "2.0 seconds"),  # Verify that .9996 rounds up to 2
    (1.9991, "1.999 seconds"),  # Verify that .999 rounds to .999
    (2 * 365 * 24 * 3600, "2.0 years"),
    (23 * 30 * 24 * 3600, "23.0 months"),
    (60 * 24 * 3600, "2.0 months"),
    (3600 * 24 * 365 * 5, "5.0 years"),  # A very large number of days (~5 years)
    (24 * 3600, "24.0 hours"),
    (24 * 3600 + 1, "24.0 hours"),  # This should end up right on 24 hours after 999 checks
    (24 * 3600 - 1, "24.0 hours"),  # This should end up right on 24 hours after 999 checks
    (1.9 * 24 * 3600, "45.6 hours"),
    (2 * 24 * 3600, "2.0 days"),
    (10.1 * 24 * 3600, "10.1 days"),
    (5, "5.0 seconds"),
    (1, "1.000 seconds"),
    (60, "60.0 seconds"),
    (119, "119.0 seconds"),
    (120, "2.0 minutes"),
    (3600 - 1, "60.0 minutes"),
    (3600, "60.0 minutes"),
    (3600 + 1, "60.0 minutes"),
    (119.9 * 60, "119.9 minutes"),
    (7200, "2.0 hours"),
    (86400, "24.0 hours"),
    (25 * 3600, "25.0 hours"),
    (0, "0.000 seconds"),
    (0.00001, "0.000 seconds"),
    (-0.00001, "0.000 seconds"),
    (1.0001, "1.000 seconds"),  # A small amount over 1 second
    (60 + 0.0001, "60.0 seconds"),  # A small amount over 1 minute
    (0.000001, "0.000 seconds"),  # A very small but non-zero number of seconds
    (-0.000001, "0.000 seconds"),  # A negative very small but non-zero number of seconds
])
def test_sec_format(seconds, expected_output):
    time_string = rule_fs.sec_format(seconds)
    assert time_string == expected_output

    # Test negative case too and don't do test case for -0.000
    if round(seconds, 3) != 0:
        seconds = -seconds
        time_string = rule_fs.sec_format(seconds)
        assert '-' + expected_output == time_string


@pytest.mark.parametrize("file_size, expected_result", [
    (15, True),
    (25, True),
    (26, True),  # Boundary case.
    (40, False)])
def test_within_max_size(temp_fs, file_size, expected_result):
    # We now the file size is 26
    for result in rule_fs.rule_fs_file_within_max_size(temp_fs, "test.txt", file_size):
        assert result.status is expected_result


def test_bad_max_size(temp_fs):
    for result in rule_fs.rule_fs_file_within_max_size(temp_fs, "doesnt_exist.txt", 100):
        assert result.status is False
        assert result.skipped is False
        assert all(s in result.msg.lower() for s in ['not', 'exist'])

    for result in rule_fs.rule_fs_file_within_max_size(temp_fs,
                                                       "doesnt_exist.txt",
                                                       100,
                                                       skip_if_missing=True):
        assert result.skipped is True


@pytest.mark.parametrize("file_size, expected_output", [
    # Edge case to get plural right
    (0, "0.0 Bytes"),
    (1, "1.0 Byte"),
    (1024, "1.0 kB"),
    (1048576, "1.0 MB"),
    (1073741824, "1.1 GB"),
    (1099511627776, "1.1 TB"),
    (1500, "1.5 kB"),
    (1536000, "1.5 MB"),
    (1572864000, "1.6 GB"),
    (500, "500.0 Bytes"),
    (500000, "500.0 kB"),
    (500000000, "500.0 MB"),
    (500000000000, "500.0 GB"),
    (500000000000000, "500.0 TB"),
    (500000000000000000, "500.0 PB"),
])
def test_human_readable_size(file_size, expected_output):
    output = rule_fs.human_readable_size(file_size, binary=False)
    assert output == expected_output


@pytest.mark.parametrize("file_size, expected_output", [
    # Edge case to get plural right
    (0, "0.0 Bytes"),
    (1, "1.0 Byte"),
    (1024, "1.0 KiB"),
    (1048576, "1.0 MiB"),
    (1073741824, "1.0 GiB"),
    (1099511627776, "1.0 TiB"),
    (1500, "1.5 KiB"),
    (1536000, "1.5 MiB"),
    (1572864000, "1.5 GiB"),
    (500, "500.0 Bytes"),
    (500000, "488.3 KiB"),
    (500000000, "476.8 MiB"),
    (500000000000, "465.7 GiB"),
    (500000000000000, "454.7 TiB"),
    (500000000000000000, "444.1 PiB"),
])
def test_human_readable_size_binary(file_size, expected_output):
    output = rule_fs.human_readable_size(file_size, binary=True)
    assert output == expected_output
