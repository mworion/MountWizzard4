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

# external packages
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal

# local import
from logic.focuser.focuserAlpaca import FocuserAlpaca
from logic.focuser.focuser import FocuserSignals


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)

    global app
    app = FocuserAlpaca(app=Test(), signals=FocuserSignals(), data={})

    yield


def test_workerPollData_1():
    app.deviceConnected = False
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value=1):
        suc = app.workerPollData()
        assert not suc


def test_workerPollData_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAlpacaProperty',
                           return_value=1):
        suc = app.workerPollData()
        assert suc
        assert app.data['ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION'] == 1


def test_move_1():
    app.deviceConnected = False
    with mock.patch.object(app,
                           'setAlpacaProperty'):
        suc = app.move(position=0)
        assert not suc


def test_move_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'setAlpacaProperty'):
        suc = app.move(position=0)
        assert suc


def test_halt_1():
    app.deviceConnected = False
    with mock.patch.object(app,
                           'getAlpacaProperty'):
        suc = app.halt()
        assert not suc


def test_halt_2():
    app.deviceConnected = True
    with mock.patch.object(app,
                           'getAlpacaProperty'):
        suc = app.halt()
        assert suc
