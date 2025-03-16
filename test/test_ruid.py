import sys

import pytest

from src import ten8t as t8


@pytest.fixture(scope="function")
def sys_path():
    """
    Prevent sys.path from being modified by tests.

    This is a case where you should @pytest.mark.usefixtures("sys_path")
    at the top of each function that can modify sys.path. This will ensure
    that sys.path is reset after each test and prevent warnings
    about sys_path not being used.
    """
    original_sys_path = sys.path.copy()
    yield
    sys.path = original_sys_path


@pytest.mark.usefixtures("sys_path")
def test_ruid1():
    """Normal case all RUIDS are unique"""
    pkg = t8.Ten8tPackage(folder="./ruid", name="ruid")

    ruids = pkg.ruids()

    assert ruids == ["suid11", "suid12", "suid21", "suid22"]
    assert t8.valid_ruids(ruids)
    assert t8.ruid_issues(ruids) == "No issues found."
    assert t8.package_ruids(pkg) == ["suid11", "suid12", "suid21", "suid22"]
    assert t8.module_ruids(pkg.modules[0]) == ["suid11", "suid12"]
    assert t8.module_ruids(pkg.modules[1]) == ["suid21", "suid22"]


def test_ruids1_module_str():
    """Make sure we can load modules individually and extract the ruids"""
    module = t8.Ten8tModule(module_name="check_suid1_a", module_file='./ruid/check_suid1_a.py')
    assert str(module) == "Ten8tModule(module_name='check_suid1_a',check_function_count=2)"


def test_ruids1_module1():
    """Make sure we can load modules individually and extract the ruids"""
    module = t8.Ten8tModule(module_name="check_suid1_a", module_file='./ruid/check_suid1_a.py')
    assert module.module_name == "check_suid1_a"
    assert module.module_file == "./ruid/check_suid1_a.py"
    assert set(module.ruids()) == {"suid11", "suid12"}

    module = t8.Ten8tModule(module_name="check_suid2_a", module_file='./ruid/check_suid2_a.py')
    assert module.module_name == "check_suid2_a"
    assert module.module_file == "./ruid/check_suid2_a.py"
    assert set(module.ruids()) == {"suid21", "suid22"}


def test_ruids1_module2():
    """Make sure we can load modules individually and extract the ruids"""
    module = t8.Ten8tModule(module_name="check_suid1_a", module_file='./ruid/check_suid1_a.py')
    assert module.module_name == "check_suid1_a"
    assert module.module_file == "./ruid/check_suid1_a.py"
    assert set(module.ruids()) == {"suid11", "suid12"}

    module = t8.Ten8tModule(module_name="check_suid2_a", module_file='./ruid/check_suid2_a.py')
    assert module.module_name == "check_suid2_a"
    assert module.module_file == "./ruid/check_suid2_a.py"
    assert set(module.ruids()) == {"suid21", "suid22"}


@pytest.mark.usefixtures("sys_path")
def test_run_ruid_1():
    """Normal case all RUIDS are unique"""
    pkg = t8.Ten8tPackage(folder="./ruid", name="ruid")
    ch = t8.Ten8tChecker(packages=pkg)

    _ = ch.run_all()

    ruids = pkg.ruids()

    assert ruids == ["suid11", "suid12", "suid21", "suid22"]
    assert t8.valid_ruids(ruids)
    assert t8.ruid_issues(ruids) == "No issues found."


@pytest.mark.usefixtures("sys_path")
def test_run_package_in_list():
    """This is a check to verify that packages can be passed in a list"""
    pkg = t8.Ten8tPackage(folder="./ruid", name="ruid")
    ch = t8.Ten8tChecker(packages=[pkg])

    _ = ch.run_all()

    ruids = pkg.ruids()

    assert ruids == ["suid11", "suid12", "suid21", "suid22"]
    assert t8.valid_ruids(ruids)
    assert t8.ruid_issues(ruids) == "No issues found."


@pytest.mark.usefixtures("sys_path")
def test_ruid_dup():
    """Load up a package with duplicate RUIDS to verify exception"""
    with pytest.raises(t8.Ten8tException, match="Duplicate RUIDs found in module: suid12"):
        t8.Ten8tPackage(folder="./ruid_dup", name="ruid_dup")


@pytest.mark.usefixtures("sys_path")
def test_no_ruid():
    """Load a package that has no RUIDS"""
    pkg = t8.Ten8tPackage(folder="./ruid_empty", name="ruid_empty")

    ruids = pkg.ruids()

    # This package doesn't have RUIDS so all 4 should be empty
    assert ruids == ["", "", "", ""]

    # Now check
    assert pkg.name == 'ruid_empty'
    assert t8.empty_ruids(ruids) is True
    assert t8.valid_ruids(ruids) is False
    assert t8.ruid_issues(ruids) == "RUIDS are not used."


def test_missing_ruids():
    ruids = ["", "foo"]

    # Now check
    assert t8.empty_ruids(ruids) is False
    assert t8.valid_ruids(ruids) is False
    assert t8.ruid_issues(ruids) == "Blank RUIDs are present."
