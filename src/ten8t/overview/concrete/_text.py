"""
Ten8tTextOverview

The purpose of this class is to generate a text representation of the test setup.  This ONLY contains
information about the test setup, including all the attributes set on each check function as
well the values in the environment.  This file provides a snapshot to the test configuration.

"""
import io
from datetime import datetime as dt

from .._base import Ten8tAbstractOverview


class Ten8tTextOverview(Ten8tAbstractOverview):
    """
    GitHub Markdown renderer that extends basic markdown with GitHub-specific features.
    GitHub Markdown supports HTML-based color styling and other GitHub-specific features.
    """

    TAB = "  "
    """Used for offsetting levels in text output"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _tab(self, level: int, msg):
        return self.TAB * level + msg + '\n'

    def generate_environment(self, file_: io.TextIOBase):
        file_.write(self._tab(0, "Environment:"))
        if self.checker.env:
            for key, value in self.checker.env.items():
                file_.write(self._tab(1, f"{key}: {value}"))
        else:
            file_.write(self._tab(1, "No environment data provided."))

    def generate_heading(self, file_: io.TextIOBase):
        formatted_datetime = dt.now().strftime("%Y-%m-%d %H:%M:%S")

        header = f"Checker Overview Generated on {formatted_datetime}"
        file_.write(self._tab(0, header))
        file_.write(self._tab(0, "=" * len(header)))
        file_.write('\n')
        file_.write(self._tab(0, f"Checker Setup: {self.checker.name}"))
        file_.write(self._tab(1, f"Check count = {self.checker.function_count}"))
        file_.write('\n')

    def generate_checks(self, file_: io.TextIOBase):
        name = self.checker.name or "Checker"
        file_.write('\n')
        file_.write(self._tab(0, f"Check Functions for {name}"))

        for check in self.checker.check_functions:
            attributes = {
                "Name": check.function_name,
                "Index": check.index,
                "RUID": check.ruid,
                "Tag": check.tag,
                "Phase": check.phase,
                "Level": check.level,
                "Weight": check.weight,
                "Thread ID": check.thread_id,
                "Attempts": check.attempts,
                "Skip on None": check.skip_on_none,
                "Fail on None": check.fail_on_none,
                "Finish on Fail": check.finish_on_fail,
            }

            for attr, value in attributes.items():
                file_.write(self._tab(1, f"{attr}: {value}"))

            if check.parameters:
                file_.write(self._tab(1, "Environment Parameters:"))
                ep = ""
                for parameter in check.parameters:
                    ep += f'{parameter} '
                file_.write(self._tab(2, ep + '\n'))
            else:
                file_.write(self._tab(1, "No environment data provided."))

            if check.doc:
                file_.write(self._tab(1, f"Description:"))
                for line in check.doc.splitlines():
                    file_.write(self._tab(2, f"{line}"))
                file_.write("\n")  # Add a blank line between checks for readability

    def generate_footer(self, file_: io.TextIOBase):

        pass
