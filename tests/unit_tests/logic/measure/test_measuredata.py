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
import numpy as np

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.measure.measure import MeasureData


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = MeasureData(app=App())
    yield


def test_property():
    app.framework = 'raw'
    app.deviceName = 'test'
    assert app.deviceName == 'test'


def test_startCommunication_1():
    suc = app.startCommunication()
    assert not suc


def test_startCommunication_2():
    app.framework = 'raw'
    with mock.patch.object(app.run[app.framework].timerTask,
                           'start'):
        suc = app.startCommunication()
        assert suc


def test_stopCommunication_1():
    suc = app.stopCommunication()
    assert not suc


def test_stopCommunication_2():
    app.framework = 'raw'
    with mock.patch.object(app.run[app.framework].timerTask,
                           'stop'):
        suc = app.stopCommunication()
        assert suc


def test_setEmptyData():
    suc = app.setEmptyData()
    assert suc


def test_calculateReference_1():
    app.raRef = 0
    app.decRef = 0
    app.app.mount.obsSite.raJNow = 1
    app.app.mount.obsSite.decJNow = 1
    app.data['status'] = np.array([])
    ra, dec, raA, decA = app.calculateReference()
    assert ra == 0
    assert dec == 0
    assert raA == 0
    assert decA == 0


def test_calculateReference_2():
    app.raRef = 0
    app.decRef = 0
    app.app.mount.obsSite.raJNow = 1
    app.app.mount.obsSite.decJNow = 1
    app.app.mount.obsSite.angularPosRA = 1
    app.app.mount.obsSite.angularPosDEC = 1
    app.data['status'] = np.array([0, 0, 0, 0, 0])
    ra, dec, raA, decA = app.calculateReference()
    assert round(ra, 0) == 54000
    assert dec == 3600


def test_calculateReference_3():
    app.raRef = 7.5
    app.decRef = 0.5
    app.app.mount.obsSite.raJNow = 1
    app.app.mount.obsSite.decJNow = 1
    app.data['status'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    ra, dec, raA, decA = app.calculateReference()
    assert round(ra, 0) == 27000
    assert dec == 1800


def test_calculateReference_4():
    app.raRef = 27000
    app.decRef = 1800
    app.app.mount.obsSite.raJNow = 1
    app.app.mount.obsSite.decJNow = 1
    app.data['status'] = np.array([0, 0, 0, 0, 1, 0, 0, 0])
    ra, dec, raA, decA = app.calculateReference()
    assert ra == 0
    assert dec == 0


def test_calculateReference_5():
    app.raRef = None
    app.decRef = None
    app.app.mount.obsSite.raJNow = 1
    app.app.mount.obsSite.decJNow = 1
    app.data['status'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    ra, dec, raA, decA = app.calculateReference()
    assert ra == 0
    assert dec == 0
    assert app.raRef is not None
    assert app.decRef is not None


def test_calculateReference_6():
    app.raRef = 0
    app.decRef = 0
    app.angularPosRaRef = 0
    app.angularPosDecRef = 0
    app.app.mount.obsSite.raJNow = 1
    app.app.mount.obsSite.decJNow = 1
    app.data['status'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    ra, dec, raA, decA = app.calculateReference()
    assert round(ra, 0) == 54000
    assert dec == 3600.0


def test_calculateReference_7():
    app.raRef = 0
    app.decRef = 0
    app.angularPosRaRef = 0
    app.angularPosDecRef = 0
    app.app.mount.obsSite.raJNow = 1
    app.app.mount.obsSite.decJNow = 1
    app.data['status'] = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    ra, dec, raA, decA = app.calculateReference()
    assert ra == 0.0
    assert dec == 0.0


def test_calculateReference_8():
    app.raRef = 0
    app.decRef = 0
    app.angularPosRaRef = 0
    app.angularPosDecRef = 0
    app.app.mount.obsSite.raJNow = 1
    app.app.mount.obsSite.decJNow = 1
    app.data['status'] = np.array([None] * 10)
    ra, dec, raA, decA = app.calculateReference()
    assert ra == 0.0
    assert dec == 0.0


def test_checkStart_1():
    suc = app.checkStart(2)
    assert suc


def test_checkStart_2():
    app.shorteningStart = True
    suc = app.checkStart(2)
    assert suc


def test_checkStart_3():
    app.data = {'test': [2, 2, 2]}
    app.shorteningStart = True
    suc = app.checkStart(3)
    assert suc


def test_checkSize_1():
    app.data['time'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.data['temp'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.data['humidity'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.data['press'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.data['dewTemp'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.data['sqr'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.data['raJNow'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.data['decJNow'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.data['status'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.MAXSIZE = 20
    lenData = len(app.data['time'])
    suc = app.checkSize(lenData=lenData)
    assert not suc


def test_checkSize_2():
    app.data['time'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.data['time'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.data['temp'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.data['humidity'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.data['press'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.data['dewTemp'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.data['sqr'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.data['raJNow'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.data['decJNow'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.data['status'] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    app.MAXSIZE = 5
    lenData = len(app.data['time'])
    suc = app.checkSize(lenData=lenData)
    assert suc


def test_getDirectWeather():
    val = app.getDirectWeather()
    assert len(val) == 4


def test_measureTask_1():
    app.mutexMeasure.lock()
    suc = app.measureTask()
    app.mutexMeasure.unlock()
    assert not suc


def test_measureTask_2():
    app.devices = ['sensorWeather']
    app.setEmptyData()
    suc = app.measureTask()
    assert suc


def test_measureTask_3():
    app.devices = ['onlineWeather']
    app.setEmptyData()
    suc = app.measureTask()
    assert suc


def test_measureTask_4():
    app.devices = ['directWeather']
    app.setEmptyData()
    suc = app.measureTask()
    assert suc


def test_measureTask_5():
    app.devices = ['skymeter']
    app.setEmptyData()
    suc = app.measureTask()
    assert suc


def test_measureTask_6():
    app.devices = ['filterwheel']
    app.setEmptyData()
    suc = app.measureTask()
    assert suc


def test_measureTask_7():
    app.devices = ['focuser']
    app.setEmptyData()
    suc = app.measureTask()
    assert suc


def test_measureTask_8():
    app.devices = ['power']
    app.setEmptyData()
    suc = app.measureTask()
    assert suc


def test_measureTask_9():
    app.devices = ['camera']
    app.setEmptyData()
    app.data['timeDiff'] = np.ones(100)
    suc = app.measureTask()
    assert suc
