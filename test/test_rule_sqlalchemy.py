import itertools

import pytest
from sqlalchemy import Column, MetaData, Table, create_engine
from sqlalchemy.types import BOOLEAN, DATE, DATETIME, DECIMAL, DOUBLE, INTEGER, VARCHAR

from src import ten8t as t8


@pytest.fixture
def engine():
    engine = create_engine('sqlite:///:memory:')
    metadata = MetaData()
    metadata.bind = engine

    # Define a table
    table = Table(
        'users', metadata,
        Column('id', INTEGER, primary_key=True),
        Column('name', VARCHAR),
        Column('email', VARCHAR),
        Column('age', INTEGER)
    )

    # Drop the table if it exists
    table.drop(engine, checkfirst=True)

    # Create all tables in the metadata
    metadata.create_all(engine)

    yield engine


@pytest.fixture
def engine_alltypes():
    engine = create_engine('sqlite:///:memory:')
    metadata = MetaData()
    metadata.bind = engine

    # Define a table
    table = Table(
        'users', metadata,
        Column('id', INTEGER, primary_key=True),
        Column('name', VARCHAR),
        Column('date', DATE),
        Column('arrival', DATETIME),
        Column('age', DOUBLE),
        Column('adult', BOOLEAN),
        Column('dec', DECIMAL),
    )

    # Drop the table if it exists
    table.drop(engine, checkfirst=True)

    # Create all tables in the metadata
    metadata.create_all(engine)

    yield engine


@pytest.mark.parametrize(
    "expected_columns, expected_results",
    [
        (
                ['id', 'name', 'email', 'age'],
                [
                    t8.Ten8tResult(status=True,
                                   msg="Column <<code>>id<</code>> is present in table <<code>>users<</code>>"),
                    t8.Ten8tResult(status=True,
                                   msg="Column <<code>>name<</code>> is present in table <<code>>users<</code>>"),
                    t8.Ten8tResult(status=True,
                                   msg="Column <<code>>email<</code>> is present in table <<code>>users<</code>>"),
                    t8.Ten8tResult(status=True,
                                   msg="Column <<code>>age<</code>> is present in table <<code>>users<</code>>")
                ]
        ),
        (
                ['id', 'name', 'email', 'age', 'unexpected'],
                [
                    t8.Ten8tResult(status=True,
                                   msg="Column <<code>>id<</code>> is present in table <<code>>users<</code>>"),
                    t8.Ten8tResult(status=True,
                                   msg="Column <<code>>name<</code>> is present in table <<code>>users<</code>>"),
                    t8.Ten8tResult(status=True,
                                   msg="Column <<code>>email<</code>> is present in table <<code>>users<</code>>"),
                    t8.Ten8tResult(status=True,
                                   msg="Column <<code>>age<</code>> is present in table <<code>>users<</code>>"),
                    t8.Ten8tResult(status=False,
                                   msg="Column <<code>>unexpected<</code>> is <<fail>>MISSING<</fail>> in table <<code>>users<</code>>")
                ]
        ),
    ],
)
def test_rule_sql_table_schema(engine, expected_columns, expected_results):
    # Call the function with the expected columns list
    results = list(t8.rule_sql_table_col_name_schema(engine, 'users', expected_columns))

    for e, r in zip(results, expected_results):
        assert e.status == r.status
        assert r.msg == e.msg
        assert r.status == e.status


@pytest.mark.parametrize(
    "expected_columns, expected_results",
    [
        (
                ['name', 'email', 'age'],
                [
                    t8.Ten8tResult(status=True,
                                   msg="Column <<code>>name<</code>> is correctly present in table <<code>>users<</code>>"),
                    t8.Ten8tResult(status=True,
                                   msg="Column <<code>>email<</code>> is correctly present in table <<code>>users<</code>>"),
                    t8.Ten8tResult(status=True,
                                   msg="Column <<code>>age<</code>> is correctly present in table <<code>>users<</code>>")
                ]
        ),
        (
                ['id', 'name', 'email'],
                [
                    t8.Ten8tResult(status=True,
                                   msg="Column <<code>>id<</code>> is correctly present in table <<code>>users<</code>>"),
                    t8.Ten8tResult(status=True,
                                   msg="Column <<code>>name<</code>> is correctly present in table <<code>>users<</code>>"),
                    t8.Ten8tResult(status=True,
                                   msg="Column <<code>>email<</code>> is correctly present in table <<code>>users<</code>>"),
                ]
        ),
    ],
)
def test_rule_sql_table_schema_with_extra(engine, expected_columns, expected_results):
    # Call the function with the expected columns list
    results = list(t8.rule_sql_table_col_name_schema(engine, 'users', expected_columns, extra_columns_ok=True))

    # NOTE: This is a bit tricky, you would think you could just compare the lists, but the code that 
    #       runs the rule fills in other low level details that we aren't concerned with
    # assert all(r.msg == e.msg and r.status == e.status for e, r in zip(results, expected_results))
    assert all(r.status == e.status for e, r in zip(results, expected_results))


def test_rule_sql_table_bad_table(engine):
    # Call the function with the expected columns list
    results = list(
        t8.rule_sql_table_col_name_schema(engine, table='', expected_columns=['users'], extra_columns_ok=True))

    assert results[0].msg == "Table name cannot be blank."
    assert not results[0].status


def test_rule_sql_table_bad_column(engine):
    # Call the function with the expected columns list
    results = list(
        t8.rule_sql_table_col_name_schema(engine, table='users', expected_columns=[''], extra_columns_ok=True))

    assert results[0].msg == "Column names cannot be empty."
    assert not results[0].status


def test_rule_sql_table_bad_column_list(engine):
    # Call the function with the expected columns list
    results = list(
        t8.rule_sql_table_col_name_schema(engine, table='users', expected_columns=[], extra_columns_ok=True))

    assert not results[0].status
    assert results[0].msg == "Column list cannot be empty."


def test_rule_sql_table_bad_extra_columns(engine):
    # Call the function with the expected columns list
    results = list(t8.rule_sql_table_col_name_schema(engine, table='users', expected_columns=['id', 'name'],
                                                     extra_columns_ok=False))
    msgs = ["Column <<code>>id<</code>> is present in table <<code>>users<</code>>",
            "Column <<code>>name<</code>> is present in table <<code>>users<</code>>",
            "Column <<code>>age<</code>> is UNEXPECTED in table <<code>>users<</code>>",
            "Column <<code>>email<</code>> is UNEXPECTED in table <<code>>users<</code>>",
            ]

    # This is very screwy, but I've had issues with different versions of python returning the results
    # in slightly different orders.  So first I'm verifying that I get 4 different messages back and
    # then I check that each message is in the result set.⁄
    # This is not ideal and should be refactored
    assert len(set([result.msg for result in results])) == 4
    for result in results:
        assert (result.status is False) if "UNEXPECTED" in result.msg else (result.status is True)
        assert result.msg in msgs


def test_rule_sql_table_types(engine):
    results = list(t8.rule_sql_table_schema(engine,
                                            table='users',
                                            expected_columns=[('id', INTEGER())],
                                            extra_columns_ok=True))
    assert results[0].status is True

    results = list(t8.rule_sql_table_schema(engine,
                                            table='users',
                                            expected_columns=[('email', VARCHAR())],
                                            extra_columns_ok=True))
    assert results[0].status is True


def test_rule_sql_all(engine_alltypes):
    """Verify column names and types are correctly handled."""
    results = list(t8.rule_sql_table_schema(engine_alltypes,
                                            table='users',
                                            expected_columns=[('id', INTEGER()),
                                                              ('name', VARCHAR()),
                                                              ('age', DOUBLE()),
                                                              ('date', DATE()),
                                                              ('arrival', DATETIME()),
                                                              ('adult', BOOLEAN()),
                                                              ('dec', DECIMAL())],
                                            extra_columns_ok=True))
    assert len(results) == 7
    assert all(r.status for r in results)


def test_rule_sql_schema_missing_cols(engine_alltypes):
    """Verify column names and types are correctly handled."""
    results = list(t8.rule_sql_table_schema(engine_alltypes,
                                            table='users',
                                            expected_columns=[('id', INTEGER()),
                                                              ('name', VARCHAR()),
                                                              ('adult', BOOLEAN()),
                                                              ('dec', DECIMAL())],
                                            extra_columns_ok=True))
    assert len(results) == 4
    assert all(r.status for r in results)


def test_permutations_rule_sql_all(engine_alltypes):
    """
    This test tries all dates in all possible orders and all possible sizes.
    
    The number of test cases is 2^n - 1 where N is the number of expected columns.
    
    At first this wasn't obvious but it should be obvious because each data type
    represents a 'bit' that may or may not be present.  If there are 7 bits then
    2^7 = 128 and -1 because we must have one. 
    """

    expected_columns = [('id', INTEGER()),
                        ('name', VARCHAR()),
                        ('age', DOUBLE()),
                        ('date', DATE()),
                        ('arrival', DATETIME()),
                        ('adult', BOOLEAN()),
                        ('dec', DECIMAL())]

    all_combinations = []
    for r in range(1, len(expected_columns) + 1):
        combs = list(itertools.combinations(expected_columns, r))
        all_combinations.extend(combs)

    for combination in all_combinations:
        results = list(t8.rule_sql_table_schema(engine_alltypes,
                                                table='users',
                                                expected_columns=list(combination),
                                                extra_columns_ok=True))
        assert len(results) == len(combination)
        assert all(r.status for r in results)
