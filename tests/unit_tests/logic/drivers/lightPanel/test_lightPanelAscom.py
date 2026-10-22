# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.base import platformInfo
from mw4.base.signalsDevices import Signals
from mw4.logic.drivers.lightPanel.lightPanelAscom import LightPanelAscom
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
    func = LightPanelAscom(parent=Parent(makeApp()))
    func.device = mock.MagicMock()
    func.device.Brightness = 100
    func.device.MaxBrightness = 255
    yield func


def test_pollData_1(function):
    with mock.patch.object(function, "getAndStoreDeviceProp"):
        function.pollData()


def test_lightOn(function):
    function.app.dReg.d["lightPanel"].instance.data = {
        "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_MAX": 200
    }
    with mock.patch.object(function, "callDeviceMethodQueued") as m:
        function.lightOn()
    m.assert_called_once_with("CalibratorOn", BrightnessVal=100)


def test_lightOff(function):
    with mock.patch.object(function, "callDeviceMethodQueued") as m:
        function.lightOff()
    m.assert_called_once_with("CalibratorOff")


def test_lightIntensity(function):
    with mock.patch.object(function, "callDeviceMethodQueued") as m:
        function.lightIntensity(128.0)
    m.assert_called_once_with("CalibratorOn", BrightnessVal=128.0)
