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

# local import
from logic.imaging.camera import Camera


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)
    global app
    app = Camera(app=Test())

    yield

    app.threadPool.waitForDone(1000)


def test_properties():
    app.framework = 'indi'
    app.host = ('localhost', 7624)
    assert app.host == ('localhost', 7624)

    app.deviceName = 'test'
    assert app.deviceName == 'test'


def test_startCommunication_1():
    app.framework = ''
    suc = app.startCommunication()
    assert not suc


def test_startCommunication_2():
    app.framework = 'indi'
    suc = app.startCommunication()
    assert not suc


def test_stopCommunication_1():
    app.framework = ''
    suc = app.stopCommunication()
    assert not suc


def test_stopCommunication_2():
    app.framework = 'indi'
    suc = app.stopCommunication()
    assert suc


def test_canSubframe_1():
    suc = app.canSubFrame(110)
    assert not suc


def test_canSubframe_2():
    suc = app.canSubFrame(1)
    assert not suc


def test_canSubframe_3():
    app.data = {}
    suc = app.canSubFrame(100)
    assert not suc


def test_canSubframe_4():
    app.data = {'CCD_FRAME.X': 1000,
                'CCD_FRAME.Y': 1000}
    suc = app.canSubFrame(100)
    assert suc


def test_canBinning_1():
    suc = app.canBinning(0)
    assert not suc


def test_canBinning_2():
    suc = app.canBinning(5)
    assert not suc


def test_canBinning_3():
    app.data = {}
    suc = app.canBinning(1)
    assert not suc


def test_canBinning_4():
    app.data = {'CCD_BINNING.HOR_BIN': 3}
    suc = app.canBinning(1)
    assert suc


def test_calcSubFrame_1():
    app.data = {'CCD_FRAME.X': 1000,
                'CCD_FRAME.Y': 1000}
    val = app.calcSubFrame(100)
    assert not val


def test_calcSubFrame_2():
    app.data = {'CCD_INFO.CCD_MAX_X': 1000,
                'CCD_FRAME.Y': 1000}
    val = app.calcSubFrame(100)
    assert not val


def test_calcSubFrame_3():
    app.data = {'CCD_INFO.CCD_MAX_X': 1000,
                'CCD_INFO.CCD_MAX_Y': 1000}
    val = app.calcSubFrame(100)
    assert val == (0, 0, 1000, 1000)


def test_calcSubFrame_4():
    app.data = {'CCD_INFO.CCD_MAX_X': 1000,
                'CCD_INFO.CCD_MAX_Y': 1000}
    val = app.calcSubFrame(50)
    assert val == (250, 250, 500, 500)


def test_calcSubFrame_5():
    app.data = {'CCD_INFO.CCD_MAX_X': 1000,
                'CCD_INFO.CCD_MAX_Y': 1000}
    val = app.calcSubFrame(5)
    assert val == (0, 0, 1000, 1000)


def test_sendDownloadMode_1():
    app.framework = ''
    suc = app.sendDownloadMode()
    assert not suc


def test_sendDownloadMode_2():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'sendDownloadMode',
                           return_value=True):
        suc = app.sendDownloadMode()
        assert suc


def test_resetExposed():
    app.exposing = True
    suc = app.resetExposed()
    assert suc
    assert not app.exposing


def test_expose_1():
    app.framework = ''
    suc = app.expose()
    assert not suc


def test_expose_2():
    app.framework = 'indi'
    suc = app.expose()
    assert not suc


def test_expose_3():
    app.framework = 'indi'
    suc = app.expose(imagePath='tests/image')
    assert not suc


def test_expose_4():
    app.framework = 'indi'
    with mock.patch.object(app,
                           'canSubFrame',
                           return_value=True):
        suc = app.expose(imagePath='tests/image')
        assert not suc


def test_expose_5():
    app.framework = 'indi'
    with mock.patch.object(app,
                           'canSubFrame',
                           return_value=True):
        with mock.patch.object(app,
                               'canBinning',
                               return_value=True):
            with mock.patch.object(app.run['indi'],
                                   'expose',
                                   return_value=True):
                suc = app.expose(imagePath='tests/image')
                assert not suc


def test_expose_6():
    app.framework = 'indi'
    app.data = {'CCD_INFO.CCD_MAX_X': 1000,
                'CCD_INFO.CCD_MAX_Y': 1000}
    with mock.patch.object(app,
                           'canSubFrame',
                           return_value=True):
        with mock.patch.object(app,
                               'canBinning',
                               return_value=True):
            with mock.patch.object(app.run['indi'],
                                   'expose',
                                   return_value=False):
                suc = app.expose(imagePath='tests/image')
                assert not suc


def test_expose_7():
    app.framework = 'indi'
    app.data = {'CCD_INFO.CCD_MAX_X': 1000,
                'CCD_INFO.CCD_MAX_Y': 1000}
    with mock.patch.object(app,
                           'canSubFrame',
                           return_value=True):
        with mock.patch.object(app,
                               'canBinning',
                               return_value=True):
            with mock.patch.object(app.run['indi'],
                                   'expose',
                                   return_value=True):
                suc = app.expose(imagePath='tests/image')
                assert suc


def test_abort_1():
    suc = app.abort()
    assert not suc


def test_abort_2():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'abort',
                           return_value=True):
        suc = app.abort()
        assert suc


def test_sendCoolerSwitch_1():
    suc = app.sendCoolerSwitch()
    assert not suc


def test_sendCoolerSwitch_2():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'sendCoolerSwitch',
                           return_value=True):
        suc = app.sendCoolerSwitch()
        assert suc


def test_sendCoolerTemp_1():
    suc = app.sendCoolerTemp()
    assert not suc


def test_sendCoolerTemp_2():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'sendCoolerTemp',
                           return_value=True):
        suc = app.sendCoolerTemp()
        assert suc
