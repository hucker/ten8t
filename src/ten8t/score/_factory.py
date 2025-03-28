"""
Registry system for score strategies.
"""
from typing import Dict, List, Type

from ._protocol import ScoreStrategyProtocol

# Registry of score strategy classes
_registered_score_strategies: Dict[str, Type[ScoreStrategyProtocol]] = {}


def register_score_class(cls: Type[ScoreStrategyProtocol]) -> Type[ScoreStrategyProtocol]:
    """
    Register a score strategy class with its strategy_name.

    Can be used as a decorator:

    @register_score_class
    class MyScoreStrategy(ScoreStrategy):
        strategy_name = "my_strategy"
        ...

    Args:
        cls: The score strategy class to register

    Returns:
        The registered class (for decorator usage)

    Raises:
        ValueError: If strategy_name is not defined or already registered
    """
    if not hasattr(cls, 'strategy_name') or not cls.strategy_name:
        raise ValueError(f"Score strategy class {cls.__name__} must define strategy_name")

    if cls.strategy_name in _registered_score_strategies:
        raise ValueError(f"Score strategy name '{cls.strategy_name}' is already registered")

    _registered_score_strategies[cls.strategy_name] = cls
    return cls


def reset_score_strategy_registry() -> None:
    """
    Reset the score strategy registry.

    This is mainly used for testing purposes.
    """
    global _registered_score_strategies
    _registered_score_strategies = {}


def get_registered_strategies() -> List[str]:
    """
    Get a list of all registered strategy names.

    Returns:
        List of strategy names
    """
    return list(_registered_score_strategies.keys())


def get_strategy_class(strategy_name: str) -> Type[ScoreStrategyProtocol]:
    """
    Get a strategy class by name.

    Args:
        strategy_name: The name of the strategy to retrieve

    Returns:
        The strategy class

    Raises:
        ValueError: If the strategy name is not registered
    """
    if strategy_name not in _registered_score_strategies:
        raise ValueError(f"Unknown score strategy: {strategy_name}")

    return _registered_score_strategies[strategy_name]
