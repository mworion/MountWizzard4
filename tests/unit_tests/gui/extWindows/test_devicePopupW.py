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
import unittest.mock as mock
import pytest
import platform
import logging
from pathlib import Path

# external packages
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QWidget

if platform.system() == "Windows":
    import win32com.client


# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidget import MWidget
from gui.extWindows.devicePopupW import DevicePopup
from base.indiClass import IndiClass
from base.alpacaClass import AlpacaClass
from base.sgproClass import SGProClass
from base.ninaClass import NINAClass


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


def test_initConfig_1(function):
    function.initConfig()


def test_initConfig_2(function):
    function.data["framework"] = "astap"
    with mock.patch.object(function, "populateTabs"):
        with mock.patch.object(function, "selectTabs"):
            with mock.patch.object(function, "updatePlateSolverStatus"):
                function.initConfig()


def test_initConfig_3(function):
    function.data = {
        "framework": "indi",
        "frameworks": {
            "indi": {
                "deviceName": "telescope",
                "deviceList": ["telescope", "test2"],
            }
        },
    }
    function.initConfig()


def test_closeEvent_1(function):
    with mock.patch.object(function, "show"):
        with mock.patch.object(MWidget, "closeEvent"):
            function.closeEvent(QCloseEvent)


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
        "framework": "astap",
        "frameworks": {
            "astap": {
                "deviceName": "astap",
                "deviceList": ["test", "test1"],
                "searchRadius": 30,
                "appPath": "test",
            },
        },
    }
    function.populateTabs()


def test_populateTabs_2(function):
    function.data = {
        "framework": "indi",
        "frameworks": {
            "indi": {
                "deviceName": "astap",
                "deviceList": ["test", "test1"],
                "host": "test",
                "messages": True,
            }
        },
    }
    function.populateTabs()


def test_readTabs_1(function):
    function.data = {
        "framework": "astap",
        "frameworks": {
            "astap": {
                "deviceName": "astap",
                "deviceList": ["test", "test1"],
                "searchRadius": 30,
                "appPath": "test",
            },
        },
    }
    function.readTabs()


def test_readTabs_2(function):
    function.framework2gui["astap"]["appPath"].setText("100")
    function.data = {
        "framework": "astap",
        "frameworks": {
            "astap": {
                "deviceName": "astap",
                "deviceList": ["test", "test1"],
                "searchRadius": 30,
                "appPath": 100,
            },
        },
    }
    function.readTabs()


def test_readTabs_3(function):
    function.framework2gui["astap"]["appPath"].setText("100")
    function.data = {
        "framework": "astap",
        "frameworks": {
            "astap": {
                "deviceName": "astap",
                "deviceList": ["test", "test1"],
                "searchRadius": 30,
                "appPath": 100.0,
            },
        },
    }
    function.readTabs()


def test_readTabs_4(function):
    function.data = {
        "framework": "indi",
        "frameworks": {
            "indi": {
                "deviceName": "astap",
                "deviceList": ["test", "test1"],
                "host": "test",
                "messages": True,
            }
        },
    }
    function.readTabs()


def test_readFramework_1(function):
    function.readFramework()


def test_storeConfig_1(function):
    with mock.patch.object(function, "readFramework"):
        with mock.patch.object(function, "readTabs"):
            with mock.patch.object(function, "close"):
                function.storeConfig()


def test_updateIndiDeviceNameList_1(function):
    function.updateIndiDeviceNameList(["test1", "test2"])


def test_discoverIndiDevices_1(function):
    with mock.patch.object(IndiClass, "discoverDevices", return_value=()):
        function.discoverIndiDevices()


def test_discoverIndiDevices_2(function):
    with mock.patch.object(IndiClass, "discoverDevices", return_value=("Test1", "Test2")):
        function.discoverIndiDevices()


def test_updateAlpacaDeviceNameList_1(function):
    with mock.patch.object(function.ui.alpacaDeviceList, "clear"):
        with mock.patch.object(function.ui.alpacaDeviceList, "setView"):
            function.updateAlpacaDeviceNameList(["test1", "test2"])


def test_discoverAlpacaDevices_1(function):
    with mock.patch.object(AlpacaClass, "discoverDevices", return_value=()):
        function.discoverAlpacaDevices()


def test_discoverAlpacaDevices_2(function):
    with mock.patch.object(AlpacaClass, "discoverDevices", return_value=("Test1", "Test2")):
        function.discoverAlpacaDevices()


def test_updateSGProDeviceNameList_1(function):
    with mock.patch.object(function.ui.sgproDeviceList, "clear"):
        with mock.patch.object(function.ui.sgproDeviceList, "setView"):
            function.updateSGProDeviceNameList(["test1", "test2"])


def test_discoverSGProDevices_1(function):
    with mock.patch.object(SGProClass, "discoverDevices", return_value=[]):
        function.discoverSGProDevices()


def test_discoverSGProDevices_2(function):
    with mock.patch.object(SGProClass, "discoverDevices", return_value=["Test1", "Test2"]):
        function.discoverSGProDevices()


def test_updateNINADeviceNameList_1(function):
    with mock.patch.object(function.ui.ninaDeviceList, "clear"):
        with mock.patch.object(function.ui.ninaDeviceList, "setView"):
            function.updateNINADeviceNameList(["test1", "test2"])


def test_discoverNINADevices_1(function):
    with mock.patch.object(NINAClass, "discoverDevices", return_value=[]):
        function.discoverNINADevices()


def test_discoverNINADevices_2(function):
    with mock.patch.object(NINAClass, "discoverDevices", return_value=["Test1", "Test2"]):
        function.discoverNINADevices()


def test_checkPlateSolveAvailability_1(function):
    class Avail:
        @staticmethod
        def checkAvailabilityProgram(appPath=Path()):
            return True

        @staticmethod
        def checkAvailabilityIndex(indexPath=Path()):
            return True

    function.app.plateSolve.run["astap"] = Avail()
    function.checkPlateSolveAvailability("astap", "test", "test")


def test_checkPlateSolveAvailability_2(function):
    class Avail:
        @staticmethod
        def checkAvailabilityProgram(appPath=0):
            return True

        @staticmethod
        def checkAvailabilityIndex(indexPath=0):
            return True

    function.app.plateSolve.run["watney"] = Avail()
    function.checkPlateSolveAvailability("watney", "test", "test")


def test_checkPlateSolveAvailability_3(function):
    class Avail:
        @staticmethod
        def checkAvailabilityProgram(appPath=0):
            return True

        @staticmethod
        def checkAvailabilityIndex(indexPath=0):
            return True

    function.app.plateSolve.run["astrometry"] = Avail()
    function.checkPlateSolveAvailability("astrometry", "test", "test")


def test_updatePlateSolverStatus(function):
    with mock.patch.object(function, "checkPlateSolveAvailability"):
        function.updatePlateSolverStatus()


def test_selectAstrometryAppPath_1(function):
    with mock.patch.object(MWidget, "openDir", return_value=Path("/test")):
        with mock.patch.object(Path, "is_dir", return_value=False):
            function.selectAstrometryAppPath()


def test_selectAstrometryAppPath_2(function):
    with mock.patch.object(MWidget, "openDir", return_value=Path("/test.app")):
        with mock.patch.object(Path, "is_dir", return_value=True):
            with mock.patch.object(platform, "system", return_value=("Darwin")):
                with mock.patch.object(function, "checkPlateSolveAvailability"):
                    function.selectAstrometryAppPath()


def test_selectAstrometryAppPath_3(function):
    with mock.patch.object(MWidget, "openDir", return_value=Path("/Astrometry.app")):
        with mock.patch.object(Path, "is_dir", return_value=True):
            with mock.patch.object(platform, "system", return_value=("Darwin")):
                with mock.patch.object(function, "checkPlateSolveAvailability"):
                    function.selectAstrometryAppPath()


def test_selectAstrometryIndexPath_1(function):
    with mock.patch.object(MWidget, "openDir", return_value=Path("/test")):
        with mock.patch.object(Path, "is_dir", return_value=False):
            function.selectAstrometryIndexPath()


def test_selectAstrometryIndexPath_2(function):
    class Avail:
        @staticmethod
        def checkAvailabilityProgram(appPath=Path()):
            return True

        @staticmethod
        def checkAvailabilityIndex(indexPath=Path()):
            return True

    function.app.plateSolve.run = {"astrometry": Avail()}
    with mock.patch.object(MWidget, "openDir", return_value=Path("/test")):
        with mock.patch.object(Path, "is_dir", return_value=True):
            with mock.patch.object(function, "checkPlateSolveAvailability"):
                function.selectAstrometryIndexPath()


def test_selectAstapAppPath_1(function):
    with mock.patch.object(MWidget, "openDir", return_value=Path("/test")):
        with mock.patch.object(Path, "is_dir", return_value=False):
            function.selectAstapAppPath()


def test_selectAstapAppPath_2(function):
    with mock.patch.object(MWidget, "openDir", return_value=Path("/test")):
        with mock.patch.object(Path, "is_dir", return_value=True):
            with mock.patch.object(function, "checkPlateSolveAvailability"):
                function.selectAstapAppPath()


def test_selectAstapAppPath_3(function):
    with mock.patch.object(MWidget, "openDir", return_value=Path("/Astap.app")):
        with mock.patch.object(Path, "is_dir", return_value=True):
            with mock.patch.object(platform, "system", return_value=("Darwin")):
                with mock.patch.object(
                    function, "checkPlateSolveAvailability", return_value=True
                ):
                    function.selectAstapAppPath()


def test_selectAstapIndexPath_1(function):
    with mock.patch.object(MWidget, "openDir", return_value=Path("/test")):
        with mock.patch.object(Path, "is_dir", return_value=False):
            with mock.patch.object(Path, "is_dir", return_value=False):
                function.selectAstapIndexPath()


def test_selectAstapIndexPath_2(function):
    class Avail:
        @staticmethod
        def checkAvailabilityProgram(appPath=Path()):
            return True

        @staticmethod
        def checkAvailabilityIndex(indexPath=Path()):
            return True

        @staticmethod
        def selectAstapIndexPath():
            return True

    function.app.plateSolve.run = {"astap": Avail()}
    with mock.patch.object(MWidget, "openDir", return_value=Path("/test")):
        with mock.patch.object(Path, "is_dir", return_value=True):
            with mock.patch.object(function, "checkPlateSolveAvailability", return_value=True):
                function.selectAstapIndexPath()


def test_selectWatneyAppPath_1(function):
    with mock.patch.object(MWidget, "openDir", return_value=Path("/test")):
        with mock.patch.object(Path, "is_dir", return_value=False):
            function.selectWatneyAppPath()


def test_selectWatneyAppPath_2(function):
    with mock.patch.object(MWidget, "openDir", return_value=Path("/test")):
        with mock.patch.object(Path, "is_dir", return_value=True):
            with mock.patch.object(function, "checkPlateSolveAvailability", return_value=True):
                function.selectWatneyAppPath()


def test_selectWatneyAppPath_3(function):
    with mock.patch.object(MWidget, "openDir", return_value=Path("test.app")):
        with mock.patch.object(Path, "is_dir", return_value=True):
            with mock.patch.object(platform, "system", return_value=("Darwin")):
                with mock.patch.object(
                    function, "checkPlateSolveAvailability", return_value=True
                ):
                    function.selectWatneyAppPath()


def test_selectWatneyIndexPath_1(function):
    with mock.patch.object(MWidget, "openDir", return_value=Path("/test")):
        with mock.patch.object(Path, "is_dir", return_value=False):
            function.selectWatneyIndexPath()


def test_selectWatneyIndexPath_2(function):
    class Avail:
        @staticmethod
        def checkAvailabilityProgram(appPath=Path()):
            return True

        @staticmethod
        def checkAvailabilityIxdex(indexPath=Path()):
            return True

        @staticmethod
        def selectWatneyIndexPath():
            return True

    function.app.plateSolve.run = {"astap": Avail()}
    with mock.patch.object(MWidget, "openDir", return_value=Path("/test")):
        with mock.patch.object(Path, "is_dir", return_value=True):
            with mock.patch.object(function, "checkPlateSolveAvailability", return_value=True):
                function.selectWatneyIndexPath()


def test_selectAscomDriver_1(function):
    if platform.system() != "Windows":
        return

    with mock.patch.object(win32com.client, "Dispatch", side_effect=Exception()):
        function.selectAscomDriver()


def test_selectAscomDriver_2(function):
    if platform.system() != "Windows":
        return

    class Test:
        DeviceType = None

        @staticmethod
        def Choose(name):
            return name

    function.ui.ascomDevice.setText("test")

    with mock.patch.object(win32com.client, "Dispatch", return_value=Test()):
        function.selectAscomDriver()
        assert function.ui.ascomDevice.text() == "test"
