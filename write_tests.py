"""Helper script to write all refactored source and test files."""
import os

BASE = "/Users/Q115346/PycharmProjects/MountWizzard4"

files = {}

# ── test_sgproClass.py ──────────────────────────────────────────────────────
files[f"{BASE}/tests/unit_tests/base/test_sgproClass.py"] = """\
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
import PySide6
import pytest
from mw4.base.loggerMW import setupLogging
from mw4.base.sgproClass import SGProClass
from mw4.base.signalsDevices import Signals
from PySide6.QtCore import QTimer
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock

setupLogging()


@pytest.fixture(autouse=True, scope="function")
def function():
    class Parent:
        app = App()
        data = {}
        signals = Signals()

    with mock.patch.object(QTimer, "start"):
        func = SGProClass(parent=Parent())
        yield func


def test_properties_1(function):
    function.deviceName = "test"
    function.deviceName = "test:2"


def test_sgConnectDevice_1(function):
    function.deviceName = "test test"
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(function, "requestProperty", return_value={}):
        suc = function.sgConnectDevice()
        assert not suc


def test_sgConnectDevice_2(function):
    function.deviceName = "test test"
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(
        function, "requestProperty", return_value={"Success": True}
    ):
        suc = function.sgConnectDevice()
        assert suc


def test_sgDisconnectDevice_1(function):
    function.deviceName = "test test"
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(function, "requestProperty", return_value={}):
        suc = function.sgDisconnectDevice()
        assert not suc


def test_sgDisconnectDevice_2(function):
    function.deviceName = "test test"
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(
        function, "requestProperty", return_value={"Success": True}
    ):
        suc = function.sgDisconnectDevice()
        assert suc


def test_sgEnumerateDevice_1(function):
    function.deviceName = "test test"
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(function, "requestProperty", return_value={}):
        suc = function.sgEnumerateDevice()
        assert not suc


def test_sgEnumerateDevice_2(function):
    function.deviceName = "test test"
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(
        function, "requestProperty", return_value={"Devices": True}
    ):
        suc = function.sgEnumerateDevice()
        assert suc


def test_startTimer(function):
    function.startSGProTimer()


def test_stopTimer(function):
    with mock.patch.object(PySide6.QtCore.QTimer, "stop"):
        function.stopSGProTimer()


def test_stopCommunication_1(function):
    function.deviceConnected = True
    function.serverConnected = True
    function.deviceName = "test"
    with mock.patch.object(function, "stopSGProTimer"):
        with mock.patch.object(function, "sgDisconnectDevice"):
            function.stopCommunication()
            assert not function.serverConnected
            assert not function.deviceConnected


def test_discoverDevices_1(function):
    with mock.patch.object(function, "sgEnumerateDevice", return_value=[]):
        val = function.discoverDevices("Camera")
        assert val == []


def test_discoverDevices_2(function):
    with mock.patch.object(function, "sgEnumerateDevice", return_value=["test"]):
        val = function.discoverDevices("Camera")
        assert val == ["test"]


def test_isConnectedState_1(function):
    assert function.isConnectedState("test")


def test_isConnectedState_2(function):
    assert not function.isConnectedState("DISCONNECTED")


def test_connectDevice_bridge(function):
    with mock.patch.object(function, "sgConnectDevice", return_value=True) as m:
        result = function.connectDevice()
        m.assert_called_once()
        assert result


def test_disconnectDevice_bridge(function):
    with mock.patch.object(function, "sgDisconnectDevice", return_value=True) as m:
        result = function.disconnectDevice()
        m.assert_called_once()
        assert result


def test_enumerateDevice_bridge(function):
    with mock.patch.object(
        function, "sgEnumerateDevice", return_value=["cam"]
    ) as m:
        result = function.enumerateDevice()
        m.assert_called_once()
        assert result == ["cam"]


def test_startTimer_bridge(function):
    with mock.patch.object(function, "startSGProTimer") as m:
        function.startTimer()
        m.assert_called_once()


def test_stopTimer_bridge(function):
    with mock.patch.object(function, "stopSGProTimer") as m:
        function.stopTimer()
        m.assert_called_once()
"""

# ── test_ninaClass.py ───────────────────────────────────────────────────────
files[f"{BASE}/tests/unit_tests/base/test_ninaClass.py"] = """\
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
import PySide6
import pytest
import requests
from mw4.base.loggerMW import setupLogging
from mw4.base.ninaClass import NINAClass
from mw4.base.signalsDevices import Signals
from PySide6.QtCore import QTimer
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock

setupLogging()


@pytest.fixture(autouse=True, scope="function")
def function():
    class Parent:
        app = App()
        data = {}
        signals = Signals()

    with mock.patch.object(QTimer, "start"):
        func = NINAClass(parent=Parent())
        yield func


def test_properties_1(function):
    function.deviceName = "test"


def test_connectDevice_1(function):
    function.deviceName = "test test"
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(function, "requestProperty", return_value={}):
        suc = function.connectDevice()
        assert not suc


def test_connectDevice_2(function):
    function.deviceName = "test test"
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(
        function, "requestProperty", return_value={"Success": True}
    ):
        suc = function.connectDevice()
        assert suc


def test_disconnectDevice_1(function):
    function.deviceName = "test test"
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(function, "requestProperty", return_value={}):
        suc = function.disconnectDevice()
        assert not suc


def test_disconnectDevice_2(function):
    function.deviceName = "test test"
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(
        function, "requestProperty", return_value={"Success": True}
    ):
        suc = function.disconnectDevice()
        assert suc


def test_enumerateDevice_1(function):
    function.deviceName = "test test"
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(function, "requestProperty", return_value={}):
        suc = function.enumerateDevice()
        assert not suc


def test_enumerateDevice_2(function):
    function.deviceName = "test test"
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(
        function, "requestProperty", return_value={"Devices": True}
    ):
        suc = function.enumerateDevice()
        assert suc


def test_startTimer(function):
    function.startNINATimer()


def test_stopTimer(function):
    with mock.patch.object(PySide6.QtCore.QTimer, "stop"):
        function.stopNINATimer()


def test_stopCommunication_1(function):
    function.deviceConnected = True
    function.serverConnected = True
    function.deviceName = "test"
    with mock.patch.object(function, "stopNINATimer"):
        with mock.patch.object(function, "disconnectDevice"):
            function.stopCommunication()
            assert not function.serverConnected
            assert not function.deviceConnected


def test_discoverDevices_1(function):
    with mock.patch.object(function, "enumerateDevice", return_value=[]):
        val = function.discoverDevices("Camera")
        assert val == []


def test_discoverDevices_2(function):
    with mock.patch.object(function, "enumerateDevice", return_value=["test"]):
        val = function.discoverDevices("Camera")
        assert val == ["test"]


def test_isConnectedState_1(function):
    assert function.isConnectedState(0)


def test_isConnectedState_2(function):
    assert not function.isConnectedState(5)


def test_startTimer_bridge(function):
    with mock.patch.object(function, "startNINATimer") as m:
        function.startTimer()
        m.assert_called_once()


def test_stopTimer_bridge(function):
    with mock.patch.object(function, "stopNINATimer") as m:
        function.stopTimer()
        m.assert_called_once()
"""

for path, content in files.items():
    with open(path, "w") as fh:
        fh.write(content)
    print(f"written {path} ({len(content)} chars)")

