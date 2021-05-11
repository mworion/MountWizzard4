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
from logic.powerswitch.pegasusUPB import PegasusUPBSignals
from base.alpacaBase import AlpacaBase, Switch


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)

    global app
    app = PegasusUPBAlpaca(app=Test(), signals=PegasusUPBSignals(), data={})

    yield


def test_getInitialConfig_1():
    with mock.patch.object(AlpacaBase,
                           'get'):
        suc = app.getInitialConfig()
        assert suc


def test_workerPollData_1():
    app.deviceConnected = False
    with mock.patch.object(AlpacaBase,
                           'get'):
        suc = app.workerPollData()
        assert not suc


def test_workerPollData_2():
    app.deviceConnected = True
    with mock.patch.object(AlpacaBase,
                           'get'):
        with mock.patch.object(Switch,
                               'maxswitch',
                               return_value=15):
            suc = app.workerPollData()
            assert suc


def test_workerPollData_3():
    app.deviceConnected = True
    with mock.patch.object(AlpacaBase,
                           'get'):
        with mock.patch.object(Switch,
                               'maxswitch',
                               return_value=21):
            suc = app.workerPollData()
            assert suc
