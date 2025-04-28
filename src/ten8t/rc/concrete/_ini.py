"""
Allow the usage of an INI file as an RC file.
"""
import configparser

from .._base import Ten8tRC
from ...ten8t_exception import Ten8tException


class Ten8tIniRC(Ten8tRC):
    """
    Loads configurations from INI files. Extends Ten8tRC.

    Note that INI files only support ONE level of section.
    """

    def __init__(self, cfg: str, section: str):
        section_data = self._load_config(cfg, section)
        super().__init__(rc_d=section_data)

        self.expand_category_attributes(section_data)

    def _load_config(self, cfg: str, section: str = '') -> dict:
        """Loads and returns the requested section from a TOML file."""
        try:
            config = configparser.ConfigParser()
            config.read(cfg, encoding="utf-8")
            if not section:
                raise Ten8tException("Section must be provided to read INI RC files.")
            if section not in config.sections():
                raise Ten8tException(f"Unknown INI section {section}")

            def mk_list(key):
                # Convert list of space or , separated values into a list of strings
                return config.get(section, key, fallback='').replace(',', ' ').split()

            # INI's work differently with the fallback mechanism so we build a dict
            # and we use split to build lists assuming the ' ' separator
            d = {"tags": mk_list("tags"),
                 "ruids": mk_list("ruids"),
                 "phases": mk_list("phases"),
                 "levels": mk_list("levels"),
                 "modules": mk_list("modules"),
                 "packages": mk_list("packages"),
                 "module_glob": config.get(section, "module_glob", fallback="check*.py"),
                 "check_prefix": config.get(section, "check_prefix", fallback="check_"),
                 "name": config.get(section, "name", fallback=""),
                 }

            # Add "env" section data if it exists
            if "env" in config.sections():
                d["env"] = dict(config.items("env"))
            else:
                d["env"] = {}

        except (FileNotFoundError, TypeError, configparser.Error, PermissionError) as error:
            raise Ten8tException(f"INI config file {cfg} error: {error}") from error

        return d
