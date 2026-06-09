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
import mw4
import pytest
from mw4.gui.extWindows.setting.tabSettDevice import SettDevice
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtWidgets import QPushButton
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = MWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)

    # Only return devices that have UI elements in setupUiDriver
    validDevices = [
        "camera",
        "cover",
        "directWeather",
        "dome",
        "filter",
        "focuser",
        "lightPanel",
        "power",
        "sensor1Weather",
        "sensor2Weather",
        "sensor3Weather",
        "sensor4Weather",
        "telescope",
    ]

    def mockConfigurable():
        for entry in mainW.app.dReg.d.values():
            isValid = entry.name in validDevices
            isValid = isValid and entry.isConfigurable
            isValid = isValid and entry.instance is not None
            if isValid:
                yield entry

    with mock.patch.object(mainW.app.dReg, "configurable", mockConfigurable):
        window = SettDevice(mainW)
    yield window
    mainW.app.threadPool.waitForDone(10000)


def test_setupIcons_1(function):
    function.setupIcons()


def test_setupDeviceGui_1(function):
    with mock.patch.object(function.app.dReg, "configurable", return_value=[]):
        function.setupDeviceGui()


def test_setupDeviceGui_2(function):
    class MockFramework:
        class Config:
            deviceName = "test_device"

        config = Config()

    class MockRun:
        def __init__(self, has_config):
            if has_config:
                self.config = MockFramework.Config()

        def __getitem__(self, key):
            return self

    class MockEntry:
        def __init__(self):
            self.name = "telescope"
            self.framework = "indi"
            self.run = {"indi": MockFramework(), "test": object()}

    class MockRegistryEntry:
        run = {"indi": MockFramework(), "test": object()}

    class MockD:
        def __getitem__(self, key):
            return MockRegistryEntry()

    with (
        mock.patch.object(function.app.dReg, "configurable", return_value=[MockEntry()]),
        mock.patch.object(function.app.dReg, "d", MockD()),
    ):
        function.setupDeviceGui()


def test_closeEvent_1(function):
    # Connect signals first so they can be disconnected without warnings
    for driver in function.setupUiDriver:
        signals = function.app.dReg[driver].signals
        signals.deviceConnected.connect(function.deviceConnected)
        signals.deviceDisconnected.connect(function.deviceDisconnected)
    function.closeEvent()


def test_processPopupResults_2(function):
    class UI:
        ok = QPushButton()

    class Test:
        returnValues = {
            "device": "telescope",
            "framework": "indi",
            "data": {
                "framework": "indi",
                "indi": {
                    "deviceName": "",
                    "deviceList": ["test", "test1"],
                },
            },
            "copyConfig": [],
        }
        ui = UI()

    function.devicePopup = Test()
    function.devicePopup.ui.ok.clicked.connect(function.processPopupResults)
    with (
        mock.patch.object(function.app.dReg, "writeConfigToSingleDevice"),
        mock.patch.object(function.app.dReg, "startDevice"),
    ):
        function.processPopupResults()


def test_processPopupResults_3(function):
    class UI:
        ok = QPushButton()

    class Test:
        returnValues = {
            "device": "telescope",
            "framework": "indi",
            "data": {
                "framework": "indi",
                "indi": {
                    "deviceName": "test_device",
                    "deviceList": ["test", "test1"],
                },
            },
            "copyConfig": ["indi"],
        }
        ui = UI()

    function.devicePopup = Test()
    function.devicePopup.ui.ok.clicked.connect(function.processPopupResults)
    with (
        mock.patch.object(function, "copyConfig"),
        mock.patch.object(function.app.dReg, "writeConfigToSingleDevice"),
        mock.patch.object(function.app.dReg, "startDevice"),
    ):
        function.processPopupResults()


def test_copyConfig_1(function):
    # copyConfig returns early, so just verify it doesn't crash
    function.copyConfig("telescope", "indi")


def test_copyConfig_2(function):
    # copyConfig returns early, so just verify it doesn't crash
    function.copyConfig("telescope", "indi")


def test_copyConfig_3(function):
    # copyConfig returns early, so just verify it doesn't crash
    function.copyConfig("telescope", "test")


def test_copyConfig_4(function):
    # copyConfig returns early, so just verify it doesn't crash
    function.copyConfig("telescope", "indi")


def test_callPopup_1(function):
    class Pop:
        class OK:
            class Clicked:
                class Connect:
                    @staticmethod
                    def connect(a):
                        return

                clicked = Connect()

            ok = Clicked()

        def initConfig(self):
            pass

        ui = OK()

    with (
        mock.patch.object(function.app.dReg, "stopDevice"),
        mock.patch.object(function.app.dReg, "collectConfigFromSingleDevice", return_value={}),
        mock.patch.object(
            mw4.gui.extWindows.setting.tabSettDevice, "DevicePopup", return_value=Pop()
        ),
    ):
        function.callPopup("cover")


def test_dispatchDriverDropdown_1(function):
    function.setupUiDriver["telescope"]["uiDropDown"].addItem("indi - test")
    with (
        mock.patch.object(function.app.dReg, "stopDevice"),
        mock.patch.object(function.app.dReg, "startDevice"),
    ):
        function.dispatchDriverDropdown("telescope", 1)


def test_dispatchDriverDropdown_2(function):
    function.setupUiDriver["dome"]["uiDropDown"].addItem("device disabled")
    with (
        mock.patch.object(function.app.dReg, "stopDevice"),
        mock.patch.object(function.app.dReg, "startDevice"),
    ):
        function.dispatchDriverDropdown("dome", 0)


def test_deviceConnected_2(function):
    with mock.patch.object(function.app.dReg, "setStat"):
        function.deviceConnected("filter", "test")


def test_deviceConnected_3(function):
    with mock.patch.object(function.app.dReg, "setStat"):
        function.deviceConnected("dome", "test")


def test_deviceDisconnected_1(function):
    with mock.patch.object(function.app.dReg, "setStat"):
        function.deviceDisconnected("dome", "test")


def test_startDevice_1(function):
    with mock.patch.object(function.app.dReg, "startDevice"):
        function.startDevice("telescope", True)


def test_stopDevice_1(function):
    with mock.patch.object(function.app.dReg, "stopDevice"):
        function.stopDevice("telescope")
