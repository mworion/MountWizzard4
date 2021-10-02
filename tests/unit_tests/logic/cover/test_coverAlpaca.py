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
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

# external packages
import PyQt5
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal

# local import
from logic.cover.coverAlpaca import CoverAlpaca
from base.driverDataClass import Signals


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)

    global app
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        app = CoverAlpaca(app=Test(), signals=Signals(), data={})

        yield


def test_workerPollData_1():
    app.deviceConnected = False
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value=1):
        suc = app.workerPollData()
        assert not suc


def test_workerPollData_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value=1):
        with mock.patch.object(app,
                               'storePropertyToData'):
            suc = app.workerPollData()
            assert suc


def test_closeCover_1():
    with mock.patch.object(app,
                           'getAlpacaProperty'):
        suc = app.closeCover()
        assert not suc


def test_closeCover_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAlpacaProperty'):
        suc = app.closeCover()
        assert suc


def test_openCover_1():
    with mock.patch.object(app,
                           'getAlpacaProperty'):
        suc = app.openCover()
        assert not suc


def test_openCover_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAlpacaProperty'):
        suc = app.openCover()
        assert suc


def test_haltCover_1():
    with mock.patch.object(app,
                           'getAlpacaProperty'):
        suc = app.haltCover()
        assert not suc


def test_haltCover_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAlpacaProperty'):
        suc = app.haltCover()
        assert suc


def test_lightOn_1():
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value=0):
        with mock.patch.object(app,
                               'setAlpacaProperty'):
            suc = app.lightOn()
            assert not suc


def test_lightOn_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value=0):
        with mock.patch.object(app,
                               'setAlpacaProperty'):
            suc = app.lightOn()
            assert suc


def test_lightOff_1():
    with mock.patch.object(app,
                           'getAlpacaProperty'):
        suc = app.lightOff()
        assert not suc


def test_lightOff_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAlpacaProperty'):
        suc = app.lightOff()
        assert suc


def test_lightIntensity_1():
    with mock.patch.object(app,
                           'setAlpacaProperty'):
        suc = app.lightIntensity(0)
        assert not suc


def test_lightIntensity_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'setAlpacaProperty'):
        suc = app.lightIntensity(0)
        assert suc

