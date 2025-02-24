"""DocString for check_dec_complex"""
import pandas as pd

from src import ten8t as t8

""" In this example we have a more complex decorator structure where
    we have 3 levels of decorators.  The decorators are applied to
    the functions in the following way:

    1) There is 1 tag for each function
    2) There is 1 at level 1
    3) There are 2 at level 2
    4) There are 3 at level 3

    This allows us to test the filtering by tags and levels.
"""

CONST_DB_CONFIG = "cfg.json"
CONST_NUMBER_CONFIG = 42


def env_setup(_: dict) -> dict:
    # TODO: the _ dict should be a frozen dict.
    # The dict passed in is the top level environment setup.  This
    # data should be considered read only.  Frozen doesn't really help
    # because you can change the contents of mutable data.

    module_env = {}
    module_env['db_config'] = CONST_DB_CONFIG
    module_env['number_config'] = CONST_NUMBER_CONFIG
    module_env['data_frame'] = pd.DataFrame()

    return module_env


def check_global(global_env):
    """ In order for this test to work the environment
    must be loaded with the values global_env="hello" """

    yield t8.Ten8tResult(status=global_env == "hello", msg=f"Got global env={global_env}")


def check_env1(db_config):
    """Should pick up db config from local env"""
    yield t8.Ten8tResult(status=db_config == CONST_DB_CONFIG, msg="DB config is correct")


def check_env2(number_config):
    """Should pick up number_config from local_env"""
    yield t8.Ten8tResult(status=number_config == CONST_NUMBER_CONFIG,
                         msg=f"Numeric config is correct {number_config}")


def check_env3(data_frame):
    """ Should pickup dataframe from local config"""
    yield t8.Ten8tResult(status=isinstance(data_frame, pd.DataFrame), msg="Data_frame is actually a dataframe.")
    yield t8.Ten8tResult(status=data_frame.empty is True, msg="Dataframe is empty")


def check_check_lots_of_stuff(db_config, number_config, global_env, data_frame):
    """Should pick them all up """
    yield t8.Ten8tResult(status=db_config == CONST_DB_CONFIG, msg="DB config is correct")
    yield t8.Ten8tResult(status=number_config == CONST_NUMBER_CONFIG,
                         msg=f"Numeric config is correct {number_config}")
    yield t8.Ten8tResult(status=isinstance(data_frame, pd.DataFrame), msg="Data_frame is actually a dataframe.")
    yield t8.Ten8tResult(status=data_frame.empty is True, msg="Dataframe is empty")
    yield t8.Ten8tResult(status=global_env == "hello", msg=f"Got global env={global_env}")


def check_order_doesnt_matter(number_config, data_frame, db_config, global_env):
    """Should pick them all up in different order """
    yield t8.Ten8tResult(status=db_config == CONST_DB_CONFIG, msg="DB config is correct")
    yield t8.Ten8tResult(status=number_config == CONST_NUMBER_CONFIG,
                         msg=f"Numeric config is correct {number_config}")
    yield t8.Ten8tResult(status=isinstance(data_frame, pd.DataFrame), msg="Data_frame is actually a dataframe.")
    yield t8.Ten8tResult(status=data_frame.empty is True, msg="Dataframe is empty")
    yield t8.Ten8tResult(status=global_env == "hello", msg=f"Got global env={global_env}")
