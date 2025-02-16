"""
This module provides functions for using ping to verify network connectivity.


"""
from typing import Generator

import ping3

from .ten8t_format import BM
from .ten8t_result import TR

NO_HOSTS_MSG = "No hosts provided for ping."
MIN_LATENCY_MS = 0.0001


def rule_ping_check(hosts: str | list, timeout_ms: float = 4000.0, skip_on_none=False, pass_on_none=False) -> Generator[
    TR, None, None]:
    """
    Given a sequence of hosts perform ping checks against each of them given a single timeout
    value.  This function handles the following:
    hosts = "google.com"   converted to ["google.com"]
    hosts = "google.com apple.com"   converted to ["google.com","apple.com"]
    hosts = ["google.com"]   as is
    Args:
        hosts: string with list of hosts or list of hosts
        timeout_ms(4000): Time in milliseconds.
        skip_on_none(False): If true an empty host list is a skip
        pass_on_none(False): If try the tests passes on empty host list
    Yields:
        list of results
    """
    hosts = hosts.replace(',', ' ').split() if isinstance(hosts, str) else hosts

    if len(hosts) == 0:
        if skip_on_none:
            yield TR(status=True, skipped=True, msg=NO_HOSTS_MSG)
            return
        else:
            yield TR(status=pass_on_none, msg=NO_HOSTS_MSG)
            return

    for host in hosts:
        try:
            # All of this to make this call
            latency = ping3.ping(host, timeout=timeout_ms, unit='ms')
            timeout_str = f'{timeout_ms:0.1f}'
            if latency is False:
                yield TR(status=False,
                         msg=f"No ping response from server {BM.code(host)} timeout = {BM.code(timeout_str)} ms")
            elif latency < MIN_LATENCY_MS:
                latency_str = f"{MIN_LATENCY_MS:0.1f}"
                yield TR(status=True, msg=f"Host {BM.code(host)} is up: response time < {BM.code(latency_str)} ms")
            else:
                latency_str = f"{latency:0.1f}"
                yield TR(status=True, msg=f"Host {BM.code(host)} is up, response time = {BM.code(latency_str)} ms")
        except Exception:
            # Document your exception handling logic here
            yield TR(status=False, msg=f"Host {BM.code(host)} not found: {BM.fail(host)}")
