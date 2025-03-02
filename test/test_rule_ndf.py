"""
Note: This is a test of the narwhals interface.  While we are using pandas, this is really a
test of the narwhals interface.  Any code that says _ndf in it is using Narwhals and as such should
be compatible with all supported data frame libraries.  This test is NOT to verify that all 
df libraries work, but that the ten8t interface to narwhals is working with the ideal being that
ten8t has NO dependency on dataframe libraries and only depends upon narwhals.

This means that the test code will create test data frames BUT nothing in spl
"""

import numpy as np
import pandas as pd
import pytest

from src.ten8t.rule_ndf import convert_to_tuple, extended_bool
from src.ten8t.rule_ndf import rule_ndf_columns_check, rule_ndf_pf_columns, rule_validate_ndf_values_by_col
from src.ten8t.ten8t_function import Ten8tFunction


@pytest.fixture(scope="module")
def dataframe() -> pd.DataFrame:
    # Make a DataFrame with 4 columns and 10 rows of random numbers
    df = pd.DataFrame(np.random.randn(10, 4), columns=list('ABCD'))
    return df


@pytest.fixture(scope="module")
def null_dataframe() -> pd.DataFrame:
    # Make a DataFrame with 4 columns and 10 rows of random numbers
    df = pd.DataFrame()
    return df


def test_rule_ndf(dataframe: pd.DataFrame):
    # dataframe = 1
    def check_good_narwhals_frame():
        yield from rule_ndf_columns_check(name="ABCD Dataframe",
                                          df=dataframe,
                                          expected_cols_=['A', 'B', 'C', 'D'],
                                          exact=True)

    s_func1 = Ten8tFunction(check_good_narwhals_frame)
    for result in s_func1():
        assert result.status is True


def test_rule_not_exact(dataframe: pd.DataFrame):
    # dataframe = 1
    def check_good_narwhals_frame():
        yield from rule_ndf_columns_check(name="ABCD Dataframe",
                                          df=dataframe,
                                          expected_cols_=['A', 'B', 'C'],
                                          exact=False)

    s_func1 = Ten8tFunction(check_good_narwhals_frame)
    for result in s_func1():
        assert result.status is True


def test_rule_ndf_missing(dataframe: pd.DataFrame):
    # dataframe = 1
    def check_good_narwhals_frame():
        yield from rule_ndf_columns_check(name="ABCD Dataframe",
                                          df=dataframe,
                                          expected_cols_=['A', 'B', 'C', 'D', 'E'],
                                          exact=False)

    s_func1 = Ten8tFunction(check_good_narwhals_frame)
    for result in s_func1():
        assert result.status is False
        assert "'E'" in result.msg


def test_rule_ndf_unexpected_null(null_dataframe: pd.DataFrame):
    # dataframe = 1
    def check_null_narwhals_frame():
        yield from rule_ndf_columns_check(name="Null Dataframe",
                                          df=null_dataframe,
                                          expected_cols_=['A', 'B', 'C', 'D', 'E'],
                                          exact=False)

    s_func1 = Ten8tFunction(check_null_narwhals_frame)
    for result in s_func1():
        assert result.status is False
        assert result.traceback
        assert "Exception" in result.msg


@pytest.mark.parametrize(
    "value", [1, '1', 'true', 't', 'pass', 'p', 'yes', 'y', True,
              'TRUE', 'T', 'PASS', 'P', 'YES', 'Y']
)
def test_extended_bool_truthy(value):
    assert extended_bool(value)


@pytest.mark.parametrize(
    "value", [0, '0', 'false', 'fail', 'f', 'no', 'n', '', None, False, 'not a bool', 2,
              'FALSE', 'FAIL', 'F', 'NO', 'N']
)
def test_extended_bool_falsy(value):
    assert not extended_bool(value)


def test_rule_ndf_expected_null(null_dataframe: pd.DataFrame):
    # dataframe = 1
    def check_null_narwhals_frame():
        yield from rule_ndf_columns_check(name="Expected Null Dataframe",
                                          df=null_dataframe,
                                          expected_cols_=[],
                                          exact=False)

    s_func1 = Ten8tFunction(check_null_narwhals_frame)
    for result in s_func1():
        assert result.status is True


@pytest.fixture
def pass_dataframe() -> pd.DataFrame:
    return pd.DataFrame({
        'Description': ['test1', 'test2', 'test3'],
        'Status': ['1', '1', '1'],
        'Enabled': ['1', '1', '1'],
    })


@pytest.fixture
def fail_dataframe() -> pd.DataFrame:
    """Pycharm does not detect that this is being used as a fixture."""
    return pd.DataFrame({
        'Description': ['test1', 'test2', 'test3'],
        'Status': ['0', '0', '0'],
        'Enabled': ['1', '1', '1'],
    })


df_params = [("pass_dataframe", True, 3),
             ("fail_dataframe", False, 3)]


@pytest.mark.parametrize("df_fixture_name,expected_status,expected_length", df_params)
def test_rule_ndf_pf_columns_enabled(request, df_fixture_name, expected_status, expected_length):
    def check_narwhals_pf_frame():
        yield from rule_ndf_pf_columns(name="Boolean Dataframe",
                                       df=request.getfixturevalue(df_fixture_name),
                                       pf_col='Status',
                                       desc_col='Description',
                                       enabled_col='Enabled',
                                       summary_only=False)

    s_func1 = Ten8tFunction(check_narwhals_pf_frame)
    results = list(s_func1())
    for result in results:
        assert result.status is expected_status
    assert len(results) == expected_length


def test_rule_ndf_pf_summary_enabled(pass_dataframe: pd.DataFrame):
    def check_narwhals_pf_frame():
        yield from rule_ndf_pf_columns(name="Boolean Dataframe",
                                       df=pass_dataframe,
                                       pf_col='Status',
                                       desc_col='Description',
                                       enabled_col='Enabled',
                                       summary_only=True)

    s_func1 = Ten8tFunction(check_narwhals_pf_frame)
    results = list(s_func1())
    for result in results:
        assert result.status is True
    assert len(results) == 1
    assert 'Boolean Dataframe' in results[0].msg


def test_rule_ndf_pf_columns_no_enabed(pass_dataframe: pd.DataFrame):
    def check_narwhals_pf_frame():
        yield from rule_ndf_pf_columns(name="Boolean Dataframe",
                                       df=pass_dataframe,
                                       pf_col='Status',
                                       desc_col='Description',
                                       summary_only=False)

    s_func1 = Ten8tFunction(check_narwhals_pf_frame)
    results = list(s_func1())
    for result in results:
        assert result.status is True
    assert len(results) == 3


def test_rule_ndf_pf_columns_empty():
    df = pd.DataFrame({'Description': [], 'Status': [], 'Enabled': []})
    results = list(rule_ndf_pf_columns(df, 'Status', 'Description', 'Enabled'))
    assert len(results) == 0


def test_rule_ndf_missing_cols(pass_dataframe: pd.DataFrame):
    def check_narwhals_no_desc_frame():
        yield from rule_ndf_pf_columns(name="Boolean Dataframe",
                                       df=pass_dataframe,
                                       pf_col='Status',
                                       desc_col='')

    def check_narwhals_no_pf_frame():
        yield from rule_ndf_pf_columns(name="Boolean Dataframe",
                                       df=pass_dataframe,
                                       pf_col='',
                                       desc_col='Description')

    def check_narwhals_no_enabled_frame():
        yield from rule_ndf_pf_columns(name="Boolean Dataframe",
                                       df=pass_dataframe,
                                       enabled_col='')

    with pytest.raises(AttributeError):
        results = list(check_narwhals_no_desc_frame())

    with pytest.raises(AttributeError):
        results = list(check_narwhals_no_pf_frame())

    with pytest.raises(AttributeError):
        results = list(check_narwhals_no_enabled_frame())


@pytest.fixture
def type_dataframe():
    """Dataframe with valid colum values."""
    return pd.DataFrame({
        'positive': [1, 2, 300],
        'non_negative': [0, 1, 200],
        'percent': [0.0, 10.0, 100.0],
        'negative': [-1, -2, -300],
        'non_positive': [0, -1, -200],
        'correlation': [-1.0, 0, 1.0],
        'probability': [0.0, .5, 1.0],
    })


def test_rule_ndf_columns(type_dataframe):
    results = list(rule_validate_ndf_values_by_col(name='name', df=type_dataframe, positive='positive'))
    assert results[0].status is True


@pytest.fixture
def type_dataframe_low():
    """Dataframe with valid colum values that will fail on the low side"""
    return pd.DataFrame({
        'positive': [-1, 2, 300],
        'non_negative': [0, -1, 200],
        'percent': [0.0, -10.0, 100.0],
        'correlation': [-1.01, 0, 1.0],
        'probability': [-0.1, .5, 1.0],
    })


def test_rule_ndf_columns_low(type_dataframe_low):
    results = list(rule_validate_ndf_values_by_col(name='name',
                                                   df=type_dataframe_low,
                                                   positive='positive',
                                                   non_negative='non_negative',
                                                   percent='percent',
                                                   correlation='correlation',
                                                   probability='probability'))
    assert results[0].status is False


@pytest.fixture
def type_dataframe_high():
    """Dataframe with valid colum values."""
    return pd.DataFrame({
        'percent': [0.0, 10.0, 100.1],
        'negative': [1, -2, -300],
        'non_positive': [0, -1, -200],
        'correlation': [-1.0, 0, 1.01],
        'probability': [0.0, .5, 1.01],
    })


def test_rule_ndf_columns_high(type_dataframe_high):
    """Each of these will fail on the high side"""
    results = list(rule_validate_ndf_values_by_col(name='name',
                                                   df=type_dataframe_high,
                                                   percent='percent',
                                                   negative='negative',
                                                   non_positive='non_positive',
                                                   correlation='correlation',
                                                   probability='probability'))
    assert results[0].status is False


def test_conv_to_tuple():
    # NOTE:you can compare floating point numbers for equality if the decimal
    #     is a fractional power of 2.  The string conversion code depends on
    #     this.  You could also do 1.0 and 2.0, but this shows there is no
    #     integer "stuff" going on.
    assert (1.23, (1, 1)) == convert_to_tuple([1.23, (1, 1)])
    assert (1.23, (1.0, 1.0)) == convert_to_tuple([1.23, "1, 1"])
    assert (1.23, (1.5, 1.25)) == convert_to_tuple([1.23, (1.50, 1.25)])
    assert (1.23, (1.5, 1.25)) == convert_to_tuple([1.23, "1.50, 1.25"])
    assert None is convert_to_tuple(None)
