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
# Python  v3.7.4
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
# local import
from mw4.test.test_units.setupQt import setupQt
from mw4.imaging.camera import CameraSignals, Camera
from mw4.base.indiClass import IndiClass


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    yield


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


def test_setPixelSize_1():
    propertyName = ''
    element = ''
    value = 0
    suc = app.imaging.setPixelSize(propertyName=propertyName,
                                   element=element,
                                   value=value)
    assert not suc


def test_setPixelSize_2():
    propertyName = 'CCD_INFO'
    element = ''
    value = 0
    suc = app.imaging.setPixelSize(propertyName=propertyName,
                                   element=element,
                                   value=value)
    assert not suc


def test_setPixelSize_3():
    propertyName = 'CCD_INFO'
    element = 'CCD_PIXEL_SIZE_X'
    value = 0
    suc = app.imaging.setPixelSize(propertyName=propertyName,
                                   element=element,
                                   value=value)
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
