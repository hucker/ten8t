import pytest

import ten8t
from ten8t import Ten8tChecker, Ten8tMarkup


# Define the fixture for the results
@pytest.fixture(scope="module")
def results():
    pkg = ten8t.Ten8tPackage(folder="./pkg_result")
    chk = ten8t.Ten8tChecker(packages=pkg, auto_setup=True)
    return chk.run_all()


def test_default_values() -> None:
    """
    A bit overkill but default values changing can cause subtle bugs
    since in general we do not set all of these values, but we still depend
    upon them.
    """
    r = ten8t.Ten8tResult()
    assert r.status is False
    assert r.msg == ""
    assert r.ruid == ""
    assert r.tag == ""
    assert r.phase == ""
    assert r.level == 1
    assert r.count == 0
    assert r.skipped is False
    assert r.except_ is None
    assert r.traceback is ""
    assert r.runtime_sec == 0.0
    assert r.warn_msg == ""
    assert r.info_msg == ""
    assert r.thread_id == ""
    assert r.func_name == ""
    assert r.module_name == ""
    assert r.pkg_name == ""
    assert r.mit_msg == ""
    assert r.summary_result == False
    assert r.owner_list == []
    assert r.skip_on_none is False
    assert r.fail_on_none is False
    assert r.summary_result is False
    assert isinstance(r.mu, Ten8tMarkup)


def test_total_results(results) -> None:
    """ Test to verify the total results """
    assert len(results) == 7


def test_fail_only_filter(results) -> None:
    """ Test to verify the fail_only filter function """
    fail_only = [r for r in results if ten8t.ten8t_result.fails_only(r)]
    assert len(fail_only) == 2


def test_pass_only_filter(results) -> None:
    """ Test to verify the pass_only filter function """
    pass_only = [r for r in results if ten8t.ten8t_result.passes_only(r)]
    assert len(pass_only) == 5


def test_no_info_filter(results) -> None:
    """ Test to verify the remove_info filter function """
    no_info = [r for r in results if ten8t.ten8t_result.remove_info(r)]
    assert len(no_info) == 6


def test_warn_is_fail_filter(results) -> None:
    """ Test to verify the warn_as_fail filter function """
    warn_is_fail = [r for r in results if ten8t.ten8t_result.warn_as_fail(r)]
    assert len(warn_is_fail) == 7


def test_warning_messages(results) -> None:
    """ Test to verify the warning messages """
    wc = sum(1 for r in results if r.warn_msg)
    assert wc == 1


def test_info_messages(results) -> None:
    """ Test to verify the info messages """
    wc = sum(1 for r in results if r.info_msg)
    assert wc == 1


def test_group_by_tags(results) -> None:
    """ Test the group_by function with the 'tags' as the group key """
    grouped_results = ten8t.ten8t_result.group_by(results, ['tag'])
    assert len(grouped_results) == 3
    assert len(grouped_results['tag1']) == 3
    assert grouped_results['tag1'][0].ruid == "pass11"
    assert len(grouped_results['tag2']) == 3
    assert grouped_results['tag2'][0].ruid == "skip_flag"
    assert len(grouped_results['tag3']) == 1
    assert grouped_results['tag3'][0].ruid == "blank_msg"


def test_group_by_tags_ruid(results) -> None:
    """ This shows that the recursion works with multi level grouping """
    grouped_results = ten8t.ten8t_result.group_by(results, ['tag', 'ruid'])
    assert len(grouped_results) == 3
    assert len(grouped_results['tag1']) == 3
    assert len(grouped_results['tag1']['pass11']) == 1
    assert len(grouped_results['tag1']['fail12']) == 1
    assert len(grouped_results['tag1']['skip_none']) == 1
    assert len(grouped_results['tag2']['skip_flag']) == 1
    assert len(grouped_results['tag2']['warning']) == 1
    assert len(grouped_results['tag2']['info']) == 1
    assert len(grouped_results['tag3']['blank_msg']) == 1


def test_group_by_empty_key(results) -> None:
    """ This shows that the recursion works with multi level grouping """
    with pytest.raises(ten8t.Ten8tException):
        _ = ten8t.ten8t_result.group_by(results, [])


def test_group_by_ruids(results) -> None:
    """ Test the group_by function with the 'ruids' as the group key """
    r_grouped_results = ten8t.group_by(results, ['ruid'])
    assert len(r_grouped_results) == 7


def test_bad_generator_type(caplog) -> None:
    """Verify that we catch exceptions for BUGs in code

    The case of yielding the integer 123 is a BUG, this test shows that whenever this type of error
    is found that the underlying code aborts immediately and that we get the expected logs
    """

    @ten8t.attributes(tag="tag")
    def check_func1() -> None:
        yield 123
        # This won't run!
        yield ten8t.Ten8tResult(status=True, msg="Yield OK")  # pragma no cover

    ch = Ten8tChecker(check_functions=[check_func1], auto_setup=True, abort_on_exception=False)
    results = ch.run_all()
    assert len(results) == 1
    assert results[0].except_

    @ten8t.attributes(tag="tag")
    def check_func2():
        yield ten8t.Ten8tResult(status=True, msg="Yield OK")
        yield 123
        # This won't run
        yield ten8t.Ten8tResult(status=True, msg="Yield OK")  # pragma no cover

    ch = Ten8tChecker(check_functions=[check_func2], auto_setup=True, abort_on_exception=False)
    results = ch.run_all()
    assert len(results) == 2
    assert results[1].except_

    @ten8t.attributes(tag="tag")
    def check_func3():
        yield ten8t.Ten8tResult(status=True, msg="Yield OK")
        yield ten8t.Ten8tResult(status=True, msg="Yield OK")
        yield 123

    ch = Ten8tChecker(check_functions=[check_func3], auto_setup=True, abort_on_exception=False)
    results = ch.run_all()
    assert len(results) == 3
    assert results[2].except_

    assert len(caplog.messages) == 3
    assert "iteration 1" in caplog.messages[0]
    assert "iteration 2" in caplog.messages[1]
    assert "iteration 3" in caplog.messages[2]
