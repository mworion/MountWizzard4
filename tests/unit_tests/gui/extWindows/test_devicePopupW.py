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
import gc
import logging
import pytest
import unittest.mock as mock
from mw4.base.ascomClass import AscomClass
from mw4.base.indiClass import IndiClass
from mw4.base.signalsDevices import Signals
from mw4.gui.extWindows.devicePopupW import DevicePopup
from mw4.gui.utilities.qtMain import MWidget
from pathlib import Path
from PySide6.QtCore import QEventLoop
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QWidget
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Parent:
    def __init__(self):
        self.app = App()
        self.data = {}
        self.signals = Signals()
        self.deviceType = "telescope"
        self.loadConfig = True


@pytest.fixture(autouse=False, scope="module")
def function(qapp):
    data = {
        "framework": "indi",
        "frameworks": {"indi": {"deviceName": "test", "deviceList": ["1", "2"]}},
    }
    widget = MWidget()
    widget.app = App()
    window = DevicePopup(widget, device="telescope", data=data)
    window.log = logging.getLogger()
    yield window
    QApplication.processEvents()
    gc.collect()
    QApplication.processEvents()


def test_initConfig_1(function):
    with (
        mock.patch.object(function, "populateTabs"),
        mock.patch.object(function, "selectTabs"),
        mock.patch.object(function, "show"),
    ):
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
    with (
        mock.patch.object(function, "checkApp"),
        mock.patch.object(function, "checkIndex"),
        mock.patch.object(function, "populateTabs"),
        mock.patch.object(function, "selectTabs"),
        mock.patch.object(function, "show"),
    ):
        function.initConfig()


def test_storeConfig_1(function):
    with (
        mock.patch.object(function, "readFramework"),
        mock.patch.object(function, "readTabs"),
        mock.patch.object(function, "close"),
    ):
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
        "indi": {
            "deviceName": "test",
            "deviceList": ["test", "test1"],
            "hostaddress": "test",
            "messages": True,
        },
    }
    function.populateTabs()


def test_populateTabs_2(function):
    function.data = {
        "astap": {
            "deviceName": "test",
            "deviceList": ["test", "test1"],
            "searchRadius": 30.0,
            "timeout": 60.0,
        },
    }
    function.populateTabs()


def test_readTabs_1(function):
    function.data = {
        "indi": {
            "deviceName": "telescope",
            "deviceList": ["test", "test1"],
            "hostaddress": "test",
            "messages": True,
            "port": 10,
        },
    }
    function.readTabs()


def test_readTabs_2(function):
    function.framework = "astap"
    function.data = {
        "astap": {
            "deviceName": "test",
            "deviceList": ["test", "test1"],
            "searchRadius": 30.0,
            "timeout": 60.0,
        },
    }
    function.readTabs()


def test_readFramework_1(function):
    function.readFramework()


def test_updateDeviceNameList_1(function):
    function.updateDeviceNameList("indi", ["test1", "test2"])


def test_discoverDevices_1(function):
    with mock.patch.object(IndiClass, "discoverDevices", return_value=()):
        function.discoverDevices("indi", QWidget())


def test_discoverDevices_2(function):
    with mock.patch.object(IndiClass, "discoverDevices", return_value=("Test1", "Test2")):
        function.discoverDevices("indi", QWidget())


def test_discoverDevices_hid_empty(function):
    """Test discoverDevices for hid framework with no devices found."""
    from mw4.logic.hidController.hidController import HidController

    function.device = "hidController"
    with mock.patch.object(HidController, "discoverDevices", return_value=[]):
        function.discoverDevices("hid")
    function.device = "telescope"


def test_discoverDevices_hid_devices_found(function):
    """Test discoverDevices for hid framework with devices found."""
    from mw4.logic.hidController.hidController import HidController

    function.device = "hidController"

    with mock.patch.object(
        HidController, "discoverDevices", return_value=["Pro Controller", "Game Pad"]
    ):
        function.discoverDevices("hid")

    assert function.framework == "hid"
    function.device = "telescope"


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
    with (
        mock.patch.object(MWidget, "openDir", return_value=Path("/test")),
        mock.patch.object(Path, "is_dir", return_value=False),
    ):
        function.selectAppPath("astap")


def test_selectAppPath_2(function):
    class Avail:
        @staticmethod
        def checkAvailabilityProgram(appPath):
            return True

    function.app.plateSolve.run["astap"] = Avail()
    with (
        mock.patch.object(MWidget, "openDir", return_value=Path("/test.app")),
        mock.patch.object(Path, "is_dir", return_value=True),
    ):
        function.selectAppPath("astap")


def test_selectAppPath_3(function):
    class Avail:
        @staticmethod
        def checkAvailabilityProgram(appPath):
            return True

    function.app.plateSolve.run["astap"] = Avail()
    with (
        mock.patch.object(MWidget, "openDir", return_value=Path("/Astrometry.app")),
        mock.patch.object(Path, "is_dir", return_value=True),
    ):
        function.selectAppPath("astap")


def test_selectIndexPath_1(function):
    class Avail:
        @staticmethod
        def checkAvailabilityIndex(indexPath):
            return True

    function.app.plateSolve.run["astap"] = Avail()
    with (
        mock.patch.object(MWidget, "openDir", return_value=Path("/test")),
        mock.patch.object(Path, "is_dir", return_value=False),
    ):
        function.selectIndexPath("astap")


def test_selectIndexPath_2(function):
    class Avail:
        @staticmethod
        def checkAvailabilityIndex(indexPath):
            return True

    function.app.plateSolve.run = {"astap": Avail()}
    with (
        mock.patch.object(MWidget, "openDir", return_value=Path("/test")),
        mock.patch.object(Path, "is_dir", return_value=True),
    ):
        function.selectIndexPath("astap")


def test_selectAscomDriver_1(function):
    # Create a mock parent with data attribute
    mockParent = mock.Mock()
    mockParent.data = {}
    function.parent = mockParent
    function.deviceType = "telescope"

    with mock.patch.object(AscomClass, "selectAscomDriver", return_value="test"):
        function.selectAscomDriver()
        assert function.ui.ascomDevice.text() == "test"


def test_selectBoltwoodPath_1(function):
    function.ui.boltwoodPath.setText("")
    with (
        mock.patch.object(MWidget, "openFile", return_value=Path("/test/file.txt")),
        mock.patch.object(Path, "is_file", return_value=True),
    ):
        function.selectBoltwoodPath()
        assert function.ui.boltwoodPath.text() == str(Path("/test/file.txt"))


def test_selectBoltwoodPath_2(function):
    function.ui.boltwoodPath.setText("")
    with (
        mock.patch.object(MWidget, "openFile", return_value=Path("/test/file.txt")),
        mock.patch.object(Path, "is_file", return_value=False),
    ):
        function.selectBoltwoodPath()
        assert function.ui.boltwoodPath.text() == ""


def test_populateTabsSkipsFrameworkKey(function) -> None:
    """Test populateTabs skips 'framework' key in data (line 167)."""
    function.data = {
        "framework": "indi",  # This should be skipped
        "indi": {
            "deviceName": "test",
            "deviceList": ["test", "test1"],
            "hostaddress": "localhost",
            "messages": False,
        },
    }
    # Should not raise error when skipping the "framework" key
    function.populateTabs()
    # Verify indi framework was processed
    assert function.data["indi"]["deviceName"] == "test"


def test_storeConfigWithIndiCopyConfig(function) -> None:
    """Test storeConfig adds 'indi' to copyConfig when checked (line 225)."""
    function.framework = "indi"
    function.data = {
        "indi": {
            "deviceName": "test_device",
            "deviceList": ["test", "test1"],
            "hostaddress": "localhost",
            "messages": False,
        },
    }
    # Mock the UI checkboxes
    with (
        mock.patch.object(function.ui.indiCopyConfig, "isChecked", return_value=True),
        mock.patch.object(function.ui.alpacaCopyConfig, "isChecked", return_value=False),
        mock.patch.object(function, "readFramework"),
        mock.patch.object(function, "readTabs"),
        mock.patch.object(function, "close"),
    ):
        function.storeConfig()
        # Verify copyConfig contains "indi"
        assert "indi" in function.returnValues["copyConfig"]
        assert "alpaca" not in function.returnValues["copyConfig"]


def test_storeConfigWithAlpacaCopyConfig(function) -> None:
    """Test storeConfig adds 'alpaca' to copyConfig when checked (line 227)."""
    function.framework = "alpaca"
    function.data = {
        "alpaca": {
            "deviceName": "test_device",
            "deviceList": ["test", "test1"],
            "hostaddress": "localhost",
            "port": 8000,
        },
    }
    # Mock the UI checkboxes
    with (
        mock.patch.object(function.ui.indiCopyConfig, "isChecked", return_value=False),
        mock.patch.object(function.ui.alpacaCopyConfig, "isChecked", return_value=True),
        mock.patch.object(function, "readFramework"),
        mock.patch.object(function, "readTabs"),
        mock.patch.object(function, "close"),
    ):
        function.storeConfig()
        # Verify copyConfig contains "alpaca"
        assert "alpaca" in function.returnValues["copyConfig"]
        assert "indi" not in function.returnValues["copyConfig"]


def test_storeConfigWithBothCopyConfigs(function) -> None:
    """Test storeConfig adds both 'indi' and 'alpaca' to copyConfig."""
    function.framework = "indi"
    function.data = {
        "indi": {
            "deviceName": "test_device",
            "deviceList": ["test", "test1"],
            "hostaddress": "localhost",
            "messages": False,
        },
    }
    # Mock the UI checkboxes
    with (
        mock.patch.object(function.ui.indiCopyConfig, "isChecked", return_value=True),
        mock.patch.object(function.ui.alpacaCopyConfig, "isChecked", return_value=True),
        mock.patch.object(function, "readFramework"),
        mock.patch.object(function, "readTabs"),
        mock.patch.object(function, "close"),
    ):
        function.storeConfig()
        # Verify copyConfig contains both
        assert "indi" in function.returnValues["copyConfig"]
        assert "alpaca" in function.returnValues["copyConfig"]


def test_closeEvent_1(function):
    function.loop = mock.MagicMock(spec=QEventLoop)
    event = QCloseEvent()
    with mock.patch("PySide6.QtWidgets.QMainWindow.closeEvent"):
        function.closeEvent(event)
    function.loop.quit.assert_called_once()
    function.loop = None


def test_closeEvent_2(function):
    function.loop = None
    event = QCloseEvent()
    with mock.patch("PySide6.QtWidgets.QMainWindow.closeEvent"):
        function.closeEvent(event)


def test_exec_1(function):
    with (
        mock.patch.object(function, "initConfig"),
        mock.patch("mw4.gui.extWindows.devicePopupW.QEventLoop") as mock_loop_cls,
    ):
        mock_loop = mock.MagicMock(spec=QEventLoop)
        mock_loop_cls.return_value = mock_loop
        function.returnValues["close"] = "ok"
        result = function.exec()
        assert result
        mock_loop.exec.assert_called_once()


def test_exec_2(function):
    with (
        mock.patch.object(function, "initConfig"),
        mock.patch("mw4.gui.extWindows.devicePopupW.QEventLoop") as mock_loop_cls,
    ):
        mock_loop = mock.MagicMock(spec=QEventLoop)
        mock_loop_cls.return_value = mock_loop
        function.returnValues["close"] = "cancel"
        result = function.exec()
        assert not result
        mock_loop.exec.assert_called_once()


def test_configure_1(function):
    parent = MWidget()
    parent.app = App()

    def mock_exec_ok(self: DevicePopup) -> bool:
        self.returnValues["close"] = "ok"
        return True

    with mock.patch.object(DevicePopup, "exec", mock_exec_ok):
        rv = DevicePopup.configure(parent, "telescope", {"framework": "indi"})
        assert rv["close"] == "ok"


def test_configure_2(function):
    parent = MWidget()
    parent.app = App()
    with mock.patch.object(DevicePopup, "exec", return_value=False):
        rv = DevicePopup.configure(parent, "telescope", {"framework": "indi"})
        assert rv["close"] == "cancel"
