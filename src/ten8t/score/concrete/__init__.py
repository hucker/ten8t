"""
Built-in scoring strategies.
"""
from ._binary_fail import ScoreBinaryFail
from ._binary_pass import ScoreBinaryPass
from ._by_result import ScoreByResult
from ._function_binary import ScoreByFunctionBinary
from ._function_mean import ScoreByFunctionMean

__all__ = [
    'ScoreByResult',
    'ScoreByFunctionBinary',
    'ScoreByFunctionMean',
    'ScoreBinaryFail',
    'ScoreBinaryPass'
]
