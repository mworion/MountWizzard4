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
# external packages
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

# local import
from logic.powerswitch import PegasusUPB


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)
    global app
    app = PegasusUPB(app=Test())

    yield

    app.threadPool.waitForDone(1000)


def test_properties():
    app.framework = 'indi'
    app.host = ('localhost', 7624)
    assert app.host == ('localhost', 7624)

    app.name = 'test'
    assert app.name == 'test'


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
    suc = app.sendAdjustableOutput()
    assert not suc
