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

# external packages
from indibase.indiDevice import Device
from indibase.indiClient import Client

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.dome.domeIndi import DomeIndi
from base.signalsDevices import Signals


@pytest.fixture(autouse=True, scope="function")
def function():
    func = DomeIndi(app=App(), signals=Signals(), data={})
    yield func


def test_setUpdateConfig_1(function):
    function.deviceName = ""
    function.loadConfig = True
    function.updateRate = 1000
    function.setUpdateConfig("test")


def test_setUpdateConfig_2(function):
    function.deviceName = "test"
    function.device = None
    function.loadConfig = True
    function.updateRate = 1000
    function.setUpdateConfig("test")


def test_setUpdateConfig_3(function):
    function.deviceName = "test"
    function.device = Device()
    function.loadConfig = True
    function.updateRate = 1000
    with mock.patch.object(function.device, "getNumber", return_value={"Test": 1}):
        function.setUpdateConfig("test")


def test_setUpdateConfig_4(function):
    function.deviceName = "test"
    function.device = Device()
    function.client = Client()
    function.loadConfig = True
    function.updateRate = 1000
    with mock.patch.object(function.device, "getNumber", return_value={"PERIOD_MS": 1}):
        with mock.patch.object(function.client, "sendNewNumber", return_value=False):
            function.setUpdateConfig("test")


def test_setUpdateConfig_5(function):
    function.deviceName = "test"
    function.device = Device()
    function.client = Client()
    function.loadConfig = True
    function.updateRate = 1000
    with mock.patch.object(function.device, "getNumber", return_value={"PERIOD_MS": 1}):
        with mock.patch.object(function.client, "sendNewNumber", return_value=True):
            function.setUpdateConfig("test")


def test_updateStatus_1(function):
    function.device = Device()
    function.client = Client()
    function.client.connected = False

    function.updateStatus()


def test_updateStatus_2(function):
    function.device = Device()
    function.client = Client()
    function.client.connected = True

    function.updateStatus()


def test_updateNumber_2(function):
    function.device = Device()
    function.deviceName = "test"
    setattr(function.device, "ABS_DOME_POSITION", {"state": "Busy"})
    with mock.patch.object(
        function.device,
        "getNumber",
        return_value={"TEST": 1, "DOME_ABSOLUTE_POSITION": 2},
    ):
        function.updateNumber("test", "ABS_DOME_POSITION")


def test_updateNumber_3(function):
    function.device = Device()
    function.deviceName = "test"
    setattr(function.device, "DOME_SHUTTER", {"state": "Busy"})
    with mock.patch.object(
        function.device, "getNumber", return_value={"TEST": 1, "SHUTTER_OPEN": 2}
    ):
        function.updateNumber("test", "SHUTTER_OPEN")


def test_updateNumber_4(function):
    function.device = Device()
    function.deviceName = "test"
    setattr(function.device, "DOME_SHUTTER", {"state": "test"})
    with mock.patch.object(
        function.device, "getNumber", return_value={"TEST": 1, "SHUTTER_OPEN": 2}
    ):
        function.updateNumber("test", "SHUTTER_OPEN")


def test_slewToAltAz_1(function):
    function.slewToAltAz(azimuth=0, altitude=0)


def test_slewToAltAz_2(function):
    function.device = Device()
    function.slewToAltAz(azimuth=0, altitude=0)


def test_slewToAltAz_3(function):
    function.device = Device()
    function.deviceName = "test"
    function.slewToAltAz(azimuth=0, altitude=0)


def test_slewToAltAz_4(function):
    function.device = Device()
    function.deviceName = "test"

    with mock.patch.object(
        function.device, "getNumber", return_value={"DOME_ABSOLUTE_POSITION": 1}
    ):
        function.slewToAltAz(azimuth=0, altitude=0)


def test_slewToAltAz_5(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = "test"

    with mock.patch.object(
        function.device, "getNumber", return_value={"DOME_ABSOLUTE_POSITION": 1}
    ):
        with mock.patch.object(function.client, "sendNewNumber", return_value=False):
            function.slewToAltAz(azimuth=0, altitude=0)


def test_slewToAltAz_6(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = "test"

    with mock.patch.object(
        function.device, "getNumber", return_value={"DOME_ABSOLUTE_POSITION": 1}
    ):
        with mock.patch.object(function.client, "sendNewNumber", return_value=True):
            function.slewToAltAz(azimuth=0, altitude=0)


def test_openShutter_1(function):
    function.openShutter()


def test_openShutter_2(function):
    function.device = Device()
    function.openShutter()


def test_openShutter_3(function):
    function.device = Device()
    function.deviceName = "test"
    function.openShutter()


def test_openShutter_4(function):
    function.device = Device()
    function.deviceName = "test"

    with mock.patch.object(function.device, "getSwitch", return_value={"SHUTTER_OPEN": 1}):
        function.openShutter()


def test_openShutter_5(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = "test"

    with mock.patch.object(function.device, "getSwitch", return_value={"SHUTTER_OPEN": 1}):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=False):
            function.openShutter()


def test_openShutter_6(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = "test"

    with mock.patch.object(function.device, "getSwitch", return_value={"SHUTTER_OPEN": 1}):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=True):
            function.openShutter()


def test_closeShutter_1(function):
    function.closeShutter()


def test_closeShutter_2(function):
    function.device = Device()
    function.closeShutter()


def test_closeShutter_3(function):
    function.device = Device()
    function.deviceName = "test"
    function.closeShutter()


def test_closeShutter_4(function):
    function.device = Device()
    function.deviceName = "test"

    with mock.patch.object(function.device, "getSwitch", return_value={"SHUTTER_CLOSE": 1}):
        function.closeShutter()


def test_closeShutter_5(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = "test"

    with mock.patch.object(function.device, "getSwitch", return_value={"SHUTTER_CLOSE": 1}):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=False):
            function.closeShutter()


def test_closeShutter_6(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = "test"

    with mock.patch.object(function.device, "getSwitch", return_value={"SHUTTER_CLOSE": 1}):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=True):
            function.closeShutter()


def test_slewCW_1(function):
    function.slewCW()


def test_slewCW_2(function):
    function.device = Device()
    function.slewCW()


def test_slewCW_3(function):
    function.device = Device()
    function.deviceName = "test"
    function.slewCW()


def test_slewCW_4(function):
    function.device = Device()
    function.deviceName = "test"

    with mock.patch.object(function.device, "getSwitch", return_value={"DOME_CW": 1}):
        function.slewCW()


def test_slewCW_5(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = "test"

    with mock.patch.object(function.device, "getSwitch", return_value={"DOME_CW": 1}):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=False):
            function.slewCW()


def test_slewCW_6(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = "test"

    with mock.patch.object(function.device, "getSwitch", return_value={"DOME_CW": 1}):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=True):
            function.slewCW()


def test_slewCCW_1(function):
    function.slewCCW()


def test_slewCCW_2(function):
    function.device = Device()
    function.slewCCW()


def test_slewCCW_3(function):
    function.device = Device()
    function.deviceName = "test"
    function.slewCCW()


def test_slewCCW_4(function):
    function.device = Device()
    function.deviceName = "test"

    with mock.patch.object(function.device, "getSwitch", return_value={"DOME_CW": 1}):
        function.slewCCW()


def test_slewCCW_5(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = "test"

    with mock.patch.object(function.device, "getSwitch", return_value={"DOME_CW": 1}):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=False):
            function.slewCCW()


def test_slewCCW_6(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = "test"

    with mock.patch.object(function.device, "getSwitch", return_value={"DOME_CW": 1}):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=True):
            function.slewCCW()


def test_abortSlew_1(function):
    function.abortSlew()


def test_abortSlew_2(function):
    function.device = Device()
    function.abortSlew()


def test_abortSlew_3(function):
    function.device = Device()
    function.deviceName = "test"
    function.abortSlew()


def test_abortSlew_4(function):
    function.device = Device()
    function.deviceName = "test"

    with mock.patch.object(function.device, "getSwitch", return_value={"ABORT": 1}):
        function.abortSlew()


def test_abortSlew_5(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = "test"

    with mock.patch.object(function.device, "getSwitch", return_value={"ABORT": 1}):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=False):
            function.abortSlew()


def test_abortSlew_6(function):
    function.device = Device()
    function.client = Client()
    function.deviceName = "test"

    with mock.patch.object(function.device, "getSwitch", return_value={"ABORT": 1}):
        with mock.patch.object(function.client, "sendNewSwitch", return_value=True):
            function.abortSlew()
