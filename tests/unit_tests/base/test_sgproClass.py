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

# external packages
import PySide6
import pytest
import requests
from PySide6.QtCore import QTimer

from mw4.base.loggerMW import setupLogging

# local import
from mw4.base.sgproClass import SGProClass
from mw4.base.signalsDevices import Signals
from tests.unit_tests.unitTestAddOns.baseTestApp import App

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


def test_requestProperty_1(function):
    function.deviceName = "test"

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return "test"

    with mock.patch.object(requests, "post", return_value=Response()):
        val = function.requestProperty("test", {"test": 1})
        assert val == "test"


def test_requestProperty_2(function):
    function.deviceName = "test"

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return "test"

    with mock.patch.object(requests, "get", return_value=Response()):
        val = function.requestProperty("test")
        assert val == "test"


def test_requestProperty_3(function):
    function.deviceName = "test"

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return "test"

    with mock.patch.object(
        requests,
        "get",
        side_effect=requests.exceptions.Timeout,
        return_value=Response(),
    ):
        val = function.requestProperty("test")
        assert not val


def test_requestProperty_4(function):
    function.deviceName = "test"

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return "test"

    with mock.patch.object(
        requests,
        "get",
        side_effect=requests.exceptions.ConnectionError,
        return_value=Response(),
    ):
        val = function.requestProperty("test")
        assert not val


def test_requestProperty_5(function):
    function.deviceName = "test"

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return "test"

    with mock.patch.object(requests, "get", side_effect=Exception, return_value=Response()):
        val = function.requestProperty("test")
        assert not val


def test_requestProperty_6(function):
    function.deviceName = "test"

    class Response:
        status_code = 400

        @staticmethod
        def json():
            return "test"

    with mock.patch.object(requests, "get", return_value=Response()):
        val = function.requestProperty("test")
        assert not val


def test_sgConnectDevice_1(function):
    function.deviceName = "test test"
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(function, "requestProperty", return_value={}):
        suc = function.sgConnectDevice()
        assert not suc


def test_sgConnectDevice_2(function):
    function.deviceName = "test test"
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(function, "requestProperty", return_value={"Success": True}):
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
    with mock.patch.object(function, "requestProperty", return_value={"Success": True}):
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
    with mock.patch.object(function, "requestProperty", return_value={"Devices": True}):
        suc = function.sgEnumerateDevice()
        assert suc


def test_startTimer(function):
    function.startSGProTimer()


def test_stopTimer(function):
    with mock.patch.object(PySide6.QtCore.QTimer, "stop"):
        function.stopSGProTimer()


def test_processPolledData(function):
    function.processPolledData()


def test_workerPollData(function):
    function.workerPollData()


def test_pollData_1(function):
    function.deviceConnected = True
    with mock.patch.object(function.threadPool, "start"):
        function.pollData()


def test_pollData_2(function):
    function.deviceConnected = False
    with mock.patch.object(function.threadPool, "start"):
        function.pollData()


def test_workerGetInitialConfig_1(function):
    function.workerGetInitialConfig()


def test_getInitialConfig_1(function):
    with mock.patch.object(function.threadPool, "start"):
        function.getInitialConfig()


def test_workerPollStatus_1(function):
    function.DEVICE_TYPE = "Camera"
    with mock.patch.object(function, "requestProperty", return_value=None):
        with mock.patch.object(function, "storePropertyToData"):
            function.workerPollStatus()


def test_workerPollStatus_2(function):
    function.DEVICE_TYPE = "Camera"

    function.deviceConnected = True
    with mock.patch.object(
        function,
        "requestProperty",
        return_value={"State": "DISCONNECTED", "Message": "test"},
    ):
        with mock.patch.object(function, "storePropertyToData"):
            with mock.patch.object(function, "getInitialConfig"):
                function.workerPollStatus()
                assert not function.deviceConnected


def test_workerPollStatus_3(function):
    function.DEVICE_TYPE = "Camera"
    function.deviceConnected = False
    with mock.patch.object(
        function,
        "requestProperty",
        return_value={"State": "DISCONNECTED", "Message": "test"},
    ):
        with mock.patch.object(function, "storePropertyToData"):
            with mock.patch.object(function, "getInitialConfig"):
                function.workerPollStatus()
                assert not function.deviceConnected


def test_workerPollStatus_4(function):
    function.DEVICE_TYPE = "Camera"
    function.deviceConnected = True
    with mock.patch.object(
        function, "requestProperty", return_value={"State": "test", "Message": "test"}
    ):
        with mock.patch.object(function, "storePropertyToData"):
            with mock.patch.object(function, "getInitialConfig"):
                function.workerPollStatus()
                assert function.deviceConnected


def test_workerPollStatus_5(function):
    function.DEVICE_TYPE = "Camera"
    function.deviceConnected = False
    with mock.patch.object(
        function, "requestProperty", return_value={"State": "test", "Message": "test"}
    ):
        with mock.patch.object(function, "storePropertyToData"):
            with mock.patch.object(function, "getInitialConfig"):
                function.workerPollStatus()
                assert function.deviceConnected


def test_clearPollStatus(function):
    function.mutexPollStatus.lock()
    function.clearPollStatus()


def test_pollStatus_1(function):
    function.mutexPollStatus.lock()
    with mock.patch.object(function.threadPool, "start"):
        function.pollStatus()
    function.mutexPollStatus.unlock()


def test_pollStatus_2(function):
    with mock.patch.object(function.threadPool, "start"):
        function.pollStatus()
    function.mutexPollStatus.unlock()


def test_startCommunication_1(function):
    function.serverConnected = False
    with mock.patch.object(function.threadPool, "start"):
        function.startCommunication()
        assert function.serverConnected


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
