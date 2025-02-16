"""
Allow the usage of an JSON file as an RC file.  
"""
import json
import pathlib

from .ten8t_exception import Ten8tException
from .ten8t_rc import Ten8tRC


class Ten8tJsonRC(Ten8tRC):
    """
    Loads configurations from JSON files. Extends Ten8tRC.
    """

    def __init__(self, cfg: str, section: str):
        section_data = self._load_config(cfg, section)

        self.expand_attributes(section_data)

    def _load_config(self, cfg: str, section: str) -> dict:
        """Loads and returns the requested section from a JSON file."""
        cfg_file = pathlib.Path(cfg)
        try:
            with cfg_file.open("rt", encoding="utf8") as j:
                config_data = json.load(j)
        except (FileNotFoundError, json.JSONDecodeError, AttributeError, PermissionError) as error:
            raise Ten8tException(f"JSON config {cfg} error: {error}") from error

        return config_data.get(section, {})
