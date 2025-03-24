# Import and register all built-in strategies
from .base import (
    ScoreStrategy,
)
from .concrete import (ScoreBinaryFail, ScoreBinaryPass, ScoreByFunctionBinary, ScoreByFunctionMean, ScoreByResult)
from .factory import (get_registered_strategies, get_strategy_class, register_score_class,
                      reset_score_strategy_registry)
from .util import (
    sanitize_results
)

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
