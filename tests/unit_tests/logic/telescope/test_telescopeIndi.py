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
# standard libraries
import unittest.mock as mock

import pytest

from mw4.base.signalsDevices import Signals
from mw4.indibase.indiClient import Client

# external packages
from mw4.indibase.indiDevice import Device
from mw4.logic.telescope.telescopeIndi import TelescopeIndi

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Parent:
    app = App()
    data = {}
    signals = Signals()
    loadConfig = True
    updateRate = 1000


@pytest.fixture(autouse=True, scope="function")
def function():
    func = TelescopeIndi(parent=Parent())
    yield func


def test_setUpdateConfig_1(function):
    function.loadConfig = True
    function.updateRate = 1000
    function.deviceName = ""
    function.setUpdateConfig("test")


def test_setUpdateConfig_2(function):
    function.loadConfig = True
    function.updateRate = 1000
    function.deviceName = "test"
    function.device = None
    function.setUpdateConfig("test")


def test_setUpdateConfig_3(function):
    function.loadConfig = True
    function.updateRate = 1000
    function.deviceName = "test"
    function.device = Device()
    with mock.patch.object(function.device, "getNumber", return_value={"Test": 1}):
        function.setUpdateConfig("test")


def test_setUpdateConfig_4(function):
    function.loadConfig = True
    function.updateRate = 1000
    function.deviceName = "test"
    function.device = Device()
    function.client = Client()
    with mock.patch.object(function.device, "getNumber", return_value={"PERIOD": 1}):
        with mock.patch.object(function.client, "sendNewNumber", return_value=False):
            function.setUpdateConfig("test")


def test_setUpdateConfig_5(function):
    function.loadConfig = True
    function.updateRate = 1000
    function.deviceName = "test"
    function.device = Device()
    function.client = Client()
    with mock.patch.object(function.device, "getNumber", return_value={"PERIOD": 1}):
        with mock.patch.object(function.client, "sendNewNumber", return_value=True):
            function.setUpdateConfig("test")
