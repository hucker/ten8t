"""
Score strategy that uses the results' scores directly.
"""

from .._base import ScoreStrategy
from ...ten8t_result import Ten8tResult


class ScoreByResult(ScoreStrategy):
    """Calculate the score by individually weighting each result"""

    strategy_name = "by_result"

    def score(self, results: list[Ten8tResult] | None = None) -> float:
        """
        Calculates the overall score based on the provided list of test results. The score is
        calculated as the weighted percentage of tests that passed, excluding any skipped results.
        If no results are provided or all results are skipped, returns a default score of 0.0.

        The weight of each result contributes to the calculation: for passed results, their
        weight values are summed up. Compute the final score as the percentage of passed
        weighted sum over the total weighted sum of all considered results.

        Args:
            results (list[Ten8tResult] | None): A list of Ten8tResult objects containing the
                test results to score. Each result includes attributes like `weight` (the
                weight of the test) and `status` (whether the test passed or failed). Skipped
                results are excluded from consideration. If None or empty, no score is calculated.

        Returns:
            float: The calculated score as a percentage. If no results are present (including
                cases where all results are skipped), returns 0.0.
        """

        if not results:
            return 0.0

        weight_sum = 0.0
        passed_sum = 0.0

        for result in [r for r in results if not r.skipped]:
            passed_sum += result.weight if result.status else 0.0
            weight_sum += result.weight

        if weight_sum == 0.0:
            return 0.0

        final_score = (100.0 * passed_sum) / (weight_sum * 1.0)
        return final_score
