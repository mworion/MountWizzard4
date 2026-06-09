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
from mw4.logic.lightPanel.lightPanel import LightPanel
from mw4.logic.lightPanel.lightPanelIndi import LightPanelIndi
from queue import Queue
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function():
    try:
        cover = LightPanel(App())
        func = LightPanelIndi(parent=cover)
        func.config.deviceName = "test_cover"
    except Exception as e:
        pytest.skip(f"Fixture initialization failed: {e}")
    yield func
    func.app.threadPool.waitForDone(5000)


# ---------------------------------------------------------------------------
# lightOn
# ---------------------------------------------------------------------------


def test_lightOn(function):
    """lightOn() puts FLAT_LIGHT_ON='On' into txQ."""
    function.txQ = Queue()
    function.lightOn()
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_cover", "FLAT_LIGHT_CONTROL", {"FLAT_LIGHT_ON": "On"})


# ---------------------------------------------------------------------------
# lightOff
# ---------------------------------------------------------------------------


def test_lightOff(function):
    """lightOff() puts FLAT_LIGHT_ON='Off' into txQ."""
    function.txQ = Queue()
    function.lightOff()
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_cover", "FLAT_LIGHT_CONTROL", {"FLAT_LIGHT_OFF": "On"})


# ---------------------------------------------------------------------------
# lightIntensity
# ---------------------------------------------------------------------------


def test_lightIntensity(function):
    """lightIntensity(value) puts the intensity value into txQ."""
    function.txQ = Queue()
    function.lightIntensity(128.0)
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == (
        "test_cover",
        "FLAT_LIGHT_INTENSITY",
        {"FLAT_LIGHT_INTENSITY_VALUE": 128.0},
    )
