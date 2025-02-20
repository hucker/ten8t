import itertools
from time import sleep, time

import pytest

import src.ten8t as t8


@pytest.fixture
def func_nothread():
    """Fixture that provides thread functions func1 and func2."""

    @t8.attributes()
    def nothread():
        return t8.Ten8tResult(status=True, msg="It works.")

    return t8.Ten8tFunction(nothread)

@pytest.fixture
def func1():
    """Fixture that provides thread functions func1 and func2."""

    @t8.attributes(thread_id="thread1")
    def func1():
        return t8.Ten8tResult(status=True, msg="It works thread1")

    return t8.Ten8tFunction(func1)


@pytest.fixture
def func2():
    """Fixture that provides thread functions func1 and func2."""

    @t8.attributes(thread_id="thread2")
    def func2():
        return t8.Ten8tResult(status=True, msg="It works thread2")

    return t8.Ten8tFunction(func2)


@pytest.fixture
def func3():
    """Fixture that provides thread functions func1 and func2."""

    @t8.attributes(thread_id="thread3")
    def func3():
        return t8.Ten8tResult(status=True, msg="It works thread3")

    return t8.Ten8tFunction(func3)


@pytest.fixture
def one_sec_func():
    """Fixture that provides thread functions func1 and func2."""

    @t8.attributes(thread_id="thread1")
    def tfunc1():
        sleep(1)
        return t8.Ten8tResult(status=True, msg="It works thread1")

    return t8.Ten8tFunction(tfunc1)


@pytest.fixture
def two_sec_func():
    """Fixture that provides thread functions func1 and func2."""

    @t8.attributes(thread_id="thread2")
    def tfunc2():
        sleep(2)
        return t8.Ten8tResult(status=True, msg="It works thread2")

    return t8.Ten8tFunction(tfunc2)


def test_verify_no_threads():
    with pytest.raises(t8.Ten8tException) as e_info:
        ch = t8.Ten8tChecker(check_functions=[], auto_setup=True)
        tcheck = t8.Ten8tThread(ch)
        _ = tcheck.run_all()
    assert str(e_info.value) == "You must provide at least one package, module or function to check."


def test_repr(func1, func2, func3):
    # This test verifies that we just run through the code path that runs in a single
    # thread.  Here we just run the same function 3 times.

    # This guy should report 1 thread1 since func1 runs 3 times in the same thread
    ch = t8.Ten8tChecker(check_functions=[func1, func1, func1], auto_setup=True)
    tcheck = t8.Ten8tThread(ch)
    assert str(tcheck) == "<Ten8tThread(expected_threads=1, checker=Ten8tChecker)>"

    # This guy should report 3 threads since each func runs in a different thread
    ch = t8.Ten8tChecker(check_functions=[func1, func2, func3], auto_setup=True)
    tcheck = t8.Ten8tThread(ch)
    assert str(tcheck) == "<Ten8tThread(expected_threads=3, checker=Ten8tChecker)>"


def test_verify_single_thread(func1):
    # This test verifies that we just run through the code path that runs in a single
    # thread.  Here we just run the same function 3 times.
    ch = t8.Ten8tChecker(check_functions=[func1, func1, func1], auto_setup=True)
    tcheck = t8.Ten8tThread(ch)
    results = tcheck.run_all()

    assert len(results) == 3
    assert tcheck.expected_threads == 1
    # Even though we built this as func1,2,3 when each function runs in a thread the order the function complete
    # is random.  So here we verify that the thread id in the result matches the thread_id message.
    for i in range(3):
        assert results[i].status == True
        assert results[i].msg == f"It works thread1"
        assert results[i].thread_id == 'thread1'


def test_simple_threads(func1, func2, func3):
    ch = t8.Ten8tChecker(check_functions=[func1, func2, func3], auto_setup=True)
    tcheck = t8.Ten8tThread(ch)
    results = tcheck.run_all()

    assert len(results) == 3
    assert tcheck.expected_threads == 3
    # Even though we built this as func1,2,3 when each function runs in a thread the order the function complete
    # is random.  So here we verify that the thread id in the result matches the thread_id message.
    for i in range(3):
        thread = results[i].thread_id
        assert results[i].status == True
        assert results[i].msg == f"It works {thread}"


@pytest.mark.parametrize("funcs_permutation", list(itertools.permutations([1, 2, 3])))  # Indexes for fixture ordering
def test_sorted_threads(funcs_permutation, func1, func2, func3):
    # This is a bit of a hack to verify that the no matter the order that the functions are given
    # the results are spit out sorted by the thread_id.

    # Map the permutation indexes to actual fixtures
    funcs = [func1, func2, func3]
    selected_funcs = [funcs[i - 1] for i in list(funcs_permutation)]  # Permute based on the fixture list

    # Feature to verify sorting by thread_id
    ch = t8.Ten8tChecker(check_functions=selected_funcs, auto_setup=True)
    tcheck = t8.Ten8tThread(ch)
    results = tcheck.run_all()

    # Verify the results have 3 threads and are sorted by thread_id
    assert len(results) == 3
    assert tcheck.expected_threads == 3
    assert results[0].thread_id == "thread1"
    assert results[1].thread_id == "thread2"
    assert results[2].thread_id == "thread3"


def test_timed_threads(one_sec_func, two_sec_func):
    ch = t8.Ten8tChecker(check_functions=[one_sec_func, one_sec_func, two_sec_func, two_sec_func], auto_setup=True)
    tcheck = t8.Ten8tThread(ch)
    start_time = time()
    _ = tcheck.run_all()
    end_time = time()
    execution_time = end_time - start_time

    # The threaded code runs sequentially in each thread so the worst case time is 4 seconds for thread2
    assert execution_time < 4.1


def test_many_threads():
    """
    Verify that we can run many io bound functions in parallel by creating 100 test functions, each
    of which takes 1 second to run.  Using the normal test runner this test would take 100 seconds.
    However, this tests gives each function its own thread so they can all run "at the same time".

    This test should only take 1 second to run.


    :return:
    """

    def make_t8_function(thread_id: str, sleep_time: int):
        """
        Creates and returns a t8.Ten8tFunction with customizable thread_id and sleep time.

        Args:
            thread_id (str): The `thread_id` attribute for the function.
            sleep_time (int): The amount of time (in seconds) the function sleeps.

        Returns:
            t8.Ten8tFunction: The created Ten8t function.
        """

        @t8.attributes(thread_id=thread_id)
        def custom_thread_func():
            """Custom thread function with parameterized thread_id and sleep."""
            sleep(sleep_time)
            return t8.Ten8tResult(status=True, msg=f"It works on {thread_id}")

        return t8.Ten8tFunction(custom_thread_func)

    functions = [make_t8_function(f"thread{i:02d}", 1) for i in range(100)]
    ch = t8.Ten8tChecker(check_functions=functions, auto_setup=True)
    tcheck = t8.Ten8tThread(ch)
    start_time = time()
    _ = tcheck.run_all(max_workers=100)
    end_time = time()
    execution_time = end_time - start_time
    assert execution_time < 1.1


@pytest.mark.parametrize("max_workers", [
    100,  # 100 Workers
    50,  # 50 Workers
    25,  # 25 Workers
    10,  # 10 Workers
])
def test_thread_execution(max_workers):
    """
    This test verifies the operation of 100 threads running with varying max_workers.
    Expected execution time depends on max_workers and the number of tests. For example
    if you have 100 tests and 100 threads it should take 1 unit of time, but if
    you have 100 tests and 25 threads it should take 4 units of time.  This test
    is a sanity check that the threading behavior of t8 matches expectations.
    """

    def make_t8_function(thread_id: str, sleep_time: int):
        @t8.attributes(thread_id=thread_id)
        def custom_thread_func():
            """
            Custom thread function with parameterized thread_id and sleep.
            """
            sleep(sleep_time)
            return t8.Ten8tResult(status=True, msg=f"It works on {thread_id}")

        # Dynamically set the docstring to include thread_id and sleep_time
        custom_thread_func.__doc__ = (
            f"This thread function has the following parameters:\n"
            f"    - thread_id: {thread_id}\n"
            f"    - sleep time: {sleep_time} seconds"
        )

        return t8.Ten8tFunction(custom_thread_func)

    sleep_time = .2  # Sleep time for each test function
    num_tests = 100  # Total number of tests to run

    # You must understand this calculation.  Expected time scales with the number of tests
    # and is reduced by the number of workers. We add a small amount of time for the overhead
    # of actually running the code, on an M1 Mac this time usually is around .015sec, but sometimes
    # this number is much larger.  0.25 seconds seems to make this always work.
    overhead_seconds = 0.25
    ideal_time = (sleep_time * float(num_tests) / float(max_workers))
    expected_time = ideal_time + overhead_seconds

    # Create 100 thread functions (using a similar function generator or fixture as before)
    thread_functions = [make_t8_function(f"thread_{i:03}", sleep_time) for i in range(num_tests)]

    # Run all the thread functions using the specified max_workers
    ch = t8.Ten8tChecker(check_functions=thread_functions, auto_setup=True)
    tcheck = t8.Ten8tThread(ch)
    start_time = time()
    results = tcheck.run_all(max_workers=max_workers)
    end_time = time()
    execution_time = end_time - start_time

    # The runtime must land between the ideal time and the ideal + overhead
    assert execution_time <= expected_time, f"Execution was too slow: {execution_time}s"
    assert execution_time > ideal_time, f"There must be some overhead!!!"

    # Check some things that better be true
    assert all(result.status for result in results), "Not all threads completed successfully"

    # Make sure we got the full number of unique thread_ids
    assert len(set(result.thread_id for result in results)) == num_tests
