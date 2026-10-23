# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
import requests
from typing import Any

log = logging.getLogger("MW4")

DEFAULT_TIMEOUT = 10


def request(
    method: str,
    url: str,
    timeout: float = DEFAULT_TIMEOUT,
    retries: int = 0,
    **kwargs: Any,
) -> requests.Response:
    """Send an HTTP request with a default timeout.

    Connection errors and timeouts are retried `retries` times, any other
    error and the last failure are raised to the caller.
    """
    func = getattr(requests, method.lower())
    attempt = 0
    while True:
        try:
            return func(url, timeout=timeout, **kwargs)
        except (requests.ConnectionError, requests.Timeout) as e:
            if attempt >= retries:
                raise
            attempt += 1
            log.debug("[%s] retry %d/%d after: %s", url, attempt, retries, e)


def safeRequest(
    method: str,
    url: str,
    timeout: float = DEFAULT_TIMEOUT,
    retries: int = 0,
    **kwargs: Any,
) -> requests.Response | None:
    """Like request, but logs the failure and returns None instead of raising."""
    try:
        return request(method, url, timeout=timeout, retries=retries, **kwargs)
    except (requests.RequestException, OSError) as e:
        log.warning("[%s] request failed: [%s]", url, e)
        return None
