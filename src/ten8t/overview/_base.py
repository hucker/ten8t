import io
import pathlib
import sys
from abc import ABC, abstractmethod

from ten8t.ten8t_checker import Ten8tChecker
from ten8t.ten8t_exception import Ten8tException
from ten8t.ten8t_util import StrOrPathOrNone


class Ten8tAbstractOverview(ABC):
    """
    Provides a mechanism to generate and display documentation
    for a given checker.

    This is an abstract base class defining methods that subclasses
    must implement to generate specific sections of the documentation
    for the desired target.
    """

    def __init__(self,
                 checker: Ten8tChecker,
                 file_name: StrOrPathOrNone = None,
                 show_header: bool = True,
                 show_environment: bool = True,
                 show_checks: bool = True,
                 show_footer: bool = True,
                 verbose: bool = False, ):
        """
        Initializes the Ten8tAbstractOverview instance.

        Args:
            checker (Ten8tChecker): The checker object whose details need to be documented.
            file_name (StrOrPathOrNone, optional): An optional file name where the
                documentation will be saved. If not provided, the content will be printed to stdout.
            show_header (bool, optional): Whether to include the header section in the
                generated documentation. Defaults to True.
            show_environment (bool, optional): Whether to include the environment section
                in the generated documentation. Defaults to True.
            show_checks (bool, optional): Whether to include the checks section in the
                generated documentation. Defaults to True.
            show_footer (bool, optional): Whether to include the footer section in the
                generated documentation. Defaults to True.
        """

        self.checker: Ten8tChecker = checker
        self.file_name: str = str(file_name) if file_name else None

        # This
        self.show_header = show_header
        self.show_environment = show_environment
        self.show_checks = show_checks
        self.show_footer = show_footer
        self.verbose = verbose

    def generate(self, file_name: StrOrPathOrNone = None) -> str:
        """
        Generates an overview of the checker structure and writes it
        to a specified file or stdout.

        If no file name is provided, the content will be written to stdout.

        Args:
            file_name (StrOrPathOrNone, optional): A file path to save the
                generated documentation. Defaults to None, in which case stdout
                is used.

        Raises:
            Ten8tException: If the provided stream is not writable.
        """

        self.file_name = file_name or self.file_name

        if self.file_name:
            # Write to the specified file
            with open(self.file_name, 'w') as file_:
                self._write_to_stream(file_)
            return self.get_text()
        else:
            # Write to sys.stdout
            self._write_to_stream(sys.stdout)
            return ""

    def get_text(self):
        """
        Get the contents of the file that was saved.

        NOTE: If you were writing to stdout (no file name) then you don't get anything back.
        """
        if self.file_name:
            return pathlib.Path(self.file_name).read_text()
        else:
            return ''

    def _write_to_stream(self, stream: io.TextIOBase):
        """
        Helper method to write documentation content to a file-like stream
        (file handle or stdout).

        Args:
            stream (io.TextIOBase): A writable file-like object, such as a file handle
                or `sys.stdout`.

        Raises:
            ValueError: If the provided stream is not writable.
        """
        # Ensure the stream is writable
        if not hasattr(stream, "write"):
            raise Ten8tException(f"Provided stream {type(stream)} is not writable. Overview aborted.")

        if self.show_header:
            self.generate_heading(stream)

        if self.show_environment:
            self.generate_environment(stream)

        if self.show_checks:
            self.generate_checks(stream)

        if self.show_footer:
            self.generate_footer(stream)

    @abstractmethod
    def generate_heading(self, file_: io.TextIOBase):
        """
        Generates the heading section of the documentation.

        Args:
            file_ (io.TextIOBase | None, optional): A writable file-like object where
                the heading section will be written. Defaults to None.
        """
        pass

    @abstractmethod
    def generate_environment(self, file_: io.TextIOBase):
        """
        Generates the environment section of the documentation.

        Args:
            file_ (io.TextIOBase | None, optional): A writable file-like object where
                the environment section will be written. Defaults to None.
        """
        pass

    @abstractmethod
    def generate_checks(self, file_: io.TextIOBase):
        """
        Generates the checks section of the documentation.

        Args:
            file_ (io.TextIOBase | None, optional): A writable file-like object where
                the checks section will be written. Defaults to None.
        """
        pass

    @abstractmethod
    def generate_footer(self, file_: io.TextIOBase):
        """
        Generates the footer section of the documentation.

        Args:
            file_ (io.TextIOBase | None, optional): A writable file-like object where
                the footer section will be written. Defaults to None.
        """
        pass
