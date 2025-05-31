"""
This is the sad place for lonely functions that don't have a place
"""
import os
import pathlib

from ten8t.ten8t_exception import Ten8tTypeError, Ten8tValueError
from ten8t.ten8t_types import IntList, IntListOrNone, PathList, StrList
from ten8t.ten8t_types import StrListOrNone, StrOrPathListOrNone, StrOrPathOrNone


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


def cwd_here(file_: StrOrPathOrNone = None) -> pathlib.Path:
    """
    Change current working directory to the provided folder or to the parent folder if a file is provided.

    If 'file_' is:
        - None: the current file (__file__) location is used to set cwd.
        - a directory: the provided directory itself becomes the current working directory.
        - a file: the parent directory containing that file becomes the current working directory.

    Why?  This is useful for running scripts in different locations without having to worry about setting
    the current working directy.  Simplifies setup of demos and examples and allows you to NOT
    set the CWD in a configuration launch files.

    python foo/fum/demo.py

    And have code call cwd_here() and know that relative paths for demo.py will be correct.

    Args:
        file_ (str | pathlib.Path | None): The path to a file or directory, or None. Default is None.

    Returns:
        pathlib.Path: Explicitly returns path of the new current working directory.

    Example usage:
    --------
    >>> cwd_here('/path/to/directory')
    # sets cwd to '/path/to/directory'

    >>> cwd_here('/path/to/file.txt')
    # sets cwd to '/path/to/'

    >>> cwd_here()
    # sets the cwd to currently running script (__FILE__)
    """

    if file_ is None:
        file_ = __file__

    path = pathlib.Path(file_).resolve()

    if path.is_file():
        new_dir = path.parent
    else:
        new_dir = path

    os.chdir(new_dir)

    return new_dir


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
        elif param == ' ':
            # Coalesce spaces
            return param.split()
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
    if isinstance(param, pathlib.Path):
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


def clean_dict(d: dict, remove_nulls=True, keep_keys=None, remove_keys=None, empty_values=None):
    """
    Recursively processes a dictionary to remove keys based on specified rules.

    Args:
        d (dict): The input dictionary to process.
        remove_nulls (bool, optional): If True, removes keys with "empty" values (as defined in `empty_values`),
                                       unless the keys are in `keep_keys`. Defaults to True.
        keep_keys (list[str], optional): A list of keys to preserve, ensuring they are not removed,
                                         even if their values are defined as empty. Defaults to None.
        remove_keys (list[str], optional): A list of keys to forcibly remove, regardless of their values.
                                           Defaults to None.
        empty_values (list, optional): A list of values that should be considered empty. By default,
                                       this is `['', [], {}]`.

    Returns:
        dict: A new dictionary where keys are removed based on `remove_nulls`, `keep_keys`,
              `remove_keys`, and `empty_values`.

    Raises:
        Ten8tTypeError: If the input is not a dictionary.
        Ten8tValueError: If there are conflicts between `keep_keys` and `remove_keys`.
    """
    # Default to empty lists if keep_keys, remove_keys, or empty_values are not provided
    keep_keys = keep_keys or []
    remove_keys = remove_keys or []
    empty_values = empty_values or ['', [], {}, set(), tuple()]

    # Ensure the input is a dictionary
    if not isinstance(d, dict):
        raise Ten8tTypeError("Input must be a dictionary.")

    # Check for conflicts between keep_keys and remove_keys
    conflicting_keys = set(keep_keys).intersection(remove_keys)
    if conflicting_keys:
        raise Ten8tValueError(f"Conflicting keys between keep_keys and remove_keys: {conflicting_keys}")

    def _clean(d):
        """
        This function does the work as a closure, allowing it to not need check and pass most parameters
        on each recursive call.
        """
        result = {}
        for key, value in d.items():
            # Skip keys in remove_keys (unless they're also in keep_keys)
            if key in remove_keys and key not in keep_keys:
                continue

            # Preserve keys in keep_keys, regardless of remove_nulls or empty_values
            if key in keep_keys:
                result[key] = value
                continue

            # Process nested dictionaries
            if isinstance(value, dict):
                cleaned_value = _clean(value)
                if cleaned_value or not remove_nulls:  # Include non-empty nested dicts or if remove_nulls is False
                    result[key] = cleaned_value

            elif remove_nulls and value in empty_values:
                # It is important for this case to go before the next two since this will
                # eliminate a case for being empty
                continue

            elif isinstance(value, list):
                # Process each element in the list, cleaning if it’s a dictionary; retain original value otherwise
                result[key] = [
                    _clean(item) if isinstance(item, dict) else item
                    for item in value
                ]
            elif isinstance(value, tuple):
                # Process each element in the list, cleaning if it’s a dictionary; retain original value otherwise
                result[key] = tuple(
                    _clean(item) if isinstance(item, dict) else item
                    for item in value
                )

            # Iterate over values to remove empty lists or custom empty values

            # Include all other valid values
            else:
                result[key] = value

        return result

    # Call the closure to clean the dict.
    return _clean(d)
