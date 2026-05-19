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
# License APL2.0
#
###########################################################
import pytest
from mw4.base.loggerMW import setupLogging
from mw4.base.ninaClass import NINAClass
from mw4.base.signalsDevices import Signals
from PySide6.QtCore import QTimer
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock

setupLogging()


@pytest.fixture(autouse=True, scope="function")
def function():
    class Parent:
        app = App()
        data = {}
        signals = Signals()

    with mock.patch.object(QTimer, "start"):
        func = NINAClass(parent=Parent())
        yield func


def test_properties_1(function):
    function.deviceName = "test"
