import pytest

from conftest import logger
from ten8t import Ten8tChecker, ten8t_checker
from ten8t import attributes, rule_ping_host_check, rule_ping_hosts_check


# urls fixture that returns list of urls to check
@pytest.fixture
def urls():
    return ["www.google.com", "www.yahoo.com", "www.bing.com"]


@pytest.fixture
def bad_urls():
    return ["asdfaasf", "123", "", None, "bad.url.foo"]


def test_empty_rule_ping(urls):
    """ Verify url is tested fail"""

    @attributes(tag="tag")
    def check_rule_ping_fail():
        yield from rule_ping_hosts_check("", pass_on_none=False)
        yield from rule_ping_hosts_check([], pass_on_none=False)

    for result in check_rule_ping_fail():
        assert not result.status


def test_empty_rule_ping_pass(urls):
    """ Verify empty url is tested pass """

    @attributes(tag="tag")
    def check_rule_ping_pass():
        yield from rule_ping_hosts_check("", pass_on_none=True)
        yield from rule_ping_hosts_check([], pass_on_none=True)

    for result in check_rule_ping_pass():
        assert result.status


def test_skip_ping_true():
    @attributes(tag="tag")
    def check_rule_ping_skip():
        yield from rule_ping_hosts_check("", skip_on_none=True)
        yield from rule_ping_hosts_check([], skip_on_none=True)

    for result in check_rule_ping_skip():
        assert result.skipped


def test_skip_ping_false():
    @attributes(tag="tag")
    def check_rule_ping_not_skipped():
        yield from rule_ping_hosts_check("", skip_on_none=False)
        yield from rule_ping_hosts_check([], skip_on_none=False)

    for result in check_rule_ping_not_skipped():
        assert not result.skipped


def test_rule_ping(urls):
    """ Verify single url is tested """

    @attributes(tag="tag")
    def check_rule_ping():
        yield from rule_ping_hosts_check(urls[0])

    for result in check_rule_ping():
        assert result.status


def test_rule_latency_fail_ping():
    """ Verify single url is tested """

    @attributes(tag="tag")
    def check_rule_ping():
        yield rule_ping_host_check("www.google.com", timeout_sec=.001)

    for result in check_rule_ping():
        assert not result.status
        assert result.msg.startswith("No ping response from server")


@pytest.mark.parametrize("invalid_timeout", [0, 0.0, -1, -1.0, -9999, -0.001])
def test_bad_non_positive_timeouts(invalid_timeout):
    """
    Test that non-positive timeout values correctly fail when passed to rule_ping_host_check.
    """

    def check_rule_bad_ping():
        # Pass the parameterized invalid timeout to the function
        yield rule_ping_host_check("localhost", timeout_sec=invalid_timeout)

    for result in check_rule_bad_ping():
        # Assert that it fails as expected
        assert result.status is False
        assert 'Ping timeout must be > 0' in result.msg


def test_rule_pings(urls):
    """ Verify list of urls is tested """

    @attributes(tag="tag")
    def check_rule_pings():
        yield from rule_ping_hosts_check(urls, yield_summary=False)

    for count, result in enumerate(check_rule_pings()):
        assert result.status
        assert "is up" in result.msg

    # Make sure we ran all the tests
    assert count == len(urls) - 1


@pytest.mark.parametrize(
    "invalid_url", [
        None,  # NoneType
        123,  # Integer
        {},  # Empty dictionary
        set(["example.com"]),  # Set
        False,  # Boolean value
        3.14,  # Float
        b"example",  # Byte string
        lambda x: x,  # Callable object (function)
    ]
)
def test_non_string_urls(invalid_url):
    """
    Verify that invalid URLs that are not strings (or a list of strings)
    generate appropriate errors or failures within the `rule_ping_check` function.
    """
    hosts = [invalid_url]  # Wrap the invalid URL in a list to feed the generator.

    with pytest.raises(Exception):  # Adjust this exception type to match your exact implementation
        # Iterate over results from rule_ping_check
        for result in rule_ping_hosts_check(hosts):
            ""  # pragma no cover


import statistics


def get_stats(numbers: list[float]):
    """
    Calculate mean, min, max, and standard deviation of a list and return as a dictionary.

    Args:
        numbers (list): List of numbers.

    Returns:
        dict: Dictionary containing the statistics and the data itself.
    """
    # Handle edge case when the list is empty
    if not numbers:
        return {
            "data": [],
            "mean": 0,
            "min": 0,
            "max": 0,
            "stdev": 0,
            "status": "empty",
            "count": 0
        }

    # Calculate statistics
    stats = {
        "mean": statistics.mean(numbers),
        "min": f"{min(numbers):.06f}",
        "max": f"{max(numbers):.06f}",
        "stdev": f"{statistics.stdev(numbers):.06f}",
        "status": "ok",
        "count": len(numbers),
        "data": list(f"{number:.06f}" for number in numbers),  # Use "data" instead of "list"
    }
    return stats


def make_check(target, samples, workers):
    """Create a check function with the right number of targets and workers"""

    def check_pings():
        yield from rule_ping_hosts_check([target] * samples, max_workers=workers)

    # Returns a custom function
    return check_pings


def test_ping_threading():
    """
    The ping code is threadable, which can significantly speed up performance for large lists
    of pings since they will happen concurrently.  For this test with the 15 workers I saw a 10x
    speed improvement.

    This test is flakey because network traffic and server loads are unpredictable, that is
    why retries are built in.
    """
    import random

    test_samples = 15
    num_tries = 3
    # these are popular ping targets that are reliable
    ping_targets = ["google.com", "1.1.1.1", "8.8.8.8", "cloudflare.com", "9.9.9.9"]
    random.shuffle(ping_targets)

    # Randomly pick num_tries (3) different targets
    ping_targets = ping_targets[:num_tries]

    # Try from the list of targets
    for try_number, ping_target in enumerate(ping_targets, start=1):
        logger.info("Run %d- Testing ping on %s", try_number, ping_target)
        # Note: Unthreaded implies 1 worker
        check_rule_pings_threaded = make_check(ping_target, test_samples, workers=test_samples)
        check_rule_pings_not_threaded = make_check(ping_target, test_samples, workers=1)

        tcheck = Ten8tChecker(check_functions=[check_rule_pings_threaded], auto_setup=True)
        ntcheck = Ten8tChecker(check_functions=[check_rule_pings_not_threaded], auto_setup=True)

        tcheck.run_all()
        ntcheck.run_all()

        # WARNING: This looks like I'm forcing the test to pass, HOWEVER in practice this
        #          test is flakey and pings will have random delays.  This makes a crude
        #          effort to run a good test.

        logger.info("Threaded time = %0.3f Single Thread time = %0.3f",
                    tcheck.duration_seconds,
                    ntcheck.duration_seconds)

        speedup = ntcheck.duration_seconds / tcheck.duration_seconds
        # On M1 Mac I see ~8-12x speedup
        logger.info(f"Speedup = {speedup:.02f}x")
        t_data = get_stats([t.runtime_sec for t in tcheck.results])
        nt_data = get_stats([t.runtime_sec for t in ntcheck.results])
        logger.info("Threaded data = %s" % str(t_data))
        logger.info("Single Thread data = %s" % str(nt_data))

        # Check retry conditions, if met, then bail
        if (tcheck.duration_seconds < ntcheck.duration_seconds and
                tcheck.pre_collected and
                ntcheck.perfect_run and
                speedup > 4.0):  # This 4 is arbitrary
            break

    # Verify obvious stuff
    assert len(tcheck.results) == test_samples
    assert tcheck.perfect_run
    assert len(ntcheck.results) == test_samples
    assert ntcheck.perfect_run
    assert speedup > 4.0

    # This is very crude, but 15 pings, expect between 4 and 12 times speed increase.
    assert tcheck.duration_seconds < ntcheck.duration_seconds


@pytest.mark.parametrize(
    "urls, show_summary, show_pass, show_fail, expected_summary_count, expected_pass_count, expected_fail_count",
    [
        # Test case: Combination of summary and pass results
        ("1.1.1.1 8.8.8.8", True, True, False, 1, 2, 0),

        # Test case: Combination of summary and fail results
        ("1.1.1.1 www.invalidurlthatdoesnotexist12345.com", True, False, True, 1, 0, 1),

        # Test case: Show summary only
        ("1.1.1.1 8.8.8.8", True, False, False, 1, 0, 0),

        # Test case: Show passed results only
        ("1.1.1.1 8.8.8.8", False, True, False, 0, 2, 0),

        # Test case: Show failed results only
        ("1.1.1.1 www.invalidurlthatdoesnotexist12345.com", False, False, True, 0, 0, 1),

        # Test case: Combination of summary and pass results
        ("1.1.1.1 8.8.8.8", True, True, False, 1, 2, 0),

        # Add more as needed for edge cases
    ]
)
def test_rule_ping_hosts_check(
        urls, show_summary, show_pass, show_fail, expected_summary_count, expected_pass_count, expected_fail_count
):
    """
    Parameterized test for rule_ping_hosts_check to ensure combinations of show_summary, show_pass, and show_fail
    result in correct output handling with direct validation against expected counts.
    """

    @attributes(tag="tag")
    def check_ping_rule():
        yield from rule_ping_hosts_check(
            urls, yield_summary=show_summary, yield_pass=show_pass, yield_fail=show_fail
        )

    logger.info(f"Running check_ping_rule with URLs: {urls}")
    ch = ten8t_checker.Ten8tChecker(check_functions=[check_ping_rule], auto_setup=True)
    results = ch.run_all()

    # Count results for each type
    summary_count = sum(1 for result in results if result.summary_result)
    pass_count = sum(1 for result in results if not result.summary_result and result.status is True)
    fail_count = sum(1 for result in results if not result.summary_result and result.status is False)

    # Directly compare actual counts with expected counts
    assert summary_count == expected_summary_count, f"Expected {expected_summary_count} summary results, got {summary_count}"
    assert pass_count == expected_pass_count, f"Expected {expected_pass_count} pass results, got {pass_count}"
    assert fail_count == expected_fail_count, f"Expected {expected_fail_count} fail results, got {fail_count}"

    # Verify the total result count matches the total expected count
    total_expected_results = expected_summary_count + expected_pass_count + expected_fail_count
    assert len(results) == total_expected_results, (
        f"Expected {total_expected_results} total results (summary + pass + fail), got {len(results)}"
    )
