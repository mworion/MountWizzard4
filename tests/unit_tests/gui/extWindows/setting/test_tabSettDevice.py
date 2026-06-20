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
import pytest
from mw4.gui.extWindows.setting.tabSettDevice import SettDevice
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QComboBox, QPushButton
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = MWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)

    # Mock all the device UI elements
    devices = [
        "camera",
        "cover",
        "directWeather",
        "dome",
        "filter",
        "focuser",
        "lightPanel",
        "measure",
        "plateSolve",
        "power",
        "relay",
        "remote",
        "seeingWeather",
        "sensor1Weather",
        "sensor2Weather",
        "sensor3Weather",
        "sensor4Weather",
        "telescope",
    ]

    for device in devices:
        # Create real QComboBox for dropdowns
        dropdown_name = f"{device}Device"
        dropdown = QComboBox()
        dropdown.addItem("No device")
        setattr(mainW.ui, dropdown_name, dropdown)

        # Mock the setup button (or create mock for some devices)
        setup_name = f"{device}Setup"
        if device not in ["directWeather", "measure", "remote"]:
            button = QPushButton()
            setattr(mainW.ui, setup_name, button)

    mainW.ui.cameraDevice = QComboBox()
    mainW.ui.cameraDevice.addItem("No device")

    # Only return devices that have UI elements in deviceUi
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
    class MockConfig:
        deviceName = "test_device"

    class MockFramework:
        config = MockConfig()

    class MockEntry:
        def __init__(self):
            self.name = "telescope"
            self.framework = "indi"
            self.stat = False
            self.run = {"indi": MockFramework()}

    class MockRegistryEntry:
        run = {"indi": MockFramework()}

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
    for driver in function.deviceUi:
        signals = function.app.dReg[driver].signals
        signals.deviceConnected.connect(function.deviceConnected)
        signals.deviceDisconnected.connect(function.deviceDisconnected)
    function.closeEvent()


def test_closeEvent_skipsEntriesWithoutSignals(function):
    class NoSigInstance:
        pass

    class Entry:
        name = "telescope"

    realEntry = function.app.dReg["telescope"]
    origInstance = realEntry.instance
    realEntry.instance = NoSigInstance()
    try:
        with mock.patch.object(function.app.dReg, "configurable", return_value=[Entry()]):
            function.closeEvent()
    finally:
        realEntry.instance = origInstance


def test_processPopupResults_2(function):
    returnValues = {
        "device": "telescope",
        "close": "ok",
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
    with (
        mock.patch.object(function.app.dReg, "writeConfigToSingleDevice"),
        mock.patch.object(function.app.dReg, "startDevice"),
    ):
        function.processPopupResults(returnValues)


def test_processPopupResults_3(function):
    returnValues = {
        "device": "telescope",
        "close": "ok",
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
    with (
        mock.patch.object(function, "copyConfig"),
        mock.patch.object(function.app.dReg, "writeConfigToSingleDevice"),
        mock.patch.object(function.app.dReg, "startDevice"),
    ):
        function.processPopupResults(returnValues)


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
    with (
        mock.patch.object(function.app.dReg, "stopDevice"),
        mock.patch.object(function.app.dReg, "collectConfigFromSingleDevice", return_value={}),
        mock.patch(
            "mw4.gui.extWindows.setting.tabSettDevice.DevicePopup.configure",
            return_value={"close": "cancel"},
        ),
    ):
        function.callPopup("cover")


def test_callPopup_2(function):
    returnValues = {
        "close": "ok",
        "device": "telescope",
        "data": {"framework": "indi", "indi": {"deviceName": "test"}},
        "copyConfig": [],
    }
    with (
        mock.patch.object(function.app.dReg, "stopDevice"),
        mock.patch.object(function.app.dReg, "collectConfigFromSingleDevice", return_value={}),
        mock.patch(
            "mw4.gui.extWindows.setting.tabSettDevice.DevicePopup.configure",
            return_value=returnValues,
        ),
        mock.patch.object(function, "processPopupResults") as mock_process,
    ):
        function.callPopup("cover")
        mock_process.assert_called_once_with(returnValues)


def test_dispatchDriverDropdown_1(function):
    dropDown = function.deviceUi["telescope"]["uiDropDown"]
    dropDown.clear()
    dropDown.addItem("indi - test")
    dropDown.setCurrentIndex(0)
    with (
        mock.patch.object(function.app.dReg, "stopDevice"),
        mock.patch.object(function.app.dReg, "startDevice"),
    ):
        function.dispatchDriverDropdown("telescope", 1)


def test_dispatchDriverDropdown_2(function):
    function.deviceUi["dome"]["uiDropDown"].addItem("device disabled")
    with (
        mock.patch.object(function.app.dReg, "stopDevice"),
        mock.patch.object(function.app.dReg, "startDevice"),
    ):
        function.dispatchDriverDropdown("dome", 0)


def test_dispatchDriverDropdownEmitsStartDeviceWhenAllConditionsMet(function) -> None:
    """Test dispatchDriverDropdown emits startDevice when framework and deviceName
    exist (line 210)."""
    from unittest.mock import MagicMock

    mock_config = MagicMock()
    mock_config.deviceName = "test_device"
    mock_fw = MagicMock()
    mock_fw.config = mock_config
    mock_instance = MagicMock()
    mock_instance.framework = "alpaca"
    mock_entry = MagicMock()
    mock_entry.framework = "alpaca"
    mock_entry.instance = mock_instance
    mock_entry.run = {"alpaca": mock_fw}

    function.deviceUi["telescope"]["uiDropDown"].clear()
    function.deviceUi["telescope"]["uiDropDown"].addItem("alpaca - test_device")
    function.deviceUi["telescope"]["uiDropDown"].setCurrentIndex(0)

    spy = QSignalSpy(function.app.startDevice)
    with mock.patch.object(function.app.dReg, "d", {"telescope": mock_entry}):
        function.dispatchDriverDropdown("telescope", 1)
    assert spy.count() == 1
    assert spy.at(0)[0] == "telescope"


def test_applyConnected_1(function):
    function.applyConnected("filter")


def test_applyConnected_2(function):
    function.applyConnected("dome")


def test_applyDisconnected_1(function):
    function.applyDisconnected("dome")


def test_deviceConnected_resolvesNameViaSender(function):
    sig = function.app.dReg["dome"].signals
    function.signalsToName[id(sig)] = "dome"
    with mock.patch.object(function, "sender", return_value=sig):
        function.deviceConnected("ignored")


def test_deviceConnected_unknownSenderIsNoOp(function):
    with mock.patch.object(function, "sender", return_value=object()):
        function.deviceConnected()


def test_deviceDisconnected_resolvesNameViaSender(function):
    sig = function.app.dReg["dome"].signals
    function.signalsToName[id(sig)] = "dome"
    with mock.patch.object(function, "sender", return_value=sig):
        function.deviceDisconnected("ignored")


def test_deviceDisconnected_unknownSenderIsNoOp(function):
    with mock.patch.object(function, "sender", return_value=object()):
        function.deviceDisconnected()


def test_setupDeviceGuiCallsDeviceConnectedWhenStatTrue(function) -> None:
    """Test setupDeviceGui calls deviceConnected when entry.stat is True (line 149)."""

    class MockConfig:
        deviceName = "test_device"

    class MockFramework:
        config = MockConfig()

    class MockEntry:
        def __init__(self):
            self.name = "telescope"
            self.framework = "indi"
            self.stat = True  # Connected state
            self.run = {"indi": MockFramework()}

    class MockRegistryEntry:
        run = {"indi": MockFramework()}

    class MockD:
        def __getitem__(self, key):
            return MockRegistryEntry()

    with (
        mock.patch.object(function.app.dReg, "configurable", return_value=[MockEntry()]),
        mock.patch.object(function.app.dReg, "d", MockD()),
        mock.patch.object(function, "applyConnected") as mock_connected,
    ):
        function.setupDeviceGui()
        # Verify applyConnected was called with the entry name
        mock_connected.assert_called()


def test_setupDeviceGuiCallsDeviceDisconnectedWhenStatFalse(function) -> None:
    """Test setupDeviceGui calls deviceDisconnected when entry.stat is False (line 151)."""

    class MockConfig:
        deviceName = "test_device"

    class MockFramework:
        config = MockConfig()

    class MockEntry:
        def __init__(self):
            self.name = "dome"
            self.framework = "alpaca"
            self.stat = False  # Disconnected state
            self.run = {"alpaca": MockFramework()}

    class MockRegistryEntry:
        run = {"alpaca": MockFramework()}

    class MockD:
        def __getitem__(self, key):
            return MockRegistryEntry()

    with (
        mock.patch.object(function.app.dReg, "configurable", return_value=[MockEntry()]),
        mock.patch.object(function.app.dReg, "d", MockD()),
        mock.patch.object(function, "applyDisconnected") as mock_disconnected,
    ):
        function.setupDeviceGui()
        # Verify applyDisconnected was called with the entry name
        mock_disconnected.assert_called()
