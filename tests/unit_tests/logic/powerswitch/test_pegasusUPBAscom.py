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


def test_togglePowerPort_1():
    app.deviceConnected = False
    suc = app.togglePowerPort()
    assert not suc


def test_togglePowerPort_2():
    app.deviceConnected = True
    suc = app.togglePowerPort()
    assert suc


def test_togglePowerPort_3():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'callAscomMethod'):
        suc = app.togglePowerPort('1')
        assert suc


def test_togglePowerPortBoot_1():
    app.deviceConnected = False
    suc = app.togglePowerPortBoot()
    assert not suc


def test_togglePowerPortBoot_2():
    app.deviceConnected = True
    suc = app.togglePowerPortBoot()
    assert suc


def test_toggleHubUSB_1():
    app.deviceConnected = False
    suc = app.toggleHubUSB()
    assert not suc


def test_toggleHubUSB_2():
    app.deviceConnected = True
    suc = app.toggleHubUSB()
    assert suc


def test_togglePortUSB_1():
    app.deviceConnected = False
    suc = app.togglePortUSB()
    assert not suc


def test_togglePortUSB_2():
    app.deviceConnected = True
    suc = app.togglePortUSB()
    assert suc


def test_togglePortUSB_3():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAscomProperty',
                           return_value=21):
        with mock.patch.object(app,
                               'callAscomMethod'):
            suc = app.togglePortUSB('1')
            assert suc


def test_toggleAutoDew_1():
    app.deviceConnected = False
    suc = app.toggleAutoDew()
    assert not suc


def test_toggleAutoDew_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAscomProperty',
                           return_value=21):
        with mock.patch.object(app,
                               'callAscomMethod'):
            suc = app.toggleAutoDew()
            assert suc


def test_toggleAutoDew_3():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAscomProperty',
                           return_value=15):
        with mock.patch.object(app,
                               'callAscomMethod'):
            suc = app.toggleAutoDew()
            assert suc


def test_sendDew_1():
    app.deviceConnected = False
    suc = app.sendDew()
    assert not suc


def test_sendDew_2():
    app.deviceConnected = True
    suc = app.sendDew()
    assert suc


def test_sendDew_3():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAscomProperty',
                           return_value=21):
        with mock.patch.object(app,
                               'callAscomMethod'):
            suc = app.sendDew('1')
            assert suc


def test_sendAdjustableOutput_1():
    app.deviceConnected = False
    suc = app.sendAdjustableOutput()
    assert not suc


def test_sendAdjustableOutput_2():
    app.deviceConnected = True
    suc = app.sendAdjustableOutput(4)
    assert suc


def test_reboot_1():
    app.deviceConnected = False
    suc = app.reboot()
    assert not suc


def test_reboot_2():
    app.deviceConnected = True
    suc = app.reboot()
    assert suc
