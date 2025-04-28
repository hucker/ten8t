"""
DocString for check_env

Verify loading of enviromnet variables
"""
from src.ten8t import TR, categories


@categories(tag='all_types', level=1)
def check_env1(env_num, env_str, env_list, env_dict):
    """Test function to verify that various types work correctly from env"""
    yield TR(status=env_num == 1, msg="Result environment number")
    yield TR(status=env_str == "str1", msg="Result environment str")
    yield TR(status=env_list == [1], msg="Result environment list")
    yield TR(status=env_dict == {"1": 1}, msg="Result environment dict")


@categories(tag='num_str_types', level=1)
def check_env2(env_num, env_str):
    """
    Test function verifiy operation of enivronment read from INI file

    The INI file only supports numbers and strings, no dicts aor lists are directly supported.
    """
    yield TR(status=int(env_num) == 1, msg="Result environment number")
    yield TR(status=env_str == "str1", msg="Result environment str")
