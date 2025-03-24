"""
Type protocols for the scoring system.
"""
from typing import Protocol

from ..ten8t_result import Ten8tResult


class ScoreStrategyProtocol(Protocol):
    """Protocol defining the interface for score strategies"""

    strategy_name: str

    def score(self, results: list[Ten8tResult]) -> float:
        """
        Calculate a score based on results.

        Args:
            results: The results to score

        Returns:
            The calculated score
        """
        ...

    def __call__(self, results: list[Ten8tResult]) -> float:
        """
        Make the strategy callable for convenience.

        Args:
            results: The results to score

        Returns:
            The calculated score
        """
        ...
