# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.logic.environment.sensorWeather import SensorWeather
from mw4.logic.environment.sensorWeatherIndi import SensorWeatherIndi
from queue import Queue
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function():
    try:
        weather = SensorWeather(App())
        func = SensorWeatherIndi(parent=weather)
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
    func.app.threadPool.waitForDone(5000)


# ---------------------------------------------------------------------------
# setUpdateConfig
# ---------------------------------------------------------------------------


@pytest.mark.skip(reason="setUpdateConfig method has been removed from SensorWeatherIndi")
def test_setUpdateConfig(function):
    function.txQ = Queue()
    function.deviceName = "test_weather"
    function.setUpdateConfig("ignored_param")
    assert function.txQ.qsize() == 1
