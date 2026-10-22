# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.base import platformInfo
from mw4.base.signalsDevices import Signals
from mw4.logic.drivers.filter.filterAscom import FilterAscom
from typing import ClassVar
from unittest import mock

if not platformInfo.IS_WINDOWS:
    pytest.skip("skipping windows-only tests", allow_module_level=True)


class Parent:
    def __init__(self, app):
        self.app = app

    data: ClassVar = {}
    signals = Signals()
    deviceType = ""
    loadConfig = True


@pytest.fixture(autouse=True, scope="module")
def function(makeApp):
    func = FilterAscom(parent=Parent(makeApp()))
    func.device = mock.MagicMock()
    func.device.Names = []
    func.device.Position = 1
    yield func


def test_getInitialConfig_noNames(function):
    with (
        mock.patch.object(function, "getAndStoreDeviceProp"),
        mock.patch.object(function, "getDeviceProp", return_value=None),
    ):
        function.getInitialConfig()


def test_getInitialConfig_withNames(function):
    with (
        mock.patch.object(function, "getAndStoreDeviceProp"),
        mock.patch.object(function, "getDeviceProp", return_value=["Red", "Green"]),
        mock.patch.object(function, "storePropertyToData") as m,
    ):
        function.getInitialConfig()
    assert m.call_count == 2


def test_pollData_noPosition(function):
    with mock.patch.object(function, "getDeviceProp", return_value=-1):
        function.pollData()


def test_pollData_nonePosition(function):
    with mock.patch.object(function, "getDeviceProp", return_value=None):
        function.pollData()


def test_pollData_validPosition(function):
    with (
        mock.patch.object(function, "getDeviceProp", return_value=2),
        mock.patch.object(function, "storePropertyToData") as m,
    ):
        function.pollData()
    m.assert_called_once_with(2, "FILTER_SLOT.FILTER_SLOT_VALUE")


def test_sendFilterNumber(function):
    with mock.patch.object(function, "setDevicePropQueued") as m:
        function.sendFilterNumber(3)
    m.assert_called_once_with("Position", 3)
