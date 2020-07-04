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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import platform
import faulthandler
faulthandler.enable()

# external packages
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
if platform.system() == 'Windows':
    import win32com.client
    import pythoncom

# local import
from mw4.environment.sensorWeatherAscom import SensorWeatherAscom
from mw4.environment.sensorWeather import SensorWeatherSignals


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test1:
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'
        temperature = 10
        humidity = 85.00
        pressure = 950
        dewpoint = 5.5

    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)

    global app

    app = SensorWeatherAscom(app=Test(), signals=SensorWeatherSignals(), data={})
    app.client = Test1()
    yield


def test_getInitialConfig_1():
    suc = app.getInitialConfig()
    assert suc


def test_workerPollData_1():
    app.deviceConnected = False
    suc = app.workerPollData()
    assert not suc


def test_workerPollData_2():
    app.deviceConnected = True
    suc = app.workerPollData()
    assert suc
