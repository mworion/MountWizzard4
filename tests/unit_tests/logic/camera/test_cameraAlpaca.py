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

# external packages
from astropy.io import fits
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal
from skyfield.api import Angle

# local import
from mountcontrol.mount import Mount
from logic.environment.skymeter import Skymeter
from logic.camera.cameraAlpaca import CameraAlpaca
from logic.camera.camera import CameraSignals
from base.alpacaBase import AlpacaBase
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
                      pathToData='tests/data')
        mount.obsSite.raJNow = Angle(hours=12)
        mount.obsSite.decJNow = Angle(degrees=45)
        deviceStat = {'mount': True}
        skymeter = Skymeter(app=TestApp())

    global app
    app = CameraAlpaca(app=Test(), signals=CameraSignals(), data={})

    yield


def test_getInitialConfig_1():
    with mock.patch.object(AlpacaBase,
                           'get'):
        suc = app.getInitialConfig()
        assert suc


def test_workerPollData_1():
    app.deviceConnected = False
    app.data['CAN_FAST'] = True
    with mock.patch.object(AlpacaBase,
                           'get'):
        suc = app.workerPollData()
        assert not suc


def test_workerPollData_2():
    app.deviceConnected = True
    app.data['CAN_FAST'] = True
    app.data['CAN_SET_CCD_TEMPERATURE'] = True
    app.data['CAN_GET_COOLER_POWER'] = True
    with mock.patch.object(AlpacaBase,
                           'get'):
        suc = app.workerPollData()
        assert suc


def test_pollData_1():
    app.deviceConnected = False
    with mock.patch.object(app.threadPool,
                           'start'):
        suc = app.pollData()
        assert not suc


def test_pollData_2():
    app.deviceConnected = True
    with mock.patch.object(app.threadPool,
                           'start'):
        suc = app.pollData()
        assert suc


def test_sendDownloadMode_1():
    app.data['CAN_FAST'] = True
    with mock.patch.object(AlpacaBase,
                           'get',
                           return_value=False):
        suc = app.sendDownloadMode()
        assert suc


def test_sendDownloadMode_2():
    app.data['CAN_FAST'] = True
    with mock.patch.object(AlpacaBase,
                           'get',
                           return_value=True):
        suc = app.sendDownloadMode(fastReadout=True)
        assert suc


def test_sendDownloadMode_3():
    app.data['CAN_FAST'] = False
    with mock.patch.object(AlpacaBase,
                           'get',
                           return_value=True):
        suc = app.sendDownloadMode()
        assert not suc


def test_workerExpose_1():
    app.data['CAN_FAST'] = False
    app.data['CCD_INFO.CCD_PIXEL_SIZE_X'] = 1000
    app.data['CCD_INFO.CCD_PIXEL_SIZE_Y'] = 1000
    app.imagePath = ''

    with mock.patch.object(AlpacaBase,
                           'get',
                           return_value=True):
        with mock.patch.object(fits.PrimaryHDU,
                               'writeto'):
            suc = app.workerExpose()
            assert suc


def test_workerExpose_2():
    app.data['CAN_FAST'] = False
    app.data['CCD_INFO.CCD_PIXEL_SIZE_X'] = 1000
    app.data['CCD_INFO.CCD_PIXEL_SIZE_Y'] = 1000
    app.imagePath = ''
    app.abortExpose = True

    with mock.patch.object(AlpacaBase,
                           'get',
                           return_value=True):
        with mock.patch.object(app.client,
                               'imageready',
                               return_value=False):
            with mock.patch.object(fits.PrimaryHDU,
                                   'writeto'):
                suc = app.workerExpose(expTime=0.3)
                assert suc


def test_workerExpose_3():
    app.data['CAN_FAST'] = False
    app.data['CCD_INFO.CCD_PIXEL_SIZE_X'] = 1000
    app.data['CCD_INFO.CCD_PIXEL_SIZE_Y'] = 1000
    app.imagePath = ''
    app.abortExpose = True

    with mock.patch.object(AlpacaBase,
                           'get',
                           return_value=True):
        with mock.patch.object(app.client,
                               'imageready',
                               return_value=False):
            with mock.patch.object(fits.PrimaryHDU,
                                   'writeto'):
                suc = app.workerExpose(expTime=0.05)
                assert suc


def test_workerExpose_4():
    app.data['CAN_FAST'] = False
    app.data['CCD_INFO.CCD_PIXEL_SIZE_X'] = 1000
    app.data['CCD_INFO.CCD_PIXEL_SIZE_Y'] = 1000
    app.imagePath = ''
    app.abortExpose = True

    with mock.patch.object(AlpacaBase,
                           'get',
                           return_value=True):
        with mock.patch.object(app.client,
                               'imageready',
                               return_value=False):
            with mock.patch.object(fits.PrimaryHDU,
                                   'writeto'):
                suc = app.workerExpose(expTime=0.05, focalLength=0)
                assert suc


def test_expose_1():
    app.deviceConnected = False
    with mock.patch.object(app.threadPool,
                           'start'):
        suc = app.expose()
        assert not suc


def test_expose_2():
    app.deviceConnected = True
    app.data['CCD_BINNING.HOR_BIN_MAX'] = 3
    app.data['CCD_BINNING.VERT_BIN_MAX'] = 3

    with mock.patch.object(app.threadPool,
                           'start'):
        suc = app.expose()
        assert suc


def test_expose_3():
    app.deviceConnected = True
    app.data['CCD_BINNING.HOR_BIN_MAX'] = 3
    app.data['CCD_BINNING.VERT_BIN_MAX'] = 3

    with mock.patch.object(app.threadPool,
                           'start'):
        suc = app.expose(expTime=1,
                         binning=4)
        assert suc


def test_abort_1():
    app.deviceConnected = False
    with mock.patch.object(AlpacaBase,
                           'get',
                           return_value=True):
        suc = app.abort()
        assert not suc


def test_abort_2():
    app.deviceConnected = True
    app.data['CAN_ABORT'] = False
    with mock.patch.object(AlpacaBase,
                           'get',
                           return_value=True):
        suc = app.abort()
        assert not suc


def test_abort_3():
    app.deviceConnected = True
    app.data['CAN_ABORT'] = True
    with mock.patch.object(AlpacaBase,
                           'get',
                           return_value=True):
        suc = app.abort()
        assert suc


def test_sendCoolerSwitch_1():
    app.deviceConnected = False
    with mock.patch.object(AlpacaBase,
                           'get',
                           return_value=True):
        suc = app.sendCoolerSwitch()
        assert not suc


def test_sendCoolerSwitch_2():
    app.deviceConnected = True
    with mock.patch.object(AlpacaBase,
                           'put',
                           return_value=True):
        suc = app.sendCoolerSwitch(coolerOn=True)
        assert suc


def test_sendCoolerTemp_1():
    app.deviceConnected = False
    app.data['CAN_SET_CCD_TEMPERATURE'] = True
    with mock.patch.object(AlpacaBase,
                           'get',
                           return_value=True):
        suc = app.sendCoolerTemp()
        assert not suc


def test_sendCoolerTemp_2():
    app.deviceConnected = True
    app.data['CAN_SET_CCD_TEMPERATURE'] = False
    with mock.patch.object(AlpacaBase,
                           'put',
                           return_value=True):
        suc = app.sendCoolerTemp(temperature=-10)
        assert not suc


def test_sendCoolerTemp_3():
    app.deviceConnected = True
    app.data['CAN_SET_CCD_TEMPERATURE'] = True
    with mock.patch.object(AlpacaBase,
                           'put',
                           return_value=True):
        suc = app.sendCoolerTemp(temperature=-10)
        assert suc


def test_sendOffset_1():
    app.deviceConnected = False
    with mock.patch.object(AlpacaBase,
                           'get',
                           return_value=True):
        suc = app.sendOffset()
        assert not suc


def test_sendOffset_2():
    app.deviceConnected = True
    with mock.patch.object(AlpacaBase,
                           'put',
                           return_value=True):
        suc = app.sendOffset(offset=50)
        assert suc


def test_sendGain_1():
    app.deviceConnected = False
    with mock.patch.object(AlpacaBase,
                           'get',
                           return_value=True):
        suc = app.sendGain()
        assert not suc


def test_sendGain_2():
    app.deviceConnected = True
    with mock.patch.object(AlpacaBase,
                           'put',
                           return_value=True):
        suc = app.sendGain(gain=50)
        assert suc
