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
    signals = Signals()
    loadConfig = True


@pytest.fixture(autouse=True, scope="module")
def function():
    func = TelescopeAlpaca(parent=Parent())
    func.device = mock.MagicMock()
    yield func


def test_getInitialConfig(function):
    with (
        mock.patch.object(function, "getAndStoreDeviceProp") as m_store,
        mock.patch.object(function, "getDeviceProp") as m_get,
    ):
        function.getInitialConfig()
        store_attrs = [c.args[0] for c in m_store.call_args_list]
        assert "Name" in store_attrs
        assert "DriverVersion" in store_attrs
        get_attrs = [c.args[0] for c in m_get.call_args_list]
        assert "ApertureDiameter" in get_attrs
        assert "FocalLength" in get_attrs
