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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

# external packages
import PySide6

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.telescope.telescopeAlpaca import TelescopeAlpaca
from base.signalsDevices import Signals


class Parent:
    app = App()
    data = {}
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="function")
def function():
    with mock.patch.object(PySide6.QtCore.QTimer, "start"):
        func = TelescopeAlpaca(parent=Parent())
        yield func


def test_workerGetInitialConfig_1(function):
    with mock.patch.object(function, "getAndStoreAlpacaProperty"):
        function.workerGetInitialConfig()


def test_workerGetInitialConfig_2(function):
    with mock.patch.object(function, "getAndStoreAlpacaProperty", return_value=100):
        function.workerGetInitialConfig()
