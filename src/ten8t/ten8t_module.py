"""
Ten8tModule represents a module with a functions set that can be run. A module
typically symbolizes a file imported into the system. It does this by identifying
all functions starting with a certain prefix and adding them to a list managed
by ten8t.
"""

import importlib
import inspect
import pathlib
import sys
from collections import Counter

from .ten8t_exception import Ten8tException
from .ten8t_function import Ten8tFunction
from .ten8t_util import next_int_value


class Ten8tModule:
    """
    A module is a collection of functions that is read from a file.  The check_ functions
    are used to verify rules, while the env_functions are used to set up any parameters
    that the rule functions might need.
    """
    AUTO_THREAD_PREFIX = "auto_thread_module"

    def __init__(
            self,
            *,
            module_file: pathlib.Path | str,
            module_name: str | None = None,
            check_prefix="check_",
            env_prefix="env_",
            env_functions: list | None = None,
            auto_load=True,
            auto_thread=False
    ) -> None:
        """
        Initialize a Ten8tModule instance that manages a collection of functions from a specified module file.

        This constructor sets up the module's core properties, including file path, name, and function prefixes.
        It can optionally load the module immediately and configure automatic threading.

        Args:
            module_file (str): Path to the Python file containing the module's functions.
            module_name (str | None, optional): Name of the module. If None, will be derived from the file name.
                Defaults to None.
            check_prefix (str, optional): Prefix used to identify check functions in the module.
                Defaults to "check_".
            env_prefix (str, optional): Prefix used to identify environment setup functions in the module.
                Defaults to "env_".
            env_functions (list | None, optional): Pre-defined list of environment functions.
                Defaults to None.
            auto_load (bool, optional): Whether to load the module automatically upon initialization.
                Defaults to True.
            auto_thread (bool, optional): Whether to automatically assign thread IDs to functions
                that don't have them. Defaults to False.

        Returns:
            None

        Note:
            When auto_load is True, the module is immediately loaded using the load() method.
            When auto_thread is True, check functions without thread IDs are assigned
            automatically generated ones.
        """

        if module_name is None:
            module_name = pathlib.Path(module_file).stem

        self.module_name: str = module_name
        self.check_functions: list[Ten8tFunction] = []
        self.env_functions: list = env_functions or []
        self.module = None
        self.module_file: str = module_file
        self.check_prefix: str = check_prefix
        self.env_prefix: str = env_prefix
        self.auto_thread: str = auto_thread
        self.doc = ""
        if auto_load:
            self.load()

    def __str__(self):
        return (
            f"Ten8tModule({self.module_name=},{self.check_function_count=})".replace("self.", '')
        )

    @property
    def check_function_count(self) -> int:
        """Return the check function count..."""
        return len(self.check_functions) if self.check_functions else 0

    def add_check_function(self, module, function):
        """Wrap the function in a ten8t function"""
        function = Ten8tFunction(function, module)
        self.check_functions.append(function)

    def add_env_function(self, func):
        """Add a discovered environment function to the list"""
        self.env_functions.append(func)

    @staticmethod
    def _add_sys_path(module_file: str | pathlib.Path) -> list[str]:
        """
        Add a module's directory to sys.path.
        If it is already there do nothing. 
        """

        # Construct a Path object from the provided file path and get its parent directory
        module_dir = pathlib.Path(module_file).parent.resolve()

        # Check if the module directory is already in sys.path
        if module_dir not in (pathlib.Path(path).resolve() for path in sys.path):
            sys.path.insert(0, str(module_dir))

        return sys.path

    # If not, add it to sys.path

    def load(self, module_name=None):
        """
        Loads a specified module and initializes relevant properties. The method dynamically
        loads a Python module by its name, processes its documentation, handles specific
        functionalities, and manages multi-threading behaviors if required.

        Args:
            module_name (str, optional): The name of the module to load. If not provided,
            it will default to self.module_name.

        Returns:
            bool: True if the module loads successfully.

        Raises:
            Ten8tException: If the specified module cannot be loaded due to an import error.
        """
        module_name = module_name or self.module_name
        self._add_sys_path(self.module_file)
        try:
            module = importlib.import_module(module_name)
            self.module = module
            # self.doc = module.__doc__
            self.doc = inspect.getdoc(module)
            self.load_special_functions(module)
            self.setup_autothread()
            return True

        except ImportError as iex:
            raise Ten8tException(f"Can't load {module_name}:{iex.msg}") from iex

    def setup_autothread(self):
        """
        Handles automatic threading for functions that do not have an assigned thread ID.

        This method checks if the ``autothread`` property is enabled. If it is, it generates
        a new threading ID in the format "auto_thread_module_{module_name}_{threading_number}_@@".
        Then, for each function in the check_functions list, if the function does not have
        an existing ``thread_id``, it assigns the generated threading ID to it.

        Raises:
            No explicit exceptions are raised by this method.

        """
        if not self.auto_thread:
            return
        threading_number = next_int_value()
        auto_thread_id = f"{self.AUTO_THREAD_PREFIX}_{self.module_name}_{threading_number}_@@"
        for function in self.check_functions:
            if not function.thread_id or function.thread_id == "main_thread__":
                function.thread_id = auto_thread_id

    def load_special_functions(self, module):
        """
        Loads and processes special functions from a provided module or the default module. This
        includes environment functions (prefixed by a specific string) and check functions
        (prefixed by a different specific string). For check functions, an index is assigned to
        each function based on their order in the module. Additionally, the method verifies the
        uniqueness of RUIDs (Resource Unique Identifiers) in the module and raises an exception
        if duplicates are found.

        Args:
            module (object | None): The module to load special functions from. If None, the
                method defaults to using the module associated with the instance.

        Raises:
            Ten8tException: If duplicate RUIDs are found in the module.
        """

        module = module or self.module

        # Dir givens you every element in the module object and allows us to look
        # for check functions that look a certain way
        check_func_count = 0
        for name in dir(module):
            if name.startswith("_"):
                continue
            obj = getattr(module, name)

            if not callable(obj):
                continue

            # Load environment functions
            if name.startswith(self.env_prefix):
                self.add_env_function(obj)

            # Load check functions.  We number them because we care about the 'file' order
            # The file order will let us sort/resort functions and access file order if we want it.
            if name.startswith(self.check_prefix):
                check_func_count += 1
                obj.index = check_func_count
                self.add_check_function(module, obj)

        # Strictly speaking this doesn't need to happen here, it could be checked later
        duplicate_ruids = [
            item
            for item, count in Counter(self.ruids()).items()
            if count > 1 and item != ""
        ]

        if duplicate_ruids:
            raise Ten8tException(
                f"Duplicate RUIDs found in module: {','.join(duplicate_ruids)}"
            )

    def ruids(self):
        """
        Return a list of all the RUIDs in the module.
        Note that this can have duplicates.  The list is
        sorted to facilitate comparison.

        RUID = rule identifier
        """
        return sorted(function.ruid for function in self.check_functions)
