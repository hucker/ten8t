"""
This is the sad place for lonely functions that don't have a place
"""
import pathlib
from typing import Sequence, TypeAlias

# Type aliases.
# Note: the *OrNone are meant to be constructors that allow a None value to be passed
#       that code will take care to convert to a [] or a ''
StrOrNone: TypeAlias = str | None
"""Type alias for a string or None."""

StrList: TypeAlias = Sequence[str]
"""Type alias for a sequence of strings."""

StrListOrNone: TypeAlias = StrList | StrOrNone
"""Type alias for a sequence of strings or None."""

IntOrNone: TypeAlias = int | None
"""Type alias for an integer or None."""

IntList: TypeAlias = Sequence[int]
"""Type alias for a sequence of integers."""

IntListOrNone: TypeAlias = IntList | IntOrNone
"""Type alias for a sequence of integers or None."""

FloatOrNone: TypeAlias = float | None
"""Type alias for a float or None."""

FloatList: TypeAlias = Sequence[float]
"""Type alias for a sequence of floats."""

FloatListOrNone: TypeAlias = FloatList | FloatOrNone
"""Type alias for a sequence of floats or None."""

StrOrPath: TypeAlias = str | pathlib.Path
StrOrPathOrNone: TypeAlias = StrOrPath | None
StrOrPathList: TypeAlias = Sequence[StrOrPath]
StrOrPathListOrNone: TypeAlias = StrOrPathList | None

PathList: TypeAlias = Sequence[pathlib.Path]

class NextIntValue:
    """
    I had to create this class in order to make mypy happy.
    Mypy does not know how to handle dynamic functions and  playing
    games
    """

    def __init__(self):
        self.current_id: int = 1  # Initialize to 1

    def __call__(self) -> int:
        self.current_id += 1
        return self.current_id


# Create an instance of the callable class
next_int_value = NextIntValue()

# next_int_value can be called like a function and the class manages the count
next_int_value.current_id = 1


def str_to_bool(s: str, default=None) -> bool:
    """ Convert a string value to a boolean."""
    s = s.strip().lower()  # Remove spaces at the beginning/end and convert to lower case

    if s in ('pass', 'true', 'yes', '1', 't', 'y', 'on'):
        return True
    if s in ('fail', 'false', 'no', '0', 'f', 'n', 'off'):
        return False

    if default is not None:
        return default

    raise ValueError(f'Cannot convert {s} to a boolean.')


def any_to_str_list(param: StrListOrNone, sep=' ') -> StrList:
    """
    Convert a string to a list of strings or if a list is given make sure it is all strings.
    Args:
        param: list of strings or string to convert to list of strings
        sep: separator character.

    Returns:

    """
    if param is None:
        return []
    if isinstance(param, str):
        param = param.strip()
        if param == '':
            return []
        else:
            return param.split(sep)
    if isinstance(param, list):
        if all(isinstance(item, str) for item in param):
            return param
    raise ValueError(f'Invalid parameter type, expected all strings. {param}')


def any_to_path_list(param: StrOrPathListOrNone, sep=' ') -> PathList:
    """
    Flexibly take a list of strings are pathlib objects and make a uniform
    list of pathlib objects.  This is useful for normalizing data read from
    different sources without have a bunch of point of use parsing.

    The assumption is that this data could come from a config file, a command line parameter,
    a UI element that returns strings, or code.  This should make all code
    just "fix" the data with this call.


    Args:
        param: StrOrPathListOrNone  Data to normalize
        sep: Separator character.  Should almost always be  ' '

    Returns:

    """
    if param is None:
        return []

    # Listify single path
    if isinstance(param, (pathlib.Path)):
        param = [param]

    # Given a string make it a list of strings
    if isinstance(param, str):
        param = param.strip()
        if param == '':
            param = []
        else:
            # Space split is slightly different and preferable
            if sep == ' ':
                param = param.split()
            else:
                param = param.split(sep)

    # Now we have a list of paths and strings, covert them all th paths
    return [pathlib.Path(p) for p in param]


def any_to_int_list(param: IntListOrNone, sep=' ') -> IntList:
    """
    Convert a string to a list of integers or if a list is given make sure it is all integers.
    Args:
        param: list of integers or string to convert to list of integers
        sep: separator character.

    Returns:
        list of integers
    """
    if param is None:
        return []
    if isinstance(param, str):
        param = param.strip()
        cleaned_param = param.split(sep)
        try:
            return [int(x) for x in cleaned_param]
        except ValueError as exc:
            raise ValueError(
                'Invalid parameter value, expected numeric string values that can be converted to integers.') from exc
    if isinstance(param, list):
        return [int(x) for x in param]

    raise ValueError(f'Invalid parameter type in {param}, expected all integers.')
