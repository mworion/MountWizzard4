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
