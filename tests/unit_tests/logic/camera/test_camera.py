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

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.camera.camera import Camera


@pytest.fixture(autouse=True, scope='function')
def function():
    func = Camera(app=App())
    yield func


def test_properties(function):
    function.framework = 'indi'
    function.host = ('localhost', 7624)
    assert function.host == ('localhost', 7624)

    function.deviceName = 'test'
    assert function.deviceName == 'test'


def test_properties_2(function):
    function.updateRate = 1000
    function.loadConfig = True
    function.framework = 'indi'
    assert function.updateRate == 1000
    assert function.loadConfig


def test_startCommunication_1(function):
    function.framework = ''
    suc = function.startCommunication()
    assert not suc


def test_startCommunication_2(function):
    function.framework = 'indi'
    suc = function.startCommunication()
    assert suc


def test_stopCommunication_1(function):
    function.framework = ''
    suc = function.stopCommunication()
    assert not suc


def test_stopCommunication_2(function):
    function.framework = 'indi'
    suc = function.stopCommunication()
    assert suc


def test_canSubframe_1(function):
    suc = function.canSubFrame(110)
    assert not suc


def test_canSubframe_2(function):
    suc = function.canSubFrame(1)
    assert not suc


def test_canSubframe_3(function):
    function.data = {}
    suc = function.canSubFrame(100)
    assert not suc


def test_canSubframe_4(function):
    function.data = {'CCD_FRAME.X': 1000,
                'CCD_FRAME.Y': 1000}
    suc = function.canSubFrame(100)
    assert suc


def test_canBinning_1(function):
    suc = function.canBinning(0)
    assert not suc


def test_canBinning_2(function):
    suc = function.canBinning(5)
    assert not suc


def test_canBinning_3(function):
    function.data = {}
    suc = function.canBinning(1)
    assert not suc


def test_canBinning_4(function):
    function.data = {'CCD_BINNING.HOR_BIN': 3}
    suc = function.canBinning(1)
    assert suc


def test_calcSubFrame_1(function):
    function.data = {'CCD_FRAME.X': 1000,
                     'CCD_FRAME.Y': 1000}
    val = function.calcSubFrame(100)
    assert val == (0, 0, 0, 0)


def test_calcSubFrame_2(function):
    function.data = {'CCD_INFO.CCD_MAX_X': 100,
                     'CCD_FRAME.Y': 1000}
    val = function.calcSubFrame(100)
    assert val == (0, 0, 100, 0)


def test_calcSubFrame_3(function):
    function.data = {'CCD_INFO.CCD_MAX_X': 1000,
                     'CCD_INFO.CCD_MAX_Y': 1000}
    val = function.calcSubFrame(100)
    assert val == (0, 0, 1000, 1000)


def test_calcSubFrame_4(function):
    function.data = {'CCD_INFO.CCD_MAX_X': 1000,
                     'CCD_INFO.CCD_MAX_Y': 1000}
    val = function.calcSubFrame(50)
    assert val == (250, 250, 500, 500)


def test_calcSubFrame_5(function):
    function.data = {'CCD_INFO.CCD_MAX_X': 1000,
                     'CCD_INFO.CCD_MAX_Y': 1000}
    val = function.calcSubFrame(5)
    assert val == (0, 0, 1000, 1000)


def test_sendDownloadMode_1(function):
    function.framework = ''
    suc = function.sendDownloadMode()
    assert not suc


def test_sendDownloadMode_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'sendDownloadMode',
                           return_value=True):
        suc = function.sendDownloadMode()
        assert suc


def test_expose_1(function):
    function.framework = ''
    suc = function.expose()
    assert not suc


def test_expose_2(function):
    function.framework = 'indi'
    suc = function.expose()
    assert not suc


def test_expose_3(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'expose',
                           return_value=True):
        suc = function.expose(imagePath='tests/workDir/image', subFrame=90)
        assert suc


def test_expose_4(function):
    function.framework = 'indi'
    with mock.patch.object(function,
                           'canSubFrame',
                           return_value=True):
        with mock.patch.object(function.run['indi'],
                               'expose',
                               return_value=True):
            suc = function.expose(imagePath='tests/workDir/image', binning=2)
            assert suc


def test_expose_5(function):
    function.framework = 'indi'
    function.app.mount.obsSite.raJNow = None
    with mock.patch.object(function,
                           'canSubFrame',
                           return_value=True):
        with mock.patch.object(function,
                               'canBinning',
                               return_value=True):
            with mock.patch.object(function.run['indi'],
                                   'expose',
                                   return_value=True):
                with mock.patch.object(function,
                                       'calcSubFrame',
                                       return_value=(0, 0, 10, 10)):
                    suc = function.expose(imagePath='tests/workDir/image')
                    assert suc


def test_expose_6(function):
    function.framework = 'indi'
    function.data = {'CCD_INFO.CCD_MAX_X': 1000,
                     'CCD_INFO.CCD_MAX_Y': 1000}
    with mock.patch.object(function,
                           'canSubFrame',
                           return_value=True):
        with mock.patch.object(function,
                               'canBinning',
                               return_value=True):
            with mock.patch.object(function.run['indi'],
                                   'expose',
                                   return_value=False):
                with mock.patch.object(function,
                                       'calcSubFrame',
                                       return_value=(0, 0, 10, 10)):
                    suc = function.expose(imagePath='tests/workDir/image')
                    assert not suc


def test_expose_7(function):
    def qWaitBreak(a):
        function.exposing = False

    sleepAndEvents = qWaitBreak
    function.exposing = True
    function.framework = 'indi'
    function.data = {'CCD_INFO.CCD_MAX_X': 1000,
                     'CCD_INFO.CCD_MAX_Y': 1000}
    with mock.patch.object(function,
                           'canSubFrame',
                           return_value=True):
        with mock.patch.object(function,
                               'canBinning',
                               return_value=True):
            with mock.patch.object(function.run['indi'],
                                   'expose',
                                   return_value=True):
                with mock.patch.object(function,
                                       'calcSubFrame',
                                       return_value=(0, 0, 10, 10)):
                    suc = function.expose(imagePath='tests/workDir/image')
                    assert suc


def test_abort_1(function):
    suc = function.abort()
    assert not suc


def test_abort_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'abort',
                           return_value=True):
        suc = function.abort()
        assert suc


def test_sendCoolerSwitch_1(function):
    suc = function.sendCoolerSwitch()
    assert not suc


def test_sendCoolerSwitch_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'sendCoolerSwitch',
                           return_value=True):
        suc = function.sendCoolerSwitch()
        assert suc


def test_sendCoolerTemp_1(function):
    suc = function.sendCoolerTemp()
    assert not suc


def test_sendCoolerTemp_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'sendCoolerTemp',
                           return_value=True):
        suc = function.sendCoolerTemp()
        assert suc


def test_sendOffset_1(function):
    suc = function.sendOffset()
    assert not suc


def test_sendOffset_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'sendOffset',
                           return_value=True):
        suc = function.sendOffset()
        assert suc


def test_sendGain_1(function):
    suc = function.sendGain()
    assert not suc


def test_sendGain_2(function):
    function.framework = 'indi'
    with mock.patch.object(function.run['indi'],
                           'sendGain',
                           return_value=True):
        suc = function.sendGain()
        assert suc
