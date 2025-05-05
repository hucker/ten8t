"""
This module allows for distributed checking to work using JSON files.  This module
allows you to read JSON output files and import that data into larger systems.

The standard output from ten8t is a JSON file with a list of all the results.  THis
can load the file and import all the result records into the larger system.

The structure of the code is similar to other modules.  There is one function
that processes a single result JSON file and another function that is given a list
of paths to process that calls the lower level function with each of the result
files (possibly using glob patterns).

"""
import datetime as dt
import json
import pathlib

import ten8t as t8


def get_file_age_in_minutes(file_path: str | pathlib.Path) -> float:
    """
    Get the age of a file in minutes based on its last modification time.

    TODO: This function currently calculates the file age using the file's
          last modification timestamp. If the `start_time` is available in the
          result dictionary returned by the checker's test results, it might
          be more accurate to calculate the file age from there.

    Args:
        file_path (str | Path): Path to the file.

    Returns:
        float: The age of the file in minutes.
               Raises FileNotFoundError if the file does not exist.
    """
    # Convert file_path to a Path object if it's not already
    file_path = pathlib.Path(file_path)

    # Check if the file exists
    if not file_path.is_file():
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    # Get the current time
    current_time = dt.datetime.now()

    # Get the file's last modification time
    modification_time = dt.datetime.fromtimestamp(file_path.stat().st_mtime)

    # Calculate and return the file's age in minutes
    age_in_minutes = (current_time - modification_time).total_seconds() / 60
    return age_in_minutes


def rule_ten8t_json_file(file_name: t8.StrOrPath,
                         max_age_min: float = 10e20,
                         encoding: str = 'utf-8',
                         ruid_leader: str = '',
                         pass_if_missing: bool = False):
    code = t8.Ten8tMarkup().code
    try:
        with open(str(file_name), 'r', encoding=encoding) as f:
            data = json.load(f)

            age_in_min = get_file_age_in_minutes(file_name)

            if age_in_min > max_age_min:
                yield t8.TR(status=False,
                            msg=f"The file {code(file_name)} is {code(age_in_min)} minutes older than the max allowable {max_age_min:0.1f} age."
                            )
                return
    except (IOError, json.JSONDecodeError, PermissionError) as e:
        if pass_if_missing:
            yield t8.TR(status=pass_if_missing,
                        msg=f"Could not find {code(msg=file_name)}, pass_if_missing=True"
                        )
        else:
            yield t8.TR(status=pass_if_missing,
                        msg=f"Exception {str(e)} loading file {code(msg=file_name)}",
                        except_=e)

        return

    results = data.get('results', None)

    if not results:
        raise t8.Ten8tException(f"No results found for {file_name}")

    for result in results:
        new_result = t8.Ten8tResult.from_dict(result)

        # This mechanism allows you to modify incoming ruids by adding a leader for
        # every ruid.  This could be used to reduce chances of collisions.
        if ruid_leader:
            new_result.ruid = f"{ruid_leader}-{new_result.ruid}"

        yield new_result


def rule_ten8t_json_files(file_names: t8.StrOrPathList,
                          max_age_min: float = 10e20,
                          encoding='utf-8',
                          ruid_leader: str = '',
                          pass_if_missing: bool = False):
    """
    Processes a list of JSON files based on certain criteria, including file age,
    encoding, and an optional unique identifier prefix. Supports file globbing
    patterns for flexible input handling.

    Args:
        file_names: A string representing file paths separated by spaces or a list
            of file paths. Supports glob patterns if the input is a single string.
        max_age_min: A float representing the maximum allowed file age in minutes.
            Default is a very large number, effectively bypassing this check
            unless otherwise specified.
        encoding: A string specifying the encoding used to read the content of
            files. Default is 'utf-8'.
        ruid_leader: A string prefix for unique identifier generation. If not
            provided, it defaults to the stem of each file's name.
        pass_if_missing: A boolean flag. If set to True, missing files will not
            raise exceptions and will be skipped. Default is False.

    Yields:
        Iterable: Yields processed results from the `rule_ten8t_json_file` function
        for each file that meets the criteria.
    """
    if isinstance(file_names, str):
        file_names = file_names.split()

    result_files = []

    # Expand glob if the first element is a single pattern
    if len(file_names) == 1:  # Check if it's a single element
        # Convert the first element to Path and test if it's a glob
        glob_path = pathlib.Path(file_names[0])
        if '*' in glob_path.name:
            # Expand using the glob pattern and collect matching files
            result_files = list(glob_path.parent.glob(glob_path.name))
        else:
            result_files = [glob_path]
    else:
        # Assume each file in the list is an individual pathname
        result_files = [pathlib.Path(f) for f in file_names]

    for result_file in result_files:
        if not ruid_leader:
            ruid_leader = result_file.stem

        yield from rule_ten8t_json_file(result_file,
                                        max_age_min=max_age_min,
                                        encoding=encoding,
                                        ruid_leader=ruid_leader,
                                        pass_if_missing=pass_if_missing)
