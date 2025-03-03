"""
This module provides a collection of composable functions for filtering elements in lists of 
Ten8tFunction objects based on various criteria such as `ruids`, `tags`, `levels`, or `phases`.

The filtering functions are divided into two categories:
1. Exclusion filters: Functions that exclude list elements matching specified criteria.
2. Inclusion filters: Functions that include only list elements matching specified criteria.

These filters can be composed to create complex filtering logic tailored to specific use cases.
"""
from enum import Enum

from .ten8t_exception import Ten8tException
from .ten8t_function import Ten8tFunction


class Ten8tFilterAttr(Enum):
    """
    Enumeration of valid filterable attributes for Ten8tFunction objects.
    """
    TAG = "tag"
    LEVEL = "level"
    PHASE = "phase"
    RUID = "ruid"


def validate_attribute(attribute: Ten8tFilterAttr):
    """
    Validates that the passed attribute is part of the Ten8tFilterAttr enum.

    Args:
        attribute (Ten8tFilterAttr): The attribute to validate as part of the Ten8tFilterAttr enum.

    Raises:
        Ten8tException: If the attribute is not valid.
    """
    return isinstance(attribute, Ten8tFilterAttr)


def exclude_by(attribute: Ten8tFilterAttr, values: list[Ten8tFunction]):
    """
    Return a filter function that will exclude elements based on the given attribute.

    Args:
        attribute (str): The name of the attribute to filter by (e.g., 'ruid', 'tag').
        values (list): A list of values to exclude.

    Returns:
        Callable: A filter function.
    """
    # Validate the attribute name
    if not validate_attribute(attribute):
        raise Ten8tException(f"Invalid attribute '{attribute}' in ten8t_filter.exclude_by. ")

    def filter_func(s_func: Ten8tFunction):
        return getattr(s_func, attribute.value) not in values

    return filter_func


def keep_by(attribute: Ten8tFilterAttr, values: list[Ten8tFunction]):
    """
    Return a filter function that will include only elements based on the given attribute.

    Args:
        attribute (str): The name of the attribute to filter by (e.g., 'ruid', 'tag').
        values (list): A list of values to include.

    Returns:
        Callable: A filter function.
    """
    # Validate the attribute name
    if not validate_attribute(attribute):
        raise Ten8tException(f"Invalid attribute '{attribute}' in ten8t_filter.keep_by. ")

    def filter_func(s_func: Ten8tFunction):
        return getattr(s_func, attribute.value) in values

    return filter_func
