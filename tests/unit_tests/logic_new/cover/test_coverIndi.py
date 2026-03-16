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
# Licence APL2.0
#
###########################################################

import pytest
import unittest.mock as mock
from mw4.base.signalsDevices import Signals
from mw4.indibase.indiClient import Client
from mw4.indibase.indiDevice import Device
from mw4.logic.cover.coverIndi import CoverIndi
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Parent:
    app = App()
    data = {}
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="function")
def function():
    func = CoverIndi(parent=Parent())
    yield func


def test_setUpdateConfig_1(function):
    function.deviceName = ""
    function.loadConfig = True
    function.updateRate = 1000
    function.setUpdateConfig("test")


def test_setUpdateConfig_2(function):
    function.deviceName = "test"
    function.loadConfig = True
    function.updateRate = 1000
    function.device = None
    function.setUpdateConfig("test")


def test_setUpdateConfig_3(function):
    function.deviceName = "test"
    function.loadConfig = True
    function.updateRate = 1000
    function.device = Device()
    with mock.patch.object(function.device, "getNumber", return_value={"Test": 1}):
        function.setUpdateConfig("test")


def test_setUpdateConfig_4(function):
    function.deviceName = "test"
    function.device = Device()
    function.client = Client()
    function.loadConfig = True
    function.updateRate = 1000
    with mock.patch.object(function.device, "getNumber", return_value={"PERIOD": 1}):
        with mock.patch.object(function.client, "sendNewNumber", return_value=False):
            function.setUpdateConfig("test")


def test_setUpdateConfig_5(function):
    function.deviceName = "test"
    function.device = Device()
    function.client = Client()
    function.loadConfig = True
    function.updateRate = 1000
    with mock.patch.object(function.device, "getNumber", return_value={"PERIOD": 1}):
        with mock.patch.object(function.client, "sendNewNumber", return_value=True):
            function.setUpdateConfig("test")


def test_updateText_2(function):
    function.device = Device()
    function.deviceName = "test"
    with mock.patch.object(function.device, "getText", return_value={"Cover": "OPEN"}):
        function.updateText("test", "CAP_PARK")


def test_updateText_3(function):
    function.device = Device()
    function.deviceName = "test"
    with mock.patch.object(function.device, "getText", return_value={"Cover": "CLOSED"}):
        function.updateText("test", "CAP_PARK")


def test_updateText_4(function):
    function.device = Device()
    function.deviceName = "test"
    with mock.patch.object(function.device, "getText", return_value={"Cover": "test"}):
        function.updateText("test", "CAP_PARK")


def test_closeCover_1(function):
    function.deviceName = "test"
    function.device = None
    function.closeCover()


def test_closeCover_2(function):
    function.deviceName = "test"
    function.device = Device()
    with mock.patch.object(function.device, "getSwitch", return_value={"Test": 1}):
        function.closeCover()


def test_closeCover_3(function):
    function.deviceName = "test"
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(
        function.device, "getSwitch", return_value={"PARK": "On", "UNPARK": "Off"}
    ):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=False):
            function.closeCover()


def test_closeCover_4(function):
    function.deviceName = "test"
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(
        function.device, "getSwitch", return_value={"PARK": "On", "": "Off"}
    ):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=False):
            function.closeCover()


def test_closeCover_5(function):
    function.deviceName = "test"
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(
        function.device, "getSwitch", return_value={"PARK": "Off", "UNPARK": "On"}
    ):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=True):
            function.closeCover()


def test_openCover_1(function):
    function.deviceName = "test"
    function.device = None
    function.openCover()


def test_openCover_2(function):
    function.deviceName = "test"
    function.device = Device()
    with mock.patch.object(function.device, "getSwitch", return_value={"Test": 1}):
        function.openCover()


def test_openCover_3(function):
    function.deviceName = "test"
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(
        function.device, "getSwitch", return_value={"PARK": "On", "UNPARK": "Off"}
    ):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=False):
            function.openCover()


def test_openCover_4(function):
    function.deviceName = "test"
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(
        function.device, "getSwitch", return_value={"PARK": "On", "": "Off"}
    ):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=False):
            function.openCover()


def test_openCover_5(function):
    function.deviceName = "test"
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(
        function.device, "getSwitch", return_value={"PARK": "Off", "UNPARK": "On"}
    ):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=True):
            function.openCover()


def test_haltCover_1(function):
    function.deviceName = "test"
    function.device = None
    function.haltCover()


def test_lightOn_1(function):
    function.deviceName = "test"
    function.device = None
    function.lightOn()


def test_lightOn_2(function):
    function.deviceName = "test"
    function.device = Device()
    with mock.patch.object(function.device, "getSwitch", return_value={"Test": 1}):
        function.lightOn()


def test_lightOn_3(function):
    function.deviceName = "test"
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(
        function.device,
        "getSwitch",
        return_value={"FLAT_LIGHT_ON": "On", "FLAT_LIGHT_OFF": "Off"},
    ):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=False):
            function.lightOn()


def test_lightOn_4(function):
    function.deviceName = "test"
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(
        function.device, "getSwitch", return_value={"FLAT_LIGHT_ON": "On", "": "Off"}
    ):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=False):
            function.lightOn()


def test_lightOn_5(function):
    function.deviceName = "test"
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(
        function.device,
        "getSwitch",
        return_value={"FLAT_LIGHT_ON": "Off", "FLAT_LIGHT_OFF": "On"},
    ):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=True):
            function.lightOn()


def test_lightOff_1(function):
    function.deviceName = "test"
    function.device = None
    function.lightOff()


def test_lightOff_2(function):
    function.deviceName = "test"
    function.device = Device()
    with mock.patch.object(function.device, "getSwitch", return_value={"Test": 1}):
        function.lightOff()


def test_lightOff_3(function):
    function.deviceName = "test"
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(
        function.device,
        "getSwitch",
        return_value={"FLAT_LIGHT_ON": "Off", "FLAT_LIGHT_OFF": "On"},
    ):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=False):
            function.lightOff()


def test_lightOff_4(function):
    function.deviceName = "test"
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(
        function.device, "getSwitch", return_value={"FLAT_LIGHT_OFF": "On", "": "Off"}
    ):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=False):
            function.lightOff()


def test_lightOff_5(function):
    function.deviceName = "test"
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(
        function.device,
        "getSwitch",
        return_value={"FLAT_LIGHT_ON": "On", "FLAT_LIGHT_OFF": "Off"},
    ):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=True):
            function.lightOff()


def test_lightIntensity_1(function):
    function.deviceName = "test"
    function.device = None
    function.lightIntensity(1)


def test_lightIntensity_2(function):
    function.deviceName = "test"
    function.device = Device()
    with mock.patch.object(function.device, "getNumber", return_value={"Test": 1}):
        function.lightIntensity(1)


def test_lightIntensity_3(function):
    function.deviceName = "test"
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(
        function.device, "getNumber", return_value={"FLAT_LIGHT_INTENSITY_VALUE": 128}
    ):
        with mock.patch.object(function.client, "sendNewNumber", return_value=False):
            function.lightIntensity(1)


def test_lightIntensity_4(function):
    function.deviceName = "test"
    function.device = Device()
    function.client = Client()
    function.UPDATE_RATE = 0
    with mock.patch.object(
        function.device, "getNumber", return_value={"FLAT_LIGHT_INTENSITY_VALUE": 128}
    ):
        with mock.patch.object(function.client, "sendNewNumber", return_value=True):
            function.lightIntensity(1)
