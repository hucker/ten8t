"""Basic scoring algorithms for Ten8t test results. """

import abc
from functools import wraps
from typing import Any

from .ten8t_exception import Ten8tException
from .ten8t_result import Ten8tResult
from .ten8t_util import StrOrNone

# Module-level dictionary to store registrations
_registered_score_strategies: dict[str, type["ScoreStrategy"]] = {}


def register_score_class(cls: type["ScoreStrategy"]):
    """Decorator to register a ScoreStrategy subclass in the module registry."""

    # if not issubclass(cls, ScoreStrategy):
    #    raise TypeError(f"Class {cls} must inherit from ScoreStrategy to be registered.")

    # Use the class name or `strategy_name`, if provided
    for strat_name in [cls.strategy_name, cls.__name__]:
        # if strat_name in _registered_score_strategies:
        #    raise ValueError(f"A strategy with the name '{strat_name}' is already registered.")

        _registered_score_strategies[strat_name] = cls
    return cls


def reset_score_strategy_registry():
    """Resets the module-level registry of scoring strategies."""
    global _registered_score_strategies
    _registered_score_strategies = {}


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
    def score(self, results: list["Ten8tResult"]) -> float:  # pragma: no cover
        """Abstract score method"""

    def __call__(self, results: list["Ten8tResult"]):
        """
        Make "calling" the object the same as calling the `score` method.

        Args:
            results (list[Ten8tResult]): A list of Ten8tResult objects that need to be
                processed.

        Returns:
            Any: The computed score based on the `results` passed as input.
        """
        return self.score(results)

    @classmethod
    def strategy_factory(cls, strategy_name: str) -> "ScoreStrategy":
        """
        Provides a method to instantiate a scoring strategy class based on the given name.
        The method uses a global registry of registered scoring strategy classes. It looks
        up the provided strategy name in the registry and returns an instance of the corresponding
        class if found. An exception is raised in cases where the strategy name is invalid or
        a matching class is not registered.

        Args:
            strategy_name (str): The name of the scoring strategy to instantiate.

        Returns:
            ScoreStrategy: An instance of the scoring strategy associated with the given name.

        Raises:
            Ten8tException: If `strategy_name` is not a string.
            Ten8tException: If no scoring strategy is registered with the provided name.
        """
        if not isinstance(strategy_name, str):
            raise Ten8tException(f"strategy name must be a string, not {type(strategy_name)}.")
        try:
            # Look up the class by name in the global registry and instantiate it
            return _registered_score_strategies[strategy_name]()
        except KeyError:
            raise Ten8tException(f"No scoring strategy registered with name '{strategy_name}'.")


@register_score_class
class ScoreByResult(ScoreStrategy):
    """Calculate the score by individually weighting each result"""

    strategy_name = "by_result"

    @sanitize_results
    def score(self, results: list[Ten8tResult] | None = None) -> float:
        """
        Calculates the overall score based on the provided list of test results. The score is
        calculated as the weighted percentage of tests that passed, excluding any skipped results.
        If no results are provided or all results are skipped, returns a default score of 0.0.

        The weight of each result contributes to the calculation: for passed results, their
        weight values are summed up. The final score is computed as the percentage of passed
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

        weight_sum = 0.0
        passed_sum = 0.0

        for result in results:
            passed_sum += result.weight if result.status else 0.0
            weight_sum += result.weight

        return (100.0 * passed_sum) / (weight_sum * 1.0)


@register_score_class
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

    @sanitize_results
    def score(self, results: list[Ten8tResult] | None = None) -> float:

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


@register_score_class
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

    @sanitize_results
    def score(self, results: list[Ten8tResult] | None = None) -> float:
        """Find the average of the results from each function."""


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


@register_score_class
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

    @sanitize_results
    def score(self, results: list[Ten8tResult] | None) -> float:

        if any(not result.status for result in results if not result.skipped):
            return 0.0
        return 100.0


@register_score_class
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

    @sanitize_results
    def score(self, results: list[Ten8tResult] | None) -> float:

        if any(result.status for result in results if not result.skipped):
            return 100.0
        return 0.0
