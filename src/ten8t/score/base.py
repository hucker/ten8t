"""
Ten8t scoring package - mechanisms for evaluating and scoring results.
"""
import abc

from ..ten8t_result import Ten8tResult
from ..ten8t_util import StrOrNone


class ScoreStrategy(abc.ABC):
    """
    Represents an abstract base class for scoring strategies in the application.

    The class is designed as an abstract base to define a consistent interface for various
    scoring strategies. Derived classes must implement the `score` method, which computes a
    score based on a list of `Ten8tResult` objects. It also provides a convenient callable
    interface and a factory method for creating registered strategy instances.

    Attributes:
        strategy_name (StrOrNone): The name of the scoring strategy, used as a key for
            registration and instantiation. Defaults to None.
    """

    strategy_name: StrOrNone = None

    @abc.abstractmethod
    def score(self, results: list[Ten8tResult]) -> float:  # pragma: no cover
        """Abstract score method"""

    def __call__(self, results: list[Ten8tResult]):
        """
        Make "calling" the object the same as calling the `score` method.

        Args:
            results (list[Ten8tResult]): A list of Ten8tResult objects that need to be
                processed.

        Returns:
            Any: The computed score based on the `results` passed as input.
        """
        return self.score(results)
