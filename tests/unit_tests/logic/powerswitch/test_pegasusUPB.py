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
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
from unittest import mock

# external packages
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

# local import
from logic.powerswitch.pegasusUPB import PegasusUPB


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
                mes = pyqtSignal(object, object, object, object)

    global app
    app = PegasusUPB(app=Test())

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
    with mock.patch.object(app.run['indi'],
                           'startCommunication',
                           return_value=True):
        suc = app.startCommunication()
        assert suc


def test_stopCommunication_1():
    app.framework = ''
    suc = app.stopCommunication()
    assert not suc


def test_stopCommunication_2():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'stopCommunication',
                           return_value=True):
        suc = app.stopCommunication()
        assert suc


def test_togglePowerPort_1():
    app.framework = ''
    suc = app.togglePowerPort()
    assert not suc


def test_togglePowerPort_2():
    app.framework = 'indi'
    suc = app.togglePowerPort()
    assert not suc


def test_togglePowerPortBoot_1():
    app.framework = ''
    suc = app.togglePowerPortBoot()
    assert not suc


def test_togglePowerPortBoot_2():
    app.framework = 'indi'
    suc = app.togglePowerPortBoot()
    assert not suc


def test_toggleHubUSB_1():
    app.framework = ''
    suc = app.toggleHubUSB()
    assert not suc


def test_toggleHubUSB_2():
    app.framework = 'indi'
    suc = app.toggleHubUSB()
    assert not suc


def test_togglePortUSB_1():
    app.framework = ''
    suc = app.togglePortUSB()
    assert not suc


def test_togglePortUSB_2():
    app.framework = 'indi'
    suc = app.togglePortUSB()
    assert not suc


def test_toggleAutoDew_1():
    app.framework = ''
    suc = app.toggleAutoDew()
    assert not suc


def test_toggleAutoDew_2():
    app.framework = 'indi'
    suc = app.toggleAutoDew()
    assert not suc


def test_sendDew_1():
    app.framework = ''
    suc = app.sendDew()
    assert not suc


def test_sendDew_2():
    app.framework = 'indi'
    suc = app.sendDew()
    assert not suc


def test_sendAdjustableOutput_1():
    app.framework = ''
    suc = app.sendAdjustableOutput()
    assert not suc


def test_sendAdjustableOutput_2():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'sendAdjustableOutput',
                           return_value=False):
        suc = app.sendAdjustableOutput()
        assert not suc


def test_sendAdjustableOutput_3():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'sendAdjustableOutput',
                           return_value=True):
        suc = app.sendAdjustableOutput()
        assert suc


def test_reboot_1():
    app.framework = ''
    suc = app.reboot()
    assert not suc


def test_reboot_2():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'reboot',
                           return_value=False):
        suc = app.reboot()
        assert not suc


def test_reboot_3():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'reboot',
                           return_value=True):
        suc = app.reboot()
        assert suc
