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
import platform

if not platform.system() == 'Windows':
    pytest.skip("skipping windows-only tests", allow_module_level=True)

# external packages
from astropy.io import fits
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal
from skyfield.api import Angle, wgs84
import ctypes


# local import
from mountcontrol.mount import Mount
from logic.environment.skymeter import Skymeter
from logic.camera.cameraAscom import CameraAscom
from base.driverDataClass import Signals
from base.ascomClass import AscomClass
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test1:
        CameraXSize = 1000
        CameraYSize = 500
        CanAbortExposure = True
        CanFastReadout = True
        CanGetCoolerPower = True
        CanSetCCDTemperature = True
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
        image = [1, 1, 1]
        ImageArray = (ctypes.c_int * len(image))(*image)
        # see
        # https://stackoverflow.com/questions/4145775/how-do-i-convert-a-python-list-into-a-c-array-by-using-ctypes
        @staticmethod
        def StartExposure(time, light=True):
            return True

        @staticmethod
        def StopExposure():
            return True

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
        skymeter = Skymeter(app=TestApp())

    global app
    app = CameraAscom(app=Test(), signals=Signals(), data={})
    app.client = Test1()
    app.clientProps = []
    yield


def test_workerGetInitialConfig_1():
    with mock.patch.object(AscomClass,
                           'getAndStoreAscomProperty',
                           return_value=True):
        with mock.patch.object(app,
                               'getAndStoreAscomProperty'):
            suc = app.workerGetInitialConfig()
            assert suc


def test_workerPollData_1():
    app.data['CAN_FAST'] = True
    app.data['CAN_SET_CCD_TEMPERATURE'] = True
    app.data['CAN_GET_COOLER_POWER'] = True
    suc = app.workerPollData()
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
    with mock.patch.object(app,
                           'sendDownloadMode'):
        with mock.patch.object(app,
                               'setAscomProperty'):
            with mock.patch.object(app,
                                   'waitExposed'):
                with mock.patch.object(app,
                                       'retrieveFits'):
                    with mock.patch.object(app,
                                           'saveFits'):
                        suc = app.workerExpose()
                        assert suc


def test_expose_1():
    with mock.patch.object(app,
                           'callMethodThreaded'):
        suc = app.expose()
        assert suc


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
    with mock.patch.object(app,
                           'callMethodThreaded'):
        suc = app.abort()
        assert suc


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
    suc = app.sendCoolerTemp()
    assert not suc


def test_sendCoolerTemp_2():
    app.deviceConnected = True
    app.data['CAN_SET_CCD_TEMPERATURE'] = False
    suc = app.sendCoolerTemp(temperature=-10)
    assert not suc


def test_sendCoolerTemp_3():
    app.deviceConnected = True
    app.data['CAN_SET_CCD_TEMPERATURE'] = True
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
