############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import platform

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.environment.sensorWeatherAscom import SensorWeatherAscom
from base.driverDataClass import Signals
if not platform.system() == 'Windows':
    pytest.skip("skipping windows-only tests", allow_module_level=True)


@pytest.fixture(autouse=True, scope='function')
def function():
    class Test1:
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'
        temperature = 10
        humidity = 85.00
        pressure = 950
        dewpoint = 5.5

    func = SensorWeatherAscom(app=App(), signals=Signals(), data={})
    func.client = Test1()
    func.clientProps = []
    yield func


def test_workerPollData_1(function):
    suc = function.workerPollData()
    assert suc
