############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
import pytest
from mw4.logic.environment.sensorWeather import SensorWeather
from mw4.logic.environment.sensorWeatherIndi import SensorWeatherIndi
from queue import Queue
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function():
    weather = SensorWeather(App())
    func = SensorWeatherIndi(parent=weather)
    yield func
    func.app.threadPool.waitForDone(5000)


# ---------------------------------------------------------------------------
# setUpdateConfig
# ---------------------------------------------------------------------------


def test_setUpdateConfig(function):
    function.txQ = Queue()
    function.deviceName = "test_weather"
    function.setUpdateConfig("ignored_param")
    assert function.txQ.qsize() == 1
