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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

# external packages
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

# local import
from mw4.environment.sensorWeatherAlpaca import SensorWeatherAlpaca
from mw4.environment.sensorWeather import SensorWeatherSignals
from mw4.base.alpacaBase import AlpacaBase


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)

    global app
    app = SensorWeatherAlpaca(app=Test(), signals=SensorWeatherSignals(), data={})

    yield


def test_getInitialConfig_1():
    with mock.patch.object(AlpacaBase,
                           'get'):
        suc = app.getInitialConfig()
        assert suc


def test_workerPollData_1():
    with mock.patch.object(AlpacaBase,
                           'get'):
        suc = app.workerPollData()
        assert suc
