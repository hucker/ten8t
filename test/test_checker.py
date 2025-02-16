import pytest

from src import ten8t
from ten8t import BM


@pytest.fixture
def func1():
    @ten8t.attributes(tag="t1", level=1, phase='p1', ruid="suid_1")
    def func1():
        yield ten8t.Ten8tResult(status=True, msg="It works1")

    return ten8t.Ten8tFunction(func1)


@pytest.fixture
def func2():
    @ten8t.attributes(tag="t2", level=2, phase='p2', ruid="suid_2")
    def func2():
        yield ten8t.Ten8tResult(status=True, msg="It works2")

    return ten8t.Ten8tFunction(func2)


@pytest.fixture
def func3():
    @ten8t.attributes(tag="t3", level=3, phase='p3', ruid="suid_3")
    def func3():
        yield ten8t.Ten8tResult(status=True, msg="It works3")

    return ten8t.Ten8tFunction(func3)


@pytest.fixture
def func3_dup():
    """Duplicate of 3 for ruid testing"""

    @ten8t.attributes(tag="t3", level=3, phase='p3', ruid="suid_3")
    def func():
        yield ten8t.Ten8tResult(status=True, msg="It works3")

    return ten8t.Ten8tFunction(func)


@pytest.fixture
def func4():
    @ten8t.attributes(finish_on_fail=True, ruid="suid_4")
    def func():
        """ Because finish on fail is set, this function will only yield 3 results."""
        yield ten8t.Ten8tResult(status=True, msg="It works1")
        yield ten8t.Ten8tResult(status=True, msg="It works2")
        yield ten8t.Ten8tResult(status=False, msg="It works3")
        yield ten8t.Ten8tResult(status=True, msg="It works4")

    return ten8t.Ten8tFunction(func)


@pytest.fixture
def func_exc():
    @ten8t.attributes(tag="t3", level=3, phase='p3', ruid="suid_3")
    def func():
        raise ten8t.Ten8tException("Throw an exception")

    return ten8t.Ten8tFunction(func)


def test_no_attrs():
    def func():
        return ten8t.Ten8tResult(status=True, msg="It works")

    sfunc = ten8t.Ten8tFunction(func)

    ch = ten8t.Ten8tChecker(check_functions=[sfunc], auto_setup=True)

    assert ch.collected[0].function == func
    assert ch.collected[0] == sfunc


def test_checker_indexing(func1, func2, func3, func4):
    """Verify that the checker indexes the functions based on the load order"""
    ch = ten8t.Ten8tChecker(check_functions=[func1, func2, func3, func4], auto_setup=True)

    for count, func in enumerate(ch.check_functions, start=1):
        assert count == func.index
        assert 'adhoc' == func.module

    ch = ten8t.Ten8tChecker(check_functions=[func4, func3, func2, func1], auto_setup=True)

    for count, func in enumerate(ch.check_functions, start=1):
        assert count == func.index
        assert 'adhoc' == func.module


def test_attr_lists(func1, func2, func3):
    ch = ten8t.Ten8tChecker(check_functions=[func1, func2, func3], auto_setup=True)
    assert ch.phases == ['p1', 'p2', 'p3']
    assert ch.tags == ['t1', 't2', 't3']
    assert ch.ruids == ['suid_1', 'suid_2', 'suid_3']
    assert ch.levels == [1, 2, 3]


def test_bad_ruids(func3, func3_dup):
    """ force an exception to occur with duplicate ruids.   """
    with pytest.raises(ten8t.Ten8tException):
        _ = ten8t.Ten8tChecker(check_functions=[func3, func3_dup], auto_setup=True)


def test_finish_on_fail(func4):
    """ Because func4 has finish_on_fail is set, this function will only yield 3 results rather then 4"""
    ch = ten8t.Ten8tChecker(check_functions=[func4], auto_setup=True)
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
    ch = ten8t.Ten8tChecker(check_functions=[func3, func4], auto_setup=True)
    results = ch.run_all()
    assert len(results) == 3 + 1

    # Now we'll set it up again with the abort on fail set to true.  This will fail out
    # immediately on the whole test when the first fail occurs.
    ch = ten8t.Ten8tChecker(check_functions=[func4, func3], auto_setup=True, abort_on_fail=True)
    results = ch.run_all()

    # NOTE: we don't know the order that these functions are run we just know that it will stop early
    # and not get the same result as the function above.
    assert len(results) < (3 + 1)


def test_abort_on_exception(func1, func2, func_exc):
    """ The system has a mechanism to bail out of a run if any uncaught exception occurs.  In general
        ten8t functions should always work and have all exceptions handled.  It is usually an error,
        and we need to bail out of the run...but YMMV"""
    ch = ten8t.Ten8tChecker(check_functions=[func_exc, func1, func2], auto_setup=True, abort_on_fail=False)

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
    ch = ten8t.Ten8tChecker(check_functions=[func_exc, func1, func2], auto_setup=True, abort_on_exception=True)
    results: list[ten8t.Ten8tResult] = ch.run_all()
    assert len(results) == 1
    assert results[0].status is False
    assert results[0].except_
    assert ch.score == 0.0
    assert not ch.perfect_run

    # This has the exception in the second spot
    ch = ten8t.Ten8tChecker(check_functions=[func1, func_exc, func2], auto_setup=True, abort_on_exception=True)
    results: list[ten8t.Ten8tResult] = ch.run_all()
    assert len(results) == 2
    assert results[1].status is False
    assert results[1].except_
    assert ch.score == 50.0
    assert not ch.perfect_run
    assert not ch.clean_run

    # Stick a perfect run in here with abort_on_ex enabled
    ch = ten8t.Ten8tChecker(check_functions=[func1, func2], auto_setup=True, abort_on_exception=True)
    results: list[ten8t.Ten8tResult] = ch.run_all()
    assert len(results) == 2
    assert results[0].status
    assert results[1].status
    assert ch.score == 100.0
    assert ch.perfect_run
    assert ch.clean_run


def test_function_list(func1, func2):
    """Test that run_all returns results"""

    funcs = [func1, func2]

    ch = ten8t.Ten8tChecker(check_functions=funcs, auto_setup=True)
    results = ch.run_all()

    assert len(results) == 2
    assert results[0].status is True
    assert results[1].status is True
    assert ch.score == 100.0


def test_filtered_function_list(func1, func2):
    """Test building a custom filter function"""

    ch = ten8t.Ten8tChecker(check_functions=[func1, func2])

    def filter1(f: ten8t.Ten8tFunction):
        return f.ruid == "suid_1"

    def filter2(f: ten8t.Ten8tFunction):
        return f.ruid == "suid_2"

    ch.pre_collect()
    ch.prepare(filter_functions=[filter1])

    results = ch.run_all()
    assert len(results) == 1
    assert results[0].status is True
    assert results[0].msg == "It works1"
    assert results[0].ruid == "suid_1"

    # Rerun with second filter
    ch.prepare(filter_functions=[filter2])

    results = ch.run_all()
    assert len(results) == 1
    assert results[0].status is True
    assert results[0].msg == "It works2"
    assert results[0].ruid == "suid_2"


def test_checker_overview(func1, func2, func3):
    """Verify we can order tests by lambda over ruids"""

    funcs = [func3, func1, func2]
    ch = ten8t.Ten8tChecker(check_functions=funcs, auto_setup=True)
    results = ch.run_all()
    over = ten8t.overview(results)
    assert over == 'Total: 3, Passed: 3, Failed: 0, Errors: 0, Skipped: 0, Warned: 0'
    assert ch.score == 100.0


def test_checker_result_dict(func3):
    funcs = [func3]
    ch = ten8t.Ten8tChecker(check_functions=funcs, auto_setup=True)
    results = ch.run_all()
    rd = ten8t.ten8t_result.results_as_dict(results)
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

    ch = ten8t.Ten8tChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare(filter_functions=[ten8t.exclude_ruids(["suid_1"])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func2, func3}

    s_funcs = ch.prepare(filter_functions=[ten8t.exclude_ruids(["suid_1", "suid_2"])])

    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}

    ch = ten8t.Ten8tChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare(filter_functions=[ten8t.keep_ruids(["suid_3"])])

    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}

    s_funcs = ch.prepare(filter_functions=[ten8t.keep_ruids(["suid_1", "suid_2"])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func1, func2}


def test_builtin_filter_phase(func1, func2, func3):
    """Test exclude_ruids"""

    # Functions in random order
    funcs = [func3, func1, func2]

    ch = ten8t.Ten8tChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare(filter_functions=[ten8t.exclude_phases(["p1"])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func2, func3}

    s_funcs = ch.prepare(filter_functions=[ten8t.exclude_phases(["p1", "p2"])])

    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}

    ch = ten8t.Ten8tChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare(filter_functions=[ten8t.keep_phases(["p3"])])

    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}

    s_funcs = ch.prepare(filter_functions=[ten8t.keep_phases(["p1", "p2"])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func1, func2}


def test_builtin_filter_level(func1, func2, func3):
    """Test exclude_ruids"""

    # Functions in random order
    funcs = [func3, func1, func2]

    ch = ten8t.Ten8tChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare(filter_functions=[ten8t.exclude_levels([1])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func2, func3}

    s_funcs = ch.prepare(filter_functions=[ten8t.exclude_levels([1, 2])])

    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}

    ch = ten8t.Ten8tChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare(filter_functions=[ten8t.keep_levels([3])])

    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}

    s_funcs = ch.prepare(filter_functions=[ten8t.keep_levels([1, 2])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func1, func2}


def test_builtin_filter_tags(func1, func2, func3):
    """Test exclude_ruids"""

    # Functions in random order
    funcs = [func3, func1, func2]

    ch = ten8t.Ten8tChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare(filter_functions=[ten8t.exclude_tags(['t1'])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func2, func3}

    s_funcs = ch.prepare(filter_functions=[ten8t.exclude_tags(['t1', 't2'])])

    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}

    ch = ten8t.Ten8tChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare(filter_functions=[ten8t.keep_tags(['t3'])])

    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}

    s_funcs = ch.prepare(filter_functions=[ten8t.keep_tags(['t1', 't2'])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func1, func2}


def test_null_check():
    """Test exclude_ruids"""
    with pytest.raises(ten8t.Ten8tException):
        funcs = []

        ch = ten8t.Ten8tChecker(check_functions=funcs, auto_setup=True)

        _ = ch.run_all()


def test_null_checker_types():
    bad_list_type = [1]
    bad_value_type = 1

    with pytest.raises(ten8t.Ten8tException):
        _ = ten8t.Ten8tChecker(check_functions=bad_value_type)
    with pytest.raises(ten8t.Ten8tException):
        _ = ten8t.Ten8tChecker(modules=bad_value_type)
    with pytest.raises(ten8t.Ten8tException):
        _ = ten8t.Ten8tChecker(packages=bad_value_type)

    with pytest.raises(ten8t.Ten8tException):
        _ = ten8t.Ten8tChecker(check_functions=bad_list_type)
    with pytest.raises(ten8t.Ten8tException):
        _ = ten8t.Ten8tChecker(modules=bad_list_type)
    with pytest.raises(ten8t.Ten8tException):
        _ = ten8t.Ten8tChecker(packages=bad_list_type)


def test_filter_all(func1, func2):
    """Test filtering everything"""

    filters = [ten8t.exclude_ruids(["suid_1", "suid_2"])]

    ch = ten8t.Ten8tChecker(check_functions=[func1, func2])
    ch.pre_collect()
    ch.prepare(filter_functions=filters)

    results = ch.run_all()
    assert len(results) == 0


def test_as_dict(func1, func2):
    ch = ten8t.Ten8tChecker(check_functions=[func1, func2], auto_setup=True)
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


def test_progress(capsys, func1, func2):
    funcs = [func1, func2]
    ch = ten8t.Ten8tChecker(check_functions=funcs, progress_object=ten8t.Ten8tDebugProgress(), auto_setup=True)
    _ = ch.run_all()
    captured = capsys.readouterr()
    assert captured[
               0] == 'Start Rule Check\nFunc Start func1\n+Func done.\nFunc Start func2\n+Func done.\nRule Check Complete.\nScore = 100.0\n'


@pytest.fixture()
def attr_functions():
    def func_a():
        @ten8t.attributes(tag="t1", level=1, phase='p1', ruid="ruid_1")
        def func():
            yield ten8t.Ten8tResult(status=True, msg="It works1")

        return ten8t.Ten8tFunction(func)

    def func_b():
        @ten8t.attributes(tag="t2", level=2, phase='p2', ruid="ruid_2")
        def func():
            yield ten8t.Ten8tResult(status=True, msg="It works2")

        return ten8t.Ten8tFunction(func)

    def func_c():
        @ten8t.attributes(tag="t3", level=3, phase='p3', ruid="ruid_3")
        def func():
            yield ten8t.Ten8tResult(status=True, msg="It works3")

        return ten8t.Ten8tFunction(func)

    def func_d():
        @ten8t.attributes(tag="t4", level=4, phase='p4', ruid="ruid_4")
        def func():
            yield ten8t.Ten8tResult(status=True, msg="It works4")

        return ten8t.Ten8tFunction(func)

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
    ch = ten8t.Ten8tChecker(check_functions=attr_functions, auto_setup=True)
    ch.include_by_attribute(tags=tags, levels=levels, phases=phases, ruids=ruids)
    assert len(ch.collected) == expected_count, msg
    assert ch.collected[0].tag == 't1', msg


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
    ch = ten8t.Ten8tChecker(check_functions=attr_functions, auto_setup=True)
    funcs = ch.exclude_by_attribute(tags=tags, levels=levels, phases=phases, ruids=ruids)
    assert len(ch.collected) == expected_count, msg


@pytest.mark.parametrize('params, expect, msg', [
    ("", [], "String with no values."),
    ("p1", ["p1"], "String with one value."),
    ("p1 p2 p3", ["p1", "p2", "p3"], "String with multiple values"),
    ([], [], "List with no values."),
    (["p1"], ["p1"], "List with one value."),
    (["p1", "p2", "p3"], ["p1", "p2", "p3"], "List with multiple values"),
])
def test__get_str_list(params, expect, msg):
    assert ten8t.ten8t_checker._param_str_list(params) == expect, msg


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

    with pytest.raises(ten8t.Ten8tException):
        _ = ten8t.ten8t_checker._param_str_list(bad_list)


def xxx_test_bad_tag_phase_ruid_strings():
    """Strings used in attributes can't have illegal characters

    This isn't very strict
    """
    disallowed = r""",!@#$%^&*(){}[]<>~`-+=\/'"""
    for c in disallowed:
        for tag in [c, f"a-{c}", f"{c}-a", f"a-{c}-a"]:
            with pytest.raises(ten8t.Ten8tException):
                ten8t.ten8t_checker._param_str_list(tag, disallowed=disallowed)


@pytest.mark.parametrize('params, expect, msg', [
    ([1], [1], "List with one value."),
    ([1, 2, 3], [1, 2, 3], "List with multiple values"),
    ([], [], "List with no values."),
    ("", [], "String with no values."),
    ("1", [1], "String with one value."),
    ("1 2 3", [1, 2, 3], "String with multiple values"),

])
def test__get_int_list(params, expect, msg):
    value = ten8t.ten8t_checker._param_int_list(params)
    assert value == expect, msg


@pytest.mark.parametrize('params, msg', [
    (['a'], "list of strings"),
    ([1, 2, 3, 'a'], "list numbers and integers"),
    ('a', "string list"),
    ('1 a', "string list"),
    ('1 2 3 a', "string list"),
])
def test__bad_int_list(params, msg):
    with pytest.raises(ten8t.Ten8tException):
        _ = ten8t.ten8t_checker._param_int_list(params)


def test_env_nulls(func1, func2, func3):
    """ Verify that we detect None values in env variables.  This will be important in the future."""

    ch = ten8t.Ten8tChecker(check_functions=[func1, func2, func3], env={'foo': 1, 'fum': None}, auto_setup=True)
    _ = ch.run_all()
    header = ch.get_header()
    assert header['env_nulls'] == ['fum']
    assert header['levels'] == [1, 2, 3]
    assert header['function_count'] == 3


def test_auto_ruids():
    """Verify that ruids are only auto-created when the auto_ruid is true. """

    @ten8t.attributes(tag="t1", level=1, phase='p1')
    def ar_func1():
        yield ten8t.Ten8tResult(status=True, msg="It works1")

    @ten8t.attributes(tag="t1", level=1, phase='p1')
    def ar_func2():
        yield ten8t.Ten8tResult(status=True, msg="It works2")

    sfunc1 = ten8t.Ten8tFunction(ar_func1)
    sfunc2 = ten8t.Ten8tFunction(ar_func2)
    ch = ten8t.Ten8tChecker(check_functions=[sfunc1, sfunc2], auto_setup=True)
    results = ch.run_all()

    for result in results:
        assert result.ruid == ''

    ch = ten8t.Ten8tChecker(check_functions=[sfunc1, sfunc2], auto_setup=True, auto_ruid=True)
    results = ch.run_all()

    # NOTE: Order tests are run is not the parameter order in check_functions.
    assert len(results) == 2
    assert results[0].ruid != results[1].ruid
    assert results[0].func_name != results[1].func_name
    assert {results[0].ruid, results[1].ruid} == {'__ruid__0001', '__ruid__0002'}


@pytest.mark.parametrize("renderer,expected", [
    (None, "It works1 hello"),
    (ten8t.Ten8tBasicMarkdown(), "It works1 `hello`"),
    (ten8t.Ten8tRenderText(), "It works1 hello"),
    (ten8t.Ten8tBasicStreamlitRenderer(), "It works1 `hello`"),
    (ten8t.Ten8tBasicRichRenderer(), "It works1 hello"),
    (ten8t.Ten8tBasicHTMLRenderer(), "It works1 <code>hello</code>"),
])
def test_check_render_p(renderer, expected):
    """
    Check that the rendering works as expected for each type at the system level.
    
    These renderers are test in more detail in their unit tests.  This just shows that
    the generated text matches that of the rendered that is configured.
    """

    @ten8t.attributes(tag="t1", level=1, phase='p1')
    def render_func1():
        yield ten8t.Ten8tResult(status=True, msg=f"It works1 {BM.code('hello')}")

    rfunc1 = ten8t.Ten8tFunction(render_func1)
    ch = ten8t.Ten8tChecker(check_functions=[rfunc1], auto_setup=True, renderer=renderer)
    results = ch.run_all()

    assert len(results) == 1
    assert results[0].status == True
    assert results[0].msg == "It works1 <<code>>hello<</code>>"
    assert results[0].msg_rendered == expected


@pytest.mark.parametrize("renderer,expected", [
    (None, "It works1 hello"),
    (ten8t.Ten8tRenderText(), "It works1 hello"),
    (ten8t.Ten8tBasicMarkdown(), "It works1 hello"),
    (ten8t.Ten8tBasicStreamlitRenderer(), "It works1 :red[hello]"),
    (ten8t.Ten8tBasicRichRenderer(), "It works1 [red]hello[/red]"),
    (ten8t.Ten8tBasicHTMLRenderer(), """It works1 <span style="color:red">hello</span>"""),
])
def test_check_render_color(renderer, expected):
    @ten8t.attributes(tag="t1", level=1, phase='p1')
    def render_func1():
        yield ten8t.Ten8tResult(status=True, msg=f"It works1 {BM.red('hello')}")

    rfunc1 = ten8t.Ten8tFunction(render_func1)
    ch = ten8t.Ten8tChecker(check_functions=[rfunc1], auto_setup=True, renderer=renderer)
    results = ch.run_all()

    assert len(results) == 1
    assert results[0].status == True
    assert results[0].msg == "It works1 <<red>>hello<</red>>"
    assert results[0].msg_rendered == expected
