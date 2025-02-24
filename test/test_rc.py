"""
These test the rc file classes.

This was built adhoc.  It could be setup to thoroughly test the
ten8t_rc code and then  the dictionaries used to initialize the
Ten8tRC class should be written off to JSON and TOML and then the
exact same tests should be run against the derived classes.

"""

import pytest

import ten8t as t8


@pytest.fixture
def test_data():
    d = {
        'tags': ['a', 'b', 'c'],
        'ruids': ['r1', 'r2', 'r3'],
        'phases': ['p1', 'p2', 'p3'],
        'levels': [1, 2, 3]
    }
    return d


def test_simple_summary(test_data):
    rc = t8.Ten8tRC(rc_d=test_data)

    assert rc.tags == ['a', 'b', 'c']
    assert rc.ruids == ['r1', 'r2', 'r3']
    assert rc.phases == ['p1', 'p2', 'p3']
    assert rc.levels == ['1', '2', '3']


@pytest.mark.parametrize(
    "bad_type",
    [
        [1, 2, 3],
        (1, 2, 3),
        {1, 2, 3},
        1,
    ],
)
def test_bad_rcd(bad_type):
    with pytest.raises(t8.Ten8tException) as exec_info:
        _ = t8.Ten8tRC(rc_d=bad_type)


def test_simple_rc(test_data):
    rc = t8.Ten8tRC(rc_d=test_data)
    assert rc.does_match(tag='a')
    assert rc.does_match(ruid='r1')
    assert rc.does_match(phase='p1')
    assert rc.does_match(level='1')
    assert rc.does_match(ruid='r1', phase='p1')
    assert rc.does_match(ruid='r1', level='1')
    assert rc.does_match(ruid='r1', tag='a')
    assert rc.does_match(ruid='r1', tag='a', level='1')
    assert rc.does_match(ruid='r1', tag='a', phase='p1', level='1')


def test_simple_fail_rc(test_data):
    rc = t8.Ten8tRC(rc_d=test_data)

    assert rc.does_match(tag='d') is False
    assert rc.does_match(ruid='r4') is False
    assert rc.does_match(phase='p4') is False
    assert rc.does_match(level='4') is False


def test_regex_rc(test_data):
    rc = t8.Ten8tRC(rc_d={'ruids': 'r.*'})

    assert rc.does_match(ruid='r1')
    assert rc.does_match(ruid='r2')
    assert rc.does_match(ruid='rasdfasdfasdf')

    rc = t8.Ten8tRC(rc_d={'ruids': r'r\d', 'phases': r'p\d'})

    assert rc.does_match(ruid='r1', phase='p1')
    assert rc.does_match(ruid='r2', phase='p2')
    assert rc.does_match(ruid='r22', phase='p2') is False
    assert rc.does_match(ruid='r2', phase='p22') is False

    rc = t8.Ten8tRC(rc_d={'ruids': r'r\d+', 'phases': r'p\d+'})
    assert rc.does_match(ruid='r12', phase='p1')
    assert rc.does_match(ruid='r2', phase='p22')


@pytest.mark.parametrize("rules, ruid, phase, tag, expected", [
    # Cases for 'ruids' rule
    ({'ruids': 'r.*'}, 'r1', '', '', True),
    ({'ruids': 'r.*'}, 'r2', '', '', True),
    ({'ruids': 'r.*'}, 'rasdfasdfasdf', '', '', True),
    # Cases for 'ruids' and 'phases' rules
    ({'ruids': r'r\d', 'phases': r'p\d'}, 'r1', 'p1', '', True),
    ({'ruids': r'r\d', 'phases': r'p\d'}, 'r2', 'p2', '', True),
    ({'ruids': r'r\d', 'phases': r'p\d'}, 'r22', 'p2', '', False),
    ({'ruids': r'r\d', 'phases': r'p\d'}, 'r2', 'p22', '', False),
    # Cases for 'ruids' and 'phases' rules with multiple-digits
    ({'ruids': r'r\d+', 'phases': r'p\d+'}, 'r12', 'p1', '', True),
    ({'ruids': r'r\d+', 'phases': r'p\d+'}, 'r2', 'p22', '', True),
    # Optionally, add cases for 'tags' rule as well
    ({'tags': 't.*'}, '', '', 't1', True),
    ({'tags': 't.*'}, '', '', 't_example', True),
    # New test cases where 'tag' doesn't match the rules
    ({'tags': r't\d'}, '', '', 't1', True),  # matches because the tag 't1' fits the rule 't\d'
    ({'tags': r't\d'}, '', '', 't', False),  # no digit after 't', so it doesn't match 't\d'
    ({'tags': r't\d'}, '', '', 'tag', False),  # 'tag' doesn't fit the rule 't\d'
    ({'tags': 't.*'}, '', '', 'tag1', True),  # matches because the rule 't.*' fits any string starting with 't'
    ({'tags': 't.*'}, '', '', '1tag', False),

])
def test_regex_fixture_rc(rules, ruid, phase, tag, expected):
    rc = t8.Ten8tRC(rc_d=rules)
    assert rc.does_match(ruid=ruid, phase=phase, tag=tag) is expected


@pytest.mark.parametrize("rules, ruid, phase, tag, expected", [
    # Test cases for 'ruids'
    ({'ruids': 'r.*'}, 'r1', '', '', True),
    ({'ruids': 'r.*'}, 'r2', '', '', True),
    ({'ruids': 'r.*'}, 'rasdfasdfasdf', '', '', True),
    ({'ruids': r'r\d'}, 'r1', '', '', True),
    ({'ruids': r'r\d'}, 'r2', '', '', True),
    ({'ruids': r'r\d'}, 'r22', '', '', False),
    ({'ruids': r'r\d'}, 'r22', '', '', False),
    ({'ruids': 'r'}, 'r22', '', '', False),
    # Test cases for 'phases'
    ({'phases': 'p.*'}, '', 'p1', '', True),
    ({'phases': 'p.*'}, '', 'p2', '', True),
    ({'phases': 'p.*'}, '', 'pasdfasdfasdf', '', True),
    ({'phases': r'p\d'}, '', 'p1', '', True),
    ({'phases': r'p\d'}, '', 'p2', '', True),
    ({'phases': r'p\d'}, '', 'p22', '', False),
    ({'phases': 'p'}, '', 'p22', '', False),
    # Test cases for 'tags'
    ({'tags': 't.*'}, '', '', 't1', True),
    ({'tags': 't.*'}, '', '', 't_example', True),
    ({'tags': r't\d'}, '', '', 't1', True),
    ({'tags': r't\d'}, '', '', 't', False),
    ({'tags': r't\d'}, '', '', 'tag', False),
    ({'tags': 't.*'}, '', '', 'tag1', True),
    ({'tags': 't.*'}, '', '', '1tag', False),
    ({'tags': 't'}, '', '', '1tag', False),
    # Combined test cases (Assuming 'does_match' checks if any rule matches)
    # (Matches 'ruids' but not 'phases' and 'tags', so expected is True)
    ({'ruids': r'r\d', 'phases': r'p\d', 'tags': r't\d'}, 'r1', 'p', 't', False),
    ({'ruids': r'r\d', 'phases': r'p\d', 'tags': r't\d'}, 'r', 'p1', 't', False),
    ({'ruids': r'r\d', 'phases': r'p\d', 'tags': r't\d'}, 'r', 'p', 't1', False),
    ({'ruids': r'r\d', 'phases': r'p\d', 'tags': r't\d'}, 'r1', 'p1', 't1', True),
])
def test_regex_big_rc(rules, ruid, phase, tag, expected):
    rc = t8.Ten8tRC(rc_d=rules)
    assert rc.does_match(ruid=ruid, phase=phase, tag=tag) is expected


@pytest.mark.parametrize("rules, level, expected", [
    # Test cases for 'levels'
    ({'levels': '1|2'}, '1', True),
    ({'levels': '1|2|3'}, '2', True),
])
def test_regex_rc_2(rules, level, expected):
    rc = t8.Ten8tRC(rc_d=rules)
    assert rc.does_match(level=level) is expected


def test_neg():
    rc = t8.Ten8tRC(rc_d={'tags': ['t1', '-t2'],
                          'ruids': ['r1', '-r2'],
                          'phases': 'p1,-p2'})

    assert rc.does_match(tag='t1')
    assert rc.does_match(tag='t2') is False
    assert rc.does_match(ruid='r1')
    assert rc.does_match(ruid='r2') is False
    assert rc.does_match(phase='p1')
    assert rc.does_match(phase='p2') is False

    assert rc.does_match(phase='p1', ruid='r1', tag='t2') is False
    assert rc.does_match(phase='p1', ruid='r1', tag='t1') is True
