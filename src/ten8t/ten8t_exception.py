"""Basic exception classes for ten8t."""


class Ten8tTypeError(TypeError):
    """Type errors associated with setting up test8t

    When bad types are sent to ten8t, this exception will be raised and should
    not be confused the TypeError that (should) indicate an unexpected lower
    level error.

    """


class Ten8tValueError(ValueError):
    """ Value Error associated with setting up test8t

    These exceptions will occur when setting up parameters on ten8t attributes and
    basic setup.  For example a negative weight.

    """


class Ten8tException(Exception):
    """Specialized exception for ten8t."""
