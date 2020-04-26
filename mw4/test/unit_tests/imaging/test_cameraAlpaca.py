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
from astropy.io import fits
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from mountcontrol.mount import Mount
from skyfield.api import Angle

# local import
from mw4.imaging.cameraAlpaca import CameraAlpaca
from mw4.imaging.camera import CameraSignals
from mw4.base.alpacaBase import AlpacaBase


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)
        mount = Mount(expire=False, verbose=False, pathToData='mw4/test/data')
        mount.obsSite.raJNow = Angle(hours=12)
        mount.obsSite.decJNow = Angle(degrees=45)
        deviceStat = {'mount': True}

    global app
    app = CameraAlpaca(app=Test(), signals=CameraSignals(), data={})

    yield


def test_getInitialConfig_1():
    with mock.patch.object(AlpacaBase,
                           'get'):
        suc = app.getInitialConfig()
        assert suc


def test_workerPollData_1():
    app.data['CAN_FAST'] = True
    with mock.patch.object(AlpacaBase,
                           'get'):
        suc = app.workerPollData()
        assert suc


def test_workerPollData_2():
    with mock.patch.object(AlpacaBase,
                           'get'):
        suc = app.workerPollData()
        assert not suc


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


def test_expose_1():
    app.deviceConnected = False
    with mock.patch.object(app.threadPool,
                           'start'):
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
    app.data['CAN_ABORT'] = False
    with mock.patch.object(AlpacaBase,
                           'put',
                           return_value=True):
        suc = app.sendCoolerSwitch(coolerOn=True)
        assert suc


def test_sendCoolerTemp_1():
    app.deviceConnected = False
    with mock.patch.object(AlpacaBase,
                           'get',
                           return_value=True):
        suc = app.sendCoolerTemp()
        assert not suc


def test_sendCoolerTemp_2():
    app.deviceConnected = True
    app.data['CAN_ABORT'] = False
    with mock.patch.object(AlpacaBase,
                           'put',
                           return_value=True):
        suc = app.sendCoolerTemp(temperature=-10)
        assert suc
