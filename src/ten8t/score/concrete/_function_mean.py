from typing import Any

from .._base import ScoreStrategy
from ...ten8t_exception import Ten8tException
from ...ten8t_result import Ten8tResult


class ScoreByFunctionMean(ScoreStrategy):
    """Score strategy that computes an average score based on function results.

    This class implements a scoring strategy where the score is calculated as a
    weighted average of the results for each function. It processes a list of
    results, groups them by function, and calculates the score based on the
    weight and status of each entry.

    Attributes:
        strategy_name (str): Name of the scoring strategy used to identify the
            classification logic.
    """

    strategy_name = "by_function_mean"

    def score(self, results: list[Ten8tResult] | None = None) -> float:
        """Find the average of the results from each function."""

        if not results:
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
