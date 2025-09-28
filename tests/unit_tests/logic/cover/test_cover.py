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
import pytest
import unittest.mock as mock

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.cover.cover import Cover


@pytest.fixture(autouse=True, scope="function")
def function():
    func = Cover(app=App())
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


def test_closeCover_2(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "closeCover", return_value=False):
        function.closeCover()


def test_closeCover_3(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "closeCover", return_value=True):
        function.closeCover()


def test_openCover_2(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "openCover", return_value=False):
        function.openCover()


def test_openCover_3(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "openCover", return_value=True):
        function.openCover()


def test_haltCover_2(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "haltCover", return_value=False):
        function.haltCover()


def test_haltCover_3(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "haltCover", return_value=True):
        function.haltCover()


def test_lightOn_2(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "lightOn", return_value=False):
        function.lightOn()


def test_lightOn_3(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "lightOn", return_value=True):
        function.lightOn()


def test_lightOff_2(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "lightOff", return_value=False):
        function.lightOff()


def test_lightOff_3(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "lightOff", return_value=True):
        function.lightOff()


def test_lightIntensity_2(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "lightIntensity", return_value=False):
        function.lightIntensity(0)


def test_lightIntensity_3(function):
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "lightIntensity", return_value=True):
        function.lightIntensity(0)
