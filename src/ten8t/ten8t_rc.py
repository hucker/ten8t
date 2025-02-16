"""
Handles configuration abstraction for ten8t, includes classes to parse TOML and JSON.
"""
import re
from typing import Sequence

from .ten8t_exception import Ten8tException


class Ten8tRC:
    """
    Loads configurations from a dictionary.
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
            'levels': rc_d.get('levels', [])
        }

        # These will get overwritten
        self.ruids: Sequence[str] = []
        self.ex_ruids: Sequence[str] = []
        self.phases: Sequence[str] = []
        self.ex_phases: Sequence[str] = []
        self.tags: Sequence[str] = []
        self.ex_tags: Sequence[str] = []
        self.levels: Sequence[int] = []
        self.ex_levels: Sequence[int] = []

        self.expand_attributes(rc_data)
        self.name = rc_data['display_name']

        # This is a special case
        self.is_inclusion_list_empty = all(not r for r in [self.ruids,
                                                           self.phases,
                                                           self.tags,
                                                           self.levels])

    # def _not_int_list(self, lst):
    #    return [item for item in lst if not item.isdigit()]

    def _load_config(self, cfg: str, section: str) -> dict:  # pragma no cover
        raise NotImplementedError

    @staticmethod
    def _separate_values(data: str | Sequence[str]) -> tuple[Sequence[str], Sequence[str]]:
        """
        Separate included and excluded values based on sign pre-fixes from the given data.

        This method receives a list of data values and splits it into two lists:
        included values and excluded values. A data value is considered as 'excluded'
        if it starts with a '-' sign, while it is 'included' otherwise (including values without any prefix).

        Spaces and commas are treated as separators for the elements in the list. Non-string
        data elements will be converted to strings.
        
        Args:
            data (Sequence or str): A list of data values or a single string to separate.

        Returns:
            tuple: A tuple containing two lists; the first list consists of included values
                   (those not starting with '-'), and the second list consists of excluded values
                   (those starting with '-').

        Example:
            separate_values(["+apple", "-banana", "+cherry", "-date", "elderberry"])

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

    def expand_attributes(self, rc_data: dict):
        """
        Convert the data from the configuration dictionary into a form that
        is useful for processing in code.
        Args:
            rc_data: dictionary of attributes that should have all expected values

        Exception: If the levels list has an integer it throws an exception
        """

        self.ruids, self.ex_ruids = self._separate_values(rc_data.get('ruids', []))
        self.tags, self.ex_tags = self._separate_values(rc_data.get('tags', []))
        self.phases, self.ex_phases = self._separate_values(rc_data.get('phases', []))
        self.levels, self.ex_levels = self._separate_values(rc_data.get('levels', []))

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
            for pattern_list, attribute in patterns:
                if not attribute:
                    continue
                if pattern_list and not any(re.fullmatch(pat, attribute) for pat in pattern_list):
                    return False

        # Check if any of the inputs match an exclusion pattern
        for ex_pattern_list, attribute in ex_patterns:
            if not attribute:
                continue
            if any(re.fullmatch(exclusion, attribute) for exclusion in ex_pattern_list):
                return False

        return True
