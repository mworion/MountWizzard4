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

# external packages
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtTest import QTest

# local import
from logic.camera.camera import Camera


@pytest.fixture(autouse=True, scope='function')
def function():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)

    app = Camera(app=Test())
    yield app
    app.threadPool.waitForDone(1000)


def test_properties(function):
    function.framework = 'indi'
    function.host = ('localhost', 7624)
    assert function.host == ('localhost', 7624)

    function.deviceName = 'test'
    assert function.deviceName == 'test'


def test_startCommunication_1(function):
    function.framework = ''
    suc = function.startCommunication()
    assert not suc


def test_startCommunication_2(function):
    function.framework = 'indi'
    suc = function.startCommunication()
    assert not suc


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
    assert not val


def test_calcSubFrame_2(function):
    function.data = {'CCD_INFO.CCD_MAX_X': 1000,
                     'CCD_FRAME.Y': 1000}
    val = function.calcSubFrame(100)
    assert not val


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


def test_resetExposed(function):
    function.exposing = True
    suc = function.resetExposed()
    assert suc
    assert not function.exposing


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
    suc = function.expose(imagePath='tests/image')
    assert not suc


def test_expose_4(function):
    function.framework = 'indi'
    with mock.patch.object(function,
                           'canSubFrame',
                           return_value=True):
        suc = function.expose(imagePath='tests/image')
        assert not suc


def test_expose_5(function):
    function.framework = 'indi'
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
                                       return_value=None):
                    suc = function.expose(imagePath='tests/image')
                    assert not suc


def test_expose_6(function):
    function.framework = 'indi'
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
                    suc = function.expose(imagePath='tests/image')
                    assert suc


def test_expose_7(function):
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
                    suc = function.expose(imagePath='tests/image')
                    assert not suc


def test_expose_8(function):
    def qWaitBreak(a):
        function.exposing = False

    QTest.qWait = qWaitBreak
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
                    suc = function.expose(imagePath='tests/image')
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
