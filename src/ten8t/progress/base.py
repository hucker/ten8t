from abc import ABC

from ..ten8t_result import Ten8tResult
from ..ten8t_util import StrOrNone


# pylint: disable=R0903
class Ten8tProgress(ABC):
    """
    Abstract base class for tracking and managing progress.

    This class serves as a base for defining progress tracking mechanisms in
    iterative processes. It is designed to be subclassed, with custom behavior
    to be implemented in the '__call__' method. Users can leverage this class
    to provide updates for operations with finite or infinite iterations, display
    status messages, and optionally handle results.

    Important point:

    Current Iteration and MaxIteration reflect the number of check functions
    in the list of checks to run and the current value of the check being run.213


    """

    def __init__(self):
        pass

    def __str__(self):
        return "Ten8tProgress base class for tracking progress"

    def __repr__(self):
        return "<Ten8tProgress>"

    def message(self, msg: str):
        """
        Just report an arbitrary message.

        This can be things like starting, stopping, exceptions.  Anything not tied to a result.
        """

    def result_msg(self, current_iteration: int, max_iteration: int, msg: StrOrNone = '',
                   result: Ten8tResult | None = None):
        """
        Report a result.
        This should report progress with the results of a check function.  Note that
        check functions can return multiple results since they are generators.
        """
