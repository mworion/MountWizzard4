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
import PyQt5
from PyQt5.QtCore import QThreadPool

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.telescope.telescopeAlpaca import TelescopeAlpaca
from base.driverDataClass import Signals


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        app = TelescopeAlpaca(app=App(), signals=Signals(), data={})
        yield


def test_workerGetInitialConfig_1():
    with mock.patch.object(app,
                           'getAndStoreAlpacaProperty'):
        suc = app.workerGetInitialConfig()
        assert suc


def test_workerGetInitialConfig_2():
    with mock.patch.object(app,
                           'getAndStoreAlpacaProperty',
                           return_value=100):
        suc = app.workerGetInitialConfig()
        assert suc
