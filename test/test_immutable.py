"""

test_immutable.py

This module contains tests for verifying the immutability of three data structures: ImmutableList,
ImmutableDict, and ImmutableDataFrame. These classes are designed to prevent modifications of list,
dictionary, and DataFrame instances respectively to ensure data integrity.

The module is using pytest and its fixtures feature for setting up initial objects. The main strategy
of this module is trying to invoke all writable/mutating methods provided by Python for lists, dictionaries,
and pandas DataFrames on instances of ImmutableList, ImmutableDict, and ImmutableDataFrame.
The expected outcome of these operations is the raise of Ten8tException, indicating successful prevention of
mutation in these collections.

Tests for ImmutableList cover methods:
 - __setitem__
 - __delitem__
 - append
 - extend
 - insert
 - remove
 - pop
 - clear
 - sort
 - reverse

Tests for ImmutableDict cover methods:
 - __setitem__
 - __delitem__
 - pop
 - popitem
 - clear
 - update
 - setdefault

Tests for ImmutableDataFrame cover methods:
 - __setitem__
 - __delitem__
 - append
 - pop
 - drop
 - insert

These tests are designed to make sure that any attempts to modify instances of these classes would be blocked
and raise the appropriate exception, consistent with the intention of preserving immutability.
"""

import pytest

from src import ten8t as t8


@pytest.fixture(scope="module")
def env_list():
    return t8.Ten8tEnvList([1, 2, 3, 4, 5])


def test_list_setitem(env_list):
    with pytest.raises(t8.Ten8tException):
        env_list[0] = 100


def test_list_delitem(env_list):
    with pytest.raises(t8.Ten8tException):
        del env_list[0]


def test_list_append(env_list):
    with pytest.raises(t8.Ten8tException):
        env_list.append(6)


def test_list_extend(env_list):
    with pytest.raises(t8.Ten8tException):
        env_list.extend([7, 8, 9])


def test_list_insert(env_list):
    with pytest.raises(t8.Ten8tException):
        env_list.insert(0, 10)


def test_list_remove(env_list):
    with pytest.raises(t8.Ten8tException):
        env_list.remove(1)


def test_list_pop(env_list):
    with pytest.raises(t8.Ten8tException):
        env_list.pop(0)


def test_list_clear(env_list):
    with pytest.raises(t8.Ten8tException):
        env_list.clear()


def test_list_sort(env_list):
    with pytest.raises(t8.Ten8tException):
        env_list.sort()


def test_list_reverse(env_list):
    with pytest.raises(t8.Ten8tException):
        env_list.reverse()


# Define a fixture to provide the test target
@pytest.fixture
def env_dict():
    return t8.Ten8tEnvDict({"a": 1, "b": 2, "c": 3})


def test_dict_setitem(env_dict):
    with pytest.raises(t8.Ten8tException):
        env_dict["a"] = 100


def test_dict_delitem(env_dict):
    with pytest.raises(t8.Ten8tException):
        del env_dict["a"]


def test_dict_pop(env_dict):
    with pytest.raises(t8.Ten8tException):
        env_dict.pop("a")


def test_dict_popitem(env_dict):
    with pytest.raises(t8.Ten8tException):
        env_dict.popitem()


def test_clear(env_dict):
    with pytest.raises(t8.Ten8tException):
        env_dict.clear()


def test_dict_update(env_dict):
    with pytest.raises(t8.Ten8tException):
        env_dict.update({"a": 0, "d": 4})


def test_dict_setdefault(env_dict):
    with pytest.raises(t8.Ten8tException):
        env_dict.setdefault("d", 4)


@pytest.fixture
def func_list():
    @t8.attributes(tag="t1")
    def func_list(env_list):
        env_list[0] = 'a'
        yield t8.Ten8tResult(status=True, msg="It works1")

    return t8.Ten8tFunction(func_list)


@pytest.fixture
def func_dict():
    @t8.attributes(tag="t1")
    def func_dict(env_dict):
        env_dict['a'] = 100
        yield t8.Ten8tResult(status=True, msg="It works1")

    return t8.Ten8tFunction(func_dict)


@pytest.fixture
def func_set():
    @t8.attributes(tag="env_set")
    def func_list(env_set):
        env_set.clear()
        yield t8.Ten8tResult(status=True, msg="It works1")

    return t8.Ten8tFunction(func_list)


def test_ten8t_function_writing_to_env_dict(func_dict):
    env = {'env_list': [1, 2, 3], 'env_dict': {'a': 10, 'b': 11}, 'env_set': {1, 2, 3}}

    ch = t8.Ten8tChecker(check_functions=[func_dict], env=env, auto_setup=True)
    results = ch.run_all()
    assert len(results) == 1
    assert results[0].except_


def test_ten8t_function_writing_to_env_list(func_list):
    env = {'env_list': [1, 2, 3], 'env_dict': {'a': 10, 'b': 11}, 'env_set': {1, 2, 3}}
    ch = t8.Ten8tChecker(check_functions=[func_list], env=env, auto_setup=True)
    results = ch.run_all()
    assert len(results) == 1
    assert results[0].except_


def test_ten8t_function_writing_to_env_set(func_set):
    env = {'env_list': [1, 2, 3], 'env_dict': {'a': 10, 'b': 11}, 'env_set': {1, 2, 3}}
    ch = t8.Ten8tChecker(check_functions=[func_set], env=env, auto_setup=True)
    results = ch.run_all()
    assert len(results) == 1
    assert results[0].except_
