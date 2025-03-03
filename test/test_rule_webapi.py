import pytest

from src import ten8t as t8
from src.ten8t.rule_webapi import is_mismatch

TIME_OUT_SEC = 15  # This doesn't always need to be this large but sometimes the endpoints are slow

@pytest.fixture
def expected_json():
    """This is a default response from the test web api"""
    return {
        "slideshow": {
            "author": "Yours Truly",
            "date": "date of publication",
            "slides": [
                {
                    "title": "Wake up to WonderWidgets!",
                    "type": "all"
                },
                {
                    "items": [
                        "Why <em>WonderWidgets</em> are great",
                        "Who <em>buys</em> WonderWidgets"
                    ],
                    "title": "Overview",
                    "type": "all"
                }
            ],
            "title": "Sample Slide Show"
        }
    }


def test_urls():
    urls = ["https://www.google.com", "https://www.yahoo.com", "https://www.bing.com"]

    @t8.attributes(tag="tag")
    def check_rule1():
        yield from t8.rule_url_200(urls=urls)

    for result in check_rule1():
        assert result.status


def test_urls_as_strings():
    urls = "https://www.google.com https://www.yahoo.com https://www.bing.com"

    @t8.attributes(tag="tag")
    def check_rule1():
        yield from t8.rule_url_200(urls=urls)

    for result in check_rule1():
        assert result.status


def test_urls_summary_only():
    urls = "https://www.google.com https://www.yahoo.com https://www.bing.com"

    @t8.attributes(tag="tag")
    def check_rule1():
        yield from t8.rule_url_200(urls=urls, summary_only=True)

    for result in check_rule1():
        assert result.status


def test_bad_urls():
    urls = ["https://www.google.com/doesnotexist", "https://www.yahooXXXXXX"]

    @t8.attributes(tag="tag")
    def check_rule1():
        yield from t8.rule_url_200(urls=urls)

    for result in check_rule1():
        assert not result.status


def test_missing_web_api():
    # Try to get a non-existent webapi end point
    @t8.attributes(tag="tag")
    def check_rule2():
        yield from t8.rule_web_api(url='https://httpbin.org/json1',
                                   json_d={'name': 'Luke Skywalker'},
                                   expected_response=[404, 502],
                                   # WARNING: This used to return 404, not sometimes is 502
                                   timeout_sec=TIME_OUT_SEC)

    for result in check_rule2():
        assert result.status


def test_wrong_response(expected_json):
    @t8.attributes(tag="tag")
    def check_rule1():
        yield from t8.rule_web_api(url='https://httpbin.org/json',
                                   json_d=expected_json,
                                   expected_response=404,  # Returns 200
                                   timeout_sec=TIME_OUT_SEC)

    for result in check_rule1():
        assert result.status is False


def test_web_api(expected_json):
    @t8.attributes(tag="tag")
    def check_rule1():
        yield from t8.rule_web_api(url='https://httpbin.org/json',
                                   json_d=expected_json,
                                   timeout_sec=TIME_OUT_SEC)

    for result in check_rule1():
        assert result.status

    # Now make it fail
    expected_json["slideshow"]["author"] = "Chuck"
    for result in check_rule1():
        assert not result.status


def convert_integers_to_strings(d):
    """This takes my integer test dictionaries and turns them into strings for test purposes"""
    if not d:
        return d
    for key, value in d.items():
        if isinstance(value, int):
            d[key] = str(value)
        elif isinstance(value, dict):
            convert_integers_to_strings(value)
    return d


def test_mismatch_fail():
    assert is_mismatch(1, {}) is False
    assert is_mismatch({}, 1) is False


def test_get_difference():
    tests = [
        ({}, {}, None, 'Null Test'),
        ({'a': 1}, {'a': 1}, None, 'Simple pass'),
        ({'a': 1}, {'a': 2}, {'a': 1}, 'Simple fail'),
        ({'a': 1}, {'A': 1}, {'a': 1}, 'Simple fail'),
        ({'a': 1}, {'b': 1}, {'a': 1}, 'Simple no key'),
        (
            {'a': 1, 'b': 2, 'c': {'d': 3, 'e': 4}}, {'a': 1, 'b': 2, 'c': {'d': 3, 'e': 5}}, {'c': {'e': 4}},
            "Nest diff"),
        ({'a': 1, 'b': 2, 'c': {'d': 3, 'e': 4}}, {'a': 1, 'b': 2, 'c': {'d': 3, 'e': 4}, 'f': 6}, None, 'Nested diff'),
    ]

    for sub_set, main_set, expected_result, msg in tests:
        result = is_mismatch(sub_set, main_set)
        assert result == expected_result

    # now convert to string values
    for sub_set, main_set, expected_result, msg in tests:
        sub_set = convert_integers_to_strings(sub_set)
        main_set = convert_integers_to_strings(main_set)
        expected_result = convert_integers_to_strings(expected_result)
        result = is_mismatch(sub_set, main_set)
        assert result == expected_result
