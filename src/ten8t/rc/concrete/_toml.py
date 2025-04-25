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
        section_data = self._load_config(cfg, section)

        # Call the baseclass that knows how to deal with a dictionary
        super().__init__(rc_d=section_data)
        self.cfg = cfg

    def _load_config(self, cfg: str, section: str = '', sep='.') -> dict:
        """
        Loads a specific section from a TOML configuration file.

        Reads a TOML configuration file and extracts the specified section. If issues
        occur during file reading or parsing, raises a `Ten8tException`.

        Because we don't really know the structure of the TOML file this supports
        a 'dotted-key' so you can say

        section='config1.prerelease'

        Which will do the same as giving you the data from this branch of the config file

        cfg['config1']['prerelease']

        Args:
            cfg (str): File path to the TOML configuration file.
            section (str): Name of the section to retrieve.
            sep (str): Separator character used to split dotted keys.  Should always be '.'

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

        if not section:
            return config_data

        # Handle nested sections using dotted keys with .get
        keys = section.split(sep)
        for key in keys:
            config_data = config_data.get(key, {})
        return config_data
