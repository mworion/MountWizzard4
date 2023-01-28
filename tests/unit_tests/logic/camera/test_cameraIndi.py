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
import zlib
# external packages
from astropy.io import fits
from indibase.indiBase import Device, Client
from skyfield.api import Angle, load

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.camera.cameraIndi import CameraIndi
from base.driverDataClass import Signals
from base.indiClass import IndiClass


@pytest.fixture(autouse=True, scope='function')
def function():
    func = CameraIndi(app=App(), signals=Signals(), data={})
    yield func


def test_setUpdateConfig_1(function):
    function.deviceName = ''
    function.loadConfig = True
    function.updateRate = 1000
    suc = function.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_2(function):
    function.deviceName = 'test'
    function.loadConfig = True
    function.updateRate = 1000
    function.device = None
    suc = function.setUpdateConfig('test')
    assert not suc


def test_setUpdateConfig_3(function):
    function.deviceName = 'test'
    function.loadConfig = True
    function.updateRate = 1000
    function.device = Device()
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'Test': 1}):
        suc = function.setUpdateConfig('test')
        assert not suc


def test_setUpdateConfig_4(function):
    function.deviceName = 'test'
    function.loadConfig = True
    function.updateRate = 1000
    function.device = Device()
    function.client = Client()
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'PERIOD_MS': 1}):
        with mock.patch.object(function.client,
                               'sendNewNumber',
                               return_value=False):
            suc = function.setUpdateConfig('test')
            assert not suc


def test_setUpdateConfig_5(function):
    function.deviceName = 'test'
    function.loadConfig = True
    function.updateRate = 1000
    function.device = Device()
    function.client = Client()
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'PERIOD_MS': 1}):
        with mock.patch.object(function.client,
                               'sendNewNumber',
                               return_value=True):
            suc = function.setUpdateConfig('test')
            assert suc


def test_setExposureState_1(function):
    function.device = Device()
    setattr(function.device, 'CCD_EXPOSURE', {'state': 'Busy'})
    function.data = {'CCD_EXPOSURE.CCD_EXPOSURE_VALUE': 0.0000001}
    function.isDownloading = False
    suc = function.setExposureState()
    assert suc
    assert function.isDownloading


def test_setExposureState_2(function):
    function.device = Device()
    setattr(function.device, 'CCD_EXPOSURE', {'state': 'Busy'})
    function.data = {'CCD_EXPOSURE.CCD_EXPOSURE_VALUE': 0.0000001}
    function.isDownloading = True
    suc = function.setExposureState()
    assert suc
    assert function.isDownloading


def test_setExposureState_3(function):
    function.device = Device()
    setattr(function.device, 'CCD_EXPOSURE', {'state': 'Busy'})
    function.data = {'CCD_EXPOSURE.CCD_EXPOSURE_VALUE': 1}
    function.isDownloading = True
    suc = function.setExposureState()
    assert suc
    assert function.isDownloading


def test_setExposureState_4(function):
    function.device = Device()
    setattr(function.device, 'CCD_EXPOSURE', {'state': 'Busy'})
    function.data = {'CCD_EXPOSURE.CCD_EXPOSURE_VALUE': None}
    function.isDownloading = True
    suc = function.setExposureState()
    assert not suc
    assert function.isDownloading


def test_setExposureState_5(function):
    function.device = Device()
    setattr(function.device, 'CCD_EXPOSURE', {'state': 'Ok'})
    function.data = {'CCD_EXPOSURE.CCD_EXPOSURE_VALUE': None}
    function.isDownloading = True
    suc = function.setExposureState()
    assert suc
    assert not function.isDownloading


def test_setExposureState_6(function):
    function.device = Device()
    setattr(function.device, 'CCD_EXPOSURE', {'state': 'test'})
    function.data = {'CCD_EXPOSURE.CCD_EXPOSURE_VALUE': None}
    function.isDownloading = True
    suc = function.setExposureState()
    assert suc
    assert function.isDownloading


def test_setExposureState_7(function):
    function.device = Device()
    setattr(function.device, 'CCD_EXPOSURE', {'state': 'Alert'})
    function.data = {'CCD_EXPOSURE.CCD_EXPOSURE_VALUE': None}
    function.isDownloading = True
    suc = function.setExposureState()
    assert suc
    assert not function.isDownloading


def test_sendDownloadMode_1(function):
    function.deviceName = 'test'
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'Test': 1}):
        suc = function.sendDownloadMode()
        assert not suc


def test_updateNumber_1(function):
    suc = function.updateNumber('test', 'test')
    assert not suc


def test_updateNumber_2(function):
    function.device = Device()
    setattr(function.device, 'CCD_EXPOSURE', {'state': 'Busy'})

    function.data = {'AUTO_DEW.DEW_C': 1,
                'VERSION.UPB': 1}
    with mock.patch.object(IndiClass,
                           'updateNumber',
                           return_value=True):
        suc = function.updateNumber('test', 'CCD_EXPOSURE')
        assert suc


def test_updateNumber_3(function):
    function.data = {'AUTO_DEW.DEW_C': 1,
                'VERSION.UPB': 1}
    with mock.patch.object(IndiClass,
                           'updateNumber',
                           return_value=True):
        suc = function.updateNumber('test', 'CCD_TEMPERATURE')
        assert suc


def test_updateNumber_4(function):
    function.device = Device()
    data = {
        'elementList': {
            'GAIN': {
                'min': 1,
                'max': 1
            }
        }
    }
    setattr(function.device, 'CCD_GAIN', data)
    with mock.patch.object(IndiClass,
                           'updateNumber',
                           return_value=True):
        with mock.patch.object(function,
                               'setExposureState'):
            suc = function.updateNumber('test', 'CCD_GAIN')
        assert suc


def test_updateNumber_5(function):
    function.device = Device()
    data = {
        'elementList': {
            'OFFSET': {
                'min': 1,
                'max': 1
            }
        }
    }
    setattr(function.device, 'CCD_OFFSET', data)
    with mock.patch.object(IndiClass,
                           'updateNumber',
                           return_value=True):
        with mock.patch.object(function,
                               'setExposureState'):
            suc = function.updateNumber('test', 'CCD_OFFSET')
        assert suc


def test_updateHeaderInfo_1(function):
    header = {}
    function.app.mount.obsSite.raJNow = None
    function.app.mount.obsSite.decJNow = None
    function.app.mount.obsSite.timeJD = None
    h = function.updateHeaderInfo(header)
    assert 'RA' not in h
    assert 'DEC' not in h


def test_updateHeaderInfo_2(function):
    header = {'RA': 90,
              'DEC': 90}
    function.raJ2000 = Angle(hours=12)
    function.decJ2000 = Angle(degrees=90)
    function.app.mount.obsSite.raJNow = None
    function.app.mount.obsSite.decJNow = None
    function.app.mount.obsSite.timeJD = None
    h = function.updateHeaderInfo(header)
    assert 'RA' in h
    assert 'DEC' in h


def test_updateHeaderInfo_3(function):
    header = {}
    function.app.mount.obsSite.raJNow = Angle(hours=12)
    function.app.mount.obsSite.decJNow = Angle(degrees=180)
    function.app.mount.obsSite.timeJD = load.timescale().tt_jd(2451544.5)
    function.raJ2000 = Angle(hours=12)
    function.decJ2000 = Angle(degrees=90)
    h = function.updateHeaderInfo(header)
    assert 'RA' in h
    assert 'DEC' in h
    assert h['RA'] != 0
    assert h['DEC'] != 0


def test_saveBlobSignalsFinished(function):
    suc = function.saveBlobSignalsFinished()
    assert suc


def test_workerSaveBLOB_1(function):
    function.imagePath = 'tests/workDir/image/test.fit'
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    data = {'value': '1',
            'name': 'CCD1',
            'format': '.fits.fz'}
    with mock.patch.object(fits.HDUList,
                           'fromstring',
                           return_value=hdu):
        suc = function.workerSaveBLOB(data)
        assert suc


def test_workerSaveBLOB_2(function):
    function.imagePath = 'tests/workDir/image/test.fit'
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    data = {'value': zlib.compress(b'1'),
            'name': 'CCD1',
            'format': '.fits.z'}
    with mock.patch.object(fits.HDUList,
                           'fromstring',
                           return_value=hdu):
        suc = function.workerSaveBLOB(data)
        assert suc


def test_workerSaveBLOB_3(function):
    function.imagePath = 'tests/workDir/image/test.fit'
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    data = {'value': '1',
            'name': 'CCD1',
            'format': '.fits'}
    with mock.patch.object(fits.HDUList,
                           'fromstring',
                           return_value=hdu):
        suc = function.workerSaveBLOB(data)
        assert suc


def test_workerSaveBLOB_4(function):
    function.imagePath = 'tests/workDir/image/test.fit'
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    data = {'value': '1',
            'name': 'CCD1',
            'format': '.test'}
    with mock.patch.object(fits.HDUList,
                           'fromstring',
                           return_value=hdu):
        suc = function.workerSaveBLOB(data)
        assert suc


def test_updateBLOB_1(function):
    function.device = Device()
    with mock.patch.object(IndiClass,
                           'updateBLOB',
                           return_value=False):
        suc = function.updateBLOB('test', 'test')
        assert not suc


def test_updateBLOB_2(function):
    function.device = Device()
    with mock.patch.object(IndiClass,
                           'updateBLOB',
                           return_value=True):
        with mock.patch.object(function.device,
                               'getBlob',
                               return_value={}):
            suc = function.updateBLOB('test', 'test')
            assert not suc


def test_updateBLOB_3(function):
    function.device = Device()
    with mock.patch.object(IndiClass,
                           'updateBLOB',
                           return_value=True):
        with mock.patch.object(function.device,
                               'getBlob',
                               return_value={'value': 1}):
            suc = function.updateBLOB('test', 'test')
            assert not suc


def test_updateBLOB_4(function):
    function.device = Device()
    with mock.patch.object(IndiClass,
                           'updateBLOB',
                           return_value=True):
        with mock.patch.object(function.device,
                               'getBlob',
                               return_value={'value': 1,
                                             'name': 'test'}):
            suc = function.updateBLOB('test', 'test')
            assert not suc


def test_updateBLOB_5(function):
    function.device = Device()
    with mock.patch.object(IndiClass,
                           'updateBLOB',
                           return_value=True):
        with mock.patch.object(function.device,
                               'getBlob',
                               return_value={'value': 1,
                                             'name': 'CCD2',
                                             'format': 'test'}):
            suc = function.updateBLOB('test', 'test')
            assert not suc


def test_updateBLOB_6(function):
    function.device = Device()
    with mock.patch.object(IndiClass,
                           'updateBLOB',
                           return_value=True):
        with mock.patch.object(function.device,
                               'getBlob',
                               return_value={'value': 1,
                                             'name': 'CCD1',
                                             'format': 'test'}):
            suc = function.updateBLOB('test', 'test')
            assert not suc


def test_updateBLOB_7(function):
    function.device = Device()
    function.imagePath = 'tests/dummy/test.txt'
    with mock.patch.object(IndiClass,
                           'updateBLOB',
                           return_value=True):
        with mock.patch.object(function.device,
                               'getBlob',
                               return_value={'value': 1,
                                             'name': 'CCD1',
                                             'format': 'test'}):
            suc = function.updateBLOB('test', 'test')
            assert not suc


def test_updateBLOB_8(function):
    function.device = Device()
    function.imagePath = 'tests/workDir/image/test.fit'
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    with mock.patch.object(IndiClass,
                           'updateBLOB',
                           return_value=True):
        with mock.patch.object(function.device,
                               'getBlob',
                               return_value={'value': 1,
                                             'name': 'CCD1',
                                             'format': '.fits.fz'}):
            with mock.patch.object(fits.HDUList,
                                   'fromstring',
                                   return_value=hdu):
                suc = function.updateBLOB('test', 'test')
                assert suc


def test_expose_1(function):
    function.deviceName = 'test'
    function.device = None
    suc = function.expose()
    assert not suc


def test_expose_2(function):
    function.deviceName = 'test'
    function.device = Device()
    with mock.patch.object(function,
                           'sendDownloadMode',
                           return_value=False):
        suc = function.expose()
        assert not suc


def test_expose_3(function):
    function.deviceName = 'test'
    function.device = Device()
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={}):
        with mock.patch.object(function.client,
                               'sendNewNumber',
                               return_value=False):
            suc = function.expose()
            assert not suc


def test_expose_4(function):
    function.deviceName = 'test'
    function.device = Device()
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={}):
        with mock.patch.object(function.client,
                               'sendNewNumber',
                               return_value=True):
            suc = function.expose()
            assert suc


def test_abort_1(function):
    function.deviceName = 'test'
    function.device = None
    suc = function.abort()
    assert not suc


def test_abort_2(function):
    function.deviceName = 'test'
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'Test': 1}):
        suc = function.abort()
        assert not suc


def test_abort_3(function):
    function.deviceName = 'test'
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'ABORT': 1}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=True):
            suc = function.abort()
            assert suc


def test_sendCoolerSwitch_1(function):
    function.deviceName = 'test'
    function.device = None
    suc = function.sendCoolerSwitch()
    assert not suc


def test_sendCoolerSwitch_2(function):
    function.deviceName = 'test'
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'Test': 1}):
        suc = function.sendCoolerSwitch()
        assert not suc


def test_sendCoolerSwitch_3(function):
    function.deviceName = 'test'
    function.device = Device()
    with mock.patch.object(function.device,
                           'getSwitch',
                           return_value={'COOLER_ON': True}):
        with mock.patch.object(function.client,
                               'sendNewSwitch',
                               return_value=True):
            suc = function.sendCoolerSwitch(True)
            assert suc


def test_sendCoolerTemp_1(function):
    function.deviceName = 'test'
    function.device = None
    suc = function.sendCoolerTemp()
    assert not suc


def test_sendCoolerTemp_2(function):
    function.deviceName = 'test'
    function.device = Device()
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'Test': 1}):
        suc = function.sendCoolerTemp()
        assert not suc


def test_sendCoolerTemp_3(function):
    function.deviceName = 'test'
    function.device = Device()
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'CCD_TEMPERATURE_VALUE': 1}):
        with mock.patch.object(function.client,
                               'sendNewNumber',
                               return_value=True):
            suc = function.sendCoolerTemp()
            assert suc


def test_sendOffset_1(function):
    function.deviceName = 'test'
    function.device = None
    suc = function.sendOffset()
    assert not suc


def test_sendOffset_2(function):
    function.deviceName = 'test'
    function.device = Device()
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'Test': 1}):
        suc = function.sendOffset()
        assert not suc


def test_sendOffset_3(function):
    function.deviceName = 'test'
    function.device = Device()
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'OFFSET': 1}):
        with mock.patch.object(function.client,
                               'sendNewNumber',
                               return_value=True):
            suc = function.sendOffset()
            assert suc


def test_sendGain_1(function):
    function.deviceName = 'test'
    function.device = None
    suc = function.sendGain()
    assert not suc


def test_sendGain_2(function):
    function.deviceName = 'test'
    function.device = Device()
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'Test': 1}):
        suc = function.sendGain()
        assert not suc


def test_sendGain_3(function):
    function.deviceName = 'test'
    function.device = Device()
    with mock.patch.object(function.device,
                           'getNumber',
                           return_value={'GAIN': 1}):
        with mock.patch.object(function.client,
                               'sendNewNumber',
                               return_value=True):
            suc = function.sendGain()
            assert suc
