# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

import pytest
from mw4.base import platformInfo
from mw4.base.signalsDevices import Signals
from mw4.logic.drivers.cover.coverAscom import CoverAscom
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
    func = CoverAscom(parent=Parent(makeApp()))
    func.device = mock.MagicMock()
    func.device.CoverState = 1
    yield func


def test_pollData_1(function):
    with (
        mock.patch.object(function, "getDeviceProp", return_value=1),
        mock.patch.object(function, "storePropertyToData"),
    ):
        function.pollData()


def test_pollData_2(function):
    with (
        mock.patch.object(function, "getDeviceProp", return_value=0),
        mock.patch.object(function, "storePropertyToData"),
    ):
        function.pollData()


def test_closeCover(function):
    with mock.patch.object(function, "callDeviceMethodQueued") as m:
        function.closeCover()
    m.assert_called_once_with("CloseCover")


def test_openCover(function):
    with mock.patch.object(function, "callDeviceMethodQueued") as m:
        function.openCover()
    m.assert_called_once_with("OpenCover")


def test_haltCover(function):
    with mock.patch.object(function, "callDeviceMethodQueued") as m:
        function.haltCover()
    m.assert_called_once_with("HaltCover")
