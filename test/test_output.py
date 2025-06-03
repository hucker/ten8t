import pytest

from src import ten8t as t8


@pytest.fixture
def simple1():
    @t8.attributes(tag="t1", level=1, ruid="ruid_1", phase='proto')
    def func1():
        """my doc string"""
        yield t8.Ten8tResult(status=True, msg="It works1")

    return t8.Ten8tFunction(func1)


@pytest.fixture
def simple2():
    @t8.attributes(tag="t2", level=2, ruid="ruid_2", phase='production')
    def func2():
        """my doc string"""
        yield t8.Ten8tResult(status=True, msg="It works2")

    return t8.Ten8tFunction(func2)


def test_json_ready_dict(simple1, simple2):
    """Test that the as_dict method serializes to json nicely"""
    ch = t8.Ten8tChecker(check_functions=[simple1, simple2])
    _ = ch.run_all()
    report = ch.as_dict()
    header = report['header']
    results = report['results']
    assert header['function_count'] == 2

    # Important to treat these as sets, don't assume order.
    assert set(header['levels']) == {1, 2}
    assert set(header['ruids']) == {'ruid_1', 'ruid_2'}
    assert set(header['tags']) == {'t1', 't2'}
    assert set(header['phases']) == {'proto', 'production'}
    assert set(header['functions']) == {'func1', 'func2'}

    assert header['pass_count'] == 2
    assert header['fail_count'] == 0
    assert header['skip_count'] == 0
    assert header['warn_count'] == 0
    assert header['check_count'] == 2
    assert header['total_count'] == 2
    assert header['clean_run'] is True
    assert header['perfect_run'] is True
    assert header['abort_on_fail'] is False
    assert header['abort_on_exception'] is False
    assert header['__version__'] == t8.__version__

    # We don't know the order that the functions run in
    assert len(results) == 2
    for result in results:
        if result['func_name'] == 'func1':
            assert result['status'] is True
            assert result['func_name'] == 'func1'
            assert result['msg'] == 'It works1'
            assert result['warn_msg'] == ''
            assert result['info_msg'] == ''
            assert result['tag'] == 't1'
            assert result['except_'] == 'None'  # Odd??
            assert result['traceback'] == ''
            assert result['skipped'] is False
            assert result['phase'] == 'proto'
            assert result['count'] == 1
            assert result['weight'] == 100
            assert result['ruid'] == 'ruid_1'
            assert result['mit_msg'] == ''
            assert result['doc'] == 'my doc string'
