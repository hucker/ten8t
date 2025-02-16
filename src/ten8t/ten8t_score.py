"""Basic scoring algorithms for Ten8t test results. """

import abc
from typing import Any

from .ten8t_exception import Ten8tException
from .ten8t_result import Ten8tResult


class ScoreStrategy(abc.ABC):
    """
    A strategy for scoring the results of a Ten8t run.
    It is assumed that many scoring strategies could be implemented, this provides a way
    for those strategies to be implemented in code (by providing a class) or from file
    by providing a name that matches the class strategy name attribute.
    """

    strategy_name: str | None = None

    @abc.abstractmethod
    def score(self, results: list[Ten8tResult]) -> float:  # pragma: no cover
        """Abstract score method"""

    def __call__(self, results: list[Ten8tResult]):
        return self.score(results)

    @classmethod
    def strategy_factory(cls, strategy_name_or_class) -> "ScoreStrategy":
        """Make a strategy object from a name or class.
        This will be read from files or code, so they support both"""
        if isinstance(strategy_name_or_class, str):
            # Note this only goes one level deep in subclasses, which for now is good enough.
            for subclass in cls.__subclasses__():
                if strategy_name_or_class in (subclass.strategy_name, subclass.__name__):
                    return subclass()
            raise Ten8tException(
                f"No scoring strategy with name '{strategy_name_or_class}' found."
            )
        if issubclass(strategy_name_or_class, cls):
            return strategy_name_or_class()
        raise Ten8tException(
            "Argument must be a strategy name or a ScoreStrategy subclass.")


class ScoreByResult(ScoreStrategy):
    """Calculate the score by individually weighting each result"""

    strategy_name = "by_result"

    def score(self, results: list[Ten8tResult] | None = None) -> float:
        """Weighted result of all results."""

        if results is None:
            return 0.0

        weight_sum = 0.0
        passed_sum = 0.0
        # Remove any skipped results
        results = [result for result in results if not result.skipped]
        if not results:
            return 0.0
            # raise Ten8tException("No results to score.")

        for result in results:
            passed_sum += result.weight if result.status else 0.0
            weight_sum += result.weight

        return (100.0 * passed_sum) / (weight_sum * 1.0)


class ScoreByFunctionBinary(ScoreStrategy):
    """Calculate the score by requiring ALL results from a function
       to have status=True to consider the function passed."""

    strategy_name = "by_function_binary"

    def score(self, results: list[Ten8tResult] | None = None) -> float:
        """If any result on a function fails then the function fails."""
        if results is None:
            return 0.0

        score_functions: dict[str, Any] = {}

        for result in results:
            key = f"{result.pkg_name}.{result.module_name}.{result.func_name}".lstrip(
                "."
            )
            score_functions.setdefault(key, []).append(result)

        # Remove any skipped results
        results = [result for result in results if not result.skipped]
        if not results:
            return 0.0

        for key, results_ in score_functions.items():
            if not results_:
                score_functions[key] = 0.0
            else:
                score_functions[key] = 100.0 if all(r.status for r in results_) else 0.0

        # The score should be the average of the scores for each function
        return sum(score_functions.values()) / (len(score_functions) * 1.0)


class ScoreByFunctionMean(ScoreStrategy):
    """Calculate score by averaging the results from a function.
       This means that a function could 50% pass"""

    strategy_name = "by_function_mean"

    def score(self, results: list[Ten8tResult] | None = None) -> float:
        """Find the average of the results from each function."""
        if results is None:
            return 0.0

        function_results: dict[str, Any] = {}

        # Remove any skipped results
        results = [result for result in results if not result.skipped]
        if not results:
            return 0.0

        for result in results:
            key = f"{result.pkg_name}.{result.module_name}.{result.func_name}".lstrip(
                "."
            )
            function_results.setdefault(key, []).append(result)

        sum_weights = 0.0
        sum_passed = 0.0

        # Now we have a dictionary of results for each function.  We can now score each function
        for key, results_ in function_results.items():
            for result in results_:
                sum_weights += result.weight
                sum_passed += result.weight if result.status else 0.0

        # This does not appear to be possible.  The empty list is protected against
        # and each of the summed weights must be > 0.  This could be removed?
        if sum_weights == 0.0:
            raise Ten8tException("The sum of weights is 0.  This is not allowed.")

        # The score should be the average of the scores for each function
        return (100.0 * sum_passed) / (sum_weights * 1.0)


class ScoreBinaryFail(ScoreStrategy):
    """Anything fails then the test is a fail.  Empty results fail."""

    strategy_name = "by_binary_fail"

    def score(self, results: list[Ten8tResult] | None) -> float:
        if results is None:
            return 0.0

        if not results:
            return 0.0

        if any(not result.status for result in results if not result.skipped):
            return 0.0
        return 100.0


class ScoreBinaryPass(ScoreStrategy):
    """Anything passes then the test is a pass. Empty results fail. """
    strategy_name = "by_binary_pass"

    def score(self, results: list[Ten8tResult] | None) -> float:
        if results is None:
            return 0.0

        if any(result.status for result in results if not result.skipped):
            return 100.0
        return 0.0
