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
import unittest.mock as mock
import platform
import faulthandler
faulthandler.enable()

# external packages
from astropy.io import fits
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from mountcontrol.mount import Mount
from skyfield.api import Angle
if platform.system() == 'Windows':
    import win32com.client
    import pythoncom

# local import
from mw4.imaging.cameraAscom import CameraAscom
from mw4.imaging.camera import CameraSignals


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test1:
        CameraXSize = 1000
        CameraYSize = 500
        CanAbortExposure = True
        FastReadout = True
        PixelSizeX = 4
        PixelSizeY = 4
        MaxBinX = 3
        MaxBinY = 3
        BinX = 1
        BinY = 1
        StartX = 0
        StartY = 0
        CameraState = 0
        CCDTemperature = 10
        CoolerOn = True
        CoolerPower = 100
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'
        ImageReady = True
        ImageArray = [1, 1, 1]

        @staticmethod
        def StartExposure(time, light=True):
            return True

        @staticmethod
        def StopExposure():
            return True

    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', expire=False, verbose=False,
                      pathToData='mw4/test/data')
        mount.obsSite.raJNow = Angle(hours=12)
        mount.obsSite.decJNow = Angle(degrees=45)
        deviceStat = {'mount': True}

    global app
    app = CameraAscom(app=Test(), signals=CameraSignals(), data={})

    app.client = Test1()

    yield


def test_getInitialConfig_1():
    suc = app.getInitialConfig()
    assert suc


def test_workerPollData_1():
    app.data['CAN_FAST'] = True
    suc = app.workerPollData()
    assert suc


def test_workerPollData_2():
    app.data['CAN_FAST'] = False

    suc = app.workerPollData()
    assert not suc


def test_pollData_1():
    app.deviceConnected = False
    suc = app.pollData()
    assert not suc


def test_pollData_2():
    app.deviceConnected = True
    suc = app.pollData()
    assert suc


def test_sendDownloadMode_1():
    app.data['CAN_FAST'] = True
    suc = app.sendDownloadMode()
    assert suc


def test_sendDownloadMode_2():
    app.data['CAN_FAST'] = True
    suc = app.sendDownloadMode(fastReadout=True)
    assert suc


def test_sendDownloadMode_3():
    app.data['CAN_FAST'] = False
    suc = app.sendDownloadMode()
    assert not suc


def test_workerExpose_1():
    app.data['CAN_FAST'] = False
    app.data['CCD_INFO.CCD_PIXEL_SIZE_X'] = 1000
    app.data['CCD_INFO.CCD_PIXEL_SIZE_Y'] = 1000
    app.imagePath = ''

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
    app.client.ImageReady = False

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
    app.client.ImageReady = False

    with mock.patch.object(fits.PrimaryHDU,
                           'writeto'):
        suc = app.workerExpose(expTime=0.05)
        assert suc


def test_expose_1():
    app.deviceConnected = False
    suc = app.expose()
    assert not suc


def test_expose_2():
    app.deviceConnected = True
    suc = app.expose()
    assert suc


def test_expose_3():
    app.deviceConnected = True
    app.data['CCD_BINNING.HOR_BIN_MAX'] = 3
    app.data['CCD_BINNING.VERT_BIN_MAX'] = 3

    suc = app.expose(expTime=1,
                     binning=4)
    assert not suc


def test_abort_1():
    app.deviceConnected = False
    suc = app.abort()
    assert not suc


def test_abort_2():
    app.deviceConnected = True
    app.data['CAN_ABORT'] = False
    suc = app.abort()
    assert not suc


def test_abort_3():
    app.deviceConnected = True
    app.data['CAN_ABORT'] = True
    suc = app.abort()
    assert suc


def test_sendCoolerSwitch_1():
    app.deviceConnected = False
    suc = app.sendCoolerSwitch()
    assert not suc


def test_sendCoolerSwitch_2():
    app.deviceConnected = True
    app.data['CAN_ABORT'] = False
    suc = app.sendCoolerSwitch(coolerOn=True)
    assert suc


def test_sendCoolerTemp_1():
    app.deviceConnected = False
    suc = app.sendCoolerTemp()
    assert not suc


def test_sendCoolerTemp_2():
    app.deviceConnected = True
    app.data['CAN_ABORT'] = False
    suc = app.sendCoolerTemp(temperature=-10)
    assert suc
