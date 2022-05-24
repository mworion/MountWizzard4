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

# external packages
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal

# local import
from logic.powerswitch.pegasusUPBAlpaca import PegasusUPBAlpaca
from base.driverDataClass import Signals


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        mes = pyqtSignal(object, object, object, object)

    global app
    app = PegasusUPBAlpaca(app=Test(), signals=Signals(), data={})

    yield


def test_workerPollData_1():
    app.deviceConnected = False
    with mock.patch.object(app,
                           'getAlpacaProperty'):
        suc = app.workerPollData()
        assert not suc


def test_workerPollData_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value=15):
        with mock.patch.object(app,
                               'storePropertyToData'):
            suc = app.workerPollData()
            assert suc


def test_workerPollData_3():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value=21):
        with mock.patch.object(app,
                               'storePropertyToData'):
            suc = app.workerPollData()
            assert suc


def test_togglePowerPort_1():
    app.deviceConnected = False
    suc = app.togglePowerPort()
    assert not suc


def test_togglePowerPort_2():
    app.deviceConnected = True
    suc = app.togglePowerPort()
    assert not suc


def test_togglePowerPort_3():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'setAlpacaProperty'):
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
    assert not suc


def test_togglePortUSB_3():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value=21):
        with mock.patch.object(app,
                               'setAlpacaProperty'):
            suc = app.togglePortUSB('1')
            assert suc


def test_toggleAutoDew_1():
    app.deviceConnected = False
    suc = app.toggleAutoDew()
    assert not suc


def test_toggleAutoDew_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value=21):
        with mock.patch.object(app,
                               'setAlpacaProperty'):
            suc = app.toggleAutoDew()
            assert suc


def test_toggleAutoDew_3():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value=15):
        with mock.patch.object(app,
                               'setAlpacaProperty'):
            suc = app.toggleAutoDew()
            assert suc


def test_sendDew_1():
    app.deviceConnected = False
    suc = app.sendDew()
    assert not suc


def test_sendDew_2():
    app.deviceConnected = True
    suc = app.sendDew()
    assert not suc


def test_sendDew_3():
    app.deviceConnected = True
    suc = app.sendDew('1')
    assert not suc


def test_sendDew_4():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value=21):
        with mock.patch.object(app,
                               'setAlpacaProperty'):
            suc = app.sendDew('1', 10)
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