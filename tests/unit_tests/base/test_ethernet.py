# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

import pytest
import socket
import wakeonlan
from mw4.base.ethernet import checkFormatMAC, getLocalAddress, getSubnetBroadcast, sendWakeOnLan
from unittest import mock


def test_checkFormatMAC_1():
    val = checkFormatMAC("")
    assert not val


def test_checkFormatMAC_2():
    val = checkFormatMAC(1234)
    assert not val


def test_checkFormatMAC_3():
    val = checkFormatMAC("00:00:00")
    assert not val


def test_checkFormatMAC_4():
    val = checkFormatMAC("00:00:00:123:00:00")
    assert not val


def test_checkFormatMAC_5():
    val = checkFormatMAC("00:00:00:12K:00:00")
    assert not val


def test_checkFormatMAC_6():
    val = checkFormatMAC("00:00:00:12:00:00")
    assert val == "00:00:00:12:00:00"


def test_checkFormatMAC_7():
    val = checkFormatMAC("00:L0:00:12:00:00")
    assert not val


def test_getLocalAddress_1():
    assert getLocalAddress("127.0.0.1") == "127.0.0.1"


def test_getLocalAddress_2():
    with mock.patch.object(socket, "gethostbyname", side_effect=socket.gaierror):
        assert getLocalAddress("invalid") is None


def test_getSubnetBroadcast_1():
    assert getSubnetBroadcast("10.1.2.3") == "10.1.2.255"


def test_sendWakeOnLan_1():
    with mock.patch.object(wakeonlan, "wake") as mockWake:
        sendWakeOnLan("AA:BB:CC:DD:EE:FF", "255.255.255.255", 9, "10.1.2.3")
        mockWake.assert_called_once_with("AA:BB:CC:DD:EE:FF", host="255.255.255.255", port=9)


def test_sendWakeOnLan_2():
    with (
        mock.patch.object(wakeonlan, "wake", side_effect=[OSError, None]) as mockWake,
        mock.patch("mw4.base.ethernet.getLocalAddress", return_value="192.168.40.222"),
    ):
        sendWakeOnLan("AA:BB:CC:DD:EE:FF", "255.255.255.255", 9, "mount.uranus")
        assert mockWake.call_count == 2
        assert mockWake.call_args.kwargs == {
            "host": "192.168.40.255",
            "port": 9,
            "interface": "192.168.40.222",
        }


def test_sendWakeOnLan_3():
    with (
        mock.patch.object(wakeonlan, "wake", side_effect=OSError),
        mock.patch("mw4.base.ethernet.getLocalAddress", return_value=None),
        pytest.raises(OSError),
    ):
        sendWakeOnLan("AA:BB:CC:DD:EE:FF", "255.255.255.255", 9, "invalid")


def test_sendWakeOnLan_4():
    with (
        mock.patch.object(wakeonlan, "wake", side_effect=OSError) as mockWake,
        mock.patch("mw4.base.ethernet.getLocalAddress", return_value="10.1.2.3"),
        pytest.raises(OSError),
    ):
        sendWakeOnLan("AA:BB:CC:DD:EE:FF", "10.1.2.255", 9, "10.1.2.3")
    mockWake.assert_called_once()
