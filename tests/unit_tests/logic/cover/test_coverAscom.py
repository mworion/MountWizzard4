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
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock
import platform

# external packages
import PyQt5
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal

# local import
from logic.cover.coverAscom import CoverAscom
from base.driverDataClass import Signals

if not platform.system() == 'Windows':
    pytest.skip("skipping windows-only tests", allow_module_level=True)


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test1:
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'
        CoverState = 1

        @staticmethod
        def CloseCover():
            return True

        @staticmethod
        def OpenCover():
            return True

        @staticmethod
        def HaltCover():
            return True

        @staticmethod
        def CalibratorOn():
            return True

        @staticmethod
        def CalibratorOff():
            return True

        @staticmethod
        def Brightness(a):
            return True

    class Test(QObject):
        threadPool = QThreadPool()
                mes = pyqtSignal(object, object, object, object)

    global app
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        app = CoverAscom(app=Test(), signals=Signals(), data={})
        app.client = Test1()
        app.clientProps = []
        yield


def test_workerPollData_1():
    with mock.patch.object(app,
                           'getAscomProperty',
                           return_value=1):
        with mock.patch.object(app,
                               'storePropertyToData'):
            suc = app.workerPollData()
            assert suc


def test_closeCover_1():
    app.deviceConnected = False
    suc = app.closeCover()
    assert not suc


def test_closeCover_2():
    app.deviceConnected = True
    suc = app.closeCover()
    assert suc


def test_closeCover_3():
    app.deviceConnected = True
    suc = app.closeCover()
    assert suc


def test_openCover_1():
    app.deviceConnected = False
    suc = app.openCover()
    assert not suc


def test_openCover_2():
    app.deviceConnected = True
    suc = app.openCover()
    assert suc


def test_openCover_3():
    app.deviceConnected = True
    suc = app.openCover()
    assert suc


def test_haltCover_1():
    app.deviceConnected = False
    suc = app.haltCover()
    assert not suc


def test_haltCover_2():
    app.deviceConnected = True
    suc = app.haltCover()
    assert suc


def test_haltCover_3():
    app.deviceConnected = True
    suc = app.haltCover()
    assert suc


def test_lightOn_1():
    app.deviceConnected = False
    suc = app.lightOn()
    assert not suc


def test_lightOn_2():
    app.deviceConnected = True
    suc = app.lightOn()
    assert suc


def test_lightOn_3():
    app.deviceConnected = True
    suc = app.lightOn()
    assert suc


def test_lightOff_1():
    app.deviceConnected = False
    suc = app.lightOff()
    assert not suc


def test_lightOff_2():
    app.deviceConnected = True
    suc = app.lightOff()
    assert suc


def test_lightOff_3():
    app.deviceConnected = True
    suc = app.lightOff()
    assert suc


def test_lightIntensity_1():
    app.deviceConnected = False
    suc = app.lightIntensity(0)
    assert not suc


def test_lightIntensity_2():
    app.deviceConnected = True
    suc = app.lightIntensity(0)
    assert suc


def test_lightIntensity_3():
    app.deviceConnected = True
    suc = app.lightIntensity(0)
    assert suc
