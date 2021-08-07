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
import platform
import unittest.mock as mock

# external packages
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal

# local import
from logic.powerswitch.pegasusUPBAscom import PegasusUPBAscom
from logic.powerswitch.pegasusUPB import PegasusUPBSignals

if not platform.system() == 'Windows':
    pytest.skip("skipping windows-only tests", allow_module_level=True)


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test1:
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'

        @staticmethod
        def getswitch(a):
            return False

        @staticmethod
        def getswitchvalue(a):
            return 0

    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)

    global app

    app = PegasusUPBAscom(app=Test(), signals=PegasusUPBSignals(), data={})
    app.clientProps = []
    app.client = Test1()
    yield


def test_getInitialConfig_1():
    suc = app.getInitialConfig()
    assert suc


def test_workerPollData_1():
    app.deviceConnected = False
    with mock.patch.object(app,
                           'getAscomProperty',
                           return_value=15):
        suc = app.workerPollData()
        assert not suc


def test_workerPollData_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAscomProperty',
                           return_value=15):
        suc = app.workerPollData()
        assert suc


def test_workerPollData_3():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAscomProperty',
                           return_value=21):
        suc = app.workerPollData()
        assert suc
