############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import platform
import unittest.mock as mock

# external packages
import PySide6
import pytest
from base.ascomClass import AscomClass
from base.loggerMW import setupLogging
from base.signalsDevices import Signals
from logic.telescope.telescopeAscom import TelescopeAscom

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App

setupLogging()

if not platform.system() == "Windows":
    pytest.skip("skipping windows-only tests", allow_module_level=True)


class Parent:
    app = App()
    data = {}
    signals = Signals()
    deviceType = ""
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="function")
def function():
    class Test1:
        ApertureDiameter = 100
        FocalLength = 570
        connected = True
        Name = "test"
        DriverVersion = "1"
        DriverInfo = "test1"

    with mock.patch.object(PySide6.QtCore.QTimer, "start"):
        func = TelescopeAscom(parent=Parent())
        func.client = Test1()
        func.clientProps = []
        yield func


def test_workerGetInitialConfig_1(function):
    with mock.patch.object(AscomClass, "workerGetInitialConfig", return_value=True):
        function.workerGetInitialConfig()


def test_workerGetInitialConfig_2(function):
    with mock.patch.object(function, "getAscomProperty", return_value=0.57):
        function.workerGetInitialConfig()
        assert function.data["TELESCOPE_INFO.TELESCOPE_APERTURE"] == 570.0
        assert function.data["TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH"] == 570.0
