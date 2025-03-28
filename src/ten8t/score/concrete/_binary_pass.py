from .._base import ScoreStrategy
from ...ten8t_result import Ten8tResult


class ScoreBinaryPass(ScoreStrategy):
    """
    Represents a scoring strategy based on binary pass/fail criteria.

    This class implements a scoring strategy to evaluate a list of results. It checks
    if any result in the list has a status that indicates success (if the
    result is not marked as skipped). Based on this evaluation, it returns a score of
    either 0.0 or 100.0. This scoring strategy specifically applies to binary scenarios
    where only pass or fail outcomes are relevant.  This is an OR operation on the results.

    Attributes:
        strategy_name (str): Name of the strategy, used to identify this scoring
            approach.
    """
    strategy_name = "by_binary_pass"

    def score(self, results: list[Ten8tResult] | None) -> float:
        if not results:
            return 0.0

        if any(result.status for result in results if not result.skipped):
            return 100.0
        return 0.0
