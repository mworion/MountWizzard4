############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import platform

import pytest
from mw4.base.signalsDevices import Signals
from mw4.logic.environment.sensorWeatherAscom import SensorWeatherAscom

# external packages
# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App

if not platform.system() == "Windows":
    pytest.skip("skipping windows-only tests", allow_module_level=True)


class Parent:
    app = App()
    data = {}
    deviceType = ""
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="function")
def function():
    class Test1:
        Name = "test"
        DriverVersion = "1"
        DriverInfo = "test1"
        temperature = 10
        humidity = 85.00
        pressure = 950
        dewpoint = 5.5

    func = SensorWeatherAscom(parent=Parent())
    func.client = Test1()
    func.clientProps = []
    yield func


def test_workerPollData_1(function):
    function.workerPollData()
