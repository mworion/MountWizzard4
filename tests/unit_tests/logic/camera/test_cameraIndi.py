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
import zlib
# external packages
from astropy.io import fits
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal
from indibase.indiBase import Device, Client
from skyfield.api import Angle, load

# local import
from logic.camera.cameraIndi import CameraIndi
from logic.camera.camera import CameraSignals
from base.indiClass import IndiClass


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test2:
        raJNow = Angle(hours=0)
        decJNow = Angle(degrees=0)
        timeJD = load.timescale().tt_jd(23456789.5)

    class Test1:
        obsSite = Test2()

    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)
        deviceStat = {'mount': True}
        mount = Test1()

    global app
    app = CameraIndi(app=Test(), signals=CameraSignals(), data={})

    yield


def test_setUpdateConfig_1():
    app.deviceName = ''
    suc = app.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_2():
    app.deviceName = 'test'
    app.device = None
    suc = app.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_3():
    app.deviceName = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'Test': 1}):
        suc = app.setUpdateConfig('test')
        assert not suc


def test_setUpdateConfig_4():
    app.deviceName = 'test'
    app.device = Device()
    app.UPDATE_RATE = 1
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'PERIOD_MS': 1}):
        suc = app.setUpdateConfig('test')
        assert suc


def test_setUpdateConfig_5():
    app.deviceName = 'test'
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
    app.deviceName = 'test'
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


def test_setExposureState_5():
    app.device = Device()
    app.data = {'CCD_EXPOSURE.CCD_EXPOSURE_VALUE': 1}
    setattr(app.device, 'CCD_EXPOSURE', {'state': 'Busy'})
    suc = app.setExposureState()
    assert suc
    assert not app.isDownloading


def test_setExposureState_6():
    app.device = Device()
    app.data = {'CCD_EXPOSURE.CCD_EXPOSURE_VALUE': 1}
    app.isDownloading = True
    setattr(app.device, 'CCD_EXPOSURE', {'state': 'Ok'})
    suc = app.setExposureState()
    assert suc
    assert not app.isDownloading


def test_sendDownloadMode_1():
    app.deviceName = 'test'
    app.device = None
    suc = app.sendDownloadMode()
    assert not suc


def test_sendDownloadMode_2():
    app.deviceName = 'test'
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


def test_updateNumber_3():
    app.data = {'AUTO_DEW.DEW_C': 1,
                'VERSION.UPB': 1}
    with mock.patch.object(IndiClass,
                           'updateNumber',
                           return_value=True):
        suc = app.updateNumber('test', 'CCD_TEMPERATURE')
        assert suc


def test_updateHeaderInfo_1():
    header = {}
    app.ra = Angle(hours=12)
    app.dec = Angle(degrees=180)
    h = app.updateHeaderInfo(header)
    assert 'RA' in h
    assert 'DEC' in h


def test_updateHeaderInfo_2():
    header = {'RA': 90,
              'DEC': 90}
    app.ra = Angle(hours=12)
    app.dec = Angle(degrees=180)
    h = app.updateHeaderInfo(header)
    assert 'RA' in h
    assert 'DEC' in h
    assert h['RA'] == 90
    assert h['DEC'] == 90


def test_updateHeaderInfo_3():
    header = {'RA': 90}
    app.ra = Angle(hours=12)
    app.dec = Angle(degrees=180)
    h = app.updateHeaderInfo(header)
    assert 'RA' in h
    assert 'DEC' in h
    assert h['RA'] == 180
    assert h['DEC'] == 180


def test_updateHeaderInfo_4():
    header = {}
    app.ra = None
    app.dec = None
    h = app.updateHeaderInfo(header)
    assert 'RA' not in h
    assert 'DEC' not in h


def test_workerSaveBLOB_1():
    app.imagePath = 'tests/image/test.fit'
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    data = {'value': '1',
            'name': 'CCD1',
            'format': '.fits.fz'}
    with mock.patch.object(fits.HDUList,
                           'fromstring',
                           return_value=hdu):
        suc = app.workerSaveBLOB(data)
        assert suc


def test_workerSaveBLOB_2():
    app.imagePath = 'tests/image/test.fit'
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    data = {'value': zlib.compress(b'1'),
            'name': 'CCD1',
            'format': '.fits.z'}
    with mock.patch.object(fits.HDUList,
                           'fromstring',
                           return_value=hdu):
        suc = app.workerSaveBLOB(data)
        assert suc


def test_workerSaveBLOB_3():
    app.imagePath = 'tests/image/test.fit'
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    data = {'value': '1',
            'name': 'CCD1',
            'format': '.fits'}
    with mock.patch.object(fits.HDUList,
                           'fromstring',
                           return_value=hdu):
        suc = app.workerSaveBLOB(data)
        assert suc


def test_workerSaveBLOB_4():
    app.imagePath = 'tests/image/test.fit'
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    data = {'value': '1',
            'name': 'CCD1',
            'format': '.test'}
    with mock.patch.object(fits.HDUList,
                           'fromstring',
                           return_value=hdu):
        suc = app.workerSaveBLOB(data)
        assert suc


def test_updateBLOB_1():
    app.device = Device()
    with mock.patch.object(IndiClass,
                           'updateBLOB',
                           return_value=False):
        suc = app.updateBLOB('test', 'test')
        assert not suc


def test_updateBLOB_2():
    app.device = Device()
    with mock.patch.object(IndiClass,
                           'updateBLOB',
                           return_value=True):
        with mock.patch.object(app.device,
                               'getBlob',
                               return_value={}):
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
                                             'name': 'test'}):
            suc = app.updateBLOB('test', 'test')
            assert not suc


def test_updateBLOB_5():
    app.device = Device()
    with mock.patch.object(IndiClass,
                           'updateBLOB',
                           return_value=True):
        with mock.patch.object(app.device,
                               'getBlob',
                               return_value={'value': 1,
                                             'name': 'CCD2',
                                             'format': 'test'}):
            suc = app.updateBLOB('test', 'test')
            assert not suc


def test_updateBLOB_6():
    app.device = Device()
    with mock.patch.object(IndiClass,
                           'updateBLOB',
                           return_value=True):
        with mock.patch.object(app.device,
                               'getBlob',
                               return_value={'value': 1,
                                             'name': 'CCD1',
                                             'format': 'test'}):
            suc = app.updateBLOB('test', 'test')
            assert not suc


def test_updateBLOB_7():
    app.device = Device()
    app.imagePath = 'tests/dummy/test.txt'
    with mock.patch.object(IndiClass,
                           'updateBLOB',
                           return_value=True):
        with mock.patch.object(app.device,
                               'getBlob',
                               return_value={'value': 1,
                                             'name': 'CCD1',
                                             'format': 'test'}):
            suc = app.updateBLOB('test', 'test')
            assert not suc


def test_updateBLOB_8():
    app.device = Device()
    app.imagePath = 'tests/image/test.fit'
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


def test_expose_1():
    app.deviceName = 'test'
    app.device = None
    suc = app.expose()
    assert not suc


def test_expose_2():
    app.deviceName = 'test'
    app.device = Device()
    with mock.patch.object(app,
                           'sendDownloadMode',
                           return_value=False):
        suc = app.expose()
        assert not suc


def test_expose_3():
    app.deviceName = 'test'
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
    app.deviceName = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={}):
        with mock.patch.object(app.client,
                               'sendNewNumber',
                               return_value=True):
            suc = app.expose()
            assert suc


def test_expose_5():
    app.deviceName = 'test'
    app.app.deviceStat['mount'] = False
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
    app.deviceName = 'test'
    app.device = None
    suc = app.abort()
    assert not suc


def test_abort_2():
    app.deviceName = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'Test': 1}):
        suc = app.abort()
        assert not suc


def test_abort_3():
    app.deviceName = 'test'
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
    app.deviceName = 'test'
    app.device = None
    suc = app.sendCoolerSwitch()
    assert not suc


def test_sendCoolerSwitch_2():
    app.deviceName = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'Test': 1}):
        suc = app.sendCoolerSwitch()
        assert not suc


def test_sendCoolerSwitch_3():
    app.deviceName = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getSwitch',
                           return_value={'COOLER_ON': True}):
        with mock.patch.object(app.client,
                               'sendNewSwitch',
                               return_value=True):
            suc = app.sendCoolerSwitch(True)
            assert suc


def test_sendCoolerTemp_1():
    app.deviceName = 'test'
    app.device = None
    suc = app.sendCoolerTemp()
    assert not suc


def test_sendCoolerTemp_2():
    app.deviceName = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'Test': 1}):
        suc = app.sendCoolerTemp()
        assert not suc


def test_sendCoolerTemp_3():
    app.deviceName = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'CCD_TEMPERATURE_VALUE': 1}):
        with mock.patch.object(app.client,
                               'sendNewNumber',
                               return_value=True):
            suc = app.sendCoolerTemp()
            assert suc


def test_sendOffset_1():
    app.deviceName = 'test'
    app.device = None
    suc = app.sendOffset()
    assert not suc


def test_sendOffset_2():
    app.deviceName = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'Test': 1}):
        suc = app.sendOffset()
        assert not suc


def test_sendOffset_3():
    app.deviceName = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'OFFSET': 1}):
        with mock.patch.object(app.client,
                               'sendNewNumber',
                               return_value=True):
            suc = app.sendOffset()
            assert suc


def test_sendGain_1():
    app.deviceName = 'test'
    app.device = None
    suc = app.sendGain()
    assert not suc


def test_sendGain_2():
    app.deviceName = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'Test': 1}):
        suc = app.sendGain()
        assert not suc


def test_sendGain_3():
    app.deviceName = 'test'
    app.device = Device()
    with mock.patch.object(app.device,
                           'getNumber',
                           return_value={'GAIN': 1}):
        with mock.patch.object(app.client,
                               'sendNewNumber',
                               return_value=True):
            suc = app.sendGain()
            assert suc
