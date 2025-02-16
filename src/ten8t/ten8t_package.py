"""
This module contains the `Ten8tPackage` class, which provides the functionality to load Ten8t
modules from a specified directory, manage these modules, and retrieve their properties.

The `Ten8tPackage` class provides the following main functionalities:

- Initialization allows specifying a directory, a naming glob pattern for the modules,
  a prefix for the functions, an option to autoload modules, a name for the package, and a
  dictionary of environment parameters.

- You can dynamically load modules from the directory matching the module_glob pattern.

- Access loaded modules directly through the `get` method and query the total
  number of modules via `module_count` property.

- Retrieve all the unique identifiers of rules existing within these modules through
  the `ruids` method.

The modules are added to the system path for easy import and use in other Python files.
"""
import pathlib
import sys

from .ten8t_exception import Ten8tException
from .ten8t_module import Ten8tModule
from .ten8t_result import Ten8tResult


class Ten8tPackage:
    """This class handles loading all modules from a folder that match a
       given file name pattern."""

    def __init__(
            self,
            folder="check",
            module_glob="check_*.py",
            function_prefix="check_",
            auto_load=True,
            name=None,
            env: dict | None = None,
    ):
        self.modules: list[Ten8tModule] = []
        self.folder: pathlib.Path = pathlib.Path(folder)
        self.module_glob: str = module_glob
        self.function_prefix: str = function_prefix
        self.env: dict = env or {}
        self.results: list[Ten8tResult] = []

        if not name:
            self.name = self.folder.name
        else:
            self.name = name

        self.folder = self.folder.resolve()

        # Add to module search path
        self._add_folder_to_sys_path(self.folder)

        self._verify_dir()

        if auto_load:
            self.load_modules()

    def _verify_dir(self):
        # Catastrophic, ten8t can't work with in check folder
        if not self.folder.exists():
            raise Ten8tException(
                f"The ten8t check folder '{self.folder}' does not exist."
            )

    @staticmethod
    def _add_folder_to_sys_path(folder):
        if not folder:
            return

        # Convert the folder path to an absolute path
        absolute_folder_path = pathlib.Path(folder).resolve()

        # Check if the absolute folder path is in sys.path
        if not any(
                pathlib.Path(path).resolve() == absolute_folder_path for path in sys.path
        ):
            # If it's not, add it to sys.path
            sys.path.insert(0, str(absolute_folder_path))

    @property
    def module_count(self) -> int:
        """ Count the number of modules in a package. """
        return 0 if not self.modules else len(self.modules)

    def load_modules(self, glob=None) -> list[Ten8tModule]:
        """ Find all the files that match the pattern and load the modules. """
        check_file_glob = glob or self.module_glob

        for file_path in sorted(self.folder.glob(check_file_glob)):
            module_name = f"{file_path.stem}"

            module = Ten8tModule(module_name, module_file=str(file_path), auto_load=True)
            self.modules.append(module)

        return self.modules

    def get(self, module_name) -> Ten8tModule | None:
        """Find a module given its name."""
        for module in self.modules:
            if module.module_name == module_name:
                return module
        return None

    def ruids(self):
        """get a list of all the RUIDS in a package"""
        ruids = []
        for module in self.modules:
            ruids.extend(module.ruids())
        return sorted(ruids)
