############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# Licence APL2.0
#
###########################################################

import PySide6
import pytest
import unittest.mock as mock
from mw4.base.signalsDevices import Signals
from mw4.logic.telescope.telescopeAlpaca import TelescopeAlpaca
from tests.unit_tests.unitTestAddOns.baseTestApp import App


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
