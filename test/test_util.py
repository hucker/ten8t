import pathlib

import pytest

import ten8t
from ten8t import any_to_int_list, any_to_path_list, any_to_str_list, clean_dict, str_to_bool


@pytest.mark.parametrize("input_val",
                         ['true', 't', 'yes', 'y', '1', 'on'])
def test_def_str_to_bool_true(input_val):
    assert str_to_bool(input_val) == True


# Test when str_to_bool return False
@pytest.mark.parametrize("input_val",
                         ['false', 'f', 'no', 'n', '0', 'off'])
def test_def_str_to_bool_false(input_val):
    assert str_to_bool(input_val) == False


@pytest.mark.parametrize("input_val", ['x', 'foo', 'whatever', '', ' '])
def test_except(input_val):
    with pytest.raises(ValueError):
        _ = str_to_bool(input_val)


@pytest.mark.parametrize("input_val, default_val",
                         [('x', True),
                          ('x', False),
                          ('foo', True),
                          ('foo', False),
                          ('fum', True),
                          ('fum', False),
                          ('whatever', True),
                          ('whatever', False)])
def test_def_str_to_bool(input_val, default_val):
    if default_val is True:
        assert str_to_bool(input_val, default_val) == True
    else:
        assert str_to_bool(input_val, default_val) == False


@pytest.mark.parametrize("input_val, default_val, expected_output",
                         [('f', True, False),
                          ('f', False, False),
                          ('t', True, True),
                          ('t', False, True)])
def test_def_str_no_override(input_val, default_val, expected_output):
    assert str_to_bool(input_val, default_val) == expected_output


@pytest.mark.parametrize('input_data, separator, expected_output', [
    ('foo bar baz', ' ', ['foo', 'bar', 'baz']),
    ('foo,bar,baz', ',', ['foo', 'bar', 'baz']),
    ('foo;bar;baz', ';', ['foo', 'bar', 'baz']),
    ('1;bar;234', ';', ['1', 'bar', '234']),
    (None, ' ', []),
    ('', ' ', []),

])
def test_str_list(input_data, separator, expected_output):
    if separator == ' ':
        params = any_to_str_list(input_data)
    else:
        params = any_to_str_list(input_data, separator)
    assert params == expected_output


@pytest.mark.parametrize("input_data", [
    [1, '1'],
    [1, 2, 3],
    ['1', 2],
    ['1', {'foo': 1}],
    {},
    1.23,
    # You can add more test cases here
])
def test_bad_str_list(input_data):
    with pytest.raises(ValueError):
        _ = any_to_str_list(input_data)


@pytest.mark.parametrize(
    "input_param,expected_result",
    [(None, []),
     ("1 2 3", [1, 2, 3]),
     ([42], [42]),
     ([42, '43'], [42, 43]),
     ]
)
def test_any_to_int_list_valid_cases(input_param, expected_result):
    assert any_to_int_list(input_param) == expected_result


@pytest.mark.parametrize(
    "input_param",
    [("a b c"),
     ([1, "two", 3]),
     ([[1]]),
     ({}),
     ]
)
def test_any_to_int_list_invalid_cases(input_param):
    with pytest.raises((ValueError, TypeError)):
        _ = any_to_int_list(input_param)


def test_next_int():
    """The next_int_value just gives me increasing numbers, this checks that."""
    s = set()
    num_tests = 5
    # Verify this gives incrementing numbers
    for _ in range(num_tests):
        v1 = ten8t.next_int_value()
        v2 = ten8t.next_int_value()
        s.add(v1)
        s.add(v2)
        assert v2 - v1 == 1
    assert len(s) == num_tests * 2




@pytest.mark.parametrize("input_files, expected_output", [

    # String with extra spaces
    ("  test.py   test2.py  ", [pathlib.Path("test.py"), pathlib.Path("test2.py")]),

    # Single filename as a simple string
    ("test.py", [pathlib.Path("test.py")]),

    # Empty string (no file)
    ("", []),

    # Multiple filenames separated by spaces
    ("test.py test2.py", [pathlib.Path("test.py"), pathlib.Path("test2.py")]),

    # List of filenames as string list
    (["test.py", "test2.py"], [pathlib.Path("test.py"), pathlib.Path("test2.py")]),

    # List including Path objects
    ([pathlib.Path("test.py"), pathlib.Path("test2.py")], [pathlib.Path("test.py"), pathlib.Path("test2.py")]),

    # Single Path object only
    (pathlib.Path("test.py"), [pathlib.Path("test.py")]),

    # Mixed list of string and Path objects
    (["test.py", pathlib.Path("test2.py")], [pathlib.Path("test.py"), pathlib.Path("test2.py")]),

    # String with extra spaces
    ("  test.py   test2.py  ", [pathlib.Path("test.py"), pathlib.Path("test2.py")]),

    # None input should yield empty list
    (None, []),

])
def test_any_to_path_list_parametrized(input_files, expected_output):
    assert any_to_path_list(input_files) == expected_output


@pytest.mark.parametrize(
    "data, keep_keys, expected",
    [
        # Test case 1: Basic dictionary without nested structure
        (
                {
                    "name": "Alice",
                    "age": 25,
                    "address": "",
                    "email": "alice@example.com",
                    "phone": []
                },
                None,  # No keep_keys provided
                {
                    "name": "Alice",
                    "age": 25,
                    "email": "alice@example.com"
                }
        ),
        # Test case 2: Nested dictionary with empty and non-empty values
        (
                {
                    "name": "Alice",
                    "details": {
                        "address": "",
                        "city": "Wonderland",
                        "hobbies": [],
                        "additional_info": {
                            "note": "",
                            "languages": ["English", "French"],
                            "preferences": []
                        }
                    },
                    "phone": ""
                },
                None,  # No keep_keys provided
                {
                    "name": "Alice",
                    "details": {
                        "city": "Wonderland",
                        "additional_info": {
                            "languages": ["English", "French"]
                        }
                    }
                }
        ),
        # Test case 3: Dictionary with empty lists only
        (
                {
                    "list1": [],
                    "list2": [],
                    "list3": [1, 2, 3]
                },
                None,  # No keep_keys provided
                {
                    "list3": [1, 2, 3]
                }
        ),
        # Test case 4: Dictionary with keep_keys parameter
        (
                {
                    "name": "Alice",
                    "address": "",
                    "phone": "",
                    "details": {
                        "note": "",
                        "special_key": ""
                    },
                    "special_key": ""
                },
                ["special_key"],  # Keep "special_key"
                {
                    "name": "Alice",
                    "details": {
                        "special_key": ""
                    },
                    "special_key": ""
                }
        ),
        # Test case 5: Empty dictionary
        (
                {},
                None,  # No keep_keys provided
                {}
        ),
        # Test case 6: Dictionary with no empty values
        (
                {
                    "name": "Alice",
                    "age": 25,
                    "email": "alice@example.com",
                    "city": "Wonderland"
                },
                None,  # No keep_keys provided
                {
                    "name": "Alice",
                    "age": 25,
                    "email": "alice@example.com",
                    "city": "Wonderland"
                }
        ),
        # Test case 7: Nested dictionary with empty lists and keep_keys parameter
        (
                {
                    "name": "Alice",
                    "details": {
                        "hobbies": [],
                        "additional_info": {
                            "preferences": []
                        },
                        "special_list": []
                    },
                    "special_key": "",
                    "phone": []
                },
                ["special_list", "special_key"],  # Keep "special_list" and "special_key"
                {
                    "name": "Alice",
                    "details": {
                        "special_list": []
                    },
                    "special_key": ""
                }
        ),
    ]
)
def test_clean_dict(data, keep_keys, expected):
    """
    Test the clean_dict function with various test cases using parameterized input.
    """
    if keep_keys is not None:
        assert clean_dict(data, keep_keys=keep_keys) == expected
    else:
        assert clean_dict(data) == expected


@pytest.mark.parametrize(
    "data, remove_keys, keep_keys, expected",
    [
        # Test case 1: Forcibly remove a specific key at the top level
        (
                {
                    "name": "Alice",
                    "email": "alice@example.com",
                    "phone": "123-456-7890",
                    "address": "Wonderland"
                },
                ["phone"],  # Remove "phone"
                None,  # No keep_keys
                {
                    "name": "Alice",
                    "email": "alice@example.com",
                    "address": "Wonderland"
                }
        ),

        # Test case 2: Remove multiple keys at the top level
        (
                {
                    "name": "Alice",
                    "email": "alice@example.com",
                    "phone": "123-456-7890",
                    "notes": "Contact me after 5 PM",
                    "address": "Wonderland"
                },
                ["phone", "notes"],  # Remove "phone" and "notes"
                None,  # No keep_keys
                {
                    "name": "Alice",
                    "email": "alice@example.com",
                    "address": "Wonderland"
                }
        ),

        # Test case 3: Remove a key inside a nested dictionary
        (
                {
                    "name": "Alice",
                    "details": {
                        "address": "Wonderland",
                        "phone": "123-456-7890"
                    },
                    "email": "alice@example.com"
                },
                ["phone"],  # Remove "phone" inside nested "details"
                None,  # No keep_keys
                {
                    "name": "Alice",
                    "details": {
                        "address": "Wonderland"
                    },
                    "email": "alice@example.com"
                }
        ),

        # Test case 4: Remove multiple keys in nested and top levels
        (
                {
                    "name": "Alice",
                    "details": {
                        "address": "Wonderland",
                        "notes": "Important notes",
                        "phone": "123-456-7890"
                    },
                    "additional_info": {
                        "languages": ["English", "French"],
                    },
                    "notes": "General notes",
                    "phone": "987-654-3210"
                },
                ["notes", "phone"],  # Remove "notes" and "phone" at all levels
                None,
                {
                    "name": "Alice",
                    "details": {
                        "address": "Wonderland"
                    },
                    "additional_info": {
                        "languages": ["English", "French"],
                    }
                }
        ),

        # Test case 5: Empty input dictionary with remove_keys
        (
                {},
                ["unused_key"],  # Attempt to remove a non-existent key
                None,
                {}
        ),

        # Test case 6: Keep all keys that are not in remove_keys
        (
                {
                    "key1": "value1",
                    "key2": "value2",
                    "key3": "value3",
                    "key4": "value4"
                },
                ["key1", "key3"],  # Remove "key1" and "key3"
                None,
                {
                    "key2": "value2",
                    "key4": "value4"
                }
        ),

        # Test case 7: Remove key with empty value (overrides default behavior)
        (
                {
                    "name": "Alice",
                    "phone": "",
                    "notes": "Important notes",
                    "address": "Wonderland"
                },
                ["phone"],  # Forcibly remove "phone" even though it's empty
                None,
                {
                    "name": "Alice",
                    "notes": "Important notes",
                    "address": "Wonderland"
                }
        ),

        # Test case 8: Deeply nested removal
        (
                {
                    "name": "Alice",
                    "details": {
                        "phone": "123-456-7890",
                        "additional_info": {
                            "languages": ["English", "French"],
                            "preferences": [],
                            "remove_me": "Value to remove"
                        }
                    },
                    "remove_me": "Another value to remove"
                },
                ["remove_me"],  # Remove "remove_me" at all levels
                None,
                {
                    "name": "Alice",
                    "details": {
                        "phone": "123-456-7890",
                        "additional_info": {
                            "languages": ["English", "French"],
                        }
                    }
                }
        ),
    ]
)
def test_clean_dict_remove_keys(data, remove_keys, keep_keys, expected):
    """
    Test the clean_dict function focusing on the behavior of the remove_keys feature
    without overlaps or conflicts with keep_keys.
    """
    result = clean_dict(data, keep_keys=keep_keys, remove_keys=remove_keys)
    assert result == expected


def test_clean_dict_exceptions():
    """
    Test that clean_dict raises appropriate exceptions
    for invalid input or conflicts between parameters.
    """

    # Test case 1: Non-dict input raises Ten8tValueError
    try:
        clean_dict(["not", "a", "dict"])  # Passing a list instead of a dictionary
        assert False, "Not a dictionary"
    except Exception as _:
        assert True

    # Test case 2: Conflicting keys in keep_keys and remove_keys
    conflicting_keep_keys = ["name", "address"]
    conflicting_remove_keys = ["address", "details"]

    # Attempting to use "address" in both keep_keys and remove_keys
    try:
        clean_dict(
            {
                "name": "Alice",
                "address": "Wonderland",
                "details": {"phone": "123-456-7890"}
            },
            keep_keys=conflicting_keep_keys,
            remove_keys=conflicting_remove_keys
        )
        assert False, "Conflicting keys in keep_keys and remove_keys"
    except Exception as _:
        assert True


def test_clean_dict_remove_nulls_behavior():
    """
    Verifies that the clean_dict function correctly removes or retains null/'', [], {} items
    based on the remove_nulls flag.
    """
    # Input dictionary containing null-like values
    input_data = {
        "name": "Alice",
        "empty_string": "",
        "empty_list": [],
        "empty_dict": {},
        "details": {
            "note": "",
            "preferences": [],
            "nested_dict": {
                "unused": {},
            },
            "not_empty": "value"
        },
        "active": True
    }

    # Case 1: remove_nulls=True (default behavior)
    result_with_nulls_removed = clean_dict(input_data, remove_nulls=True)
    expected_output_nulls_removed = {
        "name": "Alice",
        "details": {
            "not_empty": "value"
        },
        "active": True
    }
    assert result_with_nulls_removed == expected_output_nulls_removed, "Null-like values were not removed as expected when remove_nulls=True."

    # Case 2: remove_nulls=False (retain null/'', [], {} items)
    result_with_nulls_retained = clean_dict(input_data, remove_nulls=False)
    expected_output_nulls_retained = {
        "name": "Alice",
        "empty_string": "",
        "empty_list": [],
        "empty_dict": {},
        "details": {
            "note": "",
            "preferences": [],
            "nested_dict": {
                "unused": {}
            },
            "not_empty": "value"
        },
        "active": True
    }
    assert result_with_nulls_retained == expected_output_nulls_retained, "Null-like values were unexpectedly removed when remove_nulls=False."


def test_tuple_cases():
    assert clean_dict({'a': (1, 2, 3)}) == {'a': (1, 2, 3)}
    assert clean_dict({'a': (1, 2, 3), 'b': []}) == {'a': (1, 2, 3)}
    assert clean_dict({'a': (1, 2, 3), 'b': [1]}) == {'a': (1, 2, 3), 'b': [1]}
