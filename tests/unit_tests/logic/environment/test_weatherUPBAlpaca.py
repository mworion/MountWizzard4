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
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.environment.weatherUPBAlpaca import WeatherUPBAlpaca
from base.driverDataClass import Signals


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = WeatherUPBAlpaca(app=App(), signals=Signals(), data={})
    yield


def test_workerPollData_1():
    app.deviceConnected = False
    with mock.patch.object(app,
                           'getAndStoreAlpacaProperty'):
        suc = app.workerPollData()
        assert not suc


def test_workerPollData_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAndStoreAlpacaProperty'):
        suc = app.workerPollData()
        assert suc
