"""
Attributes can be added to any Ten8t function using the @attributes decorator.

Attributes allow metadata to be added to rule functions to control how they are
run, filtered, and scored. In order to meet our minimalist sensibilities, we have
kept the number of attributes to a minimum and NONE are required in order to
minimize, nearly to zero the overhead of writing a rule.

This design philosophy matches a bit of the zen of python: "Simple is better than
complex." In order to write a simple test you are never required to add each and
every attribute to a rule. Defaults are provided for all attributes. You can go
along way never using an attribute...and once you learn them you will use them all
the time.
"""
import re
from typing import Callable

from .ten8t_exception import Ten8tException

DEFAULT_TAG = ""  # A string indicating the type of rule, used for grouping/filtering results
DEFAULT_LEVEL = 1  #
DEFAULT_PHASE = ""  # String indicating what phase of the dev process a rule is best suited for
DEFAULT_WEIGHT = 100  # The nominal weight for a rule should be a positive number
DEFAULT_SKIP = False  # Set to true to skip a rule
DEFAULT_TTL_MIN = 0  # Time to live for check functions.
DEFAULT_RUID = ""
DEFAULT_FINISH_ON_FAIL = False  # If a ten8t function yields fail result stop processing
DEFAULT_SKIP_ON_NONE = False
DEFAULT_FAIL_ON_NONE = False
DEFAULT_INDEX = 1  # All ten8t functions are given an index of 1 when created.
DEFAULT_THREAD_ID = "main_thread__"

# Define at module level.  This *could* be changed...
DEFAULT_DISALLOWED_CHARS = ' ,!@#$%^&:?*<>\\/(){}[]<>~`-+=\t\n\'"'

def _parse_ttl_string(input_string: str) -> float:
    """
    Parses a time-to-live (TTL) string and converts it into a numeric value in minutes.

    The function takes an input string representing a time duration (e.g., "5 seconds",
    "2 hours") and converts it into a floating-point number representing the value
    in minutes. The time duration can be specified with various units such as seconds,
    minutes, or hours. If the string does not contain a valid unit, "minutes" is used
    as the default unit. For input values less than zero, an exception is raised. If the
    input string does not match the expected pattern, a default value of 0.0 minutes is returned.

    Args:
        input_string (str): A string representing the time-to-live (TTL) value. It can
            contain a number followed by an optional unit such as 's', 'sec', 'seconds',
            'm', 'min', 'minutes', 'h', 'hr', 'hrs', or 'hour'. If no unit is provided,
            minutes is used by default.

    Returns:
        float: A floating-point value representing the TTL in minutes.

    Raises:
        Ten8tException: If the TTL value is less than 0.0.
    """
    scale = {"seconds": 60,
             "second": 60,
             "sec": 60,
             "s": 60,
             "m": 1,
             "min": 1,
             "minute": 1,
             "minutes": 1,
             "h": 1 / 60.,
             "hr": 1 / 60.,
             "hrs": 1 / 60.,
             "hour": 1 / 60.}
    pattern = re.compile(
        r"([+-]?\d+\.\d*|\d*\.\d+|[-+]?\d+)\s*"
        r"(hour|hrs|hr|h|minutes|minute|min|m|seconds|second|sec|s)?"
    )
    matches = re.findall(pattern, input_string)
    if len(matches) == 1 and len(matches[0]) == 2:
        if matches[0][1] == '':
            unit = "m"
        else:
            unit = matches[0][1]
        number = float(matches[0][0]) / scale[unit]
        if number < 0.0:
            raise Ten8tException("TTL must be greater than or equal to 0.0")
        return number

    return 0.0


def _ensure_defaults(func):
    """Initialize all Ten8t attributes with default values if they're not already set."""
    # Category attributes
    func.tag = getattr(func, 'tag', DEFAULT_TAG)
    func.phase = getattr(func, 'phase', DEFAULT_PHASE)
    func.level = getattr(func, 'level', DEFAULT_LEVEL)
    func.ruid = getattr(func, 'ruid', DEFAULT_RUID)

    # Control attributes
    func.skip_on_none = getattr(func, 'skip_on_none', DEFAULT_SKIP_ON_NONE)
    func.fail_on_none = getattr(func, 'fail_on_none', DEFAULT_FAIL_ON_NONE)
    func.finish_on_fail = getattr(func, 'finish_on_fail', DEFAULT_FINISH_ON_FAIL)
    func.skip = getattr(func, 'skip', DEFAULT_SKIP)

    # Threading attributes
    func.thread_id = getattr(func, 'thread_id', DEFAULT_THREAD_ID)

    # Caching attributes
    func.ttl_minutes = getattr(func, 'ttl_minutes', DEFAULT_TTL_MIN)

    # Score attributes
    func.weight = getattr(func, 'weight', DEFAULT_WEIGHT)

    # Other attributes
    func.index = getattr(func, 'index', DEFAULT_INDEX)

    return func


def _validate_category_names(tag, phase, ruid, disallowed_chars=DEFAULT_DISALLOWED_CHARS):
    for attr_name, attr in (('tag', tag), ('phase', phase), ('ruid', ruid)):
        attr = str(attr)
        bad_chars = [c for c in disallowed_chars if c in attr]
        if bad_chars:
            raise Ten8tException(f"Invalid characters {bad_chars} found in {attr_name}")


def categories(*, tag: str = DEFAULT_TAG,
               phase: str = DEFAULT_PHASE,
               level: int = DEFAULT_LEVEL,
               ruid: str = DEFAULT_RUID,
               disallowed_chars=DEFAULT_DISALLOWED_CHARS) -> Callable:
    """Decorator for categorizing functions."""
    # Validation for disallowed characters

    # This does a little bit of clean up on phase/tag/ruid
    phase, tag, ruid = [str(t) for t in [phase, tag, ruid, ]]

    _validate_category_names(phase, tag, ruid, disallowed_chars)

    if not isinstance(ruid, str):
        raise Ten8tException("ruid must be a string.")

    def decorator(func):
        # Ensure all defaults are set first
        _ensure_defaults(func)

        # Now override the specific attributes this decorator manages
        func.tag = tag
        func.phase = phase
        func.level = level
        func.ruid = ruid
        return func

    return decorator


def control(*, skip_on_none: bool = DEFAULT_SKIP_ON_NONE,
            fail_on_none: bool = DEFAULT_FAIL_ON_NONE,
            finish_on_fail: bool = DEFAULT_FINISH_ON_FAIL,
            skip: bool = DEFAULT_SKIP) -> Callable:
    """Decorator for controlling function execution behavior."""

    def decorator(func):
        # Ensure all defaults are set first
        _ensure_defaults(func)

        # Now override the specific attributes this decorator manages
        func.skip_on_none = skip_on_none
        func.fail_on_none = fail_on_none
        func.finish_on_fail = finish_on_fail
        func.skip = skip
        return func

    return decorator


def threading(*, thread_id: str = DEFAULT_THREAD_ID) -> Callable:
    """Decorator for thread-related attributes."""
    if not isinstance(thread_id, str):
        raise Ten8tException("thread_id must be a string.")

    def decorator(func):
        # Ensure all defaults are set first
        _ensure_defaults(func)

        # Now override the specific attributes this decorator manages
        func.thread_id = thread_id
        return func

    return decorator


def caching(*, ttl_minutes: str | int | float = DEFAULT_TTL_MIN) -> Callable:
    """Decorator for caching-related attributes."""
    # Process ttl_minutes
    parsed_ttl = _parse_ttl_string(str(ttl_minutes))

    def decorator(func):
        # Ensure all defaults are set first
        _ensure_defaults(func)

        # Now override the specific attributes this decorator manages
        func.ttl_minutes = parsed_ttl
        return func

    return decorator


def score(*, weight: float = DEFAULT_WEIGHT) -> Callable:
    """Decorator for scoring-related attributes."""
    if weight in [None, True, False] or weight <= 0:
        raise Ten8tException("Weight must be numeric and > than 0.0. Nominal value is 100.0.")

    def decorator(func):
        # Ensure all defaults are set first
        _ensure_defaults(func)

        # Now override the specific attributes this decorator manages
        func.weight = weight
        return func

    return decorator



# Define defaults at module level since they're constant
ATTRIBUTE_DEFAULTS = {
    "tag": DEFAULT_TAG,
    "phase": DEFAULT_PHASE,
    "level": DEFAULT_LEVEL,
    "weight": DEFAULT_WEIGHT,
    "skip": DEFAULT_SKIP,
    "ruid": DEFAULT_RUID,
    "ttl_minutes": DEFAULT_TTL_MIN,
    "finish_on_fail": DEFAULT_FINISH_ON_FAIL,
    "skip_on_none": DEFAULT_SKIP_ON_NONE,
    "fail_on_none": DEFAULT_FAIL_ON_NONE,
    "index": DEFAULT_INDEX,
    "thread_id": DEFAULT_THREAD_ID,
}


def get_attribute(func, attr: str, default_value=None):
    """
    Retrieves a function's metadata attribute with fallback to default values.

    Args:
        func: Function to inspect for the attribute
        attr (str): Attribute name to retrieve (tag, phase, level, weight, etc.)
        default_value: Optional override for built-in defaults

    Returns:
        Value of the requested attribute or its default
    """
    if default_value is not None:
        return getattr(func, attr, default_value)

    return getattr(func, attr, ATTRIBUTE_DEFAULTS[attr])


def attributes(*,
               tag: str = DEFAULT_TAG,
               phase: str = DEFAULT_PHASE,
               level: int = DEFAULT_LEVEL,
               weight: float = DEFAULT_WEIGHT,
               skip: bool = DEFAULT_SKIP,
               ruid: str = DEFAULT_RUID,
               ttl_minutes: str | int | float = DEFAULT_TTL_MIN,
               finish_on_fail: bool = DEFAULT_FINISH_ON_FAIL,
               skip_on_none: bool = DEFAULT_SKIP_ON_NONE,
               fail_on_none: bool = DEFAULT_FAIL_ON_NONE,
               thread_id: str = DEFAULT_THREAD_ID,
               disallowed_chars=DEFAULT_DISALLOWED_CHARS) -> Callable:
    """
    A decorator to assign metadata and control attributes to functions for processing logic.
    This is a comprehensive decorator that combines all functionality of the more specific
    decorators (categories, control, threading, caching, score).

    This decorator is for LEGACY purposes.  Original ten8t code was written with a single
    decorator.  Over time the list of decorators grew to become unwieldy.  The attributes
    decorator is here mostly to keep the tests working.  Please used the more specific
    decorators instead.
    """
    _validate_category_names(phase, tag, ruid, disallowed_chars)

    def decorator(func):
        # Apply each specialized decorator in sequence
        # Each will ensure all defaults are set and apply its specific validations
        func = categories(tag=tag, phase=phase, level=level, ruid=ruid)(func)
        func = control(skip_on_none=skip_on_none, fail_on_none=fail_on_none,
                       finish_on_fail=finish_on_fail, skip=skip)(func)
        func = threading(thread_id=thread_id)(func)
        func = caching(ttl_minutes=ttl_minutes)(func)
        func = score(weight=weight)(func)
        return func

    return decorator
