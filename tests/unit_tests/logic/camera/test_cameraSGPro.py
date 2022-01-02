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
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock
import os

# external packages
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal
from skyfield.api import Angle, wgs84

# local import
from mountcontrol.mount import Mount
from logic.camera.cameraSGPro import CameraSGPro
from base.driverDataClass import Signals
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class TestApp:
        threadPool = QThreadPool()

    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/workDir/data')
        mount.obsSite.location = wgs84.latlon(latitude_degrees=0,
                                              longitude_degrees=0,
                                              elevation_m=0)
        mount.obsSite.raJNow = Angle(hours=12)
        mount.obsSite.decJNow = Angle(degrees=45)
        deviceStat = {'mount': True}

    global app
    app = CameraSGPro(app=Test(), signals=Signals(), data={})
    yield


def test_sgGetCameraTemp_1():
    with mock.patch.object(app,
                           'requestProperty',
                           return_value=None):
        suc, val = app.sgGetCameraTemp()
        assert not suc
        assert val == {}


def test_sgGetCameraTemp_2():
    with mock.patch.object(app,
                           'requestProperty',
                           return_value={'Success': True}):
        suc, val = app.sgGetCameraTemp()
        assert suc
        assert val == {'Success': True}


def test_sgSetCameraTemp_1():
    with mock.patch.object(app,
                           'requestProperty',
                           return_value=None):
        suc = app.sgSetCameraTemp(temperature=10)
        assert not suc


def test_sgSetCameraTemp_2():
    with mock.patch.object(app,
                           'requestProperty',
                           return_value={'Success': True}):
        suc = app.sgSetCameraTemp(temperature=10)
        assert suc


def test_sgAbortImage_1():
    with mock.patch.object(app,
                           'requestProperty',
                           return_value=None):
        suc = app.sgAbortImage()
        assert not suc


def test_sgAbortImage_2():
    with mock.patch.object(app,
                           'requestProperty',
                           return_value={'Success': True}):
        suc = app.sgAbortImage()
        assert suc


def test_sgGetImagePath_1():
    with mock.patch.object(app,
                           'requestProperty',
                           return_value=None):
        suc = app.sgGetImagePath(receipt='1')
        assert not suc


def test_sgGetImagePath_2():
    with mock.patch.object(app,
                           'requestProperty',
                           return_value={'Success': True}):
        suc = app.sgGetImagePath(receipt='1')
        assert suc


def test_sgGetCameraProps_1():
    with mock.patch.object(app,
                           'requestProperty',
                           return_value=None):
        suc, val = app.sgGetCameraProps()
        assert not suc
        assert val == {}


def test_sgGetCameraProps_2():
    with mock.patch.object(app,
                           'requestProperty',
                           return_value={'Success': True}):
        suc, val = app.sgGetCameraProps()
        assert suc
        assert val == {'Success': True}


def test_workerGetInitialConfig_1():
    with mock.patch.object(app,
                           'sgGetCameraProps',
                           return_value=(False, {})):
        suc = app.workerGetInitialConfig()
        assert not suc


def test_workerGetInitialConfig_2():
    val = {
        'Message': 'test',
        'CanSubFrame': True,
        'NumPixelsX': 1000,
        'NumPixelsY': 500,
    }
    with mock.patch.object(app,
                           'sgGetCameraProps',
                           return_value=(True, val)):
        suc = app.workerGetInitialConfig()
        assert suc


def test_workerPollData_1():
    app.data['CAN_FAST'] = True
    with mock.patch.object(app,
                           'sgGetCameraTemp',
                           return_value=(False, None)):
        suc = app.workerPollData()
        assert not suc


def test_workerPollData_2():
    app.data['CAN_FAST'] = True
    with mock.patch.object(app,
                           'sgGetCameraTemp',
                           return_value=(True, {'Temperature': 10})):
        suc = app.workerPollData()
        assert suc


def test_sendDownloadMode_1():
    app.data['CAN_FAST'] = True
    with mock.patch.object(app,
                           'storePropertyToData'):
        suc = app.sendDownloadMode()
        assert suc


def test_workerExpose_1():
    with mock.patch.object(app,
                           'sgCaptureImage',
                           return_value=(False, None)):
        suc = app.workerExpose()
        assert not suc


def test_workerExpose_2():
    with mock.patch.object(app,
                           'sgCaptureImage',
                           return_value=(True, {})):
        suc = app.workerExpose()
        assert not suc


def test_workerExpose_3():
    with mock.patch.object(app,
                           'sgCaptureImage',
                           return_value=(True, {'Receipt': '123'})):
        with mock.patch.object(app,
                               'waitCombined'):
            app.abortExpose = False
            with mock.patch.object(os.path,
                                   'splitext',
                                   return_value=('test', 'test')):
                with mock.patch.object(os,
                                       'rename'):
                    suc = app.workerExpose()
                    assert suc


def test_workerExpose_4():
    with mock.patch.object(app,
                           'sgCaptureImage',
                           return_value=(True, {'Receipt': '123'})):
        with mock.patch.object(app,
                               'waitCombined'):
            app.abortExpose = True
            suc = app.workerExpose()
            assert suc


def test_expose_1():
    app.deviceConnected = False
    suc = app.expose()
    assert not suc


def test_expose_2():
    app.deviceConnected = True
    with mock.patch.object(app.threadPool,
                           'start'):
        suc = app.expose()
        assert suc


def test_abort_1():
    app.deviceConnected = False
    with mock.patch.object(app,
                           'sgAbortImage'):
        suc = app.abort()
        assert not suc


def test_abort_2():
    app.deviceConnected = True
    app.abortExpose = False
    with mock.patch.object(app,
                           'sgAbortImage'):
        suc = app.abort()
        assert suc
        assert app.abortExpose


def test_sendCoolerSwitch_1():
    app.deviceConnected = False
    suc = app.sendCoolerSwitch()
    assert not suc


def test_sendCoolerSwitch_2():
    app.deviceConnected = True
    suc = app.sendCoolerSwitch(coolerOn=True)
    assert suc


def test_sendCoolerTemp_1():
    app.deviceConnected = False
    with mock.patch.object(app,
                           'sgSetCameraTemp'):
        suc = app.sendCoolerTemp()
        assert not suc


def test_sendCoolerTemp_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'sgSetCameraTemp'):
        suc = app.sendCoolerTemp(temperature=-10)
        assert suc


def test_sendOffset_1():
    app.deviceConnected = False
    suc = app.sendOffset()
    assert not suc


def test_sendOffset_2():
    app.deviceConnected = True
    suc = app.sendOffset(offset=50)
    assert suc


def test_sendGain_1():
    app.deviceConnected = False
    suc = app.sendGain()
    assert not suc


def test_sendGain_2():
    app.deviceConnected = True
    suc = app.sendGain(gain=50)
    assert suc
