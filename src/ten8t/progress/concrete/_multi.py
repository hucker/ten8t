from .._base import Ten8tProgress
from ...ten8t_result import Ten8tResult
from ...ten8t_util import StrOrNone


class Ten8tMultiProgress(Ten8tProgress):
    """
    A multi-progress handler for managing and consolidating updates across
    multiple progress tracking objects.

    This class inherits from Ten8tProgress and aggregates progress objects
    to allow broadcasting messages and results to all of them. It is
    especially useful when managing parallel or grouped progress tracking
    scenarios, ensuring consistent updates and communication.

    Normally I would expect that you would always use the logging object and
    perhaps you might use the custom one for whatever UI you might be running under
    so it might look like

    log_prog = Ten8tLogProgress()
    streamlit_prog = Ten8tStreamlitProgress()
    multi_prog = Ten8tMultiProgress([log_prog,streamlit_prog])

    ch = ten8t.ten8t_checker(check_functions=[check1,check2],progress=multi_prog)
    ch.run_all()

    Attributes:
        progress_list (list): A list containing progress tracking objects.
    """

    def __init__(self, progress_list):
        if not isinstance(progress_list, list):
            progress_list = [progress_list]

        self.progress_list = progress_list

    def __str__(self):
        return (
            f"Ten8tMultiProgress - Manages Progress for {len(self.progress_list)} Sub-progress Handlers"
        )

    def __repr__(self):
        return (
            f"<Ten8tMultiProgress(progress_list={len(self.progress_list)} handlers)>"
        )

    def message(self, msg):
        if msg:
            for progress in self.progress_list:
                progress.message(msg)

    def result_msg(self, current_iteration: int, max_iteration: int, msg: StrOrNone = '',
                   result: Ten8tResult | None = None):
        for progress in self.progress_list:
            progress.result_msg(current_iteration, max_iteration, msg=msg, result=result)
