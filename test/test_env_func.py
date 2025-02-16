from src import ten8t


def test_funct_env_default():
    """ Test function environment with default value"""

    @ten8t.attributes(tag="Env")
    def func(x, y=2):
        """Test Function"""
        yield ten8t.TR(status=(x == 1 and y == 2), msg="It works")

    env = {"x": 1}
    sfunc = ten8t.Ten8tFunction(func, env=env)

    for result in sfunc():
        assert result.func_name == "func"
        assert result.status is True
        assert result.msg == "It works"
        assert result.doc == "Test Function"
        assert result.skipped is False
        assert result.except_ is None
        assert result.warn_msg == ""
        assert result.info_msg == ""
        assert result.tag == "Env"


def test_func_no_defaults_used():
    """ Test function environment with default value"""

    @ten8t.attributes(tag="Env")
    def func(x=1, y=2, z=3):
        """Test Function"""
        yield ten8t.TR(status=(x == 2 and y == 3 and z == 4), msg="It works")

    env = {"x": 2, 'y': 3, 'z': 4}
    sfunc = ten8t.Ten8tFunction(func, env=env)

    for result in sfunc():
        assert result.func_name == "func"
        assert result.status is True
        assert result.msg == "It works"
        assert result.doc == "Test Function"
        assert result.tag == "Env"


def test_func_no_defaults_used_bad_order():
    """ Test function environment with various default values overriding some of them"""

    @ten8t.attributes(tag="Env")
    def func(x=1, y=2, z=3):
        """Test Function"""
        yield ten8t.TR(status=(x == 1 and y == 2 and z == 4), msg="It works")

    # Always override z and hard code x and y to the default values
    for env in [{'x': 1}, {'y': 2}, {'x': 1, 'y': 2}]:
        env['z'] = 4
        sfunc = ten8t.Ten8tFunction(func, env=env)
        result = next(sfunc())
        assert result.status is True


def test_func_defaults_used():
    """ Test function environment with no default value"""

    @ten8t.attributes(tag="Env")
    def func(x=1, y=2, z=3):
        """Test Function"""
        yield ten8t.TR(status=(x == 1 and y == 2 and z == 3), msg="It works")

    env = {}
    sfunc = ten8t.Ten8tFunction(func, env=env)

    for result in sfunc():
        assert result.func_name == "func"
        assert result.status is True
        assert result.msg == "It works"
        assert result.doc == "Test Function"
        assert result.tag == "Env"


def test_funct_all_values():
    """ Test function all from environment"""

    @ten8t.attributes(tag="Env")
    def func(x=1, y=2, z=3):
        """From Environment"""
        yield ten8t.TR(status=(x == 20 and y == 30 and z == 40), msg="It works")

    env = {"x": 20, 'y': 30, 'z': 40}
    sfunc = ten8t.Ten8tFunction(func, env=env)

    for result in sfunc():
        assert result.func_name == "func"
        assert result.status is True
        assert result.msg == "It works"
        assert result.doc == "From Environment"
        assert result.tag == "Env"
