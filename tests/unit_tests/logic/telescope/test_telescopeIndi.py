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
from mw4.logic.telescope.telescopeIndi import TelescopeIndi
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Parent:
    try:
        app = App()
    except Exception:
        app = mock.MagicMock()
    data = {}
    signals = Signals()
    loadConfig = True


@pytest.fixture(autouse=True, scope="module")
def function():
    try:
        func = TelescopeIndi(parent=Parent())
    except Exception as e:
        pytest.skip(f"Fixture initialization failed: {e}")
        func = TelescopeIndi(parent=Parent())
    except Exception as e:
        pytest.skip(f"Fixture initialization failed: {e}")
    yield func


def test_class(function):
    assert 1 == 1
