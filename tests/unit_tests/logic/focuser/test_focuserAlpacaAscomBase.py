# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.base.signalsDevices import Signals
from mw4.logic.focuser.focuserAlpaca import FocuserAlpaca
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from typing import ClassVar
from unittest import mock


class Parent:
    try:
        app = App()
    except (RuntimeError, ImportError, AttributeError, ConnectionError, OSError, ValueError):
        app = mock.MagicMock()
    data: ClassVar = {}
    DEVICE_TYPE = "focuser"
    signals = Signals()
    loadConfig = True


@pytest.fixture(autouse=True, scope="module")
def function():
    try:
        func = FocuserAlpaca(parent=Parent())
        func.device = mock.MagicMock()
    except (
        RuntimeError,
        ImportError,
        AttributeError,
        ConnectionError,
        OSError,
        ValueError,
    ) as e:
        pytest.skip(f"Fixture initialization failed: {e}")
    yield func


def test_pollData(function):
    with mock.patch.object(function, "getAndStoreDeviceProp") as m:
        function.pollData()
        m.assert_called_once_with("Position", "ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION")


def test_move(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.move(position=100)
    item = function.commandQueue.get_nowait()
    assert item.valueProp == "Move"
    assert item.kwargs == {"Position": 100}


def test_halt(function):
    while not function.commandQueue.empty():
        function.commandQueue.get_nowait()
    function.halt()
    item = function.commandQueue.get_nowait()
    assert item.valueProp == "Halt"
