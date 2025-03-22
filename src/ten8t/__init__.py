"""
Public API for the Ten8t project.
"""
from importlib.metadata import PackageNotFoundError, version

from .render import (BM, TAG_ACTUAL, TAG_BLACK, TAG_BLUE, TAG_BOLD, TAG_CODE, TAG_DATA, TAG_EXPECTED, TAG_FAIL,
                     TAG_GREEN, TAG_ITALIC, TAG_ORANGE, TAG_PASS, TAG_PURPLE, TAG_RED, TAG_SKIP, TAG_STRIKETHROUGH,
                     TAG_UNDERLINE, TAG_WARN, TAG_WHITE, TAG_YELLOW, Ten8tBasicHTMLRenderer, Ten8tBasicMarkdownRenderer,
                     Ten8tBasicRichRenderer, Ten8tBasicStreamlitRenderer, Ten8tMarkup, Ten8tTextRenderer)
# Import and re-export symbols from sub packages
from .serialize import (Ten8tDump, Ten8tDumpCSV, Ten8tDumpConfig, Ten8tDumpMarkdown, ten8t_save_csv, ten8t_save_md)
# This depends on pathlib which should always be there so
# there is no need to try to import the dependency before
# exporting these rules.
from .ten8t_attribute import DEFAULT_THREAD_ID
from .ten8t_attribute import attributes  # noqa: F401
from .ten8t_attribute import get_attribute  # noqa: F401
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
from .ten8t_jsonrc import Ten8tJsonRC  # noqa: F401
from .ten8t_logging import ten8t_logger  # noqa: F401
from .ten8t_logging import ten8t_reset_logging  # noqa: F401
from .ten8t_logging import ten8t_setup_logging  # noqa: F401
from .ten8t_module import Ten8tModule  # noqa: F401
from .ten8t_package import Ten8tPackage  # noqa: F401
from .ten8t_progress import Ten8tDebugProgress  # noqa: F401
from .ten8t_progress import Ten8tLogProgress  # noqa: F401
from .ten8t_progress import Ten8tMultiProgress  # noqa: F401
from .ten8t_progress import Ten8tNoProgress  # noqa: F401
from .ten8t_progress import Ten8tProgress  # noqa: F401
from .ten8t_rc import Ten8tRC  # noqa: F401
from .ten8t_rc_factory import ten8t_rc_factory  # noqa:F401
from .ten8t_result import TR  # noqa: F401
from .ten8t_result import Ten8tResult  # noqa: F401
from .ten8t_result import group_by  # noqa: F401
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
from .ten8t_score import register_score_class  # noqa: F401
from .ten8t_score import reset_score_strategy_registry
from .ten8t_thread import Ten8tThread  # noqa: F401
from .ten8t_tomlrc import Ten8tTomlRC  # noqa: F401
from .ten8t_util import IntList  # noqa: F401
from .ten8t_util import IntListOrNone  # noqa: F401
from .ten8t_util import IntOrNone  # noqa: F401
from .ten8t_util import StrList  # noqa: F401
from .ten8t_util import StrListOrNone  # noqa: F401
from .ten8t_util import StrOrNone  # noqa: F401
from .ten8t_util import any_to_int_list  # noqa: F401
from .ten8t_util import any_to_str_list  # noqa: F401
from .ten8t_util import next_int_value  # noqa: F401
from .ten8t_util import str_to_bool  # noqa: F401
from .ten8t_yield import Ten8tYield  # noqa: F401
from .ten8t_yield import Ten8tYieldAll  # noqa: F401
from .ten8t_yield import Ten8tYieldFailOnly  # noqa: F401
from .ten8t_yield import Ten8tYieldPassFail  # noqa: F401
from .ten8t_yield import Ten8tYieldPassOnly  # noqa: F401
from .ten8t_yield import Ten8tYieldSummaryOnly  # noqa: F401

# Dictionary of standard package installs
TEN8T_PACKAGES = {}


def _install(name: str, installed: bool = True) -> None:
    if installed:
        TEN8T_PACKAGES[name] = "Installed"
    else:
        TEN8T_PACKAGES[name] = "Not Installed"


def is_installed(name: str) -> bool:
    """Is a given package installed...based on random strings shown below."""
    return name in TEN8T_PACKAGES


def whats_installed(sep: str = ",") -> str:
    """Generate a printable list of installed packages."""
    return sep.join(sorted(TEN8T_PACKAGES.keys()))


try:
    import pathlib

    _install("pathlib")
    from .rule_files import rule_large_files  # noqa: F401
    from .rule_files import rule_max_files  # noqa: F401
    from .rule_files import rule_path_exists  # noqa: F401
    from .rule_files import rule_paths_exist  # noqa: F401
    from .rule_files import rule_stale_files  # noqa: F401

    _install("pathlib")
except ImportError:
    _install("pathlib", installed=False)
    pass


try:
    import narwhals as nw
    from .rule_ndf import rule_validate_ndf_schema  # noqa: F401
    from .rule_ndf import rule_validate_ndf_values_by_col  # noqa: F401
    from .rule_ndf import rule_ndf_columns_check  # noqa: F401
    from .rule_ndf import extended_bool  # noqa: F401
    _install("narwhals")
except ImportError:
    _install("narwhals",installed=False)
    pass

# webapi using requests
try:
    import requests
    from .rule_webapi import rule_url_200  # noqa: F401
    from .rule_webapi import rule_web_api  # noqa: F401
    _install("requests")
except ImportError:
    _install("requests", installed=False)
    pass


# ping rules
try:
    import ping3
    from .rule_ping import rule_ping_host_check  # noqa: F401
    from .rule_ping import rule_ping_hosts_check  # noqa: F401
    _install("ping")
except ImportError:
    _install("ping", installed=False)
    pass

# xlsx rules
try:
    import openpyxl
    from .rule_xlsx import rule_xlsx_a1_pass_fail
    from .rule_xlsx import rule_xlsx_df_pass_fail
    _install("openpyxl")
except ImportError:
    _install("openpyxl", installed=False)
    pass

# pdf rules
try:
    import camelot  # type: ignore
    import pandas as pd  # pylint: disable=ungrouped-imports
    from .rule_pdf import extract_tables_from_pdf  # noqa: F401
    from .rule_pdf import rule_from_pdf_rule_ids  # noqa: F401
    _install("pdf")
except ImportError:
    _install("pdf", installed=False)
    pass

# sql alchemy support
try:
    import sqlalchemy
    from .rule_sqlachemy import rule_sql_table_col_name_schema
    from .rule_sqlachemy import rule_sql_table_schema
    _install("sqlalchemy")
except ImportError:
    _install("sqlalchemy", installed=False)
    pass

try:
    import warnings

    # Suppress DeprecationWarning only during `fs` module import
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        import fs  # Import the module without triggering the warning

    from .rule_fs import rule_fs_path_exists, rule_fs_paths_exist
    from .rule_fs import rule_fs_oldest_file_age, rule_fs_file_within_max_size

    _install("fs")
except ImportError:
    _install("fs", installed=False)
    pass

try:
    __version__ = version("ten8t")  # Replace with the actual package name in pyproject.toml
except PackageNotFoundError:
    __version__ = "unknown"  # Fallback if version can't be found
