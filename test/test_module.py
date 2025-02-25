from ten8t import Ten8tModule
from ten8t import Ten8tModule


def test_module_str():
    """Make sure we can load modules individually and extract the ruids"""
    module = Ten8tModule(module_name="check_suid1_a", module_file='./ruid/check_suid1_a.py')
    assert str(module) == "Ten8tModule(module_name='check_suid1_a',check_function_count=2)"


def test_module_autothread():
    """Make sure we can load modules individually and extract the ruids"""
    module = Ten8tModule(module_name="check_suid1_a", module_file='./ruid/check_suid1_a.py', auto_thread=True)

    for function in module.check_functions:
        assert function.thread_id.startswith(Ten8tModule.AUTO_THREAD_PREFIX)

    # Verify there is only one thread id
    assert len(set(func.thread_id for func in module.check_functions)) == 1


def test_multimodule():
    """Make sure we can load modules individually and extract the ruids"""
    module1 = Ten8tModule(module_name="check_suid1_a", module_file='./ruid/check_suid1_a.py', auto_thread=True)
    module2 = Ten8tModule(module_name="check_suid2_a", module_file='./ruid/check_suid2_a.py', auto_thread=True)

    assert module1.check_function_count == 2
    assert module2.check_function_count == 2

    ch = Ten8tChecker(modules=[module1, module2], auto_setup=True)

    assert ch.collected_count == module1.check_function_count + module2.check_function_count


def test_module_autothread2():
    """Make sure we can load modules individually and extract the ruids"""
    module1 = Ten8tModule(module_name="check_suid1_a", module_file='./ruid/check_suid1_a.py', auto_thread=True)
    module2 = Ten8tModule(module_name="check_suid2_a", module_file='./ruid/check_suid2_a.py', auto_thread=True)

    # This is a pretty crude check, but it is good enough to show that all functions have auto thread ids.
    for module in [module1, module2]:
        for function in module.check_functions:
            assert function.thread_id.startswith(Ten8tModule.AUTO_THREAD_PREFIX)

    # These should be different since the modules were individually auto threaded
    assert module1.check_functions[0].thread_id != module2.check_functions[0].thread_id
