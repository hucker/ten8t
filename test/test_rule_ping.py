import pytest

from ten8t import Ten8tChecker
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
        yield from rule_ping_hosts_check(urls)

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


def test_ping_threading():
    # The ping code is threadable, which can significantly speed up performance for large lists
    # of pings since they will happen concurrently.  For this test with the 15 workers I saw a 10x
    # speed improvement.
    test_samples = 15

    @attributes(tag="tag")
    def check_rule_pings_threaded():
        yield from rule_ping_hosts_check(["google.com"] * test_samples, max_workers=test_samples)

    def check_rule_pings_not_threaded():
        yield from rule_ping_hosts_check(["google.com"] * test_samples, max_workers=1)

    tcheck = Ten8tChecker(check_functions=[check_rule_pings_threaded], auto_setup=True)
    ntcheck = Ten8tChecker(check_functions=[check_rule_pings_not_threaded], auto_setup=True)

    tcheck.run_all()
    ntcheck.run_all()

    # NOTE: This is really running a ping against google and is depending on this "basically working consistantly"
    #       This has all sorts of possible issues that can/will make this test flakey
    assert len(tcheck.results) == test_samples
    assert tcheck.perfect_run
    assert len(ntcheck.results) == test_samples
    assert ntcheck.perfect_run

    # For 15 pings I have seen between 4 and 11 times speed increase.
    assert tcheck.duration_seconds < ntcheck.duration_seconds
