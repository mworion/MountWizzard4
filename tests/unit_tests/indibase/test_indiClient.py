############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

# local import
from indibase.indiClient import Client
from indibase.indiDevice import Device
from indibase import indiXML
from indibase.indiXML import INDIBase
from base.loggerMW import setupLogging

setupLogging()


@pytest.fixture(autouse=True, scope="function")
def function():
    function = Client()
    yield function


def test_properties_1(function):
    function.host = "localhost"
    assert function.host == ("localhost", 7624)


def test_properties_2(function):
    function.host = 12
    assert function.host is None


def test_clearParser(function):
    suc = function.clearParser()
    assert suc


def test_setServer_1(function):
    suc = function.setServer()
    assert not suc
    assert not function.connected


def test_setServer_2(function):
    function.connected = True
    suc = function.setServer("localhost")
    assert suc
    assert not function.connected
    assert function.host == ("localhost", 7624)


def test_watchDevice_1(function):
    with mock.patch.object(indiXML, "clientGetProperties"):
        with mock.patch.object(function, "_sendCmd", return_value=False):
            suc = function.watchDevice("test")
            assert not suc


def test_watchDevice_2(function):
    with mock.patch.object(indiXML, "clientGetProperties"):
        with mock.patch.object(function, "_sendCmd", return_value=True):
            suc = function.watchDevice("")
            assert suc


def test_connectServer_1(function):
    function._host = None
    with mock.patch.object(function.socket, "connectToHost"):
        with mock.patch.object(function.socket, "waitForConnected", return_value=True):
            suc = function.connectServer()
            assert not suc


def test_connectServer_2(function):
    function._host = ("localhost", 7624)
    function.connected = True
    suc = function.connectServer()
    assert not suc


def test_connectServer_3(function):
    function._host = ("localhost", 7624)
    function.connected = False
    with mock.patch.object(function.socket, "connectToHost"):
        with mock.patch.object(function.socket, "state", return_value=1):
            with mock.patch.object(function.socket, "abort"):
                suc = function.connectServer()
                assert suc
                assert not function.connected


def test_clearDevices_1(function):
    function.devices = {"test1", "test2"}
    suc = function.clearDevices()
    assert suc
    assert function.devices == {}


def test_clearDevices_2(function):
    function.devices = {"test1", "test2"}
    suc = function.clearDevices("test1")
    assert suc
    assert function.devices == {}


def test_disconnectServer(function):
    with mock.patch.object(function, "clearParser"):
        with mock.patch.object(function, "clearDevices"):
            with mock.patch.object(function.socket, "abort"):
                suc = function.disconnectServer()
                assert suc


def test_isServerConnected_1(function):
    function.connected = True
    suc = function.isServerConnected()
    assert suc


def test_isServerConnected_2(function):
    function.connected = False
    suc = function.isServerConnected()
    assert not suc


def test_connectDevice_1(function):
    function.connected = False
    suc = function.connectDevice()
    assert not suc


def test_connectDevice_2(function):
    function.connected = True
    suc = function.connectDevice()
    assert not suc


def test_connectDevice_3(function):
    function.connected = True
    suc = function.connectDevice("test")
    assert not suc


def test_connectDevice_4(function):
    function.connected = True
    function.devices = {"test": Device()}
    with mock.patch.object(function.devices["test"], "getSwitch", return_value={"CONNECT": "On"}):
        suc = function.connectDevice("test")
        assert not suc


def test_connectDevice_5(function):
    function.connected = True
    function.devices = {"test": Device()}
    with mock.patch.object(function.devices["test"], "getSwitch", return_value={"CONNECT": "Off"}):
        with mock.patch.object(function, "sendNewSwitch", return_value=False):
            suc = function.connectDevice("test")
            assert not suc


def test_connectDevice_6(function):
    function.connected = True
    function.devices = {"test": Device()}
    with mock.patch.object(function.devices["test"], "getSwitch", return_value={"CONNECT": "Off"}):
        with mock.patch.object(function, "sendNewSwitch", return_value=True):
            suc = function.connectDevice("test")
            assert suc


def test_disconnectDevice_1(function):
    function.connected = False
    suc = function.disconnectDevice()
    assert not suc


def test_disconnectDevice_2(function):
    function.connected = True
    suc = function.disconnectDevice()
    assert not suc


def test_disconnectDevice_3(function):
    function.connected = True
    suc = function.disconnectDevice("test")
    assert not suc


def test_disconnectDevice_4(function):
    function.connected = True
    function.devices = {"test": Device()}
    with mock.patch.object(
        function.devices["test"], "getSwitch", return_value={"DISCONNECT": "On"}
    ):
        suc = function.disconnectDevice("test")
        assert not suc


def test_disconnectDevice_5(function):
    function.connected = True
    function.devices = {"test": Device()}
    with mock.patch.object(
        function.devices["test"], "getSwitch", return_value={"DISCONNECT": "Off"}
    ):
        with mock.patch.object(function, "sendNewSwitch", return_value=False):
            suc = function.disconnectDevice("test")
            assert not suc


def test_disconnectDevice_6(function):
    function.connected = True
    function.devices = {"test": Device()}
    with mock.patch.object(
        function.devices["test"], "getSwitch", return_value={"DISCONNECT": "Off"}
    ):
        with mock.patch.object(function, "sendNewSwitch", return_value=True):
            suc = function.disconnectDevice("test")
            assert suc


def test_getDevice_1(function):
    val = function.getDevice()
    assert val is None


def test_getDevice_2(function):
    function.devices = {"test": 1}
    val = function.getDevice("test")
    assert val == 1


def test_getDevices_1(function):
    val = function.getDevices()
    assert val == []


def test_getDevices_2(function):
    function.devices = {"test": 1}
    with mock.patch.object(function, "_getDriverInterface", return_value=0x0001):
        val = function.getDevices()
        assert val == ["test"]


def test_getDevices_3(function):
    function.devices = {"test": 1}
    with mock.patch.object(function, "_getDriverInterface", return_value=0x0003):
        val = function.getDevices(0x00F0)
        assert val == []


def test_setBlobMode_1(function):
    suc = function.setBlobMode()
    assert not suc


def test_setBlobMode_2(function):
    suc = function.setBlobMode(deviceName="test")
    assert not suc


def test_setBlobMode_3(function):
    function.devices = {"test": Device()}
    with mock.patch.object(indiXML, "enableBLOB"):
        with mock.patch.object(function, "_sendCmd", return_value=False):
            suc = function.setBlobMode(deviceName="test")
            assert not suc


def test_setBlobMode_4(function):
    function.devices = {"test": Device()}
    with mock.patch.object(indiXML, "enableBLOB"):
        with mock.patch.object(function, "_sendCmd", return_value=True):
            suc = function.setBlobMode(deviceName="test")
            assert suc


def test_getBlobMode(function):
    function.getBlobMode()


def test_getHost_1(function):
    function._host = None
    val = function.getHost()
    assert val == ""


def test_getHost_2(function):
    function._host = ("localhost", 7624)
    val = function.getHost()
    assert val == "localhost"


def test_getPort_1(function):
    function._host = None
    val = function.getPort()
    assert val == 0


def test_getPort_2(function):
    function._host = ("localhost", 7624)
    val = function.getPort()
    assert val == 7624


def test_sendNewText_1(function):
    function.devices = {"test": Device()}
    suc = function.sendNewText("")
    assert not suc


def test_sendNewText_2(function):
    function.devices = {"test": Device()}
    suc = function.sendNewText(deviceName="test", propertyName="prop")
    assert not suc


def test_sendNewText_3(function):
    function.devices = {"test": Device()}
    function.devices["test"].prop = None
    suc = function.sendNewText(deviceName="test", propertyName="prop", text="test")
    assert not suc


def test_sendNewText_4(function):
    function.devices = {"test": Device()}
    function.devices["test"].prop = None
    with mock.patch.object(indiXML, "oneText", return_value="test"):
        with mock.patch.object(indiXML, "newTextVector"):
            with mock.patch.object(function, "_sendCmd", return_value=False):
                suc = function.sendNewText(deviceName="test", propertyName="prop", text="test")
                assert not suc


def test_sendNewText_5(function):
    function.devices = {"test": Device()}
    function.devices["test"].prop = None
    with mock.patch.object(indiXML, "oneText", return_value="test"):
        with mock.patch.object(indiXML, "newTextVector"):
            with mock.patch.object(function, "_sendCmd", return_value=True):
                suc = function.sendNewText(deviceName="test", propertyName="prop", text="test")
                assert suc


def test_sendNewNumber_1(function):
    function.devices = {"test": Device()}
    suc = function.sendNewNumber("")
    assert not suc


def test_sendNewNumber_2(function):
    function.devices = {"test": Device()}
    suc = function.sendNewNumber(deviceName="test", propertyName="prop")
    assert not suc


def test_sendNewNumber_3(function):
    function.devices = {"test": Device()}
    function.devices["test"].prop = None
    suc = function.sendNewNumber(deviceName="test", propertyName="prop", number=1)
    assert not suc


def test_sendNewNumber_4(function):
    function.devices = {"test": Device()}
    function.devices["test"].prop = None
    with mock.patch.object(indiXML, "oneNumber", return_value="test"):
        with mock.patch.object(indiXML, "newNumberVector"):
            with mock.patch.object(function, "_sendCmd", return_value=False):
                suc = function.sendNewNumber(deviceName="test", propertyName="prop", number=1)
                assert not suc


def test_sendNewNumber_5(function):
    function.devices = {"test": Device()}
    function.devices["test"].prop = None
    with mock.patch.object(indiXML, "oneNumber", return_value="test"):
        with mock.patch.object(indiXML, "newNumberVector"):
            with mock.patch.object(function, "_sendCmd", return_value=True):
                suc = function.sendNewNumber(deviceName="test", propertyName="prop", number=1)
                assert suc


def test_sendNewSwitch_1(function):
    function.devices = {"test": Device()}
    suc = function.sendNewSwitch("")
    assert not suc


def test_sendNewSwitch_2(function):
    function.devices = {"test": Device()}
    suc = function.sendNewSwitch(deviceName="test", propertyName="prop")
    assert not suc


def test_sendNewSwitch_3(function):
    function.devices = {"test": Device()}
    function.devices["test"].prop = None
    suc = function.sendNewSwitch(deviceName="test", propertyName="prop")
    assert not suc


def test_sendNewSwitch_4(function):
    function.devices = {"test": Device()}
    function.devices["test"].prop = None
    with mock.patch.object(indiXML, "oneSwitch", return_value="test"):
        with mock.patch.object(indiXML, "newSwitchVector"):
            with mock.patch.object(function, "_sendCmd", return_value=False):
                suc = function.sendNewSwitch(deviceName="test", propertyName="prop")
                assert not suc


def test_sendNewSwitch_5(function):
    function.devices = {"test": Device()}
    function.devices["test"].prop = None
    with mock.patch.object(indiXML, "oneSwitch", return_value="test"):
        with mock.patch.object(indiXML, "newSwitchVector"):
            with mock.patch.object(function, "_sendCmd", return_value=True):
                suc = function.sendNewSwitch(deviceName="test", propertyName="prop")
                assert suc


def test_startBlob(function):
    suc = function.startBlob()
    assert suc


def test_sendOneBlob(function):
    suc = function.sendOneBlob()
    assert suc


def test_finishBlob(function):
    suc = function.finishBlob()
    assert suc


def test_setVerbose(function):
    suc = function.setVerbose(True)
    assert suc


def test_isVerbose(function):
    suc = function.isVerbose()
    assert not suc


def test_setConnectionTimeout(function):
    suc = function.setConnectionTimeout()
    assert suc


def test__sendCmd_1(function):
    function.connected = False
    suc = function._sendCmd("")
    assert not suc


def test__sendCmd_2(function):
    function.connected = True
    cmd = INDIBase("<begin><end>".encode(encoding="UTF-8"), 0, {}, {})
    with mock.patch.object(INDIBase, "toXML", return_value="test".encode()):
        with mock.patch.object(function.socket, "write", return_value=0):
            with mock.patch.object(function.socket, "flush"):
                suc = function._sendCmd(cmd)
                assert not suc


def test__sendCmd_3(function):
    function.connected = True
    cmd = INDIBase("<begin><end>".encode(encoding="UTF-8"), 0, {}, {})
    with mock.patch.object(INDIBase, "toXML", return_value="test".encode()):
        with mock.patch.object(function.socket, "write", return_value=256):
            with mock.patch.object(function.socket, "flush"):
                suc = function._sendCmd(cmd)
                assert suc


def test_getDriverInterface_1(function):
    function.devices = {"test": Device()}
    val = function._getDriverInterface("test")
    assert val == -1


def test_getDriverInterface_2(function):
    function.devices = {"test": Device()}
    function.devices["test"].DRIVER_INFO = None
    val = function._getDriverInterface("test")
    assert val == -1


def test_getDriverInterface_3(function):
    function.devices = {"test": Device()}
    elemList = {"elementList": {}}
    function.devices["test"].DRIVER_INFO = elemList
    val = function._getDriverInterface("test")
    assert val == -1


def test_getDriverInterface_4(function):
    function.devices = {"test": Device()}
    elemList = {"elementList": {"DRIVER_INTERFACE": {"value": 0x0001}}}
    function.devices["test"].DRIVER_INFO = elemList
    val = function._getDriverInterface("test")
    assert val == 1


def test_fillAttributes_0(function):
    elem = indiXML.DefSwitch("defSwitch", "On", {"name": ""}, None)
    chunk = indiXML.DefSwitchVector("defSwitch", [elem], {}, None)
    suc = function._fillAttributes(deviceName="test", chunk=chunk, elementList={})
    assert not suc


def test_fillAttributes_1(function):
    elem = indiXML.DefSwitch("defSwitch", "On", {"name": "test"}, None)
    chunk = indiXML.DefSwitchVector("defSwitch", [elem], {}, None)
    suc = function._fillAttributes(deviceName="test", chunk=chunk, elementList={})
    assert suc


def test_fillAttributes_2(function):
    elem = indiXML.DefSwitch("defSwitch", "On", {"name": "test"}, None)
    chunk = indiXML.DefSwitchVector("defSwitch", [elem], {}, None)
    suc = function._fillAttributes(deviceName="test", chunk=chunk, elementList={"test": {}})
    assert suc


def test_fillAttributes_3(function):
    elem = indiXML.DefSwitch("defSwitch", "On", {"name": "CONNECT"}, None)
    chunk = indiXML.DefSwitchVector("defSwitch", [elem], {"state": "Ok"}, None)
    suc = function._fillAttributes(deviceName="test", chunk=chunk, elementList={})
    assert suc


def test_fillAttributes_4(function):
    elem = indiXML.DefSwitch("defSwitch", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.DefSwitchVector("defSwitch", [elem], {"state": "Ok"}, None)
    suc = function._fillAttributes(deviceName="test", chunk=chunk, elementList={})
    assert suc


def test_setupPropertyStructure(function):
    device = Device()
    elem = indiXML.DefSwitch("defSwitch", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.DefSwitchVector("defSwitch", [elem], {"state": "Ok"}, None)
    ip, el = function._setupPropertyStructure(chunk=chunk, device=device)
    assert ip == ""
    assert el == {}


def test_getDeviceReference_1(function):
    function.devices = {"test": Device()}
    elem = indiXML.DefSwitch("defSwitch", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.DefSwitchVector("defSwitch", [elem], {"device": "test"}, None)
    dev, name = function._getDeviceReference(chunk=chunk)
    assert dev == function.devices["test"]
    assert name == "test"


def test_getDeviceReference_2(function):
    function.devices = {}
    elem = indiXML.DefSwitch("defSwitch", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.DefSwitchVector("defSwitch", [elem], {"device": "test"}, None)
    dev, name = function._getDeviceReference(chunk=chunk)
    assert dev == function.devices["test"]
    assert name == "test"


def test_delProperty_1(function):
    function.devices = {}
    elem = indiXML.DefSwitch("defSwitch", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.DefSwitchVector("defSwitch", [elem], {"device": "test"}, None)
    suc = function._delProperty(chunk=chunk, deviceName="test")
    assert not suc


def test_delProperty_2(function):
    function.devices = {"test": Device()}
    elem = indiXML.DefSwitch("defSwitch", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.DefSwitchVector("defSwitch", [elem], {"test": "test"}, None)
    suc = function._delProperty(chunk=chunk, deviceName="test")
    assert not suc


def test_delProperty_3(function):
    function.devices = {"test": Device(name="test")}
    function.devices["test"].test = None
    elem = indiXML.DefSwitch("defSwitch", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.DefSwitchVector("defSwitch", [elem], {"name": "test"}, None)
    suc = function._delProperty(chunk=chunk, device=function.devices["test"], deviceName="test")
    assert suc


def test_setProperty_1(function):
    function.devices = {"test": Device(name="test")}
    function.devices["test"].test = None
    elem = indiXML.DefBLOB("defBLOB", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.SetBLOBVector("defBLOB", [elem], {"name": "test"}, None)
    with mock.patch.object(function, "_setupPropertyStructure", return_value=("test", "test")):
        with mock.patch.object(function, "_fillAttributes"):
            suc = function._setProperty(
                chunk=chunk, device=function.devices["test"], deviceName="test"
            )
            assert suc


def test_setProperty_2(function):
    function.devices = {"test": Device(name="test")}
    function.devices["test"].test = None
    elem = indiXML.DefSwitch("defSwitch", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.SetSwitchVector("defSwitch", [elem], {"name": "test"}, None)
    with mock.patch.object(function, "_setupPropertyStructure", return_value=("test", "test")):
        with mock.patch.object(function, "_fillAttributes"):
            suc = function._setProperty(
                chunk=chunk, device=function.devices["test"], deviceName="test"
            )
            assert suc


def test_setProperty_3(function):
    function.devices = {"test": Device(name="test")}
    function.devices["test"].test = None
    elem = indiXML.DefNumber("defNumber", 1, {"name": "DISCONNECT"}, None)
    chunk = indiXML.SetNumberVector("defNumber", [elem], {"name": "test"}, None)
    with mock.patch.object(function, "_setupPropertyStructure", return_value=("test", "test")):
        with mock.patch.object(function, "_fillAttributes"):
            suc = function._setProperty(
                chunk=chunk, device=function.devices["test"], deviceName="test"
            )
            assert suc


def test_setProperty_4(function):
    function.devices = {"test": Device(name="test")}
    function.devices["test"].test = None
    elem = indiXML.DefText("defText", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.SetTextVector("defText", [elem], {"name": "test"}, None)
    with mock.patch.object(function, "_setupPropertyStructure", return_value=("test", "test")):
        with mock.patch.object(function, "_fillAttributes"):
            suc = function._setProperty(
                chunk=chunk, device=function.devices["test"], deviceName="test"
            )
            assert suc


def test_setProperty_5(function):
    function.devices = {"test": Device(name="test")}
    function.devices["test"].test = None
    elem = indiXML.DefText("defText", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.SetLightVector("defText", [elem], {"name": "test"}, None)
    with mock.patch.object(function, "_setupPropertyStructure", return_value=("test", "test")):
        with mock.patch.object(function, "_fillAttributes"):
            suc = function._setProperty(
                chunk=chunk, device=function.devices["test"], deviceName="test"
            )
            assert suc


def test_defProperty_1(function):
    function.devices = {"test": Device(name="test")}
    function.devices["test"].test = None
    elem = indiXML.DefBLOB("defBLOB", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.DefBLOBVector("defBLOB", [elem], {"name": "test"}, None)
    with mock.patch.object(function, "_setupPropertyStructure", return_value=("test", "test")):
        with mock.patch.object(function, "_fillAttributes"):
            suc = function._defProperty(
                chunk=chunk, device=function.devices["test"], deviceName="test"
            )
            assert suc


def test_defProperty_2(function):
    function.devices = {"test": Device(name="test")}
    function.devices["test"].test = None
    elem = indiXML.DefSwitch("defSwitch", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.DefSwitchVector("defSwitch", [elem], {"name": "test"}, None)
    with mock.patch.object(function, "_setupPropertyStructure", return_value=("test", "test")):
        with mock.patch.object(function, "_fillAttributes"):
            suc = function._defProperty(
                chunk=chunk, device=function.devices["test"], deviceName="test"
            )
            assert suc


def test_defProperty_3(function):
    function.devices = {"test": Device(name="test")}
    function.devices["test"].test = None
    elem = indiXML.DefNumber("defNumber", 1, {"name": "DISCONNECT"}, None)
    chunk = indiXML.DefNumberVector("defNumber", [elem], {"name": "test"}, None)
    with mock.patch.object(function, "_setupPropertyStructure", return_value=("test", "test")):
        with mock.patch.object(function, "_fillAttributes"):
            suc = function._defProperty(
                chunk=chunk, device=function.devices["test"], deviceName="test"
            )
            assert suc


def test_defProperty_4(function):
    function.devices = {"test": Device(name="test")}
    function.devices["test"].test = None
    elem = indiXML.DefText("defText", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.DefTextVector("defText", [elem], {"name": "test"}, None)
    with mock.patch.object(function, "_setupPropertyStructure", return_value=("test", "test")):
        with mock.patch.object(function, "_fillAttributes"):
            suc = function._defProperty(
                chunk=chunk, device=function.devices["test"], deviceName="test"
            )
            assert suc


def test_defProperty_5(function):
    function.devices = {"test": Device(name="test")}
    function.devices["test"].test = None
    elem = indiXML.DefLight("defLight", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.DefLightVector("defLight", [elem], {"name": "test"}, None)
    with mock.patch.object(function, "_setupPropertyStructure", return_value=("test", "test")):
        with mock.patch.object(function, "_fillAttributes"):
            suc = function._defProperty(
                chunk=chunk, device=function.devices["test"], deviceName="test"
            )
            assert suc


def test_getProperty(function):
    suc = function._getProperty(device=Device(name="test"))
    assert suc


def test_message(function):
    elem = indiXML.DefLight("defLight", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.DefLightVector("defLight", [elem], {"name": "test"}, None)
    suc = function._message(chunk=chunk)
    assert suc


def test_parseCmd_1(function):
    elem = indiXML.DefLight("defLight", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.DefLightVector("defLight", [elem], {"name": "test"}, None)

    function.connected = False
    suc = function._parseCmd(chunk=chunk)
    assert not suc


def test_parseCmd_2(function):
    elem = indiXML.DefLight("defLight", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.DefLightVector("defLight", [elem], {"test": "test"}, None)

    function.connected = True
    suc = function._parseCmd(chunk=chunk)
    assert not suc


def test_parseCmd_3(function):
    elem = indiXML.DefLight("defLight", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.Message("defLight", [elem], {"device": "test"}, None)

    function.connected = True
    suc = function._parseCmd(chunk=chunk)
    assert suc


def test_parseCmd_40(function):
    elem = indiXML.DefLight("defLight", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.SetLightVector("defLight", [elem], {"device": "test"}, None)

    function.connected = True
    with mock.patch.object(function, "_setProperty"):
        suc = function._parseCmd(chunk=chunk)
        assert not suc


def test_parseCmd_4_0(function):
    elem = indiXML.DefLight("defLight", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.DelProperty("defLight", [elem], {"device": "test", "name": "test"}, None)

    function.connected = True
    with mock.patch.object(function, "_setProperty"):
        suc = function._parseCmd(chunk=chunk)
        assert suc


def test_parseCmd_4_1(function):
    elem = indiXML.DefLight("defLight", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.SetLightVector("defLight", [elem], {"device": "test", "name": "test"}, None)

    function.connected = True
    with mock.patch.object(function, "_setProperty"):
        suc = function._parseCmd(chunk=chunk)
        assert suc


def test_parseCmd_5(function):
    elem = indiXML.DefLight("defLight", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.DefLightVector("defLight", [elem], {"device": "test", "name": "test"}, None)

    function.connected = True
    with mock.patch.object(function, "_defProperty"):
        suc = function._parseCmd(chunk=chunk)
        assert suc


def test_parseCmd_6(function):
    elem = indiXML.DefLight("defLight", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.GetProperties("defLight", [elem], {"device": "test", "name": "test"}, None)

    function.connected = True
    with mock.patch.object(function, "_getProperty"):
        suc = function._parseCmd(chunk=chunk)
        assert suc


def test_parseCmd_7(function):
    elem = indiXML.DefLight("defLight", "On", {"name": "DISCONNECT"}, None)
    chunk = indiXML.NewSwitchVector("defLight", [elem], {"device": "test", "name": "test"}, None)

    function.connected = True
    suc = function._parseCmd(chunk=chunk)
    assert suc


def test_parseCmd_8(function):
    chunk = indiXML.OneText("defLight", "On", {"device": "test", "name": "DISCONNECT"}, None)

    function.connected = True
    suc = function._parseCmd(chunk=chunk)
    assert suc


def test_parseCmd_9(function):
    class Test:
        attr = {"name": "test", "device": "test"}

    function.connected = True
    suc = function._parseCmd(chunk=Test())
    assert not suc


def test_handleReadyRead_1(function):
    function.curDepth = 0
    elem = ""
    with mock.patch.object(function.socket, "readAll"):
        with mock.patch.object(function.parser, "feed"):
            with mock.patch.object(function.parser, "read_events", side_effect=Exception):
                suc = function.handleReadyRead()
                assert not suc
                assert function.curDepth == 0


def test_handleReadyRead_2(function):
    function.curDepth = 0
    elem = ""
    with mock.patch.object(function.socket, "readAll"):
        with mock.patch.object(function.parser, "feed"):
            with mock.patch.object(function.parser, "read_events", return_value=[("end", elem)]):
                suc = function.handleReadyRead()
                assert suc
                assert function.curDepth == -1


def test_handleReadyRead_3(function):
    function.curDepth = 0
    elem = ""
    with mock.patch.object(function.socket, "readAll"):
        with mock.patch.object(function.parser, "feed"):
            with mock.patch.object(function.parser, "read_events", return_value=[("start", elem)]):
                suc = function.handleReadyRead()
                assert suc
                assert function.curDepth == 1


def test_handleReadyRead_4(function):
    function.curDepth = 0
    elem = ""
    with mock.patch.object(function.socket, "readAll"):
        with mock.patch.object(function.parser, "feed"):
            with mock.patch.object(function.parser, "read_events", return_value=[("test", elem)]):
                suc = function.handleReadyRead()
                assert suc
                assert function.curDepth == 0


def test_handleReadyRead_5(function):
    class Test:
        @staticmethod
        def clear():
            return

    function.curDepth = -1
    elem = Test()
    with mock.patch.object(function.socket, "readAll"):
        with mock.patch.object(function.parser, "feed"):
            with mock.patch.object(function.parser, "read_events", return_value=[("start", elem)]):
                with mock.patch.object(function, "_parseCmd"):
                    with mock.patch.object(indiXML, "parseETree"):
                        suc = function.handleReadyRead()
                        assert suc
                        assert function.curDepth == 0


def test_handleConnected(function):
    function.connected = True
    suc = function.handleConnected()
    assert suc
    assert function.connected


def test_handleDisconnected(function):
    function.connected = True
    suc = function.handleDisconnected()
    assert suc
    assert not function.connected


def test_handleError_1(function):
    function.connected = True
    with mock.patch.object(function, "disconnectServer"):
        suc = function.handleError("")
        assert suc
