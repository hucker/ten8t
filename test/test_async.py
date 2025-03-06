from itertools import product

import pytest

import ten8t.ten8t_checker as ten8t_checker
import ten8t.ten8t_result as ten8t_result


@pytest.fixture
def check_func():
    def check_func():
        yield ten8t_result.TR(status=True, msg="It works")

    return check_func


@pytest.fixture
def async_check_func():
    async def check_func():
        yield ten8t_result.TR(status=True, msg="It works")

    return check_func


@pytest.fixture
def coroutine_check_func():
    async def check_func():
        return ten8t_result.TR(status=True, msg="It works")

    return check_func


## This is not as bad as it looks.  I really want to test many different ways
## that check_functions could be brought in

# Helper function to generate all permutations for counts that sum to a target
def generate_permutations_for_count(target):
    return [
        p for p in product(range(target + 1), repeat=3)
        if sum(p) == target
    ]


# Generate all permutations for 1, 2, and 3
one_combinations = generate_permutations_for_count(1)  # Sums to 1
two_combinations = generate_permutations_for_count(2)  # Sums to 2
three_combinations = generate_permutations_for_count(3)  # Sums to 3

# Combine all cases
all_params = one_combinations + two_combinations + three_combinations


@pytest.mark.parametrize(
    "normal_count, coroutine_count, async_count",
    all_params
)
def test_function_collection(normal_count, coroutine_count, async_count, check_func, coroutine_check_func,
                             async_check_func):
    """
    Verify that any combination of check functions of different types gets collected properly.

    The basic idea is that the fixture provides count for the number of function types for the
    test say 3, 2 1.  The idea is that 0, 1, and 2 are all sort of different in that it checks
    none, single, more than 1 function.  This is probably massive overkill!
    """

    # Create lists of the appropriate functions
    normal_funcs = [check_func] * normal_count
    coroutine_funcs = [coroutine_check_func] * coroutine_count
    async_funcs = [async_check_func] * async_count

    # Combine all functions
    all_funcs = normal_funcs + coroutine_funcs + async_funcs

    # Initialize the Checker with these functions
    ch = ten8t_checker.Ten8tChecker(check_functions=all_funcs, auto_setup=True)

    # Assertions
    assert ch.async_count == async_count
    assert ch.coroutine_count == coroutine_count
    assert ch.collected_count == normal_count
    assert ch.async_count + ch.coroutine_count + ch.collected_count == len(ch.pre_collected)
