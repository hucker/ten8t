""" This module contains the Ten8tResult class and some common result transformers. """

import copy
import itertools
import re
import traceback
from collections import Counter
from dataclasses import dataclass, field
from operator import attrgetter
from typing import Any, Sequence

from .render import Ten8tMarkup
from .ten8t_exception import Ten8tException
from .ten8t_util import StrListOrNone, any_to_str_list


@dataclass(slots=True)
class Ten8tResult:
    """
    Represents the outcome and metadata of a Ten8tFunction execution.

    This class is designed to encapsulate detailed information about the execution
    of a function or rule in the Ten8t framework, including its status, runtime
    details, messages, and various metadata. It provides a structured way to handle
    execution results while optimizing memory and performance through the use of
    `__slots__`.

    ### Key Features:
    - Captures detailed results, including status, messages (info, warnings, errors),
      runtime, and exceptions.
    - Supports efficient memory use and faster attribute access by enabling `__slots__`.
      This is especially useful when managing large numbers of result objects.
    - Prevents unintended dynamic attribute assignment, ensuring predictable behavior.
    - Provides utility methods like `as_dict()` for easy serialization and integration.

    ### Why Use `__slots__`?
    - **Memory Efficiency**:
      By defining a fixed set of attributes, memory overhead from per-instance dictionaries (`__dict__`) is avoided.
    - **Performance Improvements**:
      Attribute access and assignment are faster due to reduced indirection overhead.
    - **Error Prevention**:
      Ensures that only predefined attributes can be added, reducing potential runtime mistakes.

    While `__slots__` is beneficial here, it limits dynamic attribute addition. If the need arises for dynamic attributes in the future, `__slots__` can be disabled by removing `slots=True` from the `@dataclass`.

    ### Attributes:
        status (bool | None): Indicates the execution status (pass, fail, or None).
        func_name (str): The name of the executed function.
        pkg_name (str): Package where the function resides.
        module_name (str): Module name where the function resides.
        msg (str): User-facing message summarizing the result.
        info_msg (str): Informational message about the execution.
        warn_msg (str): Warning message, if applicable.
        doc (str): Docstring of the executed function or rule.
        runtime_sec (float): The runtime of the function in seconds.
        except_ (Exception | None): Exception raised during execution, if any.
        traceback (str): String representation of the exception traceback.
        skipped (bool): Indicates whether the execution was skipped.
        weight (float): Relative importance or weight assigned to the result.
        tag (str): Descriptive tag for grouping results (for example, HR, Ops, Engr, Production)
        level (int): Numerical category for ordering results.
        phase (str): "Phase" category, perhaps (r&d,proto,production).
        count (int): Number of return values or individual steps.
        ruid (str): Unique identifier for this result.
        ttl_minutes (float): Time-to-live duration for the result, in minutes.
        mit_msg (str): Mitigation suggestion or message, if applicable.
        owner_list (list[str]): A list of owners or responsible parties.
        skip_on_none (bool): Whether to skip function execution if encountering `None`.
        fail_on_none (bool): Whether to fail function execution if encountering `None`.
        summary_result (bool): Indicates this result is a summary of multiple outcomes.
        thread_id (str): The identifier of the thread where this function ran.

    ### Methods:
        as_dict() -> dict:
            Converts the `Ten8tResult` instance into a dictionary representation
            for serialization or hashing purposes.

    ### Usage Example:
        ```python
        # Example instantiation
        result = Ten8tResult(
            status=True,
            func_name="my_function",
            msg="Function executed successfully",
            runtime_sec=0.45,
        )

        # Accessing attributes
        print(result.status)  # True
        print(result.runtime_sec)  # 0.45

        # Converting to dictionary
        result_dict = result.as_dict()
        print(result_dict)
        ```
    """

    status: bool | None = False

    # Name hierarchy
    func_name: str = ""
    pkg_name: str = ""
    module_name: str = ""

    # Output Message
    msg: str = ""
    msg_rendered: str = ""
    msg_text: str = ""

    info_msg: str = ""
    info_msg_rendered: str = ""
    info_msg_text: str = ""

    warn_msg: str = ""
    warn_msg_rendered: str = ""
    warn_msg_text: str = ""

    # Function Info
    doc: str = ""

    # Timing Info
    runtime_sec: float = 0.0

    # Error Info
    except_: Exception | None = None
    traceback: str = ""
    skipped: bool = False

    weight: float = 100.0

    # Attribute Info
    tag: str = ""
    level: int = 1
    phase: str = ""
    count: int = 0
    ruid: str = ""
    ttl_minutes: float = 0.0

    # Mitigations
    mit_msg: str = ""
    owner_list: list[str] = field(default_factory=list)

    # Counts the number of times a check function was "attempted"
    attempts: int = 1

    # Bad parameters
    skip_on_none: bool = False
    fail_on_none: bool = False

    # Indicate summary results, so they can be filtered
    summary_result: bool = False

    # Thread id where function ran
    thread_id: str = ""

    # Was this result pulled from cache
    cached: bool = False

    mu = Ten8tMarkup()

    def __post_init__(self):
        # Automatically grab the traceback for better debugging.
        if self.except_ is not None and not self.traceback:
            self.traceback = traceback.format_exc()

    def as_dict(self) -> dict:
        """Convert the Ten8tResult instance to a dictionary."""
        d = {slot: getattr(self, slot) for slot in self.__slots__ if hasattr(self, slot)}

        # Make the except_ attribute a string for serialization/hashability
        d['except_'] = str(d['except_'])
        return d

    @classmethod
    def from_dict(cls, data: dict) -> 'Ten8tResult':
        """
        Create a Ten8tResult instance from a dictionary (that presumably was saved with as_dict())

        Args:
            data (dict): Dictionary representation of a Ten8tResult instance.

        Returns:
            Ten8tResult: A new Ten8tResult instance populated with values from the dictionary.
        """
        # Handle exception reconstruction if it was serialized as a string
        if 'except_' in data:
            # If the `except_` was serialized, convert it appropriately
            # Here we keep it as a string since full exception reconstruction requires additional handling
            data['except_'] = None if data['except_'] == 'None' else data['except_']

        # Handle attributes with default factories like `owner_list`
        if 'owner_list' not in data:
            data['owner_list'] = []

        # Create a new instance by unpacking the dictionary
        result = cls(**data)
        return result

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


class Ten8tResultDictFilter():
    """
    Advanced filter capable of filtering result dictionary on multiple fields (ruid, tag, and phase).
    """

    def __init__(
            self,
            ruid_patterns: StrListOrNone = None,
            tag_patterns: StrListOrNone = None,
            phase_patterns: StrListOrNone = None,
            func_name_patterns: StrListOrNone = None,
            summary_results: bool = None,
            status_results: bool = None,
    ):
        # Initialize patterns for each field
        self.ruid_patterns = any_to_str_list(ruid_patterns)
        self.tag_patterns = any_to_str_list(tag_patterns)
        self.phase_patterns = any_to_str_list(phase_patterns)
        self.func_name_patterns = any_to_str_list(func_name_patterns)
        self.summary_results = summary_results
        self.status_results = status_results

    def filter(self, results: dict,
               ruid_patterns: StrListOrNone = None,
               tag_patterns: StrListOrNone = None,
               phase_patterns: StrListOrNone = None,
               func_name_patterns: StrListOrNone = None,
               summary_results: bool = None,
               status_results: bool = None) -> dict:
        """
        Filters data on ruid, tag, and phase fields using the provided patterns.
        """

        # Make a deep copy to avoid mutating the original dictionary
        results = copy.deepcopy(results)

        # Prepare patterns by combining instance-level and method-level inputs
        ruid_patterns = self._prepare_patterns(ruid_patterns, self.ruid_patterns)
        tag_patterns = self._prepare_patterns(tag_patterns, self.tag_patterns)
        phase_patterns = self._prepare_patterns(phase_patterns, self.phase_patterns)
        func_name_patterns = self._prepare_patterns(func_name_patterns, self.func_name_patterns)
        summary_results = summary_results if summary_results is not None else self.summary_results
        status_results = status_results if status_results is not None else self.status_results

        # Filter results
        results["results"] = self._filter_results(
            results["results"],
            ruid_patterns,
            tag_patterns,
            phase_patterns,
            func_name_patterns,
            summary_results,
            status_results
        )

        return results

    def _prepare_patterns(self, input_patterns, default_patterns):
        """Prepare patterns by combining the input and default ones."""
        return any_to_str_list(input_patterns or default_patterns)

    def _pattern_matches(self, result, key, patterns):
        """
        Generic match logic for any key and pattern list.

        :param result: The current result dictionary being inspected.
        :param key: The dictionary key to match the value of.
        :param patterns: A list of regex patterns to match.
        :returns: True if the key value matches any of the patterns or if patterns is empty.
        """
        if not patterns:
            return True  # If no patterns provided, consider it a match
        value = result.get(key, "")  # Get the value for the key, defaulting to an empty string
        return any(re.search(pattern, value) for pattern in patterns)

    def _filter_results(self, results, ruid_patterns, tag_patterns, phase_patterns,
                        func_name_patterns, summary_results, status_results):
        """Filter the data based on the provided patterns and filters."""
        filtered_results = []

        for r in results:
            if self._pattern_matches(r, "ruid", ruid_patterns) \
                    and self._pattern_matches(r, "tag", tag_patterns) \
                    and self._pattern_matches(r, "phase", phase_patterns) \
                    and self._pattern_matches(r, "func_name", func_name_patterns) \
                    and self._match_summary_result(r, summary_results) \
                    and self._match_status(r, status_results):
                filtered_results.append(r)

        return filtered_results

    def _match_summary_result(self, result, summary_results):
        """Check if summary_result matches the expected value."""
        if summary_results is None:  # No filtering on this value
            return True
        return result.get("summary_result") == summary_results

    def _match_status(self, result, status_results):
        """Check if status matches the expected value."""
        if status_results is None:  # No filtering on this value
            return True
        return result.get("status") == status_results
