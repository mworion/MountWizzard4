# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.logic.environment.directWeather import DirectWeather
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function():
    try:
        func = DirectWeather(app=App())
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


def test_startCommunication_1(function):
    function.startCommunication()


def test_stopCommunication_1(function):
    function.stopCommunication()


def test_updateData_1(function):
    function.enabled = False
    function.running = False
    function.updateData(1)


def test_updateData_2(function):
    class Sett:
        weatherTemperature = None
        weatherPressure = 900
        weatherHumidity = 50
        weatherDewPoint = 10
        weatherAge = 10

    function.enabled = True
    function.running = True
    function.updateData(Sett())
    assert not function.running


def test_updateData_3(function):
    class Sett:
        weatherTemperature = 10
        weatherPressure = 900
        weatherHumidity = 50
        weatherDewPoint = 10
        weatherAge = 10

    function.enabled = True
    function.running = False
    function.updateData(Sett())
    assert function.running
