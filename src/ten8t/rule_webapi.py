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
from .render import BM
from .ten8t_result import TR
from .ten8t_yield import Ten8tYield


def rule_url_200(urls: str | Sequence[str],
                 expected_status=200,
                 timeout_sec=5,
                 summary_only=False,
                 summary_name=None) -> Generator[TR, None, None]:
    """
    Verifies the HTTP status code for one or more URLs, and optionally summarizes
    the results.

    This function checks the response status codes of one or more URLs by sending
    a GET request and comparing the result against the expected status code. For
    each URL, it yields a result indicating whether the response matched the
    expected status code or an exception occurred. A summary of the evaluations
    is yielded if the `summary_only` flag is set.

    Args:
        urls (str | Sequence[str]): A single URL as a string, a comma-separated
            string of URLs, or a sequence of URLs.
        expected_status (int): The expected HTTP status code for a successful
            response. Default is 200.
        timeout_sec (int): The maximum waiting time (in seconds) for the server's
            response. Default is 5.
        summary_only (bool): If `True`, only yields a summary of the results after
            all URLs have been processed. Default is `False`.
        summary_name (str | None): A custom name used in the summary result. If
            not provided, defaults to "Rule 200 Check".

    Yields:
        Generator[TR, None, None]: A generator yielding results for each URL and
        an optional summary.
    """
    if summary_only:
        y = Ten8tYield(emit_summary=True,
                       emit_pass=False,
                       emit_fail=False,
                       summary_name=summary_name or "Http Request Response=200 Check")
    else:
        y = Ten8tYield(emit_summary=False,
                       emit_pass=True,
                       emit_fail=True)

    # Allow strings to be passed in
    if isinstance(urls, str):
        urls = urls.replace(",", " ").split()

    # This covers the case BM.code(url) throws an exception
    url_str = "URL Not Provided"

    for url in urls:
        try:
            url_str = BM.code(url)
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
            yield from y(status=False, msg=f"URL{url_str} exception.", except_=ex)

    yield from y.yield_summary()


def is_mismatch(dict1, dict2):
    """
    Checks if two dictionaries have mismatching values or missing keys. If
    a mismatch is found, returns a dictionary that represents the mismatched
    key(s) and their corresponding values from the first dictionary.
    Supports nested dictionary comparison.

    Args:
        dict1: The first dictionary to compare.
        dict2: The second dictionary to compare.

    Returns:
        A dictionary containing the mismatched key(s) and their values from
        the first dictionary. If no mismatch is found, returns None.
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
    """
    Validates a web API response based on the provided parameters and expected conditions. The function
    verifies the response status code, checks for timeouts, and performs JSON structure comparisons if
    applicable. It generates a detailed result for each check and optionally provides a summary.

    Args:
        url (str): The URL to be requested for the API call.
        json_d (dict): The dictionary representing the expected JSON structure for comparison against
            the API response.
        timeout_sec (int, optional): The timeout period in seconds for the API request. Defaults to 5.
        expected_response (int | list[int] | str, optional): The expected HTTP response code(s).
            Can be an integer, list of integers, or a string. Defaults to 200.
        timeout_expected (bool, optional): Indicates whether a timeout is an expected outcome.
            Defaults to False.
        summary_only (bool, optional): If True, only the summary results from all checks will be
            generated. Defaults to False.
        summary_name (str, optional): The custom name for the summary check. If not provided, a
            default of "Rule 200 check" is used. Defaults to None.

    Yields:
        Generator[TR, None, None]: A generator that provides individual and summary results of
        each validation step. Each result indicates the validation status, associated messages,
        and key mismatches where applicable.
    """
    y = Ten8tYield(emit_summary=summary_only)
    try:

        if isinstance(expected_response, int):
            expected_response = [expected_response]
        elif isinstance(expected_response, str):
            expected_response = str.split(expected_response)
        elif not isinstance(expected_response, list):
            raise Ten8tException(f"Expected integer or list of integers for " 
                                 f"'expected_response' for {url}")

        response = requests.get(url, timeout=timeout_sec)

        if response.status_code not in expected_response:
            yield from y(status=False,
                         msg=f"URL {BM.code(url)} expected {BM.expected(expected_response)} " 
                             f"returned {BM.actual(response.status_code)} ")
            return

        # This handles an expected failure by return true but not checking the json
        if response.status_code != 200:
            yield from y(status=True,
                         msg=f"URL {BM.code(url)} returned {BM.code(response.status_code)}, " 
                             f"no JSON comparison needed.")
            return

        response_json: dict = response.json()

        d_status = is_mismatch(json_d, response_json)

        if d_status is None:
            yield from y(status=True,
                         msg=f"URL {BM.code(url)} returned the expected JSON {BM.code(json_d)}")
        else:
            yield from y(status=False,
                         msg=f"URL {BM.code(url)} did not match at key {d_status}")

    except (requests.exceptions.ReadTimeout, requests.exceptions.Timeout):  # pragma: no cover
        yield from y(status=timeout_expected, msg=f"URL {BM.code(url)} timed out.")

    yield from y.yield_summary(summary_name or "Rule 200 check")
