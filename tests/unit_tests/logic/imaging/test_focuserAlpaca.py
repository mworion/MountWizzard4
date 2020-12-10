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
from logic.imaging.focuserAlpaca import FocuserAlpaca
from logic.imaging.focuser import FocuserSignals
from base.alpacaBase import AlpacaBase


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)

    global app
    app = FocuserAlpaca(app=Test(), signals=FocuserSignals(), data={})

    yield


def test_getInitialConfig_1():
    with mock.patch.object(AlpacaBase,
                           'get'):
        suc = app.getInitialConfig()
        assert suc


def test_workerPollData_1():
    with mock.patch.object(app.client,
                           'position',
                           return_value=1):
        suc = app.workerPollData()
        assert suc
        assert app.data['ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION'] == 1


def test_move_1():
    with mock.patch.object(AlpacaBase,
                           'put'):
        suc = app.move(position=0)
        assert suc


def test_halt_1():
    with mock.patch.object(AlpacaBase,
                           'put'):
        suc = app.halt()
        assert suc
