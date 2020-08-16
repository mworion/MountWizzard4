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

# external packages
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal

# local import
from logic.imaging.focuserAscom import FocuserAscom
from logic.imaging.focuser import FocuserSignals
from base.ascomClass import AscomClass


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test1:
        Position = 1
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'

    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)

    global app
    app = FocuserAscom(app=Test(), signals=FocuserSignals(), data={})
    app.client = Test1()

    yield


def test_getInitialConfig_1():
    app.deviceConnected = True
    suc = app.getInitialConfig()
    assert suc


def test_getInitialConfig_2():
    app.deviceConnected = False
    with mock.patch.object(AscomClass,
                           'getInitialConfig',
                           return_value=True):
        suc = app.getInitialConfig()
        assert not suc


def test_workerPollData_1():
    app.deviceConnected = True
    suc = app.workerPollData()
    assert suc
    assert app.data['ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION'] == 1


def test_workerPollData_2():
    app.deviceConnected = False
    suc = app.workerPollData()
    assert not suc
