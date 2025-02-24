import pytest

from src import ten8t as t8


@pytest.fixture
def para_env():
    return t8.Ten8tModule(module_name="check_env", module_file="para_env/check_env.py")


def test_inline_env_func(para_env):
    assert len(para_env.env_functions) == 1

    ch = t8.Ten8tChecker(modules=[para_env], env={"global_env": "hello"}, auto_setup=True)
    results = ch.run_all()
    assert len(results) == 15
    assert all((result.status for result in results))


def test_module_not_in_list(para_env):
    assert len(para_env.env_functions) == 1

    ch = t8.Ten8tChecker(modules=para_env, env={"global_env": "hello"}, auto_setup=True)
    results = ch.run_all()
    assert len(results) == 15
    assert all((result.status for result in results))


def test_fail_on_none():
    @t8.attributes(tag="tag", phase="phase", level=1, weight=100, fail_on_none=True)
    def env_test_function(var):
        yield t8.TR(status=True, msg=f"This will pass if it ever gets here. {var=}")

    s_func = t8.Ten8tFunction(function_=env_test_function)
    ch = t8.Ten8tChecker(check_functions=[s_func], env={'var': None}, auto_setup=True)
    results = ch.run_all()

    assert len(results) == 1
    assert results[0].status is False
    assert results[0].msg.startswith("Failed due to None arg. 1 in func='env_test_function'")


def test_skip_on_none():
    @t8.attributes(tag="tag", phase="phase", level=1, weight=100, skip_on_none=True)
    def env_test_function(var):
        yield t8.TR(status=True, msg="This will pass if it ever gets here.")

    s_func = t8.Ten8tFunction(function_=env_test_function)
    ch = t8.Ten8tChecker(check_functions=[s_func], env={'var': None}, auto_setup=True)
    results = ch.run_all()

    assert len(results) == 1
    assert results[0].status is None
    assert results[0].msg.startswith("Skipped due to None arg. 1 in func='env_test_function")
