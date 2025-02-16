"""
Allow the usage of an INI file as an RC file.  
"""
import configparser

from .ten8t_exception import Ten8tException
from .ten8t_rc import Ten8tRC


class Ten8tIniRC(Ten8tRC):
    """
    Loads configurations from TOML files. Extends Ten8tRC.
    """

    def __init__(self, cfg: str, section: str):
        section_data = self._load_config(cfg, section)

        self.expand_attributes(section_data)

    def _load_config(self, cfg: str, section: str) -> dict:
        """Loads and returns the requested section from a TOML file."""
        try:
            config = configparser.ConfigParser()
            config.read(cfg, encoding="utf-8")
            if not section:
                raise Ten8tException("Section must be provided to read INI RC files.")
            d = {"tags": config.get(section, "tags"),
                 "ruids": config.get(section, "ruids"),
                 "phases": config.get(section, "phases")}

        except (FileNotFoundError, TypeError, configparser.Error, PermissionError) as error:
            raise Ten8tException(f"INI config file {cfg} error: {error}") from error

        return d
