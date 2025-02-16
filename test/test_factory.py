"""
These the rc factory method allowing fairly easily to have various flavors or RC files to
be interchangeable.

"""

import pytest

from src.ten8t import Ten8tException, ten8t_rc_factory


def test_factory():
    """
    Verify that all the factory functions return the same values for files that have the same data.

    This test is sort of a rosetta stone where all the files have the same data in different formats
    and this function verifies that they all return the same thing
    """
    rc_dict = {'package1': {'ruids': 'r1 -r2',
                            'tags': 't1 -t2',
                            'phases': 'p1 -p2'}}

    rc1 = ten8t_rc_factory(param='./rc_files/good.json', section='package1')
    rc2 = ten8t_rc_factory(param='./rc_files/good.toml', section='package1')
    rc3 = ten8t_rc_factory(param=rc_dict, section='package1')
    rc4 = ten8t_rc_factory(param=rc_dict['package1'])
    rc5 = ten8t_rc_factory(param='./rc_files/good.xml', section='package1')
    rc6 = ten8t_rc_factory(param='./rc_files/good.ini', section='package1')

    assert rc1.tags == rc2.tags == rc3.tags == rc4.tags == rc5.tags == rc6.tags == ['t1']
    assert rc1.ruids == rc2.ruids == rc3.ruids == rc4.ruids == rc5.ruids == rc6.ruids == ['r1']
    assert rc1.phases == rc2.phases == rc3.phases == rc4.phases == rc5.phases == rc6.phases == ['p1']
    assert rc1.ex_tags == rc2.ex_tags == rc3.ex_tags == rc4.ex_tags == rc5.ex_tags == rc6.ex_tags == ['t2']
    assert rc1.ex_ruids == rc2.ex_ruids == rc3.ex_ruids == rc4.ex_ruids == rc5.ex_ruids == rc6.ex_ruids == ['r2']
    assert rc1.ex_phases == rc2.ex_phases == rc3.ex_phases == rc4.ex_phases == rc5.ex_phases == rc6.ex_phases == ['p2']


@pytest.mark.parametrize("param", [
    # Factory class expects a file name or a dictionary
    "foo.txt",
    1,
    [],
    set(),
    ()
    # Add more test cases as needed
])
def test_factory_exception(param):
    with pytest.raises(Ten8tException):
        _ = ten8t_rc_factory(param=param, section='')


@pytest.mark.parametrize("param, section",
                         [
                             ('./rc_files/good.ini', None),
                             ('./rc_files/___.toml', None),
                             ('./rc_files/___.xml', None),
                             ('./rc_files/___.json', None),
                             ('./rc_files/___.ini', 'package1'),
                         ])  # Add more test cases here
def test_more_exceptions(param, section):
    with pytest.raises(Ten8tException):
        _ = ten8t_rc_factory(param, section=section)
