# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.base import platformInfo
from mw4.base.signalsDevices import Signals
from mw4.logic.drivers.environment.sensorWeatherAscom import SensorWeatherAscom
from typing import ClassVar
from unittest import mock

if not platformInfo.IS_WINDOWS:
    pytest.skip("skipping windows-only tests", allow_module_level=True)


class Parent:
    def __init__(self, app):
        self.app = app

    data: ClassVar = {}
    deviceType = ""
    signals = Signals()
    loadConfig = True


@pytest.fixture(autouse=True, scope="module")
def function(makeApp):
    func = SensorWeatherAscom(parent=Parent(makeApp()))
    func.device = mock.MagicMock()
    yield func


def test_pollData_1(function):
    with mock.patch.object(function, "getAndStoreDeviceProp"):
        function.pollData()
