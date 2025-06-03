import pytest

import ten8t.ten8t_attribute as ten8t_attribute
import ten8t.ten8t_exception as ten8t_exception
import ten8t.ten8t_function as ten8t_function
import ten8t.ten8t_result as ten8t_result
from ten8t import Ten8tException


@pytest.mark.parametrize("ttl,units,result", [
    ("0", ["m", "minute", "min"], 0),
    ("0", ["s", "sec", "second", "seconds"], 0),
    ("0", ["h", "hr", "hour"], 0),
    ("1", [""], 1.0),
    ("10.5", [""], 10.5),
    ("0.25", [""], 0.25),
    ("0.5", ["h", "hr", "hour"], 30),

    ("1", ["h", "hr", "hour", "hours"], 60),
    ("2", ["h", "hr", "hour"], 120),
    ("30", ["s", "sec", "second"], .5),
    ("60", ["s", "sec", "second"], 1),
    ("630", ["s", "sec", "second"], 10.5),
    ("1", ["m", "minute", "min"], 1),
    (".5", ["m", "minute", "min"], 0.5),
    ("10", ["m", "minute", "min"], 10),
    ("101.5", ["m", "minute", "min", "minutes"], 101.5)
])
def test_attr_ttl(ttl, units, result):
    """ Test all the units and the separators  """
    seps = ['', ' ', '\t', '   ']
    for unit in units:
        for sep in seps:
            assert ten8t_attribute._parse_ttl_string(f'{ttl}{sep}{unit}') == result


@pytest.mark.parametrize("invalid_char", list('!@#$%^&*(){}[]<>~`-+=\t\n\'"'))
def test_tag_attr_exc(invalid_char):
    with pytest.raises(ten8t_exception.Ten8tException):
        ten8t_attribute.attributes(tag=f'test{invalid_char}')


@pytest.mark.parametrize("invalid_char", list('!@#$%^&*(){}[]<>~`-+=\t\n\'"'))
def test_tag_categories_exc(invalid_char):
    with pytest.raises(ten8t_exception.Ten8tException):
        ten8t_attribute.categories(tag=f'test{invalid_char}')

@pytest.mark.parametrize("invalid_char", list('!@#$%^&*(){}[]<>~`-+=\t\n\'"'))
def test_ruid_attr_exc(invalid_char):
    with pytest.raises(ten8t_exception.Ten8tException):
        ten8t_attribute.attributes(ruid=f'test{invalid_char}')


@pytest.mark.parametrize("invalid_char", list('!@#$%^&*(){}[]<>~`-+=\t\n\'"'))
def test_phase_attr_exc(invalid_char):
    with pytest.raises(ten8t_exception.Ten8tException):
        ten8t_attribute.attributes(phase=f'test{invalid_char}')


@pytest.mark.parametrize("unit_group,bad_time", [
    (["m", "minute", "min", "minutes"], "-0.1"),
    (["m", "minute", "min", "minutes"], "-1"),
    (["m", "minute", "min", "minutes"], "-1.0"),
    (["m", "minute", "min", "minutes"], "-1."),
    (["s", "sec", "second", "seconds"], "-0.1"),
    (["s", "sec", "second", "seconds"], "-1"),
    (["s", "sec", "second", "seconds"], "-1.0"),
    (["s", "sec", "second", "seconds"], "-1."),
    (["h", "hr", "hour", "hrs"], "-0.1"),
    (["h", "hr", "hour", "hrs"], "-1"),
    (["h", "hr", "hour", "hrs"], "-1.0"),
    (["h", "hr", "hour", "hrs"], "-1."),
    ([""], "-0.1"),
    ([""], "-1"),
    ([""], "-1.0"),
    ([""], "-1.")
])
def test_ttl_fail(unit_group, bad_time):
    seps = ['', ' ', '\t', '   ']
    for unit in unit_group:
        for sep in seps:
            with pytest.raises(ten8t_exception.Ten8tException):
                s = f"{bad_time}{sep}{unit}"
                ten8t_attribute._parse_ttl_string(s)


def test_skip_attribute_when_true():
    @ten8t_attribute.attributes(skip=True)
    def check_skip():
        # This will never get called because the skip happens before the call
        return ten8t_result.Ten8tResult(status=True, msg="It works")  # pragma no cover

    result = next(ten8t_function.Ten8tFunction(check_skip)())
    assert result.skipped is True


def test_skip_attribute_when_not_specified():
    @ten8t_attribute.attributes()
    def check_skip():
        return ten8t_result.Ten8tResult(status=True, msg="It works")

    result = next(ten8t_function.Ten8tFunction(check_skip)())
    assert result.skipped is False


def test_skip_attribute_when_false():
    @ten8t_attribute.attributes(skip=False)
    def check_no_skip():
        return ten8t_result.Ten8tResult(status=True, msg="It works")

    result = next(ten8t_function.Ten8tFunction(check_no_skip)())
    assert result.skipped is False


def test_catagory_decorator():
    @ten8t_attribute.categories(tag="tag", phase="phase", ruid="ruid")
    def check_skip():
        # This will never get called because the skip happens before the call
        return ten8t_result.Ten8tResult(status=True, msg="It works")  # pragma no cover

    function = ten8t_function.Ten8tFunction(check_skip)
    assert function.tag == 'tag'
    assert function.phase == 'phase'
    assert function.ruid == 'ruid'


def test_categories_with_disallowed_chars():
    # Test allowing special characters by overriding disallowed_chars
    @ten8t_attribute.categories(tag="tag!special", phase="phase-with-dash", ruid="ruid@example.com",
                                disallowed_chars="")
    def check_special_chars():
        return ten8t_result.Ten8tResult(status=True, msg="It works")

    function = ten8t_function.Ten8tFunction(check_special_chars)
    assert function.tag == 'tag!special'
    assert function.phase == 'phase-with-dash'
    assert function.ruid == 'ruid@example.com'


def test_control_decorator():
    @ten8t_attribute.control(skip_on_none=True, fail_on_none=True, finish_on_fail=True, skip=True)
    def check_control():
        return ten8t_result.Ten8tResult(status=True, msg="It works")

    function = ten8t_function.Ten8tFunction(check_control)
    assert function.skip_on_none == True
    assert function.fail_on_none == True
    assert function.finish_on_fail == True
    assert function.skip == True


def test_bad_threading_decorator():
    with pytest.raises(Ten8tException):
        @ten8t_attribute.threading(thread_id="worker-1")
        def check_threading():
            return ten8t_result.Ten8tResult(status=True, msg="It works")

        _ = ten8t_function.Ten8tFunction(check_threading)


def test_caching_decorator_with_string():
    @ten8t_attribute.caching(ttl_minutes="30 minutes")
    def check_caching_string():
        return ten8t_result.Ten8tResult(status=True, msg="It works")

    function = ten8t_function.Ten8tFunction(check_caching_string)
    assert function.schedule.name == "debounce_schedule"
    assert function.schedule.ttl_sec == 1800


def test_caching_decorator_with_number():
    @ten8t_attribute.caching(ttl_minutes=45)
    def check_caching_number():
        return ten8t_result.Ten8tResult(status=True, msg="It works")

    function = ten8t_function.Ten8tFunction(check_caching_number)
    assert function.schedule.ttl_sec == 45 * 60


def test_score_decorator():
    @ten8t_attribute.score(weight=200.5)
    def check_score():
        return ten8t_result.Ten8tResult(status=True, msg="It works")

    function = ten8t_function.Ten8tFunction(check_score)
    assert function.weight == 200.5


def test_attributes_comprehensive_decorator():
    @ten8t_attribute.attributes(
        tag="comprehensive",
        phase="testing",
        level=3,
        weight=150.0,
        skip=True,
        ruid="unique_id",
        ttl_minutes="1 hour",
        finish_on_fail=True,
        skip_on_none=True,
        fail_on_none=False,
        thread_id="main"
    )
    def check_comprehensive():
        return ten8t_result.Ten8tResult(status=True, msg="It works")

    function = ten8t_function.Ten8tFunction(check_comprehensive)

    # Check all attributes are set correctly
    assert function.tag == "comprehensive"
    assert function.phase == "testing"
    assert function.level == 3
    assert function.weight == 150.0
    assert function.skip == True
    assert function.ruid == "unique_id"
    assert function.schedule.ttl_sec == 3600
    assert function.finish_on_fail == True
    assert function.skip_on_none == True
    assert function.fail_on_none == False
    assert function.thread_id == "main"


# @pytest.mark.xfail(reason="Disallowed character overrides are not work completely yet.")
def test_attributes_with_custom_disallowed():
    @ten8t_attribute.attributes(
        tag="test-tag",  # Contains a dash which would normally be disallowed
        phase="test",
        disallowed_chars=" "  # Only spaces are disallowed
    )
    def check_custom_disallowed():
        return ten8t_result.Ten8tResult(status=True, msg="It works")

    function = ten8t_function.Ten8tFunction(check_custom_disallowed)
    assert function.tag == "test-tag"
    assert function.phase == "test"


def test_multiple_decorators_different_orderings():
    # Test order 1: categories → control → score
    @ten8t_attribute.categories(tag="multi1", phase="test1")
    @ten8t_attribute.control(skip=True)
    @ten8t_attribute.score(weight=75.5)
    def check_order1():
        return ten8t_result.Ten8tResult(status=True, msg="It works")

    function1 = ten8t_function.Ten8tFunction(check_order1)
    assert function1.tag == "multi1"
    assert function1.phase == "test1"
    assert function1.skip == True
    assert function1.weight == 75.5

    # Test order 2: score → control → categories
    @ten8t_attribute.score(weight=85.5)
    @ten8t_attribute.control(skip=False)
    @ten8t_attribute.categories(tag="multi2", phase="test2")
    def check_order2():
        return ten8t_result.Ten8tResult(status=True, msg="It works")

    function2 = ten8t_function.Ten8tFunction(check_order2)
    assert function2.tag == "multi2"
    assert function2.phase == "test2"
    assert function2.skip == False
    assert function2.weight == 85.5

    # Test order 3: control → score → categories
    @ten8t_attribute.control(finish_on_fail=True)
    @ten8t_attribute.score(weight=95.5)
    @ten8t_attribute.categories(tag="multi3", phase="test3", level=5)
    def check_order3():
        return ten8t_result.Ten8tResult(status=True, msg="It works")

    function3 = ten8t_function.Ten8tFunction(check_order3)
    assert function3.tag == "multi3"
    assert function3.phase == "test3"
    assert function3.level == 5
    assert function3.finish_on_fail == True
    assert function3.weight == 95.5

    # Test with threading and caching decorators included
    @ten8t_attribute.threading(thread_id="worker-1", disallowed_chars=' ')
    @ten8t_attribute.caching(ttl_minutes=15)
    @ten8t_attribute.control(skip=True)
    @ten8t_attribute.categories(tag="multi4", phase="test4")
    def check_order4():
        return ten8t_result.Ten8tResult(status=True, msg="It works")

    function4 = ten8t_function.Ten8tFunction(check_order4)
    assert function4.tag == "multi4"
    assert function4.phase == "test4"
    assert function4.thread_id == "worker-1"
    assert function4.schedule.ttl_sec == 15 * 60
    assert function4.skip == True

    # Test if decorators override each other's values correctly
    @ten8t_attribute.categories(tag="first_tag", phase="first_phase")
    @ten8t_attribute.categories(tag="second_tag", phase="second_phase")
    def check_override():
        return ten8t_result.Ten8tResult(status=True, msg="It works")

    function5 = ten8t_function.Ten8tFunction(check_override)
    assert function5.tag == "first_tag"  # Most recent wins
    assert function5.phase == "first_phase"


def test_retry_no_retry():
    """attempt attribute is set but doesn't need since it always works"""

    @ten8t_attribute.attempts(max_attempts=4)
    def retry_func():
        yield ten8t_result.Ten8tResult(
            status=True,
            msg=f"Always pass"
        )

    results = list(ten8t_function.Ten8tFunction(retry_func)())
    assert len(results) == 1
    assert results[0].status is True
    assert results[0].attempts == 1
    assert results[0].msg == "Always pass"


@pytest.mark.parametrize("max_attempts", range(2, 11))
def test_retry_with_max_attempts(max_attempts):
    """
    Setup parameterization so we can test a bunch of attempts.  Overkill yes, but I want to
    see this work correctly for reasonable-ish numbers of attempts
    """

    @ten8t_attribute.attempts(max_attempts=max_attempts,
                              delay=0.05)  # Decorate the function with the current max_attempts
    def retry_func():
        yield ten8t_result.Ten8tResult(
            status=False,
            msg="Always fail"
        )

    results = list(ten8t_function.Ten8tFunction(retry_func)())

    # Assertions to verify behavior
    assert len(results) == 1  # Only one result should be returned (after all attempts)
    assert results[0].status is False  # The status should always be False (since it always fails)
    assert results[0].attempts == max_attempts  # The final result should have .attempt equal to max_attempts
    assert results[0].msg == "Always fail"  # The message should remain the same


@pytest.mark.parametrize(
    "pass_attempt, expected_status",
    [
        (1, True),  # Passes on the 1st attempt
        (2, True),  # Passes on the 2nd attempt
        (3, True),  # Passes on the 3rd attempt
        (4, False),  # Fails as pass_attempt exceeds max attempts
    ],
)
def test_attempts_with_state(pass_attempt, expected_status):
    """
    Verify behavior when retry logic is applied. The function succeeds on the specified
    pass_attempt. If pass_attempt exceeds max_attempts, it fails.
    """

    # Retry function that succeeds on the pass_attempt and tracks attempts
    @ten8t_attribute.attempts(max_attempts=3, delay=0)
    def retry_func():
        retry_func.count += 1  # Increment the state
        yield ten8t_result.Ten8tResult(
            status=retry_func.count == pass_attempt,  # Passes if attempt matches pass_attempt
            msg="Attempting..."
        )

    retry_func.count = 0  # Initialize attempt counter

    # Execute the function and collect results
    results = list(ten8t_function.Ten8tFunction(retry_func)())

    # Assertions to verify result consistency
    assert len(results) == 1  # Only one final result returned
    assert results[0].status == expected_status  # Matches expected status
    assert results[0].attempts == min(pass_attempt, 3)  # Reflects the actual number of attempts
