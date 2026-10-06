# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import platform
import pytest
from mw4.base.signalsDevices import Signals
from mw4.logic.environment.sensorWeatherAscom import SensorWeatherAscom
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from typing import ClassVar
from unittest import mock

if platform.system() != "Windows":
    pytest.skip("skipping windows-only tests", allow_module_level=True)


class Parent:
    try:
        app = App()
    except (RuntimeError, ImportError, AttributeError, ConnectionError, OSError, ValueError):
        app = mock.MagicMock()
    data: ClassVar = {}
    deviceType = ""
    signals = Signals()
    loadConfig = True


@pytest.fixture(autouse=True, scope="module")
def function():
    func = SensorWeatherAscom(parent=Parent())
    func.device = mock.MagicMock()
    yield func


def test_pollData_1(function):
    with mock.patch.object(function, "getAndStoreDeviceProp"):
        function.pollData()
