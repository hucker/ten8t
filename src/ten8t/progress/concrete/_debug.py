from .._base import Ten8tProgress
from ...ten8t_result import Ten8tResult
from ...ten8t_util import StrOrNone


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

    def __str__(self):
        return "Ten8tDebugProgress - Debug progress tracker displaying messages in stdout"

    def __repr__(self):
        return "<Ten8tDebugProgress>"

    def message(self, msg: str):
        if msg:
            print(msg)

    def result_msg(self, current_iteration: int, max_iteration: int, msg: StrOrNone = '',
                   result: Ten8tResult | None = None):
        if result:
            print("+" if result.status else "-", end="")
