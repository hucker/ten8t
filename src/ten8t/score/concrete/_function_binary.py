from typing import Any

from .._base import ScoreStrategy
from ...ten8t_result import Ten8tResult


class ScoreByFunctionBinary(ScoreStrategy):
    """
    Represents a scoring strategy based on evaluating the binary success or failure of functions.

    This class implements a scoring strategy where each unique function is evaluated
    based on the results of its executions. If any result for a function fails, the
    function is considered failed. The overall score is computed as the average of the
    binary scores (pass/fail) of all functions analyzed.

    Attributes:
        strategy_name (str): The name of the scoring strategy.
    """

    strategy_name = "by_function_binary"

    def score(self, results: list[Ten8tResult] | None = None) -> float:
        if not results:
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
