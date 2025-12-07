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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################

from unittest import mock

import pytest

from mw4.logic.powerswitch.pegasusUPB import PegasusUPB



from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="function")
def function():
    func = PegasusUPB(app=App())
    yield func


def test_properties(function):
    function.framework = "indi"
    function.host = ("localhost", 7624)
    assert function.host == ("localhost", 7624)

    function.deviceName = "test"
    assert function.deviceName == "test"


def test_properties_2(function):
    function.updateRate = 1000
    function.loadConfig = True
    function.framework = "indi"
    assert function.updateRate == 1000
    assert function.loadConfig


def test_startCommunication_2(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "startCommunication", return_value=True):
        function.startCommunication()


def test_stopCommunication_2(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "stopCommunication", return_value=True):
        function.stopCommunication()


def test_togglePowerPort_2(function):
    function.framework = "indi"
    function.togglePowerPort("1")


def test_togglePowerPortBoot_2(function):
    function.framework = "indi"
    function.togglePowerPortBoot("1")


def test_toggleHubUSB_2(function):
    function.framework = "indi"
    function.toggleHubUSB()


def test_togglePortUSB_2(function):
    function.framework = "indi"
    function.togglePortUSB("1")


def test_toggleAutoDew_2(function):
    function.framework = "indi"
    function.toggleAutoDew()


def test_sendDew_2(function):
    function.framework = "indi"
    function.sendDew("1", 100)


def test_sendAdjustableOutput_2(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "sendAdjustableOutput", return_value=False):
        function.sendAdjustableOutput(1)


def test_sendAdjustableOutput_3(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "sendAdjustableOutput", return_value=True):
        function.sendAdjustableOutput(1)


def test_reboot_2(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "reboot", return_value=False):
        function.reboot()


def test_reboot_3(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "reboot", return_value=True):
        function.reboot()
