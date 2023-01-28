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
import unittest.mock as mock

# external packages
import numpy as np
from skyfield.api import Angle

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.measure.measure import MeasureData


@pytest.fixture(autouse=True, scope='function')
def function():
    func = MeasureData(app=App())
    yield func


def test_property(function):
    function.framework = 'raw'
    function.deviceName = 'test'
    assert function.deviceName == 'test'


def test_startCommunication_1(function):
    suc = function.startCommunication()
    assert not suc


def test_startCommunication_2(function):
    function.framework = 'raw'
    with mock.patch.object(function.run[function.framework].timerTask,
                           'start'):
        suc = function.startCommunication()
        assert suc


def test_stopCommunication_1(function):
    suc = function.stopCommunication()
    assert not suc


def test_stopCommunication_2(function):
    function.framework = 'raw'
    with mock.patch.object(function.run[function.framework].timerTask,
                           'stop'):
        suc = function.stopCommunication()
        assert suc


def test_setEmptyData(function):
    suc = function.setEmptyData()
    assert suc


def test_calculateReference_1(function):
    function.raRef = 0
    function.decRef = 0
    function.app.mount.obsSite.raJNow = None
    function.app.mount.obsSite.decJNow = None
    function.data['status'] = np.array([])
    ra, dec, raA, decA = function.calculateReference()
    assert ra == 0
    assert dec == 0
    assert raA == 0
    assert decA == 0


def test_calculateReference_2(function):
    function.raRef = 0
    function.decRef = 0
    function.app.mount.obsSite.raJNow = Angle(hours=0)
    function.app.mount.obsSite.decJNow = Angle(degrees=0)
    function.app.mount.obsSite.angularPosRA = Angle(degrees=0)
    function.app.mount.obsSite.angularPosDEC = Angle(degrees=0)
    function.data['status'] = np.array([0, 0, 0, 0, 0])
    ra, dec, raA, decA = function.calculateReference()
    assert round(ra, 0) == 0
    assert dec == 0


def test_calculateReference_3(function):
    function.raRef = 7.5
    function.decRef = 0.5
    function.app.mount.obsSite.raJNow = Angle(hours=0)
    function.app.mount.obsSite.decJNow = Angle(degrees=0)
    function.data['status'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    ra, dec, raA, decA = function.calculateReference()
    assert round(ra, 0) == -27000
    assert dec == -1800


def test_calculateReference_4(function):
    function.raRef = 27000
    function.decRef = 1800
    function.app.mount.obsSite.raJNow = Angle(hours=0)
    function.app.mount.obsSite.decJNow = Angle(degrees=0)
    function.data['status'] = np.array([0, 0, 0, 0, 1, 0, 0, 0])
    ra, dec, raA, decA = function.calculateReference()
    assert ra == 0
    assert dec == 0


def test_calculateReference_5(function):
    function.raRef = None
    function.decRef = None
    function.app.mount.obsSite.raJNow = Angle(hours=0)
    function.app.mount.obsSite.decJNow = Angle(degrees=0)
    function.data['status'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    ra, dec, raA, decA = function.calculateReference()
    assert ra == 0
    assert dec == 0
    assert function.raRef is not None
    assert function.decRef is not None


def test_calculateReference_6(function):
    function.raRef = 0
    function.decRef = 0
    function.angularPosRaRef = 0
    function.angularPosDecRef = 0
    function.app.mount.obsSite.raJNow = Angle(hours=0)
    function.app.mount.obsSite.decJNow = Angle(degrees=0)
    function.data['status'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    ra, dec, raA, decA = function.calculateReference()
    assert round(ra, 0) == 0
    assert dec == 0


def test_calculateReference_7(function):
    function.raRef = 0
    function.decRef = 0
    function.angularPosRaRef = 0
    function.angularPosDecRef = 0
    function.app.mount.obsSite.raJNow = Angle(hours=0)
    function.app.mount.obsSite.decJNow = Angle(degrees=0)
    function.data['status'] = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    ra, dec, raA, decA = function.calculateReference()
    assert ra == 0.0
    assert dec == 0.0


def test_calculateReference_8(function):
    function.raRef = 0
    function.decRef = 0
    function.angularPosRaRef = 0
    function.angularPosDecRef = 0
    function.app.mount.obsSite.raJNow = Angle(hours=0)
    function.app.mount.obsSite.decJNow = Angle(degrees=0)
    function.data['status'] = np.array([None] * 10)
    ra, dec, raA, decA = function.calculateReference()
    assert ra == 0.0
    assert dec == 0.0


def test_checkStart_1(function):
    suc = function.checkStart(2)
    assert suc


def test_checkStart_2(function):
    function.shorteningStart = True
    suc = function.checkStart(2)
    assert suc


def test_checkStart_3(function):
    function.data = {'test': [2, 2, 2]}
    function.shorteningStart = True
    suc = function.checkStart(3)
    assert suc


def test_checkSize_1(function):
    function.data['time'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.data['temp'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.data['humidity'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.data['press'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.data['dewTemp'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.data['sqr'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.data['raJNow'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.data['decJNow'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.data['status'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.MAXSIZE = 20
    lenData = len(function.data['time'])
    suc = function.checkSize(lenData=lenData)
    assert not suc


def test_checkSize_2(function):
    function.data['time'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.data['time'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.data['temp'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.data['humidity'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.data['press'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.data['dewTemp'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.data['sqr'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.data['raJNow'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.data['decJNow'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.data['status'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.MAXSIZE = 5
    lenData = len(function.data['time'])
    suc = function.checkSize(lenData=lenData)
    assert suc


def test_getDirectWeather(function):
    function.app.mount.setting.weatherTemperature = None
    function.app.mount.setting.weatherPressure = None
    function.app.mount.setting.weatherDewPoint = None
    function.app.mount.setting.weatherHumidity = None
    val = function.getDirectWeather()
    assert len(val) == 4


def test_measureTask_1(function):
    function.mutexMeasure.lock()
    suc = function.measureTask()
    function.mutexMeasure.unlock()
    assert not suc


def test_measureTask_2(function):
    function.devices = ['sensorWeather']
    function.setEmptyData()
    suc = function.measureTask()
    assert suc


def test_measureTask_3(function):
    function.devices = ['onlineWeather']
    function.setEmptyData()
    suc = function.measureTask()
    assert suc


def test_measureTask_4(function):
    function.devices = ['directWeather']
    function.setEmptyData()
    suc = function.measureTask()
    assert suc


def test_measureTask_5(function):
    function.devices = ['skymeter']
    function.setEmptyData()
    suc = function.measureTask()
    assert suc


def test_measureTask_6(function):
    function.devices = ['filterwheel']
    function.setEmptyData()
    suc = function.measureTask()
    assert suc


def test_measureTask_7(function):
    function.devices = ['focuser']
    function.setEmptyData()
    suc = function.measureTask()
    assert suc


def test_measureTask_8(function):
    function.devices = ['power']
    function.setEmptyData()
    suc = function.measureTask()
    assert suc


def test_measureTask_9(function):
    function.devices = ['camera']
    function.setEmptyData()
    function.data['timeDiff'] = np.ones(30)
    suc = function.measureTask()
    assert suc
