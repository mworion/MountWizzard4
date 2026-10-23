# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
import requests
from mw4.base.httpClient import DEFAULT_TIMEOUT, request, safeRequest
from unittest import mock


def test_request_defaultTimeout():
    with mock.patch.object(requests, "get", return_value="ok") as m:
        assert request("GET", "http://x", params={"a": 1}) == "ok"
    m.assert_called_once_with("http://x", timeout=DEFAULT_TIMEOUT, params={"a": 1})


def test_request_retryThenSuccess():
    with mock.patch.object(requests, "post", side_effect=[requests.Timeout(), "ok"]) as m:
        assert request("post", "http://x", retries=1) == "ok"
    assert m.call_count == 2


def test_request_retryExhausted():
    with (
        mock.patch.object(requests, "get", side_effect=requests.ConnectionError()) as m,
        pytest.raises(requests.ConnectionError),
    ):
        request("get", "http://x", retries=2)
    assert m.call_count == 3


def test_request_noRetryOnOtherError():
    with (
        mock.patch.object(requests, "get", side_effect=requests.HTTPError()) as m,
        pytest.raises(requests.HTTPError),
    ):
        request("get", "http://x", retries=2)
    assert m.call_count == 1


def test_safeRequest_success():
    with mock.patch.object(requests, "get", return_value="ok"):
        assert safeRequest("get", "http://x") == "ok"


@pytest.mark.parametrize("error", [requests.RequestException(), OSError()])
def test_safeRequest_failure(error):
    with mock.patch.object(requests, "get", side_effect=error):
        assert safeRequest("get", "http://x") is None
