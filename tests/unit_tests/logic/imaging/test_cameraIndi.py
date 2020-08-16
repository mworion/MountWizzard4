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
import zlib
# external packages
from astropy.io import fits
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from indibase.indiBase import Device, Client

# local import
from logic.imaging.cameraIndi import CameraIndi
from logic.imaging.camera import CameraSignals
from base.indiClass import IndiClass


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)

    global app
    app = CameraIndi(app=Test(), signals=CameraSignals(), data={})

    yield


def test_setUpdateConfig_1():
    app.name = ''
    suc = app.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_2():
    app.name = 'test'
    app.device = None
    suc = app.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_3():
    app.name = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'Test': 1}):
        suc = app.setUpdateConfig('test')
        assert not suc


def test_setUpdateConfig_4():
    app.name = 'test'
    app.device = Device()
    app.UPDATE_RATE = 1
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'PERIOD_MS': 1}):
        suc = app.setUpdateConfig('test')
        assert suc


def test_setUpdateConfig_5():
    app.name = 'test'
    app.device = Device()
    app.client = Client()
    app.UPDATE_RATE = 0
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'PERIOD_MS': 1}):
        with mock.patch.object(app.client,
                               'sendNewNumber',
                               return_value=False):
            suc = app.setUpdateConfig('test')
            assert not suc


def test_setUpdateConfig_6():
    app.name = 'test'
    app.device = Device()
    app.client = Client()
    app.UPDATE_RATE = 0
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'PERIOD_MS': 1}):
        with mock.patch.object(app.client,
                               'sendNewNumber',
                               return_value=True):
            suc = app.setUpdateConfig('test')
            assert suc


def test_setExposureState_1():
    suc = app.setExposureState()
    assert not suc


def test_setExposureState_2():
    app.device = Device()
    setattr(app.device, 'CCD_EXPOSURE', {'state': 'Idle'})
    suc = app.setExposureState()
    assert suc


def test_setExposureState_3():
    app.device = Device()
    setattr(app.device, 'CCD_EXPOSURE', {'state': 'Busy'})
    suc = app.setExposureState()
    assert suc


def test_setExposureState_4():
    app.device = Device()
    setattr(app.device, 'CCD_EXPOSURE', {'state': 'Ok'})
    suc = app.setExposureState()
    assert suc


def test_sendDownloadMode_1():
    app.name = 'test'
    app.device = None
    suc = app.sendDownloadMode()
    assert not suc


def test_sendDownloadMode_2():
    app.name = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'Test': 1}):
        suc = app.sendDownloadMode()
        assert not suc


def test_updateNumber_1():
    suc = app.updateNumber('test', 'test')
    assert not suc


def test_updateNumber_2():
    app.data = {'AUTO_DEW.DEW_C': 1,
                'VERSION.UPB': 1}
    with mock.patch.object(IndiClass,
                           'updateNumber',
                           return_value=True):
        suc = app.updateNumber('test', 'CCD_EXPOSURE')
        assert suc


def test_updateBLOB_1():
    suc = app.updateBLOB('test', 'test')
    assert not suc


def test_updateBLOB_2():
    app.device = Device()
    with mock.patch.object(IndiClass,
                           'updateBLOB',
                           return_value=True):
        suc = app.updateBLOB('test', 'test')
        assert not suc


def test_updateBLOB_3():
    app.device = Device()
    with mock.patch.object(IndiClass,
                           'updateBLOB',
                           return_value=True):
        with mock.patch.object(app.device,
                               'getBlob',
                               return_value={'value': 1}):
            suc = app.updateBLOB('test', 'test')
            assert not suc


def test_updateBLOB_4():
    app.device = Device()
    with mock.patch.object(IndiClass,
                           'updateBLOB',
                           return_value=True):
        with mock.patch.object(app.device,
                               'getBlob',
                               return_value={'value': 1,
                                             'name': 'CCD1'}):
            suc = app.updateBLOB('test', 'test')
            assert not suc


def test_updateBLOB_5():
    app.device = Device()
    app.data = {'value': 1}
    app.imagePath = 'mw4/test/image/test.fit'
    with mock.patch.object(IndiClass,
                           'updateBLOB',
                           return_value=True):
        with mock.patch.object(app.device,
                               'getBlob',
                               return_value={'value': 1,
                                             'name': 'CCD1'}):
            suc = app.updateBLOB('test', 'test')
            assert not suc


def test_updateBLOB_6():
    app.device = Device()
    app.data = {'value': 1}
    app.imagePath = 'mw4/test/image/test.fit'
    with mock.patch.object(IndiClass,
                           'updateBLOB',
                           return_value=True):
        with mock.patch.object(app.device,
                               'getBlob',
                               return_value={'value': 1,
                                             'name': 'CCD1',
                                             'format': 'test'}):
            suc = app.updateBLOB('test', 'test')
            assert suc


def test_updateBLOB_7():
    app.device = Device()
    app.imagePath = 'mw4/test/image/test.fit'
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    with mock.patch.object(IndiClass,
                           'updateBLOB',
                           return_value=True):
        with mock.patch.object(app.device,
                               'getBlob',
                               return_value={'value': 1,
                                             'name': 'CCD1',
                                             'format': '.fits.fz'}):
            with mock.patch.object(fits.HDUList,
                                   'fromstring',
                                   return_value=hdu):
                suc = app.updateBLOB('test', 'test')
                assert suc


def test_updateBLOB_8():
    app.device = Device()
    app.imagePath = 'mw4/test/image/test.fit'
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    with mock.patch.object(IndiClass,
                           'updateBLOB',
                           return_value=True):
        with mock.patch.object(app.device,
                               'getBlob',
                               return_value={'value': zlib.compress(b'1'),
                                             'name': 'CCD1',
                                             'format': '.fits.z'}):
            with mock.patch.object(fits.HDUList,
                                   'fromstring',
                                   return_value=hdu):
                suc = app.updateBLOB('test', 'test')
                assert suc


def test_updateBLOB_9():
    app.device = Device()
    app.imagePath = 'mw4/test/image/test.fit'
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    with mock.patch.object(IndiClass,
                           'updateBLOB',
                           return_value=True):
        with mock.patch.object(app.device,
                               'getBlob',
                               return_value={'value': 1,
                                             'name': 'CCD1',
                                             'format': '.fits'}):
            with mock.patch.object(fits.HDUList,
                                   'fromstring',
                                   return_value=hdu):
                suc = app.updateBLOB('test', 'test')
                assert suc


def test_expose_1():
    app.name = 'test'
    app.device = None
    suc = app.expose()
    assert not suc


def test_expose_2():
    app.name = 'test'
    app.device = Device()
    with mock.patch.object(app,
                           'sendDownloadMode',
                           return_value=False):
        suc = app.expose()
        assert not suc


def test_expose_3():
    app.name = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={}):
        with mock.patch.object(app.client,
                               'sendNewNumber',
                               return_value=False):
            suc = app.expose()
            assert not suc


def test_expose_4():
    app.name = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={}):
        with mock.patch.object(app.client,
                               'sendNewNumber',
                               return_value=True):
            suc = app.expose()
            assert suc


def test_abort_1():
    app.name = 'test'
    app.device = None
    suc = app.abort()
    assert not suc


def test_abort_2():
    app.name = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'Test': 1}):
        suc = app.abort()
        assert not suc


def test_abort_3():
    app.name = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'ABORT': 1}):
        with mock.patch.object(app.client,
                               'sendNewSwitch',
                               return_value=True):
            suc = app.abort()
            assert suc


def test_sendCoolerSwitch_1():
    app.name = 'test'
    app.device = None
    suc = app.sendCoolerSwitch()
    assert not suc


def test_sendCoolerSwitch_2():
    app.name = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'Test': 1}):
        suc = app.sendCoolerSwitch()
        assert not suc


def test_sendCoolerSwitch_3():
    app.name = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'COOLER_ON': True}):
        with mock.patch.object(app.client,
                               'sendNewSwitch',
                               return_value=True):
            suc = app.sendCoolerSwitch()
            assert suc


def test_sendCoolerTemp_1():
    app.name = 'test'
    app.device = None
    suc = app.sendCoolerTemp()
    assert not suc


def test_sendCoolerTemp_2():
    app.name = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'Test': 1}):
        suc = app.sendCoolerTemp()
        assert not suc


def test_sendCoolerTemp_3():
    app.name = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'CCD_TEMPERATURE_VALUE': 1}):
        with mock.patch.object(app.client,
                               'sendNewNumber',
                               return_value=True):
            suc = app.sendCoolerTemp()
            assert suc
