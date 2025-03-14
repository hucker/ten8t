"""
Classes to support progress tracking.
"""

from abc import ABC, abstractmethod


# pylint: disable=R0903
class Ten8tProgress(ABC):
    """
    Abstract base class for tracking and managing progress.

    This class serves as a base for defining progress tracking mechanisms in
    iterative processes. It is designed to be subclassed, with custom behavior
    to be implemented in the '__call__' method. Users can leverage this class
    to provide updates for operations with finite or infinite iterations, display
    status messages, and optionally handle results.

    """

    def __init__(self):
        pass

    @abstractmethod
    def __call__(self,
                 current_iteration: int,
                 max_iterations,
                 text: str,
                 result=None):  # pragma: no cover
        pass


# pylint: disable=R0903
class Ten8tNoProgress(Ten8tProgress):
    """
    Brief summary of what the class does.

    A subclass of Ten8tProgress that overrides progress functionality by
    performing no operation. This class is particularly useful for testing
    purposes when progress tracking is not required.

    """

    def __call__(self, current_iteration: int,
                 max_iterations,
                 text: str, result=None):
        """Don't do anything for progress.  This is useful for testing."""


# pylint: disable=R0903
class Ten8tDebugProgress(Ten8tProgress):
    """
    Manages and displays debug progress messages for a process.

    This class is a subclass of `Ten8tProgress` and is specifically
    designed for debugging purposes. It provides functionality to
    print debug messages alongside an optional status indicator based
    on the provided result. Typically used during iterative processes
    to notify about current progress and outcomes.

    Attributes:
        No specific attributes are defined for this subclass.
    """

    def __call__(self, current_iteration: int, max_iteration: int, msg: str,
                 result=None):  # pylint: disable=unused-argument
        """Print a debug message."""
        if msg:
            print(msg)
        if result:
            print("+" if result.status else "-", end="")
