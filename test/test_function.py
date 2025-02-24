import time

import pytest

import ten8t as t8


@pytest.fixture(scope="module")
def check_func():
    def func(value):
        return value == 1

    return t8.Ten8tFunction(func)


def test__str__(check_func):
    str_value = str(check_func)
    assert check_func.function_name == 'func'
    assert str_value == "Ten8tFunction(self.function_name='func')"


@pytest.mark.parametrize("weight", [True, False, None])
def test_weight_none(weight):
    # Note this will fail if you say Ten8tException since weights
    with pytest.raises(t8.Ten8tException):
        @t8.attributes(weight=weight)
        def func():
            yield t8.TR(status=True, msg="Hello")


def test_weight_exception():
    @t8.attributes(tag="tag")
    def func():
        yield t8.TR(status=True, msg="Hello")

    func.weight = 0
    # Note this will fail if you say Ten8tException
    with pytest.raises(t8.Ten8tException):
        t8.Ten8tFunction(func)


def test_function_str():
    @t8.attributes(tag="tag")
    def func():
        yield t8.TR(status=True, msg="Hello")

    ten8t_func = t8.Ten8tFunction(func)
    assert ten8t_func.function_name == "func"


def test_func_doc_string_extract():
    @t8.attributes(tag="tag")
    def func():
        """This is a test function

        Mitigation:
        - Do something

        Owner:
        chuck@foobar.com

        Info:
        This is a
        long info string
        that needs

        help

        """
        return True

    s_func = t8.Ten8tFunction(func)
    for result in s_func():
        assert result.func_name == "func"
        assert result.status is True

        # NOTE: The inspect module, when used to get doc strings, will strip the leading
        #       white space from the doc string.  This is why the doc string is not
        #       indented and why you should use INSPECT.getdoc() to get the doc string.

        assert s_func._get_section("Mitigation") == "- Do something"
        assert s_func._get_section("Owner") == "chuck@foobar.com"
        assert s_func._get_section("DoesntExist") == ""

        assert (
                s_func._get_section("Info")
                == "This is a\nlong info string\nthat needs\n\nhelp"
        )
        assert s_func._get_section() == "This is a test function"


def test_function_bad_weight():
    def dummy_func():
        pass

    try:
        attribute_decorator = t8.attributes(tag="tag", phase="phase", level=1, weight=0, skip=False)
        attribute_decorator(dummy_func)
    except t8.Ten8tException:
        assert True

    except Exception:
        # The above cases don't work, even though the debugger says the exception is a Ten8tValueError
        # if I compare type(e) to Ten8tValueError it says False?
        assert False


def test_function_attributes():
    """Test arbitrary attributes"""

    @t8.attributes(tag="tag", phase="phase", level=1, weight=100, skip=False, thread_id='tid')
    def func():
        return True

    assert func.tag == "tag"
    assert func.phase == "phase"
    assert func.level == 1
    assert func.weight == 100
    assert func.skip is False
    assert func.thread_id == 'tid'


def test_def_function_attributes():
    """Check default tags"""

    @t8.attributes(tag="")
    def func():
        """Generic Test"""
        pass

    assert func.tag == ""
    assert func.phase == ""
    assert func.level == 1
    assert func.weight == 100
    assert func.skip is False
    assert func.thread_id == 'main_thread__'


@t8.attributes(tag="tag")
def test_bool_pass_with_docstring():
    """Boolean True, with docstring"""

    def func():
        """Doc string message"""
        return True

    result = next(t8.Ten8tFunction(func)())
    assert result.msg == "Doc string message"
    assert result.status is True


@t8.attributes(tag="tag")
def test_bool_pass_no_docstring():
    """Boolean True, no docstring"""

    def func():
        return True

    result = next(t8.Ten8tFunction(func)())  # Combined call
    assert result.msg == "Pass from function func"
    assert result.status is True


@t8.attributes(tag="tag")
def test_bool_fail_no_docstring():
    """Boolean False, no docstring"""

    def func():
        return False

    result = next(t8.Ten8tFunction(func)())  # Combined call
    assert result.msg == "Fail from function func"
    assert result.status is False


@t8.attributes(tag="tag")
def test_tr_pass_with_docstring():
    """TR True, with docstring"""

    def func():
        """Doc string message"""
        return t8.TR(status=True)

    result = next(t8.Ten8tFunction(func)())  # Combined call
    assert result.msg == "Doc string message"
    assert result.status is True


@t8.attributes(tag="tag")
def test_tr_pass_no_docstring():
    """TR True, no docstring"""

    def func():
        return t8.TR(status=True)

    result = next(t8.Ten8tFunction(func)())  # Combined call
    assert result.msg == "Pass from function func"
    assert result.status is True


@t8.attributes(tag="tag")
def test_tr_fail_no_docstring():
    """TR False, no docstring"""

    def func():
        return t8.TR(status=False)

    result = next(t8.Ten8tFunction(func)())
    assert result.msg == "Fail from function func"
    assert result.status is False


def test_def_messages_with_tr_results():
    """Verify message generation for functions returning TR results"""

    @t8.attributes(tag="tag")
    def func_doc_result_str():
        """Doc string message"""
        return t8.TR(status=True)

    @t8.attributes(tag="tag")
    def func_doc_result_str_empty():
        return t8.TR(status=True)

    sfunc4 = t8.Ten8tFunction(func_doc_result_str)
    sfunc5 = t8.Ten8tFunction(func_doc_result_str_empty)

    for result in sfunc4():
        assert result.msg == "Doc string message"

    for result in sfunc5():
        assert result.msg == "Pass from function func_doc_result_str_empty"


def test_basic_func_call():
    @t8.attributes(tag="Test")
    def func():
        """Test Function"""
        yield t8.TR(status=True, msg="It works")

    sfunc = t8.Ten8tFunction(func)

    for result in sfunc():
        assert result.func_name == "func"
        assert result.status is True
        assert result.msg == "It works"
        assert result.doc == "Test Function"
        assert result.skipped is False
        assert result.except_ is None
        assert result.warn_msg == ""
        assert result.info_msg == ""
        assert result.tag == "Test"


def test_basic_func_call_timing():
    @t8.attributes(tag="Timing")
    def func():
        """Test Timing Function"""
        time.sleep(.6)
        yield t8.TR(status=True, msg="Timing works")

    sfunc1 = t8.Ten8tFunction(func)

    @t8.attributes(tag="Timing")
    def fast_func():
        """Test Timing Function"""
        time.sleep(0.1)
        yield t8.TR(status=True, msg="Timing works")

    sfunc2 = t8.Ten8tFunction(fast_func)

    result: t8.Ten8tResult = next(sfunc1())
    assert result.status is True
    assert result.skipped is False
    assert result.except_ is None
    assert result.runtime_sec > .5

    result: t8.Ten8tResult = next(sfunc2())
    assert result.status is True
    assert result.skipped is False
    assert result.except_ is None
    assert result.runtime_sec < 0.2


def test_info_warning_func_call():
    """Verify that warning message gets to result"""

    @t8.attributes(tag="InfoWarning")
    def func():
        """Test Complex Function"""
        yield t8.TR(status=True, msg="It still works", warn_msg="Warning")

    sfunc = t8.Ten8tFunction(func)

    result: t8.Ten8tResult = next(sfunc())
    assert result.func_name == "func"
    assert result.status is True
    assert result.skipped is False
    assert result.except_ is None
    assert result.warn_msg == "Warning"


def test_divide_by_zero():
    """Test exception handling data passes through to result and automatic tracebacks """

    @t8.attributes(tag="DivideByZero")
    def func():
        """Test Exception Function"""
        return 1 / 0

    sfunc = t8.Ten8tFunction(func)

    result: t8.Ten8tResult = next(sfunc())
    assert result.status is False
    assert result.msg == "Exception 'division by zero' occurred while running .func"
    assert result.doc == "Test Exception Function"
    assert result.skipped is False
    assert str(result.except_) == "division by zero"
    assert 'return 1 / 0' in result.traceback  # Might be python rev dependent, trying to be better not None
    assert result.tag == "DivideByZero"


def test_use_return_with_no_info():
    """
    Users do the least amount of work possible so we need to make reasonable status
    messages from doc strings and function names.
    """

    def return_only():
        return True

    def yield_only():
        yield False

    # The above function requires all default cases to work correctly
    s_func1 = t8.Ten8tFunction(return_only)
    s_func2 = t8.Ten8tFunction(yield_only)
    for s_func in (s_func1, s_func2):
        for result in s_func():
            assert result.func_name == s_func.function_name
            assert result.weight == 100
            assert result.count == 1
            assert result.ttl_minutes == 0
            assert result.level == 1
            assert result.module_name == ''
            assert result.pkg_name == ''
            assert result.owner_list == []
            assert result.skipped is False
            if result.status:
                assert result.msg == f'Pass from function {s_func.function_name}'
            else:
                assert result.msg == f'Fail from function {s_func.function_name}'
