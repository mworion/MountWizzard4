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
import unittest.mock as mock
from mw4.base.signalsDevices import Signals
from mw4.logic.telescope.telescopeAlpaca import TelescopeAlpaca
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Parent:
    app = App()
    data = {}
    DEVICE_TYPE = "telescope"
    deviceType = ""
    signals = Signals()
    loadConfig = True


@pytest.fixture(autouse=True, scope="module")
def function():
    func = TelescopeAlpaca(parent=Parent())
    func.device = mock.MagicMock()
    yield func


def test_getInitialConfig_1(function):
    with mock.patch.object(function, "getAndStoreDeviceProp") as m:
        with mock.patch.object(function, "getDeviceProp"):
            function.getInitialConfig()
            attrs = [c.args[0] for c in m.call_args_list]
            assert "ApertureDiameter" in attrs
            assert "FocalLength" in attrs


def test_startCommunication_1(function):
    with mock.patch.object(function, "createAlpacaDevice", return_value=False):
        with mock.patch.object(function.threadPool, "start") as m_start:
            function.startCommunication()
            m_start.assert_not_called()


def test_startCommunication_2(function):
    with mock.patch.object(function, "createAlpacaDevice", return_value=True):
        with mock.patch.object(function.threadPool, "start") as m_start:
            function.startCommunication()
            m_start.assert_called_once()

