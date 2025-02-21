"""
Public API for the Ten8t project.
"""
from .rule_files import rule_large_files  # noqa: F401
from .rule_files import rule_max_files  # noqa: F401
from .rule_files import rule_path_exists  # noqa: F401
from .rule_files import rule_paths_exist  # noqa: F401
from .rule_files import rule_stale_files  # noqa: F401
from .ten8t_attribute import attributes  # noqa: F401
from .ten8t_attribute import get_attribute  # noqa: F401
# from .ten8t_attribute import _convert_to_minutes # noqa:F401
from .ten8t_checker import Ten8tChecker  # noqa: F401
from .ten8t_checker import Ten8tDebugProgress  # noqa; F401
from .ten8t_checker import Ten8tNoProgress  # noqa; F401
from .ten8t_checker import Ten8tProgress  # noqa: F401
from .ten8t_checker import exclude_levels  # noqa: F401
from .ten8t_checker import exclude_phases  # noqa: F401
from .ten8t_checker import exclude_ruids  # noqa: F401
from .ten8t_checker import exclude_tags  # noqa: F401
from .ten8t_checker import keep_levels  # noqa: F401
from .ten8t_checker import keep_phases  # noqa: F401
from .ten8t_checker import keep_ruids  # noqa: F401
from .ten8t_checker import keep_tags  # noqa: F401
from .ten8t_exception import Ten8tException  # noqa: F401
from .ten8t_format import BM
from .ten8t_format import Ten8tBasicHTMLRenderer
from .ten8t_format import Ten8tBasicMarkdown
from .ten8t_format import Ten8tBasicRichRenderer
from .ten8t_format import Ten8tBasicStreamlitRenderer
from .ten8t_format import Ten8tMarkup
from .ten8t_format import Ten8tRenderText
# from .ten8t_exception import Ten8tTypeError  # noqa: F401
# from .ten8t_exception import Ten8tValueError  # noqa: F401
from .ten8t_function import Ten8tFunction  # noqa: F401
from .ten8t_immutable import Ten8tEnvDict  # noqa: F401
from .ten8t_immutable import Ten8tEnvList  # noqa: F401
from .ten8t_immutable import Ten8tEnvSet  # noqa: F401
from .ten8t_jsonrc import Ten8tJsonRC  # noqa: F401
from .ten8t_logging import ten8t_logger  # noqa: F401
from .ten8t_logging import ten8t_reset_logging  # noqa: F401
from .ten8t_logging import ten8t_setup_logging  # noqa: F401
from .ten8t_module import Ten8tModule  # noqa: F401
from .ten8t_package import Ten8tPackage  # noqa: F401
from .ten8t_rc import Ten8tRC  # noqa: F401
from .ten8t_rc_factory import ten8t_rc_factory  # noqa:F401
from .ten8t_result import TR  # noqa: F401
from .ten8t_result import Ten8tResult  # noqa: F401
from .ten8t_result import Ten8tYield  # noqa: F401
from .ten8t_result import overview  # noqa: F401
from .ten8t_ruid import empty_ruids  # noqa: F401
from .ten8t_ruid import module_ruids  # noqa: F401
from .ten8t_ruid import package_ruids  # noqa: F401
from .ten8t_ruid import ruid_issues  # noqa: F401
from .ten8t_ruid import valid_ruids  # noqa: F401
from .ten8t_score import ScoreBinaryFail  # noqa: F401
from .ten8t_score import ScoreBinaryPass  # noqa: F401
from .ten8t_score import ScoreByFunctionBinary  # noqa: F401
from .ten8t_score import ScoreByFunctionMean  # noqa: F401
from .ten8t_score import ScoreByResult  # noqa: F401
from .ten8t_score import ScoreStrategy  # noqa: F401
from .ten8t_thread import Ten8tThread  # noqa: F401
from .ten8t_tomlrc import Ten8tTomlRC  # noqa: F401
from .ten8t_util import any_to_int_list  # noqa: F401
from .ten8t_util import any_to_str_list  # noqa: F401
from .ten8t_util import str_to_bool  # noqa: F401

try:
    import narwhals as nw
    from .rule_ndf import rule_validate_ndf_schema  # noqa: F401
    from .rule_ndf import rule_validate_ndf_values_by_col  # noqa: F401
    from .rule_ndf import rule_ndf_columns_check  # noqa: F401
    from .rule_ndf import extended_bool  # noqa: F401
except ImportError:
    pass

# webapi using requests
try:
    import requests
    from .rule_webapi import rule_url_200  # noqa: F401
    from .rule_webapi import rule_web_api  # noqa: F401
except ImportError:
    pass

# ping rules
try:
    import ping3
    from .rule_ping import rule_ping_check  # noqa: F401
except ImportError:
    pass

# xlsx rules
try:
    import openpyxl
    from .rule_xlsx import rule_xlsx_a1_pass_fail
    from .rule_xlsx import rule_xlsx_df_pass_fail
except ImportError:
    pass

# pdf rules
try:
    import camelot  # type: ignore
    import pandas as pd  # pylint: disable=ungrouped-imports
    from .rule_pdf import extract_tables_from_pdf  # noqa: F401
    from .rule_pdf import rule_from_pdf_rule_ids  # noqa: F401
except ImportError:
    pass

# sql alchemy support
try:
    import sqlalchemy
    from .rule_sqlachemy import rule_sql_table_col_name_schema
    from .rule_sqlachemy import rule_sql_table_schema
except ImportError:
    pass
