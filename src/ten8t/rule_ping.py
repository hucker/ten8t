"""
This module provides functionality for performing ICMP ping checks on one or more hosts. This
module supports running pings in parallel by setting max_workers to a number large than the
default of 1.  This can dramatically increase speed.

The main functions in this module are:
- `handle_empty_hosts`: Handles scenarios where no hosts are provided and decides whether to
  skip or pass based on the provided flags.
- `rule_ping_host_check`: Performs a ping operation on a single host and returns the result.
- `rule_ping_hosts_check`: Allows for concurrent or sequential pinging of multiple hosts, using
  threading for improved performance with larger host lists.

Functions:
- handle_empty_hosts: Generates a result for scenarios where no hosts are available for
  processing, based on skip_on_none and `pass_on_none` flags.
- rule_ping_host_check: Sends a single ICMP ping request to the given host and evaluates the
  response.
- rule_ping_hosts_check: Handles ping checks for multiple hosts, supports concurrent
  operations using a thread pool, and processes the results.

This module relies on the ping3 library for sending ICMP packets and measuring the latency
of responses.

"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Generator

import ping3  # type: ignore

import ten8t
from .render import BM
from .ten8t_logging import ten8t_logger
from .ten8t_result import TR
from .ten8t_util import StrListOrNone, any_to_str_list

NO_HOSTS_MSG = "No hosts provided for ping."
MIN_LATENCY_MS = 0.0001
ALLOWED_PING_WORKERS = 100


def handle_empty_hosts(skip_on_none: bool, pass_on_none: bool) -> TR:
    """
    Handles cases where there are no hosts available for processing.

    This function evaluates the given parameters `skip_on_none` and `pass_on_none`
    to determine the behavior when no hosts are present. Depending on these values,
    it either skips processing or passes with no action.

    Args:
        skip_on_none (bool): A flag indicating whether to skip the operation
            if no hosts are present. If True, a status with a skipped flag
            is returned.
        pass_on_none (bool): A flag determining whether to pass the operation
            with no action if no hosts are present. If `skip_on_none` is False,
            this value is used to set the operation status.

    Returns:
        TR: A TR object indicating the result of the evaluation, including
            the operation status and a message.
    """
    if skip_on_none:
        return TR(status=True, skipped=True, msg=NO_HOSTS_MSG)
    return TR(status=pass_on_none, msg=NO_HOSTS_MSG)


def rule_ping_host_check(host: str,
                         timeout_sec: int) -> TR:
    """
    Perform a ping check for a single host.

    Note that this rule function returns rather than yields.  This simplifies
    upstream code.

    Args:
        host (str): The host to ping.
        timeout_sec (int): The time in seconds to wait for the ping response.

    Yields:
        TR: A single result object indicating the outcome of the ping check.

    Raises:
        ValueError: If timeout_sec is <= 0.
        Ten8tException: If an unexpected error occurs during pinging.
    """

    timeout_str = f'{timeout_sec:0.03f}'

    try:
        if timeout_sec <= 0:
            return TR(
                status=False,
                msg=f"Ping timeout must be > 0 for {BM.code(host)} timeout = {BM.code(timeout_str)} ms"
            )

        # Perform the ping call
        latency = ping3.ping(host, timeout=timeout_sec, unit='ms')

        if latency is None or latency < MIN_LATENCY_MS:
            return TR(
                status=False,
                msg=f"No ping response from server {BM.code(host)} timeout = {BM.code(timeout_str)} ms"
            )
        else:
            latency_str = f"{latency:0.1f}"
            return TR(
                status=True,
                msg=f"Host {BM.code(host)} is up, response time = {BM.code(latency_str)} ms"
            )
    except Exception as e:
        # We carry on here since we do not want to crash the app
        emsg = f"An error occurred while processing {host=}: {str(e)}"
        ten8t_logger.error(emsg)
        return TR(status=False, msg=emsg, except_=e)


def rule_ping_hosts_check(
        hosts: StrListOrNone = None,
        ping_timeout_sec: int = 4,
        skip_on_none: bool = False,
        pass_on_none: bool = False,
        max_workers: int = 1,
        emit_summary: bool = False,
        emit_pass: bool = True,
        emit_fail: bool = True,
        yielder: ten8t.Ten8tYield = None,
) -> Generator[TR, None, None]:
    """
    Perform ping checks for a list of hosts or a single host.  This supports he
    full ten8t_yield mechanism allowing any combination of results to be provided.

    Args:
        hosts (StrListOrNone): A single host as a string or a list of hosts.
        ping_timeout_sec (float): Time in seconds to wait for ping responses (default: 4.0).
        skip_on_none (bool): If True, skip execution if no hosts are provided.
        pass_on_none (bool): If True, consider an empty host list a successful test.
        max_workers (int): Maximum number of allowed workers.
        emit_summary (bool): Yield the summary result
        emit_pass (bool): Yield pass results if True.
        emit_fail (bool): Yield fail results if True
        yielder (Ten8tYield): Yield class.

    Yields:
        TR: A generator yielding result objects for each host pinged.
    """
    if max_workers <= 0:
        ten8t_logger.warning(
            "Requested %d threads is non-positive, using 1 worker.",
            max_workers,
        )
        max_workers = 1
    elif max_workers > ALLOWED_PING_WORKERS:
        requested_workers = max_workers  # Save the original value for logging
        max_workers = ALLOWED_PING_WORKERS
        ten8t_logger.warning(
            "Requested %d threads exceeds the maximum allowed (%d). Using the maximum value of %d.",
            requested_workers,
            ALLOWED_PING_WORKERS,
            max_workers
        )

    # Let the user pass a yield object, this can make for cleaner code by reducing param counts
    if yielder:
        y = yielder
    else:
        y = ten8t.Ten8tYield(emit_summary=emit_summary,
                             emit_pass=emit_pass,
                             emit_fail=emit_fail,
                             summary_name="Ping Check")

    # Normalize the input (convert string of hosts to a list)
    hosts = any_to_str_list(hosts)

    # Handle the case when no hosts are provided
    if len(hosts) == 0:
        yield handle_empty_hosts(skip_on_none, pass_on_none)
        return

    # Single thread this with no overhead
    if max_workers <= 1:
        for host in hosts:
            yield from y(rule_ping_host_check(host, ping_timeout_sec))
    else:

        # Multi thread these guys since ping can multithread
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Map futures to corresponding hosts.  Surprising to me that futures are hashable.
            futures = {
                executor.submit(rule_ping_host_check, host, ping_timeout_sec): host for host in hosts
            }

            for future in as_completed(futures):
                # host = futures[future]  # If you want logging?
                yield from y(future.result())

    yield from y.yield_summary()
