import pytest

from ten8t import any_to_int_list, any_to_str_list, str_to_bool


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
        r = any_to_int_list(input_param)
        print(r)
