"""
This is the sad place for lonely functions that don't have a place
"""


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


def any_to_str_list(param: str | list | None, sep=' ') -> list[str]:
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
    raise ValueError('Invalid parameter type, expected all strings.')


def any_to_int_list(param: str | list[int] | None, sep=' ') -> list[int]:
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
