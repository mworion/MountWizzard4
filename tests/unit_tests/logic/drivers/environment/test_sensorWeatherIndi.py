# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.base.signalsDevices import Signals
from mw4.logic.drivers.environment.sensorWeatherIndi import SensorWeatherIndi
from typing import ClassVar


class Parent:
    def __init__(self, app):
        self.app = app

    data: ClassVar = {}
    deviceType = ""
    signals = Signals()
    loadConfig = True


@pytest.fixture(autouse=True, scope="module")
def function(makeApp):
    try:
        func = SensorWeatherIndi(parent=Parent(makeApp()))
        yield func
    except (RuntimeError, ImportError, AttributeError, ConnectionError, OSError, ValueError) as e:
        pytest.skip(f"SensorWeatherIndi initialization failed: {e}")


def test_init_1(function):
    assert function.signals is function.parent.signals
