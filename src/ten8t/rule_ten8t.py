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

from .render import Ten8tMarkup
from .ten8t_exception import Ten8tException
from .ten8t_result import TR, Ten8tResult, Ten8tResultDictFilter
from .ten8t_types import StrOrPath, StrOrPathList
from .ten8t_yield import Ten8tYield, Ten8tYieldSummaryOnly


def get_file_age_in_minutes(file_path: StrOrPath) -> float:
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


def rule_ten8t_json_file(file_name: StrOrPath,
                         max_age_minutes: float = 10e20,
                         encoding: str = 'utf-8',
                         ruid: str = '',
                         ruid_sep: str = '.',
                         pass_if_missing: bool = False,
                         dfilter: Ten8tResultDictFilter | None = None,
                         yielder: Ten8tYield | None = None):

    code = Ten8tMarkup().code
    try:
        if pathlib.Path(file_name).exists() is False:
            yield TR(status=pass_if_missing,
                     msg=f"The file {code(file_name)} does not exist default status = {pass_if_missing}")
            return

        with open(str(file_name), 'r', encoding=encoding) as f:
            results = json.load(f)

        age_in_minutes = get_file_age_in_minutes(file_name)

        if age_in_minutes > max_age_minutes:
            yield TR(status=False,
                     msg=f"The file {code(file_name)} is {code(age_in_minutes)} minutes older than the max allowable {max_age_minutes:0.1f} age."
                     )
            return


    except (IOError, json.JSONDecodeError, PermissionError) as e:
        yield TR(status=False,
                 msg=f"Exception {str(e)} loading file {code(msg=file_name)}",
                 except_=e)

        return

    # Let the user pass a yield object, this can make for cleaner code by reducing param counts
    if yielder:
        y = yielder
    else:
        y = Ten8tYield(emit_summary=False,
                       emit_pass=True,
                       emit_fail=True,
                       summary_name=f"Load results from {file_name}")

    dfilter = dfilter or Ten8tResultDictFilter()
    results = dfilter.filter(results)

    if 'results' not in results or not results['results']:
        raise Ten8tException(f"No results found for {file_name}")

    for result in results['results']:
        new_result = Ten8tResult.from_dict(result)

        # For cases where a result read from the file has a ruid AND the current function has
        # a ruid, they are merged.
        if ruid:
            new_result.ruid = f'{ruid}{ruid_sep}{new_result.ruid}'

        # This is a very important.  Marking the data as cached means that the low level code
        # managing results will leave the result data untouched rather than copying the metadata
        # from this function into the result.  Let that sink in.  We are currently loading a list
        # of possibly hundreds of results, each of which has important metadata about the function
        # called to create that result.  If we don't mark the result as coming from cache the metadata
        # from THIS function would overwrite into those results.  That is NOT what we want.
        # TODO: As is, this mechanism loses the information about where the result came from which is bad.
        #       ideally, there would be a name field that is part of each result that indicates where the
        #       data comes from and each time this mechanism is used a '.' or '-' notation is used similar
        #       to what we do with ruids.
        #       For example, say the json file came from Server1-diagnostic, ideally there would be a field in
        #       this result indicating that the parent of this result was Server1-diagnostic.  That way
        #       we could concatenate that with Facility1.Serever1-diagnostic to build up the history.
        new_result.cached = True

        yield from y(new_result)

    yield from y.yield_summary(msg=f"Result file {file_name} had {y.pass_count} pass and {y.fail_count} fail results.")


def rule_ten8t_json_files(file_names: StrOrPathList,
                          max_age_minutes: float = 10e20,
                          encoding: str = 'utf-8',
                          ruid: str = '',
                          ruid_sep: str = '.',
                          dfilter: Ten8tResultDictFilter | None = None,
                          pass_if_missing: bool = False,
                          yielder: Ten8tYield | None = None):
    """
    Processes a list of JSON files based on certain criteria, including file age,
    encoding, and an optional unique identifier prefix. Supports file globbing
    patterns for flexible input handling.

    Args:
        dfilter: a dfilter object that can be used to remove unwanted results.
        ruid: An additional ruid prefix to be added to each result.
        file_names: A string representing file paths separated by spaces or a list
            of file paths. Supports glob patterns if the input is a single string.
        max_age_minutes: A float representing the maximum allowed file age in minutes.
            Default is a very large number, effectively bypassing this check
            unless otherwise specified.
        encoding: A string specifying the encoding used to read the content of
            files. Default is 'utf-8'.
        ruid_sep: A string used to separate the ruid prefix from the result ruid.
        pass_if_missing: A boolean flag. If set to True, missing files will not
            raise exceptions and will be skipped. Default is False.
        yielder: Ten8tYielder object.  Defaults to SummaryOnly

    Yields:
        Iterable: Yields processed results from the `rule_ten8t_json_file` function
        for each file that meets the criteria.
    """
    if isinstance(file_names, str):
        file_names = file_names.split()

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

        if yielder:
            y = yielder
        else:
            y = Ten8tYieldSummaryOnly(summary_name=f"Load results from {result_file}")

        yield from rule_ten8t_json_file(result_file,
                                        max_age_minutes=max_age_minutes,
                                        encoding=encoding,
                                        ruid=ruid,
                                        ruid_sep=ruid_sep,
                                        dfilter=dfilter,
                                        pass_if_missing=pass_if_missing,
                                        yielder=y)
