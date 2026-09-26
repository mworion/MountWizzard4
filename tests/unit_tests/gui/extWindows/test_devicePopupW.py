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
from mw4.base.ascomClass import AscomClass
from mw4.base.indiClass import IndiClass
from mw4.base.sgproClass import SGProClass
from mw4.base.signalsDevices import Signals
from mw4.gui.extWindows.devicePopupW import DevicePopup
from mw4.gui.utilities.nativeQt.qtFileDialog import MWFileDialog
from mw4.gui.utilities.qtMain import MWidget
from pathlib import Path
from PySide6.QtCore import QEventLoop
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QWidget
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


class Parent:
    def __init__(self):
        self.app = App()
        self.data = {}
        self.signals = Signals()
        self.deviceType = "telescope"
        self.loadConfig = True


@pytest.fixture(autouse=False, scope="module")
def function(qapp):
    widget = MWidget()
    widget.app = App()
    window = DevicePopup(widget, device="telescope")
    window.log = logging.getLogger()
    yield window
    QApplication.processEvents()
    gc.collect()
    QApplication.processEvents()


def test_initConfig_1(function):
    function.device = "telescope"
    function.framework = "indi"
    with (
        mock.patch.object(function, "populateTabs"),
        mock.patch.object(function, "selectTabs"),
        mock.patch.object(function, "show"),
    ):
        function.initConfig()


def test_initConfig_2(function):
    function.device = "plateSolve"
    function.framework = "astap"
    with (
        mock.patch.object(function, "checkApp"),
        mock.patch.object(function, "checkIndex"),
        mock.patch.object(function, "populateTabs"),
        mock.patch.object(function, "selectTabs"),
        mock.patch.object(function, "show"),
    ):
        function.initConfig()
    function.device = "telescope"


def test_storeConfig_1(function):
    function.framework = "indi"
    function.device = "telescope"
    with (
        mock.patch.object(function, "readFramework"),
        mock.patch.object(function, "readTabs"),
        mock.patch.object(function, "close"),
    ):
        function.storeConfig()
    assert function.returnValues["close"] == "ok"
    assert function.app.dReg["telescope"].instance.framework == "indi"


def test_selectTabs_1(function):
    function.device = "telescope"
    function.framework = ""
    function.selectTabs()


def test_selectTabs_2(function):
    function.device = "telescope"
    function.framework = "indi"
    function.selectTabs()


def test_selectTabs_3(function):
    function.device = "plateSolve"
    function.framework = "astap"
    function.selectTabs()
    function.device = "telescope"


def test_populateTabs_1(function):
    function.device = "telescope"
    config = function.app.dReg["telescope"].run["indi"].config
    config.deviceName = "test"
    config.hostAddress = "localhost"
    config.showMessage = True
    function.populateTabs()
    assert function.ui.indiHostAddress.text() == "localhost"
    assert function.ui.indiMessages.isChecked()


def test_populateTabs_2(function):
    function.device = "plateSolve"
    config = function.app.dReg["plateSolve"].run["astap"].config
    config.searchRadius = 30
    config.timeout = 60
    function.populateTabs()
    assert function.ui.astapSearchRadius.value() == 30
    function.device = "telescope"


def test_readTabs_1(function):
    function.device = "telescope"
    function.framework = "indi"
    function.ui.indiHostAddress.setText("host")
    function.ui.indiPort.setText("10")
    function.ui.indiMessages.setChecked(True)
    function.readTabs()
    config = function.app.dReg["telescope"].run["indi"].config
    assert config.hostAddress == "host"
    assert config.port == 10
    assert config.showMessage is True


def test_readTabs_2(function):
    function.device = "plateSolve"
    function.framework = "astap"
    function.ui.astapSearchRadius.setValue(30.0)
    function.ui.astapTimeout.setValue(60.0)
    function.ui.astapAppPath.setText("/app")
    function.readTabs()
    config = function.app.dReg["plateSolve"].run["astap"].config
    assert config.searchRadius == 30.0
    assert config.appPath == "/app"
    function.device = "telescope"


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

    function.app.dReg["plateSolve"].run["astap"] = Avail()
    function.checkApp("astap", "test")


def test_checkApp_2(function):
    class Avail:
        @staticmethod
        def checkAvailabilityProgram(appPath):
            return True

    function.app.dReg["plateSolve"].run["watney"] = Avail()
    function.checkApp("watney", "test")


def test_checkApp_3(function):
    class Avail:
        @staticmethod
        def checkAvailabilityProgram(appPath):
            return True

    function.app.dReg["plateSolve"].run["astrometry"] = Avail()
    function.checkApp("astrometry", "test")


def test_checkIndex_1(function):
    class Avail:
        @staticmethod
        def checkAvailabilityIndex(indexPath):
            return True

    function.app.dReg["plateSolve"].run["astap"] = Avail()
    function.checkIndex("astap", "test")


def test_checkIndex_2(function):
    class Avail:
        @staticmethod
        def checkAvailabilityIndex(indexPath):
            return True

    function.app.dReg["plateSolve"].run["watney"] = Avail()
    function.checkIndex("watney", "test")


def test_checkIndex_3(function):
    class Avail:
        @staticmethod
        def checkAvailabilityIndex(indexPath):
            return True

    function.app.dReg["plateSolve"].run["astrometry"] = Avail()
    function.checkIndex("astrometry", "test")


def test_selectAppPath_1(function):
    class Avail:
        @staticmethod
        def checkAvailabilityProgram(indexPath):
            return True

    function.app.dReg["plateSolve"].run["astrometry"] = Avail()
    with (
        mock.patch.object(MWFileDialog, "getExistingDirectory", return_value=Path("/test")),
        mock.patch.object(Path, "is_dir", return_value=False),
    ):
        function.selectAppPath("astap")


def test_selectAppPath_2(function):
    class Avail:
        @staticmethod
        def checkAvailabilityProgram(appPath):
            return True

    function.app.dReg["plateSolve"].run["astap"] = Avail()
    with (
        mock.patch.object(
            MWFileDialog, "getExistingDirectory", return_value=Path("/test.app")
        ),
        mock.patch.object(Path, "is_dir", return_value=True),
    ):
        function.selectAppPath("astap")


def test_selectAppPath_3(function):
    class Avail:
        @staticmethod
        def checkAvailabilityProgram(appPath):
            return True

    function.app.dReg["plateSolve"].run["astap"] = Avail()
    with (
        mock.patch.object(
            MWFileDialog, "getExistingDirectory", return_value=Path("/Astrometry.app")
        ),
        mock.patch.object(Path, "is_dir", return_value=True),
    ):
        function.selectAppPath("astap")


def test_selectIndexPath_1(function):
    class Avail:
        @staticmethod
        def checkAvailabilityIndex(indexPath):
            return True

    function.app.dReg["plateSolve"].run["astap"] = Avail()
    with (
        mock.patch.object(MWFileDialog, "getExistingDirectory", return_value=Path("/test")),
        mock.patch.object(Path, "is_dir", return_value=False),
    ):
        function.selectIndexPath("astap")


def test_selectIndexPath_2(function):
    class Avail:
        @staticmethod
        def checkAvailabilityIndex(indexPath):
            return True

    function.app.dReg["plateSolve"].instance.run = {"astap": Avail()}
    with (
        mock.patch.object(MWFileDialog, "getExistingDirectory", return_value=Path("/test")),
        mock.patch.object(Path, "is_dir", return_value=True),
    ):
        function.selectIndexPath("astap")


def test_selectAscomDriver_1(function):
    function.ui.ascomDevice.setText("initial")
    with mock.patch.object(
        AscomClass, "selectAscomDriver", return_value="selectedDriver"
    ) as mockSelect:
        function.selectAscomDriver()
        mockSelect.assert_called_once_with("initial", "telescope")
        assert function.ui.ascomDevice.text() == "selectedDriver"


def test_selectAscomDriver_2(function):
    function.device = "camera"
    function.ui.ascomDevice.setText("cameraInitial")
    with mock.patch.object(
        AscomClass, "selectAscomDriver", return_value="cameraDriver"
    ) as mockSelect:
        function.selectAscomDriver()
        mockSelect.assert_called_once_with("cameraInitial", "camera")
        assert function.ui.ascomDevice.text() == "cameraDriver"
    function.device = "telescope"


def test_selectBoltwoodPath_1(function):
    function.ui.boltwoodPath.setText("")
    with (
        mock.patch.object(
            MWFileDialog, "getOpenFileName", return_value=Path("/test/file.txt")
        ),
        mock.patch.object(Path, "is_file", return_value=True),
    ):
        function.selectBoltwoodPath()
        assert function.ui.boltwoodPath.text() == str(Path("/test/file.txt"))


def test_selectBoltwoodPath_2(function):
    function.ui.boltwoodPath.setText("")
    with (
        mock.patch.object(
            MWFileDialog, "getOpenFileName", return_value=Path("/test/file.txt")
        ),
        mock.patch.object(Path, "is_file", return_value=False),
    ):
        function.selectBoltwoodPath()
        assert function.ui.boltwoodPath.text() == ""


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
        rv = DevicePopup.configure(parent, "telescope")
        assert rv["close"] == "ok"


def test_configure_2(function):
    parent = MWidget()
    parent.app = App()
    with mock.patch.object(DevicePopup, "exec", return_value=False):
        rv = DevicePopup.configure(parent, "telescope")
        assert rv["close"] == "cancel"


def test_discoverDevices_sgpro_empty(function):
    sgproInstance = mock.MagicMock()
    sgproInstance.discoverDevices = mock.MagicMock(return_value=())
    function.app.dReg["telescope"].run["sgpro"] = sgproInstance
    with mock.patch.object(SGProClass, "discoverDevices", return_value=()):
        function.discoverDevices("sgpro", QWidget())


def test_discoverDevices_sgpro_devices_found(function):
    sgproInstance = mock.MagicMock()
    sgproInstance.discoverDevices = mock.MagicMock(return_value=("Test1", "Test2"))
    function.app.dReg["telescope"].run["sgpro"] = sgproInstance
    with mock.patch.object(SGProClass, "discoverDevices", return_value=("Test1", "Test2")):
        function.discoverDevices("sgpro", QWidget())

    assert function.framework == "sgpro"
