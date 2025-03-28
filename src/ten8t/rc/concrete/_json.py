"""
Allow the usage of an JSON file as an RC file.
"""
import json
import pathlib

from .._base import Ten8tRC
from ...ten8t_exception import Ten8tException


class Ten8tJsonRC(Ten8tRC):
    """
    Represents a JSON-based configuration reader.

    This class is used for loading configuration data from a JSON file and
    populating its attributes dynamically based on the loaded configuration. It
    extends the base functionality of the `Ten8tRC` class.

    Attributes:
        Any attributes dynamically created from the loaded configuration data will
        be added to this class instance.
    """

    def __init__(self, cfg: str, section: str):
        """
        Initializes a class instance and processes configuration data from a given file
        and section.

        The constructor reads configuration data from the specified file and section,
        expanding attributes dynamically based on the extracted configuration content.

        Args:
            cfg: Path to the configuration file as a string.
            section: Name of the section in the configuration file to process as a string.
        """
        super().__init__()
        section_data = self._load_config(cfg, section)

        self.expand_attributes(section_data)

    def _load_config(self, cfg: str, section: str) -> dict:
        """
        Loads a configuration section from a JSON configuration file. The method reads the given
        JSON file, parses its content, and retrieves the specified section. If the file cannot
        be read or does not adhere to proper JSON formatting, an exception is raised.

        Args:
            cfg (str): The path to the JSON configuration file to be loaded.
            section (str): The specific section to retrieve from the JSON configuration file.

        Returns:
            dict: The content of the specified section from the configuration file as a dictionary.

        Raises:
            Ten8tException: If there is a problem with reading the file (e.g., file not found,
                permission issues, decoding errors, incorrect file attributes).
        """
        cfg_file = pathlib.Path(cfg)
        try:
            with cfg_file.open("rt", encoding="utf8") as j:
                config_data = json.load(j)
        except (FileNotFoundError, json.JSONDecodeError, AttributeError, PermissionError) as error:
            raise Ten8tException(f"JSON config {cfg} error: {error}") from error

        return config_data.get(section, {})
