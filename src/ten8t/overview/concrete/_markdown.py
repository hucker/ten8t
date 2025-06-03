"""
Ten8tMarkdownOverview

The purpose of this class is to generate a text representation of the test setup.  This ONLY contains
information about the test setup, including all the attributes set on each check function as
well the values in the environment.  This file provides a snapshot to the test configuration.

"""
import io
from datetime import datetime as dt

from .._base import Ten8tAbstractOverview


class Ten8tMarkdownOverview(Ten8tAbstractOverview):
    """
    Generate Markdown text for a given checker.
    """

    def _heading(self, text, heading_level=3):

        return f"\n{'#' * heading_level} {text}\n\n"

    def _generate_md_table(self,
                           key_header: str = 'Key',
                           value_header: str = 'Value',
                           data: dict = None) -> str:
        """
        Generate a Markdown table from a dictionary.

        Parameters:
            key_header (str): The header name for the "Key" column.
            value_header (str): The header name for the "Value" column.
            data (dict): A dictionary containing key-value pairs.

        Returns:
            str: A string representation of the Markdown table.
        """
        if not data:
            return ""

        # Markdown header
        table = f"| {key_header} | {value_header} |\n"
        table += f"|{'-' * (len(key_header) + 2)}|{'-' * (len(value_header) + 2)}|\n"  # Divider row

        # Add the data rows
        for key, value in data.items():
            table += f"| {key} | {value} |\n"

        return table

    def generate_heading(self, file_: io.TextIOBase):
        formatted_datetime = dt.now().strftime("%Y-%m-%d %H:%M:%S")

        header = self._heading(f'Checker Overview Generated on {formatted_datetime}')

        table = self._generate_md_table(data={"Checker Setup": self.checker.name,
                                              "Check count": self.checker.function_count})
        file_.write(header)
        file_.write(table)

    def generate_environment(self, file_: io.TextIOBase):

        if not self.checker.env:
            return

        header = self._heading(f"Environment")
        table = self._generate_md_table(data=self.checker.env)
        file_.write(header)
        file_.write(table)

    def generate_checks(self, file_: io.TextIOBase):
        name = self.checker.name or "Checker"
        header = self._heading(f'Check Functions for {name}\n')
        file_.write(header)

        for check in self.checker.check_func_list:
            attributes = {
                "Index": check.index,
                "RUID": check.ruid or "N/A",
                "Tag": check.tag or "N/A",
                "Phase": check.phase or "N/A",
                "Level": check.level or "N/A",
                "Weight": check.weight,
                "Thread ID": check.thread_id,
                "Attempts": check.attempts,
                "Skip on None": check.skip_on_none,
                "Fail on None": check.fail_on_none,
                "Finish on Fail": check.finish_on_fail,
                "Parameters": check.parameters or "N/A",
                "Skip": check.skip,
            }

            if check.doc:
                file_.write(self._heading(f"Doc string for {check.function_name}:\n",
                                          heading_level=4))
                file_.write(f"```text\n{check.doc}\n```\n")

            table = self._generate_md_table(data=attributes)

            file_.write(table)

    def generate_footer(self, file_: io.TextIOBase):

        pass
