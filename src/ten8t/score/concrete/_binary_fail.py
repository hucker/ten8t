from .._base import ScoreStrategy
from ...ten8t_result import Ten8tResult


class ScoreBinaryFail(ScoreStrategy):
    """Score strategy that assesses a binary success or failure.

    This class provides a scoring mechanism based on whether any of the results
    in the provided list indicate failure, provided they are not marked as
    skipped. The class is designed for scenarios where a binary pass/fail
    evaluation is required for a set of results.  Logically speaking
    this is an AND operation.

    Attributes:
        strategy_name (str): A unique identifier for this scoring strategy.
    """

    strategy_name = "by_binary_fail"

    def score(self, results: list[Ten8tResult] | None) -> float:

        if not results:
            return 0.0

        if any(not result.status for result in results if not result.skipped):
            return 0.0
        return 100.0
