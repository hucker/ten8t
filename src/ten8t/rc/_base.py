"""
Handles configuration abstraction for ten8t, includes classes to parse TOML and JSON.
"""
import re
from typing import Sequence

from ..ten8t_exception import Ten8tException
from ..ten8t_types import IntList, StrList, StrOrPathList


class Ten8tRC:
    """
    The baseline configuration for ten8t is a simple dictionary.  Loading data
    from file should be a straight forward conversion into the interal dict format.

    Usually RC files are for things like tags,phases and levels, but a more complete
    setup is possible since higher level "things" like folders, modles and environments
    can be specified.
    """

    def __init__(self, *, rc_d: dict | None = None):

        # Any falsy value ends up being valid...which means that setting
        # rcd=0 will work.
        rc_d = rc_d or {}

        # This gives a nicer error than what might happen when you pass randomness
        # to the next function
        if not isinstance(rc_d, dict):
            raise Ten8tException(f"Ten8tRC expects a dictionary but got '{type(rc_d)}'")

        # This is being quite paranoid, but allows for the user to only specify what is
        # needed rather that having data structures filled with []
        rc_data = {
            'display_name': rc_d.get('display_name', 'NoName'),
            'ruids': rc_d.get('ruids', []),
            'tags': rc_d.get('tags', []),
            'phases': rc_d.get('phases', []),
            'levels': rc_d.get('levels', []),
            'modules': rc_d.get('modules', []),
            'module_glob': rc_d.get('module_glob', ''),
            'packages': rc_d.get('packages', []),
            'check_prefix': rc_d.get('check_prefix', 'check_'),
            'env_prefix': rc_d.get('env_prefix', 'env_'),
            'env': rc_d.get('env', {}),
            'renderer': rc_d.get('renderer', 'text'),
            'serialize': rc_d.get('serialize', ''),
            'display_name': rc_d.get('display_name', '') or rc_d.get('name', ''),

        }

        # These will get overwritten
        self.ruids: StrList = []
        self.ex_ruids: StrList = []
        self.phases: StrList = []
        self.ex_phases: StrList = []
        self.tags: StrList = []
        self.ex_tags: StrList = []
        self.levels: IntList = []
        self.ex_levels: IntList = []

        # Populate the category data for inclusions and exclusions
        self.expand_category_attributes(rc_data)

        # This is a special case for when nothing is specified by the user.
        self.is_inclusion_list_empty = all(not r for r in [self.ruids,
                                                           self.phases,
                                                           self.tags,
                                                           self.levels])
        self.packages: StrOrPathList = rc_data['packages']
        self.modules: StrOrPathList = rc_data['modules']
        self.check_prefix = rc_data['check_prefix']

        self.env: dict = rc_data['env']

        # TODO:  Pick one of these.
        self.name = rc_data['display_name']
        self.display_name = rc_data['display_name']

    # def _not_int_list(self, lst):
    #    return [item for item in lst if not item.isdigit()]

    def _load_config(self, cfg: str, section: str) -> dict:  # pragma no cover
        raise NotImplementedError

    @staticmethod
    def _separate_category_values(data: str | Sequence[str]) -> tuple[Sequence[str], Sequence[str]]:
        """
        Separate included and excluded category values based on sign pre-fixes from the given data.

        This method receives a list of data values and splits it into two lists:
        included values and excluded values. A data value is considered as 'excluded'
        if it starts with a '-' sign, while it is 'included' otherwise
        (including values without any prefix).

        Spaces and commas are treated as separators for the elements in the list. Non-string
        data elements will be converted to strings.

        Args:
            data (Sequence or str): A list of data values or a single string to separate.

        Returns:
            tuple: A tuple containing two lists; the first list consists of included values
                   (those not starting with '-'), and the second list consists of excluded values
                   (those starting with '-').

        Example:
            _separate_category_values(["+apple", "-banana", "+cherry", "-date", "elderberry"])

            Should return (['apple', 'cherry', 'elderberry'], ['banana', 'date']) as
            "elderberry" doesn't start with a "-" sign, it is also included in the 'included' list.

        """
        data = data.replace(',', ' ').split() if isinstance(data, str) else data

        # Always make sure data elements are string
        data = [str(item) for item in data]

        # Separate included and excluded values note that + is optional
        included = [x.lstrip('+') for x in data if not x.startswith('-')]
        excluded = [x.lstrip('-') for x in data if x.startswith('-')]

        return included, excluded

    def expand_category_attributes(self, rc_data: dict):
        """
        Convert the data from the configuration dictionary into a form that
        is useful for processing in code.
        Args:
            rc_data: dictionary of attributes that should have all expected values

        Exception: If the levels list has an integer it throws an exception
        """

        self.ruids, self.ex_ruids = self._separate_category_values(rc_data.get('ruids', []))
        self.tags, self.ex_tags = self._separate_category_values(rc_data.get('tags', []))
        self.phases, self.ex_phases = self._separate_category_values(rc_data.get('phases', []))
        self.levels, self.ex_levels = self._separate_category_values(rc_data.get('levels', []))

    def does_match(self, ruid: str = "", tag: str = "", phase: str = "", level: str = "") -> bool:
        """
        Determines whether a given `ruid`/`tag`/`phase`/`level` matches any of the inclusions
        defined, and doesn't match any of the exclusions.

        With no inclusions defined, all values are included by default. Exclusion matching takes
        precedent over inclusion matching.

        Args:
            ruid (str): The RUID string to check.
            tag (str): The tag string to check.
            phase (str): The phase string to check.
            level (int): The level integer to check.

        Returns:
            bool: True if it matches any inclusion and doesn't match any exclusion, False otherwise.
        """

        # This is sort of a hack levels must be integers, this makes any non integer level not match
        level = str(level)

        # This is a bit problematic because levels are ints not strs
        patterns: list[tuple[Sequence[str], str]] = [(self.ruids, ruid),
                                                     (self.tags, tag),
                                                     (self.levels, level),
                                                     (self.phases, phase)]
        ex_patterns: list[tuple[Sequence[str], str]] = [(self.ex_ruids, ruid),
                                                        (self.ex_tags, tag),
                                                        (self.ex_levels, level),
                                                        (self.ex_phases, phase)]

        # Check if any of the inputs match an inclusion pattern
        if not self.is_inclusion_list_empty:
            for pattern_list, category in patterns:
                if not category:
                    continue
                if pattern_list and not any(re.fullmatch(pat, category) for pat in pattern_list):
                    return False

        # Check if any of the inputs match an exclusion pattern
        for ex_pattern_list, category in ex_patterns:
            if not category:
                continue
            if any(re.fullmatch(exclusion, category) for exclusion in ex_pattern_list):
                return False

        return True

    def get_dotted(self, config: dict, key: str):
        """
        Retrieves a nested value from a dictionary using a dotted notation string.

        Args:
            config (dict): The configuration dictionary to search in.
            key (str): The dotted notation key string (e.g., "setup.env.env_list").

        Returns:
            Any: The value corresponding to the dotted key, or None if a key is missing.
        """
        keys = key.split(".")
        value = config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return None  # Return None if any key in the hierarchy is missing
