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


def _parse_ttl_string(input_string: str) -> float:
    """
    Use regular expression to match a TTL string.  This pattern was a pain to figure out.  There
    are so many permutations that need to be handled that are subtle (like the order matters in the
    list).

    Args:
        input_string (str): The input string to parse.

    Returns:
        Tuple[Optional[float], Optional[str]]: A tuple containing the parsed floating-point number
        and optional units. Returns (None, None) if no match is found.
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


def attributes(
        *,
        tag=DEFAULT_TAG,
        phase=DEFAULT_PHASE,
        level=DEFAULT_LEVEL,
        weight=DEFAULT_WEIGHT,
        skip=DEFAULT_SKIP,
        ruid=DEFAULT_RUID,
        ttl_minutes=DEFAULT_TTL_MIN,
        finish_on_fail=DEFAULT_FINISH_ON_FAIL,  # Abort the whole run
        skip_on_none=DEFAULT_SKIP_ON_NONE,
        fail_on_none=DEFAULT_FAIL_ON_NONE,
        thread_id=DEFAULT_THREAD_ID,

):
    """
    Decorator to add attributes to a Ten8t function.

    Note the *, I always forget that this means that the function is kwarg only.
    """

    # throws exception on bad input
    ttl_minutes = _parse_ttl_string(str(ttl_minutes))

    if weight in [None, True, False] or weight <= 0:
        raise Ten8tException("Weight must be numeric and > than 0.0.  Nominal value is 100.0.")

    # Make sure these names don't have bad characters.  Very important for regular expressions
    disallowed = ' ,!@#$%^&:?*<>\\/(){}[]<>~`-+=\t\n\'"'
    for attr_name, attr in (('tag', tag), ('phase', phase), ('ruid', ruid)):
        bad_chars = [c for c in disallowed if c in attr]
        if bad_chars:
            raise Ten8tException(f"Invalid characters {bad_chars} found in {attr_name} ")

    def decorator(func):
        """Jam in all the attributes"""
        func.phase = phase
        func.tag = tag
        func.level = level
        func.weight = weight
        func.skip = skip
        func.ruid = ruid
        func.ttl_minutes = ttl_minutes
        func.finish_on_fail = finish_on_fail
        func.skip_on_none = skip_on_none
        func.fail_on_none = fail_on_none
        func.thread_id = thread_id
        return func

    return decorator


def get_attribute(func, attr, default_value=None):
    """
    Returns an attribute from a function.
    """
    defs = {
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

    default = default_value or defs[attr]

    return getattr(func, attr, default)

