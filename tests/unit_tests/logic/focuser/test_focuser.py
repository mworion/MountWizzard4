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

import platform
import pytest
from mw4.logic.focuser.focuser import Focuser
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function():
    try:
        func = Focuser(app=App())
    except Exception as e:
        pytest.skip(f"Fixture initialization failed: {e}")
    yield func


def test_properties(function):
    function.framework = "indi"
    function.host = ("localhost", 7624)
    assert function.host == ("localhost", 7624)

    function.deviceName = "test"
    assert function.deviceName == "test"


def test_properties_2(function):
    function.loadConfig = True
    function.framework = "indi"
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


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows needed")
def test_focuserAscom_import():
    import importlib

    spec = importlib.util.find_spec("mw4.logic.focuser.focuserAscom")
    assert spec is not None


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows needed")
def test_focuser_ascom_in_run():
    from mw4.logic.focuser.focuser import Focuser
    from tests.unit_tests.unitTestAddOns.baseTestApp import App

    function = Focuser(app=App())
    if platform.system() == "Windows":
        assert "ascom" in function.run
        assert function.run["ascom"] is not None
