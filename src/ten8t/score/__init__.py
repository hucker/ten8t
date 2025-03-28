# Import and register all built-in strategies
from ._base import (
    ScoreStrategy,
)
from ._factory import (get_registered_strategies, get_strategy_class, register_score_class,
                       reset_score_strategy_registry)
from ._util import (
    sanitize_results
)
from .concrete import (ScoreBinaryFail, ScoreBinaryPass, ScoreByFunctionBinary, ScoreByFunctionMean, ScoreByResult)

__all__ = [
    'ScoreStrategy',
    'register_score_class',
    'reset_score_strategy_registry',
    'get_registered_strategies',
    'sanitize_results',
    'ScoreByResult',
    'ScoreByFunctionBinary',
    'ScoreByFunctionMean',
    'ScoreBinaryFail',
    'ScoreBinaryPass'
]
