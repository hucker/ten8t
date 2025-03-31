import re

import pytest

from src import ten8t as t8
from ten8t import TM


@pytest.fixture
def func1():
    @t8.attributes(tag="t1", level=1, phase='p1', ruid="suid_1")
    def func1():
        yield t8.Ten8tResult(status=True, msg="It works1")

    return t8.Ten8tFunction(func1)


@pytest.fixture
def func2():
    @t8.attributes(tag="t2", level=2, phase='p2', ruid="suid_2")
    def func2():
        yield t8.Ten8tResult(status=True, msg="It works2")

    return t8.Ten8tFunction(func2)


@pytest.fixture
def func3():
    @t8.attributes(tag="t3", level=3, phase='p3', ruid="suid_3")
    def func3():
        yield t8.Ten8tResult(status=True, msg="It works3")

    return t8.Ten8tFunction(func3)


@pytest.fixture
def func3_dup():
    """Duplicate of 3 for ruid testing"""

    @t8.attributes(tag="t3", level=3, phase='p3', ruid="suid_3")
    def func():
        yield t8.Ten8tResult(status=True, msg="It works3")  # pragma: no cover

    return t8.Ten8tFunction(func)


@pytest.fixture
def func4():
    @t8.attributes(finish_on_fail=True, ruid="suid_4")
    def func():
        """ Because finish on fail is set, this function will only yield 3 results."""
        yield t8.Ten8tResult(status=True, msg="It works1")
        yield t8.Ten8tResult(status=True, msg="It works2")
        yield t8.Ten8tResult(status=False, msg="It works3")
        # This is supposed to not run because finish_on_fail
        yield t8.Ten8tResult(status=True, msg="It works4")  # pragma no cover

    return t8.Ten8tFunction(func)


@pytest.fixture
def func_exc():
    @t8.attributes(tag="t3", level=3, phase='p3', ruid="suid_3")
    def func():
        raise t8.Ten8tException("Throw an exception")

    return t8.Ten8tFunction(func)


def test_no_attrs():
    def func():
        # This never runs because the checker doesn't run
        return t8.Ten8tResult(status=True, msg="It works")  # pragma no cover

    sfunc = t8.Ten8tFunction(func)

    ch = t8.Ten8tChecker(check_functions=[sfunc])

    assert ch.check_func_list[0].function == func
    assert ch.check_func_list[0] == sfunc


def test_checker_indexing(func1, func2, func3, func4):
    """Verify that the checker indexes the functions based on the load order"""
    ch = t8.Ten8tChecker(check_functions=[func1, func2, func3, func4])

    for count, func in enumerate(ch.check_functions, start=1):
        assert count == func.index
        assert t8.ten8t_checker.ADHOC_MODULE_NAME == func.module

    ch = t8.Ten8tChecker(check_functions=[func4, func3, func2, func1])

    for count, func in enumerate(ch.check_functions, start=1):
        assert count == func.index
        assert t8.ten8t_checker.ADHOC_MODULE_NAME == func.module


def test_attr_lists(func1, func2, func3):
    ch = t8.Ten8tChecker(check_functions=[func1, func2, func3])
    assert ch.phases == ['p1', 'p2', 'p3']
    assert ch.tags == ['t1', 't2', 't3']
    assert ch.ruids == ['suid_1', 'suid_2', 'suid_3']
    assert ch.levels == [1, 2, 3]


def test_bad_ruids(func3, func3_dup):
    """ force an exception to occur with duplicate ruids.   """
    with pytest.raises(t8.Ten8tException):
        _ = t8.Ten8tChecker(check_functions=[func3, func3_dup])


def test_finish_on_fail(func4):
    """ Because func4 has finish_on_fail is set, this function will only yield 3 results rather then 4"""
    ch = t8.Ten8tChecker(check_functions=[func4])
    results = ch.run_all()
    assert len(results) == 3
    assert results[0].status is True
    assert results[1].status is True
    assert results[2].status is False


def test_abort_on_fail(func4, func3):
    """
    Abort on fail exits the rule checking engine at the first fail

    WARNING: THIS TEST IS DEPENDENT UPON FUNCTION ORDERING AND THE RUN ORDER IS NOW LESS DETERMINISTIC
             CAUSING THIS TEST TO FAIL (even though the logic is still correct).  A MORE RELIABLE WAY
             TO CONTROL RUN ORDERING IS NEEDED>
    """

    # When we run the first case where the same function with finish on fail is called
    # twice, this should return 3 results for each run, since the func is configured to
    # return after the first false.  6 total results.
    ch = t8.Ten8tChecker(check_functions=[func3, func4])
    results = ch.run_all()
    assert len(results) == 3 + 1

    # Now we'll set it up again with the abort on fail set to true.  This will fail out
    # immediately on the whole test when the first fail occurs.
    ch = t8.Ten8tChecker(check_functions=[func4, func3], abort_on_fail=True)
    results = ch.run_all()

    # NOTE: we don't know the order that these functions are run we just know that it will stop early
    # and not get the same result as the function above.
    assert len(results) < (3 + 1)


def test_abort_on_exception(func1, func2, func_exc):
    """ The system has a mechanism to bail out of a run if any uncaught exception occurs.  In general
        ten8t functions should always work and have all exceptions handled.  It is usually an error,
        and we need to bail out of the run...but YMMV"""
    ch = t8.Ten8tChecker(check_functions=[func_exc, func1, func2], abort_on_fail=False)

    # Abort on exception set to false so all 3 run with the first one failing with exception
    results = ch.run_all()
    assert len(results) == 3
    assert not results[0].status
    assert results[0].except_
    assert results[1].status
    assert results[2].status
    assert ch.score == pytest.approx(66.667, rel=.1)
    assert not ch.perfect_run

    # This run has abort_on_except set to True and since the exception function is the first one
    # it aborts immediately
    ch = t8.Ten8tChecker(check_functions=[func_exc, func1, func2], abort_on_exception=True)
    results: list[t8.Ten8tResult] = ch.run_all()
    assert len(results) == 1
    assert results[0].status is False
    assert results[0].except_
    assert ch.score == 0.0
    assert not ch.perfect_run

    # This has the exception in the second spot
    ch = t8.Ten8tChecker(check_functions=[func1, func_exc, func2], abort_on_exception=True)
    results: list[t8.Ten8tResult] = ch.run_all()
    assert len(results) == 2
    assert results[1].status is False
    assert results[1].except_
    assert ch.score == 50.0
    assert not ch.perfect_run
    assert not ch.clean_run

    # Stick a perfect run in here with abort_on_ex enabled
    ch = t8.Ten8tChecker(check_functions=[func1, func2], abort_on_exception=True)
    results: list[t8.Ten8tResult] = ch.run_all()
    assert len(results) == 2
    assert results[0].status
    assert results[1].status
    assert ch.score == 100.0
    assert ch.perfect_run
    assert ch.clean_run


def test_check_counts(func1, func2, func3):
    """ Because func4 has finish_on_fail is set, this function will only yield 3 results rather then 4"""
    ch = t8.Ten8tChecker(check_functions=[func1, func2, func3])
    assert ch.function_count == 3
    assert ch.collected_count == 3
    assert ch.pre_collected_count == 3
    assert ch.module_count == 0
    assert ch.package_count == 0


def test_function_list(func1, func2):
    """Test that run_all returns results"""

    funcs = [func1, func2]

    ch = t8.Ten8tChecker(check_functions=funcs)
    results = ch.run_all()

    assert len(results) == 2
    assert results[0].status is True
    assert results[1].status is True
    assert ch.score == 100.0


def test_filtered_function_list(func1, func2):
    """Test building a custom filter function"""

    ch = t8.Ten8tChecker(check_functions=[func1, func2])

    def filter1(f: t8.Ten8tFunction):
        return f.ruid == "suid_1"

    def filter2(f: t8.Ten8tFunction):
        return f.ruid == "suid_2"

    ch.pre_collect()
    ch.prepare_functions(filter_functions=[filter1])

    results = ch.run_all()
    assert len(results) == 1
    assert results[0].status is True
    assert results[0].msg == "It works1"
    assert results[0].ruid == "suid_1"

    # Rerun with second filter
    ch.prepare_functions(filter_functions=[filter2])

    results = ch.run_all()
    assert len(results) == 1
    assert results[0].status is True
    assert results[0].msg == "It works2"
    assert results[0].ruid == "suid_2"


def test_checker_overview(func1, func2, func3):
    """Verify we can order tests by lambda over ruids"""

    funcs = [func3, func1, func2]
    ch = t8.Ten8tChecker(check_functions=funcs)
    results = ch.run_all()
    over = t8.overview(results)
    assert over == 'Total: 3, Passed: 3, Failed: 0, Errors: 0, Skipped: 0, Warned: 0'
    assert ch.score == 100.0


def test_checker_result_dict(func3):
    funcs = [func3]
    ch = t8.Ten8tChecker(check_functions=funcs)
    results = ch.run_all()
    rd = t8.ten8t_result.results_as_dict(results)
    # We can do a lot more testing here
    assert len(rd) == 1
    assert rd[0]["tag"] == 't3'
    assert rd[0]["level"] == 3
    assert rd[0]["status"]
    assert rd[0]["ruid"] == 'suid_3'


def test_builtin_filter_ruids(func1, func2, func3):
    """Test exclude_ruids"""

    # Functions in random order
    funcs = [func3, func1, func2]

    ch = t8.Ten8tChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare_functions(filter_functions=[t8.exclude_ruids(["suid_1"])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func2, func3}

    s_funcs = ch.prepare_functions(filter_functions=[t8.exclude_ruids(["suid_1", "suid_2"])])

    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}

    ch = t8.Ten8tChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare_functions(filter_functions=[t8.keep_ruids(["suid_3"])])

    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}

    s_funcs = ch.prepare_functions(filter_functions=[t8.keep_ruids(["suid_1", "suid_2"])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func1, func2}


def test_builtin_filter_phase(func1, func2, func3):
    """Test exclude_ruids"""

    # Functions in random order
    funcs = [func3, func1, func2]

    ch = t8.Ten8tChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare_functions(filter_functions=[t8.exclude_phases(["p1"])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func2, func3}

    s_funcs = ch.prepare_functions(filter_functions=[t8.exclude_phases(["p1", "p2"])])

    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}

    ch = t8.Ten8tChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare_functions(filter_functions=[t8.keep_phases(["p3"])])

    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}

    s_funcs = ch.prepare_functions(filter_functions=[t8.keep_phases(["p1", "p2"])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func1, func2}


def test_builtin_filter_level(func1, func2, func3):
    """Test exclude_ruids"""

    # Functions in random order
    funcs = [func3, func1, func2]

    ch = t8.Ten8tChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare_functions(filter_functions=[t8.exclude_levels([1])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func2, func3}

    s_funcs = ch.prepare_functions(filter_functions=[t8.exclude_levels([1, 2])])

    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}

    ch = t8.Ten8tChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare_functions(filter_functions=[t8.keep_levels([3])])

    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}

    s_funcs = ch.prepare_functions(filter_functions=[t8.keep_levels([1, 2])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func1, func2}


def test_builtin_filter_tags(func1, func2, func3):
    """Test exclude_ruids"""

    # Functions in random order
    funcs = [func3, func1, func2]

    ch = t8.Ten8tChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare_functions(filter_functions=[t8.exclude_tags(['t1'])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func2, func3}

    s_funcs = ch.prepare_functions(filter_functions=[t8.exclude_tags(['t1', 't2'])])

    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}

    ch = t8.Ten8tChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare_functions(filter_functions=[t8.keep_tags(['t3'])])

    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}

    s_funcs = ch.prepare_functions(filter_functions=[t8.keep_tags(['t1', 't2'])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func1, func2}


def test_null_check():
    """Exception if empty check function list"""
    with pytest.raises(t8.Ten8tException):
        funcs = []

        ch = t8.Ten8tChecker(check_functions=funcs)


def test_null_checker_types():
    bad_list_type = [1]
    bad_value_type = 1

    with pytest.raises(t8.Ten8tException):
        _ = t8.Ten8tChecker(check_functions=bad_value_type)  # type: ignore

    with pytest.raises(t8.Ten8tException):
        _ = t8.Ten8tChecker(modules=bad_value_type)  # type: ignore

    with pytest.raises(t8.Ten8tException):
        _ = t8.Ten8tChecker(packages=bad_value_type)  # type: ignore

    with pytest.raises(t8.Ten8tException):
        _ = t8.Ten8tChecker(check_functions=bad_list_type)  # type: ignore

    with pytest.raises(t8.Ten8tException):
        _ = t8.Ten8tChecker(modules=bad_list_type)  # type: ignore

    with pytest.raises(t8.Ten8tException):
        _ = t8.Ten8tChecker(packages=bad_list_type)  # type: ignore


def test_filter_all(func1, func2):
    """Test filtering everything"""

    filters = [t8.exclude_ruids(["suid_1", "suid_2"])]

    ch = t8.Ten8tChecker(check_functions=[func1, func2])
    ch.pre_collect()
    ch.prepare_functions(filter_functions=filters)

    results = ch.run_all()
    assert len(results) == 0


def test_as_dict(func1, func2):
    ch = t8.Ten8tChecker(check_functions=[func1, func2])
    _ = ch.run_all()
    d = ch.as_dict()
    assert isinstance(d, dict)

    assert d["functions"] == ['func1', 'func2']
    assert d["modules"] == []
    assert d["package_count"] == 0
    assert d["module_count"] == 0
    assert d["function_count"] == 2
    assert d["passed_count"] == 2
    assert d["failed_count"] == 0
    assert d["total_count"] == 2
    assert d["phases"] == ['p1', 'p2']
    assert d["levels"] == [1, 2]
    assert d["tags"] == ['t1', 't2']
    assert d["ruids"] == ['suid_1', 'suid_2']
    assert d["score"] == 100.0
    assert d["skip_count"] == ch.skip_count
    assert d["warn_count"] == 0
    assert d["start_time"] == ch.start_time
    assert d["end_time"] == ch.end_time
    assert d["abort_on_fail"] is False
    assert d["abort_on_exception"] is False
    assert d["perfect_run"] is ch.perfect_run
    assert d["clean_run"] is ch.clean_run


def test_progress(capsys, func1, func2):
    funcs = [func1, func2]
    ch = t8.Ten8tChecker(check_functions=funcs, progress_object=t8.Ten8tDebugProgress())
    _ = ch.run_all()
    captured = capsys.readouterr()
    assert captured[
               0] == 'Start Rule Check\nFunction Start func1\n+Function func1 done.\nFunction Start func2\n+Function func2 done.\nRule Check Complete.\nScore = 100.0\n'


@pytest.fixture()
def attr_functions():
    def func_a():
        @t8.attributes(tag="t1", level=1, phase='p1', ruid="ruid_1")
        def func():  # pragma no cover
            """Not called because we are only checking attributes"""
            yield t8.Ten8tResult(status=True, msg="It works1")

        return t8.Ten8tFunction(func)

    def func_b():
        """Not called because we are only checking attributes"""

        @t8.attributes(tag="t2", level=2, phase='p2', ruid="ruid_2")
        def func():  # pragma no cover
            yield t8.Ten8tResult(status=True, msg="It works2")

        return t8.Ten8tFunction(func)

    def func_c():
        """Not called because we are only checking attributes"""

        @t8.attributes(tag="t3", level=3, phase='p3', ruid="ruid_3")
        def func():  # pragma no cover
            yield t8.Ten8tResult(status=True, msg="It works3")

        return t8.Ten8tFunction(func)

    def func_d():
        """Not called because we are only checking attributes"""

        @t8.attributes(tag="t4", level=4, phase='p4', ruid="ruid_4")
        def func():  # pragma no cover
            yield t8.Ten8tResult(status=True, msg="It works4")

        return t8.Ten8tFunction(func)

    return [func_a(), func_b(), func_c(), func_d()]


@pytest.mark.parametrize('tags,levels,phases,ruids,expected_count,msg', [
    ([], [], 'p1 p2 p3 p4', 'ruid_1', 4, "All parameters empty except 'phases' and 'ruids'."),
    (['t1'], [], [], [], 1, "Single tag match."),
    (['t1'], 1, [], [], 1, "Duplicated matches give 1 output."),
    (['t1'], 1, 'p1', [], 1, "Duplicated matches give 1 output."),
    (['t1'], 1, 'p1', 'ruid_1', 1, "Duplicated matches give 1 output."),
    (['t4'], 3, 'p2', ['ruid_1'], 4, "Single function 't4' with level, phase, and 'ruids'"),
    ('t1 t2 t3 t4', [], [], [], 4, "All different functions."),
    (['t1'], 2, ['p3'], ['ruid_4'], 4, "Single function with level, phase array and 'ruids'."),
    ('t1 t2 t3 t4', [], [], [], 4, "All different tags without extra parameters."),
    ([], [1, 2, 3, 4], [], [], 4, "All levels and no functions."),
    ([], [], 'p1 p2 p3 p4', [], 4, "All phases and no functions."),
    ([], [], [], 'ruid_1 ruid_2 ruid_3 ruid_4', 4, "All 'ruids' and no functions."),
    (['t1'], [2], [], [], 2, "Single function 't1' with level 2."),
    (['t1'], 2, [], [], 2, "Same function with level."),
    (['t1'], 2, 'p1', [], 2, "Same function with level and single phase."),
    (['t1'], 2, 'p1', 'ruid_1', 2, "Same function with level, phase and 'ruid_1'."),
    (['t1'], 2, [], 'ruid_3', 3, "Single function array, with level and 'ruid_3'."),
    (['t1'], 2, 'p1', 'ruid_3', 3, "Single function array, with level, phase and 'ruid_3'."),
    (['t1'], 2, 'p4', 'ruid_1', 3, "Single function array, with level, phase and 'ruid_1'."),
])
def test_include_by_attribute(attr_functions, tags, levels, phases, ruids, expected_count, msg):
    ch = t8.Ten8tChecker(check_functions=attr_functions)
    ch.include_by_attribute(tags=tags, levels=levels, phases=phases, ruids=ruids)
    assert len(ch.check_func_list) == expected_count, msg
    assert ch.check_func_list[0].tag == 't1', msg


@pytest.mark.parametrize('tags,levels,phases,ruids,expected_count,msg', [
    # Broken
    ([], [1, 2, 3, 4], [], [], 0, 'All levels leave none.'),
    ([], [], 'p1 p2 p3 p4', [], 0, 'All phases leave none.'),
    ([], [], [], 'ruid_1 ruid_2 ruid_3 ruid_4', 0, "All ruids leave none."),
    (['t1'], [2], [], [], 2, 'Tag level leave 2'),

    # OK
    (['t1'], [], [], [], 3, "Tag only"),
    ([], [], 'p1 p2 p3 p4', [], 0, "all phases leave none"),
    ('t1 t2 t3 t4', [], [], [], 0, 'All tags leave none'),
    (['t1'], 1, [], [], 3, 'Tag and level'),
    (['t1'], 1, 'p1', [], 3, 'Tag level and phase'),
    (['t1'], 1, 'p1', 'ruid_1', 3, 'Tag level phase and ruid'),
    (['t4'], 3, 'p2', ['ruid_1'], 0, "all phases leave none"),
    (['t1'], 2, ['p3'], ['ruid_4'], 0, "one of each leave none"),
    (['t1'], 2, [], [], 2, 'Tag level leave 2'),
    (['t1'], 2, 'p1', [], 2, 'Tag level and redundant phase leave 2'),
    (['t1'], 2, 'p1', 'ruid_1', 2, 'Tag Level Phase and Ruid with 2 redundant leave 2'),
    (['t1'], 2, [], 'ruid_3', 1, "Tag level ruid leave 1"),
    (['t1'], 2, 'p1', ['ruid_3'], 1, "Tag level phase with redundant tag/phase leave 1"),
])
def test_exclude_by_attribute(attr_functions, tags, levels, phases, ruids, expected_count, msg):
    ch = t8.Ten8tChecker(check_functions=attr_functions)
    _ = ch.exclude_by_attribute(tags=tags, levels=levels, phases=phases, ruids=ruids)
    assert len(ch.check_func_list) == expected_count, msg


@pytest.mark.parametrize('params, expect, msg', [
    ("", [], "String with no values."),
    ("p1", ["p1"], "String with one value."),
    ("p1 p2 p3", ["p1", "p2", "p3"], "String with multiple values"),
    ([], [], "List with no values."),
    (["p1"], ["p1"], "List with one value."),
    (["p1", "p2", "p3"], ["p1", "p2", "p3"], "List with multiple values"),
])
def test__get_str_list(params, expect, msg):
    assert t8.ten8t_checker._param_str_list(params) == expect, msg


@pytest.mark.parametrize("bad_list", [
    ["foo", 1],
    ["foo", None],
    ["foo", 3.3],
    ["foo", True],
    [[], "foo"],
    [{"key": "value"}, "foo"],
    ["foo", 1],
    [1],
])
def test_bad_get_str_list_2(bad_list):
    """ This only handles lists of strings"""

    with pytest.raises(t8.Ten8tException):
        _ = t8.ten8t_checker._param_str_list(bad_list)


# Define a list of disallowed characters for _param_str_list
DISALLOWED_CHARS = ["[", "]", "{", "}", "<", ">", "|", ":", "*", "?", '"']


def test_bad_tag_phase_ruid_strings():
    """Strings used in attributes can't have illegal characters

    This isn't very strict
    """
    disallowed = r""",!@#$%^&*(){}[]<>~`-+=\/'"""
    for c in disallowed:
        for tag in [c, f"a-{c}", f"{c}-a", f"a-{c}-a"]:
            with pytest.raises(t8.Ten8tException):
                t8.ten8t_checker._param_str_list(tag, disallowed=disallowed)


@pytest.mark.parametrize('params, expect, msg', [
    ([1], [1], "List with one value."),
    ([1, 2, 3], [1, 2, 3], "List with multiple values"),
    ([], [], "List with no values."),
    ("", [], "String with no values."),
    ("1", [1], "String with one value."),
    ("1 2 3", [1, 2, 3], "String with multiple values"),

])
def test__get_int_list(params, expect, msg):
    value = t8.ten8t_checker._param_int_list(params)
    assert value == expect, msg


@pytest.mark.parametrize('params, msg', [
    (['a'], "list of strings"),
    ([1, 2, 3, 'a'], "list numbers and integers"),
    ('a', "string list"),
    ('1 a', "string list"),
    ('1 2 3 a', "string list"),
])
def test__bad_int_list(params, msg):
    with pytest.raises(t8.Ten8tException):
        _ = t8.ten8t_checker._param_int_list(params)


def test_env_nulls(func1, func2, func3):
    """ Verify that we detect None values in env variables.  This will be important in the future."""

    ch = t8.Ten8tChecker(check_functions=[func1, func2, func3], env={'foo': 1, 'fum': None})
    _ = ch.run_all()
    header = ch.get_header()
    assert header['env_nulls'] == ['fum']
    assert header['levels'] == [1, 2, 3]
    assert header['function_count'] == 3


def test_verify_version(func1):
    ch = t8.Ten8tChecker(check_functions=[func1])
    _ = ch.run_all()
    header = ch.get_header()

    ver = t8.version("ten8t")

    # This is a it circular, but it is important that the version makes it into the output data stream
    # and that it is not unknown.   Note that is not verifying that the version number is correct, just
    # that it exists and isn't unkown.
    assert header['__version__'] == ver
    assert ver.lower() != 'unknown'

    # Should match versions like 1.22.23.  All numbers are required and they must be 0-99
    # Strictly speaking this is not a real test, the version can be anything, but at this time
    # this is the pattern I expect.
    pattern = r'^\d{1,2}\.\d{1,2}\.\d{1,2}$'

    # The version should match the patter.
    match = re.match(pattern, ver)
    assert match, "Version did not match xx.yy.zz version number pattern."


def test_auto_ruids():
    """Verify that ruids are only auto-created when the auto_ruid is true. """

    @t8.attributes(tag="t1", level=1, phase='p1')
    def ar_func1():
        yield t8.Ten8tResult(status=True, msg="It works1")

    @t8.attributes(tag="t1", level=1, phase='p1')
    def ar_func2():
        yield t8.Ten8tResult(status=True, msg="It works2")

    sfunc1 = t8.Ten8tFunction(ar_func1)
    sfunc2 = t8.Ten8tFunction(ar_func2)
    ch = t8.Ten8tChecker(check_functions=[sfunc1, sfunc2])
    results = ch.run_all()

    for result in results:
        assert result.ruid == ''

    ch = t8.Ten8tChecker(check_functions=[sfunc1, sfunc2], auto_ruid=True)
    results = ch.run_all()

    # NOTE: Order tests are run is not the parameter order in check_functions.
    assert len(results) == 2
    assert results[0].ruid != results[1].ruid
    assert results[0].func_name != results[1].func_name
    assert {results[0].ruid, results[1].ruid} == {'__ruid__0001', '__ruid__0002'}


@pytest.mark.parametrize(
    "renderer,expected",
    [
        (None, "It works1 hello"),
        (t8.Ten8tBasicMarkdownRenderer(), "It works1 `hello`"),
        (t8.Ten8tTextRenderer(), "It works1 hello"),
        (t8.Ten8tBasicStreamlitRenderer(), "It works1 `hello`"),
        (t8.Ten8tBasicRichRenderer(), "It works1 [bold]hello[/bold]"),
        (t8.Ten8tBasicHTMLRenderer(), "It works1 <code>hello</code>"),
    ],
)
def test_check_render_p(renderer, expected):
    """
    Check that the rendering works as expected for each type at the system level.
    
    These renderers are test in more detail in their unit tests.  This just shows that
    the generated text matches that of the rendered that is configured.
    """

    @t8.attributes(tag="t1", level=1, phase='p1')
    def render_func1():
        yield t8.Ten8tResult(status=True, msg=f"It works1 {TM.code('hello')}")

    rfunc1 = t8.Ten8tFunction(render_func1)
    ch = t8.Ten8tChecker(check_functions=[rfunc1], renderer=renderer)
    results = ch.run_all()

    assert len(results) == 1
    assert results[0].status == True
    assert results[0].msg == "It works1 <<code>>hello<</code>>"
    assert results[0].msg_rendered == expected


@pytest.mark.parametrize("renderer,expected", [
    (None, "It works1 hello"),
    (t8.Ten8tTextRenderer(), "It works1 hello"),
    (t8.Ten8tBasicMarkdownRenderer(), "It works1 hello"),
    (t8.Ten8tBasicStreamlitRenderer(), "It works1 :red[hello]"),
    (t8.Ten8tBasicRichRenderer(), "It works1 [red]hello[/red]"),
    (t8.Ten8tBasicHTMLRenderer(), """It works1 <span style="color:red">hello</span>"""),
])
def test_check_render_color(renderer, expected):
    @t8.attributes(tag="t1", level=1, phase='p1')
    def render_func1():
        yield t8.Ten8tResult(status=True, msg=f"It works1 {TM.red('hello')}")

    rfunc1 = t8.Ten8tFunction(render_func1)
    ch = t8.Ten8tChecker(check_functions=[rfunc1], renderer=renderer)
    results = ch.run_all()

    assert len(results) == 1
    assert results[0].status == True
    assert results[0].msg == "It works1 <<red>>hello<</red>>"
    assert results[0].msg_rendered == expected


def test_msg_renderer_simple():
    """Verify that all the messages are populated in a simple case."""

    @t8.attributes(tag="t1", level=1, phase='p1')
    def render_func1():
        yield t8.Ten8tResult(status=True, msg=f"message", warn_msg="warning", info_msg="info")

    ch = t8.Ten8tChecker(check_functions=[render_func1])
    results = ch.run_all()
    result = results[0]
    assert result.msg_rendered == "message"
    assert result.warn_msg_rendered == "warning"
    assert result.info_msg_rendered == "info"

    assert result.msg == "message"
    assert result.warn_msg == "warning"
    assert result.info_msg == "info"

    assert result.msg_text == "message"
    assert result.warn_msg_text == "warning"
    assert result.info_msg_text == "info"


def test_msg_renderer_complex():
    """
    Verify that msg/info/warn messages are populated in a rendered case.

    In this case all messages are the same
    """

    @t8.attributes(tag="t1", level=1, phase='p1')
    def render_func1():
        yield t8.TR(status=True,
                    msg=f"<<code>>message<</code>>",
                    warn_msg="<<code>>warning<</code>>",
                    info_msg="<<code>>info<</code>>")

    ch = t8.Ten8tChecker(check_functions=[render_func1], renderer=t8.Ten8tBasicMarkdownRenderer())
    results = ch.run_all()
    result = results[0]

    # Renderer applied
    assert result.msg_rendered == "`message`"
    assert result.warn_msg_rendered == "`warning`"
    assert result.info_msg_rendered == "`info`"

    # Raw messages with markup
    assert result.msg == "<<code>>message<</code>>"
    assert result.warn_msg == "<<code>>warning<</code>>"
    assert result.info_msg == "<<code>>info<</code>>"

    # Raw Text
    assert result.msg_text == "message"
    assert result.warn_msg_text == "warning"
    assert result.info_msg_text == "info"


@pytest.fixture(scope="module")
def bare_func1():
    def func():
        return True

    return func


@pytest.fixture(scope="module")
def bare_func2():
    def func():
        return False

    return func


def test_auto_ten8t_funct(bare_func1, bare_func2):
    """
    Show that we can natively handle regular python functions.

    This depends on the checker setup code detecting that the function isn't "right" and it automatically
    wrapping it with the Ten8tFunction class when detected.
    """

    def bare_func3():
        return t8.TR(status=True, msg="Hello world.")

    ch = t8.Ten8tChecker(check_functions=[bare_func1, bare_func2, bare_func3])
    results = ch.run_all()
    assert len(results) == 3
    assert results[0].status is True
    assert results[1].status is False
    assert results[2].status is True
    assert results[2].msg == "Hello world."


def test_module_autothread2():
    """Make sure we can load modules individually and extract the ruids"""
    module1 = t8.Ten8tModule(module_name="check_suid1_a", module_file='./ruid/check_suid1_a.py', auto_thread=True)
    module2 = t8.Ten8tModule(module_name="check_suid2_a", module_file='./ruid/check_suid2_a.py', auto_thread=True)

    ch = t8.Ten8tChecker(modules=[module1, module2])

    # Now we added two modules, each with auto threading on, so there should be 2 unique thread ids.
    assert len(set(func.thread_id for func in ch.check_func_list)) == 2

    # Since there is no filtering of functions the pre-collect and collect counts should be the same
    assert ch.collected_count == ch.pre_collected_count
