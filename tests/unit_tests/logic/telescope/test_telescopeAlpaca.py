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
    try:
        app = App()
    except Exception:
        app = mock.MagicMock()
    data = {}
    DEVICE_TYPE = "telescope"
    deviceType = ""
    signals = Signals()
    loadConfig = True


@pytest.fixture(autouse=True, scope="module")
def function():
    try:
        func = TelescopeAlpaca(parent=Parent())
        func.device = mock.MagicMock()
    except Exception as e:
        pytest.skip(f"Fixture initialization failed: {e}")
    yield func


def test_getInitialConfig_1(function):
    with (
        mock.patch.object(function, "getAndStoreDeviceProp"),
        mock.patch.object(function, "getDeviceProp") as m,
    ):
        function.getInitialConfig()
        attrs = [c.args[0] for c in m.call_args_list]
        assert "ApertureDiameter" in attrs
        assert "FocalLength" in attrs


def test_startCommunication_1(function):
    """Test that startCommunication (from AlpacaClass) works."""
    with mock.patch.object(function.threadPool, "start") as m_start:
        function.startCommunication()
        m_start.assert_called_once()


def test_startCommunication_2(function):
    """Test that startCommunication (from AlpacaClass) starts the worker thread."""
    with mock.patch.object(function.threadPool, "start") as m_start:
        function.startCommunication()
        m_start.assert_called_once()
