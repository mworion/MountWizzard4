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
from unittest import mock

import pytest
from logic.focuser.focuser import Focuser

# external packages
# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="function")
def function():
    func = Focuser(app=App())
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


def test_move_2(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "move", return_value=True):
        function.move(1000)


def test_halt_2(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "halt", return_value=True):
        function.halt()
