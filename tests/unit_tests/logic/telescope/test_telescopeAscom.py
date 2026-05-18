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

import platform
import pytest
import unittest.mock as mock
from mw4.base.loggerMW import setupLogging
from mw4.base.signalsDevices import Signals
from mw4.logic.telescope.telescopeAscom import TelescopeAscom
from tests.unit_tests.unitTestAddOns.baseTestApp import App

setupLogging()

if platform.system() != "Windows":
    pytest.skip("skipping windows-only tests", allow_module_level=True)


class Parent:
    app = App()
    data = {}
    signals = Signals()
    deviceType = ""
    loadConfig = True


@pytest.fixture(autouse=True, scope="module")
def function():
    func = TelescopeAscom(parent=Parent())
    func.client = mock.MagicMock()
    func.client.ApertureDiameter = 0.1
    func.client.FocalLength = 0.57
    yield func


def test_getInitialConfig_floatValues(function):
    with mock.patch.object(function, "getAndStoreAscomProperty"):
        with mock.patch.object(function, "getAscomProperty", return_value=0.57):
            function.getInitialConfig()
    assert function.data["TELESCOPE_INFO.TELESCOPE_APERTURE"] == 570.0
    assert function.data["TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH"] == 570.0


def test_getInitialConfig_nonFloatValues(function):
    with mock.patch.object(function, "getAndStoreAscomProperty"):
        with mock.patch.object(function, "getAscomProperty", return_value=None):
            function.getInitialConfig()
