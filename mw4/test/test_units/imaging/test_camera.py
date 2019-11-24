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
import zlib
# external packages
from astropy.io import fits
# local import
from mw4.test.test_units.setupQt import setupQt
from mw4.imaging.camera import CameraSignals, Camera
from mw4.base.indiClass import IndiClass


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    yield
    import shutil
    shutil.rmtree(mwGlob['imageDir'] + 'm-file*', ignore_errors=True)


def test_cameraSignals_1():
    a = CameraSignals()
    assert a.integrated
    assert a.saved
    assert a.message


def test_setUpdateConfig_1():
    deviceName = None
    suc = app.imaging.setUpdateConfig(deviceName=deviceName)
    assert not suc


def test_setUpdateConfig_2():
    deviceName = 'CCD Simulator'
    suc = app.imaging.setUpdateConfig(deviceName=deviceName)
    assert not suc


def test_setUpdateConfig_3():
    deviceName = 'CCD Simulator'
    app.imaging.device = IndiClass().device
    app.imaging.name = 'CCD Simulator'
    suc = app.imaging.setUpdateConfig(deviceName=deviceName)
    assert not suc


def test_setUpdateConfig_4():
    class Test:

        @staticmethod
        def getNumber(number):
            return {'PERIOD': 1000}

        @staticmethod
        def getText(text):
            return {'POLLING_PERIOD': {'PERIOD_MS': 1000}}

        @staticmethod
        def getSwitch(switch):
            return {'POLLING_PERIOD': {'PERIOD_MS': 1000}}

    deviceName = 'CCD Simulator'
    app.imaging.name = 'CCD Simulator'
    app.imaging.device = Test()

    suc = app.imaging.setUpdateConfig(deviceName=deviceName)
    assert not suc


def test_setUpdateConfig_5():
    class Test:

        @staticmethod
        def getNumber(number):
            return {'PERIOD_MS': 1000}

        @staticmethod
        def getText(text):
            return {'POLLING_PERIOD': {'PERIOD_MS': 1000}}

        @staticmethod
        def getSwitch(switch):
            return {'POLLING_PERIOD': {'PERIOD_MS': 1000}}

    deviceName = 'CCD Simulator'
    app.imaging.name = 'CCD Simulator'
    app.imaging.device = Test()

    suc = app.imaging.setUpdateConfig(deviceName=deviceName)
    assert suc


def test_setExposureState_1(qtbot):
    propertyName = ''
    value = 0
    with qtbot.assertNotEmitted(app.imaging.signals.message):
        suc = app.imaging.setExposureState(propertyName=propertyName,
                                           value=value)
        assert not suc


def test_setExposureState_2(qtbot):
    propertyName = 'CCD_EXPOSURE'
    value = 0
    setattr(app.imaging.device, 'CCD_EXPOSURE', {'state': 'Idle'})
    with qtbot.waitSignal(app.imaging.signals.message) as blocker:
        suc = app.imaging.setExposureState(propertyName=propertyName,
                                           value=value)
        assert suc
    assert [''] == blocker.args


def test_setExposureState_3(qtbot):
    propertyName = 'CCD_EXPOSURE'
    value = 0
    setattr(app.imaging.device, 'CCD_EXPOSURE', {'state': 'Busy'})
    with qtbot.waitSignal(app.imaging.signals.message) as blocker:
        suc = app.imaging.setExposureState(propertyName=propertyName,
                                           value=value)
        assert suc
    assert ['download'] == blocker.args


def test_setExposureState_4(qtbot):
    propertyName = 'CCD_EXPOSURE'
    value = 1
    setattr(app.imaging.device, 'CCD_EXPOSURE', {'state': 'Busy'})
    with qtbot.waitSignal(app.imaging.signals.message) as blocker:
        suc = app.imaging.setExposureState(propertyName=propertyName,
                                           value=value)
        assert suc
    assert ['expose  1 s'] == blocker.args


def test_setExposureState_5(qtbot):
    propertyName = 'CCD_EXPOSURE'
    value = 0
    setattr(app.imaging.device, 'CCD_EXPOSURE', {'state': 'Ok'})
    with qtbot.waitSignal(app.imaging.signals.message) as blocker:
        suc = app.imaging.setExposureState(propertyName=propertyName,
                                           value=value)
        assert suc
    assert [''] == blocker.args


def test_setExposureState_6(qtbot):
    propertyName = 'CCD_EXPOSURE'
    value = 0
    setattr(app.imaging.device, 'CCD_EXPOSURE', {'state': 'Busy'})
    with qtbot.waitSignal(app.imaging.signals.integrated) as blocker:
        suc = app.imaging.setExposureState(propertyName=propertyName,
                                           value=value)
        assert suc


def test_updateNumber_1():
    class Test:
        name = 'test'

    propertyName = ''
    deviceName = ''
    app.imaging.device = None
    app.imaging.device = IndiClass().device
    suc = app.imaging.updateNumber(propertyName=propertyName,
                                   deviceName=deviceName)
    assert not suc


def test_updateNumber_2():
    class Test:
        name = 'test'

        @staticmethod
        def getNumber(name):
            return {}

    propertyName = ''
    app.imaging.device = Test()
    deviceName = 'tester'
    app.imaging.name = 'test'
    suc = app.imaging.updateNumber(propertyName=propertyName,
                                   deviceName=deviceName)
    assert not suc


def test_updateNumber_3():
    class Test:
        name = 'test'

        @staticmethod
        def getNumber(name):
            return {}

    propertyName = ''
    app.imaging.device = Test()
    deviceName = 'test'
    app.imaging.name = 'test'
    suc = app.imaging.updateNumber(propertyName=propertyName,
                                   deviceName=deviceName)
    assert suc


def test_updateText_1():
    class Test:
        name = 'test'

    propertyName = ''
    deviceName = ''
    app.imaging.device = None
    app.imaging.device = IndiClass().device
    suc = app.imaging.updateText(propertyName=propertyName,
                                 deviceName=deviceName)
    assert not suc


def test_updateText_2():
    class Test:
        name = 'test'

        @staticmethod
        def getText(name):
            return {}

    propertyName = ''
    app.imaging.device = Test()
    deviceName = 'tester'
    app.imaging.name = 'test'
    suc = app.imaging.updateText(propertyName=propertyName,
                                 deviceName=deviceName)
    assert not suc


def test_updateText_3():
    class Test:
        name = 'test'

        @staticmethod
        def getText(name):
            return {}

    propertyName = ''
    app.imaging.device = Test()
    deviceName = 'test'
    app.imaging.name = 'test'
    suc = app.imaging.updateText(propertyName=propertyName,
                                 deviceName=deviceName)
    assert suc


def test_updateSwitch_1():
    class Test:
        name = 'test'

    propertyName = ''
    deviceName = ''
    app.imaging.device = None
    app.imaging.device = IndiClass().device
    suc = app.imaging.updateSwitch(propertyName=propertyName,
                                   deviceName=deviceName)
    assert not suc


def test_updateSwitch_2():
    class Test:
        name = 'test'

        @staticmethod
        def getNumber(name):
            return {}

    propertyName = ''
    app.imaging.device = Test()
    deviceName = 'tester'
    app.imaging.name = 'test'
    suc = app.imaging.updateSwitch(propertyName=propertyName,
                                   deviceName=deviceName)
    assert not suc


def test_updateSwitch_3():
    class Test:
        name = 'test'

        @staticmethod
        def getSwitch(name):
            return {}

    propertyName = ''
    app.imaging.device = Test()
    deviceName = 'test'
    app.imaging.name = 'test'
    suc = app.imaging.updateSwitch(propertyName=propertyName,
                                   deviceName=deviceName)
    assert suc


def test_updateLight_1():
    class Test:
        name = 'test'

    propertyName = ''
    deviceName = ''
    app.imaging.device = None
    app.imaging.device = IndiClass().device
    suc = app.imaging.updateLight(propertyName=propertyName,
                                  deviceName=deviceName)
    assert not suc


def test_updateLight_2():
    class Test:
        name = 'test'

        @staticmethod
        def getLight(name):
            return {}

    propertyName = ''
    app.imaging.device = Test()
    deviceName = 'tester'
    app.imaging.name = 'test'
    suc = app.imaging.updateLight(propertyName=propertyName,
                                  deviceName=deviceName)
    assert not suc


def test_updateLight_3():
    class Test:
        name = 'test'

        @staticmethod
        def getLight(name):
            return {}

    propertyName = ''
    app.imaging.device = Test()
    deviceName = 'test'
    app.imaging.name = 'test'
    suc = app.imaging.updateLight(propertyName=propertyName,
                                  deviceName=deviceName)
    assert suc


def test_updateBLOB_1():
    class Test:
        name = 'test'

    propertyName = ''
    deviceName = ''
    app.imaging.device = None
    app.imaging.device = IndiClass().device
    suc = app.imaging.updateBLOB(propertyName=propertyName,
                                 deviceName=deviceName)
    assert not suc


def test_updateBLOB_2():
    class Test:
        name = 'test'

        @staticmethod
        def getBlob(name):
            return {}

    propertyName = ''
    app.imaging.device = Test()
    deviceName = 'tester'
    app.imaging.name = 'test'
    suc = app.imaging.updateBLOB(propertyName=propertyName,
                                 deviceName=deviceName)
    assert not suc


def test_updateBLOB_3():
    class Test:
        name = 'test'

        @staticmethod
        def getBlob(name):
            return {}

    propertyName = ''
    app.imaging.device = Test()
    deviceName = 'test'
    app.imaging.name = 'test'
    suc = app.imaging.updateBLOB(propertyName=propertyName,
                                 deviceName=deviceName)
    assert not suc


def test_updateBLOB_4():
    class Test:
        name = 'test'

        @staticmethod
        def getBlob(name):
            return {}

    propertyName = ''
    app.imaging.device = Test()
    deviceName = 'test'
    app.imaging.name = 'test'

    suc = app.imaging.updateBLOB(propertyName=propertyName,
                                 deviceName=deviceName)
    assert not suc


def test_updateBLOB_5():
    class Test:
        name = 'test'

        @staticmethod
        def getBlob(name):
            return {'value': 'CCD1'}

    propertyName = ''
    app.imaging.device = Test()
    deviceName = 'test'
    app.imaging.name = 'test'
    app.imaging.imagePath = 'test'

    suc = app.imaging.updateBLOB(propertyName=propertyName,
                                 deviceName=deviceName)
    assert not suc


def test_updateBLOB_5():
    class Test:
        name = 'test'

        @staticmethod
        def getBlob(name):
            return {'name': 'CCD1',
                    'value': 'CCD1',
                    'format': '.fits.fz'}

    propertyName = ''
    app.imaging.device = Test()
    deviceName = 'test'
    app.imaging.name = 'test'
    app.imaging.imagePath = './mw4/test/test_units/image/test.fit'

    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    with mock.patch.object(fits.HDUList,
                           'fromstring',
                           return_value=hdu):
        suc = app.imaging.updateBLOB(propertyName=propertyName,
                                     deviceName=deviceName)
        assert suc


def test_updateBLOB_6():
    class Test:
        name = 'test'

        @staticmethod
        def getBlob(name):
            return {'name': 'CCD1',
                    'value': zlib.compress(b'CCD1'),
                    'format': '.fits.z'}

    propertyName = ''
    app.imaging.device = Test()
    deviceName = 'test'
    app.imaging.name = 'test'
    app.imaging.imagePath = './mw4/test/test_units/image/test.fit'

    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    with mock.patch.object(fits.HDUList,
                           'fromstring',
                           return_value=hdu):
        suc = app.imaging.updateBLOB(propertyName=propertyName,
                                     deviceName=deviceName)
        assert suc


def test_updateBLOB_7():
    class Test:
        name = 'test'

        @staticmethod
        def getBlob(name):
            return {'name': 'CCD1',
                    'value': 'CCD1',
                    'format': '.fits'}

    propertyName = ''
    app.imaging.device = Test()
    deviceName = 'test'
    app.imaging.name = 'test'
    app.imaging.imagePath = './mw4/test/test_units/image/test.fit'

    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    with mock.patch.object(fits.HDUList,
                           'fromstring',
                           return_value=hdu):
        suc = app.imaging.updateBLOB(propertyName=propertyName,
                                     deviceName=deviceName)
        assert suc


def test_canSubFrame_1():
    suc = app.imaging.canSubFrame()
    assert not suc


def test_canSubFrame_2():
    suc = app.imaging.canSubFrame(subFrame=5)
    assert not suc


def test_canSubFrame_3():
    suc = app.imaging.canSubFrame(subFrame=110)
    assert not suc


def test_canSubFrame_4():
    app.imaging.data['CCD_FRAME.X'] = 1
    suc = app.imaging.canSubFrame()
    assert not suc


def test_canSubFrame_5():
    del app.imaging.data['CCD_FRAME.X']
    app.imaging.data['CCD_FRAME.Y'] = 1
    suc = app.imaging.canSubFrame()
    assert not suc


def test_canSubFrame_6():
    app.imaging.data['CCD_FRAME.Y'] = 1
    app.imaging.data['CCD_FRAME.X'] = 1
    suc = app.imaging.canSubFrame()
    assert suc


def test_canBinning_1():
    suc = app.imaging.canBinning()
    assert not suc


def test_canBinning_2():
    suc = app.imaging.canBinning(binning=0)
    assert not suc


def test_canBinning_3():
    suc = app.imaging.canBinning(binning=5)
    assert not suc


def test_canBinning_4():
    app.imaging.data['CCD_BINNING.HOR_BIN'] = 1
    suc = app.imaging.canBinning()
    assert suc


def test_calcSubFrame_1():
    app.imaging.data['CCD_INFO.CCD_MAX_X'] = 1000
    app.imaging.data['CCD_INFO.CCD_MAX_Y'] = 1000
    subFrame = 100

    px, py, w, h = app.imaging.calcSubFrame(subFrame=subFrame)
    assert py == 0
    assert py == 0
    assert w == 1000
    assert h == 1000


def test_calcSubFrame_2():
    app.imaging.data['CCD_INFO.CCD_MAX_X'] = 1000
    app.imaging.data['CCD_INFO.CCD_MAX_Y'] = 1000
    subFrame = 50

    px, py, w, h = app.imaging.calcSubFrame(subFrame=subFrame)
    assert py == 250
    assert py == 250
    assert w == 500
    assert h == 500


def test_calcSubFrame_3():
    app.imaging.data['CCD_INFO.CCD_MAX_X'] = 1001
    app.imaging.data['CCD_INFO.CCD_MAX_Y'] = 1001
    subFrame = 50

    px, py, w, h = app.imaging.calcSubFrame(subFrame=subFrame)
    assert py == 250
    assert py == 250
    assert w == 500
    assert h == 500


def test_calcSubFrame_4():
    app.imaging.data['CCD_INFO.CCD_MAX_X'] = 1001
    app.imaging.data['CCD_INFO.CCD_MAX_Y'] = 1001
    subFrame = 10

    px, py, w, h = app.imaging.calcSubFrame(subFrame=subFrame)
    assert py == 450
    assert py == 450
    assert w == 100
    assert h == 100


def test_calcSubFrame_5():
    app.imaging.data['CCD_INFO.CCD_MAX_X'] = 1001
    app.imaging.data['CCD_INFO.CCD_MAX_Y'] = 1001
    subFrame = 5

    px, py, w, h = app.imaging.calcSubFrame(subFrame=subFrame)
    assert py == 0
    assert py == 0
    assert w == 1001
    assert h == 1001


def test_setupExposure_1():
    class Test:
        @staticmethod
        def getSwitch(name):
            return {'test': False}

    app.imaging.device = Test()

    suc = app.imaging.setupFrameCompress()
    assert not suc


def test_setupExposure_2():
    class Test:
        @staticmethod
        def getSwitch(name):
            return {'CCD_COMPRESS': False}

    app.imaging.device = Test()

    suc = app.imaging.setupFrameCompress()
    assert not suc


def test_setupExposure_3():
    class Test:
        @staticmethod
        def getSwitch(name):
            return {'CCD_COMPRESS': False}

    class Test1:
        @staticmethod
        def sendNewSwitch(deviceName='',
                          propertyName='',
                          elements=None):
            return True

    app.imaging.device = Test()
    app.imaging.client = Test1()

    suc = app.imaging.setupFrameCompress()
    assert not suc


def test_setupExposure_4():
    class Test:
        @staticmethod
        def getSwitch(name):
            return {'CCD_COMPRESS': False,
                    'FRAME_LIGHT': True}

    class Test1:
        @staticmethod
        def sendNewSwitch(deviceName='',
                          propertyName='',
                          elements=None):
            return True

    app.imaging.device = Test()
    app.imaging.client = Test1()

    suc = app.imaging.setupFrameCompress()
    assert suc


def test_expose_1():
    suc = app.imaging.expose()
    assert not suc


def test_expose_2():
    class Test:
        @staticmethod
        def getNumber(name):
            return {}

        @staticmethod
        def getSwitch(name):
            return {}

    class Test1:
        @staticmethod
        def sendNewNumber(deviceName='',
                          propertyName='',
                          elements=None):
            return True

        @staticmethod
        def sendNewSwitch(deviceName='',
                          propertyName='',
                          elements=None):
            return True

    app.imaging.device = Test()
    app.imaging.client = Test1()

    with mock.patch.object(app.imaging,
                           'setupFrameCompress',
                           return_value=True):
        suc = app.imaging.expose(imagePath='test')
        assert suc


def test_abort_1():
    class Test:
        @staticmethod
        def getSwitch(name):
            return {}

    class Test1:
        @staticmethod
        def sendNewSwitch(deviceName='',
                          propertyName='',
                          elements=None):
            return True

    app.imaging.device = Test()
    app.imaging.client = Test1()

    suc = app.imaging.abort()
    assert not suc


def test_abort_2():
    class Test:
        @staticmethod
        def getSwitch(name):
            return {'ABORT': True}

    class Test1:
        @staticmethod
        def sendNewSwitch(deviceName='',
                          propertyName='',
                          elements=None):
            return True

    app.imaging.device = Test()
    app.imaging.client = Test1()

    suc = app.imaging.abort()
    assert suc
