""" The result of a ten8t run is a list of Ten8tResult objects.  These objects
    contain the results of the tests.  The results can be scored in a number of
    ways.  The simplest way is to score the results as a percentage of the total
    """

import pytest

from src import ten8t


@pytest.fixture
def by_func_weights_with_skip():
    # NOTE: This gives a case than handles most of the edge case
    return [
        ten8t.TR(status=False, msg="No RUID", func_name="func1", weight=100.0),
        ten8t.TR(status=False, msg="No RUID", func_name="func1", weight=100.0),
        ten8t.TR(status=True, msg="No RUID", func_name="func2", weight=200.0),
        ten8t.TR(status=True, msg="No RUID", func_name="func2", weight=200.0, skipped=True),
        ten8t.TR(status=False, msg="No RUID", func_name="func3", weight=300.0),
        ten8t.TR(status=True, msg="No RUID", func_name="func3", weight=300.0),
    ]


@pytest.fixture
def half_pass():
    # NOTE: This gives a case than handles most of the edge case
    return [
        ten8t.TR(status=True, msg="No RUID", func_name="func3", weight=300.0),
        ten8t.TR(status=False, msg="No RUID", func_name="func3", weight=300.0),
        ten8t.TR(status=False, msg="No RUID", func_name="func3", weight=300.0, skipped=True),
    ]


@pytest.fixture
def all_pass():
    # NOTE: This gives a case than handles most of the edge case
    return [
        ten8t.TR(status=True, msg="No RUID", func_name="func3", weight=300.0),
        ten8t.TR(status=True, msg="No RUID", func_name="func3", weight=300.0),
        ten8t.TR(status=False, msg="No RUID", func_name="func3", weight=300.0, skipped=True),
    ]


@pytest.fixture
def all_fail():
    # NOTE: This gives a case than handles most of the edge case
    return [
        ten8t.TR(status=False, msg="No RUID", func_name="func3", weight=300.0),
        ten8t.TR(status=False, msg="No RUID", func_name="func3", weight=300.0),
        ten8t.TR(status=True, msg="No RUID", func_name="func3", weight=300.0, skipped=True),
    ]


def test_score_by_result(by_func_weights_with_skip):
    # Set up the 3 strategies
    by_result = ten8t.ScoreByResult()

    # By result, it is easy to just add with code
    total_weight = 2 * 100 + 1 * 200 + 2 * 300
    total_pass = 1 * 200 + 1 * 300
    score = 100.0 * (total_pass * 1.0 / total_weight * 1.0)
    assert by_result.score(by_func_weights_with_skip) == pytest.approx(score)
    assert by_result(by_func_weights_with_skip) == pytest.approx(score)
    assert by_result([]) == 0.0


def test_score_by_function_binary(by_func_weights_with_skip):
    by_function_binary = ten8t.ScoreByFunctionBinary()
    # for the binary function case I'll do it by hand.  There are 3 functions with 3 different weights
    total_weight = 100 + 200 + 300  # weights for 3 functions
    total_pass = 0 * 100 + 1 * 200 + 0 * 300

    score = 100.0 * (total_pass / total_weight)

    assert by_function_binary.score(by_func_weights_with_skip) == pytest.approx(score)
    assert by_function_binary(by_func_weights_with_skip) == pytest.approx(score)
    assert by_function_binary.score([]) == 0.0


def test_score_by_function_mean(by_func_weights_with_skip):
    by_function_mean = ten8t.ScoreByFunctionMean()

    # for the mean function case I'll do it by hand.  There are 3 functions with 3 different weights
    total_weight = (2 * 100) + (1 * 200) + (2 * 300)  # weights for 3 functions
    total_pass = (0 / 2 * 100) + (1 * 200) + (1 * 300)
    score = 100.0 * (total_pass * 1.0 / total_weight * 1.0)
    assert by_function_mean.score(by_func_weights_with_skip) == pytest.approx(score)
    assert by_function_mean(by_func_weights_with_skip) == pytest.approx(score)
    assert by_function_mean([]) == 0.0


def test_score_binary_pass(all_pass, all_fail, half_pass):
    """Check that the full binary pass works"""
    by_binary_pass = ten8t.ScoreBinaryPass()
    assert by_binary_pass(all_pass) == 100.0
    assert by_binary_pass(all_fail) == 0.0
    assert by_binary_pass(half_pass) == 100
    assert by_binary_pass([]) == 0


def test_score_binary_fail(all_pass, all_fail, half_pass):
    """Check that the full binary fail works"""
    by_binary_fail = ten8t.ScoreBinaryFail()
    assert by_binary_fail(all_pass) == 100.0
    assert by_binary_fail(all_fail) == 0.0
    assert by_binary_fail(half_pass) == 0.0
    assert by_binary_fail([]) == 0


@pytest.mark.parametrize("strategy_name, strategy_class", [
    ("by_function_mean", ten8t.ScoreByFunctionMean),
    ("by_function_binary", ten8t.ScoreByFunctionBinary),
    ("by_result", ten8t.ScoreByResult),
    ("by_binary_pass", ten8t.ScoreBinaryPass),
    ("by_binary_fail", ten8t.ScoreBinaryFail),
    ("ScoreByFunctionMean", ten8t.ScoreByFunctionMean),
    ("ScoreByFunctionBinary", ten8t.ScoreByFunctionBinary),
    ("ScoreByResult", ten8t.ScoreByResult),
    ("ScoreBinaryPass", ten8t.ScoreBinaryPass),
    ("ScoreBinaryFail", ten8t.ScoreBinaryFail),
])
def test_strategy_factory(strategy_name, strategy_class):
    """Test the strategy factory in  both methods."""
    assert isinstance(ten8t.ScoreStrategy.strategy_factory(strategy_name), strategy_class)


def test_bad_strategy_name():
    """Exception on invalid strategy name."""
    with pytest.raises(ten8t.Ten8tException):
        ten8t.ScoreStrategy.strategy_factory("bad_strategy_name")


def test_bad_strategy_class():
    """Exception from non-derived class"""
    with pytest.raises(ten8t.Ten8tException):
        ten8t.ScoreStrategy.strategy_factory(dict)


@pytest.mark.parametrize("scoring_function", [
    ten8t.ScoreBinaryFail,
    ten8t.ScoreBinaryPass,
    ten8t.ScoreByResult,
    ten8t.ScoreByFunctionMean,
    ten8t.ScoreByFunctionBinary,
])
def test_null_results(scoring_function):
    score = scoring_function()
    assert score([]) == 0.0
