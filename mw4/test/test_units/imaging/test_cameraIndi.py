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


def test_setUpdateConfig_1():
    deviceName = None
    suc = app.camera.run['indi'].setUpdateConfig(deviceName=deviceName)
    assert not suc


def test_setUpdateConfig_2():
    deviceName = 'CCD Simulator'
    suc = app.camera.run['indi'].setUpdateConfig(deviceName=deviceName)
    assert not suc


def test_setUpdateConfig_3():
    deviceName = 'CCD Simulator'
    app.camera.run['indi'].device = IndiClass().device
    app.camera.run['indi'].name = 'CCD Simulator'
    suc = app.camera.run['indi'].setUpdateConfig(deviceName=deviceName)
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
    app.camera.run['indi'].name = 'CCD Simulator'
    app.camera.run['indi'].device = Test()

    suc = app.camera.run['indi'].setUpdateConfig(deviceName=deviceName)
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
    app.camera.run['indi'].name = 'CCD Simulator'
    app.camera.run['indi'].device = Test()

    suc = app.camera.run['indi'].setUpdateConfig(deviceName=deviceName)
    assert suc


def test_setExposureState_1(qtbot):
    with qtbot.assertNotEmitted(app.camera.run['indi'].signals.message):
        suc = app.camera.run['indi'].setExposureState()
        assert not suc


def test_setExposureState_2(qtbot):
    app.camera.data['CCD_EXPOSURE.CCD_EXPOSURE_VALUE'] = 0
    setattr(app.camera.run['indi'].device, 'CCD_EXPOSURE', {'state': 'Idle'})
    with qtbot.waitSignal(app.camera.run['indi'].signals.message) as blocker:
        suc = app.camera.run['indi'].setExposureState()
        assert suc
    assert [''] == blocker.args


def test_setExposureState_3(qtbot):
    app.camera.data['CCD_EXPOSURE.CCD_EXPOSURE_VALUE'] = 0
    setattr(app.camera.run['indi'].device, 'CCD_EXPOSURE', {'state': 'Busy'})
    with qtbot.waitSignal(app.camera.run['indi'].signals.message) as blocker:
        suc = app.camera.run['indi'].setExposureState()
        assert suc
    assert ['download'] == blocker.args


def test_setExposureState_4(qtbot):
    app.camera.data['CCD_EXPOSURE.CCD_EXPOSURE_VALUE'] = 1
    setattr(app.camera.run['indi'].device, 'CCD_EXPOSURE', {'state': 'Busy'})
    with qtbot.waitSignal(app.camera.run['indi'].signals.message) as blocker:
        suc = app.camera.run['indi'].setExposureState()
        assert suc
    assert ['expose  1 s'] == blocker.args


def test_setExposureState_5(qtbot):
    app.camera.data['CCD_EXPOSURE.CCD_EXPOSURE_VALUE'] = 0
    setattr(app.camera.run['indi'].device, 'CCD_EXPOSURE', {'state': 'Ok'})
    with qtbot.waitSignal(app.camera.run['indi'].signals.message) as blocker:
        suc = app.camera.run['indi'].setExposureState()
        assert suc
    assert [''] == blocker.args


def test_setExposureState_6(qtbot):
    app.camera.data['CCD_EXPOSURE.CCD_EXPOSURE_VALUE'] = 0
    setattr(app.camera.run['indi'].device, 'CCD_EXPOSURE', {'state': 'Busy'})
    with qtbot.waitSignal(app.camera.run['indi'].signals.integrated) as blocker:
        suc = app.camera.run['indi'].setExposureState()
        assert suc


def test_updateNumber_1():
    class Test:
        name = 'test'

    propertyName = ''
    deviceName = ''
    app.camera.run['indi'].device = None
    app.camera.run['indi'].device = IndiClass().device
    suc = app.camera.run['indi'].updateNumber(propertyName=propertyName,
                                              deviceName=deviceName)
    assert not suc


def test_updateNumber_2():
    class Test:
        name = 'test'

        @staticmethod
        def getNumber(name):
            return {}

    propertyName = ''
    app.camera.run['indi'].device = Test()
    deviceName = 'tester'
    app.camera.run['indi'].name = 'test'
    suc = app.camera.run['indi'].updateNumber(propertyName=propertyName,
                                              deviceName=deviceName)
    assert not suc


def test_updateNumber_3():
    class Test:
        name = 'test'

        @staticmethod
        def getNumber(name):
            return {}

    propertyName = ''
    app.camera.run['indi'].device = Test()
    deviceName = 'test'
    app.camera.run['indi'].name = 'test'
    suc = app.camera.run['indi'].updateNumber(propertyName=propertyName,
                                              deviceName=deviceName)
    assert suc


def test_updateText_1():
    class Test:
        name = 'test'

    propertyName = ''
    deviceName = ''
    app.camera.run['indi'].device = None
    app.camera.run['indi'].device = IndiClass().device
    suc = app.camera.run['indi'].updateText(propertyName=propertyName,
                                            deviceName=deviceName)
    assert not suc


def test_updateText_2():
    class Test:
        name = 'test'

        @staticmethod
        def getText(name):
            return {}

    propertyName = ''
    app.camera.run['indi'].device = Test()
    deviceName = 'tester'
    app.camera.run['indi'].name = 'test'
    suc = app.camera.run['indi'].updateText(propertyName=propertyName,
                                            deviceName=deviceName)
    assert not suc


def test_updateText_3():
    class Test:
        name = 'test'

        @staticmethod
        def getText(name):
            return {}

    propertyName = ''
    app.camera.run['indi'].device = Test()
    deviceName = 'test'
    app.camera.run['indi'].name = 'test'
    suc = app.camera.run['indi'].updateText(propertyName=propertyName,
                                            deviceName=deviceName)
    assert suc


def test_updateSwitch_1():
    class Test:
        name = 'test'

    propertyName = ''
    deviceName = ''
    app.camera.run['indi'].device = None
    app.camera.run['indi'].device = IndiClass().device
    suc = app.camera.run['indi'].updateSwitch(propertyName=propertyName,
                                              deviceName=deviceName)
    assert not suc


def test_updateSwitch_2():
    class Test:
        name = 'test'

        @staticmethod
        def getNumber(name):
            return {}

    propertyName = ''
    app.camera.run['indi'].device = Test()
    deviceName = 'tester'
    app.camera.run['indi'].name = 'test'
    suc = app.camera.run['indi'].updateSwitch(propertyName=propertyName,
                                              deviceName=deviceName)
    assert not suc


def test_updateSwitch_3():
    class Test:
        name = 'test'

        @staticmethod
        def getSwitch(name):
            return {}

    propertyName = ''
    app.camera.run['indi'].device = Test()
    deviceName = 'test'
    app.camera.run['indi'].name = 'test'
    suc = app.camera.run['indi'].updateSwitch(propertyName=propertyName,
                                              deviceName=deviceName)
    assert suc


def test_updateLight_1():
    class Test:
        name = 'test'

    propertyName = ''
    deviceName = ''
    app.camera.run['indi'].device = None
    app.camera.run['indi'].device = IndiClass().device
    suc = app.camera.run['indi'].updateLight(propertyName=propertyName,
                                             deviceName=deviceName)
    assert not suc


def test_updateLight_2():
    class Test:
        name = 'test'

        @staticmethod
        def getLight(name):
            return {}

    propertyName = ''
    app.camera.run['indi'].device = Test()
    deviceName = 'tester'
    app.camera.run['indi'].name = 'test'
    suc = app.camera.run['indi'].updateLight(propertyName=propertyName,
                                             deviceName=deviceName)
    assert not suc


def test_updateLight_3():
    class Test:
        name = 'test'

        @staticmethod
        def getLight(name):
            return {}

    propertyName = ''
    app.camera.run['indi'].device = Test()
    deviceName = 'test'
    app.camera.run['indi'].name = 'test'
    suc = app.camera.run['indi'].updateLight(propertyName=propertyName,
                                             deviceName=deviceName)
    assert suc


def test_updateBLOB_1():
    class Test:
        name = 'test'

    propertyName = ''
    deviceName = ''
    app.camera.run['indi'].device = None
    app.camera.run['indi'].device = IndiClass().device
    suc = app.camera.run['indi'].updateBLOB(propertyName=propertyName,
                                            deviceName=deviceName)
    assert not suc


def test_updateBLOB_2():
    class Test:
        name = 'test'

        @staticmethod
        def getBlob(name):
            return {}

    propertyName = ''
    app.camera.run['indi'].device = Test()
    deviceName = 'tester'
    app.camera.run['indi'].name = 'test'
    suc = app.camera.run['indi'].updateBLOB(propertyName=propertyName,
                                            deviceName=deviceName)
    assert not suc


def test_updateBLOB_3():
    class Test:
        name = 'test'

        @staticmethod
        def getBlob(name):
            return {}

    propertyName = ''
    app.camera.run['indi'].device = Test()
    deviceName = 'test'
    app.camera.run['indi'].name = 'test'
    suc = app.camera.run['indi'].updateBLOB(propertyName=propertyName,
                                            deviceName=deviceName)
    assert not suc


def test_updateBLOB_4():
    class Test:
        name = 'test'

        @staticmethod
        def getBlob(name):
            return {}

    propertyName = ''
    app.camera.run['indi'].device = Test()
    deviceName = 'test'
    app.camera.run['indi'].name = 'test'

    suc = app.camera.run['indi'].updateBLOB(propertyName=propertyName,
                                            deviceName=deviceName)
    assert not suc


def test_updateBLOB_5():
    class Test:
        name = 'test'

        @staticmethod
        def getBlob(name):
            return {'value': 'CCD1'}

    propertyName = ''
    app.camera.run['indi'].device = Test()
    deviceName = 'test'
    app.camera.run['indi'].name = 'test'
    app.camera.run['indi'].imagePath = 'test'

    suc = app.camera.run['indi'].updateBLOB(propertyName=propertyName,
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
    app.camera.run['indi'].device = Test()
    deviceName = 'test'
    app.camera.run['indi'].name = 'test'
    app.camera.run['indi'].imagePath = mwGlob['imageDir'] + '/test.fit'

    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    with mock.patch.object(fits.HDUList,
                           'fromstring',
                           return_value=hdu):
        suc = app.camera.run['indi'].updateBLOB(propertyName=propertyName,
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
    app.camera.run['indi'].device = Test()
    deviceName = 'test'
    app.camera.run['indi'].name = 'test'
    app.camera.run['indi'].imagePath = mwGlob['imageDir'] + '/test.fit'

    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    with mock.patch.object(fits.HDUList,
                           'fromstring',
                           return_value=hdu):
        suc = app.camera.run['indi'].updateBLOB(propertyName=propertyName,
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
    app.camera.run['indi'].device = Test()
    deviceName = 'test'
    app.camera.run['indi'].name = 'test'
    app.camera.run['indi'].imagePath = mwGlob['imageDir'] + '/test.fit'

    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    with mock.patch.object(fits.HDUList,
                           'fromstring',
                           return_value=hdu):
        suc = app.camera.run['indi'].updateBLOB(propertyName=propertyName,
                                                deviceName=deviceName)
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

    app.camera.run['indi'].device = Test()
    app.camera.run['indi'].client = Test1()

    suc = app.camera.run['indi'].abort()
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

    app.camera.run['indi'].device = Test()
    app.camera.run['indi'].client = Test1()

    suc = app.camera.run['indi'].abort()
    assert suc
