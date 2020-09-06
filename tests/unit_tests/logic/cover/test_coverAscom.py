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
from logic.cover.coverAscom import CoverAscom
from logic.cover.cover import CoverSignals

if not platform.system() == 'Windows':
    pytest.skip("skipping windows-only tests", allow_module_level=True)


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test1:
        Name = 'test'

        @staticmethod
        def sendCoverPark():
            return True

    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)

    global app
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        app = CoverAscom(app=Test(), signals=CoverSignals(), data={})
        app.client = Test1()
        yield


def test_getInitialConfig_1():
    suc = app.getInitialConfig()
    assert suc


def test_workerPollData_1():
    app.deviceConnected = False
    suc = app.workerPollData()
    assert not suc


def test_workerPollData_2():
    app.deviceConnected = True
    suc = app.workerPollData()
    assert suc


def test_sendCoverPark_1():
    app.deviceConnected = False
    suc = app.sendCoverPark(park=True)
    assert not suc


def test_sendCoverPark_2():
    app.deviceConnected = True
    suc = app.sendCoverPark(park=True)
    assert suc


def test_sendCoverPark_3():
    app.deviceConnected = True
    suc = app.sendCoverPark(park=False)
    assert suc
