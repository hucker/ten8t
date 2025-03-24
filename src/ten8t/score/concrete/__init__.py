"""
Built-in scoring strategies.
"""
from .binary_fail import ScoreBinaryFail
from .binary_pass import ScoreBinaryPass
from .by_result import ScoreByResult
from .function_binary import ScoreByFunctionBinary
from .function_mean import ScoreByFunctionMean

__all__ = [
    'ScoreByResult',
    'ScoreByFunctionBinary',
    'ScoreByFunctionMean',
    'ScoreBinaryFail',
    'ScoreBinaryPass'
]
