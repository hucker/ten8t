"""
Functions for sanitizing results before scoring.
"""
from functools import wraps

from ..ten8t_result import Ten8tResult


def sanitize_results(func):
    """
    A decorator that ensures scoring methods receive a valid list of results.
    Handles None, skips invalid entries, and provides a clean list of results.

    This simplifies most scoring functions by handling the integrity checks
    internally.
    """

    @wraps(func)
    def wrapper(self, results: list["Ten8tResult"] | None):
        if results is None:
            return 0.0
        results = [result for result in results if not result.skipped]
        if not results:
            return 0.0
        return func(self, results)

    return wrapper
