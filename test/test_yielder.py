import pytest

from src import ten8t as t8


def test_yielder_do_something():
    @t8.attributes(tag="tag", phase="phase", level=1, weight=100, skip=False)
    def func1():
        y = t8.Ten8tYield()
        for i in [1, 2, 3]:
            yield from y.results(t8.Ten8tResult(status=False, msg=f"Msg {i}"))
        if not y.yielded:
            yield from y.results(t8.Ten8tResult(status=True, msg="Nothing was to be done"))

    s_func = t8.Ten8tFunction(func1)

    ch = t8.Ten8tChecker(check_functions=[s_func], auto_setup=True)
    results = ch.run_all()

    assert len(results) == 3
    assert results[0].status is False
    assert results[0].msg == "Msg 1"
    assert results[1].status is False
    assert results[1].msg == "Msg 2"
    assert results[2].status is False
    assert results[2].msg == "Msg 3"


def test_result_yielder_counts():
    """
    This is tricky meta code.  The yield object is used to track how many passes
    and fails have been yielded because it is a common pattern to perform reporting
    based on all passes or all fails.  This test function runs through a simple
    scenario where it tests the counters in the yield object...and yields those
    results.

    """

    @t8.attributes(tag="tag", phase="phase", level=1, weight=100, skip=False)
    def func1():
        y = t8.Ten8tYield()
        yield from y.results(t8.Ten8tResult(status=False, msg="Here's a fail"))
        yield from y.results(t8.Ten8tResult(status=True, msg="Here's a pass"))
        yield from y.results(t8.Ten8tResult(y.fail_count == 1 and y.pass_count == 1 and y.count == 2,
                                            msg=f"Should be 1/1 counted {y.pass_count} pass and {y.fail_count} fail."))
        yield from y.results(t8.Ten8tResult(y.fail_count == 1 and y.pass_count == 2 and y.count == 3,
                                            msg=f"Should be 2/1 counted {y.pass_count} pass and {y.fail_count} fail."))
        yield from y.results(t8.Ten8tResult(status=False, msg="Here's another fail"))
        yield from y.results(t8.Ten8tResult(y.fail_count == 2 and y.pass_count == 3 and y.count == 5,
                                            msg=f"Should be 2/1 counted {y.pass_count} pass and {y.fail_count} fail."))
        p, f, t = y.counts
        yield from y.results(
            t8.Ten8tResult(status=all((f == 2, p == 4, t == 6)), msg=f"Counts check {p}==1 and {f}==1 and {t}==5"))

    s_func = t8.Ten8tFunction(func1)
    results = list(s_func())
    assert len(results) == 7
    assert results[0].status is False  # Hardcoded false
    assert results[1].status is True  # Hardcoded pass
    assert results[2].status is True  # verify counters
    assert results[3].status is True  # verify counters
    assert results[4].status is False  # verify y.counts
    assert results[5].status is True  # verify y.counts
    assert results[6].status is True  # verify y.counts


def test__call__yielder_counts():
    """
    This is tricky meta code again, only this test uses the __call__ method in
    the yielder class to clean up the syntax of yielding results

    """

    @t8.attributes(tag="tag", phase="phase", level=1, weight=100, skip=False)
    def func1():
        y = t8.Ten8tYield()
        yield from y(status=False, msg="Here's a fail")
        yield from y(status=True, msg="Here's a pass")
        yield from y(y.fail_count == 1 and y.pass_count == 1 and y.count == 2,
                     msg=f"Should be 1/1 counted {y.pass_count} pass and {y.fail_count} fail.")
        yield from y(y.fail_count == 1 and y.pass_count == 2 and y.count == 3,
                     msg=f"Should be 2/1 counted {y.pass_count} pass and {y.fail_count} fail.")
        yield from y(status=False, msg="Here's another fail")
        yield from y(y.fail_count == 2 and y.pass_count == 3 and y.count == 5,
                     msg=f"Should be 2/1 counted {y.pass_count} pass and {y.fail_count} fail.")
        p, f, t = y.counts
        yield from y(status=all((f == 2, p == 4, t == 6)), msg=f"Counts check {p}==1 and {f}==1 and {t}==5")

    s_func = t8.Ten8tFunction(func1)
    results = list(s_func())
    assert len(results) == 7
    assert results[0].status is False  # Hardcoded false
    assert results[1].status is True  # Hardcoded pass
    assert results[2].status is True  # verify counters
    assert results[3].status is True  # verify counters
    assert results[4].status is False  # verify y.counts
    assert results[5].status is True  # verify y.counts
    assert results[6].status is True  # verify y.counts


def test_yielder_do_nothing():
    """Verify that you can check if anything has happened"""

    def false():
        return False

    @t8.attributes(tag="tag", phase="phase", level=1, weight=100, skip=False)
    def func():
        y = t8.Ten8tYield()
        # This degenerate function does no checks so by definition it hasn't yielded
        if not y.yielded:
            yield from y.results(t8.Ten8tResult(status=True, msg="Nothing needed to be done."))

    s_func = t8.Ten8tFunction(func)

    ch = t8.Ten8tChecker(check_functions=[s_func], auto_setup=True)
    results = ch.run_all()

    assert len(results) == 1
    assert results[0].status is True
    assert results[0].msg == "Nothing needed to be done."


def test_yielder_exc():
    @t8.attributes(tag="tag", phase="phase", level=1, weight=100, skip=False)
    def should_pass_a_result_not_a_string():
        y = t8.Ten8tYield()
        yield from y.results("foo")

    s_func = t8.Ten8tFunction(should_pass_a_result_not_a_string)

    results = s_func()
    for result in results:
        assert result.status is False
        assert result.traceback


def test_yielder_result():
    @t8.attributes(tag="tag", phase="phase", level=1, weight=100, skip=False)
    def yield_a_result():
        y = t8.Ten8tYield()
        yield from y(t8.TR(status=True, msg="Yield result the 'normal' way."))

    s_func = t8.Ten8tFunction(yield_a_result)

    results = s_func()
    for result in results:
        assert result.status is True
        assert result.msg.startswith("Yield result the 'normal' way")


def test_yielder_result():
    @t8.attributes(tag="tag", phase="phase", level=1, weight=100, skip=False)
    def yield_a_result():
        y = t8.Ten8tYield()
        yield from y(t8.TR(status=True, msg="Yield result the 'normal' way."))

    s_func = t8.Ten8tFunction(yield_a_result)

    results = s_func()
    for result in results:
        assert result.status is True
        assert result.msg.startswith("Yield result the 'normal' way")


def test_yielder_summary():
    """
    This is tricky meta code again, only this test uses the __call__ method in
    the yielder class to clean up the syntax of yielding results
    
    Because the summary only flag is set, even though func1 has many tests that
    are verified and "yielded" this function only yields the summary result 
    rather than the 6 results.

    """

    @t8.attributes(tag="tag", phase="phase", level=1, weight=100, skip=False)
    def func1():
        y = t8.Ten8tYield(show_summary=True, show_fail=False, show_pass=False, summary_name="Func1 Summary")
        yield from y(status=False, msg="Here's a fail")
        yield from y(status=True, msg="Here's a pass")
        yield from y(y.fail_count == 1 and y.pass_count == 1 and y.count == 2,
                     msg=f"Should be 1/1 counted {y.pass_count} pass and {y.fail_count} fail.")
        yield from y(y.fail_count == 1 and y.pass_count == 2 and y.count == 3,
                     msg=f"Should be 2/1 counted {y.pass_count} pass and {y.fail_count} fail.")
        yield from y(status=False, msg="Here's another fail")
        yield from y(y.fail_count == 2 and y.pass_count == 3 and y.count == 5,
                     msg=f"Should be 2/1 counted {y.pass_count} pass and {y.fail_count} fail.")
        p, f, t = y.counts
        yield from y(status=all((f == 2, p == 4, t == 6)), msg=f"Counts check {p}==1 and {f}==1 and {t}==5")
        yield from y.yield_summary()

    s_func = t8.Ten8tFunction(func1)
    results = list(s_func())
    assert len(results) == 1
    assert results[0].status is False
    assert results[0].msg == "Func1 Summary had 5 pass and 2 fail."
    assert results[0].summary_result is True


@pytest.mark.parametrize(
    "config, expected_results",
    [
        # Test Case 1: show_pass=True, show_fail=False, show_summary=False
        (
                {"show_pass": True, "show_fail": False, "show_summary": False},
                {"pass_count": 2, "fail_count": 0, "summary_count": 0, "total_count": 2},
        ),
        # Test Case 2: show_pass=False, show_fail=True, show_summary=False
        (
                {"show_pass": False, "show_fail": True, "show_summary": False},
                {"pass_count": 0, "fail_count": 3, "summary_count": 0, "total_count": 3},
        ),
        # Test Case 3: show_pass=True, show_fail=True, show_summary=True
        (
                {"show_pass": True, "show_fail": True, "show_summary": True},
                {"pass_count": 2, "fail_count": 4, "summary_count": 1, "total_count": 6},
        ),
        # Test Case 4: show_pass=False, show_fail=True, show_summary=True
        (
                {"show_pass": False, "show_fail": True, "show_summary": True},
                {"pass_count": 0, "fail_count": 4, "summary_count": 1, "total_count": 4},
        ),

    ],
)
def test_ten8t_yield(config, expected_results):
    # Config is the paramters we pass to the Yield constructor
    # results are the pass/fail/total/summary counts for each configuration.

    # Common generator function with variable config
    def generated_yield():
        y = t8.Ten8tYield(**config)
        yield from y(status=False, msg="Here's a fail")  # Fail 1
        yield from y(status=False, msg="Here's a fail")  # Fail 2
        yield from y(status=False, msg="Here's a fail")  # Fail 3
        yield from y(status=True, msg="Here's a pass")  # Pass 1
        yield from y(status=True, msg="Here's a pass")  # Pass 2
        yield from y.yield_summary()  # Summary (if enabled)

    # Process results
    results = list(t8.Ten8tFunction(generated_yield)())

    # Assertions
    assert len(results) == expected_results["total_count"]
    assert len([r for r in results if r.status]) == expected_results["pass_count"]
    assert len([r for r in results if not r.status]) == expected_results["fail_count"]
    assert sum(r.summary_result for r in results) == expected_results["summary_count"]


def test_bad_yield_setup():
    @t8.attributes(tag="tag", phase="phase", level=1, weight=100, skip=False)
    def yield_a_result():
        # Should throw exception (don't need any more code after making yielder
        _ = t8.Ten8tYield(show_summary=False, show_fail=False, show_pass=False, summary_name="Func1 Summary")

    s_func = t8.Ten8tFunction(yield_a_result)
    ch = t8.Ten8tChecker(check_functions=[s_func], auto_setup=True)
    results = ch.run_all()
    assert results[0].status is False
    assert results[0].except_
    assert results[0].traceback
    assert "You must show a result or a summary" in results[0].msg
