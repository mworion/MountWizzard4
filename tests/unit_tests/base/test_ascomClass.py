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
import platform
from unittest import mock

import pytest

if not platform.system() == "Windows":
    pytest.skip("skipping windows-only tests", allow_module_level=True)

# external packages
import PySide6
import win32com.client
from PySide6.QtCore import QTimer

import mw4.base.ascomClass

# local import
from mw4.base.ascomClass import AscomClass
from mw4.base.loggerMW import setupLogging
from mw4.base.signalsDevices import Signals
from tests.unit_tests.unitTestAddOns.baseTestApp import App

setupLogging()


class Parent:
    app = App()
    data = {}
    deviceType = ""
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="function")
def function():
    with mock.patch.object(QTimer, "start"):
        func = AscomClass(parent=Parent())
        func.signals = Signals()
        yield func


def test_startTimer(function):
    with mock.patch.object(PySide6.QtCore.QTimer, "start"):
        function.startAscomTimer()


def test_stopTimer(function):
    with mock.patch.object(PySide6.QtCore.QTimer, "stop"):
        function.stopAscomTimer()


def test_getAscomProperty_0(function):
    function.deviceConnected = False
    function.propertyExceptions = ["Connected"]
    val = function.getAscomProperty("Connected")
    assert val is None


def test_getAscomProperty_1(function):
    function.deviceConnected = True
    function.propertyExceptions = ["Connected"]
    val = function.getAscomProperty("Connected")
    assert val is None


def test_getAscomProperty_2(function):
    function.propertyExceptions = ["test"]
    function.deviceConnected = True
    with mock.patch.object(mw4.base.ascomClass, "eval", side_effect=Exception):
        val = function.getAscomProperty("Connected")
        assert val is None
        assert "Connected" in function.propertyExceptions


def test_getAscomProperty_3(function):
    class Client:
        connect = True

    function.client = Client()
    function.propertyExceptions = ["test"]
    function.deviceConnected = True
    with mock.patch.object(mw4.base.ascomClass, "eval", return_value="1"):
        val = function.getAscomProperty("Connected")
        assert val


def test_getAscomProperty_4(function):
    class Client:
        connect = True
        imagearray = None

    function.client = Client()
    function.propertyExceptions = ["test"]
    function.deviceConnected = True
    with mock.patch.object(mw4.base.ascomClass, "eval", return_value="1"):
        val = function.getAscomProperty("ImageArray")
        assert val


def test_setAscomProperty_0(function):
    function.deviceConnected = False
    function.propertyExceptions = ["Connected"]
    function.setAscomProperty("Connected", True)


def test_setAscomProperty_1(function):
    function.deviceConnected = True
    function.propertyExceptions = ["Connected"]
    function.setAscomProperty("Connected", True)


def test_setAscomProperty_2(function):
    function.propertyExceptions = ["test"]
    function.deviceConnected = True
    with mock.patch.object(mw4.base.ascomClass, "exec", side_effect=Exception):
        function.setAscomProperty("Connected", True)
        assert "Connect" not in function.propertyExceptions


def test_setAscomProperty_3(function):
    function.propertyExceptions = ["test"]
    function.deviceConnected = True
    with mock.patch.object(mw4.base.ascomClass, "exec", side_effect=Exception):
        function.setAscomProperty("Names", True)
        assert "Names" in function.propertyExceptions


def test_setAscomProperty_4(function):
    class Client:
        Connect = False

    function.client = Client()
    function.propertyExceptions = ["test"]
    function.deviceConnected = True
    function.setAscomProperty("Connected", True)
    assert function.client


def test_callAscomMethod_1(function):
    function.propertyExceptions = ["Connected"]
    function.callAscomMethod("Connected", True)


def test_callAscomMethod_2(function):
    function.propertyExceptions = ["Test"]
    with mock.patch.object(mw4.base.ascomClass, "exec", side_effect=Exception):
        function.callAscomMethod("Connected", True)
        assert "Connected" in function.propertyExceptions


def test_callAscomMethod_3(function):
    class Client:
        Connect = False

    function.client = Client()
    function.propertyExceptions = ["Test"]
    with mock.patch.object(mw4.base.ascomClass, "exec"):
        function.callAscomMethod("Connected", True)
        assert function.client


def test_getAndStoreAscomProperty(function):
    with mock.patch.object(function, "getAscomProperty"):
        with mock.patch.object(function, "storePropertyToData"):
            function.getAndStoreAscomProperty(10, "YES")


def test_workerConnectDevice_1(function):
    function.serverConnected = False
    function.deviceConnected = False
    with mock.patch.object(mw4.base.ascomClass, "sleepAndEvents"):
        with mock.patch.object(function, "setAscomProperty"):
            with mock.patch.object(function, "getAscomProperty", return_value=False):
                function.workerConnectDevice()
                assert not function.serverConnected
                assert not function.deviceConnected


def test_workerConnectDevice_2(function):
    function.serverConnected = False
    function.deviceConnected = False
    with mock.patch.object(mw4.base.ascomClass, "sleepAndEvents"):
        with mock.patch.object(function, "setAscomProperty"):
            with mock.patch.object(function, "getAscomProperty", return_value=True):
                function.workerConnectDevice()
                assert function.serverConnected
                assert function.deviceConnected


def test_workerGetInitialConfig_1(function):
    with mock.patch.object(function, "getAndStoreAscomProperty", return_value="test"):
        function.workerGetInitialConfig()


def test_pollStatus_1(function):
    function.deviceConnected = True
    with mock.patch.object(function, "getAscomProperty", return_value=False):
        function.workerPollStatus()
        assert not function.deviceConnected


def test_pollStatus_2(function):
    function.deviceConnected = False
    with mock.patch.object(function, "getAscomProperty", return_value=True):
        function.workerPollStatus()
        assert function.deviceConnected


def test_callerInitUnInit_1(function):
    def test():
        return 1

    function.callerInitUnInit(test)


def test_callMethodThreaded_1(function):
    def test():
        return

    function.deviceConnected = False
    function.callMethodThreaded(test)


def test_callMethodThreaded_2(function):
    def test():
        return

    function.deviceConnected = True
    with mock.patch.object(function.threadPool, "start"):
        function.callMethodThreaded(test, cb_fin=test, cb_res=test)


def test_callMethodThreaded_3(function):
    def test():
        return

    function.deviceConnected = True
    with mock.patch.object(function.threadPool, "start"):
        function.callMethodThreaded(test, 10, 20, cb_fin=test, cb_res=test)


def test_callMethodThreaded_4(function):
    def test():
        return

    function.deviceConnected = True
    with mock.patch.object(function.threadPool, "start"):
        function.callMethodThreaded(test, 10, 20)


def test_processPolledData(function):
    function.processPolledData()


def test_workerPollData(function):
    function.workerPollData()


def test_pollData(function):
    with mock.patch.object(function, "callMethodThreaded"):
        function.pollData()


def test_pollStatus(function):
    with mock.patch.object(function, "callMethodThreaded"):
        function.pollStatus()


def test_getInitialConfig(function):
    with mock.patch.object(function, "callMethodThreaded"):
        function.getInitialConfig()


def test_startCommunication_1(function):
    function.deviceName = "test"
    with mock.patch.object(function.threadPool, "start"):
        with mock.patch.object(win32com.client.dynamic, "Dispatch"):
            function.startCommunication()


def test_startCommunication_2(function):
    function.deviceName = "test"
    with mock.patch.object(win32com.client.dynamic, "Dispatch", side_effect=Exception()):
        function.startCommunication()


def test_startCommunication_3(function):
    function.startCommunication()


def test_stopCommunication_1(function):
    function.deviceConnected = True
    function.serverConnected = True
    function.deviceName = "test"
    with mock.patch.object(function, "stopAscomTimer"):
        with mock.patch.object(function, "setAscomProperty"):
            function.stopCommunication()


def test_stopCommunication_2(function):
    function.client = 1
    function.deviceConnected = True
    function.serverConnected = True
    function.deviceName = "test"
    with mock.patch.object(function, "stopAscomTimer"):
        with mock.patch.object(function, "setAscomProperty"):
            function.stopCommunication()
            assert not function.serverConnected
            assert not function.deviceConnected


def test_selectAscomDriver_1(function):
    with mock.patch.object(win32com.client, "Dispatch", side_effect=Exception()):
        function.selectAscomDriver("Test")


def test_selectAscomDriver_2(function):
    class Test:
        def init(self):
            self.DeviceType = None

        @staticmethod
        def Choose(name):
            return name

    with mock.patch.object(win32com.client, "Dispatch", return_value=Test()):
        function.selectAscomDriver("Test")
