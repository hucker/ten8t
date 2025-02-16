"""
Allow the usage of an TOML file as an RC file.  
"""
import pathlib

import toml

from .ten8t_exception import Ten8tException
from .ten8t_rc import Ten8tRC


class Ten8tTomlRC(Ten8tRC):
    """
    Loads configurations from TOML files. Extends Ten8tRC.
    """

    def __init__(self, cfg: str, section: str):
        section_data = self._load_config(cfg, section)

        self.expand_attributes(section_data)

    def _load_config(self, cfg: str, section: str) -> dict:
        """Loads and returns the requested section from a TOML file."""
        cfg_file = pathlib.Path(cfg)
        try:
            with cfg_file.open("rt", encoding="utf8") as t:
                config_data = toml.load(t)
        except (FileNotFoundError, toml.TomlDecodeError, AttributeError, PermissionError) as error:
            raise Ten8tException(f"TOML config file {cfg} error: {error}") from error

        return config_data.get(section, {})
