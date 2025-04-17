import pathlib

import pytest

from ten8t import Ten8tChecker
from ten8t import Ten8tModule


@pytest.mark.parametrize(
    "module_file",
    [
        './ruid/check_suid1_a.py',  # Test case with string
        pathlib.Path('./ruid/check_suid1_a.py'),  # Test case with pathlib.Path
    ]
)
def test_module_loading(module_file):
    """Ensure we can load modules and extract the correct ruids."""
    module = Ten8tModule(module_name="check_suid1_a", module_file=module_file)
    assert str(module) == "Ten8tModule(module_name='check_suid1_a',check_function_count=2)"


def test_module_autothread():
    """Make sure we can load modules individually and extract the ruids"""
    module = Ten8tModule(module_name="check_suid1_a", module_file='./ruid/check_suid1_a.py', auto_thread=True)

    for function in module.check_functions:
        assert function.thread_id.startswith(Ten8tModule.AUTO_THREAD_PREFIX)

    # Verify there is only one thread id
    assert len(set(func.thread_id for func in module.check_functions)) == 1


@pytest.mark.parametrize(
    "module_file1, module_file2",
    [  # Test case with string file paths
        ('./ruid/check_suid1_a.py', './ruid/check_suid2_a.py'),
        # Test case with pathlib.Path objects
        (pathlib.Path('./ruid/check_suid1_a.py'), pathlib.Path('./ruid/check_suid2_a.py')),
    ]
)
def test_multimodule(module_file1, module_file2):
    """Ensure we can load multiple modules and extract the correct ruids."""
    module1 = Ten8tModule(module_name="check_suid1_a", module_file=module_file1, auto_thread=True)
    module2 = Ten8tModule(module_name="check_suid2_a", module_file=module_file2, auto_thread=True)

    assert module1.check_function_count == 2
    assert module2.check_function_count == 2

    ch = Ten8tChecker(modules=[module1, module2])

    assert ch.collected_count == module1.check_function_count + module2.check_function_count


@pytest.mark.parametrize(
    "module_file1, module_file2",
    [
        # Test case using string file paths
        ('./ruid/check_suid1_a.py', './ruid/check_suid2_a.py'),
        # Test case using pathlib.Path objects
        (pathlib.Path('./ruid/check_suid1_a.py'), pathlib.Path('./ruid/check_suid2_a.py')),
    ]
)
def test_module_autothread2(module_file1, module_file2):
    """Ensure we can load modules, auto-assign thread IDs, and assign unique IDs for different modules."""
    module1 = Ten8tModule(module_name="check_suid1_a", module_file=module_file1, auto_thread=True)
    module2 = Ten8tModule(module_name="check_suid2_a", module_file=module_file2, auto_thread=True)

    # Ensure all check functions in both modules have thread IDs starting with the auto-thread prefix
    for module in [module1, module2]:
        for function in module.check_functions:
            assert function.thread_id.startswith(Ten8tModule.AUTO_THREAD_PREFIX)

    # Ensure that thread IDs between the modules are unique
    assert module1.check_functions[0].thread_id != module2.check_functions[0].thread_id
