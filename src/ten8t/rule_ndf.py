"""
This module contains the rules for interacting with dataframes.  Instead of using a single type of
dataframe like pandas, polars or versions of these data frames, I'm using narwhals which is
a compatibility layer that allows ANY type of dataframe to be handled.
"""
from typing import Generator

import narwhals as nw
from narwhals.typing import FrameT

from .ten8t_exception import Ten8tException
from .ten8t_format import BM
from .ten8t_result import TR, Ten8tYield
from .ten8t_util import any_to_str_list


@nw.narwhalify()
def rule_validate_ndf_schema(df: FrameT,
                             int_cols: str | list[str] = None,
                             float_cols: str | list[str] = None,
                             str_cols: str | list[str] = None,
                             number_cols: str | list[str] = None,
                             no_null_cols: str | list[str] = None,
                             summary_name: str | None = '',
                             summary_only: bool = False,
                             name=None) -> Generator[TR, None, None]:
    """
        Validates the schema of a DataFrame according to the specified rules.

        Parameters:
        df: The DataFrame to validate
        int_cols: A list or a string representing column(s) that should contain integers
        float_cols: A list or a string representing column(s) that should contain floats
        str_cols: A list or a string representing column(s) that should contain strings
        number_cols: A list or a string representing column(s) that should contain numeric values (either int or float)
        no_null_cols: A list or a string representing column(s) that should not contain null values
        summary_name: An optional name for the summary of the validation result
        summary_only: A boolean flag indicating whether to yield only the summary of the validation result
        name: An optional name for this rule

        Returns:
        A generator of TR (Test Result) objects, each representing the validation result of a particular rule on a column

        Raises:
        Ten8tException: If no schema checks (i.e., no columns for each of the column types) were specified
    """
    int_cols = any_to_str_list(int_cols)
    float_cols = any_to_str_list(float_cols)
    number_cols = any_to_str_list(number_cols)
    str_cols = any_to_str_list(str_cols)
    no_null_cols = any_to_str_list(no_null_cols)
    name = name or "rule_validate_ndf_schema"
    summary_name = summary_name or "data frame."

    if not any((int_cols, float_cols, no_null_cols, str_cols, number_cols)):
        raise Ten8tException(f"No schema checks were specified for {name}")

    schema = df.dtypes

    y = Ten8tYield(summary_name=summary_name, summary_only=summary_only)

    int_types = "int8 int16 int32 int64 uint8 uint16 uint32 uint64".split()
    float_types = "float32 float64".split()
    num_types = int_types + float_types
    str_types = "object".split()

    for int_col in int_cols:
        if schema[int_col].name in int_types:
            yield from y(TR(True, f"Column {int_col} is an integer type"))
        else:
            yield from y(TR(False, f"Column {BM.code(int_col)} is {BM.bold('NOT')} an integer type"))

    for float_col in float_cols:
        if schema[float_col].name in float_types:
            yield from y(TR(True, f"Column {BM.code(float_col)} is a float type"))
        else:
            yield from y(TR(False, f"Column {BM.code(float_col)} is {BM.bold('NOT')} an float type"))

    for number_col in number_cols:
        if schema[number_col].name in num_types:
            yield from y(TR(True, f"Column {BM.code(number_col)} is a number type"))
        else:
            yield from y(TR(False, f"Column {BM.code(number_col)} is {BM.bold('NOT')} an number type"))

    for str_col in str_cols:
        if schema[str_col].name in str_types:
            yield from y(TR(True, f"Column {BM.code(str_col)} is an string type"))
        else:
            yield from y(TR(False, f"Column {BM.code(str_col)} is {BM.bold('NOT')} an string type"))

    for no_null_col in no_null_cols:
        null_count = len(v for v in df[no_null_col] if v is None or v == '')
        if null_count == 0:
            yield from y(TR(True, f"Column {BM.code(no_null_col)} has {null_count} empty/null values."))
        else:
            yield from y(TR(False, f"Column {BM.code(no_null_col)} has {null_count} empty/null values"))


@nw.narwhalify()
def rule_ndf_columns_check(name: str, df: FrameT, expected_cols_: str | list[str], exact=False):
    """
    A FrameT is a narwhals dataframe.  This supports ANY version of pandas, polars etc. based on what you have
    pip installed into your project.  This allows us to not worry about which version you have installed.

    NOTE: narwhalify takes the dataframe that you pass in whatever type it happens to be and converts
          it to a narwhals dataframe.  This conversion is cheap in that it is just a function wrapper.

    Args:
        name: The name of the dataframe, used for reporting
        df: The dataframe to check
        expected_cols: A list or space separated string of column names that are expected in the dataframe
        exact: If true, the dataframe must have exactly the expected columns. 
               If false, the dataframe can have additional columns.

    Returns:
        A generator that yields Ten8tResult object(s) based on the column checks.
    """

    if df.is_empty() or not df.columns:
        if not expected_cols_:
            yield TR(status=True, msg=f"The {BM.code(name)} data frame is empty and there are no expected columns.")
        else:
            raise ValueError(f"There are no columns in {BM.code(name)}.")

    df_col_names = set(df.columns)
    expected_cols = set(any_to_str_list(expected_cols_))

    missing_columns = expected_cols - df_col_names
    extra_columns = df_col_names - expected_cols

    if exact:
        if not missing_columns and not extra_columns:
            yield TR(status=True,
                     msg=f"All columns were found in the {BM.code(name)} dataframe: {BM.expected(expected_cols)}")
        else:
            msg = f"Data frame {BM.code(name)} is missing {BM.expected(missing_columns)} columns and has extra {BM.expected(extra_columns)} columns"
            yield TR(status=False, msg=msg)

    else:
        # The not exact case means there are no missing but may be extra.
        if not missing_columns:
            yield TR(status=True,
                     msg=f"Data frame {BM.code(name)} has NO missing columns")
        else:
            yield TR(status=False,
                     msg=f"Data frame {BM.code(name)} has missing columns {BM.expected(missing_columns)}")


def convert_to_tuple(input_val: tuple[float, list[str] | str] | None) -> tuple[float, list[str]] | None:
    """
    Convert data inf the form (1.23,[1,2]) and (1.23,"1 2") into a tuple
    with the values (1.23,[1,2]) while keeping mypy happy.
    """
    if input_val is None:
        return None
    value, arr = input_val
    if isinstance(arr, str):
        arr = tuple(float(x) for x in arr.replace(',', ' ').split())
    return value, arr


@nw.narwhalify()
def rule_validate_ndf_values_by_col(df: FrameT,
                                    positive: list[str] | str | None = None,
                                    non_negative: list[str] | str | None = None,
                                    percent: list[str] | str | None = None,
                                    min_: tuple[float, list[str]] | None = None,
                                    max_: tuple[float, list[str]] | None = None,
                                    negative: list[str] | str | None = None,
                                    non_positive: list[str] | str | None = None,
                                    correlation: list[str] | str | None = None,
                                    probability: list[str] | str | None = None,
                                    name: str = '') -> Generator[TR, None, None]:
    """
        Validate DataFrame schema based on given conditions. Parameters are as follows:

        Parameters:
        - df (pd.DataFrame): DataFrame to validate.
        - columns (Sequence[str], optional): Col names to validate. Defaults to None.
        - no_null_columns (Sequence[str], optional): Cols shouldn't have null values. Defaults to None.
        - int_columns (Sequence[str], optional): Columns of integer type. Defaults to None.
        - float_columns (Sequence[str], optional): Columns of float type. Defaults to None.
        - str_columns (Sequence[str], optional): Columns of string type. Defaults to None.
        - row_min_max (Tuple[int,int], optional): Min/max # of rows in DataFrame. Defaults to None.
        - allowed_values (Sequence, optional): Allowed values in columns. Defaults to None.
        - empty_ok (bool, optional): If True, empty DataFrame is valid. Defaults to False.

        Raises:
        - Ten8tException: If df is None, min_rows/max_rows aren't positive integers, or
                           min_rows is > max_rows.

        Yields:
        - TR: An obj with the status of the validation (True if condition is met, False otherwise)
              and a message describing the result.
    """

    if df is None or df.is_empty():
        raise Ten8tException("Dataframe is empty or None")

    # THis is probably the most readable way to do this...but using vars['variable'] is tempting
    positive = any_to_str_list(positive, sep=',')
    non_negative = any_to_str_list(non_negative, sep=',')
    percent = any_to_str_list(percent, sep=',')
    negative = any_to_str_list(negative, sep=',')
    non_positive = any_to_str_list(non_positive, sep=',')
    correlation = any_to_str_list(correlation, sep=',')
    probability = any_to_str_list(probability, sep=',')

    if min_:
        min_ = convert_to_tuple(min_)
    if max_:
        max_ = convert_to_tuple(max_)

    conditions = [positive, non_negative, negative, non_positive,
                  percent, min_, max_, probability, correlation]

    if not any(conditions):
        raise Ten8tException("No data frame column value rules specified.")

    if positive:
        for col in positive:
            if df[col].min() > 0.0:
                yield TR(status=True, msg=f"All values in {BM.code(col)} are positive.")

            else:
                yield TR(status=False, msg=f"All values in {BM.code(col)} are {BM.bold('NOT')}  positive.")

    if non_negative:
        for col in non_negative:
            if df[col].min() >= 0.0:
                yield TR(status=True, msg=f"All values in {BM.code(col)} are non-negative.")
            else:
                yield TR(status=False, msg=f"All values in {BM.code(col)} are {BM.bold('NOT')} non-negative.")

    if percent:
        # Just check 0-100
        for col in percent:
            if 0.0 <= df[col].min() and df[col].max() <= 100.0:
                yield TR(status=True, msg=f"All values in {BM.code(col)} are  a percent.")
            else:
                yield TR(status=False, msg=f"All values in {BM.code(col)} are {BM.bold('NOT')} a percent.")

    if probability:
        for col in probability:
            # Just check 0-100
            if 0.0 <= df[col].min() and df[col].max() <= 1.0:
                yield TR(status=True, msg=f"All values in {BM.code(col)} are probabilities.", )
            else:
                yield TR(status=False, msg=f"All values in {BM.code(col)} are {BM.bold('NOT')} probabilities.")

    if correlation:
        for col in correlation:
            # Just check 0-100
            if -1.0 <= df[col].min() and df[col].max() <= 1.0:
                yield TR(status=True, msg=f"All values in {BM.code(col)} are correlations.", )
            else:
                yield TR(status=False, msg=f"All values in {BM.code(col)} are {BM.bold('NOT')} correlations.")

    if min_:
        val, cols = min_
        for col in cols:
            if df[col].min() >= val:
                yield TR(status=True, msg=f"All values in {BM.code(col)} are > {val}")
            else:
                yield TR(status=False, msg=f"All values in {BM.code(col)} are {BM.bold('NOT')} > {val}")

    if max_:
        val, cols = max_
        for col in cols:
            if df[col].max() <= val:
                yield TR(status=True, msg=f"All values in {BM.code(col)} are < {val}")
            else:
                yield TR(status=False, msg=f"All values in {BM.code(col)} are {BM.bold('NOT')} < {val}")

    if negative:
        for col in negative:
            if df[col].max() < 0.0:
                yield TR(status=True, msg=f"All values in {BM.code(col)} are negative.")
            else:
                yield TR(status=False, msg=f"All values in {BM.code(col)} are {BM.bold('NOT')} negative.")

    if non_positive:
        for col in non_positive:
            if df[col].max() <= 0.0:
                yield TR(status=True, msg=f"All values in {BM.code(col)} are non-positive.")
            else:
                yield TR(status=False, msg=f"All values in {BM.code(col)} are {BM.bold('NOT')} non-positive.")

    if non_positive:
        for col in non_positive:
            if df[col].max() < 0:
                yield TR(status=True, msg=f"All values in {BM.code(col)} are non-positive.")
            else:
                yield TR(status=False, msg=f"All values in {col} are {BM.bold('NOT')} non-positive.")


def extended_bool(value) -> bool:
    """
    Spreadsheet friendly boolean values
    Args:
        value: string

    Returns:

    """
    truthy_values = [True, 1, '1', 'true', 't', 'pass', 'p', 'yes', 'y']
    untruthy_values = [None, False, 0, '0', 'false', 't' 'fail', 'f', 'no', 'n']

    # If value is boolean True, return True
    if isinstance(value, bool) and value is True:
        return True

    # For non-boolean values, convert to string and do a case-insensitive comparison
    str_value = str(value).lower()
    if str_value in truthy_values:
        return True
    elif str_value in untruthy_values:
        return False

    # This could be an exception
    return False


@nw.narwhalify()
def rule_ndf_pf_columns(df: FrameT,
                        pf_col: str = "Status",
                        desc_col: str = "Description",
                        enabled_col: str = None,
                        name: str = '',
                        summary_only: bool = False) -> Generator[TR, None, None]:
    """
    Given a dataframe of the form:
    Description  Status  Enabled
    Test1        1       1
    Test2        0       1
    Test3        0       0
    
    Check the status honoring the enabled column.  The enable column is optional, but it is assumed
    that this could come from a 'live' spreadsheet, so we need to be flexible on what "pass" means.
    
    In this case it can be True, 1, "Pass"
    
    Args:
        df: Data Frame
        pf_col: Pass Fail Column
        desc_col:  Description Column
        enabled_col: Enabled Column (when not included assumes all are enabled)
        name: Name used for summary
        summary_only: Only display summary?

    Returns:

    """
    if not desc_col:
        raise AttributeError("Invalid description column")
    if not pf_col:
        raise AttributeError("Invalid pass/fail column")
    if isinstance(enabled_col, str) and enabled_col.strip() == '':
        raise AttributeError("Invalid enable column name.")

    summary_yield = Ten8tYield(summary_only=summary_only)

    for row in df.iter_rows(named=True):
        if enabled_col and not extended_bool(row[enabled_col]):
            continue

        pass_status = extended_bool(row[pf_col])
        row_description = BM.code(row[desc_col])
        ten8t_result = TR(pass_status,
                          f"{row_description} {BM.pass_('passed.') if pass_status else BM.fail('failed.')}")

        yield from summary_yield(ten8t_result)

    if summary_only:
        yield from summary_yield.yield_summary(name=name)
