"""
Public API for the Ten8t project.
"""
from importlib.metadata import PackageNotFoundError, version

# Checker Overview Output
from .overview import Ten8tMarkdownOverview
from .overview import Ten8tStreamlitOverview
from .overview import Ten8tTextOverview
# Some simple progress indicators.
from .progress import Ten8tDebugProgress  # noqa: F401
from .progress import Ten8tLogProgress  # noqa: F401
from .progress import Ten8tMultiProgress  # noqa: F401
from .progress import Ten8tNoProgress  # noqa: F401
from .progress import Ten8tProgress  # noqa: F401
# Resource File Support
from .rc import Ten8tIniRC  # noqa: F401
from .rc import Ten8tJsonRC  # noqa: F401
from .rc import Ten8tRC  # noqa: F401
from .rc import Ten8tTomlRC  # noqa: F401
from .rc import Ten8tXMLRC  # noqa: F401
from .rc import ten8t_rc_factory  # noqa: F401
# Built-in render engines (single line results)
from .render import TM  # noqa: F401
from .render import Ten8tAbstractRenderer  # noqa: F401
from .render import Ten8tBasicHTMLRenderer  # noqa: F401
from .render import Ten8tBasicMarkdownRenderer  # noqa: F401
from .render import Ten8tBasicRichRenderer  # noqa: F401
from .render import Ten8tBasicStreamlitRenderer  # noqa: F401
from .render import Ten8tGitHubMarkdownRenderer  # noqa: F401
from .render import Ten8tMarkup  # noqa: F401
from .render import Ten8tRendererFactory  # noqa: F401
from .render import Ten8tRendererProtocol  # noqa: F401
from .render import Ten8tTextRenderer  # noqa: F401
# This set of rules has no dependencies, so it should always be available
# it supports loading results using the json output from running a checker instance.
from .rule_ten8t import rule_ten8t_json_file, rule_ten8t_json_files
# Schedule Support
from .schedule import Ten8tBaseSchedule  # noqa: F401
from .schedule import Ten8tCompositeSchedule  # noqa: F401
from .schedule import Ten8tCronSchedule  # noqa: F401
from .schedule import Ten8tIntersectionSchedule  # noqa: F401
from .schedule import Ten8tInverseSchedule  # noqa: F401
from .schedule import Ten8tNthWeekdaySchedule  # noqa: F401
from .schedule import Ten8tTTLSchedule  # noqa: F401
from .schedule import Ten8tWeekdaySchedule  # noqa: F401
from .schedule import Ten8tWeekendSchedule  # noqa: F401
from .score import ScoreBinaryFail  # noqa: F401
# Scoring Support
from .score import ScoreBinaryPass  # noqa: F401
from .score import ScoreByFunctionBinary  # noqa: F401
from .score import ScoreByFunctionMean  # noqa: F401
from .score import ScoreByResult  # noqa: F401
from .score import ScoreStrategy  # noqa: F401
from .score import get_registered_strategies  # noqa: F401
from .score import get_strategy_class  # noqa: F401
from .score import register_score_class  # noqa: F401
from .score import reset_score_strategy_registry  # noqa: F401
# Serialization to file
from .serialize import Ten8tDump  # noqa: F401
from .serialize import Ten8tDumpCSV  # noqa: F401
from .serialize import Ten8tDumpConfig  # noqa: F401
from .serialize import Ten8tDumpExcel  # noqa: F401
from .serialize import Ten8tDumpHTML  # noqa: F401
from .serialize import Ten8tDumpMarkdown  # noqa: F401
from .serialize import Ten8tDumpSQLite  # noqa: F401
from .serialize import ten8t_save_csv  # noqa: F401
from .serialize import ten8t_save_md  # noqa: F401
from .serialize import ten8t_save_xls  # noqa: F401
from .ten8t_attribute import attempts  # noqa: F401
from .ten8t_attribute import attributes  # noqa: F401
from .ten8t_attribute import caching  # noqa: F401
from .ten8t_attribute import categories  # noqa: F401
from .ten8t_attribute import control  # noqa: F401
from .ten8t_attribute import get_attribute  # noqa: F401
from .ten8t_attribute import score  # noqa: F401
from .ten8t_attribute import threading  # noqa: F401
from .ten8t_checker import Ten8tChecker  # noqa: F401
from .ten8t_exception import Ten8tException  # noqa: F401
from .ten8t_filter import exclude_levels  # noqa: F401
from .ten8t_filter import exclude_phases  # noqa: F401
from .ten8t_filter import exclude_ruids  # noqa: F401
from .ten8t_filter import exclude_tags  # noqa: F401
from .ten8t_filter import keep_levels  # noqa: F401
from .ten8t_filter import keep_phases  # noqa: F401
from .ten8t_filter import keep_ruids  # noqa: F401
from .ten8t_filter import keep_tags  # noqa: F401
from .ten8t_function import Ten8tFunction  # noqa: F401
from .ten8t_immutable import Ten8tEnvDict  # noqa: F401
from .ten8t_immutable import Ten8tEnvList  # noqa: F401
from .ten8t_immutable import Ten8tEnvSet  # noqa: F401
from .ten8t_import import _install  # noqa: F401
from .ten8t_import import installed_ten8t_packages  # noqa: F401
from .ten8t_import import is_installed  # noqa: F401
from .ten8t_import import whats_installed  # noqa: F401
from .ten8t_logging import ten8t_logger  # noqa: F401
from .ten8t_logging import ten8t_reset_logging  # noqa: F401
from .ten8t_logging import ten8t_setup_logging  # noqa: F401
from .ten8t_module import Ten8tModule  # noqa: F401
from .ten8t_package import Ten8tPackage  # noqa: F401
from .ten8t_result import TR  # noqa: F401
from .ten8t_result import Ten8tResult  # noqa: F401
from .ten8t_result import Ten8tResultDictFilter  # noqa: F401
from .ten8t_result import group_by  # noqa: F401
from .ten8t_result import overview  # noqa: F401
from .ten8t_ruid import empty_ruids  # noqa: F401
from .ten8t_ruid import module_ruids  # noqa: F401
from .ten8t_ruid import package_ruids  # noqa: F401
from .ten8t_ruid import ruid_issues  # noqa: F401
from .ten8t_ruid import valid_ruids  # noqa: F401
from .ten8t_thread import Ten8tThread  # noqa: F401
from .ten8t_util import IntList  # noqa: F401
from .ten8t_util import IntListOrNone  # noqa: F401
from .ten8t_util import IntOrNone  # noqa: F401
from .ten8t_util import ListOrNone  # noqa: F401
from .ten8t_util import StrList  # noqa: F401
from .ten8t_util import StrListOrNone  # noqa: F401
from .ten8t_util import StrOrNone  # noqa: F401
from .ten8t_util import StrOrPath  # noqa: F401
from .ten8t_util import StrOrPathList  # noqa: F401
from .ten8t_util import StrOrPathListOrNone  # noqa: F401
from .ten8t_util import StrOrPathOrNone  # noqa: F401
from .ten8t_util import Ten8tResultOrNone  # noqa: F401
from .ten8t_util import any_to_int_list  # noqa: F401
from .ten8t_util import any_to_path_list  # noqa: F401
from .ten8t_util import any_to_str_list  # noqa: F401
from .ten8t_util import clean_dict  # noqa: F401
from .ten8t_util import cwd_here  # noqa: F401
from .ten8t_util import next_int_value  # noqa: F401
from .ten8t_util import str_to_bool  # noqa: F401
from .ten8t_yield import Ten8tNoResultSummary  # noqa: F401
from .ten8t_yield import Ten8tYield  # noqa: F401
from .ten8t_yield import Ten8tYieldAll  # noqa: F401
from .ten8t_yield import Ten8tYieldFailOnly  # noqa: F401
from .ten8t_yield import Ten8tYieldPassFail  # noqa: F401
from .ten8t_yield import Ten8tYieldPassOnly  # noqa: F401
from .ten8t_yield import Ten8tYieldSummaryOnly  # noqa: F401

_install("ten8t_result")

try:
    import pathlib  # noqa: F401

    _install("pathlib")
    from .rule_pathlib import rule_large_files  # noqa: F401
    from .rule_pathlib import rule_max_files  # noqa: F401
    from .rule_pathlib import rule_path_exists  # noqa: F401
    from .rule_pathlib import rule_paths_exist  # noqa: F401
    from .rule_pathlib import rule_stale_files  # noqa: F401

except ImportError:
    _install("pathlib", installed=False)

try:
    import narwhals as nw

    from .rule_ndf import extended_bool  # noqa: F401
    from .rule_ndf import rule_ndf_columns_check  # noqa: F401
    from .rule_ndf import rule_validate_ndf_schema  # noqa: F401
    from .rule_ndf import rule_validate_ndf_values_by_col  # noqa: F401

    _install("narwhals")
except ImportError:
    _install("narwhals", installed=False)

# webapi using requests
try:
    import requests

    from .rule_webapi import rule_url_200  # noqa: F401
    from .rule_webapi import rule_web_api  # noqa: F401

    _install("requests")
except ImportError:
    _install("requests", installed=False)

# ping rules
try:
    import ping3

    from .rule_ping import rule_ping_host_check  # noqa: F401
    from .rule_ping import rule_ping_hosts_check  # noqa: F401

    _install("ping")
except ImportError:
    _install("ping", installed=False)

# xlsx rules
try:
    import openpyxl

    from .rule_xlsx import rule_xlsx_a1_pass_fail  # noqa: F401
    from .rule_xlsx import rule_xlsx_df_pass_fail  # noqa: F401

    _install("openpyxl")
except ImportError:
    _install("openpyxl", installed=False)

# pdf rules
try:
    import camelot  # type: ignore
    import pandas as pd  # pylint: disable=ungrouped-imports

    from .rule_pdf import extract_tables_from_pdf  # noqa: F401
    from .rule_pdf import rule_from_pdf_rule_ids  # noqa: F401

    _install("pdf")
except ImportError:
    _install("pdf", installed=False)

# sql alchemy support
try:
    import sqlalchemy

    from .rule_sqlachemy import rule_sql_table_col_name_schema  # noqa: F401
    from .rule_sqlachemy import rule_sql_table_schema  # noqa: F401

    _install("sqlalchemy")
except ImportError:
    _install("sqlalchemy", installed=False)

try:
    import warnings

    # Suppress DeprecationWarning only during `fs` module import
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        import fs  # noqa: F401

    from .rule_fs import rule_fs_file_within_max_size  # noqa: F401
    from .rule_fs import rule_fs_oldest_file_age  # noqa: F401
    from .rule_fs import rule_fs_path_exists  # noqa: F401
    from .rule_fs import rule_fs_paths_exist  # noqa: F401

    _install("fs")
except ImportError:
    _install("fs", installed=False)

try:
    __version__ = version("ten8t")  # Replace with the actual package name in pyproject.toml
except PackageNotFoundError:
    __version__ = "unknown"  # Fallback if version can't be found
