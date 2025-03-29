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
    """Initialize Ten8t attributes with default values if not already set.

    Sets all Ten8t attributes on the function with their default values if they
    haven't been set yet. This ensures all functions have a complete set of attributes.

    Args:
        func (Callable): Function to initialize with default attributes.

    Returns:
        Callable: The function with all default attributes set.
    """
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


def validate_string(attr_name: str, attr_value, disallowed_chars=DEFAULT_DISALLOWED_CHARS):
    """Validates a string attribute doesn't contain disallowed characters.

    Args:
        attr_name (str): Name of the attribute being validated (for error message)
        attr_value: Value to validate
        disallowed_chars (str, optional): Characters not allowed in the string.
            Defaults to DEFAULT_DISALLOWED_CHARS.

    Raises:
        Ten8tException: If the value is not a string or contains disallowed characters
    """
    if not isinstance(attr_value, str):
        raise Ten8tException(f"{attr_name} with value {attr_value} must be a string.")

    bad_chars = [c for c in disallowed_chars if c in attr_value]
    if bad_chars:
        raise Ten8tException(f"Invalid characters {bad_chars} found in {attr_name}")


def _validate_category_names(tag, phase, ruid, disallowed_chars=DEFAULT_DISALLOWED_CHARS):
    """Validates that category names don't contain disallowed characters.

    Args:
        tag (str): Tag value to validate.
        phase (str): Phase value to validate.
        ruid (str): RUID value to validate.
        disallowed_chars (str, optional): String containing characters that aren't allowed.
            Defaults to DEFAULT_DISALLOWED_CHARS.

    Raises:
        Ten8tException: If any attribute contains disallowed characters.
    """
    for attr_name, attr_value in (('tag', tag), ('phase', phase), ('ruid', ruid)):
        validate_string(attr_name, attr_value, disallowed_chars)



def categories(*, tag: str = DEFAULT_TAG,
               phase: str = DEFAULT_PHASE,
               level: int = DEFAULT_LEVEL,
               ruid: str = DEFAULT_RUID,
               disallowed_chars=DEFAULT_DISALLOWED_CHARS) -> Callable:
    """Decorator for applying categorization attributes to Ten8t functions.

    This decorator sets attributes that help categorize and organize Ten8t functions
    for filtering and reporting purposes.

    Args:
        tag (str, optional): Identifier indicating the function's type or group.
            Defaults to DEFAULT_TAG.
        phase (str, optional): Development phase the function is suited for.
            Defaults to DEFAULT_PHASE.
        level (int, optional): Numeric level value for the function.
            Defaults to DEFAULT_LEVEL.
        ruid (str, optional): Rule unique identifier.
            Defaults to DEFAULT_RUID.
        disallowed_chars (str, optional): Characters not allowed in category names.
            Defaults to DEFAULT_DISALLOWED_CHARS.

    Returns:
        Callable: Decorator function that applies the category attributes.

    Raises:
        Ten8tException: If any attribute contains disallowed characters or
            if ruid is not a string.
    """

    # Validation for disallowed characters
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
    """Decorator for controlling Ten8t function execution behavior.

    This decorator sets attributes that determine how a Ten8t function
    behaves in different scenarios.

    Args:
        skip_on_none (bool, optional): Whether to skip the function if a None result.
            Defaults to DEFAULT_SKIP_ON_NONE.
        fail_on_none (bool, optional): Whether to fail the function if a None result.
            Defaults to DEFAULT_FAIL_ON_NONE.
        finish_on_fail (bool, optional): Whether to stop processing if function fails.
            Defaults to DEFAULT_FINISH_ON_FAIL.
        skip (bool, optional): Whether to skip this function entirely.
            Defaults to DEFAULT_SKIP.

    Returns:
        Callable: Decorator function that applies the control attributes.
    """


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


def threading(*, thread_id: str = DEFAULT_THREAD_ID, disallowed_chars=DEFAULT_DISALLOWED_CHARS) -> Callable:
    """Decorator for specifying thread-related attributes for Ten8t functions.

    This decorator assigns threading attributes that determine how and where
    a Ten8t function should be executed.

    Args:
        thread_id (str, optional): Identifier for the thread to run the function in.
            Defaults to DEFAULT_THREAD_ID.

    Returns:
        Callable: Decorator function that applies the threading attributes.

    Raises:
        Ten8tException: If thread_id is not a string.
    """
    validate_string("thread_id", thread_id, disallowed_chars=disallowed_chars)

    def decorator(func):
        # Ensure all defaults are set first
        _ensure_defaults(func)

        # Now override the specific attributes this decorator manages
        func.thread_id = thread_id
        return func

    return decorator


def caching(*, ttl_minutes: str | int | float = DEFAULT_TTL_MIN) -> Callable:
    """Decorator for specifying caching behavior for Ten8t functions.

    This decorator sets attributes that control how results from the function
    are cached and for how long.

    Args:
        ttl_minutes (str | int | float, optional): Time-to-live for cached results.
            Can be a numeric value or a string with unit specifiers.
            Defaults to DEFAULT_TTL_MIN.

    Returns:
        Callable: Decorator function that applies the caching attributes.
    """

    parsed_ttl = _parse_ttl_string(str(ttl_minutes))

    def decorator(func):
        # Ensure all defaults are set first
        _ensure_defaults(func)

        # Now override the specific attributes this decorator manages
        func.ttl_minutes = parsed_ttl
        return func

    return decorator


def score(*, weight: float = DEFAULT_WEIGHT) -> Callable:
    """Decorator for specifying scoring attributes for Ten8t functions.

    This decorator sets attributes that determine how the function's results
    are weighted in scoring calculations.

    Args:
        weight (float, optional): Numeric weight to assign to the function.
            Defaults to DEFAULT_WEIGHT.

    Returns:
        Callable: Decorator function that applies the scoring attributes.

    Raises:
        Ten8tException: If weight is non-numeric, False, True, None, or not > 0.0.
    """

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
    """Retrieves a function's metadata attribute with fallback to default values.

    Looks up an attribute on the given function with fallback to module defaults
    or a specified default value.

    Args:
        func (Callable): Function to inspect for the attribute.
        attr (str): Attribute name to retrieve (tag, phase, level, weight, etc.).
        default_value (Any, optional): Override for built-in defaults.
            Defaults to None.

    Returns:
        Any: Value of the requested attribute or its default.
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
    """A comprehensive decorator that applies all Ten8t function attributes.

    Combines all functionality of the more specific decorators (categories, control,
    threading, caching, score) into a single decorator. This decorator exists
    primarily for legacy compatibility - using the more specific decorators is
    generally preferred.

    Args:
        tag (str, optional): Function type identifier. Defaults to DEFAULT_TAG.
        phase (str, optional): Development phase. Defaults to DEFAULT_PHASE.
        level (int, optional): Numeric level. Defaults to DEFAULT_LEVEL.
        weight (float, optional): Scoring weight. Defaults to DEFAULT_WEIGHT.
        skip (bool, optional): Whether to skip this function. Defaults to DEFAULT_SKIP.
        ruid (str, optional): Rule unique identifier. Defaults to DEFAULT_RUID.
        ttl_minutes (str | int | float, optional): Cache TTL. Defaults to DEFAULT_TTL_MIN.
        finish_on_fail (bool, optional): Whether to stop on failure. Defaults to DEFAULT_FINISH_ON_FAIL.
        skip_on_none (bool, optional): Skip if None result. Defaults to DEFAULT_SKIP_ON_NONE.
        fail_on_none (bool, optional): Fail if None result. Defaults to DEFAULT_FAIL_ON_NONE.
        thread_id (str, optional): Thread identifier. Defaults to DEFAULT_THREAD_ID.
        disallowed_chars (str, optional): Characters not allowed in attributes.
            Defaults to DEFAULT_DISALLOWED_CHARS.

    Returns:
        Callable: Decorator function that applies all Ten8t attributes.
    """

    _validate_category_names(phase, tag, ruid, disallowed_chars)

    def decorator(func):
        # Apply each specialized decorator in sequence
        # Each will ensure all defaults are set and apply its specific validations
        func = categories(tag=tag, phase=phase, level=level, ruid=ruid, disallowed_chars=disallowed_chars)(func)
        func = control(skip_on_none=skip_on_none, fail_on_none=fail_on_none,
                       finish_on_fail=finish_on_fail, skip=skip)(func)
        func = threading(thread_id=thread_id, disallowed_chars=disallowed_chars)(func)
        func = caching(ttl_minutes=ttl_minutes)(func)
        func = score(weight=weight)(func)
        return func

    return decorator
