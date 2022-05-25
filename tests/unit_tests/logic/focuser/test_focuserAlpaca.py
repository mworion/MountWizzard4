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
import unittest.mock as mock

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.focuser.focuserAlpaca import FocuserAlpaca
from base.driverDataClass import Signals


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = FocuserAlpaca(app=App(), signals=Signals(), data={})
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
