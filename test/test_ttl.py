import pathlib
import time

import ten8t


def test_ttl_func(tmp_path):
    """
    Test the TTL functionality.

    This is a bit crude as it doesn't test all the edge cases, but it does verify
    that the mechanism of time is handled and that multiple yielded results are handled
    using the objects in the same way.  E.g. top level code has no clue about ttl and
    doesn't do anything to support it.

    The check goes like this

    1) Create a test function that has a ttl of 1 second.  That means that
       it saves its values and if the function is called before one second it
       returns the stored results.
    2) Verify that all tests pass from a function that returns multiple values
    3) Delete the file that we are checking
    4) Immediately check again, if there were no caching this would fail, but it
       passes again.
    5) Wait longer than the ttl and run the test again.
    6) This should now all fail, showing that the cached vales were not used.


    Args:
        tmp_path: place for us to create a file

    """

    f = pathlib.Path(tmp_path) / "__bad_file__.txt"
    f.touch(exist_ok=True)

    # This function checks if the file exists
    @ten8t.attributes(ttl_minutes='1s')
    def func():
        yield ten8t.TR(status=f.exists(), msg="Exist 1")
        yield ten8t.TR(status=f.exists(), msg="Exist 2")
        yield ten8t.TR(status=f.exists(), msg="Exist 3")

    ten8t_func = ten8t.Ten8tFunction(func, "")

    ch = ten8t.Ten8tChecker(check_functions=[ten8t_func], auto_setup=True)
    results = ch.run_all()

    # All 3 different messages and all pass
    assert len(results) == 3
    assert all(result.msg == f"Exist {i}" and result.status for i, result in enumerate(results, start=1))

    # now we delete the file
    f.unlink()

    # All 3 different messages and all pass even though the file DOES NOT EXIST
    # this means that we got the cached messages
    results = ch.run_all()
    assert len(results) == 3
    assert all(result.msg == f"Exist {i}" and result.status for i, result in enumerate(results, start=1))

    # Get pass the TTL
    time.sleep(1.01)

    # Now they should all fail
    results = ch.run_all()
    assert len(results) == 3
    assert all(result.msg == f"Exist {i}" and not result.status for i, result in enumerate(results, start=1))


# @pytest.mark.skip(reason="Found bug that needs to be fixed in ch.run_all()")
def test_ttl_func_boolean_return(tmp_path):
    """
    This is the same as the code above but using non generators.  This uses
    a different loop through the low level code.

    Args:
        tmp_path: place for us to create a file

    """

    f = pathlib.Path(tmp_path) / "__bad_file__.txt"
    f.touch(exist_ok=True)

    # This function checks if the file exists and uses RETURN NOT YIELD
    @ten8t.attributes(ttl_minutes='1s')
    def func():
        return f.exists()

    ten8t_func = ten8t.Ten8tFunction(func, "")

    ch = ten8t.Ten8tChecker(check_functions=[ten8t_func], auto_setup=True)
    results = ch.run_all()

    # All 3 different messages and all pass
    assert len(results) == 1
    assert all(result.status for i, result in enumerate(results, start=1))

    # now we delete the file
    f.unlink()

    # All pass even though the file DOES NOT EXIST
    # this means that we got the cached results
    results = ch.run_all()
    assert len(results) == 1
    assert all(result.status for i, result in enumerate(results, start=1))

    # Get pass the TTL
    time.sleep(1.01)

    # Now they should all fail
    results = ch.run_all()
    assert len(results) == 1
    assert all(not result.status for i, result in enumerate(results, start=1))
