"""Do nothing progress bar. """
from .._base import Ten8tProgress
from ...ten8t_util import StrOrNone, Ten8tResultOrNone


# TODO:  Rename this to Ten8tNullProgress

# pylint: disable=R0903
class Ten8tNoProgress(Ten8tProgress):
    """
     A subclass of Ten8tProgress that overrides progress functionality by
    performing no operation. This class is particularly useful for testing
    purposes when progress tracking is not required.

    """

    def __str__(self):
        return f"{self.__class__.__name__} - No progress tracking (used primarily for testing)"

    def __repr__(self):
        return f"<{self.__class__.__name__}>"


    def message(self, msg: str):
        """ Do Nothing"""

    def result_msg(self, current_iteration: int, max_iteration: int, msg: StrOrNone = '',
                   result: Ten8tResultOrNone = None):
        """ Do Nothing"""
