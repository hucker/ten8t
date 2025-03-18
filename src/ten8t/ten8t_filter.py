"""
Functions useful for creating function for filtering check functions
"""
from ten8t.ten8t_function import Ten8tFunction


def exclude_ruids(ruids: list[str]):
    """Return a filter function that will exclude the ruids from the list."""

    def filter_func(s_func: Ten8tFunction):
        return s_func.ruid not in ruids

    return filter_func


def exclude_tags(tags: list[str]):
    """Return a filter function that will exclude the tags from the list."""

    def filter_func(s_func: Ten8tFunction):
        return s_func.tag not in tags

    return filter_func


def exclude_levels(levels: list[int]):
    """Return a filter function that will exclude the levels from the list."""

    def filter_func(s_func: Ten8tFunction):
        return s_func.level not in levels

    return filter_func


def exclude_phases(phases: list[str]):
    """Return a filter function that will exclude the phases from the list."""

    def filter_func(s_func: Ten8tFunction):
        return s_func.phase not in phases

    return filter_func


def keep_ruids(ruids: list[str]):
    """Return a filter function that will keep the ruids from the list."""

    def filter_func(s_func: Ten8tFunction):
        return s_func.ruid in ruids

    return filter_func


def keep_tags(tags: list[str]):
    """Return a filter function that will keep the tags from the list."""

    def filter_func(s_func: Ten8tFunction):
        return s_func.tag in tags

    return filter_func


def keep_levels(levels: list[int]):
    """Return a filter function that will keep the levels from the list."""

    def filter_func(s_func: Ten8tFunction):
        return s_func.level in levels

    return filter_func


def keep_phases(phases: list[str]):
    """Return a filter function that will keep the phases from the list."""

    def filter_func(s_func: Ten8tFunction):
        return s_func.phase in phases

    return filter_func
