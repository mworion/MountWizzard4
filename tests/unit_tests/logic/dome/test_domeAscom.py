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
# written in python3 , (c) 2019, 2020 by mworion
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
from logic.dome.dome import DomeSignals

if not platform.system() == 'Windows':
    pytest.skip("skipping windows-only tests", allow_module_level=True)


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test1:
        Azimuth = 100
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'
        shutterstatus = '4'

        @staticmethod
        def SlewToAzimuth(azimuth):
            return True

    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)

    global app
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        app = DomeAscom(app=Test(), signals=DomeSignals(), data={})
        app.client = Test1()
        yield


def test_processPolledData_1():
    suc = app.processPolledData()
    assert suc


def test_workerPollData_1():
    app.deviceConnected = False
    suc = app.workerPollData()
    assert not suc


def test_workerPollData_2():
    app.deviceConnected = True
    suc = app.workerPollData()
    assert suc


def test_workerPollData_3():
    class Test:
        shutterstatus = 0
        Slewing = False
        Azimuth = 0

    app.deviceConnected = True
    app.client = Test()
    suc = app.workerPollData()
    assert suc


def test_workerPollData_4():
    class Test:
        shutterstatus = 1
        Slewing = False
        Azimuth = 0

    app.deviceConnected = True
    app.client = Test()
    suc = app.workerPollData()
    assert suc


def test_workerPollData_5():
    class Test:
        shutterstatus = mock.PropertyMock(side_effect=Exception)
        Slewing = False
        Azimuth = 0

    app.deviceConnected = True
    app.client = Test()
    suc = app.workerPollData()
    assert suc


def test_slewToAltAz_1():
    app.deviceConnected = False
    suc = app.slewToAltAz()
    assert not suc


def test_slewToAltAz_2():
    app.deviceConnected = True
    suc = app.slewToAltAz()
    assert suc
