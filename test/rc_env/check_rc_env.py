"""
DocString for check_env

Verify loading of enviromnet variables
"""
from src.ten8t import TR, categories


@categories(tag='tag1', level=1)
def check_env(env_num, env_str, env_list, env_dict):
    """Test function to verify that various types work correctly from env"""
    yield TR(status=env_num == 1, msg="Result environment number")
    yield TR(status=env_str == "str1", msg="Result environment str")
    yield TR(status=env_list == [1], msg="Result environment list")
    yield TR(status=env_dict == {"1": 1}, msg="Result environment dict")
