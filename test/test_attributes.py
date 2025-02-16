import pytest

import src.ten8t.ten8t_attribute as ten8t_attribute
import src.ten8t.ten8t_exception as ten8t_exception


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
