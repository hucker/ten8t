"""
This module contains ten8t rules that are useful for checking the status of
files on the native file system.

Note:
    These functions may be removed in a future release and replaced by alternatives
    that utilize the pyfilesystem package.
"""

import pathlib
import time
from typing import Generator

from .ten8t_exception import Ten8tException
from .ten8t_format import BM
from .ten8t_result import TR
from .ten8t_yield import Ten8tYield


def rule_path_exists(path_: str) -> Generator[TR, None, None]:
    """
    Checks whether a given file path exists on the filesystem and yields the result.

    This function determines the existence of a specified file path. It yields a
    generator object containing the status of the check along with an appropriate
    message. The status indicates whether the path exists or not, while the message
    provides a formatted string for additional details regarding the existence
    status of the path.

    Args:
        path_ (str): The file system path to check for existence.

    Yields:
        TR: A generator object containing the status of the check and a message
        detailing whether the path exists or not. The `status` attribute is a
        boolean indicating the result of the existence check, and the `msg`
        attribute provides a formatted string message describing the result.
    """
    path_str = BM.code(path_)
    if pathlib.Path(path_).exists():
        yield TR(status=True, msg=f"The path {BM.code(path_str)} does exist.")
    else:
        yield TR(status=False, msg=f"The path  {BM.code(path_str)} does {BM.bold('NOT')} exist.")


def rule_paths_exist(paths: list[str] | str,
                     summary_only=False,
                     summary_name=None,
                     name="Path Check",
                     no_paths_pass_status=False) -> Generator[TR, None, None]:
    """
    Generator function to verify the existence of provided file paths. The function
    iterates over the given paths, checks their presence, and yields results for each
    path. Optionally, it can also yield a summary of all checks. If no paths are provided
    for validation, it yields a specific status message.

    Args:
        paths (list[str] | str): A list of file paths or a string containing space-separated
            file paths to verify for existence.
        summary_only (bool): A flag indicating whether to only return a summary of the
            checks instead of individual results. Defaults to False.
        summary_name (typing.Optional[str]): A summary label or name to be included in the
            summarized output. Defaults to None.
        name (str): A descriptive name or identifier for the verification process.
            Defaults to "Path Check".
        no_paths_pass_status (bool): A status to determine the result to be yielded in
            case no paths are provided for validation. Defaults to False.

    Yields:
        Generator[TR, None, None]: Generator yielding verification results for each path,
        status for missing paths, or a summary of checks depending on the configuration.

    """
    y = Ten8tYield(show_summary=summary_only, summary_name=summary_name)

    if isinstance(paths, str):
        paths = paths.split(" ")

    for path in paths:
        yield from y(rule_path_exists(path))

    if y.count == 0:
        yield from y(status=no_paths_pass_status,
                     msg=f"There were no paths to check in {BM.code(name)}.")

    yield from y.yield_summary()


def rule_stale_file(
        filepath: pathlib.Path,
        days: float = 0,
        hours: float = 0,
        minutes: float = 0,
        seconds: float = 0,
        current_time=None
) -> Generator[TR, None, None]:
    """
    Checks whether a given file is stale based on its modification time and the
    specified age thresholds. Files older than the provided duration in days,
    hours, minutes, or seconds are considered stale.

    Args:
        filepath (pathlib.Path): The path to the file being checked.
        days (float): The threshold number of days for the file to be considered stale.
        hours (float): The threshold number of hours for the file to be considered stale.
        minutes (float): The threshold number of minutes for the file to be considered stale.
        seconds (float): The threshold number of seconds for the file to be considered stale.
        current_time (float): Current time in seconds since the epoch. If not
            provided, `time.time()` is used by default.

    Yields:
        Generator[TR, None, None]: A generator yielding TR objects indicating
            the status of the file (stale or not) and an accompanying message.

    Raises:
        Ten8tException: If the combined age threshold (days, hours, minutes,
            seconds) is less than or equal to 0.
    """
    current_time = current_time or time.time()

    age_in_seconds = days * 86400.0 + hours * 3600.0 + minutes * 60.0 + seconds
    if age_in_seconds <= 0:
        raise Ten8tException(f"Age for stale file check {BM.code(age_in_seconds)} should be > 0")

    try:
        file_mod_time = filepath.stat().st_mtime
        file_age_in_seconds = current_time - file_mod_time

        if file_age_in_seconds > age_in_seconds:
            unit = "seconds"
            if days > 0:
                file_age = file_age_in_seconds / 86400.0
                unit = "days"
            elif hours > 0:
                file_age = file_age_in_seconds / 3600.0
                unit = "hours"
            elif minutes > 0:
                file_age = file_age_in_seconds / 60.0
                unit = "minutes"
            elif seconds > 0:
                file_age = file_age_in_seconds

            age_msg = f"age = {file_age:.2f} {unit} {age_in_seconds=}"
            yield TR(status=False, msg=f"Stale file {BM.code(filepath)} {BM.code(age_msg)}")
        else:
            yield TR(status=True, msg=f"Not stale file {BM.code(filepath)}")
    except (FileNotFoundError, PermissionError, IOError) as exc:
        yield TR(status=False,
                 msg="Exception occurred while checking for the path {SM.code(path_str)}",
                 except_=exc)


def rule_stale_files(
        folder: str | pathlib.Path,
        pattern: str | pathlib.Path,
        days: float = 0,
        hours: float = 0,
        minutes: float = 0,
        seconds: float = 0,
        no_files_pass_status: bool = True,
        summary_only=False,
        summary_name=None
) -> Generator[TR, None, None]:
    """
    Identify and evaluate files within a specified folder and pattern against a defined age criteria
    in terms of days, hours, minutes, and seconds. The rule checks the files recursively based
    on the provided pattern and compares their last modified time against the stipulated duration.

    Args:
        folder: The folder path where the files should be searched. This can be either
            a string or a pathlib.Path object.
        pattern: The file name pattern to search for within the folder. It supports
            wildcard patterns and can also be a pathlib.Path.
        days: The number of full days to be used for calculating the age limit, defaulting to 0.
        hours: The number of hours to include in the age threshold, defaulting to 0.
        minutes: The number of minutes to include in the age threshold, defaulting to 0.
        seconds: The number of seconds to add to the age limit, defaulting to 0.
        no_files_pass_status: A flag indicating whether the rule should pass (`True`)
            or fail (`False`) when no files matching the pattern are found. Defaults to True.
        summary_only: A Boolean that, when set to True, instructs the rule to yield only a
            summary of the evaluation results instead of individual file details. Defaults to False.
        summary_name: An optional custom name for the summary to replace the default
             "Rule_stale_files".

    Yields:
        Generator[TR, None, None]: Provides results or a summary of the stale file evaluations,
            indicating whether files matched the criteria and detailing their respective status.
    """
    y = Ten8tYield(show_summary=summary_only, summary_name=summary_name or "Rule_stale_files")

    current_time = time.time()
    for filepath in pathlib.Path(folder).rglob(str(pattern)):
        yield from y.results(rule_stale_file(filepath=filepath,
                                             days=days,
                                             hours=hours,
                                             minutes=minutes,
                                             seconds=seconds,
                                             current_time=current_time))

    if y.count == 0:
        yield from y(status=no_files_pass_status,
                     msg=f"No files were found in {BM.code(folder)} matching pattern " \
                         f"{BM.code(folder)}")

    yield from y.yield_summary()


def rule_large_files(folder: str,
                     pattern: str,
                     max_size: float,
                     no_files_pass_status: bool = True,
                     summary_only=False,
                     summary_name=None):
    """
    Checks for any large files exceeding the specified maximum size in a folder
    matching a given pattern and generates corresponding status messages.

    Args:
        folder (str): The directory to search for files.
        pattern (str): The file search pattern to apply (e.g., "\*.txt").
        max_size (float): The maximum allowed file size in bytes.
                          Files exceeding this size will be flagged.
        no_files_pass_status (bool): The status to use if no files matching
                                     the pattern are found. Default is True.
        summary_only (bool, optional): If set to True, only the summary is yielded.
                                        Default is False.
        summary_name (str or None, optional): The name to assign to the summary.
                                              Default is None.
    """

    y = Ten8tYield(show_summary=summary_only, summary_name=summary_name or "Rule_large_files")

    if max_size <= 0:
        raise Ten8tException(f"Size for large file check should be > 0 not {max_size=}")

    code = BM.code
    for filepath in pathlib.Path(folder).rglob(pattern):
        size_bytes = filepath.stat().st_size
        if size_bytes > max_size:
            yield from y(
                status=False,
                msg=f"Large file {code(filepath)}, {code(size_bytes)} bytes, " \
                    f"exceeds limit of {code(max_size)} bytes",
            )
    if y.count == 0:
        yield from y(status=no_files_pass_status,
                     msg=f"No files found matching {code(pattern)} in {code(folder)}.")

    yield from y.yield_summary()


def rule_max_files(folders: list,
                   max_files: list | int,
                   pattern: str = '*',
                   summary_only=False,
                   summary_name=None):
    """
    Checks if the number of files in specified folders is within the provided maximum limit,
    based on a pattern.

    This function validates the count of files in each folder provided against the maximum file
    limits. If the file count exceeds the defined maximum, it yields a failure message. It also
    supports providing summary results only via the `summary_only` parameter.

    Args:
        folders (list or str):
            The directories to check for files. Can be a single folder or a list of folders.
        max_files (list or int):
            The maximum number of files allowed in the corresponding folder(s). Can be a single
            integer to apply the same limit to all folders or a list of limits corresponding to the
            folders.
        pattern (str):
            The file-matching pattern to count files in the folder(s). Default is '*' for all files.
        summary_only (bool):
            Whether to yield only a summary result instead of individual checks. Default is False.
        summary_name (str or None):
            An optional name for the summary. Default is None.

    Raises:
        Ten8tException:
            If the lengths of `folders` and `max_files` are not the same when `max_files` is
            provided as a list.

    Yields:
        Ten8tYield:
            The result of each folder's file count check or a summary if `summary_only` is True.
    """

    y = Ten8tYield(show_summary=summary_only, summary_name=summary_name or "Rule_max_files")

    if isinstance(folders, (str, pathlib.Path)):
        folders = [folders]
    if isinstance(max_files, int):
        max_files = [max_files] * len(folders)

    if len(folders) != len(max_files):
        raise Ten8tException(f"Number of folders and max_files {max_files} must be the same.")

    for folder, max_file in zip(folders, max_files):
        count = 0
        # don't materialize the list, just count
        for count, _ in enumerate(pathlib.Path(folder).rglob(pattern), start=1):
            pass

        if count <= max_file:
            yield from y(status=True,
                         msg=f"Folder {BM.code(folder)} contains less than or equal to " \
                             f"{BM.code(max_file)} files.")
        else:
            yield from y(status=False,
                         msg=f"Folder {BM.code(folder)} contains greater than " \
                             f"{BM.code(max_file)} files.")

    yield from y.yield_summary()
