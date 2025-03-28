"""
Allow the usage of a TOML file as an RC file.
"""

import pathlib

import toml

from .._base import Ten8tRC
from ...ten8t_exception import Ten8tException


class Ten8tTomlRC(Ten8tRC):
    """
    Configuration handler for TOML files specific to a section.

    Allows loading of a specific section from a TOML configuration file and dynamically
    expands its attributes, enabling flexible access to the data.

    Attributes:
        cfg (str): Path to the TOML configuration file.
        section (str): Section of the TOML file to load and parse.
    """

    def __init__(self, cfg: str, section: str):
        super().__init__()
        section_data = self._load_config(cfg, section)
        self.cfg = cfg
        self.section = section
        self.expand_attributes(section_data)

    def _load_config(self, cfg: str, section: str) -> dict:
        """
        Loads a specific section from a TOML configuration file.

        Reads a TOML configuration file and extracts the specified section. If issues
        occur during file reading or parsing, raises a `Ten8tException`.

        Args:
            cfg (str): File path to the TOML configuration file.
            section (str): Name of the section to retrieve.

        Returns:
            dict: Key-value pairs from the specified section of the file.

        Raises:
            Ten8tException: If the TOML file cannot be found, is invalid, or cannot
            be parsed.
        """
        cfg_file = pathlib.Path(cfg)

        try:
            with cfg_file.open("rt", encoding="utf-8") as file:
                config_data = toml.load(file)
        except (FileNotFoundError, toml.TomlDecodeError, AttributeError, PermissionError) as error:
            raise Ten8tException(f"TOML config file {cfg} error: {error}") from error

        return config_data.get(section, {})
