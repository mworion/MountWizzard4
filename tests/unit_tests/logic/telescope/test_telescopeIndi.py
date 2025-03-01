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
from logic.telescope.telescopeIndi import TelescopeIndi
from base.signalsDevices import Signals


@pytest.fixture(autouse=True, scope="function")
def function():
    func = TelescopeIndi(app=App(), signals=Signals(), data={})
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
