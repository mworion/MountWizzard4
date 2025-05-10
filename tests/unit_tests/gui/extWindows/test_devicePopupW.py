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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import logging
from pathlib import Path

# external packages
from PySide6.QtWidgets import QWidget

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidget import MWidget
from gui.extWindows.devicePopupW import DevicePopup
from base.indiClass import IndiClass
from base.ascomClass import AscomClass



@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    data = {
        "framework": "indi",
        "frameworks": {"indi": {"deviceName": "test", "deviceList": ["1", "2"]}},
    }
    widget = QWidget()
    with mock.patch.object(DevicePopup, "show"):
        window = DevicePopup(
            widget, app=App(), data=data, driver="telescope", deviceType="telescope"
        )
        window.log = logging.getLogger()
        yield window
        window.app.threadPool.waitForDone(10000)
        del window


def test_initConfig_1(function):
    with mock.patch.object(function, "populateTabs"):
        with mock.patch.object(function, "selectTabs"):
            function.initConfig()


def test_initConfig_2(function):
    function.data = {
        "framework": "astap",
        "frameworks": {
            "astap": {
                "deviceName": "telescope",
                "deviceList": ["telescope", "test2"],
            }
        },
    }
    with mock.patch.object(function, "checkApp"):
        with mock.patch.object(function, "checkIndex"):
            with mock.patch.object(function, "populateTabs"):
                with mock.patch.object(function, "selectTabs"):
                    function.initConfig()


def test_storeConfig_1(function):
    with mock.patch.object(function, "readFramework"):
        with mock.patch.object(function, "readTabs"):
            with mock.patch.object(function, "close"):
                function.storeConfig()


def test_selectTabs_1(function):
    function.data = {
        "framework": "",
        "frameworks": {
            "astap": {
                "test": 1,
            }
        },
    }
    function.selectTabs()


def test_selectTabs_2(function):
    function.data = {
        "framework": "astap",
        "frameworks": {
            "astap": {
                "test": 1,
            }
        },
    }
    function.selectTabs()


def test_selectTabs_3(function):
    function.data = {
        "framework": "test",
        "frameworks": {
            "test": {
                "test": 1,
            }
        },
    }
    function.selectTabs()


def test_populateTabs_1(function):
    function.data = {
        "framework": "indi",
        "frameworks": {
            "indi": {
                "deviceName": "test",
                "deviceList": ["test", "test1"],
                "updateRate": 30,
                "hostaddress": "test",
                "messages": True,
            },
        },
    }
    function.populateTabs()


def test_readTabs_1(function):
    function.data = {
        "framework": "indi",
        "frameworks": {
            "indi": {
                "deviceName": "astap",
                "deviceList": ["test", "test1"],
                "updateRate": 30.0,
                "hostaddress": "test",
                "messages": True,
                "port": 10,
            },
        },
    }
    function.readTabs()


def test_readFramework_1(function):
    function.readFramework()


def test_updateDeviceNameList_1(function):
    function.updateDeviceNameList("indi", ["test1", "test2"])


def test_discoverDevices_1(function):
    with mock.patch.object(IndiClass, "discoverDevices", return_value=()):
        function.discoverDevices('indi', QWidget())


def test_discoverDevices_2(function):
    with mock.patch.object(IndiClass, "discoverDevices", return_value=("Test1", "Test2")):
        function.discoverDevices('indi', QWidget())


def test_checkApp_1(function):
    class Avail:
        @staticmethod
        def checkAvailabilityProgram(appPath):
            return True

    function.app.plateSolve.run["astap"] = Avail()
    function.checkApp("astap", "test")


def test_checkApp_2(function):
    class Avail:
        @staticmethod
        def checkAvailabilityProgram(appPath):
            return True

    function.app.plateSolve.run["watney"] = Avail()
    function.checkApp("watney", "test")


def test_checkApp_3(function):
    class Avail:
        @staticmethod
        def checkAvailabilityProgram(appPath):
            return True

    function.app.plateSolve.run["astrometry"] = Avail()
    function.checkApp("astrometry", "test")


def test_checkIndex_1(function):
    class Avail:
        @staticmethod
        def checkAvailabilityIndex(indexPath):
            return True

    function.app.plateSolve.run["astap"] = Avail()
    function.checkIndex("astap", "test")


def test_checkIndex_2(function):
    class Avail:
        @staticmethod
        def checkAvailabilityIndex(indexPath):
            return True

    function.app.plateSolve.run["watney"] = Avail()
    function.checkIndex("watney", "test")


def test_checkIndex_3(function):
    class Avail:
        @staticmethod
        def checkAvailabilityIndex(indexPath):
            return True

    function.app.plateSolve.run["astrometry"] = Avail()
    function.checkIndex("astrometry", "test")


def test_selectAppPath_1(function):
    class Avail:
        @staticmethod
        def checkAvailabilityProgram(indexPath):
            return True

    function.app.plateSolve.run["astrometry"] = Avail()
    with mock.patch.object(MWidget, "openDir", return_value=Path("/test")):
        with mock.patch.object(Path, "is_dir", return_value=False):
            function.selectAppPath('astap')


def test_selectAppPath_2(function):
    class Avail:
        @staticmethod
        def checkAvailabilityProgram(appPath):
            return True

    function.app.plateSolve.run["astap"] = Avail()
    with mock.patch.object(MWidget, "openDir", return_value=Path("/test.app")):
        with mock.patch.object(Path, "is_dir", return_value=True):
            function.selectAppPath('astap')


def test_selectAppPath_3(function):
    class Avail:
        @staticmethod
        def checkAvailabilityProgram(appPath):
            return True

    function.app.plateSolve.run["astap"] = Avail()
    with mock.patch.object(MWidget, "openDir", return_value=Path("/Astrometry.app")):
        with mock.patch.object(Path, "is_dir", return_value=True):
            function.selectAppPath('astap')


def test_selectIndexPath_1(function):
    class Avail:
        @staticmethod
        def checkAvailabilityIndex(indexPath):
            return True

    function.app.plateSolve.run["astap"] = Avail()
    with mock.patch.object(MWidget, "openDir", return_value=Path("/test")):
        with mock.patch.object(Path, "is_dir", return_value=False):
            function.selectIndexPath('astap')


def test_selectIndexPath_2(function):
    class Avail:
        @staticmethod
        def checkAvailabilityIndex(indexPath):
            return True

    function.app.plateSolve.run = {"astap": Avail()}
    with mock.patch.object(MWidget, "openDir", return_value=Path("/test")):
        with mock.patch.object(Path, "is_dir", return_value=True):
            function.selectIndexPath('astap')


def test_selectAscomDriver_1(function):
    with mock.patch.object(AscomClass, "selectAscomDriver", return_value="test"):
        function.selectAscomDriver()
        assert function.ui.ascomDevice.text() == "test"
