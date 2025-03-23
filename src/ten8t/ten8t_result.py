""" This module contains the Ten8tResult class and some common result transformers. """

import itertools
import traceback
from collections import Counter
from dataclasses import asdict, dataclass, field
from operator import attrgetter
from typing import Any, Sequence

from .render import Ten8tMarkup
from .ten8t_exception import Ten8tException


@dataclass
class Ten8tResult:
    """
    Return value of a Ten8tFunction.

    This dataclass tracks the status of a Ten8tFunction. It includes data relating to the function
    call, such as the status, module name, function name, message, additional info, warning message,
    docstring, runtime, exceptions, traceback, skip flag, tag, level, and count.

    While normally I choose "reasonable" defaults, in this case there really are none that aren't
    "zero" values except for weight and level, which default to 100% and 1 respectively.

    This data can be used for reporting purposes.

    Attributes:
        status (bool): Check status. Default is False.
        module_name (str): Module name. Default is "".
        func_name (str): Function name. Default is "".
        msg (str): Message to the user. Default is "".
        info_msg (str): Additional function call info. Default is "".
        warn_msg (str): Warning message. Default is "".
        doc (str): Function docstring. Default is "".
        runtime_sec (float): Function runtime in seconds. Default is 0.0.
        except_ (Exception): Raised exception, if any. Default is None.
        traceback (str): Exception traceback, if any. Default is "".
        skipped (bool): Function skip flag. Default is False.
        tag (str): Function tag. Default is "".
        level (int): Function level. Default is 1.
        thread_id(str):Thread the function ran on. Default is "".
        count (int): Return value count from a Ten8tFunction.
        """

    status: bool | None = False

    # Name hierarchy
    func_name: str = ""
    pkg_name: str = ""
    module_name: str = ""

    # Msg Hierarchy
    msg: str = ""
    info_msg: str = ""
    warn_msg: str = ""

    msg_rendered: str = ""

    # Function Info
    doc: str = ""

    # Timing Info
    runtime_sec: float = 0.0

    # Error Info
    except_: Exception | None = None
    traceback: str = ""
    skipped: bool = False

    weight: float = 100.0

    # Attribute Info - This needs to be factored out?
    tag: str = ""
    level: int = 1
    phase: str = ""
    count: int = 0
    ruid: str = ""
    ttl_minutes: float = 0.0

    # Mitigations
    mit_msg: str = ""
    owner_list: list[str] = field(default_factory=list)

    # Bad parameters
    skip_on_none: bool = False
    fail_on_none: bool = False

    # Indicate summary results, so they can be filtered
    summary_result: bool = False

    # Thread id where function ran
    thread_id: str = ""

    mu = Ten8tMarkup()

    def __post_init__(self):
        # Automatically grab the traceback for better debugging.
        if self.except_ is not None and not self.traceback:
            self.traceback = traceback.format_exc()

    def as_dict(self) -> dict:
        """Convert the Ten8tResult instance to a dictionary."""
        d = asdict(self)

        # We want this dict to be hashable so we make this a string.
        # Place any other unhashable things here (including deleting them).
        d['except_'] = str(d['except_'])
        return d


# Shorthand
TR = Ten8tResult


# Result transformers do one of three things, nothing and pass the result on, modify the result
# or return None to indicate that the result should be dropped.  What follows are some
# common result transformers.

def passes_only(sr: Ten8tResult):
    """ Return only results that have pass status"""
    return sr if sr.status else None


def fails_only(sr: Ten8tResult):
    """Filters out successful results.

    Args:
        sr (Ten8tResult): The result to check.

    Returns:
        Ten8tResult: The result if it has failed, otherwise None.
    """
    return None if sr.status else sr


def remove_info(sr: Ten8tResult):
    """Filter out messages tagged as informational

    Args:
        sr (Ten8tResult): The result to check.

    Returns:
        Ten8tResult: The result if it has failed, otherwise None.
    """
    return None if sr.info_msg else sr


def warn_as_fail(sr: Ten8tResult):
    """Treats results with a warning message as failures.

    Args:
        sr (Ten8tResult): The result to check.

    Returns:
        Ten8tResult: The result with its status set to False if there's a warning message.
    """
    if sr.warn_msg:
        sr.status = False
    return sr


def results_as_dict(results: list[Ten8tResult]):
    """Converts a list of Ten8tResult to a list of dictionaries.

    Args:
        results (list[Ten8tResult]): The list of results to convert.

    Returns:
        list[Dict]: The list of dictionaries.
    """
    return [result.as_dict() for result in results]


def group_by(results: Sequence[Ten8tResult], keys: Sequence[str]) -> dict[str, Any]:
    """
    Groups a list of Ten8tResult by a list of keys.

    This function allows for arbitrary grouping of Ten8tResult using the keys of the
    Ten8tResult as the grouping criteria.  You can group in any order or depth with
    any number of keys.

    Args:
        results (Sequence[Ten8tResult]): The list of results to group.
        keys (Sequence[str]): The list of keys to group by.S

    """

    if not keys:
        raise Ten8tException("Empty key list for grouping results.")

    key = keys[0]
    key_func = attrgetter(key)

    # I do not believe this is an actual test case as it would require a bug in
    # the code.  I'm leaving it here for now.
    # if not all(hasattr(x, key) for x in results):
    #    raise ten8t.Ten8tValueError(f"All objects must have an attribute '{key}'")

    # Sort and group by the first key
    results = sorted(results, key=key_func)
    group_results: list[tuple[str, Any]] = [(k, list(g))
                                            for k, g in itertools.groupby(results, key=key_func)]

    # Recursively group by the remaining keys
    if len(keys) > 1:
        for i, (k, group) in enumerate(group_results):
            group_results[i] = (k, group_by(group, keys[1:]))

    return dict(group_results)


def overview(results: list[Ten8tResult]) -> str:
    """
    Returns an overview of the results.

    Args:
        results (list[Ten8tResult]): The list of results to summarize.

    Returns:
        str: A summary of the results.
    """

    result_counter = Counter(
        'skip' if result.skipped else
        'error' if result.except_ else
        'fail' if not result.status else
        'warn' if result.warn_msg else
        'pass'
        for result in results
    )

    total = len(results)
    passed = result_counter['pass']
    failed = result_counter['fail']
    errors = result_counter['error']
    skipped = result_counter['skip']
    warned = result_counter['warn']

    return f"Total: {total}, Passed: {passed}, Failed: {failed}, " \
           f"Errors: {errors}, Skipped: {skipped}, Warned: {warned}"
