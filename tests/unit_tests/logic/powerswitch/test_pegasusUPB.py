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
from mw4.logic.powerswitch.pegasusUPB import PegasusUPB
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function():
    func = PegasusUPB(app=App())
    yield func


# ---------------------------------------------------------------------------
# properties
# ---------------------------------------------------------------------------


def test_properties(function):
    """host, deviceName, and loadConfig round-trip correctly."""
    function.framework = "indi"
    function.host = ("localhost", 7624)
    assert function.host == ("localhost", 7624)

    function.deviceName = "test"
    assert function.deviceName == "test"

    function.loadConfig = True
    assert function.loadConfig


# ---------------------------------------------------------------------------
# startCommunication / stopCommunication
# ---------------------------------------------------------------------------


def test_startCommunication(function):
    """startCommunication() delegates to the active framework adapter."""
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "startCommunication", return_value=True):
        function.startCommunication()


def test_stopCommunication(function):
    """stopCommunication() delegates to the active framework adapter."""
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "stopCommunication", return_value=True):
        function.stopCommunication()


# ---------------------------------------------------------------------------
# togglePowerPort
# ---------------------------------------------------------------------------


def test_togglePowerPort(function):
    """togglePowerPort() delegates to the active framework adapter."""
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "togglePowerPort") as mock_toggle:
        function.togglePowerPort("1")
        mock_toggle.assert_called_once_with(port="1")


# ---------------------------------------------------------------------------
# togglePowerPortBoot
# ---------------------------------------------------------------------------


def test_togglePowerPortBoot(function):
    """togglePowerPortBoot() delegates to the active framework adapter."""
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "togglePowerPortBoot") as mock_toggle:
        function.togglePowerPortBoot("1")
        mock_toggle.assert_called_once_with(port="1")


# ---------------------------------------------------------------------------
# toggleHubUSB
# ---------------------------------------------------------------------------


def test_toggleHubUSB(function):
    """toggleHubUSB() delegates to the active framework adapter."""
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "toggleHubUSB") as mock_toggle:
        function.toggleHubUSB()
        mock_toggle.assert_called_once()


# ---------------------------------------------------------------------------
# togglePortUSB
# ---------------------------------------------------------------------------


def test_togglePortUSB(function):
    """togglePortUSB() delegates to the active framework adapter."""
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "togglePortUSB") as mock_toggle:
        function.togglePortUSB("1")
        mock_toggle.assert_called_once_with(port="1")


# ---------------------------------------------------------------------------
# toggleAutoDew
# ---------------------------------------------------------------------------


def test_toggleAutoDew(function):
    """toggleAutoDew() delegates to the active framework adapter."""
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "toggleAutoDew") as mock_toggle:
        function.toggleAutoDew()
        mock_toggle.assert_called_once()


# ---------------------------------------------------------------------------
# sendDew
# ---------------------------------------------------------------------------


def test_sendDew(function):
    """sendDew() delegates port and value to the active framework adapter."""
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "sendDew") as mock_send:
        function.sendDew("1", 100)
        mock_send.assert_called_once_with(port="1", value=100)


# ---------------------------------------------------------------------------
# sendAdjustableOutput
# ---------------------------------------------------------------------------


def test_sendAdjustableOutput_returns_false(function):
    """sendAdjustableOutput() delegates even when adapter returns False."""
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "sendAdjustableOutput", return_value=False):
        function.sendAdjustableOutput(1)


def test_sendAdjustableOutput_returns_true(function):
    """sendAdjustableOutput() delegates even when adapter returns True."""
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "sendAdjustableOutput", return_value=True):
        function.sendAdjustableOutput(1)


# ---------------------------------------------------------------------------
# reboot
# ---------------------------------------------------------------------------


def test_reboot_returns_false(function):
    """reboot() delegates even when adapter returns False."""
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "reboot", return_value=False):
        function.reboot()


def test_reboot_returns_true(function):
    """reboot() delegates even when adapter returns True."""
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "reboot", return_value=True):
        function.reboot()
