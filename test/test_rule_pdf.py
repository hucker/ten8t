import logging

import pytest

import ten8t.rule_pdf as rule_pdf
from ten8t.ten8t_exception import Ten8tException

logging.getLogger('camelot').setLevel(logging.CRITICAL)


@pytest.mark.parametrize("file, rule_id, status, expected_msg", [
    ("./rule_pdf/RuleId.pdf", "Rule001", True, "Test Result 92%"),
    ("./rule_pdf/RuleId.pdf", "Rule002", True, "Test Result 91%"),
    ("./rule_pdf/RuleId.pdf", "Rule003", False, "TestResult 61%"),
])
def test_extract_tables(file, rule_id, status, expected_msg):
    tables = rule_pdf.extract_tables_from_pdf(file)
    assert tables

    for result in rule_pdf.rule_from_pdf_rule_ids(file, rule_id=rule_id):
        assert result.status is status
        assert result.msg == expected_msg

    for result in rule_pdf.rule_from_pdf_rule_ids(file, default_msg="Override Message", rule_id=rule_id):
        assert result.status is status
        assert result.msg == "Override Message"


@pytest.mark.parametrize("file, rule_id, status, expected_msg", [
    ("./rule_pdf/TwoPage.pdf", "Rule036", True, "TestResult 61%"),
    ("./rule_pdf/TwoPage.pdf", "Rule001", True, "Test Result 92%"),
])
def test_extract_tables_two_page(file, rule_id, status, expected_msg):
    tables = rule_pdf.extract_tables_from_pdf(file, pages='all')
    assert tables

    for result in rule_pdf.rule_from_pdf_rule_ids(file, rule_id=rule_id):
        assert result.status is status
        assert result.msg == expected_msg


@pytest.mark.parametrize("pages, start_count, max_results", [('1', 1, 28), ('2', 29, 8)])
def test_extract_tables_by_page(pages, start_count, max_results):
    file = "./rule_pdf/RepeatedRule.pdf"
    col_names = {'note_col': "Description", 'rule_id': "Rule001"}
    rule_id = "Rule001"

    for count, result in enumerate(rule_pdf.rule_from_pdf_rule_ids(file, col_names=col_names,
                                                                   pages=pages,
                                                                   rule_id=rule_id,
                                                                   max_results=max_results),
                                   start=start_count):
        assert result.status is True
        # Count offset makes you be able to get the number right on the second page
        assert result.msg == f'Case {count}'


def test_extract_tables_bad():
    with pytest.raises(Ten8tException):
        _ = rule_pdf.extract_tables_from_pdf("bad_file.pdf", pages='all')

    tables = rule_pdf.extract_tables_from_pdf("./rule_pdf/NoTables.pdf", pages='all')
    assert len(tables) == 0


def test_extract_pdf_with_no_table():
    file_name = "./rule_pdf/NoTables.pdf"
    tables = rule_pdf.extract_tables_from_pdf(file_name, pages='all')
    assert len(tables) == 0
    assert isinstance(tables, list)

    for _ in rule_pdf.rule_from_pdf_rule_ids(file_name, rule_id='Rule001'):
        pass
    else:
        pass


def test_pdf_with_repeated_rules():
    """Load a multipage file with the same rule id having many results"""
    required = ["RuleId", "Description", "Status"]
    file = './rule_pdf/RepeatedRule.pdf'
    tables = rule_pdf.extract_tables_from_pdf(file, required_columns=required, pages='all')
    assert tables
    assert len(tables) == 2
    count = 0
    for count, result in enumerate(rule_pdf.rule_from_pdf_rule_ids(file,
                                                                   rule_id="Rule001",
                                                                   col_names={'note_col': "Description",
                                                                              'rule_id': "Rule001"},
                                                                   max_results=100,
                                                                   ),
                                   start=1):
        assert result.status is True
        assert result.msg == f'Case {count}'
    assert count == 36


def test_pdf_with_repeated_rules_2():
    """This file has 36 results, but we check for 10 expecting exception"""
    file = './rule_pdf/RepeatedRule.pdf'
    with pytest.raises(Ten8tException) as e_info:
        for _ in rule_pdf.rule_from_pdf_rule_ids(file, rule_id="Rule001",
                                                 col_names={'note_col': "Description",
                                                            'rule_id': "Rule001"},
                                                 max_results=10):
            pass
    assert 'Maximum number of results' in str(e_info.value)
