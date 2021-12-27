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
import platform

# external packages
import PyQt5
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal

# local import
from logic.dome.domeAscom import DomeAscom
from base.driverDataClass import Signals

if not platform.system() == 'Windows':
    pytest.skip("skipping windows-only tests", allow_module_level=True)


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test1:
        Azimuth = 100
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'
        ShutterStatus = 4
        Slewing = True
        CanSetAltitude = True
        CanSetAzimuth = True
        CanSetShutter = True
        AbortSlew = False
        OpenShutter = None
        CloseShutter = None
        AbortSlew = None

        @staticmethod
        def SlewToAzimuth(azimuth):
            return True

        @staticmethod
        def SlewToAltitude(altitude):
            return True

    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)

    global app
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        app = DomeAscom(app=Test(), signals=Signals(), data={})
        app.client = Test1()
        app.clientProps = []
        yield


def test_workerGetInitialConfig_1():
    with mock.patch.object(AscomClass,
                           'getAndStoreAscomProperty',
                           return_value=True):
        with mock.patch.object(app,
                               'getAndStoreAscomProperty'):
            suc = app.workerGetInitialConfig()
            assert suc


def test_processPolledData_1():
    suc = app.processPolledData()
    assert suc


def test_workerPollData_1():
    with mock.patch.object(app,
                           'getAscomProperty',
                           return_value=0):
        with mock.patch.object(app,
                               'storePropertyToData'):
            with mock.patch.object(app,
                                   'getAndStoreAscomProperty'):
                suc = app.workerPollData()
                assert suc


def test_workerPollData_2():
    with mock.patch.object(app,
                           'getAscomProperty',
                           return_value=1):
        with mock.patch.object(app,
                               'storePropertyToData'):
            with mock.patch.object(app,
                                   'getAndStoreAscomProperty'):
                suc = app.workerPollData()
                assert suc


def test_workerPollData_3():
    with mock.patch.object(app,
                           'getAscomProperty',
                           return_value=2):
        with mock.patch.object(app,
                               'storePropertyToData'):
            with mock.patch.object(app,
                                   'getAndStoreAscomProperty'):
                suc = app.workerPollData()
                assert suc


def test_slewToAltAz_1():
    app.deviceConnected = False
    with mock.patch.object(app,
                           'callMethodThreaded'):
        suc = app.slewToAltAz()
        assert not suc


def test_slewToAltAz_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'callMethodThreaded'):
        suc = app.slewToAltAz()
        assert suc


def test_openShutter_1():
    app.deviceConnected = False
    with mock.patch.object(app,
                           'callMethodThreaded'):
        suc = app.openShutter()
        assert not suc


def test_openShutter_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'callMethodThreaded'):
        suc = app.openShutter()
        assert suc


def test_closeShutter_1():
    app.deviceConnected = False
    with mock.patch.object(app,
                           'callMethodThreaded'):
        suc = app.closeShutter()
        assert not suc


def test_closeShutter_2():
    app.data['CanSetShutter'] = True
    app.deviceConnected = True
    with mock.patch.object(app,
                           'callMethodThreaded'):
        suc = app.closeShutter()
        assert suc


def test_abortSlew_1():
    app.deviceConnected = False
    with mock.patch.object(app,
                           'callMethodThreaded'):
        suc = app.abortSlew()
        assert not suc


def test_abortSlew_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'callMethodThreaded'):
        suc = app.abortSlew()
        assert suc
