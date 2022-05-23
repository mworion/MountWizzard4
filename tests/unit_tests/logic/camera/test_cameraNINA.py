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
from logic.camera.cameraNINA import CameraNINA
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
        messageN = pyqtSignal(object, object, object, object)

        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/workDir/data')
        mount.obsSite.location = wgs84.latlon(latitude_degrees=0,
                                              longitude_degrees=0,
                                              elevation_m=0)
        mount.obsSite.raJNow = Angle(hours=12)
        mount.obsSite.decJNow = Angle(degrees=45)
        deviceStat = {'mount': True}

    global app
    app = CameraNINA(app=Test(), signals=Signals(), data={})
    yield


def test_getCameraTemp_1():
    with mock.patch.object(app,
                           'requestProperty',
                           return_value=None):
        suc, val = app.getCameraTemp()
        assert not suc
        assert val == {}


def test_getCameraTemp_2():
    with mock.patch.object(app,
                           'requestProperty',
                           return_value={'Success': True}):
        suc, val = app.getCameraTemp()
        assert suc
        assert val == {'Success': True}


def test_setCameraTemp_1():
    with mock.patch.object(app,
                           'requestProperty',
                           return_value=None):
        suc = app.setCameraTemp(temperature=10)
        assert not suc


def test_setCameraTemp_2():
    with mock.patch.object(app,
                           'requestProperty',
                           return_value={'Success': True}):
        suc = app.setCameraTemp(temperature=10)
        assert suc


def test_captureImage_1():
    with mock.patch.object(app,
                           'requestProperty',
                           return_value=None):
        suc, val = app.captureImage(0)
        assert not suc
        assert val == {}


def test_captureImage_2():
    with mock.patch.object(app,
                           'requestProperty',
                           return_value={'Success': True}):
        suc, val = app.captureImage(0)
        assert suc
        assert val == {'Success': True}


def test_abortImage_1():
    with mock.patch.object(app,
                           'requestProperty',
                           return_value=None):
        suc = app.abortImage()
        assert not suc


def test_abortImage_2():
    with mock.patch.object(app,
                           'requestProperty',
                           return_value={'Success': True}):
        suc = app.abortImage()
        assert suc


def test_getImagePath_1():
    with mock.patch.object(app,
                           'requestProperty',
                           return_value=None):
        suc = app.getImagePath(receipt='1')
        assert not suc


def test_getImagePath_2():
    with mock.patch.object(app,
                           'requestProperty',
                           return_value={'Success': True}):
        suc = app.getImagePath(receipt='1')
        assert suc


def test_getCameraProps_1():
    with mock.patch.object(app,
                           'requestProperty',
                           return_value=None):
        suc, val = app.getCameraProps()
        assert not suc
        assert val == {}


def test_getCameraProps_2():
    with mock.patch.object(app,
                           'requestProperty',
                           return_value={'Success': True}):
        suc, val = app.getCameraProps()
        assert suc
        assert val == {'Success': True}


def test_workerGetInitialConfig_1():
    app.deviceName = 'controlled'
    suc = app.workerGetInitialConfig()
    assert not suc


def test_workerGetInitialConfig_2():
    app.deviceName = 'test'
    with mock.patch.object(app,
                           'storePropertyToData'):
        with mock.patch.object(app,
                               'getCameraProps',
                               return_value=(False, {})):
            suc = app.workerGetInitialConfig()
            assert not suc


def test_workerGetInitialConfig_3():
    app.deviceName = 'test'
    val = {
        'Message': 'test',
        'SupportsSubframe': True,
        'NumPixelsX': 1000,
        'NumPixelsY': 500,
        'GainValues': ['1'],
        'IsoValues': ['1'],
    }
    with mock.patch.object(app,
                           'storePropertyToData'):
        with mock.patch.object(app,
                               'getCameraProps',
                               return_value=(True, val)):
            suc = app.workerGetInitialConfig()
            assert suc


def test_workerPollData_1():
    app.deviceName = 'controlled'
    suc = app.workerPollData()
    assert not suc


def test_workerPollData_2():
    app.deviceName = 'test'
    app.data['CAN_FAST'] = True
    with mock.patch.object(app,
                           'getCameraTemp',
                           return_value=(False, None)):
        suc = app.workerPollData()
        assert not suc


def test_workerPollData_3():
    app.deviceName = 'test'
    app.data['CAN_FAST'] = True
    with mock.patch.object(app,
                           'getCameraTemp',
                           return_value=(True, {'Temperature': 10})):
        suc = app.workerPollData()
        assert suc


def test_sendDownloadMode_1():
    suc = app.sendDownloadMode()
    assert suc


def test_workerExpose_1():
    with mock.patch.object(app,
                           'captureImage',
                           return_value=(False, None)):
        suc = app.workerExpose()
        assert not suc


def test_workerExpose_2():
    app.deviceName = 'test'
    with mock.patch.object(app,
                           'captureImage',
                           return_value=(True, {})):
        suc = app.workerExpose()
        assert not suc


def test_workerExpose_3():
    app.deviceName = 'test'
    app.abortExpose = False
    with mock.patch.object(app,
                           'captureImage',
                           return_value=(True, {'Receipt': '123'})):
        with mock.patch.object(app,
                               'waitStart'):
            with mock.patch.object(app,
                                   'waitExposedApp'):
                with mock.patch.object(app,
                                       'waitDownload'):
                    with mock.patch.object(app,
                                           'waitSave'):
                        with mock.patch.object(os.path,
                                               'splitext',
                                               return_value=('test', 'test')):
                            with mock.patch.object(os,
                                                   'rename'):
                                suc = app.workerExpose()
                                assert suc


def test_workerExpose_4():
    app.deviceName = 'test'
    app.data['READOUT_QUALITY.QUALITY_LOW'] = True
    app.abortExpose = True
    with mock.patch.object(app,
                           'captureImage',
                           return_value=(True, {'Receipt': '123'})):
        with mock.patch.object(app,
                               'waitStart'):
            with mock.patch.object(app,
                                   'waitExposedApp'):
                with mock.patch.object(app,
                                       'waitDownload'):
                    with mock.patch.object(app,
                                           'waitSave'):
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
                           'abortImage'):
        suc = app.abort()
        assert not suc


def test_abort_2():
    app.deviceConnected = True
    app.abortExpose = False
    with mock.patch.object(app,
                           'abortImage'):
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
                           'setCameraTemp'):
        suc = app.sendCoolerTemp()
        assert not suc


def test_sendCoolerTemp_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'setCameraTemp'):
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
