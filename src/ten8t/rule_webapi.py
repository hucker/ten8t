"""
This module provides functions for conducting URL checks and handling their responses.

Includes:
- `rule_url_200`: Checks if an array of URLs returns a specific HTTP status code.

- `is_mismatch`: Compares two dictionaries, returns the first differing pair.

- `rule_web_api`: Verifies a URLs HTTP response status code and compares returned JSON data.

Uses the `requests` library for HTTP requests, and handles exceptions accordingly.
"""
from typing import Generator, Sequence

import requests
from requests.exceptions import RequestException

from . import Ten8tException
from .ten8t_format import BM
from .ten8t_result import TR, Ten8tYield


def rule_url_200(urls: str | Sequence[str],
                 expected_status=200,
                 timeout_sec=5,
                 summary_only=False,
                 summary_name=None) -> Generator[TR, None, None]:
    """
    Simple rule check to verify that URL is active.
    
    TAs setup this just checks that a web API URL is active. The urls parameter
    is set up to be tolerant of varius ways you could pass a list of URLS
    
    urls(str|Sequence[str]): List of URLs to check or a string that can be split into URLs
    expected_status(200): Expected response status code
    timeout_sec(int): Timeout in seconds.
    
    """
    y = Ten8tYield(summary_only=summary_only, summary_name=summary_name or "Rule 200 Check")

    # Allow strings to be passed in
    if isinstance(urls, str):
        urls = urls.replace(",", " ").split()

    for url in urls:
        try:
            response = requests.get(url, timeout=timeout_sec)
            url_str = BM.code(url)
            code_str = BM.code(response.status_code)

            if response.status_code == expected_status:
                yield from y(status=True, msg=f"URL {url_str} returned {code_str}")
            else:
                yield from y(
                    status=response.status_code == expected_status,
                    msg=f"URL {url_str} returned {code_str}",
                )

        except RequestException as ex:
            yield from y(status=False, msg=f"URL{BM.code(url)} exception.", except_=ex)

    if summary_only:
        yield from y.yield_summary()


def is_mismatch(dict1, dict2):
    """
    Return the first differing values from dict1 and dict2
    Args:
        dict1:
        dict2:

    Returns: None if every key/value pair in dict1 is in dict, otherwise
            returns the first value that differs from dict 2

    """
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return False
    for key, value in dict1.items():
        if key not in dict2:
            return {key: value}
        if isinstance(value, dict):
            nested_result = is_mismatch(value, dict2[key])
            if nested_result is not None:  # Manual short-circuit the mismatch search.
                return {key: nested_result}
        elif value != dict2[key]:
            return {key: value}
    return None  # Return None if it is a subset.


def rule_web_api(url: str,
                 json_d: dict,
                 timeout_sec=5,
                 expected_response=200,
                 timeout_expected=False,
                 summary_only=False,
                 summary_name=None) -> Generator[TR, None, None]:
    """Simple rule check to verify that URL is active and handles timeouts."""
    y = Ten8tYield(summary_only=summary_only)
    try:

        if isinstance(expected_response, int):
            expected_response = [expected_response]
        elif isinstance(expected_response, str):
            expected_response = str.split(expected_response)
        elif not isinstance(expected_response, list):
            raise Ten8tException(f"Expected integer or list of integers for 'expected_response' for {url}")

        response = requests.get(url, timeout=timeout_sec)

        if response.status_code not in expected_response:
            yield from y(status=False,
                         msg=f"URL {BM.code(url)} expected {BM.expected(expected_response)} returned {BM.actual(response.status_code)} ")
            return

        # This handles an expected failure by return true but not checking the json
        if response.status_code != 200:
            yield from y(status=True,
                         msg=f"URL {BM.code(url)} returned {BM.code(response.status_code)}, no JSON comparison needed.")
            return

        response_json: dict = response.json()
        # d_status = verify_dicts(response_json, json_d)

        d_status = is_mismatch(json_d, response_json)

        if d_status is None:
            yield from y(status=True,
                         msg=f"URL {BM.code(url)} returned the expected JSON {BM.code(json_d)}")
        else:
            yield from y(status=False,
                         msg=f"URL {BM.code(url)} did not match at key {d_status}")

    except (requests.exceptions.ReadTimeout, requests.exceptions.Timeout):  # pragma: no cover
        yield from y(status=timeout_expected, msg=f"URL {BM.code(url)} timed out.")

    if summary_only:
        yield from y.yield_summary(summary_name or "Rule 200 check")
